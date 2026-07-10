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
             audio_path = session.file / f'audio_track_{scene.id}.wav'
             output_path = session.file / f'audio_transcribe_{scene.id}.ass'
             self.tr.transcribe(audio_path, output_path)