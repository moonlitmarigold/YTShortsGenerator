# YouTube Shorts Generator — Python Automation Overview

## Video Types to Generate

| Type | Format | Why it works |
|---|---|---|
| **Facts & trivia** | Hook → fact → explanation → CTA | Easy to batch; fixed structure |
| **Top 5 / 10 lists** | Numbered items with text overlay + voiceover | Countdown format drives retention |
| **Quick tutorials** | Single actionable tip per video | Works for coding, life hacks, productivity |
| **Quote videos** | Animated quote text on looping background | Simplest to fully automate |
| **News recaps** | RSS/scraped headlines → 45–60 s narrated summary | Good for daily upload cadence |
| **Micro fiction** | LLM story + image slideshow + TTS narration | Great for niche channels |

---

## Automation Workflow

### Step 1 — Topic & script generation
Prompt an LLM to produce a title, hook sentence, body (5–10 sentences), and a CTA. Store output as JSON for downstream steps.

**Tools:** `anthropic` SDK, `openai` SDK, `jinja2` (prompt templates)

---

### Step 2 — Text-to-speech narration
Pass the script to a TTS API and save the resulting MP3/WAV. Mix in background music at a lower volume.

**Tools:** `ElevenLabs`, `gTTS`, `pydub`

---

### Step 3 — Visuals & background video
Pull royalty-free stock footage (Pexels API), generate AI images per scene (DALL·E / Stable Diffusion), or compose text-on-background frames with Pillow.

**Tools:** `Pexels API`, `Pillow`, `diffusers`

---

### Step 4 — Subtitle overlay
Transcribe audio with Whisper to get word-level timestamps. Burn animated, word-highlight captions into the video.

**Tools:** `openai-whisper`, `moviepy`, `ffmpeg-python`

---

### Step 5 — Video assembly & encoding
Composite all layers (background, subtitles, watermark) into a **9:16 — 1080×1920 MP4**. Trim to ≤60 s. Target bitrate ~8 Mbps.

**Tools:** `moviepy`, `ffmpeg`

---

### Step 6 — Metadata & thumbnail generation
Auto-generate an SEO title, description, and tags via the LLM. Create a thumbnail by overlaying bold text on a keyframe.

**Tools:** `anthropic` SDK, `Pillow`

---

### Step 7 — Schedule & upload
Upload via the YouTube Data API v3 with a scheduled publish time. Log results to SQLite or Google Sheets. Trigger the pipeline on a cadence.

**Tools:** `google-api-python-client`, `celery`, `sqlite3`

---

## Full Python Stack at a Glance

```
anthropic / openai     →  script & metadata generation
ElevenLabs / gTTS      →  text-to-speech narration
pydub                  →  audio mixing
Pexels API / diffusers →  stock video & AI image sourcing
openai-whisper         →  audio transcription (timestamps)
Pillow                 →  frame composition & thumbnails
moviepy / ffmpeg       →  video assembly & encoding
google-api-python-client → YouTube upload & scheduling
celery + cron          →  pipeline orchestration
sqlite3                →  run logging & tracking
```

---