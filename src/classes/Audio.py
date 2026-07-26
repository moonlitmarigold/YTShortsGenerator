# add audios together
# build music
from .. import sessions
from pydub import AudioSegment
from pydub.effects import speedup
from pydub.silence import detect_leading_silence
from .. import utils
from pydantic_settings import BaseSettings
import dataclasses
import requests
import logging
logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Audio:
    config: utils.AudioConfig
    secrets: type[BaseSettings]


    def __post_init__(self):
        self.music_types = {
            "downloaded": self.downloaded,
        }
        if self.config.music_type not in self.music_types.keys():
            raise ValueError(f'Music Type {self.config.music_type} is not supported, music_types are: {self.music_types.keys()}')

    def music(self, session:sessions.SessionInfo):
        music_type = self.config.music_type
        self.music_types[music_type](session)

    def downloaded(self, session:sessions.SessionInfo):
        logger.debug('Using Downloaded files for music')
        video_guidance = session.script.video_guidance
        downloaded_files = utils.Downloaded('music')
        files = downloaded_files.get_genre(video_guidance.music_genre.value)
        combined = AudioSegment.silent(0)

        while True:
            combined += AudioSegment.from_file(str(files.__next__()))
            if combined.duration_seconds > session.duration_seconds:
                break
        logger.debug(f'Created song background')
        output_path = session.music_path()

        res_audio = combined[:session.duration_seconds*1000]
        res_audio.export(str(output_path))

    def _strip_silence(self, segment: AudioSegment) -> AudioSegment:
        thresh = self.config.silence_thresh
        start_trim = detect_leading_silence(segment, silence_threshold=thresh)
        end_trim = detect_leading_silence(segment.reverse(), silence_threshold=thresh)
        return segment[start_trim:len(segment) - end_trim]

    def _speed_up(self, segment: AudioSegment) -> AudioSegment:
        if self.config.speed == 1.0:
            return segment
        return speedup(segment, playback_speed=self.config.speed)

    def run(self, session:sessions.SessionInfo):
        # audio_file
        scenes = session.script.scenes
        last_session_id = scenes[-1].id
        combined = AudioSegment.silent(0)
        for scene in scenes:
            path = session.audio_path(scene.id)
            seg = AudioSegment.from_file(str(path))
            seg = self._strip_silence(seg)
            seg = self._speed_up(seg)
            utils.duration.set_duration(scene, seg.duration_seconds)
            combined += seg
            if scene.id != last_session_id and self.config.silence != 0:
                combined += AudioSegment.silent(self.config.silence)
        output_path = session.full_audio_path()

        session.set_duration(combined.duration_seconds)

        combined.export(str(output_path))

        # music
        self.music(session)



