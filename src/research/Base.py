import dataclasses
from .. import utils
from pydantic import BaseModel, Secret
from .. import utils

class ResearchConfig(BaseModel):

    max_api_calls:int = 3
    timeout_sec:int = 30

@dataclasses.dataclass
class BaseResearch:

    config:ResearchConfig
    secrets:utils.Secrets

    def collect(self, external_ids:list[int]) -> list[utils.planner_schemas.Material]:
        raise NotImplemented


