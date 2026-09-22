# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityWindow"]

from .activity_chart import ActivityChart
from .style import activity_window_style
import omni.ui as ui

LABEL_WIDTH = 120
SPACING = 4


class ActivityWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, model, delegate=None, activity_menu=None, **kwargs):
        super().__init__(title, raster_policy=ui.RasterPolicy.NEVER, **kwargs)
        self.__chart = None

        # Apply the style to all the widgets of this window
        self.frame.style = activity_window_style

        self.deferred_dock_in("Content", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)

        # Set the function that is called to build widgets when the window is
        # visible
        self.frame.set_build_fn(lambda: self.__build(model, activity_menu))

    def destroy(self):
        if self.__chart:
            self.__chart.destroy()

        # It will destroy all the children
        super().destroy()

    def _menu_new(self, model=None):
        if self.__chart:
            self.__chart.new(model)

    def get_data(self):
        if self.__chart:
            return self.__chart.save_for_report()
        return None

    def __build(self, model, activity_menu):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        self.__chart = ActivityChart(model, activity_menu)
