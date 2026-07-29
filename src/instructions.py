from .sessions import SessionInfo
from .pipeline import PipelineBuilder, Pipeline
from .utils import errors
from typing import Callable, Optional
import dataclasses
import os
from pathlib import Path

@dataclasses.dataclass
class Instruction:

    session:Optional[SessionInfo] = None
    _exec:Optional[Callable] = None

    _pipeline_exec:bool = False

    def __call__(self):
        if self._pipeline_exec:
            with PipelineBuilder(self.config_file, self.env_file) as pipeline_builder:
                pipeline_builder.build_list(
                    self._exec,
                    self.session
                )
                _pipeline = pipeline_builder.build()
        else:
            if not self.session is None and not self._exec is None:
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
        
