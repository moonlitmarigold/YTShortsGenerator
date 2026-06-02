import yaml

from . import config
from .classes import Prompt
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class Pipeline:
    
    def __init__(self):
        self.steps = dict()

    def add_steps(self, **kwargs):
        for key, value in kwargs.items():
            self.steps[key] = value

    def run(self):
        logger.info('Starting pipeline with {} steps'.format(len(self.steps)))
        for key, value in self.steps.items():
            logger.debug('Running step: {}'.format(key))
            try:
                value.run()
            except Exception as e:
                logger.error('Error running step {}: {}'.format(key, e))
                raise e
    
class PipelineBuilder:
    
    def __init__(self, path_config:Path, path_env:Path):
        self.pipeline = Pipeline()
        self.path_config = path_config
        self.path_env = path_env


    def add_steps(self, **kwargs):
        self.pipeline.add_steps(**kwargs)

    def build_list(self):
        return (
            self._prompt,
        )

    def build(self):
        logger.debug('Building pipeline')
        logger.debug('Loading in config')
        _conf = self._config()
        logger.debug('config after loading:\n{}'.format(yaml.dump(_conf, default_flow_style=False, indent=4, width=80)))
        build_list = self.build_list()

        logger.info('Building pipeline with {} steps'.format(len(build_list)))
        for step in build_list:
            step(_conf)

        logger.info('Finished Building the pipeline')

        # TODO: validate pipeline // use extra parameters fro required parameters in the steps
        return self.pipeline

    def _config(self):
        c = config.Config(self.path_config, self.path_env)
        _conf = c.read()
        return _conf

    def _prompt(self, _conf:yaml.YAMLObject):
        p = Prompt.Prompt(_conf)
        self.add_steps(Prompt=p)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None