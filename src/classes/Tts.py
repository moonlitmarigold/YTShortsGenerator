import soundfile as sf
from pydantic import BaseModel
from .. import sessions
from .. import TTS as _TTS
import logging
logger = logging.getLogger(__name__)

class TTS:

     def __init__(self, config:_TTS.Base.TTSConfig, secrets:type[BaseModel]):
         self.config = config
         self.tts = _TTS.TTS_REGISTER[config.name](config, secrets)

     def run(self, session:sessions.SessionInfo):
         logger.debug(f'Running TTS with model {self.config.tts_model} and voice {self.config.voice}')
         scenes = session.script.scenes
         for scene in scenes:
             audio_path = session.audio_path(scene.id)
             audio = self.tts.audio(scene.spoken_text)
             sf.write(str(audio_path), audio, self.config.sample_rate)
             logger.debug(f'Wrote Audio track {scene.id} to {str(audio_path)}')
