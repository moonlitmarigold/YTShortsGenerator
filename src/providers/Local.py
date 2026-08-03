import dataclasses
from .Base import register
from .OpenAICompatible import BaseOpenAICompatible

@register
@dataclasses.dataclass
class Local(BaseOpenAICompatible):

    def __post_init__(self):
        self.provider_url()  # fail fast: there is no universal default for a self-hosted server

    def _api_key(self) -> str | None:
        return self.secrets.local_api_key if self.secrets else None
