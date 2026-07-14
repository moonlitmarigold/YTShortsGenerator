from .. import sessions
from .. import utils
import SubTextHighlight
import pysubs2
from pathlib import Path

alignment = {
    'top': 8,
    'center': 5,
    'bottom':2,
}

formatter = {
    'one_word' : SubTextHighlight.Formatters.one_word,
    'joined': SubTextHighlight.Formatters.joined,
    'sentence': SubTextHighlight.Formatters.sentence,
}

class Subtitles:



    def run(self, session:sessions.SessionInfo):
        script = session.script

        config:SubTextHighlight.SubtitleConfig = self.return_config(script.style_defaults)

        for scene in script.scenes:
            self.edit_sub_file(
                scene,
                session,
                config
            )

    @staticmethod
    def return_config(style_class:utils.schemas.StyleDefaults):
        highlight_class = style_class.highlighting
        conf =  SubTextHighlight.SubtitleConfig(
            '', None,
            subtitle_style=SubTextHighlight.StyleConfig(
                fontname=style_class.font_family,
                fontsize=style_class.font_size,
                primarycolor=style_class.primary_text_color,

            ),
            subtitle_type=formatter.get(style_class.subtitle_type, SubTextHighlight.Formatters.sentence),
            word_max=style_class.word_max if style_class.word_max else 11,
            fill_sub_times=style_class.fill_sub_times,
            alignment = alignment.get(style_class.text_position, 5),
            rounded_border=True,
            appear=highlight_class.appear,
            fonts_path=str(Path(__file__).parent.parent / "fonts"),
            docker_force_install=True,
        )
        if highlight_class.fade_ms:
            conf.fade = (float(highlight_class.fade_ms[0]), float(highlight_class.fade_ms[1]))
        if highlight_class.enabled:
            conf.highlight_word_max = highlight_class.word_max
            conf.highlight_as_borders = highlight_class.as_borders
            if highlight_class.font_size:
                highlight_style = SubTextHighlight.StyleConfig(
                    primarycolor=style_class.highlight_color,
                    fontsize=highlight_class.font_size
                )
            else:
                highlight_style = SubTextHighlight.StyleConfig(
                    primarycolor=style_class.highlight_color,
                )

            conf.highlight_style = highlight_style
        return conf

    def edit_sub_file(self, scene:utils.schemas.Scene, session:sessions.SessionInfo, config:SubTextHighlight.SubtitleConfig):
        scene_id = scene.id
        input_path = session.transcribe_path(scene_id)
        output_path = session.subtitle_file(scene_id)
        config.input = str(input_path)
        config.output = str(output_path)
        config.render()