from omni import ui
from omni.kit.environment.core import Clock
from .style import CLOCK_STYLE


class ClockWindow(ui.Window):
    def __init__(self, model: ui.AbstractValueModel):
        flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_POPUP
        )
        super().__init__("Clock", flags=flags, width=0, height=0, padding_x=0, padding_y=0)

        self._container = None
        self._calendar = None
        self._model = model
        self.frame.set_style(CLOCK_STYLE)
        self._build_ui()

    def _build_ui(self):
        with self.frame:
            self._container = ui.VStack()
            with self._container:
                ui.Spacer(height=5)
                self._clock = Clock(self._model)
                ui.Spacer(height=5)

    @property
    def computed_content_width(self) -> float:
        if self._container is not None:
            return self._container.computed_content_width
        else:
            return 0

    @property
    def computed_content_height(self) -> float:
        if self._container is not None:
            return self._container.computed_content_height
        else:
            return 0
