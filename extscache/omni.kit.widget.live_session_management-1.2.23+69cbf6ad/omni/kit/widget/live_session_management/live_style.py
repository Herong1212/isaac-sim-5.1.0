# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["Styles"]


class Styles:

    RELOAD_BTN = None
    RELOAD_AUTO = None
    RELOAD_OTD = None
    LIVE_TOOL_TIP = None

    @staticmethod
    def on_startup():
        # from .layer_icons import LayerIcons as li
        from omni.ui import color as cl

        c_otd = cl("#eb9d00")
        c_otdh = cl("#ffaa00")
        c_live = cl("#76B900")
        c_liveh = cl("#9bf400")
        c_lived = cl("#76B900")
        c_auto = cl("#34C7FF")
        c_autoh = cl("#82dcff")
        c_white = cl("#ffffff")
        c_rel = cl("#888888")
        c_relh = cl("#BBBBBB")
        c_disabled = cl("#555555")

        Styles.LIVE_TOOL_TIP = {"background_color": 0xEE222222, "color": 0x33333333}

        Styles.LIVE_GREEN = {"color": c_live, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.LIVE_SEL = {"color": c_liveh, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.LIVE_GREEN_DARKER = {"color": c_lived, "Tooltip": Styles.LIVE_TOOL_TIP}

        Styles.RELOAD_BTN = {
            "color": c_rel,
            ":hovered": {"color": c_relh},
            ":pressed": {"color": c_white},
            ":disabled": {"color": c_disabled},
        }

        Styles.RELOAD_AUTO = {
            "color": c_auto, "Tooltip": Styles.LIVE_TOOL_TIP,
            ":hovered": {"color": c_autoh},
            ":pressed": {"color": c_white},
            ":disabled": {"color": c_disabled},
        }

        Styles.RELOAD_OTD = {
            "color": c_otd, "Tooltip": Styles.LIVE_TOOL_TIP,
            ":hovered": {"color": c_otdh},
            ":pressed": {"color": c_white},
            ":disabled": {"color": c_disabled},
        }
