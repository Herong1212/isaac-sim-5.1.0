__all__ = ["ActionsDelegate"]
from typing import List

import omni.ui as ui
from typing import Optional
from .abstract_column_delegate import AbstractColumnDelegate
from ..model.abstract_actions_model import AbstractActionsModel
from ..column_registry import ColumnRegistry
from ..style import ICON_PATH, VIEW_ROW_HEIGHT


class ActionsDelegate(ui.AbstractItemDelegate):
    """
    General action delegate to show action item in treeview.

    Args:
        column_registry (ColumnRegistry): Registry to get column delegate.
    """
    def __init__(self, model: AbstractActionsModel, column_registry: ColumnRegistry):
        self._model = model
        self._column_registry = column_registry
        self.__context_menu: Optional[ui.Menu] = None
        self.__execute_menuitem: Optional[ui.MenuItem] = None
        super().__init__()

    @property
    def column_widths(self) -> List[ui.Length]:
        """
        Column widths for treeview.
        """
        widths = []
        for i in range(self._column_registry.max_column_id):
            delegate = self._column_registry.get_delegate(i)
            if delegate:
                widths.append(delegate.width)
        return widths

    def build_branch(self, model: ui.AbstractItemModel, item: ui.AbstractItem, column_id: int=0, level: int = 0, expanded: bool = False):
        """
        Build branch for column.
        Refer to ui.AbstractItemDelegate.build_branch for detail.
        """
        if column_id == 0:
            with ui.HStack(width=20 * (level + 1), height=0):
                if model.can_item_have_children(item):
                    with ui.ZStack():
                        with ui.VStack(height=VIEW_ROW_HEIGHT):
                            ui.Spacer()
                            ui.Rectangle(height=26, style_type_name_override="ActionsView.Row.Background")
                            ui.Spacer()
                        with ui.VStack():
                            ui.Spacer()
                            self.__build_expand_icon(expanded)
                            super().build_branch(model, item, column_id, level, expanded)
                            ui.Spacer()
                else:
                    ui.Spacer()
    
    def build_widget(self, model: ui.AbstractItemModel, item: ui.AbstractItem, column_id: int=0, level: int=0, expanded: bool=False):
        """
        Build widget for column.
        Refer to ui.AbstractItemDelegate.build_widget for detail.
        """
        delegate = self._column_registry.get_delegate(column_id)
        if delegate:
            widget = delegate.build_widget(model, item, level, expanded)
            if widget:
                widget.set_mouse_pressed_fn(lambda x, t, b, f, i=item, d=delegate: self.on_mouse_pressed(b, i, d))
                widget.set_mouse_double_clicked_fn(lambda x, y, b, f, i=item, d=delegate: self.on_mouse_double_click(b, i, d))

    def build_header(self, column_id):
        """
        Build header for column.
        Refer to ui.AbstractItemDelegate.build_header for detail.
        """
        delegate = self._column_registry.get_delegate(column_id)
        if delegate:
            delegate.build_header()

    def on_mouse_double_click(self, button: int, item: ui.AbstractItem, column_delegate: AbstractColumnDelegate):
        if button == 0:
            self._model.execute(item)

    def on_mouse_pressed(self, button: int, item: ui.AbstractItem, column_delegate: AbstractColumnDelegate):
        if button == 1:
            if self.__context_menu is None:
                self.__context_menu = ui.Menu(f"ACTION CONTEXT MENU##{hash(self)}")
                with self.__context_menu:
                    self.__execute_menuitem = ui.MenuItem("Execute")
            self.__execute_menuitem.set_triggered_fn(lambda i=item: self._model.execute(item))
            self.__context_menu.show()

    def __build_expand_icon(self, expanded: bool):
        # Draw the +/- icon
        with ui.HStack():
            ui.Spacer()
            image_name = "Minus" if expanded else "Plus"
            ui.Image(
                f"{ICON_PATH}/{image_name}.svg", width=10, height=10, style_type_name_override="TreeView.Item"
            )
            ui.Spacer(width=5)
