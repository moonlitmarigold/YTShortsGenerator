from .. import sessions
from .. import utils
from SubtitleFX import Formatters, Config, Style, DockerConfig, BorderConfig, SubtitleBuild
import pysubs2
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
        'one_word': Formatters.one_word,
        'joined': Formatters.joined,
        'sentence': Formatters.sentence,
    }


    def run(self, session:sessions.SessionInfo):
        script = session.script

        config:Config = self.return_config(
            script.style_defaults,
            self.resolution,
            session.background_video(),
            self.background_config
        )

        subtitles_files:list[pysubs2.ssafile.SSAFile] = list()

        for scene in script.scenes:
            subtitles_files.append(
                self.edit_sub_file(
                    scene,
                    session,
                    config,
                )
            )

        # add events to export file
        output_file = subtitles_files[0]
        for file in subtitles_files[1:]:
            events = output_file.events
            events.extend(file.events)
            output_file.events = events
        output_file.save(session.subtitle_file(), format_='ass')

    @staticmethod
    def return_config(style_class:utils.schemas.StyleDefaults, resolution:tuple[int, int], video:Path, background_config:utils.SubtitleBackground=None,):
        highlight_class = style_class.highlighting


        docker_conf = DockerConfig(
            fonts_path=str(Path(__file__).parent.parent / "fonts"),
            force_install=True,
        )

        if highlight_class.fade_ms:
            fade = (float(highlight_class.fade_ms[0]), float(highlight_class.fade_ms[1]))
        else:
            fade = (0, 0)

        if background_config:
            rounded_border = background_config.rounded_border
            bg_conf = BorderConfig(
                radius=background_config.radius,
                transformy=background_config.transformy,
                offset=background_config.offset,
                height_scaling=background_config.height_scaling,
            )

        else:
            rounded_border = True
            bg_conf = BorderConfig()

        if highlight_class.enabled:
            highlight_char_max = highlight_class.word_max
            highlight_as_borders = highlight_class.as_borders
            if highlight_class.font_size:
                highlight_style = Style(
                    primarycolor=style_class.highlight_color,
                    fontsize=highlight_class.font_size
                )
            else:
                highlight_style = Style(
                    primarycolor=style_class.highlight_color,
                )
        else:
            highlight_style = None
            highlight_char_max = None
            highlight_as_borders = False

        print(str(video))
        conf =  Config(
            input='', output=None,
            input_video=str(video),
            subtitle_style=Style(
                fontname=style_class.font_family,
                fontsize=style_class.font_size,
                primarycolor=style_class.primary_text_color,
            ),
            highlight_style=highlight_style,
            subtitle_type= Subtitles.formatter.get(style_class.subtitle_type, Formatters.sentence),
            char_max=style_class.word_max if style_class.word_max else 11,
            resolution=resolution,
            fill_sub_times=style_class.fill_sub_times,
            alignment = Subtitles.alignment.get(style_class.text_position, 5),
            rounded_border =  rounded_border,
            border_config=bg_conf,
            appear=highlight_class.appear,
            fade= fade,
            docker_config=docker_conf,
            highlight_char_max=highlight_char_max,
            highlight_as_borders=highlight_as_borders,
        )

        return conf


    @staticmethod
    def edit_sub_file(scene:utils.schemas.Scene, session:sessions.SessionInfo, config:Config):
        scene_id = scene.id
        input_path = session.transcribe_path(scene_id)

        # Load in the subfile
        tmp_subfile = pysubs2.SSAFile().from_file(input_path.open())

        config.input = tmp_subfile

        with SubtitleBuild(config) as Build:
            Build.run()
            sub_file = Build.save()

        return sub_file