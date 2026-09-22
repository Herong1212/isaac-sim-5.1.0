from typing import Callable

import carb.windowing
import omni.ui as ui

from ..model.category_model import CategoryStatus
from .viewport_menu_delegate import ViewportMenuDelegate

__all__ = ["CategoryMenuDelegate"]


class CategoryMenuDelegate(ViewportMenuDelegate):
    """
    A menu delegate that show icon for category status within a viewport menubar.
    """
    def __init__(self, status: CategoryStatus, icon_clicked_fn: Callable[[None], None] = None):
        """
        Constructor.

        Args:
            status (CategoryStatus): Current category status.
            icon_clicked_fn (Callable[[None], None]): Callback when icon clicked, defaults to None.
        """
        self._status = status
        super().__init__(icon_clicked_fn=icon_clicked_fn)

    def build_item(self, item: ui.MenuItem) -> None:
        """
        Build icon for category status.

        Args:
            item (ui.MenuItem): Menu item.
        """
        # icons required
        super().build_item(item)
        if self.icon:
            self.icon.name = self._status
            self.icon.set_mouse_hovered_fn(self._on_icon_hovered)

    @property
    def status(self) -> CategoryStatus:
        """Category status"""
        return self._status

    @status.setter
    def status(self, value: CategoryStatus) -> None:
        self._status = value
        if self.icon:
            self.icon.name = self._status

    def _on_icon_hovered(self, hovered) -> None:
        try:
            import omni.kit.window.cursor
            main_cursor = omni.kit.window.cursor.get_main_window_cursor()
            if main_cursor:
                if hovered:
                    main_cursor.override_cursor_shape(carb.windowing.CursorStandardShape.HAND)
                else:
                    main_cursor.clear_overridden_cursor_shape()
        except ImportError:
            carb.log_info("omni.kit.window.cursor not available, omni.kit.viewport.menubar cursor won't be changed")
