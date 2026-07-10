from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class Secrets(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)
    youtube_api_key: str               # <- from env YOUTUBE_API_KEY, errors if missing
    elevenlabs_api_key: str | None = None

class AudioConfig(BaseModel):

    silence:int