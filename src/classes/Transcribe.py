import soundfile as sf
from pydantic import BaseModel
from .. import sessions
from .. import Transcribe as _TR

class Transcribe:

     def __init__(self, config:_TR.Base.TranscribeConfig, secrets:type[BaseModel]):
         self.config = config
         self.tr = _TR.TR_REGISTER[config.name](config, secrets)

     def run(self, session:sessions.SessionInfo):
         scenes = session.script.scenes
         for scene in scenes:
             audio_path = session.audio_path(scene.id)
             output_path = session.transcribe_path(scene.id)
             self.tr.transcribe(audio_path, output_path)