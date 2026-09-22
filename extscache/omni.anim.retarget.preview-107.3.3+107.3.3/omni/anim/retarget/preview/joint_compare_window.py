# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import omni.ui as ui
import omni.kit.app
import omni.usd
from functools import partial
from typing import List


__all__ = ['JointCompareWindow']


common_style = {"color": 0xFFFFFF00}
unmatched_style = {"color": 0xFF03BAFC}
scrollingframe_style = {"background_color": 0xFF23211F}


class ListModel(ui.SimpleStringModel):
    def __init__(self, text: str, is_common: bool, path: str):
        super().__init__(text)
        self.is_common = is_common
        self.path = path


class ListItem(ui.AbstractItem):
    def __init__(self, value_model: ui.AbstractValueModel):
        super().__init__()
        self.model = value_model
        self.children = []
        self._has_child = False

    @property
    def has_child(self):
        return self._has_child

    def get_children(self):
        return self.children

    def append_child(self, item):
        self._has_child = True
        self.children.append(item)

    def get_item_children(self, item):
        if item is None:
            return self._children
        return item.get_children()

    def get_item_value_model(self, item, column_id: int = 0):
        return item.model


class JointTreeItemModel(ui.AbstractItemModel):
    def __init__(self):
        super().__init__()
        self._children = []

    def get_item_children(self, item=None):
        if item is None:
            return self._children
        return item.get_children()

    def get_item_value_model_count(self, item):
        return 1

    def get_item_value_model(self, item=None, column_id: int = 0):
        if item is None:
            return None
        return item.model

    def append_child_item(self, parent, value_model):
        item = ListItem(value_model)
        if parent is None:
            self._children.append(item)
        else:
            parent.append_child(item)
        return item

    def destroy(self):
        self._children = None


class Delegate(ui.AbstractItemDelegate):
    def __init__(self, mouse_hovered_fn=None) -> None:
        super().__init__()
        self._mouse_hovered_fn = mouse_hovered_fn

    def build_branch(self, model, item, column_id, level, expanded):
        text = "    " * (level + 1)
        if item.has_child:
            if expanded:
                text += "-   "
            else:
                text += "+   "
        ui.Label(text, alignment=ui.Alignment.CENTER)

    def build_widget(self, model, item, column_id, level, expanded):
        item_value_model = model.get_item_value_model(item, column_id)
        label = ui.Label(
            item_value_model.as_string,
        )
        if item_value_model.is_common:
            label.set_style(common_style)
        else:
            label.set_style(unmatched_style)
        if self._mouse_hovered_fn:
            label.set_mouse_hovered_fn(partial(self._mouse_hovered_fn, item_value_model.path))


class JointCompareWindow:
    def __init__(
        self,
        context: omni.usd.UsdContext,
        joint_prim_paths: List[str],
        joint_lists: List[List[str]],
        captions: List[str],
        title: str = None,
        intersections: List[str] = None,
        uniques: List[List[str]] = None,
        visible: bool = True
    ):
        self._context = context
        self._joint_prim_paths = joint_prim_paths
        self._window = ui.Window(
            title if title else "Comparison",
            width=1000,
            height=400,
            visible=visible,
            flags=0,
        )
        self._window.set_visibility_changed_fn(self._on_visibility_changed)
        self._tree_models = []
        self._tree_views = []
        self._delegates = []
        with self._window.frame:
            with ui.HStack():
                for i, joint_list in enumerate(joint_lists):
                    if i > 0:
                        ui.Spacer(width=10)
                    with ui.VStack():
                        with ui.HStack(height=20):
                            ui.Label(captions[i])
                        with ui.ScrollingFrame(style=scrollingframe_style):
                            tree_model = JointTreeItemModel()
                            self._tree_models.append(tree_model)

                            # make sure root is the first element in the list
                            roots = [x for x in joint_list if '/' not in x]
                            if len(roots) == 0:
                                joint_list.insert(0, 'Root')
                            else:
                                joint_list.insert(0, joint_list.pop(joint_list.index(roots[0])))

                            for joint in joint_list:
                                tokens = joint.split('/')
                                if len(tokens) == 1:  # root
                                    model = ListModel(joint, joint in intersections, joint)
                                    tree_model.append_child_item(None, model)
                                else:
                                    parent = tree_model.get_item_children(None)[0]
                                    for i in range(1, len(tokens)):
                                        token = tokens[i]
                                        children = tree_model.get_item_children(parent)
                                        found = False
                                        for child in children:
                                            child_model = tree_model.get_item_value_model(child)
                                            if child_model is not None and hasattr(child_model, 'as_string') and\
                                               child_model.as_string == token:
                                                parent = child
                                                found = True
                                                break
                                        if not found:
                                            model = ListModel(token, joint in intersections, joint)
                                            model.is_common = joint in intersections
                                            tree_model.append_child_item(parent, model)
                                            children = tree_model.get_item_children(parent)
                                            parent = children[-1]

                            delegate = Delegate(self._on_mouse_hovered)
                            treeview = ui.TreeView(tree_model, root_visible=False, delegate=delegate)
                            self._tree_views.append(treeview)
                            self._delegates.append(delegate)

        asyncio.ensure_future(self._expand(True, -1))

    async def _expand(self, expanded=True, tab_index: int = -1):
        await omni.kit.app.get_app().next_update_async()
        for i, tree_view in enumerate(self._tree_views):
            if tab_index < 0 or i == tab_index:
                root = tree_view.model.get_item_children(None)[0]
                tree_view.set_expanded(root, expanded, True)

    def clean(self):
        self._window.set_visibility_changed_fn(None)
        self._window.destroy()
        self._window = None
        for tree_model in self._tree_models:
            tree_model.destroy()
        self._tree_models = []

    def show(self):
        self._window.visible = True

    def hide(self):
        self._window.visible = False

    @property
    def visible(self):
        if self._window:
            return self._window.visible
        return False

    def _on_visibility_changed(self, visible: bool):
        if not visible and self._context:
            self._context.get_selection().set_selected_prim_paths([], False)

    def _on_mouse_hovered(self, joint_name: str, hovered: bool = True):
        if hovered:
            for joint_path in self._joint_prim_paths:
                if joint_path.endswith(joint_name):
                    self._context.get_selection().set_selected_prim_paths([joint_path], True)
