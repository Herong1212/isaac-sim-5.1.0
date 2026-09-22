# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import time
from typing import List, Tuple

import omni.ui as ui
import omni.usd
from omni.kit.widget.stage import StageIcons
from pxr import Sdf, Usd

# Number of seconds until an inactive PrimListItem is considered stale
NUM_SECONDS_UNTIL_STALE = 1.25

# TODO: Remove dead code!
DEV_ALLOW_DUPLICATES = True
DEV_SHOW_ON_OFF_COLUMN = False


def _get_adjusted_column_id(column_id):
    return column_id if DEV_SHOW_ON_OFF_COLUMN else column_id - 1


class PrimNameModel(ui.SimpleStringModel):
    """Prim name with icon path based on prim type"""

    def __init__(self, name, icon_path):
        super().__init__(name)
        self.icon_path = icon_path


class PrimListItem(ui.AbstractItem):
    """Single prim list item"""

    def __init__(self, path, name, icon_path, parent):
        super().__init__()
        self.path_model = ui.SimpleStringModel(path)
        self.name_model = PrimNameModel(name, icon_path)
        self.on_off_model = ui.SimpleBoolModel(True)
        self.active_model = ui.SimpleBoolModel(True)
        self.time_deactivated_model = ui.SimpleFloatModel()
        self.inc_children_model = ui.SimpleBoolModel(True)
        self.hover_model = ui.SimpleBoolModel(False)
        self.children = []
        self.parent = parent

    def build_path_set(self, path_set):
        # Build recursively while eliminating duplicates
        if self.on_off_model.as_bool:
            path_set.add(self.path_model.as_string)

        if self.inc_children_model.as_bool:
            for child in self.children:
                child.build_path_set(path_set)

    def includes_children(self):
        item = self

        while item:
            if not item.inc_children_model.as_bool:
                return False
            item = item.parent

        return True

    def __repr__(self):
        return f"PrimListItem('{self.path_model.as_string}')"

    def __eq__(self, other):
        if type(self) == type(other):
            return self.path_model.as_string == other.path_model.as_string
        else:
            return False

    def __hash__(self):
        return hash(self.path_model.as_string)


class PrimListModel(ui.AbstractItemModel):
    """
    Prim list model.
    For now this is a de-duplicated flat list.
    """

    def __init__(self):
        super().__init__()
        self._children = []
        self._usd_context = omni.usd.get_context()
        self.stage_icons = StageIcons()

    def _get_stage_icon_path(self, prim):
        """
        Returns a filesystem path to the icon that the stage uses for the specified prim type.
        """
        # Workaround credit: Andrew Grant
        node_type = prim.GetTypeName()
        if node_type in ["DistantLight", "SphereLight", "RectLight", "DiskLight", "CylinderLight", "DomeLight"]:
            return self.stage_icons.get(node_type, "Light")
        if node_type == "":
            node_type = "Xform"

        return self.stage_icons.get(node_type, "Prim")

    def clear_all(self):
        self._children = []
        self._item_changed(None)

    def remove_item(self, item):
        # TODO: Explicitly clean-up the discarded sub-tree
        if not item.parent:
            self._children.remove(item)
        else:
            item.parent.children.remove(item)

        self._item_changed(None)

    def activate_item_by_path(self, path, active):
        item = next((c for c in self._children if path == c.path_model.as_string), None)
        if item:
            item.active_model.set_value(active)
            item.time_deactivated_model.set_value(time.time())
            self._item_changed(None)

    def activate_all_for_prefix(self, prefix, active):
        for item in self._children:
            if Sdf.Path(item.path_model.as_string).HasPrefix(prefix):
                item.active_model.set_value(active)
                item.time_deactivated_model.set_value(time.time())

        self._item_changed(None)

    def remove_stale_items(self):
        current_time = time.time()
        for item in self._children:
            if not item.active_model.as_bool:
                elapsed_time = current_time - item.time_deactivated_model.get_value_as_float()
                if elapsed_time > NUM_SECONDS_UNTIL_STALE:
                    self.remove_item(item)

    def select_item_on_stage(self, item):
        selection = self._usd_context.get_selection()
        selection.set_selected_prim_paths([item.path_model.as_string], False)

    def contains_descendants_of(self, path):
        """
        Returns True iff any top-level item in the current prim list has 'path' as a strict prefix.
        """
        return any(
            Sdf.Path(item.path_model.as_string).HasPrefix(path) and item.path_model.as_string != path.pathString
            for item in self._children
        )

    def contains_an_equal_or_ancestors_of(self, path):
        """
        Returns True iff 'path' is equal to or has a prefix of any top-level item in the current prim list.
        """
        return any(path.HasPrefix(Sdf.Path(item.path_model.as_string)) for item in self._children)

    def contains_an_equal_of(self, path):
        """
        Returns True iff 'path' is equal to any top-level item in the current prim list.
        """
        return any(path == item.path_model.as_string for item in self._children)

    def remove_descendants_of(self, path):
        """
        Removes any top-level items from the prim list which have 'path' as a strict prefix.
        """
        # TODO: Consider a better way to achieve the same result
        new_children = [
            c
            for c in self._children
            if not Sdf.Path(c.path_model.as_string).HasPrefix(path) or c.path_model.as_string == path.pathString
        ]
        self._children = new_children
        self._item_changed(None)

    def allow_duplicates(self):
        return DEV_ALLOW_DUPLICATES

    def add_subtree(self, root_path):
        stage = self._usd_context.get_stage()
        root_prim = stage.GetPrimAtPath(root_path)

        # TODO: Consider using something fancier like deque
        stack = []
        itr = iter(Usd.PrimRange.PreAndPostVisit(root_prim))
        for prim in itr:
            if itr.IsPostVisit():
                stack.pop()
            else:
                parent = stack[-1] if stack else None

                item = PrimListItem(
                    prim.GetPath().pathString,
                    prim.GetName(),
                    self._get_stage_icon_path(prim),
                    parent,
                )

                if parent:
                    parent.children.append(item)
                else:
                    self._children.append(item)

                stack.append(item)

        self._item_changed(None)

    def get_target_paths(self) -> List[Tuple[str, bool]]:
        """
        Returns a list of tuples, each specifying the path and whether to include children
        """
        # TODO: Remove dead code starting from item.build_path_set!
        # TODO: Specify types throughout!
        return [
            (item.path_model.as_string, item.inc_children_model.as_bool)
            for item in self._children
            if item.on_off_model.as_bool and item.active_model.as_bool
        ]

    def is_empty(self):
        return not any(item for item in self._children if item.on_off_model.as_bool and item.active_model.as_bool)

    def get_item_children(self, item):
        """A request for the root will have item equal to None."""
        if not item:
            return [child for child in self._children if child.active_model.as_bool]
        elif item.includes_children() and not self.allow_duplicates():
            return [child for child in item.children if child.active_model.as_bool]
        else:
            return []

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return _get_adjusted_column_id(3)

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        """
        if column_id == _get_adjusted_column_id(0):
            return item.on_off_model
        elif column_id == _get_adjusted_column_id(1):
            return item.name_model
        else:
            return item.inc_children_model


class PrimListDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer. TreeView calls the methods
    of the delegate to create custom widgets for each item.
    """

    def __init__(self, icon_path):
        super().__init__()
        # icon_path: Path to app icon folder
        self._icon_path = icon_path

    def build_branch(self, model, item, column_id, level, expanded):
        if not model.allow_duplicates():
            if column_id == _get_adjusted_column_id(1):
                """Create a branch widget that opens or closes subtree"""
                with ui.HStack(width=16 * (level + 1), height=0):
                    ui.Spacer()
                    if item.children and item.includes_children():
                        image_name = "Minus" if expanded else "Plus"
                        ui.Image(
                            model.stage_icons.get(image_name),
                            width=12,
                            height=12,
                            style={"color": 0xFFA8A8A8},
                        )

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per column per item"""
        if column_id == _get_adjusted_column_id(0):
            with ui.ZStack():
                ui.Rectangle(style={"background_color": 0xFF454545, "margin_height": 1}, width=65535)
                ui.ToolButton(
                    model=model.get_item_value_model(item, column_id),
                    image_height=18,
                    style={
                        "Button": {"background_color": 0x0},
                        "Button:checked": {"background_color": 0x0},
                        "Button.Image": {"image_url": f"{self._icon_path}/toggle-off.svg"},
                        "Button.Image:checked": {"image_url": f"{self._icon_path}/toggle-on.svg"},
                    },
                    tooltip="Toggle this line item only",
                )
        elif column_id == _get_adjusted_column_id(1):
            with ui.ZStack():
                ui.Rectangle(style={"background_color": 0xFF454545, "margin_height": 1}, width=65535)
                with ui.HStack():
                    with ui.VStack(width=25):
                        ui.Spacer(height=3)
                        ui.Image(
                            model.get_item_value_model(item, column_id).icon_path,
                            height=19,
                        )
                    ui.Spacer(width=2)
                    ui.Label(
                        model.get_item_value_model(item, column_id).as_string,
                        tooltip="Double click to set selection",
                        height=25,
                        mouse_double_clicked_fn=lambda x, y, btn, m: model.select_item_on_stage(item),
                    )
        else:
            with ui.HStack(height=25):
                with ui.ZStack():
                    ui.Rectangle(style={"background_color": 0xFF454545, "margin_height": 1}, width=75)
                    if item.children:
                        with ui.HStack():
                            ui.Spacer(width=50)
                            with ui.VStack():
                                ui.Spacer(height=5.5)
                                ui.CheckBox(
                                    model=model.get_item_value_model(item, column_id),
                                    style={"CheckBox": {"background_color": 0xFFA8A8A8}},
                                    tooltip="Toggle this item's children",
                                )

                                model.get_item_value_model(item, column_id,).add_value_changed_fn(
                                    lambda ivm: model._item_changed(item),
                                )

                if not item.parent:
                    style = {
                        "Button": {
                            "background_color": 0x0,
                            "padding": 0,
                            "margin": 0,
                            "margin_height": 1,
                            "border_width": 0,
                            "border_radius": 0,
                        },
                    }
                    remove_button = ui.Button(
                        style=style,
                        image_url=f"{self._icon_path}/remove.svg",
                        width=20,
                        clicked_fn=lambda: model.remove_item(item),
                        tooltip="Click to remove from list",
                    )

                    remove_button.visible = False

                    def hover_change(model):
                        remove_button.visible = model.as_bool

                    item.hover_model.add_value_changed_fn(hover_change)

    def build_header(self, column_id):
        """Build the header"""
        if column_id == _get_adjusted_column_id(0):
            column = "On/Off"
        elif column_id == _get_adjusted_column_id(1):
            column = "        Name"
        else:
            column = "Include Children"

        with ui.VStack():
            ui.Label(column, height=25)
            ui.Rectangle(style={"background_color": 0xFF23211F}, height=3)

    def get_column_widths(self):
        if DEV_SHOW_ON_OFF_COLUMN:
            return [ui.Pixel(45), ui.Fraction(1), ui.Pixel(95)]
        else:
            return [ui.Fraction(1), ui.Pixel(95)]
