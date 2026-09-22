from omni.ui import color as cl


cl.datetime_bg = cl('#242424')
cl.datetime_fg = cl('#545454')
cl.datetime_fg2 = cl('#848484')
cl.blue_light = cl('#3c63d3')

default_datetime_window_style = {
    "Window": {"background_color": cl.transparent},
    "Button": {"margin_height": 0.5, "margin_width": 0.5, },
    "Button::day:selected": {"background_color": cl.datetime_fg},
    "ComboBox::year": {"background_color": cl.datetime_bg},
    "ComboBox::timezone": {"secondary_color": cl.datetime_bg},
    "Rectangle::blank": {"background_color": cl.transparent},
    "Label::number": {"font_size": 32},
    "Label::morning": {"font_size": 14},
    "Label::week": {"font_size": 16},
    "Triangle::spinner": {"background_color": cl.datetime_fg2, "border_width": 0},
    "Triangle::spinner:hovered": {"background_color": cl.datetime_fg},
    "Triangle::spinner:pressed": {"background_color": cl.datetime_fg},
    "Circle::clock": {"background_color": cl.datetime_fg2, "border_width": 0},
    "Circle::day": {
        "background_color": cl.transparent,
        "border_color": cl.transparent,
        "border_width": 2,
        "margin": 2
    },
    "Circle::day:hovered": {"border_color": cl.blue_light},
}

select_circle_style = {"border_color": cl.blue_light}
unselect_circle_style = {"border_color": cl.transparent}