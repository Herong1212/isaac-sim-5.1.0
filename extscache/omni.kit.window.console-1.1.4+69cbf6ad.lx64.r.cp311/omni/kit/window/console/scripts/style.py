import carb.logging
import omni.ui as ui
from omni.ui import color as cl

CL_LOG_DEFAULT = cl(0.5, 0.5, 0.5, 1)
CL_LOG_VERBOSE = cl('#BABABA')
CL_LOG_INFO = cl('#79BAEB')
CL_LOG_WARNING = cl('#DFCB4A')
CL_LOG_ERROR = cl('#F6B1AA')
CL_LOG_FATAL = cl(0.96471, 0.69412, 0.66667, 1)

LOG_LEVEL_ICONS = {
    carb.logging.LEVEL_VERBOSE: "${glyphs}/asterisk.svg",
    carb.logging.LEVEL_INFO: "${glyphs}/Info_Log.svg",
    carb.logging.LEVEL_WARN: "${glyphs}/Warning_Log.svg",
    carb.logging.LEVEL_ERROR: "${glyphs}/Error_Log.svg",
    carb.logging.LEVEL_FATAL: "${glyphs}/Error_Log.svg",
}

CONSOLE_WINDOW_STYLE = {
    "Toolbar.Frame": {"padding": 0, "margin_width": 0},
    "Toolbar.Button": {
        "stack_direction": ui.Direction.LEFT_TO_RIGHT,
        "background_color": 0,
        "padding": 2.5,
    },
    "Toolbar.Button:hovered": {
        "background_color": 0xFF373737,
    },
    "Toolbar.Button:checked": {
        "background_color": 0xFF373737,
    },
    "Toolbar.Button.Image": {
        "color": 0xFFCCCCCC,
    },
    "Toolbar.Button.Image::clear": {"image_url": "${glyphs}/Clear_Log.svg"},
    "Toolbar.Button.Image::open_log": {"image_url": "${glyphs}/Open_Log.svg"},
    "Toolbar.Button.Image::open_folder": {"image_url": "${glyphs}/Open_Folder.svg"},
    "Toolbar.Button.Image::verbose": {"image_url": "${glyphs}/asterisk.svg", "color": CL_LOG_DEFAULT},
    "Toolbar.Button.Image::verbose:checked": {"color": cl(0.72941, 0.72941, 0.72941, 1)},
    "Toolbar.Button.Image::info": {"image_url": "${glyphs}/Info_Log.svg", "color": CL_LOG_DEFAULT},
    "Toolbar.Button.Image::info:checked": {"color": CL_LOG_INFO},
    "Toolbar.Button.Label::warning": {"color": CL_LOG_DEFAULT},
    "Toolbar.Button.Label::warning:checked": {"color": CL_LOG_WARNING},
    "Toolbar.Button.Image::warning": {"image_url": "${glyphs}/Warning_Log.svg", "color": CL_LOG_DEFAULT},
    "Toolbar.Button.Image::warning:checked": {"color": CL_LOG_WARNING},
    "Toolbar.Button.Label::error": {"color": CL_LOG_ERROR},
    "Toolbar.Button.Image::error": {"image_url": "${glyphs}/Error_Log.svg", "color": CL_LOG_DEFAULT},
    "Toolbar.Button.Image::error:checked": {"color": cl('#F88A7D')},

    "Toolbar.SearchField": {"background_color": cl.shade(cl('#1F2124'))},
    "Toolbar.SearchField.hint": {"margin_width": 8, "color": cl.shade(cl('#6E6E6E'))},

    "LogView": {"background_color": cl.shade(cl('#1F2124')), "background_selected_color": 0xFF333333},
    "LogView:selected": {"background_color": 0xFF333333},

    "LogView.Item.Text": {"margin_height": 1},
    "LogView.Item.Text::verbose": {"color": CL_LOG_INFO},
    "LogView.Item.Text::info": {"color": CL_LOG_INFO},
    "LogView.Item.Text::warning": {"color": CL_LOG_WARNING},
    "LogView.Item.Text::error": {"color": CL_LOG_ERROR},
    "LogView.Item.Text::fatal": {"color": CL_LOG_FATAL},

    "CommandField.Hint": {"color": cl.shade(cl('#4A4A4A'))},
}