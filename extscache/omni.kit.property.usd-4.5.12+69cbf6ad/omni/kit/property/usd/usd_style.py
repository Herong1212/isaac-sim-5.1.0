__all__ = []


class Styles:
    """
    A class to represent the styles.
    """

    LIVE_STATE_PAYREF = None
    LIVE_GREEN = None
    LIVE_GREEN_DARKER = None
    LIVE_SEL = None
    LIVE_TOOL_TIP = None
    DEFAULT_BTN = None
    REMOVE_BTN = None
    BROWSE_BTN = None
    FIND_BTN = None
    SESSIONS_MENU = None
    BACK_DROP = None
    RELOAD_ORANGE = None
    RELOAD_SEL = None
    REFERENCE_ERROR = 0xFF6F72FF

    @staticmethod
    def on_startup():
        """
        Initializes the styles.
        """

        from omni.ui import color as cl

        from .widgets import ICON_PATH

        c_otd = cl("#eb9d00")
        c_otdh = cl("#ffaa00")
        c_live = cl("#76b800")
        c_liveh = cl("#76b900")
        c_lived = cl("#76B900")

        Styles.LIVE_TOOL_TIP = {"background_color": 0xEE222222, "color": 0x33333333}

        Styles.RELOAD_ORANGE = {"color": c_otd, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.RELOAD_SEL = {"color": c_otdh, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.LIVE_GREEN = {"color": c_live, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.LIVE_SEL = {"color": c_liveh, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.LIVE_GREEN_DARKER = {"color": c_lived, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.BROWSE_BTN = {
            "image_url": str(ICON_PATH.joinpath("small_folder.png")),
            "padding": 1,
            "margin": 0,
            "Button:Image:disabled": {"color": 0xFF333333},
            "Button.Image::browse": {"color": 0xFFAAAAAA},
            "Button.Image::browse:hovered": {"color": 0xFFFFFFFF},
            "Button:hovered": {"background_color": 0x00000000},
        }

        Styles.FIND_BTN = {
            "image_url": str(ICON_PATH.joinpath("find.png")),
            "padding": 1,
            "margin": 0,
            "Button.Image::find:disabled": {"color": 0xFF333333},
            "Button.Image::find": {"color": 0xFF888888},
            "Button.Image::find:hovered": {"color": 0xFFFFFFFF},
            "Button:hovered": {"background_color": 0x00000000},
        }

        Styles.FIND_BTN_MISSING = {
            "image_url": str(ICON_PATH.joinpath("find.png")),
            "padding": 1,
            "margin": 0,
            "Button.Image::find:disabled": {"color": 0xFF666666},
            "Button.Image::find": {"color": 0xFF666666},
        }

        Styles.LIVE_STATE_PAYREF = {
            "Image::lightning": {"image_url": str(ICON_PATH.joinpath("lightning.svg")), "color": 0xFFAAAAAA},
            "Image::lightning:hovered": {"color": 0xFFEEEEEE},
            "Image::lightning-live": {"image_url": str(ICON_PATH.joinpath("lightning.svg")), "color": 0xFF00B86B},
            "Image::lightning-live:hovered": {
                "image_url": str(ICON_PATH.joinpath("lightning.svg")),
                "color": 0xFF00F86E,
            },
            "Label::label-live": {"color": 0xFF00B86B},
        }

        Styles.SESSIONS_MENU = {
            "Button:hovered": {"color": 0x00000000},
        }

        Styles.DEFAULT_BTN = {
            "Image": {"image_url": str(ICON_PATH.joinpath("Default value.svg"))},
            "Image::changed": {"image_url": str(ICON_PATH.joinpath("Changed value.svg"))},
        }

        Styles.REMOVE_BTN = {
            "image_url": str(ICON_PATH.joinpath("remove.svg")),
            "margin": 0,
            "padding": 0,
            "Button:hovered": {"color": 0xEEEEEEEE},
            "Button:disabled": {"color": 0x11EEEEEE},
            "Rectangle": {"background_color": 0xEE335533},
        }

        Styles.BACK_DROP = {
            "Rectangle::backdrop-live": {"background_color": 0xEE335533},
        }
