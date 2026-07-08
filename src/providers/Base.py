import yaml
import dataclasses
from pydantic import BaseModel, Field, field_validator
from .. import generation_types

PROVIDER_REGISTER = dict()

def register(cls):
    PROVIDER_REGISTER[cls.__name__.lower()] = cls
    return cls

class ProviderConfig(BaseModel):
    name: str
    model: str
    url: str = "http://127.0.0.1:11434"  # the fallback lives here now
    num_ctx: int = Field(default=8192, ge=8192)
    prompt: str | None = None  # inject after load
    # Holds the GenerationOutput *subclass* (used as a factory in Prompt.run), not an
    # instance. Excluded from serialization: it's injected from generation_type, and a
    # class object isn't JSON-serializable (PydanticSerializationError otherwise).
    generation_output: type[generation_types.schemas.GenerationOutput] | None = Field(default=None, exclude=True)

    @field_validator('name', mode='after')
    @classmethod
    def check_model(cls, value:str):
        if value not in PROVIDER_REGISTER.keys():
            raise ValueError('Provider {} is not supported: Supported Provider are: {}'.format(value, PROVIDER_REGISTER.keys()))
        return value

@dataclasses.dataclass
class BaseProvider:
    config: ProviderConfig

    _fallback_provider_url:str = "" # For the providers to specify their default URL if not provided in the config

    def provider_url(self) -> str:
        if not self._fallback_provider_url:
            return self.config.url
        if self.config.url != self._fallback_provider_url:
            return self._fallback_provider_url
        return self.config.url

    @property
    def num_ctx(self) -> int:
        return self.config.num_ctx

    @property
    def model(self):
        return self.config.model

    def prompt(self) -> str:
        raise NotImplementedError("Subclasses must implement the prompt method")
