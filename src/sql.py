from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    suggested_title: str
    key_theme: str
    total_duration_seconds: Optional[int]
    platform: str
    font_family: str
    render_status: str = "not_rendered"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    scenes: list["Scene"] = Relationship(back_populates="video")

class Scene(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: int = Field(foreign_key="video.id")
    scene_order: int
    type: str
    spoken_text: str
    display_mode: str
    duration_ms: int

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
    quote_variant_count: int = Field(default=1)

    model_name: str
    status: str = Field(default="pending")  # pending | success | failed | invalid_json
    raw_llm_output: Optional[str] = None
    error_message: Optional[str] = None
    generation_ms: Optional[int] = None


class VideoPerformance(SQLModel, table=True):
    __tablename__ = "video_performance"

    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: int = Field(foreign_key="videos.id")

    platform_post_id: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)