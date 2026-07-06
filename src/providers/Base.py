import yaml
import dataclasses
from pydantic import BaseModel, Field

@dataclasses.dataclass
class BaseProvider:
    config: yaml.YAMLObject

    fallback_provider_url:str = "" # For the providers to specify their default URL if not provided in the config

    @property
    def base_url(self) -> str:
        return self.config.get("provider_url", self.fallback_provider_url)

    @property
    def model(self):
        _model = self.config.get("provider_model", None)
        if _model:
            return _model
        raise Exception("Provider model not specified in config")

    def prompt(self) -> str:
        raise NotImplementedError("Subclasses must implement the prompt method")

class ProviderConfig(BaseModel):
    name: str
    model: str
    url: str = "http://127.0.0.1:11434"  # the fallback lives here now
    num_ctx: int = Field(default=8192, ge=8192)
