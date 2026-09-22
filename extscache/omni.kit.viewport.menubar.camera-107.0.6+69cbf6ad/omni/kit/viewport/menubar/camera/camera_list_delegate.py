__all__ = ["CameraListDelegate"]

from typing import Optional

import carb
from omni.kit.viewport.menubar.core import IconMenuDelegate, USDAttributeModel
import omni.ui as ui
from pxr import Sdf

from .camera_widget_delegate_manager import CameraWidgetDelegateManager


class CameraListDelegate(IconMenuDelegate):
    def __init__(self, viewport_api, widget_delegate_manager: CameraWidgetDelegateManager):
        self.__model: Optional[USDAttributeModel] = None
        self.__sub = None
        self.__viewport_api = viewport_api
        self.__selected_camera_path = Sdf.Path.emptyPath
        self.__widget_delegate_manager = widget_delegate_manager
        super().__init__("UnlockedCamera", text=True, build_custom_widgets=self.__build_custom_widgets)

    def destroy(self):
        self.__sub = None
        if self.__widget_delegate_manager:
            self.__widget_delegate_manager.on_parent_destroyed(id(self), True)
            self.__widget_delegate_manager = None
        super().destroy()

    def __build_custom_widgets(self, item: ui.MenuItem):
        if not self.__widget_delegate_manager:
            return

        try:
            self.__widget_delegate_manager.build_widgets(
                id(self), self.__viewport_api, self.__selected_camera_path, True
            )
        except Exception as e:  # noqa: PLW0718
            carb.log_error(f"Failed to build widget: {str(e)}")

    def _build_icon(self):
        # with vstack to not trigger menu if click on icon
        if self._text:
            with ui.VStack(content_clipping=True, width=0):
                icon = super()._build_icon()
                icon.set_mouse_pressed_fn(lambda x, y, b, a: self.__toggle_lock())
        else:
            icon = super()._build_icon()
            icon.name = self.__get_icon_name()
        return icon

    @property
    def camera_path(self) -> Sdf.Path:
        return self.__selected_camera_path

    @camera_path.setter
    def camera_path(self, path):
        self.__selected_camera_path = path
        if self.__widget_delegate_manager:
            self.__widget_delegate_manager.on_camera_path_changed(id(self), path, True)

    @property
    def model(self) -> USDAttributeModel:
        return self.__model

    @model.setter
    def model(self, new_model: USDAttributeModel) -> None:
        self.__model = new_model

        icon_name = self.__get_icon_name()
        if self.icon:
            self.icon.name = icon_name
        else:
            self._name = icon_name

        if self.__sub:
            self.__sub = None
        if self.__model:
            self.__sub = self.__model.subscribe_value_changed_fn(self._on_lock_changed)

    def __get_icon_name(self):
        if not self.__model:
            return "UnlockedCameraWithoutHovered"

        hov_text = "" if bool(self._text) else "WithoutHovered"
        lock_text = "LockedCamera" if self.__model.as_bool else "UnlockedCamera"
        return f"{lock_text}{hov_text}"

    def _on_lock_changed(self, model: ui.AbstractValueModel) -> None:
        icon_name = self.__get_icon_name()
        if self.icon:
            self.icon.name = icon_name
        else:
            self._name = icon_name

    def __toggle_lock(self):
        if self.__model:
            self.__model.set_value(not self.__model.as_bool)
