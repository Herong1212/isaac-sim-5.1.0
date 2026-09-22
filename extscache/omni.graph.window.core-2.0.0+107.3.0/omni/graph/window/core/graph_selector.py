# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Callable, List

import omni.ui as ui
from omni.kit.widget.searchfield import SearchField

from . import graph_config


class OmniGraphSelectorItemDelegate(ui.AbstractItemDelegate):
    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        name = item.name.get_value_as_string()

        with ui.HStack(height=20, tooltip_fn=lambda: self.tooltip(name)):
            ui.Spacer(width=4)
            ui.Label(name)

    def tooltip(self, name: str):
        padding = 2
        with ui.VStack():
            ui.Spacer(height=padding)
            with ui.HStack():
                ui.Spacer(width=padding)
                ui.Label(
                    f"{name}\n",
                    style={"font_size": 14, "color": 0xFF23211F},
                )
                ui.Spacer(width=padding)
            ui.Spacer(height=padding)


class OmniGraphSelectorItem(ui.AbstractItem):
    """Single item of the selector"""

    def __init__(self, model, name):
        super().__init__()
        self._model = model
        self.name = name


class OmniGraphSelectorModel(ui.AbstractItemModel):
    # List model handling the graph selector popup
    def __init__(self):
        super().__init__()
        self._all_items = []
        self._items = []
        self._filter = ""
        self._column_count = 1

    def get_item_children(self, item: OmniGraphSelectorItem) -> list:
        """Returns all the children when the widget asks it."""
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self.items

    def get_item_value_model_count(self, item) -> int:
        """The number of columns"""
        return self._column_count

    def get_item_value_model(self, item: OmniGraphSelectorItem, column_id: int):
        """Return the model given an item"""
        return item.name

    @property
    def items(self) -> List[OmniGraphSelectorItem]:
        return self._items

    @items.setter
    def items(self, values: List[OmniGraphSelectorItem]):
        self._all_items = values
        self._apply_filter()
        self._item_changed(None)

    @property
    def filter(self) -> str:  # noqa: A003
        return self._filter

    @filter.setter
    def filter(self, value: str):  # noqa: A003
        self._filter = value.strip()
        self._apply_filter()

    def _apply_filter(self):
        items = None
        if not self._filter:
            items = self._all_items
        else:
            items = [
                item for item in self._all_items if self._filter.lower() in item.name.get_value_as_string().lower()
            ]
        self._items = items
        self._item_changed(None)


class OmniGraphSelector:
    # Pop-up used by the breadcrumbs to select a new graph for display in the editor.
    def __init__(
        self,
        get_graphs_fn: Callable[[None], List[str]],
        selected_fn: Callable[[str], None],
        **kwargs,
    ):
        self._get_graphs_fn: Callable[[None], None] = get_graphs_fn
        self._selected_fn: Callable[[str], None] = selected_fn
        self._frame = ui.Frame(**kwargs)
        self._frame.set_build_fn(self.on_build)
        self._button = None

        self._tree_view = None
        self._search_field = None
        self._window = None
        self._model = OmniGraphSelectorModel()
        self._delegate = OmniGraphSelectorItemDelegate()

    def destroy(self):
        if self._frame:
            self._frame.destroy()
        self._frame = None
        if self._button:
            self._button.destroy()
        self._button = None
        if self._tree_view:
            self._tree_view.destroy()
        self._tree_view = None
        if self._search_field:
            self._search_field.destroy()
        self._search_field = None
        if self._window:
            self._window.destroy()
        self._window = None
        self._delegate = None
        self._model = None

    def _on_selected_item(self, item: OmniGraphSelectorItem):
        """Perform callback & close selector after selecting an item"""
        self._close_selector()
        self._selected_fn(item.name.get_value_as_string())

    def _filter(self, str_model):
        """Apply a filter to the items"""
        self._model.filter = str_model.get_value_as_string()

    def _close_selector(self):
        """Close the selector"""
        if self._window:
            self._window.visible = False

    def _show_selector(self, btn: ui.Button):
        """Show the selector popup window"""
        if self._window:
            self._window.destroy()
        if self._search_field:
            self._search_field.destroy()
        if self._tree_view:
            self._tree_view.destroy()

        self._window = ui.Window(
            "Graph Selector",
            width=200,
            height=150,
            position_x=btn.screen_position_x,
            position_y=btn.screen_position_y + btn.computed_height,
            padding_x=2,
            padding_y=2,
            flags=ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_MOVE,
        )
        with self._window.frame:
            with ui.VStack():
                with ui.Frame(height=20):
                    with ui.VStack():
                        self._search_field = SearchField(show_tokens=False)
                        self._search_field._search_field.model.add_value_changed_fn(  # noqa: protected-access
                            self._filter
                        )
                with ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    style_type_name_override="TreeView",
                ):
                    self._tree_view = ui.TreeView(
                        self._model,
                        delegate=self._delegate,
                        root_visible=False,
                        header_visible=False,
                        selection_changed_fn=lambda selection: self._on_selected_item(selection[-1]),
                    )

        self._model.items = [
            OmniGraphSelectorItem(self._model, ui.SimpleStringModel(attr)) for attr in self._get_graphs_fn()
        ]

    def on_build(self):
        """Build UI elements"""
        if self._button:
            self._button.destroy()

        # No graphs, don't build any UI
        if not self._get_graphs_fn():
            return

        self._button = ui.Button(
            "",
            name="Open Graph",
            height=15,
            width=15,
            image_width=18,
            image_height=18,
            image_url=f"{graph_config.Paths.ICON_PATH}/graph_selector_dark.svg",
            style={
                "Button": {
                    "padding": 2,
                    "font_size": 15,
                    "background_color": 0x0,
                    "color": graph_config.rgb_to_abgr(0xE0E0E0),
                }
            },
        )
        self._button.set_mouse_pressed_fn(lambda x, y, b, m: self._show_selector(self._button))
