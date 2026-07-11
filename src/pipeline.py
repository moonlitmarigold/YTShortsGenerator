import pydantic
from . import config, sessions
from .classes import Prompt, Tts, Transcribe, Audio
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class Pipeline:
    
    def __init__(self):
        self.steps = dict()
        self.session_obj:sessions.SessionInfo = None

    def add_steps(self, **kwargs):
        for key, value in kwargs.items():
            self.steps[key] = value

    def set_session_obj(self, obj):
        self.session_obj = obj

    def run(self):
        logger.info('Starting pipeline with {} steps'.format(len(self.steps)))

        self.session_obj.set_status(sessions.Status.RUNNING)

        for key, value in self.steps.items():
            logger.info('Running step: {}'.format(key))
            try:
                value.run(self.session_obj)
                logger.info('Finished step: {}'.format(key))
                self.session_obj.set_step(key)
                self.session_obj.save()
            except Exception as e:
                logger.error('Error running step {}: {}'.format(key, e))
                self.session_obj.set_error(str(e))
                self.session_obj.set_status(sessions.Status.FAILED)
                raise e

        self.session_obj.set_status(sessions.Status.FINISHED)
        logger.info('Finished with the pipeline')
    
class PipelineBuilder:
    
    def __init__(self, path_config:Path | None = None, path_env:Path | None = None):
        self.pipeline = Pipeline()
        self.path_config = path_config
        self.path_env = path_env
        self.app_config:config.AppConfig = None
        self.env_config:config.Secrets = None


    def add_steps(self, **kwargs):
        self.pipeline.add_steps(**kwargs)

    def build_list(self):
        return (
            self._config,
            self._session,
            self._prompt,
            self._tts,
            self._transcribe,
            self._audio,
        )

    def build(self):
        logger.debug('Building pipeline')
        build_list = self.build_list()

        logger.info('Building pipeline with {} steps'.format(len(build_list)))
        for step in build_list:
            step()

        logger.info('Finished Building the pipeline')

        return self.pipeline

    def _config(self):
        logger.debug('Loading in config')
        self.app_config, self.env_config = config.open_config_env(self.path_config, self.path_env)
        logger.debug('config after loading:\n{}'.format(self.app_config.model_dump_json()))

    def _prompt(self):
        p = Prompt.Prompt(self.app_config.provider, self.env_config)
        self.add_steps(Prompt=p)

    def _session(self):
        s = sessions.SessionInfo.from_config(self.app_config)
        self.pipeline.set_session_obj(s)

    def _tts(self):
        t = Tts.TTS(self.app_config.tts, self.env_config)
        self.add_steps(TTS=t)

    def _transcribe(self):
        t = Transcribe.Transcribe(self.app_config.transcribe, self.env_config)
        self.add_steps(transcribe=t)

    def _audio(self):
        a = Audio.Audio(self.app_config.audio, self.env_config)
        self.add_steps(Audio=a)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None