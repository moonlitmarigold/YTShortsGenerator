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

def write_font_file():
    fonts_1 = get_font_names()
    fonts_2 = list_font_families()
    fonts_1.extend(fonts_2)
    fonts_1.sort()

    fonts_file = Path(__file__).parent.parent / "fonts" / "fonts.txt"
    fonts_file.write_text('\n'.join(fonts_1))
    return str(fonts_file)

