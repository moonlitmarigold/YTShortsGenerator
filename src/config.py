# Read the config from the file
import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from .providers import Base
from .generation_types import GENERATION_TYPES
from . import TTS
from . import Transcribe
from .utils import Secrets, AudioConfig, schemas, extra_configs
from typing import Optional

def find_config_file() -> Path:
    """Search for config.yaml in the current directory and parent directories."""
    possible_path = Path(os.curdir) / "config.yaml"
    if possible_path.exists():
        return possible_path.resolve()
    raise FileNotFoundError("No config.yaml found in current or parent directories.")

def find_env_file() -> Path:
    """Search for .env in the current directory and parent directories."""
    possible_path = Path(os.curdir) / ".env"
    if possible_path.exists():
        return possible_path.resolve()
    raise FileNotFoundError("No .env file found in current or parent directories.")

def open_config_env(conf_file:Path | None = None, env_file:Path | None = None):
    if conf_file is None:
        conf_file = find_config_file()
    if env_file is None:
        env_file = find_env_file()

    app_config = AppConfig.model_validate(yaml.safe_load(conf_file.read_text()))
    env = Secrets(_env_file=env_file)
    return app_config, env


class AppConfig(BaseModel):
    generation_type: str
    metadata: extra_configs.Metadata
    provider: Base.ProviderConfig
    tts: TTS.Base.TTSConfig
    transcribe:Transcribe.Base.TranscribeConfig
    audio:AudioConfig
    background:Optional[extra_configs.SubtitleBackground] = None
    background_speed: float = Field(default=1.1, ge=1.0, le=1.1)
    resolution: Optional[tuple[int, int]] = None

    @field_validator('generation_type', mode='after')
    @classmethod
    def check_generation_type(cls, value:str):
        if value not in GENERATION_TYPES.keys():
            raise ValueError('Generation type {} is not supported'.format(value))
        return value

    @model_validator(mode='after')
    def resolve_resolution(self):
        if self.resolution is None:
            self.resolution = GENERATION_TYPES[self.generation_type].resolution
        return self



        
