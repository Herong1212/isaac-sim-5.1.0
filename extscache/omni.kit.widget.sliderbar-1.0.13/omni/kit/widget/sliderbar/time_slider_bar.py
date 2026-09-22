from .slider_bar import SliderBar


class TimeSliderBar(SliderBar):
    def _get_display_value(self, value: float) -> str:
        section = " PM"
        if value < 1.0:
            section = " AM"
            hour = 12
        elif value < 12.0:
            hour = int(value)
            section = " AM"
        elif value < 13.0:
            hour = int(value)
        else:
            hour = int(value) - 12

        minute = int((value - int(value)) * 60)
        return "{:2d}:{:02d} {}".format(hour, minute, section)
