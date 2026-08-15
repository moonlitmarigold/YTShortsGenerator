"""Pydantic schemas for the Planner step and material tracking.

These schemas are the contract between the LLM planner response, the
`sql.Material` persistence table, and the prompt-rendering code.
"""

from typing import Optional

from pydantic import BaseModel


class Material(BaseModel):
    """One row of content material a generation type can draw from.

    Mirrors `sql.Material` row-for-row. `id` is optional when surfacing a brand
    new candidate from the planner (the database will assign it on insert).

    Attributes:
        id: Primary key from the database; omit for new candidates.
        generation_type: Generation type this material belongs to (e.g. "quote").
        name: Human-readable angle/title (e.g. "Why deadlines don't motivate you").
        used: Whether this angle has already been made into a video.
        material_metadata: Arbitrary JSON metadata for this type (links, counts, etc.).
    """

    id: Optional[int] = None
    generation_type: str
    name: str
    used: bool = False
    material_metadata: dict = {}

    @staticmethod
    def table_head() -> list[str]:
        """Return the Markdown table header used in planner prompts."""
        return [
            "id|generation_type|name|used|material_metadata",
            ":---|:---:|:---:|:---:|---:",
        ]

    def table(self) -> str:
        """Render this material as one Markdown table row."""
        return (
            f"{self.id}|{self.generation_type}|{self.name}|{self.used}|{self.material_metadata}"
        )


class PlannerOutput(BaseModel):
    """Universal parse target for every generation type's planner.md response.

    Mirrors `schemas.GeneratedVideoScript` in spirit: one shape all generation
    types are parsed into. Fields every planner must reason about are typed;
    `custom_data` is the escape hatch for generation-type-specific values
    (e.g. source links for a Reddit-stories type) without forcing a schema
    change per type.

    Attributes:
        chosen_topic: The specific angle selected for this video.
        reasoning: Why this angle was chosen and how it differs from used ones.
        material_used: Rows this plan consumed (to mark used in the DB).
        material_available: New candidate rows to persist as still-unused.
        custom_data: Generation-type-specific extra data passed to the script prompt.
    """

    chosen_topic: str
    reasoning: Optional[str] = None
    material_used: list[Material] = []
    material_available: list[Material] = []
    custom_data: dict = {}
