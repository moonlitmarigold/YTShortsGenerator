from sqlmodel import SQLModel, Field, Relationship, create_engine
from sqlalchemy import Column, JSON
from typing import Optional
from datetime import datetime
from pathlib import Path

def return_engine():
    p = Path(__file__).parent / 'database.db'
    if not p.exists():
        p.touch()
    engine = create_engine(f'sqlite:///{str(p)}', connect_args={"timeout": 30})
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode=WAL")
    SQLModel.metadata.create_all(engine)
    return engine


class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    suggested_title: str
    key_theme: str
    video_description: Optional[str] = None
    tags: list[str] = Field(default=[], sa_column=Column(JSON))
    total_duration_seconds: Optional[int]
    platform: str

    # style_defaults
    font_family: str
    font_size: int
    primary_text_color: str
    highlight_color: str
    text_position: str
    background_color: Optional[str] = None

    # style_defaults.highlighting
    highlight_enabled: bool = True
    highlight_word_max: Optional[int] = None
    highlight_as_borders: bool = False
    highlight_fade_ms: Optional[tuple[int, int]] = Field(default=None, sa_column=Column(JSON))
    highlight_appear: bool = False
    highlight_font_size: Optional[int] = None

    # video_guidance
    pacing_recommendation: str
    music_genre: str
    music_energy_curve: Optional[str] = None
    background_genre: str

    render_status: str = "not_rendered"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    generation_session_id: Optional[int] = Field(default=None, foreign_key="generation_sessions.id")
    generation_session: Optional["GenerationSession"] = Relationship(back_populates="video")

    scenes: list["Scene"] = Relationship(back_populates="video")

class Scene(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: int = Field(foreign_key="video.id")
    scene_order: int
    type: str
    spoken_text: str
    duration_ms: int
    style_override: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    video: Video = Relationship(back_populates="scenes")

class GenerationSession(SQLModel, table=True):
    __tablename__ = "generation_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    topic: str
    tone: str
    target_audience: str
    video_length_seconds: int
    platform: str
    pov: str

    step: str = "init"  # scripted | tts | rendered | uploaded
    status: str = Field(default="pending")  # pending | running | failed | finished
    raw_llm_output: Optional[str] = None
    error_message: Optional[str] = None
    generation_ms: Optional[int] = None

    video: Optional["Video"] = Relationship(back_populates="generation_session")


class VideoPerformance(SQLModel, table=True):
    __tablename__ = "video_performance"

    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: int = Field(foreign_key="video.id")

    platform_post_id: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)