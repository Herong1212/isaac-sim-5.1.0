# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial
from omni import ui
from .checkpoints_model import CheckpointItem, CheckpointModel
from .style import get_style


class CheckpointSlimView:
    def __init__(self, model: CheckpointModel, **kwargs):
        self._model = model
        self._tree_view = None
        self._delegate = CheckpointSlimViewDelegate(**kwargs)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._build_ui()

    def _build_ui(self):
        with ui.ZStack(style=get_style()):
            ui.Rectangle(style_type_name_override="TreeView.Background")
            self._tree_view = ui.TreeView(
                self._model,
                delegate=self._delegate,
                root_visible=False,
                header_visible=False,
                column_widths=[ui.Fraction(1)],
                style_type_name_override="TreeView"
            )
        self._tree_view.set_selection_changed_fn(self._on_selection_changed)

    def _on_selection_changed(self, selections):
        if len(selections) > 1:
            # only allow selecting one checkpoint
            self._tree_view.selection = [selections[-1]]
        if self._selection_changed_fn:
            self._selection_changed_fn(selections)

    def destroy(self):
        if self._delegate:
            self._delegate.destroy()
            self._delegate = None
        self._tree_view = None


class CheckpointSlimViewDelegate(ui.AbstractItemDelegate):
    def __init__(self, **kwargs):
        super().__init__()
        self._widget = None
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)

    def build_branch(self, model, item, column_id, level, expanded):
        pass

    def build_widget(self, model: CheckpointModel, item: CheckpointItem, column_id: int, level: int, expanded: bool):
        """Create a widget per item"""
        if not item or column_id > 0:
            return

        tooltip = f"#{item.entry.relative_path[1:]}. {item.entry.comment}\n"
        tooltip += f"{CheckpointItem.datetime_to_string(item.entry.modified_time)}\n"
        tooltip += f"{item.entry.modified_by}"

        def on_mouse_pressed(item: CheckpointItem, x, y, b, key_mod):
            if self._mouse_pressed_fn:
                self._mouse_pressed_fn(b, key_mod, item)

        def on_mouse_double_clicked(item: CheckpointItem, x, y, b, key_mod):
            if self._mouse_double_clicked_fn:
                self._mouse_double_clicked_fn(b, key_mod, item)

        with ui.ZStack(style=get_style()):
            self._widget = ui.Rectangle(
                mouse_pressed_fn=partial(on_mouse_pressed, item),
                mouse_double_clicked_fn=partial(on_mouse_double_clicked, item),
                style_type_name_override="Card"
            )
            with ui.VStack(spacing=0):
                ui.Spacer(height=4)
                with ui.HStack():
                    ui.Label(
                        f"#{item.entry.relative_path[1:]}.", width=0,
                        style_type_name_override="Card.Label"
                    )
                    ui.Spacer(width=2)
                    if item.entry.comment:
                        ui.Label(
                            f"{item.entry.comment}",
                            tooltip=tooltip,
                            word_wrap=not item.comment_elided,
                            elided_text=item.comment_elided,
                            style_type_name_override="Card.Label"
                        )
                    else:
                        ui.Label(
                            f"{CheckpointItem.datetime_to_string(item.entry.modified_time)}", 
                            style_type_name_override="Card.Label"
                        )
                if item.entry.comment:
                    ui.Label(
                        f"{CheckpointItem.datetime_to_string(item.entry.modified_time)}", 
                        style_type_name_override="Card.Label"
                    )
                ui.Label(f"{item.entry.modified_by}", style_type_name_override="Card.Label")
                ui.Spacer(height=8)
                ui.Separator(style_type_name_override="Card.Separator")
                ui.Spacer(height=4)

    def destroy(self):
        self._widget = None
        self._mouse_pressed_fn = None
        self._mouse_double_clicked_fn = None
