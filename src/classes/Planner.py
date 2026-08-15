"""Planner pipeline step.

The Planner narrows the broad topic from config into one specific, fresh angle
for this video. It uses the generation type's `planner.md` prompt and the
provider LLM to pick a `chosen_topic`, then records which material was used so
future runs can avoid repeating the same angle.
"""

import dataclasses
import logging

from pydantic import ValidationError

from .. import generation_types
from .. import providers
from .. import sessions
from .. import utils
from ..utils import planner_schemas
from .Prompt import Prompt

logger = logging.getLogger(__name__)

# Number of times to ask the LLM for a valid plan before giving up.
MAX_PLAN_RETRIES = 3


@dataclasses.dataclass()
class Planner:
    """Chooses a concrete topic/angle for a video and writes the final prompt.

    Attributes:
        generation_type: Key into GENERATION_TYPES (e.g. "quote").
        metadata: Baseline metadata for this run.
        config: Provider configuration used to call the planning LLM.
        secrets: Loaded secrets (.env) needed by the provider.
    """

    generation_type: str
    metadata: utils.Metadata
    config: providers.Base.ProviderConfig
    secrets: utils.Secrets

    def __post_init__(self):
        self.provider: providers.Base.BaseProvider = self._provider()

    def _provider(self) -> providers.Base.BaseProvider:
        """Instantiate the configured LLM provider."""
        provider_cls = providers.get_provider(self.config.name)
        return provider_cls(self.config, self.secrets)

    @staticmethod
    def _parse_output(output: str) -> planner_schemas.PlannerOutput:
        """Parse and validate the LLM's JSON plan response."""
        clean_output = Prompt.clean_and_parse_json(output)
        return planner_schemas.PlannerOutput.model_validate(clean_output)

    @staticmethod
    def _mark_used_material(
        session: sessions.SessionInfo,
        materials: list[planner_schemas.Material],
        original_material: list[planner_schemas.Material],
    ) -> None:
        """Persist which material rows this plan consumed.

        For every material the planner says it used:
          - If it already existed in the table, mark it used.
          - If it is new (the planner invented a candidate), insert it as used.
        """
        original_ids = {material.id for material in original_material}
        for material in materials:
            if material.id in original_ids:
                session.set_material_used(material.id)
            else:
                session.add_material(material)

    @staticmethod
    def _persist_new_material(
        session: sessions.SessionInfo,
        materials: list[planner_schemas.Material],
        original_material: list[planner_schemas.Material],
    ) -> None:
        """Persist any new material candidates the planner surfaced.

        Only inserts rows that were not already in the original table; rows
        already present with `used: false` are left unchanged.
        """
        original_ids = {material.id for material in original_material}
        for material in materials:
            if material.id not in original_ids:
                session.add_material(material)

    def run(self, session: sessions.SessionInfo) -> None:
        """Run the planning step for this session.

        Builds the planner prompt from the generation type's planner.md, asks the
        LLM for a structured plan, persists material usage, then renders the final
        script prompt using the chosen topic.
        """
        generation_obj = generation_types.GENERATION_TYPES[self.generation_type]

        # Load existing material for this generation type and render it as a
        # Markdown table so the planner can avoid repeating angles.
        original_material = session.return_material_list(self.generation_type)
        table_rows = planner_schemas.Material.table_head()
        table_rows.extend([material.table() for material in original_material])
        material_table = "\n".join(table_rows)

        context = {
            **self.metadata.model_dump(mode="json"),
            "fonts": utils.fonts.list_font_families(),
            "material_table": material_table,
        }

        planner_prompt = generation_obj.return_planner_file(context)
        session.planner_file().write_text(planner_prompt)

        # Retry a few times: reasoning models sometimes emit malformed JSON or
        # forget a required field. We log each failure and bail out after
        # MAX_PLAN_RETRIES attempts so we don't loop forever.
        num_tries = 0
        while True:
            response = self.provider.prompt(planner_prompt)
            try:
                plan = self._parse_output(response)
                break
            except ValidationError:
                num_tries += 1
                logger.error("The Planner AI has not returned a valid plan, will retry")
                if num_tries == MAX_PLAN_RETRIES:
                    logger.error(
                        "The Planner AI was unable to deliver a valid plan after %s attempts. Stopping.",
                        MAX_PLAN_RETRIES,
                    )
                    raise RuntimeError(
                        f"The Planner AI was unable to deliver a valid plan after {MAX_PLAN_RETRIES} attempts."
                    )

        logger.debug("Planner output: %s", plan.model_dump())

        self._mark_used_material(session, plan.material_used, original_material)
        self._persist_new_material(session, plan.material_available, original_material)

        # The script prompt receives the planner's chosen topic plus any
        # generation-type-specific custom data (e.g. source links).
        script_context = {**context, "topic": plan.chosen_topic, **plan.custom_data}
        prompt_text = generation_obj.return_file(script_context)

        session.prompt_file().touch(exist_ok=True)
        session.prompt_file().write_text(prompt_text)
