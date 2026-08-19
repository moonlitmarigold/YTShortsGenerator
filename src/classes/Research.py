

from .. import generation_types
from .. import sessions
from .. import utils
from .. import research
import dataclasses

@dataclasses.dataclass
class Research:

    generation_type: str

    def generation_obj(self):
        return generation_types.GENERATION_TYPES[self.generation_type]

    def research_backend(self) -> type[research.BaseResearch]:
        return self.generation_obj().research_backend()


    def run(self, session:sessions.SessionInfo):

        material = session.return_material_list(self.generation_type)


        # 1: Check if there is sufficent material (default number of unused entries)

        # 2: DO the query

        # Build a list of external ids (like reddit post ids) to stop content from duplicating
        external_ids = [mat.external_id for mat in material]

        output_materials =self.research_backend().collect(external_ids)

        for material in output_materials:
            session.add_material(material)

        