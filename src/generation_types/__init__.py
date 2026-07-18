import dataclasses
from pathlib import Path
from . import hooks

@dataclasses.dataclass
class GenerationType:
    name: str
    _prompt_file: str  # points at the .yaml/.md next to it
    hooks:tuple
    resolution:tuple[int, int]

    @property
    def prompt_file(self):
        path = Path(__file__).parent / self._prompt_file
        return path

    def read_file(self):
        return self.prompt_file.read_text()

    def return_file(self, context:dict):
        prompt_text = self.read_file()
        prompt_text = hooks.hook_metadata(prompt_text, context)

        for hook in self.hooks:
            prompt_text = hook(prompt_text, context)

        return prompt_text

GENERATION_TYPES = {
    "quote": GenerationType(
        name="quote",
        _prompt_file="quote.md",
        hooks=(
            hooks.hook_fonts,
        ),
        resolution=(1080, 1920)
    ),
}
