import yaml
import dataclasses
from pydantic import BaseModel, Field, field_validator
from pathlib import Path

TR_REGISTER = dict()

def register(cls):
    TR_REGISTER[cls.__name__.lower()] = cls
    return cls

class TranscribeConfig(BaseModel):
    name: str
    model: str
    url: str = "http://127.0.0.1:11434"

    @field_validator('name', mode='after')
    @classmethod
    def check_model(cls, value:str):
        if value not in TR_REGISTER.keys():
            raise ValueError('Provider {} is not supported: Supported Provider are: {}'.format(value, TR_REGISTER.keys()))
        return value

@dataclasses.dataclass
class BaseTR:
    config: TranscribeConfig
    secrets: type[BaseModel] = None

    @property
    def models(self):
        return ()

    def __post_init__(self):
        self.check_model()

    def check_model(self):
        if not self.config.model in self.models:
            raise ValueError(
                f'Model {self.config.model} is not supported, list of supported models are: {self.models}')

    def transcribe(self, audio_file:Path, output_path:Path):
        raise NotImplementedError("Subclasses must implement the prompt method")

