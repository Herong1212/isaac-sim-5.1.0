import omni.ui as ui
from omni.ui import color as cl

## colors
LABEL_COLOR = 0xFFD8D8D8
DISABLED_COLOR = 0xFF6E6E6E
FONT_SIZE = 12
PROGRESS_BACKGROUND = 0x0
PROGRESS_BORDER = 0xFF323434
PROGRESS_BAR = 0xFFC9974C
PROGRESS_TEXT_COLOR = 0xFFD8D8D8
WINDOW_BACKGRUND = 0xCC484848
GREEN_COLOR = cl(0.3, 1.0, 0.3, 1.0)
PROFILER_WINDOW_STYLE = {
    "Button": {"border_radius": 2, "padding": 2},
    "Button:disabled": {"background_color": DISABLED_COLOR, "border_radius": 2, "padding": 2},
    "CheckBox": {"border_radius": 4},
    "Drag": {"border_radius": 2, "padding": 2},
    "Label.Green": {"color": GREEN_COLOR},
    "ProgressBar": {
        "background_color": PROGRESS_BACKGROUND,
        "border_width": 2,
        "border_radius": 0,
        "border_color": PROGRESS_BORDER,
        "color": PROGRESS_BAR,
        "secondary_color": PROGRESS_TEXT_COLOR,
        "margin": 0,
        "padding": 1,
        "font_size": FONT_SIZE,
        "alignment": ui.Alignment.LEFT_CENTER,
    },
    "Window": {"background_color": WINDOW_BACKGRUND},
}
