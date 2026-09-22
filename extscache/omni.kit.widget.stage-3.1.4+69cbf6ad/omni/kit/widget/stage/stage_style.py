__all__ = ["Styles"]

import omni.ui as ui

from .stage_icons import StageIcons as Icons


class Styles:

    ITEM_DARK = None
    ITEM_GRAY = None
    ITEM_HOVER = None
    ITEM_SEL = None
    ITEM_BG_SEL = None

    ICON_DARK = None

    STAGE_WIDGET = None

    @staticmethod
    def on_startup():
        # List Items
        Styles.ITEM_DARK = 0x7723211F
        Styles.ITEM_GRAY = 0xFF8A8777
        Styles.ITEM_HOVER = 0xFFBBBAAA
        Styles.ITEM_SEL = 0xFFDDDCCC
        Styles.ITEM_BG_SEL = 0x66888777

        Styles.STAGE_WIDGET = {
            "Button.Image::filter": {"image_url": Icons().get("filter"), "color": 0xFF8A8777},
            "Button.Image::options": {"image_url": Icons().get("options"), "color": 0xFF8A8777},
            "Button::filter": {"background_color": 0x0, "margin": 0},
            "Button::options": {"background_color": 0x0, "margin": 0},
            "Label::search": {"color": 0xFF808080, "margin_width": 4},
            "TreeView.ScrollingFrame": {"background_color": 0xFF23211F},
            "TreeView.Image:disabled": {"color": 0x60FFFFFF},
            "TreeView.Item": {"color": Styles.ITEM_GRAY},
            "TreeView.Item:disabled": {"color": 0x608A8777},
            "TreeView.Item:hovered": {"color": Styles.ITEM_HOVER},
            "TreeView.Item:selected": {"color": Styles.ITEM_SEL},
            "TreeView:selected": {"background_color": Styles.ITEM_BG_SEL},
            "TreeView": {
                "background_color": 0xFF23211F,
                "background_selected_color": 0x664F4D43,
                "secondary_color": 0xFF403B3B,
                "border_width": 1.5,
            },
            "TreeView:drop": {
                "background_color": ui.color.shade(ui.color("#34C7FF3B")),
                "background_selected_color": ui.color.shade(ui.color("#34C7FF3B")),
                "border_color": ui.color.shade(ui.color("#2B87AA")),
            },
            # Top of the column section (that has sorting options)
            "TreeView.Header": {"background_color": 0xFF343432, "color": 0xFFCCCCCC, "font_size": 12},
            "TreeView.Header::drop_down_background": {"background_color": 0xE0808080},
            "TreeView.Header::drop_down_button": {"background_color": ui.color.white},
            "TreeView.Header::drop_down_hovered_area": {"background_color": ui.color.transparent},
            "TreeView.Header::hovering": {"background_color": 0x0, "border_radius": 1.5},
            "TreeView.Header::hovering:hovered": {
                "background_color": ui.color.shade(ui.color("#34C7FF3B")),
                "border_width": 1.5,
                "border_color": ui.color.shade(ui.color("#2B87AA"))
            }
        }
