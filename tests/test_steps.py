import os
import shutil
from pathlib import Path
from src.generation_types import schemas
from src import config, sql, sessions
from src.classes import Prompt, Tts, Transcribe, Audio, background, subtitles
import shutil

input_parse = '''
```json
{
  "video_metadata": {
    "suggested_title": "Your Code Isn't Your Worth",
    "key_theme": "Burnout is not a personal failure; it is a systemic signal that your energy resources must be managed as carefully as any production deployment.",
    "total_duration_seconds": 40,
    "platform": "reels"
  },
  "style_defaults": {
    "font_family": "Inter Semibold",FAILED                                                                   [100%]['```json', '{', '  "video_metadata": {', '    "suggested_title": "Stop Judging Yourself For Procrastinating",', '    "key_theme": "Procrastination is not a moral failing or lack of discipline; it is an emotional regulation strategy to avoid temporary feelings of failure.",', '    "total_duration_seconds": 29,', '    "platform": "shorts"', '  },', '  "style_defaults": {', '    "font_family": "Poppins Medium",', '    "font_size": "large",', '    "primary_text_color": "#FFFFFF",', '    "highlight_color": "#34A853",', '    "text_position": "center",', '    "background_overlay": "subtle_dark_gradient"', '  },', '  "scenes": [', '    {', '      "id": 1,', '      "type": "hook",', '      "spoken_text": "You know you should start writing the paper, but your brain feels like hitting a brick wall.",', '      "display_mode": "highlighted_keywords",', '      "on_screen_text": "Should start writing. Feels like a brick wall.",', '      "highlight_words": [', '        {"word": "brick wall", "emphasis": "size_pop"}', '      ],', '      "duration_ms": 3000,', '      "style_override": null', '    },', '    {', '      "id": 2,', '      "type": "quote_core",', '      "spoken_text": "Procrastination isn\'t a failure of discipline. It’s your brain trying to protect you from the temporary feeling of being inadequate.",', '      "display_mode": "word_by_word",', '      "on_screen_text": [', '        "It\'s not lack of discipline.",', '        "It\'s protection.",', '        "From inadequacy."', '      ],', '      "highlight_words": [', '        {"word": "protect", "emphasis": "color_pop"}', '      ],', '      "duration_ms": 4500,', '      "style_override": {', '        "font_size": "xlarge",', '        "primary_text_color": "#FFFFFF"', '      }', '    },', '    {', '      "id": 3,', '      "type": "body",', '      "spoken_text": "You are demanding a perfect first draft. And the gap between \'perfect\' and \'good enough\' is massive—and paralyzing.",', '      "display_mode": "highlighted_keywords",', '      "on_screen_text": "Demanding a perfect first draft. It’s paralyzing.",', '      "highlight_words": [', '        {"word": "paralyzing", "emphasis": "underline"}', '      ],', '      "duration_ms": 5000,', '      "style_override": null', '    },', '    {', '      "id": 4,', '      "type": "body",', '      "spoken_text": "So stop aiming for brilliance. For the next ten minutes, your only goal is to create something so bad it\'s embarrassing.",', '      "display_mode": "highlighted_keywords",', '      "on_screen_text": "Create something so bad... just get words down.",', '      "highlight_words": [', '        {"word": "bad", "emphasis": "shake"}', '      ],', '      "duration_ms": 6000,', '      "style_override": null', '    },', '    {', '      "id": 5,', '      "type": "body",', '      "spoken_text": "Lower the stakes. Just get five random sentences on paper. That\'s it. The pressure is removed.",', '      "display_mode": "full_sentence",', '      "on_screen_text": "Just get five random sentences. That’s enough.",', '      "highlight_words": [', '        {"word": "five", "emphasis": "color_pop"}', '      ],', '      "duration_ms": 5000,', '      "style_override": null', '    },', '    {', '      "id": 6,', '      "type": "call_to_action",', '      "spoken_text": "Next time you feel blocked, remember: the goal is completion, not perfection. Save this video.",', '      "display_mode": "full_sentence",', '      "on_screen_text": "Goal = Completion. Not Perfection. ⬇️",', '      "highlight_words": [', '        {"word": "completion", "emphasis": "size_pop"}', '      ],', '      "duration_ms": 4000,', '      "style_override": null', '    }', '  ],', '  "video_guidance": {', '    "pacing_recommendation": "moderate_with_pauses",', '    "music_genre": "piano_minimal",', '    "music_energy_curve": "gentle build through body scenes, slight swell at quote_core, steady resolve through CTA"', '  }', '}', '```']

    "font_size": "medium",
    "primary_text_color": "#FFFFFF",
    "highlight_color": "#9B59B6",
    "text_position": "center",
    "background_overlay": "subtle_dark_gradient"
  },
  "scenes": [
    {
      "id": 1,
      "type": "hook",
      "spoken_text": "You feel like you're always running—that your worth is tied to the last pull request.",
      "display_mode": "highlighted_keywords",
      "on_screen_text": "Worth tied to the last PR?",
      "highlight_words": [
        {"word": "worth", "emphasis": "color_pop"}
      ],
      "duration_ms": 3500,
      "style_override": null
    },
    {
      "id": 2,
      "type": "quote_core",
      "spoken_text": "Remember that you are not a CPU core running at peak capacity. You need scheduled downtime.",
      "display_mode": "word_by_word",
      "on_screen_text": [
        "You are not",
        "a CPU core",
        "running at peak capacity.",
        "Scheduled downtime."
      ],
      "highlight_words": [
        {"word": "downtime", "emphasis": "size_pop"}
      ],
      "duration_ms": 6000,
      "style_override": {
        "font_size": "xlarge",
        "primary_text_color": "#EAEAEA"
      }
    },
    {
      "id": 3,
      "type": "body",
      "spoken_text": "Burnout isn't a personal failure. It’s a systemic resource management problem that companies often forget to factor in.",
      "display_mode": "full_sentence",
      "on_screen_text": "It's a systematic resource problem.",
      "highlight_words": [
        {"word": "systemic", "emphasis": "underline"}
      ],
      "duration_ms": 6000,
      "style_override": null
    },
    {
      "id": 4,
      "type": "body",
      "spoken_text": "Peak performance isn't about logging the most hours. It’s about designing sustainable systems—including your own mental health.",
      "display_mode": "highlighted_keywords",
      "on_screen_text": "Design sustainable systems (mental health).",
      "highlight_words": [
        {"word": "sustainable", "emphasis": "shake"}
      ],
      "duration_ms": 8000,
      "style_override": null
    },
    {
      "id": 5,
      "type": "body",
      "spoken_text": "Build in the downtime. Treat your rest time like you treat a critical deployment—non-negotiable.",
      "display_mode": "word_by_word",
      "on_screen_text": [
        "Build in the downtime.",
        "Treat it like a critical deployment:",
        "Non-negotiable."
      ],
      "highlight_words": [
        {"word": "non-negotiable", "emphasis": "color_pop"}
      ],
      "duration_ms": 7000,
      "style_override": null
    },
    {
      "id": 6,
      "type": "call_to_action",
      "spoken_text": "If this resonates, send it to the teammate who needs a reminder that they are allowed to rest.",
      "display_mode": "full_sentence",
      "on_screen_text": "Send this to a struggling coworker.",
      "highlight_words": [
        {"word": "allowed to rest", "emphasis": "size_pop"}
      ],
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


def test_prompt():
    app_config, env = config.open_config_env()

    session = sessions.SessionInfo.from_config(app_config)
    #session.inject_prompt_output(Prompt.Prompt._parse_output(input_parse), input_parse)
    try:
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

        session.delete()
    except Exception as e:
        raise e
    finally:
        session.delete()


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

def test_background():
    app_config, env, session = init()

    try:
        b = background.Background()
        b.run(session)
    except Exception as e:
        raise e
    finally:
        session.delete()