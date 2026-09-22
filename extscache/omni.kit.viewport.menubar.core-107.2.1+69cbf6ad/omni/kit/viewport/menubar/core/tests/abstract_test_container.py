__all__ = ["AbstractTestContainer"]

import copy
from typing import Dict

import carb
from omni.kit.viewport.menubar.core import ViewportMenuContainer, IconMenuDelegate
import omni.ui as ui

from ..style import VIEWPORT_MENUBAR_STYLE
from .style import UI_STYLE


class AbstractTestContainer(ViewportMenuContainer):
    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._settings.set("/exts/omni.kit.viewport.menubar.delegate/visible", True)
        self._settings.set("/exts/omni.kit.viewport.menubar.delegate/order", -100)

        self._triggered = 0
        self._right_clicked = 0
        self.root_menu = None

        test_ui_style = copy.copy(VIEWPORT_MENUBAR_STYLE)
        test_ui_style.update(UI_STYLE)
        super().__init__(
            name="Icon",
            delegate=IconMenuDelegate("Sample", triggered_fn=self._on_trigger, right_clicked_fn=self._on_right_click),
            visible_setting_path="/exts/omni.kit.viewport.menubar.delegate/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.delegate/order",
            style=test_ui_style
        )

        self._settings = carb.settings.get_settings()

    def destroy(self):
        self._delegate.destroy()
        super().destroy()

    def _on_trigger(self) -> None:
        self._triggered += 1

    def _on_right_click(self) -> None:
        self._right_clicked += 1

    def build_fn(self, factory: Dict):
        self.root_menu = ui.Menu(
            self.name, delegate=self._delegate, on_build_fn=self._build_menu_items, style=self._style
        )

    def _build_menu_items(self):
        pass
