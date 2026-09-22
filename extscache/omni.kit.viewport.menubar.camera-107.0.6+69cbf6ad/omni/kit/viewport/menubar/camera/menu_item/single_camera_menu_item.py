import abc
import weakref
from typing import TYPE_CHECKING, Callable, Optional

import carb
import omni.ui as ui
from omni.kit.viewport.menubar.core import LabelMenuDelegate, ViewportMenuDelegate
from pxr import Sdf

from ..camera_widget_delegate_manager import CameraWidgetDelegateManager
from ..utils import get_camera_display

if TYPE_CHECKING:
    from omni.kit.widget.viewport.api import ViewportAPI


class SingleCameraMenuItemBase(ui.MenuItem):
    """
    A base class for creating custom single camera menu items.
    """

    def __init__(
        self,
        camera_path: Sdf.Path,
        viewport_api: "ViewportAPI",
        lock_model: ui.AbstractValueModel,
        root: ui.Menu,
        triggered_fn: Callable,
        widget_delegate_manager: CameraWidgetDelegateManager,
        hotkey_text: str = "",
        show_hotkey_placeholder: bool = False,
    ):
        """
        A base class for creating custom single camera menu items.

        Args:
            camera_path (Sdf.Path): Path to camera.
            viewport_api (ViewportAPI): Viewport API.
            lock_model (ui.AbstractValueModel): Value model to indicate if camera locked.
            root (ui.Menu): Root menu.
            triggered_fn (Callable): Callback when men item clicked.
            widget_delegate_manager (CameraWidgetDelegateManager): Manager to custom button/menu item delegates.

        Keyword Args:
            hotkey_text (str): Hotkey text. By default "" means no hotkey text displayed.
            show_hotkey_placeholder (bool): If show placeholder for hotkey in menu item. Default False.

        """
        self._lock_model = lock_model
        self.__camera_path = camera_path
        self.__viewport_api = viewport_api
        self.__lock_button: Optional[ui.Button] = None
        self.__lock_model_sub = None  # noqa: PLW0238
        self.__options_button = None
        self.__widget_delegate_manager = widget_delegate_manager

        def _build_menuitem_widgets(_self=weakref.ref(self)):
            if (self := _self()) is None:
                return
            return self._build_menuitem_widgets()

        super().__init__(
            get_camera_display(camera_path, viewport_api.stage),
            checkable=True,
            checked=viewport_api.camera_path == camera_path,
            hide_on_click=False,
            triggered_fn=triggered_fn,
            delegate=ViewportMenuDelegate(
                force_checked=False,
                build_custom_widgets=lambda delegate, item: _build_menuitem_widgets(),
                show_hotkey_placeholder=show_hotkey_placeholder,
            ),
            hotkey_text=hotkey_text,
        )

    @property
    def camera_path(self) -> Sdf.Path:
        """Path to camera"""
        return self.__camera_path

    @property
    def viewport_api(self) -> "ViewportAPI":
        """Viewport API"""
        return self.__viewport_api

    def destroy(self):
        """Removes all the callbacks and circular references."""
        if self.__widget_delegate_manager:
            self.__widget_delegate_manager.on_parent_destroyed(id(self), False)
            self.__widget_delegate_manager = None
        self.__options_button = None
        super().destroy()
        self.__lock_model_sub = None  # noqa: PLW0238

    def __build_custom_widgets(self):
        if not self.__widget_delegate_manager:
            return

        try:
            self.__widget_delegate_manager.build_widgets(id(self), self.__viewport_api, self.__camera_path, False)
        except Exception as e:  # noqa: PLW0718
            carb.log_error(f"Failed to build widget: {str(e)}")

    def _build_menuitem_widgets(self):
        """Build additional buttons in the camera menu item"""
        ui.Spacer(width=10)

        def _option_clicked(_self=weakref.ref(self)):
            if (self := _self()) is None:
                return
            self._option_clicked()

        with ui.VStack(content_clipping=1, width=0):
            # Button to select camera
            self.__options_button = ui.Button(
                style_type_name_override="Menu.Item.Button",
                name="OptionBox",
                width=16,
                height=16,
                image_width=16,
                image_height=16,
                visible=self.checked,
                clicked_fn=_option_clicked,
            )
        if self._lock_model:

            def _toggle_camera_lock(_self=weakref.ref(self)):
                if (self := _self()) is None:
                    return
                self.__toggle_camera_lock()

            # Button to toggle lock status
            with ui.VStack(content_clipping=1, width=0):
                self.__lock_button = ui.Button(
                    style_type_name_override="Menu.Item.Button",
                    name=self.__get_lock_button_name(),
                    width=16,
                    height=16,
                    image_width=16,
                    image_height=16,
                    clicked_fn=_toggle_camera_lock,
                )

            def _on_lock_changed(model: ui.AbstractValueModel, _self=weakref.ref(self)) -> None:
                if (self := _self()) is None:
                    return
                self._on_lock_changed(model)

            self.__lock_model_sub = self._lock_model.subscribe_value_changed_fn(_on_lock_changed)  # noqa: PLW0238

        self.__build_custom_widgets()

    @abc.abstractmethod
    def _option_clicked(self):
        """Function to implement when the option is clicked. Used by RTX Remix"""
        return

    def __toggle_camera_lock(self):
        self._lock_model.set_value(not self._lock_model.as_bool)
        self.__lock_button.name = self.__get_lock_button_name()

    def _on_lock_changed(self, model: ui.AbstractValueModel) -> None:
        self.__lock_button.name = self.__get_lock_button_name()

    def __get_lock_button_name(self):
        return "CameraLocked" if self._lock_model.as_bool else "CameraUnlocked"

    def set_checked(self, checked: bool) -> None:
        """Set menu state to be checked"""
        self.checked = checked  # noqa: PLW0201
        self.delegate.checked = checked

        # Only show options button when it is current camera
        self.__options_button.visible = checked


class SingleCameraMenuItem(SingleCameraMenuItemBase):
    """
    A single menu item represent a single camera in the camera list
    """

    def _option_clicked(self):
        self.viewport_api.usd_context.get_selection().set_selected_prim_paths([self.camera_path.pathString], True)


class NoCameraMenuItem(ui.MenuItem):
    """
    A single menu item represent a no camera in the camera list
    """

    def __init__(self):
        super().__init__(
            "No camera",
            hide_on_click=False,
            delegate=LabelMenuDelegate(enabled=False, width=120, alignment=ui.Alignment.CENTER),
        )
