# Read the config from the file
import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict, BaseSettings
from .providers import Base

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

class Config:
    
    def __init__(self, config_file:Path, env_file:Path) -> None:
        self.config_file = config_file
        self.env_file = env_file

    @property
    def current_dir(self):
        return Path(__file__).parent.resolve()

    @property
    def generation_types(self):
        return self.current_dir / "generation_types"
        
    def read(self):
        config: yaml.YAMLObject = self._read_config()
        #print(config)
        
        # TODO: validate config

        generation_types = [entry.name.split('.')[0] for entry in self.generation_types.iterdir()]
        
        if config['generation_type'] not in generation_types:
            raise ValueError('No such generation_type {}'.format(config['generation_type']))
        
        config = self._add_prompt(config)

        #print(config)
        
        return config
        
    def _read_config(self) -> yaml.YAMLObject:
        with self.config_file.open() as f:
            raw = yaml.safe_load(f)
        return self._resolve_env_vars(raw)

    def _resolve_env_vars(self, obj) -> yaml.YAMLObject:
        """Replace ${ENV_VAR} placeholders with actual env values."""
        if isinstance(obj, str) and obj.startswith("${"):
            key = obj[2:-1]
            return os.getenv(key, "")   # fails gracefully, validate after
        if isinstance(obj, dict):
            return {k: self._resolve_env_vars(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._resolve_env_vars(i) for i in obj]
        return obj
    
    def _add_prompt(self, config) -> yaml.YAMLObject:
        path_to_yaml = self.generation_types / str(config['generation_type'] + '.yaml')
        prompt = yaml.safe_load(path_to_yaml.open())['prompt']
        
        config['prompt'] = prompt
        
        return config

class AppConfig(BaseModel):
    generation_type: str
    provider: Base.ProviderConfig
    prompt: str | None = None  # inject after load


class Secrets(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)
    youtube_api_key: str               # <- from env YOUTUBE_API_KEY, errors if missing
    elevenlabs_api_key: str | None = None


        
