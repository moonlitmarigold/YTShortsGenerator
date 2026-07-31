import pydantic
from . import config, sessions
from .classes import Prompt, Tts, Transcribe, Audio, Planner, background as _back, video as vid, subtitles as sub, thumbnail as thumb, Upload
from pathlib import Path
from typing import Callable, Optional
from .utils import errors, extra_configs, rich_progress
from rich.progress import Progress

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

        with Progress() as progress:
            rich_progress.set_progress(progress)
            try:
                task = progress.add_task('Running pipeline', total=len(self.steps))

                for key, value in self.steps.items():
                    progress.update(task, description=f'Running step: {key}')
                    logger.info('Running step: {}'.format(key))
                    try:
                        self.session_obj.set_step(key)
                        self.session_obj.save()

                        value.run(self.session_obj)
                        logger.info('Finished step: {}'.format(key))
                        progress.advance(task)

                        # If a step ran without issues, delete any error messages, as they might me missleading
                        self.session_obj.clear_error()
                    except Exception as e:
                        logger.error('Error running step {}: {}'.format(key, e))
                        self.session_obj.set_error(str(e))
                        self.session_obj.set_status(sessions.Status.FAILED)
                        self.session_obj.save()
                        raise e
            finally:
                rich_progress.set_progress(None)

        self.session_obj.set_status(sessions.Status.FINISHED)
        self.session_obj.save()
        logger.info('Finished with the pipeline')
    
class PipelineBuilder:

    steps = (
        'Planner',
        'Prompt',
        'TTS',
        'Transcribe',
        'Audio',
        'Background',
        'Thumbnail',
        'Subtitles',
        'Video',
    )
    
    def __init__(self, path_config:Path | None = None, path_env:Path | None = None):
        self.pipeline = Pipeline()
        self.path_config = path_config
        self.path_env = path_env
        self.app_config:config.AppConfig = None
        self.env_config:extra_configs.Secrets = None

        self._build_list:tuple[Callable] = ()

        self.__base_build_list = {
            'Planner': self.plan,
            'Prompt': self.prompt,
            'TTS': self.tts,
            'Transcribe': self.transcribe,
            'Audio': self.audio,
            'Background': self.background,
            'Thumbnail': self.thumbnail,
            'Subtitles': self.subtitles,
            'Video': self.video,
        }



    def add_steps(self, **kwargs):
        self.pipeline.add_steps(**kwargs)

    def build_list(self, start_step:Optional[str]=None, session_obj:Optional[sessions.SessionInfo]=None):
        logger.info(f'Using start step {start_step} for building the build_list')

        _list = [self._config]
        if session_obj:
            self.pipeline.set_session_obj(session_obj)
        else:
            _list.append(self.session)

        if start_step and not start_step == 'Upload':
            keys = [str(x) for x in self.__base_build_list.keys()]
            _index = keys.index(start_step)
            values = [x for x in self.__base_build_list.values()]
            _list.extend(values[_index:])
        elif start_step and start_step == 'Upload':
            _list.append(self.upload)
        else:
            _list.extend(self.__base_build_list.values())
        self._build_list = _list
        return self


    def build(self):
        if not self._build_list:
            raise errors.NoPipelineBuildList()

        logger.debug('Building pipeline')

        logger.info('Building pipeline with {} steps'.format(len(self._build_list)))
        for step in self._build_list:
            step()

        logger.info('Finished Building the pipeline')

        return self.pipeline

    def _config(self):
        logger.debug('Loading in config')
        self.app_config, self.env_config = config.open_config_env(self.path_config, self.path_env)
        logger.debug('config after loading:\n{}'.format(self.app_config.model_dump_json()))

    def prompt(self):
        p = Prompt.Prompt(self.app_config.provider, self.env_config)
        self.add_steps(Prompt=p)

    def session(self, _session_obj:Optional[sessions.SessionInfo] = None):
        s = sessions.SessionInfo.from_config(self.app_config)
        self.pipeline.set_session_obj(s)

    def tts(self):
        t = Tts.TTS(self.app_config.tts, self.env_config)
        self.add_steps(TTS=t)

    def transcribe(self):
        t = Transcribe.Transcribe(self.app_config.transcribe, self.env_config)
        self.add_steps(Transcribe=t)

    def audio(self):
        a = Audio.Audio(self.app_config.audio, self.env_config)
        self.add_steps(Audio=a)

    def plan(self):
        p = Planner.Planner(
            self.app_config.generation_type,
            self.app_config.metadata,
            self.env_config
        )
        self.add_steps(Planner=p)

    def background(self):
        b = _back.Background(self.app_config.resolution, self.app_config.background_speed)
        self.add_steps(Background=b)

    def thumbnail(self):
        t = thumb.Thumbnail(self.app_config.resolution)
        self.add_steps(Thumbnail=t)

    def subtitles(self):
        s = sub.Subtitles(self.app_config.resolution)
        self.add_steps(Subtitles=s)

    def video(self):
        v = vid.Video()
        self.add_steps(Video=v)

    def upload(self):
        if self.app_config.uploader is None:
            return
        u = Upload.Upload(self.app_config.uploader, self.env_config)
        self.add_steps(Upload=u)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None