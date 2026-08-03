import dataclasses
import requests
from .Base import BaseProvider

@dataclasses.dataclass
class BaseOpenAICompatible(BaseProvider):

    def _api_key(self) -> str | None:
        return None

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        api_key = self._api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def prompt(self, prompt_text:str) -> str:
        response = requests.post(
            f"{self.provider_url()}/chat/completions",
            headers=self._headers(),
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt_text}],
                "max_tokens": self.num_ctx,
            },
        )
        response.raise_for_status()
        choice = response.json()["choices"][0]
        content = choice.get("message", {}).get("content")

        if not content:
            raise RuntimeError(
                f"{type(self).__name__} returned empty content (finish_reason={choice.get('finish_reason')})."
            )

        return content
