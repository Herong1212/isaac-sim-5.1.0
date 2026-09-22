# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["NameColumnDelegate"]

import asyncio
import math
import omni.ui as ui

from ..abstract_stage_column_delegate import AbstractStageColumnDelegate
from ..stage_model import StageModel, StageItemSortPolicy
from ..stage_item import StageItem
from ..stage_icons import StageIcons
from functools import partial
from typing import List
from enum import Enum


COLOR_LIVE_GREEN = 0xFF00B86B
COLOR_LIVE_SEL = 0xFF00F86E
COLOR_RELOAD_ORANGE = 0xFF0088CC
COLOR_RELOAD_SEL = 0xFF00AAFF
WIDGET_STYLES = {
    "TreeView.Image::object_icon_grey": {"color": 0x80FFFFFF},
    "TreeView.Item::object_name_grey": {"color": 0xFF4D4B42},
    "TreeView.Item::object_name_missing": {"color": 0xFF6F72FF},
    "TreeView.Item::object_name_missing:hovered": {"color": 0xFF6F72FF},
    "TreeView.Item::object_name_missing:selected": {"color": 0xFF6F72FF},
    "TreeView.Item.Outdated": {"color": COLOR_RELOAD_ORANGE},
    "TreeView.Item.Outdated:hovered": {"color": COLOR_RELOAD_SEL},
    "TreeView.Item.Outdated:selected": {"color": COLOR_RELOAD_SEL},
    "TreeView.Item.Live": {"color": COLOR_LIVE_GREEN},
    "TreeView.Item.Live:hovered": {"color": COLOR_LIVE_SEL},
    "TreeView.Item.Live:selected": {"color": COLOR_LIVE_SEL},
    "TreeView.Image::not_active": {"color": 0xFFFFFFFF}
}


class NameColumnSortPolicy(Enum):
    NEW_TO_OLD = 0
    OLD_TO_NEW = 1
    A_TO_Z = 2
    Z_TO_A = 3


def split_selection(text, selection):
    """
    Split given text to substrings to draw selected text. Result starts with unselected text.
    Example: "helloworld" "o" -> ["hell", "o", "w", "o", "rld"]
    Example: "helloworld" "helloworld" -> ["", "helloworld"]
    """
    if not selection or text == selection:
        return ["", text]

    selection = selection.lower()
    selection_len = len(selection)
    result = []
    while True:
        found = text.lower().find(selection)

        result.append(text if found < 0 else text[:found])
        if found < 0:
            break
        else:
            result.append(text[found : found + selection_len])
            text = text[found + selection_len :]

    return result


class NameColumnDelegate(AbstractStageColumnDelegate):
    """The column delegate that represents the type column"""

    def __init__(self):
        super().__init__()

        self.__name_label_layout = None
        self.__name_label = None

        self.__drop_down_layout = None
        self.__name_sort_options_menu = None
        self.__items_sort_policy = NameColumnSortPolicy.OLD_TO_NEW

        self.__highlighting_enabled = None
        # Text that is highlighted in flat mode
        self.__highlighting_text = None

        self.__stage_model: StageModel = None

    def set_highlighting(self, enable: bool = None, text: str = None):
        """
        Specify if the widgets should consider highlighting. Also set the text that should be highlighted in flat mode.
        """
        if enable is not None:
            self.__highlighting_enabled = enable

        if text is not None:
            self.__highlighting_text = text.lower()

    @property
    def sort_policy(self):
        return self.__items_sort_policy

    @sort_policy.setter
    def sort_policy(self, value):
        if self.__items_sort_policy != value:
            self.__items_sort_policy = value
            self.__on_policy_changed()

    def destroy(self):
        if self.__name_label_layout:
            self.__name_label_layout.set_mouse_pressed_fn(None)

        if self.__drop_down_layout:
            self.__drop_down_layout.set_mouse_pressed_fn(None)
            self.__drop_down_layout = None

        self.__name_sort_options_menu = None

        if self.__name_label_layout:
            self.__name_label_layout.set_mouse_pressed_fn(None)
            self.__name_label_layout = None

        self.__stage_model = None

    @property
    def initial_width(self):
        """The width of the column"""
        return ui.Fraction(1)

    def __initialize_policy_from_model(self):
        stage_model = self.__stage_model
        if not stage_model:
            return

        if stage_model.get_items_sort_policy() == StageItemSortPolicy.NAME_COLUMN_NEW_TO_OLD:
            self.__items_sort_policy = NameColumnSortPolicy.NEW_TO_OLD
        elif stage_model.get_items_sort_policy() == StageItemSortPolicy.NAME_COLUMN_A_TO_Z:
            self.__items_sort_policy = NameColumnSortPolicy.A_TO_Z
        elif stage_model.get_items_sort_policy() == StageItemSortPolicy.NAME_COLUMN_Z_TO_A:
            self.__items_sort_policy = NameColumnSortPolicy.Z_TO_A
        else:
            self.__items_sort_policy = NameColumnSortPolicy.OLD_TO_NEW

        self.__update_label_from_policy()

    def __update_label_from_policy(self):
        if not self.__name_label:
            return

        if self.__items_sort_policy == NameColumnSortPolicy.NEW_TO_OLD:
            name = "Name (New to Old)"
        elif self.__items_sort_policy == NameColumnSortPolicy.A_TO_Z:
            name = "Name (A to Z)"
        elif self.__items_sort_policy == NameColumnSortPolicy.Z_TO_A:
            name = "Name (Z to A)"
        else:
            name = "Name (Old to New)"

        self.__name_label.text = name

    def __on_policy_changed(self):
        stage_model = self.__stage_model
        if not stage_model:
            return

        if self.__items_sort_policy == NameColumnSortPolicy.NEW_TO_OLD:
            stage_model.set_items_sort_policy(StageItemSortPolicy.NAME_COLUMN_NEW_TO_OLD)
        elif self.__items_sort_policy == NameColumnSortPolicy.A_TO_Z:
            stage_model.set_items_sort_policy(StageItemSortPolicy.NAME_COLUMN_A_TO_Z)
        elif self.__items_sort_policy == NameColumnSortPolicy.Z_TO_A:
            stage_model.set_items_sort_policy(StageItemSortPolicy.NAME_COLUMN_Z_TO_A)
        else:
            stage_model.set_items_sort_policy(StageItemSortPolicy.NAME_COLUMN_OLD_TO_NEW)

        self.__update_label_from_policy()

    def __on_name_label_clicked(self, x, y, b, m):
        if b != 0 or not self.__stage_model:
            return

        if self.__items_sort_policy == NameColumnSortPolicy.A_TO_Z:
            self.__items_sort_policy = NameColumnSortPolicy.Z_TO_A
        elif self.__items_sort_policy == NameColumnSortPolicy.Z_TO_A:
            self.__items_sort_policy = NameColumnSortPolicy.NEW_TO_OLD
        elif self.__items_sort_policy == NameColumnSortPolicy.NEW_TO_OLD:
            self.__items_sort_policy = NameColumnSortPolicy.OLD_TO_NEW
        else:
            self.__items_sort_policy = NameColumnSortPolicy.A_TO_Z

        self.__on_policy_changed()

    def build_header(self, **kwargs):
        """Build the header"""

        style_type_name = "TreeView.Header"
        stage_model = kwargs.get("stage_model", None)
        self.__stage_model = stage_model
        if stage_model:
            with ui.HStack():
                self.__name_label_layout = ui.HStack()
                self.__name_label_layout.set_mouse_pressed_fn(self.__on_name_label_clicked)

                with self.__name_label_layout:
                    ui.Spacer(width=10)
                    self.__name_label = ui.Label(
                        "Name", name="columnname", style_type_name_override=style_type_name
                    )
                    self.__initialize_policy_from_model()
                    ui.Spacer()

                with ui.ZStack(width=16):
                    ui.Rectangle(name="drop_down_hovered_area", style_type_name_override=style_type_name)
                    self.__drop_down_layout = ui.ZStack(width=0)
                    with self.__drop_down_layout:
                        ui.Rectangle(width=16, name="drop_down_background", style_type_name_override=style_type_name)
                        with ui.HStack():
                            ui.Spacer()
                            with ui.VStack(width=0):
                                ui.Spacer(height=4)
                                ui.Triangle(
                                    name="drop_down_button",
                                    width=8, height=8,
                                    style_type_name_override=style_type_name,
                                    alignment=ui.Alignment.CENTER_BOTTOM
                                )
                                ui.Spacer(height=2)
                            ui.Spacer()
                ui.Spacer(width=4)

                def on_sort_policy_changed(policy, value):
                    if self.sort_policy != policy:
                        self.sort_policy = policy
                        self.__on_policy_changed()

                def on_mouse_pressed_fn(x, y, b, m):
                    if b != 0:
                        return

                    items_sort_policy = self.__items_sort_policy
                    self.__name_sort_options_menu = ui.Menu("Sort Options")
                    with self.__name_sort_options_menu:
                        ui.MenuItem("Sort By", enabled=False)
                        ui.Separator()
                        ui.MenuItem(
                            "New to Old",
                            checkable=True,
                            checked=items_sort_policy == NameColumnSortPolicy.NEW_TO_OLD,
                            checked_changed_fn=partial(
                                on_sort_policy_changed,
                                NameColumnSortPolicy.NEW_TO_OLD
                            ),
                            hide_on_click=False,
                        )
                        ui.MenuItem(
                            "Old to New",
                            checkable=True,
                            checked=items_sort_policy == NameColumnSortPolicy.OLD_TO_NEW,
                            checked_changed_fn=partial(
                                on_sort_policy_changed,
                                NameColumnSortPolicy.OLD_TO_NEW
                            ),
                            hide_on_click=False,
                        )
                        ui.MenuItem(
                            "A to Z",
                            checkable=True,
                            checked=items_sort_policy == NameColumnSortPolicy.A_TO_Z,
                            checked_changed_fn=partial(
                                on_sort_policy_changed,
                                NameColumnSortPolicy.A_TO_Z
                            ),
                            hide_on_click=False
                        )
                        ui.MenuItem(
                            "Z to A",
                            checkable=True,
                            checked=items_sort_policy == NameColumnSortPolicy.Z_TO_A,
                            checked_changed_fn=partial(
                                on_sort_policy_changed,
                                NameColumnSortPolicy.Z_TO_A
                            ),
                            hide_on_click=False
                        )
                    self.__name_sort_options_menu.show()

                self.__drop_down_layout.set_mouse_pressed_fn(on_mouse_pressed_fn)
                self.__drop_down_layout.visible = False
        else:
            self.__name_label_layout.set_mouse_pressed_fn(None)
            with ui.HStack():
                ui.Spacer(width=10)
                ui.Label("Name", name="columnname", style_type_name_override="TreeView.Header")

    def get_type_icon(self, node_type):
        """Convert USD Type to icon file name"""
        icons = StageIcons()
        if node_type in ["DistantLight", "SphereLight", "RectLight", "DiskLight", "CylinderLight", "DomeLight"]:
            return icons.get(node_type, "Light")
        if node_type == "":
            # an empty typename will either be an untyped def/over or a class. Untyped defs are naughty, and overs are
            # hidden in the stage traversal, so Class is the only "valid" type to display
            node_type = "Class"
        return icons.get(node_type, "Prim")

    async def build_widget(self, _, **kwargs):
        self.build_widget_async(_, **kwargs)

    def __get_all_icons_to_draw(self, item: StageItem, item_is_native):
        # Get the node type
        node_type = item.type_name if item != item.stage_model.root else None

        icon_filenames = [self.get_type_icon(node_type)]
        # Get additional icons based on the properties of StageItem
        if item_is_native:
            if item.references:
                icon_filenames.append(StageIcons().get("Reference"))
            if item.payloads:
                icon_filenames.append(StageIcons().get("Payload"))
            if item.instanceable:
                icon_filenames.append(StageIcons().get("Instance"))
            if item.inherits:
                icon_filenames.append(StageIcons().get("Inherited"))
            if item.specializes:
                icon_filenames.append(StageIcons().get("Specialized"))

        return icon_filenames

    def __draw_all_icons(self, item: StageItem, item_is_native, is_highlighted):
        icon_filenames = self.__get_all_icons_to_draw(item, item_is_native)

        # Gray out the icon if the filter string is not in the text
        iconname = "object_icon" if is_highlighted else "object_icon_grey"
        parent_layout = ui.ZStack(width=20, height=20)
        with parent_layout:
            for icon_filename in icon_filenames:
                ui.Image(icon_filename, name=iconname, style_type_name_override="TreeView.Image")

        if item.instance_proxy:
            parent_layout.set_tooltip("Instance Proxy")

    def __build_rename_field(self, item: StageItem, name_labels, parent_stack):
        def on_end_edit(name_labels, field):
            for label in name_labels:
                label.visible = True

            field.visible = False
            self.end_edit_subscription = None

        def on_mouse_double_clicked(button, name_labels, field):
            if button != 0 or item.instance_proxy:
                return

            for label in name_labels:
                label.visible = False

            field.visible = True
            self.end_edit_subscription = field.model.subscribe_end_edit_fn(lambda _: on_end_edit(name_labels, field))

            import omni.kit.app

            async def focus(field):
                await omni.kit.app.get_app().next_update_async()
                field.focus_keyboard()

            asyncio.ensure_future(focus(field))

        field = ui.StringField(item.name_model, identifier="rename_field", visible=False)
        parent_stack.set_mouse_double_clicked_fn(
            lambda x, y, b, _: on_mouse_double_clicked(b, name_labels, field)
        )

        item._ui_widget = parent_stack

    def build_widget_sync(self, _, **kwargs):
        """Build the type widget"""
        # True if it's StageItem. We need it to determine if it's a Root item (which is None).
        model = kwargs.get("stage_model", None)
        item = kwargs.get("stage_item", None)

        if not item:
            item = model.root
            item_is_native = False
        else:
            item_is_native = True

        if not item or not item.stage_model:
            return

        if not item.active and not model.show_inactive_prims:
            return
        
        if item.abstract and not model.show_abstract_prims:
            return

        # If highlighting disabled completley, all the items should be light
        is_highlighted = not self.__highlighting_enabled and not self.__highlighting_text
        if not is_highlighted:
            # If it's not disabled completley
            is_highlighted = item_is_native and item.filtered

        with ui.ZStack(style=WIDGET_STYLES):
            with ui.HStack(enabled=not item.instance_proxy and item.active, spacing=4, height=20):
                # Draw all icons on top of each other
                self.__draw_all_icons(item, item_is_native, is_highlighted)

                value_model = item.name_model
                text = value_model.get_value_as_string()

                stack = ui.HStack()
                name_labels = []

                # We have three different text draw model depending on the column and on the highlighting state
                if item_is_native and model.flat:
                    # Flat search mode. We need to highlight only the part that is is the search field
                    selection_chain = split_selection(text, self.__highlighting_text)
                    labelnames_chain = ["object_name_grey", "object_name"]

                    # Extend the label names depending on the size of the selection chain. Example, if it was [a, b]
                    # and selection_chain is [z,y,x,w], it will become [a, b, a, b].
                    labelnames_chain *= int(math.ceil(len(selection_chain) / len(labelnames_chain)))

                    with stack:
                        for current_text, current_name in zip(selection_chain, labelnames_chain):
                            if not current_text:
                                continue

                            label = ui.Label(
                                current_text,
                                name=current_name,
                                width=0,
                                style_type_name_override="TreeView.Item",
                                hide_text_after_hash=False
                            )

                            name_labels.append(label)

                    if hasattr(item, "_callback_id"):
                        item._callback_id = None
                else:
                    with stack:
                        if item.has_missing_references:
                            name = "object_name_missing"
                        else:
                            name = "object_name" if is_highlighted else "object_name_grey"

                        if item.is_outdated:
                            name = "object_name_outdated"

                        if item.in_session:
                            name = "object_name_live"

                        if item.is_outdated:
                            style_override = "TreeView.Item.Outdated"
                        elif item.in_session:
                            style_override = "TreeView.Item.Live"
                        else:
                            style_override = "TreeView.Item"

                        text = value_model.get_value_as_string()
                        if item.is_default:
                            text += " (defaultPrim)"

                        label = ui.Label(
                            text, hide_text_after_hash=False,
                            name=name, style_type_name_override=style_override
                        )
                        if item.has_missing_references:
                            label.set_tooltip("Missing references found.")

                        name_labels.append(label)

                # The hidden field for renaming the prim
                if item != model.root and not item.instance_proxy:
                    self.__build_rename_field(item, name_labels, stack)
                elif hasattr(item, "_ui_widget"):
                    item._ui_widget = None

            if not item.active:
                with ui.VStack():
                    ui.Spacer(height=6)
                    ui.Image(
                        StageIcons().get("active_off"), name="not_active", style_type_name_override="TreeView.Image",
                        width=14, height=14
                    )

    def rename_item(self, item: StageItem):
        if not item or not hasattr(item, "_ui_widget") or not item._ui_widget or item.instance_proxy:
            return

        item._ui_widget.call_mouse_double_clicked_fn(0, 0, 0, 0)

    def on_stage_items_destroyed(self, items: List[StageItem]):
        for item in items:
            if hasattr(item, "_ui_widget"):
                item._ui_widget = None

    def on_header_hovered(self, hovered):
        self.__drop_down_layout.visible = hovered

    @property
    def sortable(self):
        return True

    @property
    def order(self):
        return -100000

    @property
    def minimum_width(self):
        return ui.Pixel(40)
