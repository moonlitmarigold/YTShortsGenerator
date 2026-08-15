"""Generation-type registry and prompt rendering.

A generation type defines a category of short video (e.g. "quote"). Each type
has its own prompt template (`prompt.md`) for script generation and an
optional planner template (`planner.md`) for angle selection. Templates are
rendered by applying a small hook pipeline that substitutes `{{placeholder}}`
values and injects shared context (fonts, material table, etc.).
"""

import dataclasses
from pathlib import Path

from . import hooks


@dataclasses.dataclass
class GenerationType:
    """Configuration for one video generation category.

    Attributes:
        name: Directory name under `src/generation_types/` that holds the
            `prompt.md` and optional `planner.md` files.
        hooks: Prompt-rendering hooks applied to `prompt.md` after the
            universal metadata substitution.
        resolution: Target (width, height) for rendered videos of this type.
        planner_hooks: Extra hooks applied to `planner.md` after the universal
            metadata/material-table substitution. Use these to inject
            generation-type-specific sections (e.g. source links).
    """

    name: str
    hooks: tuple
    resolution: tuple[int, int]
    # Hooks specific to this type's planner.md (e.g. injecting a generation-type-specific
    # "custom_data" section like reddit story links) - applied in addition to the
    # universal hook_metadata/hook_material_table pair every planner.md gets.
    planner_hooks: tuple = ()

    @property
    def prompt_file(self) -> Path:
        """Path to this type's script-generation prompt."""
        return Path(__file__).parent / self.name / "prompt.md"

    @property
    def planner_file(self) -> Path:
        """Path to this type's planning prompt, if any."""
        return Path(__file__).parent / self.name / "planner.md"

    def read_file(self) -> str:
        """Read the script prompt template as a string."""
        return self.prompt_file.read_text()

    def return_file(self, context: dict) -> str:
        """Render the script prompt template with the given context."""
        prompt_text = self.read_file()
        prompt_text = hooks.hook_metadata(prompt_text, context)

        for hook in self.hooks:
            prompt_text = hook(prompt_text, context)

        return prompt_text

    def return_planner_file(self, context: dict) -> str:
        """Render the planner prompt template with the given context.

        Runs the universal metadata + material-table hooks, then any
        generation-type-specific planner hooks.
        """
        prompt_text = self.planner_file.read_text()
        prompt_text = hooks.hook_metadata(prompt_text, context)
        prompt_text = hooks.hook_material_table(prompt_text, context)

        for hook in self.planner_hooks:
            prompt_text = hook(prompt_text, context)

        return prompt_text

    @staticmethod
    def all_generation_types() -> list[str]:
        """Return the names of all generation-type subdirectories."""
        path = Path(__file__).parent
        return [x.name for x in path.iterdir() if x.is_dir()]


GENERATION_TYPES = {
    "quote": GenerationType(
        name="quote",
        hooks=(
            hooks.hook_fonts,
        ),
        resolution=(1080, 1920)
    ),
}
