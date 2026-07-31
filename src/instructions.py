from .sessions import SessionInfo
from .pipeline import PipelineBuilder, Pipeline
from .utils import errors
from typing import Callable, Optional
import dataclasses
import json
import os
import subprocess
import tempfile
from pathlib import Path
from rich.console import Console

@dataclasses.dataclass
class Instruction:

    session:Optional[SessionInfo] = None
    _exec:Optional[Callable] | Optional[str] = None

    _pipeline_exec:bool = False

    def __call__(self):
        if self._pipeline_exec:
            with PipelineBuilder(self.config_file, self.env_file) as pipeline_builder:
                pipeline_builder.build_list(
                    self._exec,
                    self.session
                )
                _pipeline = pipeline_builder.build()
                _pipeline.run()
        else:
            if self.session is None and self._exec is None:
                raise RuntimeError('Both values cant be none')
            self._exec(self.session)

    @property
    def config_file(self):
        if 'config_path' in os.environ:
            return Path(os.environ['config_path'])
        raise errors.ConfigFileNotSet()

    @property
    def env_file(self):
        if 'env_path' in os.environ:
            return Path(os.environ['env_path'])
        raise errors.ConfigFileNotSet()

    def is_pipeline(self):
        self._pipeline_exec = True
        return self

    @classmethod
    def delete(cls, session:SessionInfo):
        return Instruction(
            session,
            SessionInfo.delete
        )

    @classmethod
    def new(cls):
        return Instruction().is_pipeline()

    @classmethod
    def restart(cls, session:SessionInfo):
        return Instruction(
            session,
            'Prompt',
        ).is_pipeline()

    @classmethod
    def restart_from_step(cls, session:SessionInfo, step:Optional[str] = None):
        return Instruction(
            session,
            session.step if not step else step,
        ).is_pipeline()

    @classmethod
    def upload(cls, session:SessionInfo):
        pass

    @classmethod
    def show_script(cls, session:SessionInfo):
        return Instruction(
            session,
            cls._print_script,
        )

    @staticmethod
    def _print_script(session: SessionInfo):
        raw = session.generation_session.raw_llm_output
        if not raw:
            Console().print("[yellow]No script generated yet for this session.[/yellow]")
            return

        from .classes import Prompt
        try:
            data = Prompt.Prompt.clean_and_parse_json(raw)
        except (ValueError, json.JSONDecodeError):
            data = raw

        print(json.dumps(data, indent=2, default=str))

    @classmethod
    def edit_script(cls, session:SessionInfo):
        return Instruction(
            session,
            cls._edit_script,
        )

    @staticmethod
    def _edit_script(session: SessionInfo):
        console = Console()
        raw = session.generation_session.raw_llm_output
        if not raw:
            console.print("[yellow]No script generated yet for this session.[/yellow]")
            return

        from .classes import Prompt
        try:
            data = Prompt.Prompt.clean_and_parse_json(raw)
            text = json.dumps(data, indent=2, ensure_ascii=False)
        except (ValueError, json.JSONDecodeError):
            text = raw

        editor = os.environ.get('EDITOR', 'nvim')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write(text)
            tmp_path = Path(f.name)

        try:
            while True:
                subprocess.run([editor, str(tmp_path)])
                edited_text = tmp_path.read_text(encoding='utf-8')

                try:
                    script = Prompt.Prompt._parse_output(edited_text)
                except Exception as e:
                    console.print(f"[red]Edited script is not valid: {e}[/red]")
                    retry = console.input("[bold]Re-open in editor to fix? (Y/n): [/bold]").strip().lower()
                    if retry in ('', 'y', 'yes'):
                        continue
                    console.print("[yellow]Discarding edits.[/yellow]")
                    return

                session.inject_prompt_output(script, edited_text)
                session.save()
                console.print("[green]Script updated.[/green]")
                return
        finally:
            tmp_path.unlink(missing_ok=True)

