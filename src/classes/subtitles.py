from .. import sessions
from .. import utils
import SubTextHighlight
import pysubs2
import pydub
from pathlib import Path
import dataclasses


@dataclasses.dataclass
class Subtitles:

    resolution: tuple[int, int]
    background_config:utils.SubtitleBackground = None

    alignment = {
        'top': 8,
        'center': 5,
        'bottom': 2,
    }

    formatter = {
        'one_word': SubTextHighlight.Formatters.one_word,
        'joined': SubTextHighlight.Formatters.joined,
        'sentence': SubTextHighlight.Formatters.sentence,
    }


    def run(self, session:sessions.SessionInfo):
        script = session.script

        config:SubTextHighlight.SubtitleConfig = self.return_config(
            script.style_defaults,
            self.background_config
        )

        subtitles_files:list[pysubs2.ssafile.SSAFile] = list()

        for scene in script.scenes:
            subtitles_files.append(
                self.edit_sub_file(
                    scene,
                    session,
                    config,
                    self.resolution
                )
            )

        cur_duration:float = 0.0
        for i, file in enumerate(subtitles_files):
            file.shift(s=cur_duration)

            # add duration
            audio = pydub.AudioSegment.from_file(str(session.audio_path(i)))
            cur_duration += audio.duration_seconds

        # add events to export file
        output_file = subtitles_files[0]
        for file in subtitles_files[1:]:
            events = output_file.events
            events.extend(file.events)
            output_file.events = events
        output_file.to_file(session.subtitle_file(), format_='ass')

    @staticmethod
    def return_config(style_class:utils.schemas.StyleDefaults, background_config:utils.SubtitleBackground=None):

        highlight_class = style_class.highlighting
        conf =  SubTextHighlight.SubtitleConfig(
            '', None,
            subtitle_style=SubTextHighlight.StyleConfig(
                fontname=style_class.font_family,
                fontsize=style_class.font_size,
                primarycolor=style_class.primary_text_color,

            ),
            subtitle_type= Subtitles.formatter.get(style_class.subtitle_type, SubTextHighlight.Formatters.sentence),
            word_max=style_class.word_max if style_class.word_max else 11,
            fill_sub_times=style_class.fill_sub_times,
            alignment = Subtitles.alignment.get(style_class.text_position, 5),
            rounded_border=True,
            appear=highlight_class.appear,
            fonts_path=str(Path(__file__).parent.parent / "fonts"),
            docker_force_install=True,
        )
        if highlight_class.fade_ms:
            conf.fade = (float(highlight_class.fade_ms[0]), float(highlight_class.fade_ms[1]))
        if background_config:
            conf.radius = background_config.radius
            conf.transformy = background_config.transformy
            conf.offset = background_config.offset
            conf.height_scaling = background_config.height_scaling
            conf.rounded_border = background_config.rounded_border


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

    @staticmethod
    def edit_sub_file(scene:utils.schemas.Scene, session:sessions.SessionInfo, config:SubTextHighlight.SubtitleConfig, resolution:tuple[int, int]):
        scene_id = scene.id
        input_path = session.transcribe_path(scene_id)

        #TODO: Cleanup the resolution mess

        # Load in the subfile
        tmp_subfile = pysubs2.SSAFile().from_file(input_path.open())
        tmp_subfile.info['PlayResX'] = str(resolution[0])
        tmp_subfile.info['PlayResY'] = str(resolution[1])

        # save to tmp, so that the package can read it
        tmp_path = session.transcribe_path(scene_id)
        tmp_subfile.save(tmp_path)

        config.input = str(tmp_path)
        return config.render()