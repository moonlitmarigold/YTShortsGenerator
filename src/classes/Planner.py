from .. import sessions
from .. import generation_types
import dataclasses
from .. import utils

@dataclasses.dataclass()
class Planner:

    generation_type:str
    metadata:utils.Metadata
    secrets:utils.Secrets

    def run(self, session:sessions.SessionInfo):

        generation_obj = generation_types.GENERATION_TYPES[self.generation_type]
        context = {**self.metadata.model_dump(mode='json'), 'fonts': utils.fonts.list_font_families()}
        prompt_text = generation_obj.return_file(context)

        session.prompt_file().touch(exist_ok=True)
        session.prompt_file().write_text(prompt_text)
