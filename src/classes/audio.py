# add audios together
# build music
from .. import sessions
from pydub import AudioSegment
from .. import utils
from pydantic_settings import BaseSettings
import dataclasses

@dataclasses.dataclass
class Audio:
    config: utils.AudioConfig
    secrets: type[BaseSettings]

    def run(self, session:sessions.SessionInfo):
        # music
        pass
        # audio_file
        scenes = session.script.scenes
        last_session_id = scenes[-1].id
        combined = AudioSegment.silent(0)
        for scene in scenes:
            path = session.audio_path(scene.id)

            if combined is None:
                combined = AudioSegment.from_file(str(path))
            else:
                combined += AudioSegment.from_file(str(path))
            if scene.id != last_session_id and self.config.silence != 0:
                combined += AudioSegment.silent(self.config.silence)
        output_path = session.full_audio_path()
        combined.export(str(output_path), format=output_path.suffix)



