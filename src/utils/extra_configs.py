from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from . import schemas
from typing import Optional

class Secrets(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)
    youtube_api_key: str               # <- from env YOUTUBE_API_KEY, errors if missing
    elevenlabs_api_key: str | None = None
    jamendo_client_id: str | None = None

class AudioConfig(BaseModel):

    silence:int
    music_type:str

class Metadata(BaseModel):
    topic: str
    tone: str
    target_audience: str
    video_length_seconds: int
    platform: schemas.Platform
    pov: schemas.POV

class SubtitleBackground(BaseModel):
    radius: int
    offset: int
    transformy: int
    height_scaling: int
    rounded_border: bool