import subprocess
from pathlib import Path
from matplotlib.font_manager import get_font_names

_FONT_EXTENSIONS = ('.ttf', '.otf')


def list_font_families() -> list[str]:
    font_dir = Path(__file__).parent.parent / "fonts"
    font_dir.mkdir(exist_ok=True)
    families = set()
    for font_file in font_dir.iterdir():
        if font_file.suffix.lower() not in _FONT_EXTENSIONS:
            continue
        result = subprocess.run(
            ['fc-scan', '--format', '%{family[0]}\n', str(font_file)],
            capture_output=True, text=True, check=True,
        )
        family = result.stdout.strip()
        if family:
            families.add(family)
    return sorted(families)

def font_exists(name):
    """
    Check if a font family exists on the system.
    :param name: The name of the font family (e.g., 'Arial', 'Courier New').
    :return: True if the font exists, False otherwise.
    """
    return name in get_font_names()

def find_font_file(name: str) -> Path:
    """Resolve a font family name to an actual font file, for renderers (e.g. PIL) that need a path rather than a family name.

    Checks the project's own src/fonts directory first (same fc-scan match used by
    list_font_families), then falls back to matplotlib's system font lookup.
    """
    font_dir = Path(__file__).parent.parent / "fonts"
    for font_file in font_dir.iterdir():
        if font_file.suffix.lower() not in _FONT_EXTENSIONS:
            continue
        result = subprocess.run(
            ['fc-scan', '--format', '%{family[0]}\n', str(font_file)],
            capture_output=True, text=True, check=True,
        )
        if result.stdout.strip() == name:
            return font_file

    from matplotlib import font_manager
    return Path(font_manager.findfont(font_manager.FontProperties(family=name)))


def write_font_file():
    fonts_1 = get_font_names()
    fonts_2 = list_font_families()
    fonts_1.extend(fonts_2)
    fonts_1.sort()

    fonts_file = Path(__file__).parent.parent / "fonts" / "fonts.txt"
    fonts_file.write_text('\n'.join(fonts_1))
    return str(fonts_file)

