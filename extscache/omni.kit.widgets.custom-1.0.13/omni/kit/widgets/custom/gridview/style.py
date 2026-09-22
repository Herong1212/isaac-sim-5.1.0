from omni.kit.widgets.custom import COLORS, DarkColors, LightColors

LIGHT_STYLE = {
    "GridView.Frame": {
        "background_color": COLORS.TRANSPARENT,
        "secondary_color": COLORS.TRANSPARENT,
        "border_radius": 0,
        "scrollbar_size": 1,
    },
    "GridView.Grid": {"background_color": LightColors.Background},
    "GridView.Item": {"background_color": LightColors.Background, "color": LightColors.Text},
}

DARK_STYLE = {
    "GridView.Frame": {
        "background_color": COLORS.TRANSPARENT,
        "secondary_color": COLORS.TRANSPARENT,
        "border_radius": 0,
        "scrollbar_size": 1,
    },
    "GridView.Grid": {"background_color": DarkColors.Background},
    "GridView.Item": {"background_color": DarkColors.Background, "color": DarkColors.Text},
}

UI_STYLES = {"NvidiaLight": LIGHT_STYLE, "NvidiaDark": DARK_STYLE}
