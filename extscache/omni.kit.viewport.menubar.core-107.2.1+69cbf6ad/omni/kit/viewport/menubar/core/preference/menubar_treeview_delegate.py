from typing import Dict, Callable

import omni.ui as ui

from ..menu_item.viewport_menu_item import ViewportMenuItem
from ..viewport_menu_model import ViewportMenuModel
from ..model.combobox_model import SettingComboBoxModel
from ..model.reset_button import ResetButton

__all__ = ["AlignmentImages", "MenubarTreeViewDelegate"]


class AlignmentImages():
    def __init__(self, left: bool, on_alignment_changed: Callable[[bool], None], icon_size: int = 20):
        self._on_alignment_clicked = on_alignment_changed

        with ui.VStack(width=0):
            ui.Spacer()
            with ui.HStack(spacing=10, height=0):
                self._left = ui.ImageWithProvider(width=icon_size, height=icon_size, style_type_name_override="TreeView.Item.Alignment", name="left", checked=not left)
                self._right = ui.ImageWithProvider(width=icon_size, height=icon_size, style_type_name_override="TreeView.Item.Alignment", name="right", checked=left)
            ui.Spacer()

        if left:
            self._right.set_mouse_pressed_fn(lambda x, y, b, a: on_alignment_changed(False))
        else:
            self._left.set_mouse_pressed_fn(lambda x, y, b, a: on_alignment_changed(True))


class MenubarTreeViewDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer.
    TreeView calls the methods of the delegate to create custom widgets for each item.
    """

    def __init__(self):
        super().__init__()
        self._widgets: Dict[ViewportMenuItem, ui.Widget] = {}

    def destroy(self):
        self._widgets.clear()

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        return

    def build_widget(self, model: ViewportMenuModel, item: ViewportMenuItem, column_id, level, expanded):
        """Create a widget per column per item"""
        if "ViewportMenuSpacer" in item.name:
            # Do not show spacer here
            return

        if column_id == 0:
            self._widgets[item] = ui.HStack(height=20)
            with self._widgets[item]:
                # NAME
                name_model = model.get_item_value_model(item, 0)
                ui.Label(name_model.as_string, style_type_name_override="TreeView.Item.Label")

                ui.Spacer()

                with ui.HStack(spacing=10, width=ui.Percent(60)):
                    # Visible
                    with ui.VStack(width=0):
                        ui.Spacer()
                        ui.CheckBox(item.visible_model, width=10, height=0, style_type_name_override="TreeView.Item.CheckBox")
                        ui.Spacer()

                    # Alignment
                    AlignmentImages(item.order_model.as_int < 0, lambda l, m=model, i=item: self._on_alignment_changed(m, i, l))

                    # Expand
                    if item.expand_model:
                        expand_combox_model = SettingComboBoxModel(item.expand_model.path, ["Expanded", "Collapsed"], values=[True, False])
                        ui.ComboBox(expand_combox_model, style_type_name_override="TreeView.Item.ComboBox")

                    # Line
                    ui.Line(width=ui.Fraction(1), style_type_name_override="TreeView.Item.Line")

                    # Reset button
                    models = [item.visible_model, item.order_model]
                    if item.expand_model:
                        models.append(item.expand_model)
                    reset_btn = ResetButton(models, on_reset_fn=lambda m=model, i=item: self._on_reset(m, i))
                    item.visible_model.set_reset_button(reset_btn)
                    item.order_model.set_reset_button(reset_btn)
                    if item.expand_model:
                        item.expand_model.set_reset_button(reset_btn)

    def _on_alignment_changed(self, model: ViewportMenuModel, item: ViewportMenuItem, left: bool):
        item.order_model.set_value(-item.order_model.as_int)

        # Need to update both item and whole treeview
        model._item_changed(item)  # noqa: PLW0212
        model._item_changed(None)  # noqa: PLW0212

    def _on_reset(self, model: ViewportMenuModel, item: ViewportMenuItem):
        # Need to update both item and whole treeview
        model._item_changed(item)  # noqa: PLW0212
        model._item_changed(None)  # noqa: PLW0212
