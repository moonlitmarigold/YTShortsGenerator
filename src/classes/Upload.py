from pydantic import BaseModel
from .. import sessions
from .. import Uploaders
import dataclasses
import logging
logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Upload:

    config: Uploaders.Base.UploaderConfig
    secrets: type[BaseModel]

    uploader: type[Uploaders.Base.BaseUploader] = dataclasses.field(init=False)

    def __post_init__(self):
        self.uploader = Uploaders.UPLOADER_REGISTER[self.config.name](self.config, self.secrets)

    def description(self):
        pass

    def run(self, session:sessions.SessionInfo):
        video_metadata = session.script.video_metadata
        video_path = session.output_video()
        description = self.description()
        logger.debug(f'Uploading video for session {session.id} via {self.config.name}')
        video_id = self.uploader.upload(
            video_path=video_path,
            title=video_metadata.suggested_title,
            description=description,
            tags=video_metadata.tags,
        )
        logger.info(f'Uploaded session {session.id} as {self.config.name} video {video_id}')
        return video_id
