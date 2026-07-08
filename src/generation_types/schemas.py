# schemas.py
from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Union, Optional

class Platform(str, Enum):
    tiktok = "tiktok"
    reels = "reels"
    shorts = "shorts"

class POV(str, Enum):
    direct_address = "direct_address"
    narrator = "narrator"

class DisplayMode(str, Enum):
    full_sentence = "full_sentence"
    highlighted_keywords = "highlighted_keywords"
    word_by_word = "word_by_word"
    keyword_only = "keyword_only"

class Emphasis(str, Enum):
    color_pop = "color_pop"
    size_pop = "size_pop"
    underline = "underline"
    shake = "shake"
    none = "none"

class SceneType(str, Enum):
    hook = "hook"
    quote_core = "quote_core"
    body = "body"
    call_to_action = "call_to_action"

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


class VideoMetadata(BaseModel):
    suggested_title: str
    key_theme: str
    total_duration_seconds: Optional[int] = None
    platform: Platform


class StyleDefaults(BaseModel):
    font_family: str
    font_size: str
    primary_text_color: str
    highlight_color: str
    text_position: str
    background_overlay: Optional[str] = None


class HighlightWord(BaseModel):
    word: str
    emphasis: Emphasis


class Scene(BaseModel):
    id: int
    type: SceneType
    spoken_text: str
    display_mode: DisplayMode
    on_screen_text: Union[str, list[str]]
    highlight_words: list[HighlightWord] = []
    duration_ms: int
    style_override: Optional[dict] = None

    @field_validator("highlight_words")
    @classmethod
    def words_must_appear_in_spoken_text(cls, words, info):
        spoken = info.data.get("spoken_text", "").lower()
        for hw in words:
            if hw.word.lower() not in spoken:
                raise ValueError(
                    f"highlight word '{hw.word}' not found verbatim in spoken_text"
                )
        return words


class VideoGuidance(BaseModel):
    pacing_recommendation: Pacing
    music_genre: MusicGenre
    music_energy_curve: Optional[str] = None


class GeneratedVideoScript(BaseModel):
    video_metadata: VideoMetadata
    style_defaults: StyleDefaults
    scenes: list[Scene]
    quote_variants: list[str] = []
    video_guidance: VideoGuidance