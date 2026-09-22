"""Manages the camera settings integration into the viewport menu bar"""

from .abstract_camera_widget_delegate import AbstractCameraButtonDelegate, AbstractCameraMenuItemDelegate, AbstractWidgetDelegate
from .extension import get_instance, ViewportCameraMenuBarExtension
from .menu_item import SingleCameraMenuItemBase


__all__ = ["AbstractCameraButtonDelegate", "AbstractCameraMenuItemDelegate", "AbstractWidgetDelegate", "get_instance", "ViewportCameraMenuBarExtension", "SingleCameraMenuItemBase"]