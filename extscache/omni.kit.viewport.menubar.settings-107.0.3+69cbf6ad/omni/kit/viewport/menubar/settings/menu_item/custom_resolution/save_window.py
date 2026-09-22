from typing import Tuple, Callable
import omni.ui as ui
from ...style import SAVE_WINDOW_STYLE  # noqa: PLE0402


class SaveWindow(ui.Window):
    """
    Window to save custom resolution.
    """
    PADDING = 8

    def __init__(self, resolution: Tuple[int, int], on_save_fn: Callable[[str, Tuple[int, int]], bool]):
        self.name_model = ui.SimpleStringModel()
        self.__resolution = resolution
        self.__on_save_fn = on_save_fn
        self.__sub_begin_edit = None

        flags = ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_MODAL
        super().__init__("Save Resolution", width=400, height=180, flags=flags, auto_resize=False, padding_x=0, padding_y=0)

        self.frame.set_style(SAVE_WINDOW_STYLE)
        self.frame.set_build_fn(self.__build_ui)

    def __del__(self):
        self.__sub_begin_edit = None
        self.destroy()

    def __build_ui(self):
        with self.frame:
            with ui.VStack(height=0):
                self._build_titlebar()
                ui.Spacer(height=30)
                self._build_input()
                ui.Spacer(height=30)
                self._build_buttons()
                ui.Spacer(height=15)

    def _build_titlebar(self):
        with ui.ZStack(height=0):
            ui.Rectangle(style_tyle_name_override="Titlebar.Background")
            with ui.VStack():
                ui.Spacer(height=self.PADDING)
                with ui.HStack():
                    ui.Spacer(width=self.PADDING)
                    ui.Label("Save Custom Viewport Resolution", width=0, style_type_name_override="Titlebar.Title")
                    ui.Spacer()
                    ui.Image(width=20, height=20, mouse_released_fn=lambda x, y, b, f: self.__on_cancel(), name="close")
                    ui.Spacer(width=self.PADDING)
                ui.Spacer(height=self.PADDING)

    def _build_input(self):
        with ui.HStack():
            ui.Spacer()
            with ui.ZStack(width=160):
                name_input = ui.StringField(self.name_model)
                hint_label = ui.Label("Type Name", style_type_name_override="Input.Hint")
            ui.Spacer(width=20)
            ui.Label(f"{self.__resolution[0]} x {self.__resolution[1]}")
            ui.Spacer()

        name_input.focus_keyboard()

        def __hide_hint():
            hint_label.visible = False

        self.__sub_begin_edit = self.name_model.subscribe_begin_edit_fn(lambda m: __hide_hint())

    def _build_buttons(self):
        with ui.HStack():
            ui.Spacer()
            ui.Button("Save", width=80, clicked_fn=self.__on_save)
            ui.Spacer(width=20)
            ui.Button("Cancel", width=80, clicked_fn=self.__on_cancel)
            ui.Spacer()

    def __on_save(self) -> None:
        if self.__on_save_fn(self.name_model.as_string, self.__resolution):
            self.visible = False  # noqa: PLW0201

    def __on_cancel(self) -> None:
        self.visible = False  # noqa: PLW0201
