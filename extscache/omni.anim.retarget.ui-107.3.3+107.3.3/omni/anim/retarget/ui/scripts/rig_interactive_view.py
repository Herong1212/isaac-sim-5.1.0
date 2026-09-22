# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni
import omni.ui as ui
from omni.anim.retarget.core.scripts.rig import RetargetRig
from omni.anim.retarget.core.scripts.utils import get_selected_joint
from omni.anim.retarget.ui.scripts.rig_tree_view import TreeItemUIContainer

from typing import Tuple
import math
import os

# todo: these should be read from the rig config
IMAGE_X_MARGIN = 10
IMAGE_Y_MARGIN = 10
IMAGE_WIDTH = 407
IMAGE_WIDTH_HALF = 203
IMAGE_HEIGHT = 446
PLACER_WIDTH = 224
PLACER_WIDTH_HALF = 112
PLACER_HEIGHT = 135


class RigTagPin:
    def __init__(self, rig_interactive_view, tag_name, group, pin_x, pin_y, g_offset_x, g_offset_y):
        self._rig_interactive_view = rig_interactive_view
        self._rig = self._rig_interactive_view.rig
        self._joint = self._rig.get_joint(tag_name) if self._rig else ""
        self._name = tag_name
        self._group = group
        selection_size = self._rig.selection_size
        pin_size = self._rig.pin_size
        self.active_pin_color = self._rig.pin_color
        self.inactive_pin_color = 0xFF4ACBDF

        self._x = pin_x - selection_size + g_offset_x
        self._y = pin_y - selection_size + g_offset_y

        tooltip = f"{self._name}: {'Unassigned' if self._joint == '' else self._joint}"

        self._icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/icons"

        with ui.ZStack():
            with ui.Placer(
                name=self._name,
                draggable=False,
                width=selection_size,
                height=selection_size,
                offset_x=pin_x - selection_size + g_offset_x,
                offset_y=pin_y - selection_size + g_offset_y,
            ):
                with ui.ZStack(width=selection_size, height=selection_size,
                               mouse_pressed_fn=self.on_mouse_pressed,
                               tooltip=tooltip):
                    ui.Circle(
                        radius=selection_size - 1,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        visible=True,
                        style={"background_color": 0x000000FF, "border_width": 2,
                               "border_color": 0xFFFABD2D if (self._name == self._rig_interactive_view._selected_tag) else 0xFF625B38,
                               "border_style": "dashed"}
                    )
                    self._active_pin = ui.Circle(
                        radius=pin_size - 2,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        visible=True,
                        style={"background_color": self._rig.pin_color}
                    )

            with ui.Placer(
                draggable=False,
                width=12,
                height=12,
                offset_x=pin_x + selection_size - 5,
                offset_y=pin_y + selection_size - 4
            ):
                ui.Image(f"{self._icon_path}/joint_select_triangle.svg", width=10, height=10,
                         alignment=ui.Alignment.H_CENTER, visible=True)

        pin_active = self._rig.is_tag_mapped(self._name)
        self.set_active(pin_active)

    def on_mouse_pressed(self, x, y, button, modifier):
        # display context menu only if the right button is pressed
        if button == 0:
            self._rig_interactive_view.on_view_tag_selected(self._name)
        else:
            self._rig_interactive_view.show_context_menu(self._name, x, y)

    def set_selected(self, selected):
        self._selected = selected

    def set_active(self, active):
        self._active = active
        if active:
            self._active_pin.style = {"background_color": self.active_pin_color}
        else:
            self._active_pin.style = {"background_color": self.inactive_pin_color}
        self._active_pin.visible = active or self._rig.is_default_tag(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y


class RigTagPinProperties:
    _default_text = "Please select a Pin"

    def __init__(self, rig_interactive_view: "RigInteractiveView", active_pin: RigTagPin, joint: str, tag: str):
        self._rig_interactive_view = rig_interactive_view
        self._rig = self._rig_interactive_view.rig
        self._active_pin = active_pin
        self._value = None

        self._x, self._y = self._fit_within_image_rect(active_pin.x, active_pin.y)
        self._width = 200
        self._height = PLACER_HEIGHT

        self.tag_model = ui.SimpleStringModel(tag)
        self.joint_model = ui.SimpleStringModel(joint)

        self._icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/icons"

        self._remove_button_style = {
            "Button": {"stack_direction": ui.Direction.RIGHT_TO_LEFT},
            "Button.Image": {
                "color": 0xFFFFCC99,
                "image_url": f"{self._icon_path}/clear.svg",
                "alignment": ui.Alignment.RIGHT_CENTER,
            },
            "Button.Label": {"alignment": ui.Alignment.LEFT},
        }

        self._placer = ui.Placer(
            name="RigTagPinPropertiesPlacer",
            draggable=False,
            width=self._width,
            height=0,
            visible=True,
            offset_x=self._x,
            offset_y=self._y,
        )

        with self._placer:
            self._zstack = ui.ZStack(width=200, opaque_for_mouse_events=True)
            with self._zstack:
                # this is the entire rectangle background
                ui.Rectangle(style={"background_color": 0xFF555555})
                with ui.VStack(width=200):
                    self._tag_ui = TreeItemUIContainer()

                    stack = ui.HStack(height=30, width=0)
                    with stack:
                        ui.Spacer(width=8)
                        self._tag_ui.create_label(self.tag_model, stack, self._on_double_click)

                    midline_zstack = ui.ZStack()
                    with midline_zstack:
                        # this rectangle color matches the background to make it look like all one item
                        ui.Rectangle(style={"background_color": 0xFF1F2124})
                        with ui.HStack():
                            self._tag_ui.create_joint_selection(
                                self._rig._skeleton,
                                self.tag_model.as_string,
                                self.joint_model.as_string,
                                self.on_view_joint_modified
                            )

                    ui.Button(
                        "Assign Selected Joint",
                        height=30,
                        image_url="resources/icons/Select_model_64.png", image_width=16, image_height=16,
                        style={"stack_direction": ui.Direction.LEFT_TO_RIGHT},
                        clicked_fn=lambda: self._rig_interactive_view.on_assign_joint(self.tag_model.as_string)
                    )

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def placer(self) -> ui.Placer:
        return self._placer

    def _fit_within_image_rect(self, x: float, y: float) -> Tuple[float, float]:
        result_x = max(IMAGE_X_MARGIN, min(x - PLACER_WIDTH_HALF, IMAGE_WIDTH - PLACER_WIDTH - IMAGE_X_MARGIN))
        if y < IMAGE_WIDTH_HALF:
            result_y = y + IMAGE_Y_MARGIN * 2.0
        else:
            result_y = y - (IMAGE_Y_MARGIN + PLACER_HEIGHT) + 40
        return (result_x, result_y)

    def on_view_joint_modified(self, tag_name, joint_name):
        self._rig.set_joint(tag_name, joint_name, True)

    def on_view_tag_modified(self, old_tag_name, new_tag_name):
        self._rig.rename_tag(old_tag_name, new_tag_name)

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
        self._rig.rename_tag(self._tag_to_be_edited, model.as_string)
        # clear old key name
        self._tag_to_be_edited = ""

    def _on_remove_item(self, model, item):
        """Callback hit when the button to remove an existing item was pressed"""
        self._rig.remove_tag(model.as_string)


class GroupItem(ui.AbstractItem):
    def __init__(self, str):
        super().__init__()
        self.model = ui.SimpleStringModel(str)


class GroupItemModel(ui.AbstractItemModel):

    def __init__(self, group_names):
        super().__init__()
        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(
            lambda a: self._item_changed(None))

        self._items = [
            GroupItem(group_name)
            for group_name in group_names
        ]

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item=None, column_id=0):
        if item is None:
            return self._current_index
        return item.model


class RigInteractiveView:
    def __init__(self, rig: RetargetRig):
        self._rig = rig
        self._image = None
        self._tags = dict()
        self._selected_tag = None
        self._frame = ui.Frame(
            build_fn=self._rebuild_ui,
            width=IMAGE_WIDTH + IMAGE_X_MARGIN * 2,
            height=IMAGE_HEIGHT + IMAGE_Y_MARGIN * 2
        )
        self._context_menu = None
        self._rig_tag_pin_properties = None
        # listen to delegates
        rig.register_tag_added(self.on_tag_added)
        rig.register_tag_removed(self.on_tag_removed)
        rig.register_tag_changed(self.on_tag_modified)
        rig.register_joint_changed(self.on_joint_modified)
        rig.register_tags_cleared(self.on_tags_cleared)
        rig.register_tag_selected(self.on_tag_selected)
        rig.register_skeleton_changed(self.on_skeleton_changed)

    def __del__(self):
        self._image = None
        self._frame = None
        if self._context_menu:
            self._context_menu.clear()
        self._context_menu = None
        if (self._rig):
            # listen to delegates
            self._rig.unregister_tag_added(self.on_tag_added)
            self._rig.unregister_tag_removed(self.on_tag_removed)
            self._rig.unregister_tag_changed(self.on_tag_modified)
            self._rig.unregister_joint_changed(self.on_joint_modified)
            self._rig.unregister_tags_cleared(self.on_tags_cleared)
            self._rig.unregister_tag_selected(self.on_tag_selected)
            self._rig.unregister_skeleton_changed(self.on_skeleton_changed)

    def rebuild(self):
        ui.Frame.rebuild(self._frame)

    def _rebuild_ui(self):
        with ui.ZStack():
            ui.Rectangle(style={"background_color": 0xFF2D2D2D})
            with ui.HStack():
                ui.Spacer(width=IMAGE_X_MARGIN)
                with ui.VStack():
                    ui.Spacer(height=IMAGE_Y_MARGIN)
                    self._image = ui.Image(
                        f"{self._rig.path}/{self._rig.current_group}.map.svg",
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        alignment=ui.Alignment.CENTER,
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        mouse_pressed_fn=self._on_background_clicked_deselect_callback,
                    )
            # OM-42863: Created an overlay, which should be opaque to mouse clicks, but that doesn't appear to work.
            # So we disable the dropdown if there's no skeleton.
            if self._rig.skeleton:
                active_pin = None
                active_tag = ""
                active_joint = ""
                for tag in self._rig.get_active_tags():
                    name = tag["name"]
                    group = tag.get("group", "Body")
                    pin_x, pin_y = tag["pin_xy"]
                    pin = RigTagPin(self, name, group, pin_x + 2, pin_y + 2, IMAGE_X_MARGIN, IMAGE_Y_MARGIN)
                    self._tags[name] = pin
                    if self.get_selected_pin_name() == pin.name:
                        active_pin = pin
                        active_tag = name
                        active_joint = self._rig.get_joint(active_tag) or ""

                if active_pin:
                    # draw this last so it appears above the RigTagPins
                    self._rig_tag_pin_properties = RigTagPinProperties(self, active_pin, joint=active_joint, tag=active_tag)

    def _on_background_clicked_deselect_callback(self, x: float, y: float, button: int, *args):
        """
        Punting here: Since ZStacks don't properly stop mouse clicks from bubbling up,
        scan the higher children and ignore the click if it lands on one of them.
        """
        def distance_to_pin(pin: RigTagPin) -> float:
            return math.sqrt(x * x + y * y)

        def bounds_check() -> bool:
            if not self._rig_tag_pin_properties:
                return False
            placer = self._rig_tag_pin_properties.placer
            if not placer:
                return False

            placer_x = self._image.screen_position_x + placer.offset_x
            placer_y = self._image.screen_position_y + placer.offset_y - IMAGE_Y_MARGIN
            size_x = PLACER_WIDTH
            size_y = PLACER_HEIGHT

            if x < placer_x:
                return False
            if x > (placer_x + size_x):
                return False
            if y < placer_y:
                return False
            if y > (placer_y + size_y):
                return False

            return True

        # check against RigTagPinProperties instance
        if bounds_check():
            return

        if self._rig:
            # check against pins
            active_tags = self._rig.get_active_tags()
            pin_checks = [GroupItem.name for GroupItem in self._tags.values() if distance_to_pin(GroupItem) <= self._rig.selection_size]
            if len(pin_checks):
                return

            # click definitely landed on the image itself.
            self._rig.clear_select()

    def _on_outside_clicked_deselect_callback(self, x: float, y: float, button: int, *args):
        def bounds_check() -> bool:
            if not self._image:
                return False

            image_x = self._image.screen_position_x
            image_y = self._image.screen_position_y

            if x < image_x:
                return False
            if x > (image_x + IMAGE_WIDTH):
                return False
            if y < image_y:
                return False
            if y > (image_y + IMAGE_HEIGHT):
                return False
            return True

        # check against RigTagPinProperties instance
        if bounds_check():
            return

        if self._rig:
            self._rig.clear_select()

    @property
    def rig(self):
        return self._rig

    def show_context_menu(self, tag_name, x, y):
        joint = self._rig.get_joint(tag_name)
        # reset context menu?
        self._context_menu = ui.Menu(
            "Option"
        )
        with self._context_menu:
            ui.MenuItem("Assign Selected Joint", triggered_fn=lambda: self.on_assign_joint(tag_name))
            if joint != "":
                ui.MenuItem("Delete", triggered_fn=lambda: self.delete_tag(tag_name))

        self._context_menu.show_at(x, y)

    def on_assign_joint(self, tag_name):
        joint = get_selected_joint(self._rig.skeleton)
        self._rig.set_joint(tag_name, joint, True)

    def delete_tag(self, tag_name):
        self._rig.set_joint(tag_name, "", True)

    def on_view_tag_selected(self, tag_name):
        self.set_tag_selected(tag_name, True)

    def on_tag_selected(self, tag_name, selected):
        # if self._selected_tag is not None:
        #    self._tags[self._selected_tag].set_selected(False)
        # if I don't have it, I just clear it
        if tag_name in self._tags:
            if selected:
                self._selected_tag = tag_name
            else:
                self._selected_tag = ""
            self._tags[tag_name].set_selected(selected)
        ui.Frame.rebuild(self._frame)

    def get_selected_pin_name(self) -> str:
        if self._selected_tag and self._selected_tag in self._tags:
            return self._selected_tag
        return None

    def set_tag_selected(self, tag_name, active):
        self._rig.set_selected(tag_name, active)

    def on_tag_added(self, tag_name):
        ui.Frame.rebuild(self._frame)

    def on_tag_removed(self, tag_name):
        ui.Frame.rebuild(self._frame)

    def on_tag_modified(self, old_tag_name, new_tag_name):
        ui.Frame.rebuild(self._frame)

    def on_joint_modified(self, tag_name, joint_name):
        ui.Frame.rebuild(self._frame)

    def on_tags_cleared(self):
        for tag in self._tags:
            self._tags[tag].set_active(self._rig.is_tag_mapped(tag))

    def on_skeleton_changed(self, skeleton):
        ui.Frame.rebuild(self._frame)
