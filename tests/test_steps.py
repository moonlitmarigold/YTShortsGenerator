from pathlib import Path
from src import config, sessions
from src.classes import Prompt, Tts, Transcribe, Audio, background, Planner, subtitles
import shutil
from pydub import AudioSegment

input_parse = '''
```json
{
  "video_metadata": {
    "suggested_title": "Your Code Isn't Your Worth",
    "key_theme": "Burnout is not a personal failure; it is a systemic signal that your energy resources must be managed as carefully as any production deployment.",
    "video_description": "Why peak performance isn't about logging more hours. Send this to a teammate who needs to hear it.",
    "tags": ["burnout", "softwareengineering", "productivity", "mentalhealth"],
    "total_duration_seconds": 40,
    "platform": "reels"
  },
  "style_defaults": {
    "font_family": "Bebas Neue",
    "font_size": 44,
    "primary_text_color": "#FFFFFF",
    "highlight_color": "#9B59B6",
    "text_position": "center",
    "background_color": "#1A1A1A",
    "highlighting": {
      "enabled": true,
      "word_max": 0,
      "as_borders": false,
      "fade_ms": [50, 50],
      "appear": false,
      "font_size": 52
    }
  },
  "scenes": [
    {
      "id": 1,
      "type": "hook",
      "spoken_text": "You feel like you're always running—that your worth is tied to the last pull request.",
      "duration_ms": 3500,
      "style_override": null
    },
    {
      "id": 2,
      "type": "quote_core",
      "spoken_text": "Remember that you are not a CPU core running at peak capacity. You need scheduled downtime.",
      "duration_ms": 6000,
      "style_override": {
        "primary_text_color": "#EAEAEA"
      }
    },
    {
      "id": 3,
      "type": "body",
      "spoken_text": "Burnout isn't a personal failure. It’s a systemic resource management problem that companies often forget to factor in.",
      "duration_ms": 6000,
      "style_override": null
    },
    {
      "id": 4,
      "type": "body",
      "spoken_text": "Peak performance isn't about logging the most hours. It’s about designing sustainable systems—including your own mental health.",
      "duration_ms": 8000,
      "style_override": null
    },
    {
      "id": 5,
      "type": "body",
      "spoken_text": "Build in the downtime. Treat your rest time like you treat a critical deployment—non-negotiable.",
      "duration_ms": 7000,
      "style_override": null
    },
    {
      "id": 6,
      "type": "call_to_action",
      "spoken_text": "If this resonates, send it to the teammate who needs a reminder that they are allowed to rest.",
      "duration_ms": 9000,
      "style_override": null
    }
  ],
  "video_guidance": {
    "pacing_recommendation": "moderate_with_pauses",
    "music_genre": "piano_minimal",
    "music_energy_curve": "low, thoughtful intro, subtle swell at quote_core and body 2, fading back to a calm resolve through CTA",
    "background_genre": "satisfying_asmr"
  }
}
```
'''

def init():
    app_config, env = config.open_config_env()

    session = sessions.SessionInfo.from_config(app_config)
    session.inject_prompt_output(Prompt.Prompt._parse_output(input_parse), input_parse)
    return app_config, env, session

def add_audio(session:sessions.SessionInfo):
    script = session.script
    base_audio = Path(__file__).parent / 'test_audio_track.wav'
    for scene in script.scenes:
        audio_path = session.audio_path(scene.id)
        shutil.copy(base_audio, audio_path)

def add_transcript(session:sessions.SessionInfo):
    script = session.script
    base_transcript = Path(__file__).parent / 'transcript.srt'
    for scene in script.scenes:
        output_path = session.transcribe_path(scene.id)
        shutil.copy(base_transcript, output_path)

def full_audio(session:sessions.SessionInfo):
    base_audio = Path(__file__).parent / 'test_audio_track.wav'
    new_audio = AudioSegment.silent(0)

    script = session.script
    for scene in script.scenes:
        new_audio += AudioSegment.from_file(str(base_audio))

    new_audio.export(str(session.full_audio_path()))

def background_video(session:sessions.SessionInfo):
    base_video = Path(__file__).parent / "background_video.mp4"

    shutil.copy(base_video, session.background_video())


def test_subtitles():
    app_config, env, session = init()
    add_transcript(session)
    background_video(session)

    try:
        s = subtitles.Subtitles(app_config.resolution)
        s.run(session)
    except Exception as e:
        raise e
    finally:
        pass
        #session.delete()

def test_background():
    app_config, env, session = init()
    full_audio(session)
    print(session.file)

    try:
        b = background.Background(app_config.resolution)
        b.run(session)
    except Exception as e:
        raise e
    finally:
        session.delete()

def test_prompt():
    app_config, env = config.open_config_env()

    session = sessions.SessionInfo.from_config(app_config)
    #session.inject_prompt_output(Prompt.Prompt._parse_output(input_parse), input_parse)
    try:
        pl = Planner.Planner(
            app_config.generation_type,
            app_config.metadata,
            env
        )
        pl.run(session)
        p = Prompt.Prompt(app_config.provider, env)
        p.run(session)
    except Exception as e:
        raise e
    finally:
        session.delete()

def test_tts():
    app_config, env, session = init()

    try:
        t = Tts.TTS(app_config.tts, env)
        t.run(session)
    except Exception as e:
        raise e
    finally:
        session.delete()


def test_transcribe():
    app_config, env, session = init()
    # inject audio before running
    add_audio(session)

    try:
        tr = Transcribe.Transcribe(app_config.transcribe, env)
        tr.run(session)
    except Exception as e:
        raise e
    finally:
        pass
        #session.delete()


def test_audio():
    app_config, env, session = init()
    add_audio(session)
    try:
        audio = Audio.Audio(app_config.audio, env)
        audio.run(session)
    except Exception as e:
        raise e
    finally:
        session.delete()

