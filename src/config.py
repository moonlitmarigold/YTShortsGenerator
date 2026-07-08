# Read the config from the file
import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict, BaseSettings
from .providers import Base
from . import generation_types

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

def open_config_env():
    config_file = find_config_file()
    env_file = find_env_file()

    app_config = AppConfig.model_validate(yaml.safe_load(config_file.read_text()))
    env = Secrets(_env_file=env_file)
    return app_config, env

class AppConfig(BaseModel):
    generation_type: str
    provider: Base.ProviderConfig

    @field_validator('generation_type', mode='before')
    @classmethod
    def check_generation_type(cls, value:str):
        if value not in generation_types.GENERATION_TYPES.keys():
            raise ValueError('Generation type {} is not supported'.format(value))
        return value

    @model_validator(mode='after')
    def inject_prompt(self):
        generation_obj =generation_types.GENERATION_TYPES[self.generation_type]
        raw = yaml.safe_load(generation_obj.prompt_file.read_text())
        self.provider.prompt = raw['prompt']
        return self


class Secrets(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)
    youtube_api_key: str               # <- from env YOUTUBE_API_KEY, errors if missing
    elevenlabs_api_key: str | None = None


        
