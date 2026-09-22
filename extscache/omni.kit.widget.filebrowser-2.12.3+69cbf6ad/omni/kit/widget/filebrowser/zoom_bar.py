# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
UI Widget to change the scale of items inside :obj:`FileBrowserGridView`.
"""
__all__ = ["ZoomBar"]
import carb.settings
import omni.ui as ui
from .style import UI_STYLES, ICON_PATH

# key is scale level and value is the actual scale value
SCALE_MAP = {0: 0.25, 1: 0.5, 2: 0.75, 3: 1, 4: 1.5, 5: 2.0}


class ZoomBar:
    """
    Widget to control the scale of items inside :obj:`FileBrowserGridView`.
    """
    def __init__(self, **kwargs):
        self._show_grid_view = kwargs.get("show_grid_view", True)
        self._grid_view_scale = kwargs.get("grid_view_scale", 2)
        self._on_toggle_grid_view_fn = kwargs.get("on_toggle_grid_view_fn", None)
        self._on_scale_grid_view_fn = kwargs.get("on_scale_grid_view_fn", None)

        settings = carb.settings.get_settings()
        theme = settings.get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"

        self._theme = theme
        self._style = UI_STYLES[theme]
        self._slider = None
        self._layout_button = None
        self._build_ui()

        # Notify any potential listeners registered through the "_on_toggle_grid_view_fn" argument that the view has
        # been enabled in the initial state depicted by the resolved `self._show_grid_view` property:
        self._toggle_grid_view(self._show_grid_view)

    def destroy(self):
        """ Destructor """
        self._on_toggle_grid_view_fn = None
        self._on_scale_grid_view_fn = None
        self._slider = None
        self._layout_button = None

    def _build_ui(self):
        with ui.HStack(height=0, style=self._style):
            ui.Spacer()
            with ui.ZStack(width=0, style=self._style, content_clipping=True):
                ui.Rectangle(height=20, style_type_name_override="ZoomBar")
                with ui.HStack():
                    ui.Spacer(width=6)
                    self._slider = ui.IntSlider(min=0, max=5, width=150, style=self._style["ZoomBar.Slider"])
                    self._slider.model.add_value_changed_fn(self._scale_grid_view)
                    self._layout_button = ui.Button(
                        image_url=self._get_layout_icon(not self._show_grid_view),
                        width=16,
                        style_type_name_override="ZoomBar.Button",
                        clicked_fn=lambda: self._toggle_grid_view(not self._show_grid_view),
                    )
                    ui.Spacer(width=6)
            ui.Spacer(width=16)

    def _get_layout_icon(self, grid_view: bool) -> str:
        if grid_view:
            return f"{ICON_PATH}/{self._theme}/thumbnail.svg"
        else:
            return f"{ICON_PATH}/{self._theme}/list.svg"

    def _scale_grid_view(self, model: ui.SimpleIntModel):
        scale_level = model.get_value_as_int()
        scale = SCALE_MAP.get(scale_level, 2)
        if self._on_scale_grid_view_fn:
            self._on_scale_grid_view_fn(scale)

        # If currently displaying the "Grid" View, remember the scale level so it can be rehabilitated later when
        # toggling back from the "List" View, for which the scale level is set to `0`:
        if self._show_grid_view:
            self._grid_view_scale = scale_level

    def _toggle_grid_view(self, show_grid_view: bool):
        self._layout_button.image_url = self._get_layout_icon(not show_grid_view)
        self._show_grid_view = show_grid_view

        # If showing the "Grid" View, restore the scale level previously set. Showing the "List" View otherwise sets the
        # scale level to `0`:
        if show_grid_view:
            self._slider.model.set_value(self._grid_view_scale)
        else:
            self._slider.model.set_value(0)

        if self._on_toggle_grid_view_fn:
            self._on_toggle_grid_view_fn(show_grid_view)
