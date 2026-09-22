# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .skel_joint_search_selection_box import SkelJointSelectionSearchable

import omni
from omni.anim.retarget.core.scripts.rig import Rig
import omni.ui as ui
import omni.graph.tools as ogt

from typing import Dict, Callable
from contextlib import suppress
import os


HSTACK_PROPERTIES = {"spacing": 10}
NAME_VALUE_WIDTH = 150  # Width of the node property name column


def name_value_label(property_name: str, tooltip: str = ""):
    """Emit a UI label for the node property names; allows a common fixed width for the column"""
    return ui.Label(property_name, width=NAME_VALUE_WIDTH, alignment=ui.Alignment.RIGHT_TOP, tooltip=tooltip)


def name_value_hstack():
    """Emit an HStack widget suitable for the property/value pairs for node properties"""
    return ui.HStack(**HSTACK_PROPERTIES)


def find_unique_name(base_name: str, names_taken: Dict):
    """Returns the base_name with a suffix that guarantees it does not appear as a key in the names_taken
    find_unique_name("fred", ["fred": "flintsone", "fred0": "mercury"]) -> "fred1"
    """
    if base_name not in names_taken:
        return base_name
    index = 0
    while f"{base_name}{index}" in names_taken:
        index += 1
    return f"{base_name}{index}"


class DestructibleButton(ui.Button):
    """Class that enhances the standard button with a destroy method that removes callbacks"""

    def __init__(self, *args, **kwargs):
        """Initialize the button with the passed-in arguments"""
        super().__init__(*args, **kwargs)

    def destroy(self):
        """Called when the button is being destroyed"""
        self.set_clicked_fn(None)


class TreeItem(ui.AbstractItem):
    def __init__(self, tag: str, joint: str):
        """Initialize both of the models to the key/value pairs"""
        super().__init__()
        self.tag_model = ui.SimpleStringModel(tag)
        self.joint_model = ui.SimpleStringModel(joint)

    def destroy(self):
        ogt.destroy_property(self, "tag_model")
        ogt.destroy_property(self, "joint_model")

    def __repr__(self):
        return f'TreeItem("{self.tag_model.as_string} : {self.joint_model.as_string}")'


class TreeItemModel(ui.AbstractItemModel):
    def __init__(self):
        super().__init__()
        self._children = []
        self._rig = None
        self._default_tags = []

    def destroy(self):
        self._rig = None
        ogt.destroy_property(self, "_children")

    def set_rig(self, rig):
        self._rig: Rig = rig
        if rig:
            self._default_tags = rig.get_default_tags()
        else:
            self._default_tags.clear()

        self._rebuild_children()

    def refresh(self):
        self._rebuild_children()

    def _rebuild_children(self):

        if self._rig.skeleton:
            tag_joint_dict = self._rig.get_tags()
            self._key_list = tag_joint_dict.keys()
            self._children = [
                TreeItem(key, tag_joint_dict[key].joint) for key in self._key_list
            ]
            self._item_changed(None)
        else:
            self._children.clear()
            self._item_changed(None)

    def get_all_tags(self):
        return self._key_list

    def add_child(self, tag_name):
        self._rig.set_joint(tag_name, "", True)
        self._rebuild_children()

    def remove_child(self, key_value: str):
        self._rig.remove_tag(key_value)
        self._rebuild_children()

    def get_item_count(self):
        """Returns the number of children (i.e. rows in the tree widget)."""
        return len(self._children)

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        # Since we are doing a flat list, we return the children of root only.
        # If it's not root we return the empty list.
        return item.tag_model if item is not None else self._children

    def get_item_value_model_count(self, item):
        return 3

    def get_item_value_model(self, item, column_id: int):
        if (item is not None):
            return [item.tag_model, item.tag_model, item.joint_model][column_id]

    # for now we don't have reverification - i.e. if it failed
    # the event flow makes it difficult to revalidate, if I rebuild here, it will crash due to recursiveness
    # we need RigTreeView to handle this manually individually, without refreshing all window
    def set_tag_joint(self, tag_name, joint_name):
        self._rig.set_joint(tag_name, joint_name, True)

    # for now we don't have reverification - i.e. if it failed
    # the event flow makes it difficult to revalidate, if I rebuild here, it will crash due to recursiveness
    # we need RigTreeView to handle this manually individually, without refreshing all window
    def set_tag_name(self, old_tag, new_tag):
        self._rig.rename_tag(old_tag, new_tag)

    def get_tree_item(self, tag_name):

        for item in self._children:
            if item.tag_model.as_string == tag_name:
                return item
        return None

    def clear_select(self):
        self._rig.clear_select()

    def select(self, item: TreeItem):
        if item:
            self._rig.set_selected(item.tag_model.as_string, True)

    def get_unassigned_tags(self):
        available_tags_by_group = {}
        groups = self._rig.group_names
        for group in groups:
            available_tags_by_group[group] = self._rig.get_unassigned_tags(group)
        return available_tags_by_group

    def is_default_tag(self, item: TreeItem):
        return (item.tag_model.as_string in self._default_tags)

    def find_unique_tag_name(self):
        return find_unique_name("New Tag", self._rig.get_tags())


class TreeItemUIContainer():
    def __init__(self):
        self.label = None
        self.stack = None
        self.selection = None
        self.button = None
        self.on_button_clicked = None
        self._icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/icons"

    def destroy(self):
        self.label = None
        self.selection = None
        with suppress(AttributeError):
            if self.stack:
                self.stack.set_mouse_double_clicked_fn(None)
        self.stack = None
        ogt.destroy_property(self, "button")

    def create_button(self, text, w, h, on_click_fn, style, tooltip):
        self.button = DestructibleButton(
            text,
            width=w,
            height=h,
            clicked_fn=on_click_fn,
            style=style,
            tooltip=tooltip
        )

    def create_label(self, value_model, stack, on_double_click):
        self.label = ui.Label(value_model.as_string, padding_x=5)
        field = ui.StringField(value_model, visible=False)
        # start editing when double clicked
        stack.set_mouse_double_clicked_fn(
            lambda x, y, b, m, f=field, lb=self.label: on_double_click(b, f, lb)
        )
        self.stack = stack

    def set_label_text(self, str):
        self.label.text = str

    def create_joint_selection(self, skeleton, tag, joint, on_joint_modified):
        self.selection = SkelJointSelectionSearchable(on_joint_modified, skeleton, tag, joint, self._icon_path)

    def set_joint_selection(self, joint):
        if self.selection is not None:
            self.selection.set_selection(self.label.text, joint)

    def set_tag_name(self, str):
        self.set_label_text(str)
        self.selection.set_tag_name(str)


class TreeItemDelegate(ui.AbstractItemDelegate):
    def __init__(self, on_joint_modified, on_tag_modified):
        """Initialize the state with no subscription on the end edit; it will be used later"""
        super().__init__()
        self._subscription = None
        self._skeleton = None
        self._remove_button_style = {
            "Button": {"stack_direction": ui.Direction.RIGHT_TO_LEFT},
            "Button.Image": {
                "color": 0xFFFFCC99,
                "image_url": f"{ICON_PATH}/clear.svg",
                "alignment": ui.Alignment.RIGHT_CENTER,
            },
            "Button.Label": {"alignment": ui.Alignment.LEFT},
        }
        # modified event for view trigger
        self._on_joint_modified = on_joint_modified
        self._on_tag_modified = on_tag_modified
        # TreeItemUIContainer
        self._ui_container = {}
        self._add_menu = ui.Menu("")

    def destroy(self):
        """Release any hanging references"""
        ogt.destroy_property(self, "_ui_container")
        self._subscription = None
        self._add_menu = None

    def build_branch(self, model, item, column_id: int, level: int, expanded: bool):
        """Create a branch widget that opens or closes subtree"""
        pass

    def build_header(self, column_id: int):
        """Set up the header entry at the named column"""
        header_style = "TreeView.Header"
        if column_id == 0:
            ui.Label("Tag", style_type_name_override=header_style, style={"font_size": 14.0, "padding": 5, "margin": 5})
        elif column_id == 1:
            ui.Label("Joint", style_type_name_override=header_style, style={"font_size": 14.0, "padding": 5, "margin": 5})

    def on_add_button_clicked(self, model):
        available_tags_by_group = model.get_unassigned_tags()
        groups = available_tags_by_group.keys()
        # Reset the previous context popup
        self._add_menu.clear()
        with self._add_menu:
            for group in groups:
                with ui.Menu(group):
                    tags = available_tags_by_group[group]
                    for tag in tags:
                        ui.MenuItem(tag, triggered_fn=lambda m=model, t=tag: self._on_add_item(m, t))
            ui.MenuItem("Custom", triggered_fn=lambda m=model: self._on_add_item(m, ""))

        self._add_menu.show()

    def _on_add_item(self, model, tag):
        """Callback hit when the button to add a new item was pressed"""
        if tag == "":
            tag = model.find_unique_tag_name()
        model.add_child(tag)

    def _on_remove_item(self, model, item):
        """Callback hit when the button to remove an existing item was pressed"""
        model.remove_child(item.tag_model.as_string)

    def _on_double_click(self, button, field, label):
        """Called when the user double-clicked the item in TreeView"""
        if button != 0:
            return
        # make Field visible when double clicked
        field.visible = True
        field.focus_keyboard()
        self._tag_to_be_edited = label.text
        # when editing is finished (enter pressed of mouse clicked outside of the viewport)
        self._subscription = field.model.subscribe_end_edit_fn(
            lambda m, f=field, lb=label: self._on_end_edit(m, f, lb)
        )

    def _on_end_edit(self, model, field, label):
        """Called when the user is editing the item and pressed Enter or clicked outside of the item"""
        field.visible = False
        label.text = model.as_string
        # todo: Verify that this is not duplicating an existing entry
        self._subscription = None
        self._on_tag_modified(self._tag_to_be_edited, model.as_string)
        # clear old key name
        self._tag_to_be_edited = ""

    def build_widget(self, model, item, column_id: int, level: int, expanded: bool):
        """Create a widget per column per item"""
        tag = item.tag_model.as_string
        if tag not in self._ui_container:
            self._ui_container[tag] = TreeItemUIContainer()
        tag_ui: TreeItemUIContainer = self._ui_container[tag]
        if column_id == 0:
            stack = ui.ZStack(height=20)
            with stack:
                value_model = model.get_item_value_model(item, column_id)
                tag_ui.create_label(value_model, stack, self._on_double_click)
        elif column_id == 1:
            tag_ui.create_joint_selection(self._skeleton, item.tag_model.as_string, item.joint_model.as_string, self._on_joint_modified)
        elif column_id == 2:
            # if not default tag, allow remove
            if not model.is_default_tag(item):
                tag_ui.create_button(
                    "", 30, 30,
                    lambda: self._on_remove_item(model, item),
                    self._remove_button_style, "Remove"
                )

    # view notification from rig model
    # assumption here is all model is fixed, so just view has to reflect the change
    def on_tag_modified(self, old_name, new_name):
        if old_name in self._ui_container:
            self._ui_container[new_name] = self._ui_container[old_name]
            self._ui_container[new_name].set_tag_name(new_name)
            self._ui_container.pop(old_name)

    def on_joint_modified(self, tag_name, joint_name):
        if tag_name in self._ui_container:
            self._ui_container[tag_name].set_joint_selection(joint_name)

    def set_skeleton(self, skeleton):
        if self._skeleton != skeleton:
            self._skeleton = skeleton
            if self._skeleton is not None:
                for tag in self._ui_container:
                    self._ui_container[tag].destroy()
                self._ui_container.clear()


class RigTreeView:
    def __init__(self, rig: Rig, icon_path: str, on_clear_tag: Callable):
        self._icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/icons"

        self._on_clear_tag = on_clear_tag
        self._item_model = TreeItemModel()
        self._item_delegate = TreeItemDelegate(self.on_view_joint_modified, self.on_view_tag_modified)
        self._style = {
            "Button": {"stack_direction": ui.Direction.RIGHT_TO_LEFT},
            "Button::listbox": {"stack_direction": ui.Direction.RIGHT_TO_LEFT},
            "Button.Image::listbox": {
                "color": 0xFFA8A8A8,
                "image_url": f"{self._icon_path}/listbox.svg",
                "alignment": ui.Alignment.RIGHT_CENTER,
            },
            "Button.Label::listbox": {"alignment": ui.Alignment.LEFT},
        }
        with ui.VStack():
            with ui.ScrollingFrame(
                height=200,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                style_type_name_override="TreeView",
                style={"Field": {"background_color": 0xFF000000}},
            ):
                self._tree_view = ui.TreeView(
                    self._item_model,
                    delegate=self._item_delegate,
                    root_visible=False,
                    header_visible=False,
                    columns_resizable=False,
                    column_widths=[100, ui.Percent(65), ui.Percent(35)]
                )

                self._tree_view.identifier = "RigTreeView"

            ui.Spacer(height=5)
            # buttons for the actions
            with ui.VStack(style=self._style):
                with ui.HStack():
                    ui.Spacer()
                    ui.Button("Reset All", width=80, height=30, clicked_fn=self._on_clear_tag, tooltip="Remove all the tags...")
                    ui.Button(
                        "Add Tag",
                        name="listbox",
                        image_width=10,
                        image_height=10,
                        width=80,
                        height=30,
                        clicked_fn=lambda: self._item_delegate.on_add_button_clicked(self._item_model),
                        tooltip="Add More Tags..."
                    )
        self._tree_view.set_selection_changed_fn(self.on_treeview_selection_changed)

        # listen to delegates
        rig.register_tag_added(self.on_tag_added)
        rig.register_tag_removed(self.on_tag_removed)
        rig.register_tag_changed(self.on_tag_modified)
        rig.register_joint_changed(self.on_joint_modified)
        rig.register_tags_cleared(self.on_tags_cleared)
        rig.register_tag_selected(self.on_tag_selected)
        rig.register_skeleton_changed(self.on_skeleton_changed)

        self._item_model.set_rig(rig)
        self._item_delegate.set_skeleton(rig.skeleton)
        self._tree_view.dirty_widgets()

    def __del__(self):
        if (self._item_model._rig):
            # listen to delegates
            self._item_model._rig.unregister_tag_added(self.on_tag_added)
            self._item_model._rig.unregister_tag_removed(self.on_tag_removed)
            self._item_model._rig.unregister_tag_changed(self.on_tag_modified)
            self._item_model._rig.unregister_joint_changed(self.on_joint_modified)
            self._item_model._rig.unregister_tags_cleared(self.on_tags_cleared)
            self._item_model._rig.unregister_tag_selected(self.on_tag_selected)
            self._item_model._rig.unregister_skeleton_changed(self.on_skeleton_changed)
        self._item_model = None
        self._item_delegate = None

    def _refresh(self, skeleton):
        self._item_delegate.set_skeleton(skeleton)
        self._item_model.refresh()
        self._tree_view.dirty_widgets()

    def on_tag_added(self, tag_name):
        # only rebuild if our model doesn't have it
        if tag_name not in self._item_model.get_all_tags():
            self._item_model.refresh()

    def on_tag_removed(self, tag_name):
        if tag_name in self._item_model.get_all_tags():
            self._item_model.refresh()

    def on_tag_modified(self, old_tag_name, new_tag_name):
        self._item_delegate.on_tag_modified(old_tag_name, new_tag_name)

    def on_joint_modified(self, tag_name, joint_name):
        self._item_model.refresh()

    def on_tags_cleared(self):
        self._item_model.refresh()

    # set selected
    def on_treeview_selection_changed(self, items):
        self._item_model.clear_select()
        for item in items:
            self._item_model.select(item)

    def on_tag_selected(self, tag_name, selected):
        selected_item = self._item_model.get_tree_item(tag_name)
        if selected:
            if selected_item not in self._tree_view.selection:
                self._tree_view.selection = [selected_item]
        else:
            if selected_item in self._tree_view.selection:
                self._tree_view.selection.clear()

    def on_skeleton_changed(self, skeleton):
        self._refresh(skeleton)

    def on_view_joint_modified(self, tag_name, joint_name):
        self._item_model.set_tag_joint(tag_name, joint_name)

    def on_view_tag_modified(self, old_tag_name, new_tag_name):
        self._item_model.set_tag_name(old_tag_name, new_tag_name)
