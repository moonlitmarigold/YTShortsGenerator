from . import Base
import stable_whisper
import whisper
from pathlib import Path
from dataclasses import dataclass

@Base.register
@dataclass
class Whisper(Base.BaseTR):

    _model = None

    @property
    def models(self):
        return whisper.available_models()

    @property
    def model(self):
        if self._model is None:
            self._model = stable_whisper.load_model(self.config.model)
        return self._model

    def transcribe(self, audio_file:Path, output_path:Path):
        result = self.model.transcribe(str(audio_file))
        result.to_srt_vtt(str(output_path), segment_level=False, word_level=True)