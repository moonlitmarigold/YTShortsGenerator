from .. import sessions
from .. import utils
from moviepy import *
from pydub import AudioSegment
import logging
logger = logging.getLogger(__name__)

class Background:


    def run(self, session:sessions.SessionInfo):
        logger.debug('Starting background video')
        # downloaded videos
        downloaded_files = utils.Downloaded('videos')
        script = session.script
        genre = script.video_guidance.background_genre
        logger.debug(f'Genre {genre}')
        videos = downloaded_files.get_genre(genre)

        # audio duration
        audio = AudioSegment.from_file(str(session.full_audio_path()))
        audio_duration = audio.duration_seconds

        clips: list[VideoClip] = list()
        cur_duration = 0
        while True:
            video = next(videos)
            logger.debug(f'Added Video File Clip {str(video)}')
            clip = VideoFileClip(str(video))
            clips.append(clip)
            cur_duration += clip.duration
            logger.debug(f'Current clip duration {cur_duration}s')
            if cur_duration > audio_duration:
                break

        output_clip = concatenate_videoclips(clips).subclipped(0, audio_duration)
        output_clip.write_videofile(str(session.background_video()))

