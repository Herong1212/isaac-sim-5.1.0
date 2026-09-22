__all__ = ["RadioMenuCollection"]

from typing import Optional
from omni import ui
from ..model.combobox_model import ComboBoxModel
from ..delegate.viewport_menu_delegate import ViewportMenuDelegate
from ..utils import menu_is_tearable
from .viewport_menu_separator import ViewportMenuSeparator


class RadioMenuCollection(ui.MenuItemCollection):
    """
    A menu collection for radio menu items.
    """

    def __init__(
        self,
        text: str,
        model: ComboBoxModel,
        identifier: Optional[str] = None,
        hide_on_click: bool = False,
        can_toggle_off: bool = False,
        delegate: ui.MenuDelegate = None
    ):
        """
        Constructor.

        Args:
            text (str): Menu text.
            model (ComboBoxModel): Radio data model.

        Keyword Args:
            identifier (Optional[str]): Menu item Identifier, defaults to None.
            hide_on_click (bool): Hide menu when radio menu item clicked, defaults to False.
            can_toggle_off (bool):Toggle selected state to off when radio menu item clicked and already selected, defaults to False.
            delegate (ui.MenuDelegate): Menu item Delegate, defaults to None.
        """
        self._model = model
        self._hide_on_click = hide_on_click
        self.__menu_items = []
        self.__in_triggered = False
        self.__can_toggle_off = can_toggle_off
        self._sub = None
        self._sub_model = None
        super().__init__(text, delegate=delegate, on_build_fn=self._build_menu_items, tearable=menu_is_tearable(identifier))

    def __destroy_menu_items(self, value=None):
        if self.__menu_items:
            for menu_item in self.__menu_items:
                menu_item.destroy()
        self.__menu_items = value

    def destroy(self) -> None:
        """Release resources"""
        model, self._model, self._sub, self._sub_model = self._model, None, None, None
        if model and hasattr(model, 'destroy'):
            model.destroy()
        self.__destroy_menu_items(None)
        super().destroy()

    def _build_menu_items(self):
        self.__destroy_menu_items([])

        with self:
            for index, item in enumerate(self._model.get_item_children(None)):
                menu_item = self.build_menu_item(item)
                if not isinstance(menu_item, ViewportMenuSeparator):
                    menu_item.checkable = True
                    menu_item.checked = index == self._model.current_index.as_int
                    menu_item.set_triggered_fn(lambda i=index: self._item_chosen(i))
                menu_item.hide_on_click = self._hide_on_click
                # Only need to save the menu-item if cannot toggle to off
                if not bool(self.__can_toggle_off):
                    self.__menu_items.append(menu_item)

        # When current is changed outside, update menu items
        self._sub = self._model.current_index.subscribe_value_changed_fn(self._on_current_changed)
        self._sub_model = self._model.subscribe_item_changed_fn(self._on_item_changed)

    def build_menu_item(self, item: ui.AbstractItem) -> ui.MenuItem:
        """
        Build single radio menu item.

        Args:
            item (ui.AbstractItem): Model item.
        """
        return ui.MenuItem(
            item.model.as_string,
            delegate=ViewportMenuDelegate(),
        )

    def _item_chosen(self, index: int):
        try:
            self.__in_triggered = True
            # Set the current index if it has changed
            current_index = self._model.current_index.as_int if (self._model and self._model.current_index) else None
            if current_index != index:
                self._model.current_index.set_value(index)
            elif (not bool(self.__can_toggle_off)) and self.__menu_items and index < len(self.__menu_items):
                # Force the check state on in the case that it hasn't
                import asyncio

                async def force_checked_state(index: int, checked: bool):
                    self.__menu_items[index].checked = checked
                asyncio.ensure_future(force_checked_state(index, True))
        finally:
            self.__in_triggered = False

    def _on_current_changed(self, model: ui.AbstractValueModel):
        if not self.__in_triggered:
            self.invalidate()

    def _on_item_changed(self, model: ui.AbstractValueModel, item: ui.AbstractItem):
        self.invalidate()
