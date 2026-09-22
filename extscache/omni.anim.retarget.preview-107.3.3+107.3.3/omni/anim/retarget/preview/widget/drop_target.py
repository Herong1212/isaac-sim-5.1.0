# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui
from omni.ui import color as cl

DEFAULT_RECT_STYLE = {"background_color": cl("#77777788"), "border_width": 2, "border_color": cl("#AAAAAAFF")}
DISABLED_RECT_STYLE = {"background_color": cl("#33333388"), "border_width": 1, "border_color": cl("#33333388")}
ACTIVE_RECT_STYLE = {"background_color": cl.shade(cl("#34C7FF3B")), "border_width": 2, "border_color": cl.shade(cl("#34C7FF"))}

DEFAULT_LABEL_STYLE = {"font_size": 14}
DISABLED_LABEL_STYLE = {"font_size": 14, "color": cl("#55555588")}
ACTIVE_LABEL_STYLE = {"font_size": 14}


class DropTarget:
    def __init__(self, label, icon=None, height=ui.Percent(20), width=ui.Percent(90), drop_fn=None, valid_fn=None):
        self._rectangle = None
        self._label = None

        self._label_text = label
        self._icon = icon

        self._height = height
        self._width = width

        self._drop_fn = drop_fn
        self._valid_fn = valid_fn

        self._build()

    def destroy(self):
        if self._rectangle:
            self._rectangle.destroy()
            self._rectangle = None
        if self._label:
            self._label.destroy()
            self._label = None
        self._drop_fn = None
        self._valid_fn = None

    def _build(self):
        with ui.HStack(height=self._height):
            ui.Spacer()
            with ui.ZStack(width=self._width):
                self._rectangle = ui.Rectangle(style=DEFAULT_RECT_STYLE)
                with ui.VStack():
                    ui.Spacer()
                    if self._icon:
                        ui.Image(self._icon, alignment=ui.Alignment.CENTER)
                    self._label = ui.Label(self._label_text, alignment=ui.Alignment.CENTER, style=DEFAULT_LABEL_STYLE)
                    ui.Spacer()
            ui.Spacer()

    def drop(self, url):
        if self._drop_fn is not None:
            self._drop_fn(url)

    def is_valid(self, url):
        if self._valid_fn is not None:
            return self._valid_fn(url)

        # If there's no valid check, everything is valid!
        return True

    def update_valid(self, url):
        if self.is_valid(url):
            if self._rectangle:
                self._rectangle.style = DEFAULT_RECT_STYLE
            if self._label:
                self._label.style = DEFAULT_LABEL_STYLE
        else:
            if self._rectangle:
                self._rectangle.style = DISABLED_RECT_STYLE
            if self._label:
                self._label.style = DISABLED_LABEL_STYLE

    def set_active(self, active):
        if active:
            if self._rectangle:
                self._rectangle.style = ACTIVE_RECT_STYLE
            if self._label:
                self._label.style = ACTIVE_LABEL_STYLE
        else:
            if self._rectangle:
                self._rectangle.style = DEFAULT_RECT_STYLE
            if self._label:
                self._label.style = DEFAULT_LABEL_STYLE

    def contains_position(self, x, y):
        if not self._rectangle:
            return False

        x_min = self._rectangle.screen_position_x
        x_max = self._rectangle.screen_position_x + self._rectangle.computed_content_width

        y_min = self._rectangle.screen_position_y
        y_max = self._rectangle.screen_position_y + self._rectangle.computed_content_height

        result = (x >= x_min and x <= x_max) and (y >= y_min and y <= y_max)
        return result
