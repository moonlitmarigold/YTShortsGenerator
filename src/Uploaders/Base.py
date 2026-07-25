import dataclasses
from pathlib import Path
from pydantic import BaseModel, field_validator

UPLOADER_REGISTER = dict()

def register(cls):
    UPLOADER_REGISTER[cls.__name__.lower()] = cls
    return cls

class UploaderConfig(BaseModel):
    name: str
    privacy_status: str = "private"
    made_for_kids: bool = False

    @field_validator('name', mode='after')
    @classmethod
    def check_model(cls, value:str):
        if value not in UPLOADER_REGISTER.keys():
            raise ValueError('Uploader {} is not supported: Supported Uploaders are: {}'.format(value, UPLOADER_REGISTER.keys()))
        return value

@dataclasses.dataclass
class BaseUploader:
    config: UploaderConfig
    secrets: type[BaseModel] = None

    def upload(self, video_path:Path, title:str, description:str, tags:list[str]) -> str:
        raise NotImplementedError("Subclasses must implement the upload method")
