import subprocess
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent.parent / 'fonts'
INSTALLED_FONTS_DIR = Path.home() / '.local' / 'share' / 'fonts' / 'ytshorts-generator'

_FONT_EXTENSIONS = ('.ttf', '.otf')


def list_font_families() -> list[str]:
    """Family names of the fonts bundled in FONTS_DIR, read directly from each file's
    metadata via fc-scan (doesn't require the font to be installed first)."""
    families = set()
    for font_file in FONTS_DIR.iterdir():
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


def ensure_fonts_installed() -> None:
    """Idempotently make FONTS_DIR discoverable to fontconfig (and therefore to the
    eventual libass/ffmpeg render) by symlinking it into the standard per-user font
    directory and refreshing fontconfig's cache."""
    if not INSTALLED_FONTS_DIR.exists():
        INSTALLED_FONTS_DIR.parent.mkdir(parents=True, exist_ok=True)
        INSTALLED_FONTS_DIR.symlink_to(FONTS_DIR, target_is_directory=True)
    subprocess.run(['fc-cache', '-f', str(INSTALLED_FONTS_DIR)], capture_output=True, check=True)
