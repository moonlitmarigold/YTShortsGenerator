# AGENTS.md

This file provides guidance to Hermes, Claude Code, and other agents when working in this repository.
It mirrors `CLAUDE.md` so all agents share the same project context.

## What this project actually is

This repo began as a fork of **MoneyPrinterV2** but is being rewritten into a focused **YouTube Shorts generator/uploader**. Treat the root `README.md` as largely inherited upstream baggage (Twitter bot, affiliate marketing, cold outreach) — it does **not** reflect current scope. `requirements.txt` is now a mix of real current dependencies (`sqlmodel`, `ollama`, `kittentts`, `whisper`/`faster-whisper`, `pydub`, `pydantic`/`pydantic_settings`) and leftover upstream cruft (`selenium`, `selenium_firefox`). The authoritative scope docs are `docs/overview.md` (the intended 7-step pipeline) and `docs/Roadmap.md`.

Much of `src/` is still un-migrated upstream leftovers that are **not wired into the current pipeline**: `old_main.py`, `old_config.py`, `cron.py`, `cache.py`, `status.py`, `validate.py`, `llm_provider.py`, `classes/YouTube.py`, `classes/background.py`, `classes/subtitles.py`, `classes/thumbnail.py`, `classes/video.py`, and the top-level `src/utils.py` (shadowed — see Config below). Don't assume a file is live just because it exists — check that it's reachable from `PipelineBuilder`/`__main__` first. `sessions.py` and `classes/Tts.py` were previously in this dead-file bucket but are **now live** — see below.

## Commands

- **Python version:** 3.12 (see `.python-version`).
- **Install:** `pip install -r requirements.txt`
- **Run the app:** `python -m src` (entry point is `src/__main__.py`; `main()` is currently a stub).
- **Tests:** the tests use config paths **relative to the current directory** (`Path('config.yaml')`, `Path('.env')`), and those fixtures live in `tests/`. So run pytest from inside `tests/`:
  ```bash
  cd tests && python -m pytest tests.py
  ```
  Single test: `cd tests && python -m pytest tests.py::test_pipeline_build`
- **Parallel runs:** `pytest-xdist` is in `requirements.txt`. `src/sql.py`'s `return_engine()` opens the shared sqlite db with `connect_args={"timeout": 30}` and `PRAGMA journal_mode=WAL` specifically so concurrent `session.save()`/`.delete()` calls from parallel workers don't throw `database is locked`. Run with `cd tests && python -m pytest test_steps.py -n 4` (cap worker count to roughly the number of tests — `-n auto` just idles extra workers here).
- **`tests/pytest.ini`** sets `log_cli = true` / `log_cli_level = DEBUG`, so `logger.debug(...)` calls in `src/` show up live in the console for any run from `tests/` (PyCharm or CLI) without needing `--log-cli-level` passed manually. This is independent of stdout capturing — `-s` is still needed separately to see `print()` output, and still isn't fully live under `-n` (xdist buffers each worker's output until that test finishes).
- **Ollama required for some tests:** `test_providers`, `test_pipeline_build`, `test_config`, `test_pipeline`, `test_session` hit either a running Ollama server (at the URL in `tests/config.yaml`) or the real sqlite db at `src/database.db`. They will fail if Ollama isn't running or the model isn't pulled.
- **Step-level unit tests don't need Ollama or the DB.** `test_prompt_step_*`, `test_tts_step_*`, `test_transcribe_step_*` in `tests/tests.py` build a bare `sessions.SessionInfo` around an in-memory `sql.GenerationSession(...)` (never calling `.save()`/`.delete()`), and construct the step class via `Step.__new__(Step)` with its heavy backend (Ollama/TTS/Whisper) replaced by a small fake object. This is the pattern to follow for new step tests (e.g. once `Audio` is wired in) — it keeps tests fast and independent of the real `src/database.db`.

## Architecture (the big picture)

The runtime is a **linear pipeline of steps**, each a class exposing `.run(session)`, assembled by a builder from config.

**`PipelineBuilder` (`src/pipeline.py`)** is the composition root. `build()` loads config, then calls each factory in `build_list()` to instantiate a step and register it via `add_steps`. `Pipeline.run()` executes steps in insertion order, and **after each step** calls `session_obj.set_step(key)` and `session_obj.save()` — so pipeline progress is persisted to sqlite incrementally, not just at the end. **`build_list()` is the single place that controls which steps run** — currently: `_config`, `_session`, `_prompt`, `_tts`, `_transcribe`. A `_audio` factory already exists on `PipelineBuilder` (wiring `classes/Audio.py`) but is **not yet added to `build_list()`** — it's built but not live.

**Config has finished migrating to Pydantic.** `src/config.py` no longer has a dict-based `Config` class — `open_config_env()` returns `(AppConfig, Secrets)`, both Pydantic (`AppConfig` is a `BaseModel`, `Secrets` is a `pydantic_settings.BaseSettings` reading `.env`). `AppConfig` composes `Metadata`, `provider: ProviderConfig`, `tts: TTSConfig`, `transcribe: TranscribeConfig`, `audio: AudioConfig` and injects the selected generation-type prompt text into `provider.prompt` via a `model_validator`. **Keep the Pydantic *schema* classes separate from the runtime provider/backend classes** — `XConfig` is a `BaseModel` (holds validated values); `BaseX`/concrete backends are dataclasses (do the work). Do not make one inherit the other.

There are now **three parallel registries** following the same pattern — `provider.name`/`tts.name`/`transcribe.name` in config selects a class registered via a `@register` decorator into a module-level dict, keyed by the class's lowercased name:
- `src/providers/` → `PROVIDER_REGISTER` (e.g. `"ollama"` → `Ollama`, in `providers/Ollama.py`)
- `src/TTS/` → `TTS_REGISTER` (e.g. `"kitten"` → `Kitten` in `TTS/kitten_tts.py`, wraps the `kittentts` package)
- `src/Transcribe/` → `TR_REGISTER` (e.g. `"whisper"` → `Whisper` in `Transcribe/whisper.py`, wraps `stable_whisper`/`openai-whisper`)

Register any new backend in the matching dict.

**Generation types (`src/generation_types/`)** are prompt templates, but **not** bare files scanned off disk — they're explicit entries in the `GENERATION_TYPES` dict in `generation_types/__init__.py`, each a `GenerationType(name=..., _prompt_file=...)` pointing at a **Markdown** file (e.g. `quote.md`, not `.yaml`). `AppConfig.generation_type` is validated against `GENERATION_TYPES.keys()`, and its `prompt_file` is read and `{{placeholder}}`-substituted with `Metadata` fields. Adding a new video type = adding both the `.md` prompt file **and** a new `GENERATION_TYPES` entry.

### Persistence layer: `src/sql.py` + `src/sessions.py`

This is now central, not peripheral. `src/sql.py` defines SQLModel tables (`GenerationSession`, `Video`, `Scene`, `VideoPerformance`) backed by a single sqlite file at `src/database.db`, created via `sql.return_engine()`. `sessions.SessionInfo` (a plain dataclass wrapping a `sql.GenerationSession` row, plus the parsed `script: GeneratedVideoScript`) is threaded through **every** pipeline step's `.run(session)` call — steps read `session.script.scenes`, write to `session.audio_path(scene_id)` / `session.transcribe_path(scene_id)` / `session.full_audio_path()` / `session.music_path()` (all under `src/files/<session.id>/`), and mutate `session.script`/status via `inject_prompt_output`, `set_status`, `set_step`, `set_error`.

**Gotcha:** `sql.return_engine()` hardcodes its path relative to `sql.py`'s own location — there's no override hook for tests to point at an isolated/in-memory db. Anything that calls `session.save()`, `session.delete()`, or `sessions.SessionInfo.from_sql()` hits the real `src/database.db`. For step-level tests, avoid those calls entirely (see Commands above); only reach for a real save/delete when specifically testing the persistence layer itself.

`SessionInfo.delete()` does a **hand-rolled cascade delete** (performances → scenes → video → session, in that FK-safe order) rather than relying on ORM cascade — if you touch that method, keep the ordering, since deleting out of order will violate the FK constraints.

## Roadmap: unattended multi-video batch generation

Current state (2026-08-13): the only entrypoint is the interactive `menu.Menu().start()` in `src/__main__.py`, and `AppConfig.metadata.topic` (`src/utils/extra_configs.py`) is a single static string — running the pipeline twice back to back produces two videos on the same topic with a human required to click through the menu each time. Making this "reusable" (generate many shorts on a cadence with minimal intervention) needs:

1. **Headless/batch entrypoint** — a non-interactive path (`python -m src --batch N`) that drives `PipelineBuilder` directly instead of `menu.Menu().start()`.
2. **Topic/metadata variation per run** — something has to hand out a different `Metadata` (and possibly `generation_type`) each iteration instead of the one fixed value in `config.yaml`.
3. **Scheduling** — nothing currently triggers a run on a cadence (cron/systemd timer calling the batch entrypoint; concurrent-session safety already exists via the WAL setup in `src/sql.py`).
4. **Failure handling without a human** — a failed step currently just sets `Status.FAILED` and raises (`Pipeline.run` in `src/pipeline.py`); a batch run needs to catch per-session failures and continue rather than aborting the whole batch.
5. **Upload auth** — `Uploaders`/`classes/Upload.py` exist but the menu still shows "Login (not implemented)"; unattended uploads need stored/refreshed OAuth tokens instead of an interactive consent flow per run.
6. **Per-run resource variation** — background footage/voice/generation type currently come from one static `AppConfig`; many videos likely want these to vary too, not just the topic.

Design direction decided for #1 and #2 (not yet implemented):

- `PipelineBuilder.__init__` (`src/pipeline.py`) gains optional `metadata_override: Metadata | None` and `generation_type_override: str | None`; `_config()` applies them to `self.app_config` right after `open_config_env()` loads it. This keeps the existing single-run path untouched (defaults `None`) and gives a batch driver a clean seam to inject a different topic/tone/type per iteration without touching the YAML file on disk.
- New `BatchConfig`/`MetadataVariants` Pydantic schemas (in `src/utils/extra_configs.py`, alongside `Metadata`) read an optional `batch:` block in `config.yaml` — `count`, `strategy` (`random`/`cycle`), and per-field lists (`topic`, `tone`, `target_audience`, `video_length_seconds`, `platform`, `pov`) plus an optional list of `generation_type`s to rotate through. Absent `batch:` = today's single-run behavior.
- New `src/batch.py` `BatchRunner` (runtime dataclass, not the schema) consumes `BatchConfig`, samples one `Metadata`/`generation_type` per iteration, and drives one `PipelineBuilder` per session — catching and logging per-session exceptions so one failure doesn't kill the batch (addresses #4 too).
- Topic *content* sourcing should follow the **existing 3-registry pattern** (`PROVIDER_REGISTER`/`TTS_REGISTER`/`TR_REGISTER`) rather than being jammed into the config-level lists above: a new `src/topics/` package with a `TOPIC_REGISTER` and backends — `list` (the config-driven `MetadataVariants.topic`, fine for cheap human-curated variation like quotes), `file` (mirrors `utils.Downloaded`'s folder + JSON-sidecar pattern for pre-collected content, e.g. scraped Reddit stories), `feed` (future: RSS/API pull for live niche content like F1 recaps). Each `GenerationType` entry (`src/generation_types/__init__.py`) would declare its default topic source, since the right source is a property of the content type, not a global setting — config-level `variants.topic` stays for cheap style axes (tone/pov/audience/length) that apply regardless of source.

## Gotcha: Ollama reasoning models and `num_ctx`

The configured models are qwen3-family **reasoning models**: they emit thousands of "thinking" tokens (in a separate `thinking` field) before producing `content`. Ollama's default context window (`num_ctx=4096`) is too small — the response truncates mid-thought (`done_reason == "length"`) and `message.content` comes back **empty/None** even though the model clearly ran. `Ollama.prompt()` passes a larger `num_ctx` (default 8192, override via config) and raises a clear error on truncation instead of returning empty content. Keep that headroom when adding models or longer prompts.
