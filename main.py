import flet as ft
from flet import icons

from aesthetic_audioplayer import AestheticAudioPlayer

_current_theme_mode = None
window_always_on_top = None

# can't use None(var)
none_r = lambda var: None if var == "None" else var


def main(page: ft.Page):
    music_folder_path = page.client_storage.get("Aesthetic Vibes Music Folder")
    image_src = page.client_storage.get("Aesthetic Vibes Image")
    color_scheme_seed = page.client_storage.get("Aesthetic Vibes Color Scheme Seed")

    page.title = "Aesthetic Audio Player"

    page.window_frameless = True
    page.window_width = 386
    page.window_height = 500

    global window_always_on_top
    window_always_on_top = False
    page.window_always_on_top = window_always_on_top

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.theme = ft.Theme(
        color_scheme_seed=(
            "Pink" if none_r(color_scheme_seed) is None else color_scheme_seed
        ),
        font_family="Comfortaa",
    )
    page.theme_mode = ft.ThemeMode.SYSTEM

    global _current_theme_mode
    _current_theme_mode = page.platform_brightness

    page.fonts = {
        "Comfortaa": "Comfortaa-Regular.ttf",
        "Symbols-NF": "SymbolsNerdFont-Regular.ttf",
    }

    def _switch_visible_page(idx):
        if idx == 0:
            main_page.visible = True
            settings_page.visible = False

            page.scroll = None
        elif idx == 1:
            main_page.visible = False
            settings_page.visible = True

            page.scroll = ft.ScrollMode.AUTO

    def navigate_to_page(e):
        selected_page = e.control.selected_index
        _switch_visible_page(selected_page)

        page.close_drawer()
        page.update()

    def handle_keyboard_shortcuts(e: ft.KeyboardEvent):
        if e.ctrl:
            if e.key == ",":
                _switch_visible_page(1)
            elif e.key == ".":
                _switch_visible_page(0)
        page.update()

    def switch_theme_mode(e):
        global _current_theme_mode
        if _current_theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            _current_theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.DARK
            _current_theme_mode = ft.ThemeMode.DARK
        page.update()

    def set_color_scheme(e):
        page.client_storage.set(
            "Aesthetic Vibes Color Scheme Seed", color_scheme_seed_field.value
        )

    def select_audio_folder(e):
        filepicker = ft.FilePicker(
            on_result=lambda e: page.client_storage.set(
                "Aesthetic Vibes Music Folder", e.path
            )
        )
        page.overlay.append(filepicker)
        page.update()
        filepicker.get_directory_path("Select folder")

    def select_image(e):
        filepicker = ft.FilePicker(
            on_result=lambda e: page.client_storage.set(
                "Aesthetic Vibes Image", e.files[0].path
            )
        )
        page.overlay.append(filepicker)
        page.update()
        filepicker.pick_files("Select image")

    def del_app_data(e):
        page.client_storage.set("Aesthetic Vibes Music Folder", "None")
        page.client_storage.set("Aesthetic Vibes Image", "None")
        page.client_storage.set("Aesthetic Vibes Color Scheme Seed", "None")

    def switch_windows_always_on_top(e):
        global window_always_on_top
        page.window_always_on_top = not window_always_on_top
        window_always_on_top = not window_always_on_top
        page.update()

    page.appbar = ft.AppBar(
        title=ft.WindowDragArea(ft.Text(page.title)),
        center_title=True,
        leading=ft.IconButton(
            icons.MENU_SHARP, on_click=lambda _: page.show_drawer(page.drawer)
        ),
    )

    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.NavigationDrawerDestination(
                icon=icons.HOME_OUTLINED,
                label="Home",
                selected_icon=icons.HOME_SHARP,
            ),
            ft.NavigationDrawerDestination(
                icon=icons.SETTINGS_OUTLINED,
                label="Settings",
                selected_icon=icons.SETTINGS_SHARP,
            ),
        ],
        selected_index=0,
        on_change=navigate_to_page,
    )

    if none_r(music_folder_path) is None:
        main_page = ft.Text(
            "Please select musics folder in settings menu, and restart."
        )
    else:
        if none_r(image_src) is None:
            image_src = "aesthetic_vibes.jpg"

        main_page = AestheticAudioPlayer(
            page=page,
            image_src=image_src,
            image_width=page.width / 4,
            image_height=page.height / 4,
            src_dir=music_folder_path,
            curr_idx=0,
            font_family="Comfortaa",
            controls_vertical_alignment=ft.MainAxisAlignment.CENTER,
            controls_horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    settings_page = ft.Column(
        [
            # image selection controls
            ft.Row(
                [
                    ft.Text(
                        "Image to show:",
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.IconButton(
                        icon=icons.FOLDER_OUTLINED,
                        on_click=select_image,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=0,
            ),
            # music folder selection controls
            ft.Row(
                [
                    ft.Text(
                        "Select a folder with songs:",
                        size=20,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.IconButton(
                        icon=icons.FOLDER_OUTLINED,
                        on_click=select_audio_folder,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=0,
            ),
            # delete app data button
            ft.Row(
                [
                    ft.Text(
                        "Delete app data: ", size=20, text_align=ft.TextAlign.CENTER
                    ),
                    ft.IconButton(icon=icons.DELETE, on_click=del_app_data),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=0,
            ),
            # theme mode switch button
            ft.IconButton(
                content=ft.Text("󰔎  Switch theme", size=20, font_family="Symbols-NF"),
                on_click=switch_theme_mode,
            ),
            # specify color scheme seed text_field and submit button
            ft.Row(
                [
                    ft.Container(
                        color_scheme_seed_field := ft.TextField(
                            hint_text="color scheme seed e.g. #ff0266"
                        ),
                        width=page.width / 4,
                    ),
                    ft.IconButton(icon=icons.CHECK, on_click=set_color_scheme),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # window always on top
            ft.IconButton(
                icon=icons.TOPIC,
                on_click=switch_windows_always_on_top,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=18,
        visible=False,
    )

    page.add(main_page, settings_page)

    # page.on_resize = lambda _: print(page.window_width, page.window_height)
    page.on_keyboard_event = handle_keyboard_shortcuts


ft.app(main)
