import os

import flet as ft
from flet import CrossAxisAlignment, MainAxisAlignment, OptionalNumber

from audioplayer import AudioPlayer


class AestheticAudioPlayer(AudioPlayer):
    def __init__(
        self,
        page: ft.Page,
        image_src: str | None = None,
        image_width: OptionalNumber = None,
        image_height: OptionalNumber = None,
        src_dir: str | None = None,
        curr_idx: int | None = 0,
        font_family: str | None = None,
        controls_vertical_alignment: MainAxisAlignment = MainAxisAlignment.NONE,
        controls_horizontal_alignment: CrossAxisAlignment = CrossAxisAlignment.NONE,
        *args,
        **kwargs
    ):
        super().__init__(
            page=page,
            src_dir=src_dir,
            curr_idx=curr_idx,
            font_family=font_family,
            controls_vertical_alignment=controls_vertical_alignment,
            controls_horizontal_alignment=controls_horizontal_alignment,
            *args,
            **kwargs
        )

        self.image = ft.Image(
            src=image_src,
            width=image_width,
            height=image_height,
        )

        # this can be modified by user, like, he wants something other
        # than the name of song, like,
        # Life ❤
        self.song_name = ft.TextField(
            value=self._sep_file_ext(
                os.path.basename(self.src_dir_contents[self.curr_idx])
            ),
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD, size=19, font_family=font_family
            ),
            border_width=0,
            text_align=ft.TextAlign.CENTER,
        )

        # in the parent class, self.contents contains only bare music controls
        # now I add some bells and swings to it
        self.contents = [self.image, self.song_name] + self.contents  # of parent class

        self.content = ft.Column(
            self.contents, horizontal_alignment=controls_horizontal_alignment
        )
    
    @property
    def font_family(self):
        return self.__font_family
    
    @font_family.setter
    def font_family(self, value):
        for text_control in self.times_row.controls:
            text_control.font_family = value
        self.__font_family = value
        self.page_.update()

    @staticmethod
    def _sep_file_ext(filename: str):
        split_ = filename.split(".")
        if len(split_) > 2:
            return ".".join(split_[:-1])
        else:
            return split_[0]

    def prev_next_music(self, e):
        super().prev_next_music(e)
        self.song_name.value = self._sep_file_ext(os.path.basename(self.audio.src))
