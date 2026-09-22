class TimelineWidgetStyle:
    FONT_SIZE = 14

    @staticmethod
    def get_style():
        style = {
            "TimelineWidget.MainFrame": {"margin_width": 0},
            "TimelineWidget.BackgroundRectangle": {"background_color": 0xFF2A2A27, "margin_width": 0},
            "TimelineContent.BackgroundRectangle": {"background_color": 0xFF222222, "margin_width": 0},
            "TimelineWidget.HorizontalRectangle": {"background_color": 0xFF31312F, "margin_width": 0},
            "TimelineWidget.Tick.Line": {"color": 0x44BCB9A5},
            "TimelineWidget.Tick.FrameNumberLabel": {"color": 0xAABCB9A5, "margin": 0},
            "TimelineWidget.Grid.Line": {"color": 0x11BCB9A5, "width": 2},
            "TimelineWidget.FrameNumberLabel": {
                "color": 0xFF2A2825,
                "margin_width": 0,
                "margin_height": 0,
                "font_size": TimelineWidgetStyle.FONT_SIZE,
            },
            "TimelineWidget.Scrubber": {
                "background_color": 0xFFFF7E09,
                "border_width": 1,
                "border_color": 0xFFFF7E09,
            },
            "TimelineWidget.Scrubber.FrameShadowRectangle": {
                "background_color": 0x44AA8820,
            },
            "TimelineWidget.Scrubber.FrameLine": {"border_width": 2, "color": 0xFFFF7E09},
            "RangeWidget.ViewFrameInput": {"background_color": 0xFF292929, "border_radius": 0},
            "RangeWidget.RangeSliderBackground": {"background_color": 0x66292929, "border_radius": 2},
        }
        return style
