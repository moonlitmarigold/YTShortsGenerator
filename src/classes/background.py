from .. import sessions
from .. import utils
import moviepy

class Background:


    def run(self, session:sessions.SessionInfo):
        downloaded_files = utils.Downloaded('video')
        script = session.script
        genre = script.video_guidance.background_genre
        videos = downloaded_files.get_genre(genre)

        while True:
            pass
