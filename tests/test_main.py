from pathlib import Path
from src import pipeline, utils

def test_pipeline_build():
    config_file = Path('config.yaml')
    env_file = Path('.env')

    with pipeline.PipelineBuilder(config_file, env_file) as pipeline_builder:
        _pipeline = pipeline_builder.build()

    print(_pipeline.run())