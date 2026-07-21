# schemas.py
import re
from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Optional
from . import fonts

HEX_COLOR_RE = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')

class Platform(str, Enum):
    tiktok = "tiktok"
    reels = "reels"
    shorts = "shorts"

class POV(str, Enum):
    direct_address = "direct_address"
    narrator = "narrator"

class SceneType(str, Enum):
    hook = "hook"
    quote_core = "quote_core"
    body = "body"
    call_to_action = "call_to_action"

class TextPosition(str, Enum):
    top = 'top'
    center = 'center'
    bottom = 'bottom'

class Pacing(str, Enum):
    slow_and_steady = "slow_and_steady"
    moderate_with_pauses = "moderate_with_pauses"
    quick_cuts = "quick_cuts"
    rapid_fire = "rapid_fire"

class MusicGenre(str, Enum):
    cinematic_orchestral = "cinematic_orchestral"
    lofi_hiphop = "lofi_hiphop"
    indie_pop = "indie_pop"
    dark_ambient = "dark_ambient"
    epic_trailer = "epic_trailer"
    piano_minimal = "piano_minimal"

class BackgroundGenre(str, Enum):
    minecraft_parkour = "minecraft_parkour"
    subway_surfers = "subway_surfers"
    cooking = "cooking"
    satisfying_asmr = "satisfying_asmr"

class SubtitleType(str, Enum):
    one_word = "one_word"
    joined = "joined"
    sentence = "sentence"

class VideoMetadata(BaseModel):
    suggested_title: str
    key_theme: str
    video_description: Optional[str] = None
    tags: list[str] = []
    total_duration_seconds: Optional[float] = None
    platform: Platform

class HighlightConfig(BaseModel):
    """Video-wide, locked-for-the-whole-video highlighting behavior.

    Mirrors the SubTextHighlight library's SubtitleConfig/StyleConfig options
    (https://github.com/moonlitmarigold/SubTextHighlight) so it can be passed
    through to the renderer near verbatim. Word selection itself is no longer
    authored by the AI - it's derived downstream from transcription timestamps.
    """
    enabled: bool = True
    word_max: Optional[int] = None
    as_borders: bool = False
    fade_ms: Optional[tuple[int, int]] = None
    appear: bool = False
    font_size: Optional[int] = None

class StyleDefaults(BaseModel):
    font_family: str
    font_size: int
    primary_text_color: str
    highlight_color: str
    text_position: TextPosition
    background_color: Optional[str] = None
    # Base subtitle line chunking - distinct from highlighting.word_max (how many
    # words get highlighted at once). None -> SubTextHighlight's library default of 11.
    word_max: Optional[int] = None
    subtitle_type: SubtitleType = SubtitleType.joined
    fill_sub_times: bool = True
    highlighting: HighlightConfig

    @field_validator("font_family", mode="after")
    @classmethod
    def font_family_must_be_allowed(cls, value):
        if not fonts.font_exists(value) and value not in fonts.list_font_families():
            raise ValueError(f'Font {value} does not exist/ is installed on this machine. A file of all accessible fonts is in {fonts.write_font_file()}')
        return value

    @field_validator("primary_text_color", "highlight_color", "background_color", mode="after")
    @classmethod
    def must_be_hex_color(cls, value):
        if value is not None and not HEX_COLOR_RE.match(value):
            raise ValueError(f'{value!r} is not a valid hex color (expected e.g. "#FFFFFF" or "#FFF")')
        return value


class Scene(BaseModel):
    id: int
    type: SceneType
    spoken_text: str
    duration_ms: int
    style_override: Optional[dict] = None

class VideoGuidance(BaseModel):
    pacing_recommendation: Pacing
    music_genre: MusicGenre
    music_energy_curve: Optional[str] = None
    background_genre: BackgroundGenre


class GeneratedVideoScript(BaseModel):
    video_metadata: VideoMetadata
    style_defaults: StyleDefaults
    scenes: list[Scene]
    video_guidance: VideoGuidance
