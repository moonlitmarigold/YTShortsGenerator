#import yaml
import dataclasses
from .Base import BaseProvider
import ollama

@dataclasses.dataclass
class Ollama(BaseProvider):


    fallback_provider_url: str = "http://127.0.0.1:11434"

    @property
    def _client(self) -> ollama.Client:
        return ollama.Client(host=self.base_url)

    def prompt(self, content:str):
        response = self._client.chat(
            model=self.model,
            messages=[{"role": "user", "content": content}],
        )

        return response["message"]["content"].strip()
