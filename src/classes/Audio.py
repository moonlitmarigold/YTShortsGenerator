# add audios together
# build music
from .. import sessions
from pydub import AudioSegment
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

    JAMENDO_API = "https://api.jamendo.com/v3.0/tracks/"


    def __post_init__(self):
        self.music_types = {
            "jamendo": self.jamendo,
            "downloaded": self.downloaded,
        }
        if self.config.music_type not in self.music_types.keys():
            raise ValueError(f'Music Type {self.config.music_type} is not supported, music_types are: {self.music_types.keys()}')

    def music(self, session:sessions.SessionInfo, audio_track:AudioSegment):
        music_type = self.config.music_type
        self.music_types[music_type](session, audio_track)

    def downloaded(self, session:sessions.SessionInfo, audio_track:AudioSegment):
        logger.debug('Using Downloaded files for music')
        video_guidance = session.script.video_guidance
        downloaded_files = utils.Downloaded('music')
        files = downloaded_files.get_genre(video_guidance.music_genre.value)
        combined = AudioSegment.silent(0)
        while True:
            combined += AudioSegment.from_file(str(files.__next__()))
            if combined.duration_seconds > audio_track.duration_seconds:
                break
        logger.debug(f'Created song background')
        output_path = session.music_path()

        res_audio = combined[:audio_track.duration_seconds*1000]
        res_audio.export(str(output_path))

    def jamendo(self, session:sessions.SessionInfo, audio_track:AudioSegment):
        video_guidance = session.script.video_guidance
        duration_min = int(audio_track.duration_seconds)
        duration_max = 2 * duration_min

        params = {
            "client_id": self.secrets.jamendo_client_id,
            "format": "json",
            "limit": 1,
            "tags": video_guidance.music_genre.value,  # our genre naming may not 1:1 match Jamendo's tag taxonomy
            "audioformat": "mp32",
            "include": "musicinfo",
            "vocalinstrumental": "instrumental",  # background bed under narration, never vocals
            "durationbetween": f"{duration_min}_{duration_max}",
            "order": "popularity_total",
        }
        logger.debug('Requesting songs from Jamendo')
        resp = requests.get(self.JAMENDO_API, params=params, timeout=20)
        resp.raise_for_status()

        data = resp.json()
        if data["headers"]["status"] != "success":
            raise RuntimeError(f"Jamendo error: {data['headers'].get('error_message')}")

        tracks = [t for t in data["results"] if t.get("audiodownload_allowed") and t.get("audiodownload")]
        if not tracks:
            raise RuntimeError(
                "No downloadable tracks matched your filters. Try different --tags "
                "or widen --min-duration/--max-duration."
            )
        track = tracks[0]

        music_path = session.music_path()

        logger.debug('Downloading song from Jamendo')
        r = requests.get(track["audiodownload"], stream=True, timeout=60)
        r.raise_for_status()
        with open(music_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    def run(self, session:sessions.SessionInfo):
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
        print(output_path.suffix)
        combined.export(str(output_path))

        # music
        self.music(session, combined)



