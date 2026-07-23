# assemble the video
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
from .. import sessions
from .. import utils
import ffmpeg
from moviepy.audio.fx import MultiplyVolume


class Video:

    def run(self, session:sessions.SessionInfo):
        duration = session.script.video_metadata.total_duration_seconds

        # load in the needed clips
        video = VideoFileClip(session.background_video())
        audio = AudioFileClip(session.full_audio_path())
        music = AudioFileClip(session.music_path())

        music = music.with_effects([MultiplyVolume(0.4)])


        (CompositeVideoClip(
            (
                video.subclipped(0, duration),
            )
        )
        .with_audio(
            CompositeAudioClip(
                (
                    audio.subclipped(0, duration),
                    music.subclipped(0, duration)
                )
            )
        )
        .write_videofile(str(session.output_video_tmp()), codec="libx264", audio_codec="aac")
        )

        self._subtitles(session)

    @staticmethod
    def _subtitles(session:sessions.SessionInfo):
        # burn the subtitles generated previously
        in_stream = ffmpeg.input(str(session.output_video_tmp()))

        video = in_stream.video.filter(
            'ass',
            filename=str(session.subtitle_file()),
            fontsdir=str(session.fonts_path()),
        )
        audio = in_stream.audio

        out = ffmpeg.output(video, audio, str('./test.mp4'), acodec='copy')
        ffmpeg.run(out, overwrite_output=True)

