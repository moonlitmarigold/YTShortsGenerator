# Read the config from the file
import os
from pathlib import Path
import yaml

class Config:
    
    def __init__(self, config_file:Path, env_file:Path) -> None:
        self.config_file = config_file
        self.env_file = env_file
        
    def read(self):
        config: yaml.YAMLObject = self._read_config()
        print(config)
        
        # TODO: validate config
        
        generation_types = Path("src/generation_types").iterdir()
        generation_types = [x.name.split('.')[0] for x in generation_types]
        
        if config['generation_type'] not in generation_types:
            raise ValueError('No such generation_type {}'.format(config['generation_type']))
        
        config = self._add_prompt(config)
        
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
    
    def _add_prompt(self, config):
        path_to_yaml = Path("src/generation_types") / str(config['generation_type'] + '.yaml')
        print(path_to_yaml)
        prompt = yaml.safe_load(path_to_yaml.open())['prompt']
        
        config['prompt'] = prompt
        
        return config
        
