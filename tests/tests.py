import os
from pathlib import Path
import sys
from src import config, sql, sessions
from src.providers import Ollama
from src.classes import Prompt
from src import pipeline
import yaml

input_parse = '''{
  "video_metadata": {
    "suggested_title": "Your Code Isn't Your Worth",
    "key_theme": "Burnout is not a personal failure; it is a systemic signal that your energy resources must be managed as carefully as any production deployment.",
    "total_duration_seconds": 40,
    "platform": "reels"
  },
  "style_defaults": {
    "font_family": "Inter Semibold",
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
    "music_energy_curve": "low, thoughtful intro, subtle swell at quote_core and body 2, fading back to a calm resolve through CTA"
  }
}'''

def test_config():
    app_config, env = config.open_config_env()

    print(' ')
    print(app_config)
    print(env)

    assert True

def test_pipeline():

    config_file = Path('config.yaml')
    env_file = Path('.env')

    with pipeline.PipelineBuilder(config_file, env_file) as pipeline_builder:
        _pipeline = pipeline_builder.build()

    assert isinstance(_pipeline, pipeline.Pipeline)

def test_parse():
    print(Prompt.Prompt._parse_output(input_parse))

def test_session():
    app_config, env = config.open_config_env()

    engine = sql.return_engine()
    session = sessions.SessionInfo.from_config(app_config)
    session.inject_prompt_output(Prompt.Prompt._parse_output(input_parse), input_parse)

def test_pipeline_build():
    config_file = Path('config.yaml')
    env_file = Path('.env')

    with pipeline.PipelineBuilder(config_file, env_file) as pipeline_builder:
        _pipeline = pipeline_builder.build()

    print(_pipeline.run())
