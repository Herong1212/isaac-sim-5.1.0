# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui

from functools import partial
from .checkpoints_model import CheckpointModel, CheckpointItem
from .style import get_style


class CheckpointTableView():
    def __init__(self, model: CheckpointModel, **kwargs):
        self._model = model
        self._tree_view = None
        self._delegate = CheckpointTableViewDelegate(**kwargs)
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
                column_widths=[25, ui.Fraction(1), 120, 120, 60],
                columns_resizable=True,
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
        self._delegate = None
        self._tree_view = None


class CheckpointTableViewDelegate(ui.AbstractItemDelegate):
    def __init__(self, **kwargs):
        super().__init__()
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)

    def build_header(self, column_id: int) -> None:  # pragma: no cover -- header is always turned off, see #L31
        headers = ["Checkpoint", "Description", "Date", "User", "Size"]
        return ui.Label(headers[column_id], height=22, style_type_name_override="TreeView.Header", name="label")

    def build_branch(self, model, item, column_id, level, expanded):
        pass

    def build_widget(self, model, item, column_id, level, expanded):
        def on_mouse_pressed(item: CheckpointItem, x, y, b, key_mod):
            if self._mouse_pressed_fn:
                self._mouse_pressed_fn(b, key_mod, item)

        def on_mouse_double_clicked(item: CheckpointItem, x, y, b, key_mod):
            if self._mouse_double_clicked_fn:
                self._mouse_double_clicked_fn(b, key_mod, item)

        if column_id == 0:
            ui.Label(
                f"{item.entry.relative_path[1:]}",
                style_type_name_override="TreeView.Item",
                mouse_pressed_fn=partial(on_mouse_pressed, item),
                mouse_double_clicked_fn=partial(on_mouse_double_clicked, item),
            )
        elif column_id == 1:
            with ui.VStack(height=20):
                ui.Spacer()
                with ui.HStack(height=0):
                    ui.Label(
                        f"{item.entry.comment}",
                        style_type_name_override="TreeView.Item",
                        tooltip=f"{item.entry.comment}",
                        word_wrap=not item.comment_elided,
                        elided_text=item.comment_elided,
                        mouse_pressed_fn=partial(on_mouse_pressed, item),
                        mouse_double_clicked_fn=partial(on_mouse_double_clicked, item),
                    )
                ui.Spacer()
        elif column_id == 2:
            ui.Label(
                f"{CheckpointItem.datetime_to_string(item.entry.modified_time)}",
                style_type_name_override="TreeView.Item",
            )
        elif column_id == 3:
            ui.Label(
                f"{item.entry.modified_by}",
                style_type_name_override="TreeView.Item",
                elided_text=True,
            )
        elif column_id == 4:
            ui.Label(
                f"{CheckpointItem.size_to_string(item.entry.size)}",
                style_type_name_override="TreeView.Item",
            )
