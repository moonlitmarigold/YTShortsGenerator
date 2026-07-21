# assemble the video
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
from .. import sessions
from .. import utils
import ffmpeg

class Video:

    def run(self, session:sessions.SessionInfo):
        # load in the needed clips
        video = VideoFileClip(session.background_video())
        audio = AudioFileClip(session.full_audio_path())
        music = AudioFileClip(session.music_path())

        # TODO: Adjust volume of music to be relative to the audio volume

        # TODO: Speed up the Audio and remove gaps

        (
        CompositeVideoClip(
            (
                video,
            )
        ).with_audio(
            CompositeAudioClip(
                (
                    audio,
                    music
                )
            )
        )
        .write_videofile(str(session.tmp_output_video()))
        )

        self._subtitles(session)

    @staticmethod
    def _subtitles(session:sessions.SessionInfo):
        # burn the subtitles generated previously
        stream = ffmpeg.input(str(session.tmp_output_video()))
        stream = stream.filter(
            'ass',
            filename=str(session.subtitle_file()),
            fontsdir=str(session.fonts_path()),
        )
        stream = ffmpeg.output(stream, str(session.output_video()), acodec='copy')
        ffmpeg.run(stream, overwrite_output=True)

