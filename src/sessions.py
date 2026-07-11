from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging
import shutil
from pathlib import Path

from sqlmodel import Session, select

from . import config, sql
from .generation_types import schemas

logger = logging.getLogger(__name__)


class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    FINISHED = "finished"


@dataclass
class SessionInfo:

    generation_session: sql.GenerationSession
    script: Optional[schemas.GeneratedVideoScript] = field(default=None)

    @property
    def id(self):
        return self.generation_session.id

    @property
    def return_status(self):
        return self.generation_session.status

    @property
    def file(self):
        p = Path(__file__).parent / 'files' / str(self.generation_session.id)
        p.mkdir(exist_ok=True, parents=True)
        return p

    def audio_path(self, scene_id):
        return self.file / f'audio_track_{scene_id}.wav'

    def transcribe_path(self, scene_id):
        return self.file / f'audio_transcribe_{scene_id}.srt'

    def full_audio_path(self):
        return self.file / 'audio.wav'

    def music_path(self):
        return self.file / 'music.mp3'

    def set_status(self, status: Status):
        self.generation_session.status = status.value

    def set_step(self, step:str):
        self.generation_session.step = step

    def set_error(self, error: str):
        self.generation_session.error_message = error
        self.set_status(Status.FAILED)

    @classmethod
    def from_config(cls, app_config: config.AppConfig) -> "SessionInfo":
        generation_session = sql.GenerationSession(
            topic=app_config.metadata.topic,
            tone=app_config.metadata.tone,
            target_audience=app_config.metadata.target_audience,
            video_length_seconds=app_config.metadata.video_length_seconds,
            platform=app_config.metadata.platform.value,
            pov=app_config.metadata.pov.value,
            status=Status.PENDING.value,
        )
        return cls(generation_session).save()

    @classmethod
    def from_sql(cls, generation_session_id: int) -> "SessionInfo":
        engine = sql.return_engine()
        with Session(engine) as session:
            generation_session = session.get(sql.GenerationSession, generation_session_id)
            if generation_session is None:
                raise ValueError(f"No generation session with id {generation_session_id}")
            script = None
            if generation_session.raw_llm_output:
                from src.classes import Prompt
                script = Prompt.Prompt._parse_output(generation_session.raw_llm_output)
            return cls(generation_session, script)

    def inject_prompt_output(self, script: schemas.GeneratedVideoScript, raw: str):
        self.script = script
        self.generation_session.raw_llm_output = raw
        self.set_status(Status.FINISHED)

    def _build_video_rows(self) -> tuple[sql.Video, list[sql.Scene]]:
        script = self.script

        video = sql.Video(
            suggested_title=script.video_metadata.suggested_title,
            key_theme=script.video_metadata.key_theme,
            total_duration_seconds=script.video_metadata.total_duration_seconds,
            platform=script.video_metadata.platform.value,
            font_family=script.style_defaults.font_family,
            font_size=script.style_defaults.font_size,
            primary_text_color=script.style_defaults.primary_text_color,
            highlight_color=script.style_defaults.highlight_color,
            text_position=script.style_defaults.text_position,
            background_overlay=script.style_defaults.background_overlay,
            pacing_recommendation=script.video_guidance.pacing_recommendation.value,
            music_genre=script.video_guidance.music_genre.value,
            music_energy_curve=script.video_guidance.music_energy_curve,
            generation_session_id=self.generation_session.id,
        )

        scenes = [
            sql.Scene(
                scene_order=scene.id,
                type=scene.type.value,
                spoken_text=scene.spoken_text,
                display_mode=scene.display_mode.value,
                on_screen_text=scene.on_screen_text,
                highlight_words=[hw.model_dump(mode="json") for hw in scene.highlight_words],
                duration_ms=scene.duration_ms,
                style_override=scene.style_override,
            )
            for scene in script.scenes
        ]

        return video, scenes

    def save(self):
        engine = sql.return_engine()

        with Session(engine, expire_on_commit=False) as session:
            session.add(self.generation_session)
            session.commit()

            if self.script is not None:
                video, scenes = self._build_video_rows()
                video.scenes = scenes
                session.add(video)
                session.commit()

        return self

    def delete(self):
        """Explicitly remove this session (and any associated video/scenes) from the database.

        Not implemented as __del__: that hook fires whenever Python garbage-collects
        the object (e.g. end of any function scope), which was silently wiping rows
        right after save() persisted them.
        """
        engine = sql.return_engine()

        with Session(engine) as session:
            generation_session = session.get(sql.GenerationSession, self.id)
            if generation_session is None:
                return

            video = generation_session.video
            if video is not None:
                performances = session.exec(
                    select(sql.VideoPerformance).where(sql.VideoPerformance.video_id == video.id)
                ).all()
                for performance in performances:
                    session.delete(performance)

                for scene in video.scenes:
                    session.delete(scene)

                session.delete(video)

            session.delete(generation_session)
            session.commit()

        file_dir = Path(__file__).parent / 'files' / str(self.id)
        if file_dir.exists():
            shutil.rmtree(file_dir)
