import os
from pathlib import Path
import sys
from src import config
from src.providers import Ollama
from src import pipeline
import yaml

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

def test_pipeline_build():
    config_file = Path('config.yaml')
    env_file = Path('.env')

    with pipeline.PipelineBuilder(config_file, env_file) as pipeline_builder:
        _pipeline = pipeline_builder.build()

    print(_pipeline.run())

