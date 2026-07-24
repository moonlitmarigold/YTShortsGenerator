from .. import sessions
from .. import utils
from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Thumbnail:

    resolution: tuple[int, int]
    margin: int = 60
    stroke_color: str = '#000000'

    def run(self, session: sessions.SessionInfo):
        logger.debug('Starting thumbnail generation')
        script = session.script
        style = script.style_defaults

        clip = VideoFileClip(str(session.background_video()))
        try:
            frame = clip.get_frame(clip.duration / 2)
        finally:
            clip.close()

        image = self._fit_to_resolution(Image.fromarray(frame), self.resolution)
        draw = ImageDraw.Draw(image)

        font_path = utils.fonts.find_font_file(style.font_family)
        max_width = image.width - 2 * self.margin
        max_height = image.height - 2 * self.margin
        font, lines = self._fit_text(draw, script.video_metadata.suggested_title, font_path, max_width, max_height)

        self._draw_lines(draw, image, lines, font, style)

        image.save(session.thumbnail_path())
        logger.debug(f'Saved thumbnail to {session.thumbnail_path()}')

    @staticmethod
    def _fit_to_resolution(image: Image.Image, resolution: tuple[int, int]) -> Image.Image:
        """Scale-to-cover + center-crop, mirroring Background._fit_to_resolution so the thumbnail matches the video's own framing."""
        target_w, target_h = resolution
        scale = max(target_w / image.width, target_h / image.height)
        resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
        left = (resized.width - target_w) / 2
        top = (resized.height - target_h) / 2
        return resized.crop((left, top, left + target_w, top + target_h))

    @staticmethod
    def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        lines = []
        current = ''
        for word in text.split():
            candidate = f'{current} {word}'.strip()
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _fit_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font_path,
        max_width: int,
        max_height: int,
        start_size: int = 180,
        min_size: int = 48,
    ) -> tuple[ImageFont.FreeTypeFont, list[str]]:
        size = start_size
        while size > min_size:
            font = ImageFont.truetype(str(font_path), size)
            lines = self._wrap_text(draw, text, font, max_width)
            if self._block_height(font, lines) <= max_height:
                return font, lines
            size -= 4

        font = ImageFont.truetype(str(font_path), min_size)
        return font, self._wrap_text(draw, text, font, max_width)

    @staticmethod
    def _block_height(font: ImageFont.FreeTypeFont, lines: list[str]) -> float:
        line_height = font.getbbox('Ag')[3] * 1.2
        return line_height * len(lines)

    def _draw_lines(self, draw: ImageDraw.ImageDraw, image: Image.Image, lines: list[str], font: ImageFont.FreeTypeFont, style):
        line_height = font.getbbox('Ag')[3] * 1.2
        block_height = line_height * len(lines)

        if style.text_position == utils.schemas.TextPosition.top:
            y = self.margin
        elif style.text_position == utils.schemas.TextPosition.bottom:
            y = image.height - self.margin - block_height
        else:
            y = (image.height - block_height) / 2

        stroke_width = max(round(font.size / 18), 2)
        for line in lines:
            width = draw.textlength(line, font=font)
            x = (image.width - width) / 2
            draw.text(
                (x, y),
                line,
                font=font,
                fill=style.primary_text_color,
                stroke_width=stroke_width,
                stroke_fill=self.stroke_color,
            )
            y += line_height
