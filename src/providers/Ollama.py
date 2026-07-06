#import yaml
import dataclasses
from .Base import BaseProvider
import ollama
from ollama import ChatResponse

@dataclasses.dataclass
class Ollama(BaseProvider):

    fallback_provider_url: str = "http://127.0.0.1:11434"

    # Ollama's default context window is 4096. Reasoning models (qwen3, ...) spend
    # thousands of tokens "thinking" before emitting content, so the default is too
    # small and the response gets truncated mid-thought, leaving content empty.
    fallback_num_ctx: int = 8192

    @property
    def _client(self) -> ollama.Client:
        return ollama.Client(host=self.base_url)

    @property
    def num_ctx(self) -> int:
        return self.config.get("provider_num_ctx", self.fallback_num_ctx)

    def prompt(self) -> str:
        content = self.config.get("prompt")
        response:ChatResponse = self._client.chat(
            model=self.model,
            messages=[
                {"role": "user",
                 "content": content}
            ],
            options={"num_ctx": self.num_ctx},
        )

        # done_reason == "length" means the model ran out of context window before
        # finishing. For reasoning models this usually means it never got past the
        # thinking phase, so message.content comes back empty.
        if response.done_reason == "length":
            used = (response.prompt_eval_count or 0) + (response.eval_count or 0)
            raise RuntimeError(
                "Ollama response truncated: hit the context window "
                f"(num_ctx={self.num_ctx}, used ~{used} tokens). "
                "Increase 'provider_num_ctx' in the config."
            )

        if not response.message.content:
            raise RuntimeError(
                f"Ollama returned empty content (done_reason={response.done_reason})."
            )

        return response.message.content
