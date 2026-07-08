from pathlib import Path
import dataclasses
from . import schemas

@dataclasses.dataclass
class GenerationType:
    name: str
    _prompt_file: str  # points at the .yaml/.md next to it
    generation_output: schemas.GenerationOutput

    @property
    def prompt_file(self):
        path = Path(__file__).parent / self._prompt_file
        return path

GENERATION_TYPES = {
    "quote": GenerationType(
        name="quote",
        _prompt_file="quote.md",
        generation_output= schemas.QuoteOutput
    ),
}