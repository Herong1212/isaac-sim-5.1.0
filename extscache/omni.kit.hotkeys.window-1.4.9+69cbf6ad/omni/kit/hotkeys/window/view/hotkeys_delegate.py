# pylint: disable=relative-beyond-top-level

__all__ = ["HotkeysDelegate"]
from typing import List
from omni.kit.actions.window import ActionsDelegate, AbstractColumnDelegate
import omni.ui as ui

from ..model.hotkey_item import EmptyFilterWindowItem, AddWindowItem, ActionExtItem
from ..style import VIEW_ROW_HEIGHT


class HotkeysDelegate(ActionsDelegate):
    def build_branch(
        self,
        model: ui.AbstractItemModel,
        item: ui.AbstractItem,
        column_id: int = 0,
        level: int = 0,
        expanded: bool = False
    ):
        if isinstance(item, AddWindowItem):
            return
        if isinstance(item, EmptyFilterWindowItem):
            return
        if model.can_item_have_children(item):
            super().build_branch(model, item, column_id, level, expanded)
        else:
            if column_id == 0 and isinstance(item, ActionExtItem):
                # Show background rectangle here when no sub hotkeys found for search/filter
                # Otherwise here will be blank but name with background next
                with ui.VStack(height=VIEW_ROW_HEIGHT):
                    ui.Spacer()
                    ui.Rectangle(width=20, height=26, style_type_name_override="ActionsView.Row.Background")
                    ui.Spacer()
            else:
                super().build_branch(model, item, column_id, level, expanded)

    def on_mouse_double_click(self, button: int, item: ui.AbstractItem, column_delegate: AbstractColumnDelegate):
        # No execute when double click
        pass

    def on_mouse_pressed(self, button: int, item: ui.AbstractItem, column_delegate: AbstractColumnDelegate):
        # No context menu
        pass

    def on_selection_changed(self, selections: List[ui.AbstractItem]):
        for i in range(self._column_registry.max_column_id + 1):
            delegate = self._column_registry.get_delegate(i)
            if delegate and hasattr(delegate, "on_selection_changed"):
                delegate.on_selection_changed(selections)

    def on_hover_changed(self, item, hovered) -> None:
        for i in range(self._column_registry.max_column_id + 1):
            delegate = self._column_registry.get_delegate(i)
            if delegate and hasattr(delegate, "on_hover_changed"):
                delegate.on_hover_changed(item, hovered)
