#import yaml
import dataclasses
from .Base import BaseProvider, register
import ollama

@register
@dataclasses.dataclass
class Ollama(BaseProvider):

    fallback_provider_url: str = "http://127.0.0.1:11434"

    # Ollama's default context window is 4096. Reasoning models (qwen3, ...) spend
    # thousands of tokens "thinking" before emitting content, so the default is too
    # small and the response gets truncated mid-thought, leaving content empty.
    fallback_num_ctx: int = 8192

    def __post_init__(self):
        self._validate_model()

    def _validate_model(self):
        client = self._client
        models = [x.model for x in client.list()['models']]
        if self.model not in models:
            raise ValueError(f'Model {self.model} is not supported/installed. Installed models are {models}')

    @property
    def _client(self) -> ollama.Client:
        return ollama.Client(host=self.provider_url())

    def prompt(self) -> str:
        response = self._client.chat(
            model=self.model,
            messages=[
                {"role": "user",
                 "content": self.config.prompt}
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
