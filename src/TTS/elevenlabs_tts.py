import dataclasses
import numpy as np
import requests
from .Base import BaseTTS, register

@register
@dataclasses.dataclass
class Elevenlabs(BaseTTS):

    _api_url: str = "https://api.elevenlabs.io/v1"

    def __post_init__(self):
        if not self.secrets or not self.secrets.elevenlabs_api_key:
            raise ValueError("Missing ElevenLabs API key: set ELEVENLABS_API_KEY in your .env file")
        super().__post_init__()

    @property
    def _headers(self) -> dict:
        return {"xi-api-key": self.secrets.elevenlabs_api_key}

    @property
    def models(self):
        response = requests.get(f"{self._api_url}/models", headers=self._headers)
        response.raise_for_status()
        return tuple(model["model_id"] for model in response.json())

    @property
    def voices(self):
        response = requests.get(f"{self._api_url}/voices", headers=self._headers)
        response.raise_for_status()
        return tuple(voice["voice_id"] for voice in response.json()["voices"])

    def audio(self, text:str):
        response = requests.post(
            f"{self._api_url}/text-to-speech/{self.config.voice}",
            headers=self._headers,
            params={"output_format": f"pcm_{self.config.sample_rate}"},
            json={"text": text, "model_id": self.config.tts_model},
        )
        response.raise_for_status()

        # ElevenLabs returns raw 16-bit PCM when output_format is pcm_*, matching
        # our requested sample rate; soundfile needs a float array, not raw bytes.
        pcm = np.frombuffer(response.content, dtype="<i2")
        return pcm.astype(np.float32) / 32768.0
