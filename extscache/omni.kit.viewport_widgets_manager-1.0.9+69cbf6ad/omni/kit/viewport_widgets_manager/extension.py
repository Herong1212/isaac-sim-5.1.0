# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb
import omni.ext
from typing import Union
from pxr import Sdf
from .manager import ViewportWidgetsManager, WidgetAlignment
from .widget_provider import WidgetProvider


_global_instance = None


class ViewportWidgetsManagerExtension(omni.ext.IExt):
    def on_startup(self):
        global _global_instance
        _global_instance = self
        self._widgets_manager = ViewportWidgetsManager()
        self._widgets_manager.start()

    def on_shutdown(self):
        global _global_instance
        _global_instance = None
        self._widgets_manager.stop()

    @staticmethod
    def _get_instance():
        global _global_instance
        return _global_instance
    
    def add_widget(self, prim_path: Sdf.Path, widget: WidgetProvider, alignment=WidgetAlignment.CENTER):
        return self._widgets_manager.add_widget(prim_path, widget, alignment)
    
    def remove_widget(self, widget_id):
        self._widgets_manager.remove_widget(widget_id)
    
    
def add_widget(prim_path: Union[str, Sdf.Path], widget: WidgetProvider, alignment=WidgetAlignment.CENTER):
    """Add widget to viewport, which is positioned to the screen pos
    of prim on the viewport.
    
    REMINDER: Currently, it's possible that a prim
    may includes multiple widgets, and they will be overlapped to each
    other.
    
    Args:
        prim_path (Union[str, Sdf.Path]): The prim you want to add the widget to.
        widget (WidgetProvider): The widget provider that you can override
        to customize the UI layout.
        alignment: The anchor point of the widget. By default, it will be
        the calculated by the position of prim.
    
    Returns:
        widget id, which you can use it for widget remove. Or None if prim
        cannot be found.
    """

    instance = ViewportWidgetsManagerExtension._get_instance()
    if not instance:
        carb.log_warn("Extension omni.kit.viewport_widgets_manager is not enabled.")
        return None
    
    return ViewportWidgetsManagerExtension._get_instance().add_widget(Sdf.Path(prim_path), widget, alignment)
        

def remove_widget(widget_id):
    """
    Remove widget with id.

    Args:
        widget_id: The widget id returned with add_widget.
    """

    instance = ViewportWidgetsManagerExtension._get_instance()
    if not instance:
        carb.log_warn("Extension omni.kit.viewport_widgets_manager is not enabled.")
        return None
    
    return ViewportWidgetsManagerExtension._get_instance().remove_widget(widget_id)
    
