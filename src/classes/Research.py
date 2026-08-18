

from .. import generation_types
from .. import sessions
from .. import utils
from .. import research
import dataclasses

@dataclasses.dataclass
class Research:

    generation_type: str


    def run(self, session:sessions.SessionInfo):

        generation_obj = generation_types.GENERATION_TYPES[self.generation_type]

