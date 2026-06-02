import yaml
import dataclasses

@dataclasses.dataclass
class BaseProvider:
    config: yaml.YAMLObject

    fallback_provider_url:str = "" # For the providers to specify their default URL if not provided in the config

    @property
    def base_url(self) -> str:
        return self.config.get("provider_url", self.fallback_provider_url)

    @property
    def model(self):
        return self.config.get("provider_model", None)