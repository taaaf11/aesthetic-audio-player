import os
from datetime import timedelta

import flet as ft
from flet import CrossAxisAlignment, MainAxisAlignment, icons

from utils import format_timedelta_str_ms, get_src_dir_contents

# from inside, this control is just a Column control,
# so, asking about vertical and horizontal alignments makes sense


# for now, only mp3 format is supported
class AudioPlayer(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        src_dir: str | None = None,
        curr_idx: int = 0,
        font_family: str | None = None,
        controls_vertical_alignment: MainAxisAlignment = MainAxisAlignment.NONE,
        controls_horizontal_alignment: CrossAxisAlignment = CrossAxisAlignment.NONE,
        *args,
        **kwargs,
    ):
        """
        Arguments to constructor:
        page: page
        src_dir: Path to directory where audio files rest
        curr_idx: The index number of file the control should use when it is just added
        font_family: Font family to be used in the textual controls
        controls_vertical_alignment: From inside, AudioPlayer is just a Column control,
                                    so these control_..._alignment is for the Column control
        controls_horizontal_alignment: ...
        """

        super().__init__(*args, **kwargs)
        self.page_ = page
        self.__font_family = font_family

        self.__curr_idx = curr_idx

        self.src_dir = src_dir
        self.src_dir_contents = get_src_dir_contents(self.src_dir)

        self.curr_song_name = self.src_dir_contents[self.curr_idx]
        self.seek_bar = ft.ProgressBar(width=self.width)

        # for elapsed time and duration
        self.times_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # play pause next buttons
        self.play_controls = ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=icons.REPLAY_5_SHARP,
                                data="replay",
                                tooltip="Replay 5 seconds",
                                on_click=lambda _: setattr(
                                    self, "curr_pos", self.curr_pos - 5000
                                ),
                            ),
                            ft.IconButton(
                                icon=icons.SKIP_PREVIOUS_SHARP,
                                data="prev",
                                tooltip="Previous song",
                                on_click=self.prev_next_music,
                            ),
                            play_pause_btn := ft.IconButton(
                                icon=icons.PLAY_ARROW,
                                on_click=lambda _: setattr(
                                    self, "playing", not self.playing
                                ),
                            ),
                            ft.IconButton(
                                icon=icons.SKIP_NEXT_SHARP,
                                data="next",
                                tooltip="Next song",
                                on_click=self.prev_next_music,
                            ),
                            ft.IconButton(
                                icon=icons.FORWARD_5_SHARP,
                                data="forward",
                                tooltip="Forward 5 seconds",
                                on_click=lambda _: setattr(
                                    self, "curr_pos", self.curr_pos + 5000
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Container(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=icons.ADD,
                                    data="inc",
                                    on_click=self.adjust_vol,
                                    icon_size=18,
                                ),
                                ft.IconButton(
                                    icon=icons.REMOVE,
                                    data="dec",
                                    on_click=self.adjust_vol,
                                    icon_size=18,
                                ),
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ),
                ],
                spacing=0,
            ),
            width=page.width,
            alignment=ft.alignment.center,
            margin=0,
        )

        self.contents = [
            ft.Container(self.seek_bar, border_radius=20, width=self.width),
            self.times_row,
            self.play_controls,
        ]

        self.content = ft.Column(
            self.contents,
            alignment=controls_vertical_alignment,
            horizontal_alignment=controls_horizontal_alignment,
        )

        self.audio = ft.Audio(
            src=self.src_dir_contents[self.curr_idx],
            volume=1,
            on_loaded=self._show_controls,
            on_state_changed=self._on_state_change,
            on_position_changed=self._update_controls,
            # autoplay=1
        )

        self.page_.overlay.append(self.audio)
        self.page_.update()

        self.play_pause_btn = play_pause_btn

        self.__playing = False
        self.__curr_state = None

    @property
    def font_family(self):
        return self.__font_family

    @font_family.setter
    def font_family(self, value):
        for text_control in self.times_row.controls:
            text_control.font_family = value
        self.__font_family = value
        self.page_.update()

    @property
    def playing(self):
        return self.__playing

    @playing.setter
    def playing(self, value: bool):
        if value:
            self.audio.resume()
            self.play_pause_btn.icon = icons.PAUSE
            self.__playing = True
        else:
            self.audio.pause()
            self.play_pause_btn.icon = icons.PLAY_ARROW
            self.__playing = False
        self.play_pause_btn.update()

    @property
    def curr_pos(self):
        return self.__curr_pos

    @curr_pos.setter
    def curr_pos(self, value):
        self.audio.seek(value)
        self.__curr_pos = value

    @property
    def curr_idx(self):
        return self.__curr_idx

    @curr_idx.setter
    def curr_idx(self, value):
        if value >= len(self.src_dir_contents):
            value = len(self.src_dir_contents) - 1
        elif value <= 0:
            value = 0

        self.__curr_idx = value

        self._update_audio()

    @property
    def duration(self):
        return self.__duration

    @property
    def curr_state(self):
        return self.__curr_state

    @property
    def src_dir(self):
        return self.__src_dir

    @src_dir.setter
    def src_dir(self, value):
        self.__src_dir = value
        self.src_dir_contents = get_src_dir_contents(value)

    def prev_next_music(self, e):
        if e.control.data == "next":
            self.curr_idx += 1
        elif e.control.data == "prev":
            self.curr_idx -= 1

    def adjust_vol(self, e):
        if e.control.data == "inc":
            self.audio.volume += 0.05
        elif e.control.data == "dec":
            self.audio.volume -= 0.05
        self.audio.update()

    def _on_state_change(self, e):
        self.__curr_state = e.data

    # the "backend" function for prev_next_music, does all the processing needed
    # this code being present in the curr_idx.setter was not looking good
    # so created a new function
    def _update_audio(self):
        old_audio_src = self.audio.src
        old_audio_state = self.curr_state

        new_path = os.path.join(self.__src_dir, self.src_dir_contents[self.curr_idx])

        # if it is the same song as the old one, resume the audo and bail out
        if old_audio_src == new_path:
            if old_audio_state == "playing":
                self.audio.resume()
            return

        self.audio.src = new_path
        self.__duration = self.audio.get_duration()

        if old_audio_state == "playing":
            self.play_pause_btn.icon = icons.PAUSE
            # too hacky way
            self.audio.autoplay = True
        elif old_audio_state == "paused":
            self.play_pause_btn.icon = icons.PLAY_ARROW

        self.page_.update()
        self.audio.autoplay = False

    # executed when audio is loaded
    def _show_controls(self, e):
        self.seek_bar.value = 0
        self.__duration = self.audio.get_duration()

        elapsed_time, duration = self._calculate_formatted_times(0)

        self._update_times_row(elapsed_time, duration)

    # updating the progressbar and times_row
    def _update_controls(self, e):
        if self.curr_state == "completed":
            self.play_pause_btn.icon = icons.PLAY_ARROW
            self.__playing = False
            self.page_.update()
            return
        self.__curr_pos = int(e.data)  # the elapsed time
        try:
            self.seek_bar.value = self.curr_pos / self.duration
        except AttributeError:
            self.__duration = self.audio.get_duration()
        finally:
            self.seek_bar.value = self.curr_pos / self.duration

        elapsed_time, duration = self._calculate_formatted_times(self.curr_pos)

        self._update_times_row(elapsed_time, duration)

    def _calculate_formatted_times(self, elapsed_time: int):
        formatted_elapsed_time = format_timedelta_str_ms(
            str(timedelta(milliseconds=elapsed_time))
        )
        formatted_time_duration = format_timedelta_str_ms(
            str(timedelta(milliseconds=self.duration))
        )

        return formatted_elapsed_time, formatted_time_duration

    def _update_times_row(self, elapsed_time, time_duration):
        self.times_row.controls = [
            ft.Text(elapsed_time, font_family=self.__font_family),
            ft.Text(time_duration, font_family=self.__font_family),
        ]

        self.page_.update()
