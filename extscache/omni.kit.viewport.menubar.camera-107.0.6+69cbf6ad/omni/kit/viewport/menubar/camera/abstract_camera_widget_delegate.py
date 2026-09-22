__all__ = ["AbstractCameraButtonDelegate", "AbstractCameraMenuItemDelegate", "AbstractWidgetDelegate"]

import abc
from typing import Optional, TYPE_CHECKING
import weakref

import omni.ui as ui
from pxr import Sdf

if TYPE_CHECKING:
    from omni.kit.widget.viewport.api import ViewportAPI


class AbstractWidgetDelegate(abc.ABC):
    """
    A base class for creating custom widgets in camera button and camera menu item.
    """

    @abc.abstractmethod
    def build_widget(self, parent_id: int, viewport_api: "ViewportAPI", camera_path: Sdf.Path) -> Optional[ui.Widget]:
        """
        Builds widget. This must be overridden to provide the layout.

        Args:
            parent_id (int): It's unique id of the camera item, with which you can use to manage the camera widget.
            viewport_api (ViewportAPI): Viewport interface.
            camera_path (Sdf.Path): The camera path to build widget for.
        """
        return

    @abc.abstractmethod
    def on_parent_destroyed(self, parent_id: int) -> None:
        """
        Called before the destroy of the parent widget to release the bound resources specific to the parent.

        Args:
            parent_id (int): It's unique id of the camera item, with which you can use to manage the camera widget.
        """
        return

    @abc.abstractmethod
    def on_camera_path_changed(self, parent_id: int, camera_path: Sdf.Path):
        """
        Callback when the tracked camera has changed.

        Args:
            parent_id (int): It's unique id of the camera item, with which you can use to manage the camera widget.
            camera_path (Sdf.Path): The new camera path.
        """
        return

    def destroy(self):
        """Release resources."""
        return

    @property
    def order(self) -> int:
        """
        The order of the widget relative to the right of camera label.
        The lower the order number, the closer the widget to the camera label.
        """
        return 0


class AbstractCameraButtonDelegate(AbstractWidgetDelegate):
    """
    Self-register delegate to manage additional widgets in camera button.
    """
    # Use a list to track all instances
    __g_registered = []

    @classmethod
    def get_instances(cls):
        """
        Retrieves all registered camera button delegates.
        """
        remove = []
        # Return a copy to avoid remove in the middle of iterating.
        all_instances = AbstractCameraButtonDelegate.__g_registered.copy()
        for wref in all_instances:
            obj = wref()
            if obj:
                yield obj
            else:
                remove.append(wref)

        for wref in remove:
            AbstractCameraButtonDelegate.__g_registered.remove(wref)

    def __init__(self):
        """Construct delegate and register."""
        super().__init__()

        self.__g_registered.append(
            weakref.ref(self, AbstractCameraButtonDelegate.__g_registered.remove)
        )

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Release resource and deregister all camera button delegates."""
        for wref in AbstractCameraButtonDelegate.__g_registered:
            if wref() == self:
                AbstractCameraButtonDelegate.__g_registered.remove(wref)
                break

        super().destroy()


class AbstractCameraMenuItemDelegate(AbstractWidgetDelegate):
    """
    Self-register delegate to manage additional widgets in camera menu item.
    """
    # Use a list to track all instances
    __g_registered = []

    @classmethod
    def get_instances(cls):
        """
        Retrieves all registered camera menu item delegates.
        """
        remove = []
        # Return a copy to avoid remove in the middle of iterating.
        all_instances = AbstractCameraMenuItemDelegate.__g_registered.copy()
        for wref in all_instances:
            obj = wref()
            if obj:
                yield obj
            else:
                remove.append(wref)

        for wref in remove:
            AbstractCameraMenuItemDelegate.__g_registered.remove(wref)

    def __init__(self):
        """Construct delegate and register."""
        super().__init__()

        self.__g_registered.append(
            weakref.ref(self, AbstractCameraMenuItemDelegate.__g_registered.remove)
        )

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Release resource and deregister all camera menu item delegates."""
        for wref in AbstractCameraMenuItemDelegate.__g_registered:
            if wref() == self:
                AbstractCameraMenuItemDelegate.__g_registered.remove(wref)
                break

        super().destroy()
