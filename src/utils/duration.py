from . import schemas
import logging
logger = logging.getLogger(__name__)

def set_duration(script:schemas.GeneratedVideoScript, duration_seconds:float):

    duration_seconds = round(duration_seconds, 2)
    script.video_metadata.total_duration_seconds = duration_seconds
