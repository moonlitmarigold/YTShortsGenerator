import dataclasses
from .Base import register
from .OpenAICompatible import BaseOpenAICompatible

@register
@dataclasses.dataclass
class OpenCodeZen(BaseOpenAICompatible):

    _fallback_provider_url: str = "https://opencode.ai/zen/v1"

    def __post_init__(self):
        if not self.secrets or not self.secrets.opencode_api_key:
            raise ValueError("Missing OpenCode Zen API key: set OPENCODE_API_KEY in your .env file")

    def _api_key(self) -> str | None:
        return self.secrets.opencode_api_key
