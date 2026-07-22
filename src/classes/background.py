from .. import sessions
from .. import utils
from moviepy import *
from pydub import AudioSegment
from dataclasses import dataclass
import random
import logging
logger = logging.getLogger(__name__)

@dataclass
class Background:

    resolution:tuple[int, int]
    speed:float = 1.1

    def _speed_up(self, clip: VideoClip) -> VideoClip:
        if self.speed == 1.0:
            return clip
        return clip.with_effects([vfx.MultiplySpeed(self.speed)])

    def run(self, session:sessions.SessionInfo):
        logger.debug('Starting background video')
        # downloaded videos
        downloaded_files = utils.Downloaded('videos')
        script = session.script
        genre = script.video_guidance.background_genre
        logger.debug(f'Genre {genre}')
        videos = downloaded_files.get_genre(genre)

        # audio duration
        audio_duration = session.duration_seconds
        # raw footage needed before speeding up, so the final clip still matches audio_duration
        raw_duration = audio_duration * self.speed

        clips: list[VideoClip] = list()
        cur_duration = 0
        while True:
            video = next(videos)
            logger.debug(f'Added Video File Clip {str(video)}')
            clip = VideoFileClip(str(video))
            clip = self._fit_to_resolution(clip, self.resolution)
            clips.append(clip)
            cur_duration += clip.duration
            logger.debug(f'Current clip duration {cur_duration}s')
            if cur_duration > raw_duration:
                break

        # extra: For long videos
        if len(clips):
            output_clip = concatenate_videoclips(clips)
            rand_int = random.randint(0, output_clip.duration-raw_duration)
            output_clip = output_clip.subclipped(rand_int, rand_int+raw_duration)
        else:
            output_clip = concatenate_videoclips(clips).subclipped(0, raw_duration)

        output_clip = self._speed_up(output_clip)

        output_clip.write_videofile(str(session.background_video()))

    @staticmethod
    def _fit_to_resolution(clip: VideoClip, resolution: tuple[int, int]) -> VideoClip:
        """Scale-to-cover + center-crop.

        Scales uniformly (so aspect ratio - and thus no stretching/distortion)
        until the clip covers the full target frame, then crops the overflow
        off the longer dimension. Trade-off vs letterboxing: this fills the
        frame with no black bars, but crops off the source's edges.
        """
        target_w, target_h = resolution
        scale = max(target_w / clip.w, target_h / clip.h)
        resized = clip.resized(scale)
        return resized.cropped(
            x_center=resized.w / 2,
            y_center=resized.h / 2,
            width=target_w,
            height=target_h,
        )

