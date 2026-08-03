from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from . import schemas
from typing import Optional

class Secrets(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)
    youtube_api_key: str               # <- from env YOUTUBE_API_KEY, errors if missing
    elevenlabs_api_key: str | None = None
    opencode_api_key: str | None = None
    local_api_key: str | None = None
    jamendo_client_id: str | None = None
    youtube_client_secret_file: str | None = None  # OAuth client secret JSON downloaded from Google Cloud Console
    youtube_token_file: str = "youtube_token.json"  # where the refreshed OAuth token gets cached after first consent

class AudioConfig(BaseModel):

    silence:int
    music_type:str
    speed:float
    silence_thresh:float

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
    height_scaling: float
    rounded_border: bool