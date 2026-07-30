from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging
import shutil
from pathlib import Path
from sqlmodel import Session, select
from . import config, sql
from .utils import schemas, duration, fonts

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

    @staticmethod
    def base_path():
        p = Path(__file__).parent / 'files'
        p.mkdir(exist_ok=True, parents=True)
        return p

    @property
    def file(self):
        p = self.base_path() / str(self.generation_session.id)
        p.mkdir(exist_ok=True, parents=True)
        return p

    def _path(self, name:str, _base=None):
        if not _base:
            _base = self.file
        p = _base / name
        p.touch(exist_ok=True)
        return p

    def audio_path(self, scene_id):
        return self._path(f'audio_track_{scene_id}.wav')

    def transcribe_path(self, scene_id):
        return self._path(f'audio_transcribe_{scene_id}.srt')

    def full_audio_path(self):
        return self._path('audio.wav')

    def music_path(self):
        return self._path('music.mp3')

    def background_video(self):
        return self._path('background_video.mp4')

    def prompt_file(self):
        return self._path('prompt.md')

    def subtitle_file(self):
        return self._path(f'subtitle_file.ass')

    def output_video_tmp(self):
        return self._path('output_video_tmp.mp4')

    def output_video(self):
        return self._path('output_video.mp4')

    def thumbnail_path(self):
        return self._path('thumbnail.jpg')

    @property
    def tmp(self):
        p = Path(__file__).parent / 'tmp' / str(self.generation_session.id)
        p.mkdir(exist_ok=True, parents=True)
        return p

    def tmp_subfile(self, scene_id):
        #return self.tmp / f'audio_transcribe_{scene_id}.srt'
        return self._path(f'audio_transcribe_{scene_id}.srt', _base=self.tmp)

    def tmp_output_video(self):
        return self._path('output_video.mp4', _base=self.tmp)

    def set_duration(self, duration_seconds:float):
        duration.set_duration(self.script, duration_seconds)

    @property
    def duration_seconds(self):
        return self.script.video_metadata.total_duration_seconds

    @staticmethod
    def fonts_path():
        p = Path(__file__).parent / "fonts"
        p.mkdir(exist_ok=True)
        return p

    @property
    def step(self):
        return self.generation_session.step

    @property
    def is_finished(self):
        return self.return_status == Status.FINISHED

    def set_status(self, status: Status):
        self.generation_session.status = status.value

    def set_step(self, step:str):
        self.generation_session.step = step

    def set_error(self, error: str):
        self.generation_session.error_message = error
        self.set_status(Status.FAILED)

    def add_description(self, des:str):
        if self.script.video_metadata.video_description:
            self.script.video_metadata.video_description += '\n'
            self.script.video_metadata.video_description += des
        else:
            self.script.video_metadata.video_description = des

    @staticmethod
    def all_sessions_id():
        engine = sql.return_engine()
        with Session(engine) as s:
             statement = select(sql.GenerationSession)
             every_session = s.exec(statement)
             ids = [x.id for x in every_session]
        return ids

    @staticmethod
    def all_files_id():
        files = SessionInfo.base_path()
        ids = [x for x in files.iterdir() if x.is_dir() and x.name.isdigit()]
        return ids

    @staticmethod
    def delete_stray_dirs():
        sql_ids = SessionInfo.all_sessions_id()
        files_ids = SessionInfo.all_files_id()

        stray_files = [_id for _id in files_ids if int(_id.name) not in sql_ids]
        for stray_file in stray_files:
            shutil.rmtree(stray_file)

    @staticmethod
    def delete_stray_sql_entries():
        sql_ids = SessionInfo.all_sessions_id()
        files_ids = SessionInfo.all_files_id()
        file_ids = {int(_id.name) for _id in files_ids}

        stray_sqls = [_id for _id in sql_ids if _id not in file_ids]
        for stray_sql in stray_sqls:
            obj = SessionInfo.from_sql(stray_sql)
            obj.delete()

    @staticmethod
    def reset():
        database = Path(__file__).parent / 'database.db'
        shutil.rmtree(database)

        SessionInfo.delete_stray_dirs()

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
                try:
                    script = Prompt.Prompt._parse_output(generation_session.raw_llm_output)
                except Exception:
                    logger.warning(
                        "Session %s has raw_llm_output that failed to parse; loading without a script",
                        generation_session_id, exc_info=True,
                    )

            session.expunge(generation_session)
            return cls(generation_session, script)

    def inject_prompt_output(self, script: schemas.GeneratedVideoScript, raw: str):
        self.script = script
        self.generation_session.raw_llm_output = raw
        self.set_status(Status.FINISHED)

    def _build_video_rows(self) -> tuple[sql.Video, list[sql.Scene]]:
        script = self.script

        highlighting = script.style_defaults.highlighting

        video = sql.Video(
            suggested_title=script.video_metadata.suggested_title,
            key_theme=script.video_metadata.key_theme,
            video_description=script.video_metadata.video_description,
            tags=script.video_metadata.tags,
            total_duration_seconds=script.video_metadata.total_duration_seconds,
            platform=script.video_metadata.platform.value,
            font_family=script.style_defaults.font_family,
            font_size=script.style_defaults.font_size,
            primary_text_color=script.style_defaults.primary_text_color,
            highlight_color=script.style_defaults.highlight_color,
            text_position=script.style_defaults.text_position,
            background_color=script.style_defaults.background_color,
            word_max=script.style_defaults.word_max,
            subtitle_type=script.style_defaults.subtitle_type.value,
            fill_sub_times=script.style_defaults.fill_sub_times,
            highlight_enabled=highlighting.enabled,
            highlight_word_max=highlighting.word_max,
            highlight_as_borders=highlighting.as_borders,
            highlight_fade_ms=highlighting.fade_ms,
            highlight_appear=highlighting.appear,
            highlight_font_size=highlighting.font_size,
            pacing_recommendation=script.video_guidance.pacing_recommendation.value,
            music_genre=script.video_guidance.music_genre.value,
            music_energy_curve=script.video_guidance.music_energy_curve,
            background_genre=script.video_guidance.background_genre.value,
            generation_session_id=self.generation_session.id,
        )

        scenes = [
            sql.Scene(
                scene_order=scene.id,
                type=scene.type.value,
                spoken_text=scene.spoken_text,
                duration_seconds=scene.duration_seconds,
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
                new_video, new_scenes = self._build_video_rows()

                existing_video = session.exec(
                    select(sql.Video).where(sql.Video.generation_session_id == self.generation_session.id)
                ).first()

                if existing_video is None:
                    new_video.scenes = new_scenes
                    session.add(new_video)
                else:
                    skip_fields = {"id", "generation_session_id", "created_at"}
                    for field in sql.Video.model_fields:
                        if field in skip_fields:
                            continue
                        setattr(existing_video, field, getattr(new_video, field))

                    for scene in existing_video.scenes:
                        session.delete(scene)
                    existing_video.scenes = new_scenes

                session.commit()

        return self

    def delete(self):
        """Explicitly remove this session (and any associated video/scenes) from the database.

        Not implemented as __del__: that hook fires whenever Python garbage-collects
        the object (e.g. end of any function scope), which was silently wiping rows
        right after save() persisted them.

        File cleanup runs in `finally` so that a missing/already-deleted DB row (or a
        failure partway through the cascade) never leaves an orphaned src/files/<id> dir.
        """
        engine = sql.return_engine()
        file_dir = Path(__file__).parent / 'files' / str(self.id)

        try:
            with Session(engine) as session:
                generation_session = session.get(sql.GenerationSession, self.id)
                if generation_session is None:
                    return

                videos = session.exec(
                    select(sql.Video).where(sql.Video.generation_session_id == self.id)
                ).all()
                for video in videos:
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
        finally:
            if file_dir.exists():
                shutil.rmtree(file_dir)

    def __del__(self):
        tmp_folder = self.tmp.parent
        if tmp_folder.exists():
            shutil.rmtree(str(tmp_folder))


