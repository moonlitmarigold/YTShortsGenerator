"""Structured LLM output schemas, one per generation type.

Each generation_type's prompt (see the sibling *.yaml files) asks the model for a
specific JSON shape. These models validate/parse that JSON so the rest of the
pipeline (TTS, assembly, upload) works with typed fields instead of a raw blob.
"""
from pydantic import BaseModel


class GenerationOutput(BaseModel):
    """Base type for a generation type's structured output.

    Subclass per generation_type. Kept as a common base so SessionInfo can hold
    "some generation's output" without hard-coding a single type."""


# --- quote.yaml -------------------------------------------------------------

class VideoMetadata(BaseModel):
    suggested_title: str
    key_theme: str
    recommended_visual_mood: str


class ScriptElements(BaseModel):
    hook: str
    quote_core: str
    body_text: str
    call_to_action: str


class TimePause(BaseModel):
    """Inter-segment pauses, in milliseconds."""
    hook_quote: int
    quote_body: int
    body_call: int


class VideoGuidance(BaseModel):
    pacing_recommendation: str
    music_genre: str
    visual_text_highlight: str
    time_pause: TimePause


class QuoteOutput(GenerationOutput):
    """Expected output of generation_types/quote.yaml."""
    video_metadata: VideoMetadata
    script_elements: ScriptElements
    video_guidance: VideoGuidance
