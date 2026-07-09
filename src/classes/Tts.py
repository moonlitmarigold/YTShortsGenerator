import soundfile as sf
from .. import sessions
from .. import TTS as _TTS

class TTS:

     def __init__(self, config:_TTS.Base.TTSConfig):
         self.config = config
         self.tts = _TTS.TTS_REGISTER[config.name](config)

     def run(self, session:sessions.SessionInfo):
         scenes = session.script.scenes
         for scene in scenes:
             audio_path = session.file / f'audio_track_{scene.id}.wav'
             audio = self.tts.audio(scene.spoken_text)
             sf.write(str(audio_path), audio, self.config.sample_rate)
