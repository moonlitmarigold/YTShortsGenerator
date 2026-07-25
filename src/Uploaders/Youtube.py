import dataclasses
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .Base import BaseUploader, register

logger = logging.getLogger(__name__)

# Shorts aren't a separate category in the Data API taxonomy - they're just
# <=60s vertical videos uploaded through the normal videos.insert endpoint.
# 22 = "People & Blogs", a reasonable default for short-form talking/quote content.

@register
@dataclasses.dataclass
class Youtube(BaseUploader):


    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __post_init__(self):
        if not getattr(self.secrets, "youtube_client_secret_file", None):
            raise ValueError(
                "youtube_client_secret_file is not set (add it to .env). "
                "Download it from the Google Cloud Console for a project with the "
                "YouTube Data API v3 enabled."
            )

    @property
    def category_id(self):
        _id = self.config.youtube_category_id
        if _id:
            return str(_id)
        else:
            return '22'

    def _credentials(self) -> Credentials:
        token_path = Path(self.secrets.youtube_token_file)
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.secrets.youtube_client_secret_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())

        return creds

    def _client(self):
        return build("youtube", "v3", credentials=self._credentials())

    def upload(self, video_path:Path, title:str, description:str, tags:list[str]) -> str:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": self.category_id,
            },
            "status": {
                "privacyStatus": self.config.privacy_status,
                "selfDeclaredMadeForKids": self.config.made_for_kids,
            },
        }

        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/*")

        request = self._client().videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.debug(f"Upload progress: {int(status.progress() * 100)}%")

        video_id = response["id"]
        logger.info(f"Uploaded video {video_id} to YouTube")
        return video_id
