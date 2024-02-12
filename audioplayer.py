import os
from datetime import timedelta

import flet as ft
from flet import CrossAxisAlignment, MainAxisAlignment

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

        self.curr_idx = curr_idx

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
                                icon=ft.icons.SKIP_PREVIOUS_SHARP,
                                data="prev",
                                on_click=self.prev_next_music,
                            ),
                            play_pause_btn := ft.IconButton(
                                icon=ft.icons.PLAY_ARROW, on_click=self.play_pause
                            ),
                            ft.IconButton(
                                icon=ft.icons.SKIP_NEXT_SHARP,
                                data="next",
                                on_click=self.prev_next_music,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Container(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.ADD,
                                    data="inc",
                                    on_click=self.adjust_vol,
                                    icon_size=18,
                                ),
                                ft.IconButton(
                                    icon=ft.icons.REMOVE,
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
            self.play_pause_btn.icon = ft.icons.PAUSE
            self.__playing = True
        else:
            self.audio.pause()
            self.play_pause_btn.icon = ft.icons.PLAY_ARROW
            self.__playing = False
        self.play_pause_btn.update()

    @property
    def duration(self):
        return self.__duration

    @property
    def curr_state(self):
        return self.__curr_state

    def _on_state_change(self, e):
        self.__curr_state = e.data

    def play_pause(self, e):
        if self.playing:
            self.playing = False
        else:
            self.playing = True
        self.page_.update()

    def prev_next_music(self, e):
        old_audio_src = self.audio.src
        try:
            old_audio_state = self.__curr_state
        except:  # when user has not changed the state, that is, control is just added to the page
            old_audio_state = "paused"
        self.audio.pause()
        if e.control.data == "next":
            idx = self.curr_idx + 1
            if idx >= len(self.src_dir_contents):
                idx = len(self.src_dir_contents) - 1
        elif e.control.data == "prev":
            idx = self.curr_idx - 1
            if idx <= 0:
                idx = 0
        self.curr_idx = idx

        new_path = os.path.join(self.src_dir, self.src_dir_contents[self.curr_idx])
        self.curr_song_name = self.src_dir_contents[self.curr_idx]

        # if it is the same song as the old one, resume the audo and bail out
        if old_audio_src == new_path:
            if old_audio_state == "playing":
                self.audio.resume()
            return

        self.audio.src = new_path
        self.__duration = self.audio.get_duration()

        if old_audio_state == "playing":
            self.play_pause_btn.icon = ft.icons.PAUSE
            # too hacky way
            self.audio.autoplay = True
        elif old_audio_state == "paused":
            self.play_pause_btn.icon = ft.icons.PLAY_ARROW

        self.page_.update()
        self.audio.autoplay = False

    def adjust_vol(self, e):
        if e.control.data == "inc":
            self.audio.volume += 0.1
        elif e.control.data == "dec":
            self.audio.volume -= 0.1
        self.audio.update()

    # executed when audio is loaded
    def _show_controls(self, e):
        self.seek_bar.value = 0
        self.__duration = self.audio.get_duration()

        elapsed_time, duration = self._calculate_formatted_times(0)

        self._update_times_row(elapsed_time, duration)

    # updating the progressbar and times_row
    def _update_controls(self, e):
        if self.curr_state == "completed":
            self.play_pause_btn.icon = ft.icons.PLAY_ARROW
            self.__playing = False
            self.page_.update()
            return
        curr_time = int(e.data)  # the elapsed time
        try:
            self.seek_bar.value = curr_time / self.duration
        except AttributeError:
            self.__duration = self.audio.get_duration()
        finally:
            self.seek_bar.value = curr_time / self.duration

        elapsed_time, duration = self._calculate_formatted_times(curr_time)

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
