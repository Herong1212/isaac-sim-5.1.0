from pathlib import Path

import omni.kit
import omni.ui as ui
from omni.kit.property.usd.widgets import ICON_PATH


REMOVE_BUTTON_STYLE = style = {"image_url": str(Path(ICON_PATH).joinpath("remove.svg")), "margin": 0, "padding": 0}
EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
EXT_ICON_PATH = f"{EXT_PATH}/data/icons"

COLORS = {
    "WHITE": ui.color("#DDDDDD"),
    "GREY": ui.color("#888888"),
    "CYAN": ui.color("#33FFF3"),
    "PINK": ui.color("#FC63FF"),
    "PURPLE": ui.color("#637CFF"),
    "GREEN": ui.color("#61A729"),
    "BLUE": ui.color("#4f7da0"),
}

SKEL_MODE_BIND_STYLE = {
    "image_url": str(Path(EXT_ICON_PATH).joinpath("state_bind.png")),
    # "alignment": ui.Alignment.CENTER,
    # "debug_color": ui.color(255, 0, 0, 100)
}

SKEL_MODE_REST_STYLE = {
    "image_url": str(Path(EXT_ICON_PATH).joinpath("state_rest.png"))
}

SKEL_MODE_RETARGET_STYLE = {
    "image_url": str(Path(EXT_ICON_PATH).joinpath("state_retarget.png")),
}

SKEL_MODE_ANIM_STYLE = {
    "image_url": str(Path(EXT_ICON_PATH).joinpath("state_animation.png")),
}

RADIO_STYLE = {
    "": {
        "stack_direction": ui.Direction.LEFT_TO_RIGHT,
        "background_color": ui.color.transparent,
        "color": COLORS["GREY"],
        "alignment": ui.Alignment.LEFT_CENTER,
        "image_url": str(Path(EXT_ICON_PATH).joinpath("radio_off.svg"))
    },
    ":Text": {
        "font_size": 10,
        "alignment": ui.Alignment.LEFT_CENTER
    },
    ":checked": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("radio_on.svg"))
    },
}

SAVE_BTN_STYLE = {
    "Button": {
        "background_color": ui.color.transparent,
    },
    "Button.Image": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("save.svg"))
    },
    "Button.Image:disabled": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("save_grey.svg"))
    },
    "Button:hovered": {
        "background_color": ui.color.transparent,
    }
}

COPY_BTN_STYLE = {
    "Button": {
        "background_color": ui.color.transparent,
    },
    "Button.Image": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("copy.svg"))
    },
    "Button.Image:disabled": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("copy_grey.svg"))
    },
    "Button:hovered": {
        "background_color": ui.color.transparent,
    }
}

PASTE_BTN_STYLE = {
    "Button": {
        "background_color": ui.color.transparent,
    },
    "Button.Image": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("paste.svg"))
    },
    "Button.Image:disabled": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("paste_grey.svg"))
    },
    "Button:hovered": {
        "background_color": ui.color.transparent,
    }
}

RESET_BTN_STYLE = {
    "Button": {
        "background_color": ui.color.transparent,
    },
    "Button.Image": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("reset.svg"))
    },
    "Button.Image:disabled": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("reset_grey.svg"))
    },
    "Button:hovered": {
        "background_color": ui.color.transparent,
    }
}

REVERT_BTN_STYLE = {
    "Button": {
        "background_color": ui.color.transparent,
    },
    "Button.Image": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("trash.svg"))
    },
    "Button.Image:disabled": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("trash_grey.svg"))
    },
    "Button:hovered": {
        "background_color": ui.color.transparent,
    }
}

BROWSE_BTN_STYLE = {
    "Button": {
        "background_color": ui.color.transparent,
    },
    "Button.Image": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("folder.svg"))
    },
    "Button.Image:disabled": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("folder_grey.svg"))
    },
    "Button:hovered": {
        "background_color": ui.color.transparent,
    }
}

LOCATE_BTN_STYLE = {
    "Button": {
        "background_color": ui.color.transparent,
    },
    "Button.Image": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("locate.svg"))
    },
    "Button.Image:disabled": {
        "image_url": str(Path(EXT_ICON_PATH).joinpath("locate_grey.svg"))
    },
    "Button:hovered": {
        "background_color": ui.color.transparent,
    }
}

ANIM_FIELD_STYLE = {
    "": {"color": ui.color.white},
    ":disabled": {"color": ui.color.grey}
}
