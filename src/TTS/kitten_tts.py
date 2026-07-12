from kittentts import KittenTTS
from .Base import BaseTTS, register
import dataclasses

@register
@dataclasses.dataclass
class Kitten(BaseTTS):

    _model:KittenTTS = dataclasses.field(init=False, default=None)

    @property
    def models(self):
        return (
            'KittenML/kitten-tts-mini-0.8',
            'KittenML/kitten-tts-micro-0.8',
            'KittenML/kitten-tts-nano-0.8',
            'KittenML/kitten-tts-nano-0.8-int8',
        )

    @property
    def voices(self):
        return self.model.available_voices

    @property
    def model(self):
        if self._model is None:
            self._model = KittenTTS(self.config.tts_model)
        return self._model

    def audio(self, text:str):
        return self.model.generate(text)
