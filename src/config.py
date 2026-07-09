# Read the config from the file
import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict, BaseSettings
from .providers import Base
from . import generation_types
from . import TTS

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

class Metadata(BaseModel):
    topic: str
    tone: str
    target_audience: str
    video_length_seconds: int
    platform: generation_types.schemas.Platform
    pov: generation_types.schemas.POV


class AppConfig(BaseModel):
    generation_type: str
    metadata: Metadata
    provider: Base.ProviderConfig
    tts: TTS.Base.TTSConfig

    @field_validator('generation_type', mode='after')
    @classmethod
    def check_generation_type(cls, value:str):
        if value not in generation_types.GENERATION_TYPES.keys():
            raise ValueError('Generation type {} is not supported'.format(value))
        return value

    @model_validator(mode='after')
    def inject_prompt(self):
        generation_obj = generation_types.GENERATION_TYPES[self.generation_type]
        prompt_text = generation_obj.prompt_file.read_text()
        for key, value in self.metadata.model_dump(mode='json').items():
            prompt_text = prompt_text.replace('{{' + key + '}}', str(value))
        self.provider.prompt = prompt_text
        return self


class Secrets(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)
    youtube_api_key: str               # <- from env YOUTUBE_API_KEY, errors if missing
    elevenlabs_api_key: str | None = None


        
