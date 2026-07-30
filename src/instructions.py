from .sessions import SessionInfo
from .pipeline import PipelineBuilder, Pipeline
from .utils import errors
from typing import Callable, Optional
import dataclasses
import json
import os
from pathlib import Path
from rich.console import Console

@dataclasses.dataclass
class Instruction:

    session:Optional[SessionInfo] = None
    _exec:Optional[Callable] | Optional[str] = None

    _pipeline_exec:bool = False

    def __call__(self):
        if self._pipeline_exec:
            with PipelineBuilder(self.config_file, self.env_file) as pipeline_builder:
                pipeline_builder.build_list(
                    self._exec,
                    self.session
                )
                _pipeline = pipeline_builder.build()
                _pipeline.run()
        else:
            if self.session is None and self._exec is None:
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

    @classmethod
    def restart(cls, session:SessionInfo):
        return Instruction(
            session,
            'Prompt',
        ).is_pipeline()

    @classmethod
    def restart_from_step(cls, session:SessionInfo, step:Optional[str] = None):
        return Instruction(
            session,
            session.step if not step else step,
        ).is_pipeline()

    @classmethod
    def show_script(cls, session:SessionInfo):
        return Instruction(
            session,
            cls._print_script,
        )

    @staticmethod
    def _print_script(session: SessionInfo):
        raw = session.generation_session.raw_llm_output
        if not raw:
            Console().print("[yellow]No script generated yet for this session.[/yellow]")
            return

        from .classes import Prompt
        try:
            data = Prompt.Prompt.clean_and_parse_json(raw)
        except (ValueError, json.JSONDecodeError):
            data = raw

        print(json.dumps(data, indent=2, default=str))

