from pathlib import Path
import dataclasses

@dataclasses.dataclass
class GenerationType:
    name: str
    _prompt_file: str  # points at the .yaml/.md next to it

    @property
    def prompt_file(self):
        path = Path(__file__).parent / self._prompt_file
        return path

GENERATION_TYPES = {
    "quote": GenerationType(
        name="quote",
        _prompt_file="quote.yaml",
    ),
}