from pydantic import BaseModel, field_validator, model_validator
import dataclasses

TTS_REGISTER = dict()

def register(cls):
    TTS_REGISTER[cls.__name__.lower()] = cls
    return cls

class TTSConfig(BaseModel):

    name:str
    tts_model:str
    voice:str
    sample_rate:int = 24000

    @field_validator('name', mode='after')
    @classmethod
    def check_model(cls, value:str):
        if value not in TTS_REGISTER.keys():
            raise ValueError('TTS-Provider {} is not supported: Supported TTS-Provider are: {}'.format(value, TTS_REGISTER.keys()))
        return value


@dataclasses.dataclass()
class BaseTTS:

    config: TTSConfig
    secrets: type[BaseModel] = None

    @property
    def models(self):
        return ()

    @property
    def voices(self):
        return ()

    def __post_init__(self):
        self.check_model()
        self.check_voice()

    def check_model(self):
        if not self.config.tts_model in self.models:
            raise ValueError(f'Model {self.config.tts_model} is not supported, list of supported models are: {self.models}')

    def check_voice(self):
        if self.config.voice not in self.voices:
            raise ValueError(f'Voice {self.config.voice} is not supported, list of supported voices on this model are: {self.voices}')

    def audio(self, text:str):
        raise NotImplementedError()
