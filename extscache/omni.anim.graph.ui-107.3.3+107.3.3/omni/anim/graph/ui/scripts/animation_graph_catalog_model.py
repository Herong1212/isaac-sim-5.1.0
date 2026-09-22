import json
import omni.ui as ui
from pxr import Usd 
from .config import Paths
from .config import (
    get_blend_tree_node_types,
    get_state_machine_node_types,
    get_condition_graph_node_types,
    get_icon_urls
)
from enum import Enum
from typing import Any, List

EMPTY_STRING_MODEL = ui.SimpleStringModel("")


class AnimationGraphCatalogItem(ui.AbstractItem):
    def __init__(self, type_name: str):
        super().__init__()
        self.name_model = ui.SimpleStringModel(type_name)
        icon_file = get_icon_urls()[type_name]
        self.icon_model = ui.SimpleStringModel(f"{Paths.ICON_PATH}/{icon_file}")
        prim_def = Usd.SchemaRegistry().FindConcretePrimDefinition(type_name)
        info = "" if prim_def is None else prim_def.GetDocumentation()
        self.info_model = ui.SimpleStringModel(info)
        self.in_filter = True


class AnimationGraphCatalogGroup(AnimationGraphCatalogItem):
    def __init__(self, group_name: str, node_types: List[str]):
        super().__init__(group_name)
        self.children = [AnimationGraphCatalogItem(type_name) for type_name in node_types]

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""

        if not filter_name_text:
            for item in self.children:
                item.in_filter = True

            self.in_filter = True
        else:
            filter_name_text = filter_name_text.lower()
            group_visible = False
            for item in self.children:
                item.in_filter = filter_name_text in item.name_model.as_string.lower()
                group_visible |= item.in_filter

            self.in_filter = group_visible


class AnimationGraphCatalogModel(ui.AbstractItemModel):
    class Column(Enum):
        NAME = 0
        TYPE = 1
        ICON = 2
        INFO = 3

    class GraphType(Enum):
        NONE = 0
        BLEND_TREE = 1
        STATE_MACHINE = 2
        CONDITION = 3

    def __init__(self, graph_type: GraphType = GraphType.NONE):
        super().__init__()

        self._graph_type = graph_type

        def create_groups(node_type_dict_fn):
            groups = []
            node_type_dict = node_type_dict_fn()
            for category, node_types in node_type_dict.items():
                groups.append(AnimationGraphCatalogGroup(category, node_types))

            return groups

        self._catalog_list = [
            [],
            create_groups(get_blend_tree_node_types),
            create_groups(get_state_machine_node_types),
            create_groups(get_condition_graph_node_types)
        ]

        self._last_filter_text = None

    def destroy(self):
        self._graph_type = None
        self._catalog_list = None
        self._last_filter_text = None

    @property
    def graph_type(self) -> GraphType:
        return self._graph_type

    @graph_type.setter
    def graph_type(self, value: GraphType):
        self._graph_type = value
        self.filter_by_text(self._last_filter_text)

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is None:
            return [child for child in self._catalog_list[self._graph_type.value] if child.in_filter]
        if isinstance(item, AnimationGraphCatalogGroup):
            return [c for c in item.children if c.in_filter]
        return []

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item, column_id):
        if column_id == self.Column.NAME.value:
            return item.name_model
        elif column_id == self.Column.ICON.value:
            return item.icon_model
        elif column_id == self.Column.INFO.value:
            return item.info_model
        return EMPTY_STRING_MODEL

    def get_drag_mime_data(self, item):
        """Returns data for be able to drop this item somewhere"""
        if isinstance(item, AnimationGraphCatalogItem):
            return json.dumps({"node_type": item.name_model.as_string})

        return None

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""
        self._last_filter_text = filter_name_text

        for group in self._catalog_list[self._graph_type.value]:
            group.filter_by_text(filter_name_text)

        self._item_changed(None)


class AnimationGraphQuickSearchModel(AnimationGraphCatalogModel):
    def __init__(
        self,
        graph_window: "AnimationGraphWindow",
        graph_type: AnimationGraphCatalogModel.GraphType
    ):
        super().__init__(graph_type)

        self._graph_window = graph_window

    def destroy(self):
        self._graph_window = None
        super().destroy()

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        children = []

        # Bypass groups
        for group in super().get_item_children(item):
            children += super().get_item_children(group)

        return children

    def execute(self, item: Any):
        """The user pressed enter"""
        if not self._graph_window or not self._graph_window.graph_widget:
            return

        # Mime Data has the information about USD types.
        data = self.get_drag_mime_data(item)
        if not data:
            return

        class CustomEvent:
            def __init__(self, mime_data):
                self.mime_data = mime_data
                self.x = None
                self.y = None

        self._graph_window.graph_widget.on_drop(CustomEvent(data))
