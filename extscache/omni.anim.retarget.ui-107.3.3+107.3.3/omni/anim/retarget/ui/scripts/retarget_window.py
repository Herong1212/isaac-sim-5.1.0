# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import functools
from functools import partial
import weakref


import carb
import omni.kit.app
from omni.kit.commands.command import _log_error
import omni.kit.ui
import omni.kit.undo
import omni.stageupdate
import omni.ui as ui
import omni.usd
import omni.timeline
from omni.kit.viewport.utility import frame_viewport_selection
import omni.kit.notification_manager as nm
from omni.anim.retarget.core.scripts.utils import get_forward_up_axis, get_joint_token_from_simple_joint, get_retarget_pose, get_joint_skeleton_token
from omni.anim.retarget.core.scripts.rig import RetargetRig

import omni.kit.widget.context_menu
from omni.kit.widget.context_menu import DefaultMenuDelegate

from .ui_panels import FacingPanel, RetargetPosePanel, post_skeleton_message
from .rig_interactive_view import RigInteractiveView
from .skel_selection_combo import AxisSelection, SkeletonSelection

from pxr import Usd, UsdSkel, Gf, Sdf
import OmniSkelSchema


EXTENSION_NAME = "Animation Retargeting"
EXTENSION_DESC = "Set up animation retarget information"
TITLE_TEXT = "Pick a joint that matches the tag"
TITLE_DESCRIPTION = "This tag is used to create a chain by walking up to the parent from the given joint.  "
WINDOW_MENU = "Window/Animation/Retargeting"
WINDOW_WIDTH = 330
WINDOW_HEIGHT = 700
SUB_WINDOW_HEIGHT = 880
SETTINGS_SHOW_WINDOW = "/exts/omni.anim.retarget.ui/show_window"


__button_styles__ = {
    "Button": {
        "min-width": 76,
    },
    "Button.Label": {},
    "Button::start": {},
    "Button.Label::start": {},
    "Button::stop": {
        "background_color": 0xFF6A6ACB
    },
    "Button.Label::stop": {
        "color": 0xFF24211F
    },
    "Button::disabled": {
    },

    "Button.Label::disabled": {
        "color": 0xFF555555
    },
}

__checkbox_styles__ = {
    "border_radius": 4,
    "border_width": 0,
    "padding": 8,
    "margin_width": 4,
    "margin_height": 4,
}


class RetargetWindow:
    def get_name(self):
        return EXTENSION_NAME

    def get_description(self):
        return EXTENSION_DESC

    def __init__(self, ext_id, stageInfo):
        self._usd_context = omni.usd.get_context()
        self._sub_to_undo_redo()
        self._selection = self._usd_context.get_selection()

        settings = carb.settings.get_settings()
        settings.set_default_bool(SETTINGS_SHOW_WINDOW, False)
        show_window = settings.get_as_bool(SETTINGS_SHOW_WINDOW)
        self._window = ui.Window(EXTENSION_NAME, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                                 visible=show_window, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR)
        self._ext_id = ext_id
        self._ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        self._icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/icons"

        self._rig:RetargetRig = RetargetRig("Human")
        self._rig.register_tag_selected(self._on_tag_selected)
        self._rig.register_tag_added(self._on_tag_added)
        self._rig.register_tag_removed(self._on_tag_removed)
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(WINDOW_MENU, self._on_click, toggle=True, value=show_window)
        # if user close the window, rebuild the menu
        self._window.set_visibility_changed_fn(self._visibility_changed_fn)
        self._window.deferred_dock_in("Property")
        self._docked = True
        self._selected_in_dock = True
        self._window.set_selected_in_dock_changed_fn(self.__selected_in_dock_changed)
        self._window.set_docked_changed_fn(self.__dock_changed)

        # ui elements
        self._rig_tree_view = None
        self._rig_interactive_view = None
        self._stage_info = weakref.ref(stageInfo)
        self._skeleton_combo_box = SkeletonSelection(self._on_select_skeleton_prim, "Select skeleton to configure.", self._stage_info())
        self._facing_up_axis_box = AxisSelection(self._on_up_axis_callback)
        self._facing_forward_axis_box = AxisSelection(self._on_forward_axis_callback)
        self._facing_panel = FacingPanel(self._rig, self._facing_forward_axis_box,
                                         self._facing_up_axis_box, self._ext_id, self.is_window_visible)
        self._auto_setup_button = None
        self._send_to_preview_button = None

        self._initialize_window()

        # stage update function subscription
        stage_update = omni.stageupdate.get_stage_update_interface()
        self.stage_subscription = stage_update.create_stage_update_node(
            "omni.anim.retarget." + str(__class__),
            on_attach_fn=functools.partial(__class__._on_attach, weakref.proxy(self)),
            on_detach_fn=functools.partial(__class__._on_detach, weakref.proxy(self)),
            on_update_fn=functools.partial(__class__._on_update, weakref.proxy(self))
        )

        # initial axis visibility
        self._facing_up_axis_box._current_index.set_value(1)    # y
        self._facing_forward_axis_box._current_index.set_value(2)   # z

    def __del__(self):
        self.stage_subscription = None
        self._rig.unregister_tag_selected(self._on_tag_selected)
        self._rig.unregister_tag_added(self._on_tag_added)
        self._rig.unregister_tag_removed(self._on_tag_removed)
        self._unsub_to_undo_redo()
        self._usd_context = None
        self._rig = None
        self._rig_tree_view = None
        self._rig_interactive_view = None
        self._skeleton_combo_box = None
        self._retarget_menu = None
        self._window = None
        self._menu = None
        self._select_label = None
        self._type_label = None
        self._select_rect = None
        self._retarget_pose_panel = None
        self._stage_info = None

    def destroy(self):
        self._window.destroy()

    def rebuild(self):
        self._window.frame.rebuild()

    def _on_attach(self, stage_id, meters_per_unit):
        pass

    # Called when a USD map is closed
    def _on_detach(self):
        pass

    def _on_update(self, t, dt):
        self._retarget_pose_panel.on_update(t, dt)

        # if recommend tag is missing
        if self._rig.skeleton is None or self._rig.is_default_tag_mapped():
            self._warning_mark.visible = False
        else:
            self._warning_mark.visible = True

        self._auto_setup_button.enabled = bool(self._rig.skeleton)

    def _on_click(self, *args):
        self._window.visible = not self._window.visible

    # callback functions for camera tool under the Animation menu
    def _visibility_changed_fn(self, visible):
        omni.kit.ui.get_editor_menu().set_value(WINDOW_MENU, visible)

    def __selected_in_dock_changed(self, is_selected):
        self._selected_in_dock = is_selected

    def __dock_changed(self, is_docked):
        self._docked = is_docked

    def _on_select_skeleton_prim(self, index, skeleton_path):
        if index > 0:
            skeleton_prim = self._usd_context.get_stage().GetPrimAtPath(skeleton_path)
            if (skeleton_prim):
                skeleton = UsdSkel.Skeleton(skeleton_prim)
        else:
            skeleton = None

        if skeleton:
            carb.log_info("currently selected skeleton : " + skeleton.GetPrim().GetPath().pathString)
        else:
            carb.log_info("skeleton is none")

        # todo: need to make sure we don't override previous set up
        self._rig.set_skeleton(skeleton)

        if skeleton:
            # if error exists, return, we won't support this
            if self._rig.should_run_auto_setup():
                self._auto_setup()

            # set axis info
            forward_axis, up_axis = get_forward_up_axis(skeleton)
            self._facing_forward_axis_box.set_value(forward_axis)
            self._facing_up_axis_box.set_value(up_axis)
            if self._facing_panel:
                self._facing_panel.set_up_axis(up_axis)
                self._facing_panel.set_forward_axis(forward_axis)

            # check error
            self._check_error(skeleton)

            # clear the help label
            self._select_label.visible = False
            self._type_label.visible = True
            self._select_rect.visible = False
            # self._hs_simple_advanced_combo.visible = True
            # self._zs_optionals.visible = True

        else:
            # restore the help label
            self._select_label.visible = True
            self._type_label.visible = False
            self._select_rect.visible = True
            # self._hs_simple_advanced_combo.visible = False
            # self._zs_optionals.visible = False

        self._update_button_styles()

    def _check_error(self, skeleton):
        # if root is not identity, we have issue
        transforms = get_retarget_pose(skeleton)
        root_translation = transforms[0].ExtractTranslation()
        if not Gf.IsClose(root_translation, Gf.Vec3d(0.0), 0.001):
            error_message = (
                "Retarget Warning: Root translation should be identity ("
                + str(skeleton.GetPrim().GetPath())
                + ") [" + str(root_translation) + "]"
            )
            nm.post_notification(error_message, status=nm.NotificationStatus.WARNING, duration=7)
            carb.log_warn(error_message)
            return True
        return False

    def _on_up_axis_callback(self, index, up_axis):
        if self._rig.skeleton:
            self._rig.set_up_axis(up_axis)
        if self._facing_panel:
            self._facing_panel.set_up_axis(up_axis)

    def _on_forward_axis_callback(self, index, forward_axis):
        if self._rig.skeleton:
            self._rig.set_forward_axis(forward_axis)
        if self._facing_panel:
            self._facing_panel.set_forward_axis(forward_axis)

    def _auto_setup(self):
        # check identity first, but still let it pass
        self._check_error(self._rig.skeleton)

        success = self._rig.auto_setup(auto_posing=self._rig.should_run_auto_setup())
        if success:
            message = (
                "Auto Set up : Successfully added retarget set up  for ("
                + str(self._rig.skeleton.GetPrim().GetPath())
                + ")"
            )
            nm.post_notification(message, status=nm.NotificationStatus.INFO, duration=7)
            carb.log_info(message)
        else:
            message = (
                "Error : Automatic retarget set up has failed for ("
                + str(self._rig.skeleton.GetPrim().GetPath())
                + "). Please check the console for more information."
            )
            nm.post_notification(message, status=nm.NotificationStatus.WARNING, duration=7)
            _log_error(message)

            # go back to default setting
            self._rig.set_up_axis("Y")
            self._rig.set_forward_axis("Z")

        self._rebuild_window()
        self._skeleton_combo_box.select_skeleton(self._rig.skeleton.GetPrim().GetPath())
        return success

    def _send_to_preview(self):
        # calling the above auto-setup now, with the checks in place
        # to not overwrite existing retarget poses
        self._auto_setup()
        prim_path = str(self._rig.skeleton.GetPrim().GetPath())

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)

        if not prim.IsA(UsdSkel.Root) and prim.GetParent().IsA(UsdSkel.Root):
            prim = prim.GetParent()

        omni.kit.commands.execute("AnimationPreviewCommand", prim_path=str(prim.GetPath()))

    def _on_clear_tags(self):
        self._rig.clear()
        self._rig.reset_tags()

    def _on_save_pose(self):
        self._rig.save_retarget_pose()
        post_skeleton_message(self._rig.skeleton, "Apply Pose", "current pose is saved to retarget pose")

    def _is_timeline_active(self):
        if omni.timeline.get_timeline_interface().is_stopped():
            return False

        return True

    def _on_load_pose(self):
        if self._is_timeline_active():
            post_skeleton_message(self._rig.skeleton, "View Pose", "stop playing to view the retarget pose", nm.NotificationStatus.WARNING)
            return

        self._rig.load_retarget_pose()
        post_skeleton_message(self._rig.skeleton, "View Pose", "currently you're viewing retarget pose")

    def _on_unload_pose(self):
        if self._is_timeline_active():
            post_skeleton_message(self._rig.skeleton, "Hide Pose", "stop playing to view the retarget pose", nm.NotificationStatus.WARNING)
            return

        self._rig.unload_retarget_pose()
        post_skeleton_message(self._rig.skeleton, "Hide Pose", "currently you're viewing animation mode")

    def _on_clear_pose(self):
        if self._is_timeline_active():
            post_skeleton_message(self._rig.skeleton, "Reset Pose", "stop playing to clear the retarget pose", nm.NotificationStatus.WARNING)
            return

        # once reset, we should show it
        self._rig.reset_retarget_pose()
        post_skeleton_message(self._rig.skeleton, "Reset Pose", "reset retarget pose to default bind pose")

    def _on_assign_selected(self):
        # find currently selected joint
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        selection = usd_context.get_selection()
        selected_prims = selection.get_selected_prim_paths()
        skeleton = None
        if len(selected_prims) > 0:
            prim = stage.GetPrimAtPath(selected_prims[0])
            if OmniSkelSchema.OmniJoint(prim):
                selected_skeleton, joint_token = get_joint_skeleton_token(prim)
            elif UsdSkel.Skeleton(prim):
                skeleton = UsdSkel.Skeleton(prim)
            elif UsdSkel.Root(prim):
                for child in Usd.PrimRange(prim):
                    if UsdSkel.Skeleton(child):
                        skeleton = UsdSkel.Skeleton(child)
            elif UsdSkel.BindingAPI(prim):
                paths = UsdSkel.BindingAPI(prim).GetSkeletonRel().GetTargets()
                if len(paths) > 0:
                    skel_prim = prim.GetStage().GetPrimAtPath(paths[0])
                    if UsdSkel.Skeleton(skel_prim):
                        skeleton = UsdSkel.Skeleton(skel_prim)
        if skeleton:
            self._skeleton_combo_box.select_skeleton(skeleton.GetPrim().GetPath())

    def open_window(self):
        self._window.visible = True
        self._window.focus()

    def is_window_visible(self):
        return self._window.visible and (self._selected_in_dock if self._docked else True)

    def get_skeleton(self):
        return self._rig.skeleton

    def set_skeleton(self, skel_prim_path: str):
        self._skeleton_combo_box.select_skeleton(Sdf.Path(skel_prim_path))

    def _on_focus_skeleton(self):
        self.select_skeleton_viewport()

    def select_skeleton_viewport(self):
        skeleton = self._rig.skeleton
        if skeleton:
            self.select_prim_in_viewport(skeleton.GetPrim(), False, True)

    def select_prim_in_viewport(self, prim, select_skel_root, focus):
        if prim:
            self._selection.set_selected_prim_paths([prim.GetPath().pathString], True)

        prim_to_select = prim
        if prim_to_select:
            if select_skel_root:
                parent = prim.GetParent()
                while parent:
                    if parent.GetTypeName() == "SkelRoot":
                        prim_to_select = parent
                        break
                    parent = parent.GetParent()

            self._selection.set_selected_prim_paths([prim_to_select.GetPath().pathString], True)
            if focus:
                frame_viewport_selection(force_legacy_api=True)

    def _process_usd_change(self, objects, stage):
        # We only care about deletion and rename/move in the context stage
        context_stage = omni.usd.get_context().get_stage()
        if context_stage == stage:
            paths = objects.GetResyncedPaths()
            if not len(paths):
                return

            if len(paths) == 2:
                # Rename operation
                carb.log_error("NEXT")
                pass

            obj_path = str(paths[0])
            if "." in obj_path:
                # property change, not object change
                return

    def _force_enable_secondary_groups(self):
        # Request: remove Optionals menu and allow for all tags to be drawn
        if self._rig:
            for group in "Head", "Hands":
                self._rig.enable_secondary_group(group)

    def _rebuild_window(self):
        self._force_enable_secondary_groups()
        if self._rig_interactive_view:
            self._rig_interactive_view.rebuild()
            # set axis info
            forward_axis, up_axis = get_forward_up_axis(self._rig.skeleton)
            self._facing_forward_axis_box.set_value(forward_axis)
            self._facing_up_axis_box.set_value(up_axis)

    def _build_command_bar(self):
        self._command_bar_layout = ui.HStack(
            height=40,
            width=ui.Fraction(1),
            style={
                "margin": 4,
                "alignment": ui.Alignment.LEFT,
            },
        )

        with self._command_bar_layout:
            ui.Spacer(width=30)

            self._facing_panel._build_facing()

            ui.Spacer(width=ui.Fraction(0.6))

            self._auto_setup_button = ui.Button(
                "Retarget",
                clicked_fn=self._auto_setup,
                width=80,
                height=30,
            )

            self._send_to_preview_button = ui.Button(
                "Preview",
                clicked_fn=self._send_to_preview,
                width=80,
                height=30,
            )

            self._update_button_styles()

    def _update_button_styles(self):
        has_skeleton = bool(self._rig.skeleton)
        self._send_to_preview_button.visible = \
            omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.anim.retarget.preview")

        enabled_button_style = {
            "padding": 4,
            "alignment": ui.Alignment.H_CENTER,
            "min-width": 80,
            "min-height": 30,
            "max-width": 80,
            "max-height": 30,
            "Button": {},
            "Button.Label": {},
            "Button::start": {},
            "Button.Label::start": {},
            "Button::stop": {
                "background_color": 0xFF6A6ACB
            },
        }

        disabled_button_style = {"color": 0xFF999999}
        disabled_button_style.update(enabled_button_style)
        button_style = enabled_button_style if has_skeleton else disabled_button_style

        for button in self._auto_setup_button, self._send_to_preview_button:
            if button:
                button.enabled = has_skeleton
                button.style   = button_style

    def _build_rig_bar(self):
        with ui.VStack():
            ui.Spacer()
            with ui.HStack(name="Rig Bar Stack", height=30):
                self._type_label = ui.Label(
                    # This is "Human", currently, but could change
                    self._rig.rig_name,
                    style={
                        "font_size": 36,
                        # "alignment": ui.Alignment.RIGHT_BOTTOM,
                        "alignment": ui.Alignment.RIGHT,
                        "margin": 0,
                    }
                )
                self._type_label.visible = False

                ui.Spacer(width=12)
            # pad out the bottom
            ui.Spacer(height=12)

    def _initialize_window(self):
        """
        Main entry point for the whole UI
        """
        self._retarget_menu = None
        self._rig_interactive_view = None
        self._rig_tree_view = None
        self._skeleton_combo_box_ui = None
        self._scrollframe = None

        self._force_enable_secondary_groups()

        with self._window.frame:
            self._scrollframe = ui.ScrollingFrame(
                width=ui.Percent(100),
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED
            )
            with self._scrollframe:
                with ui.VStack(height=0, width=ui.Percent(100)):
                    with ui.VStack(height=ui.Percent(100)):
                        ui.Spacer(height=5)
                        # Skeleton Bar
                        with ui.HStack(style={"alignment": ui.Alignment.LEFT_CENTER}):
                            ui.Spacer(width=5)
                            ui.Label("Skeleton", width=30, style={"font_size": 18.0})
                            with ui.VStack(width=20):
                                ui.Spacer(height=8)
                                self._warning_mark = ui.Image(f"{self._icon_path}/warning_dark.svg",
                                                              width=15, height=15, alignment=ui.Alignment.BOTTOM,
                                                              visible=False, tooltip="Yellow joints must be assigned for proper retargeting")
                            with ui.VStack(width=ui.Fraction(1)):
                                ui.Spacer(height=5)
                                self._skeleton_combo_box_ui = ui.ComboBox(self._skeleton_combo_box)
                            self._assign_skeleton_button = ui.Button(
                                "",
                                style={
                                    "Button": {
                                        "stack_direction": ui.Direction.TOP_TO_BOTTOM
                                    },
                                    "Button.Image": {
                                        "image_url": "resources/glyphs/toolbar_select_models.svg",
                                        "alignment": ui.Alignment.CENTER,
                                    },
                                    "Button.Label": {"alignment": ui.Alignment.CENTER},
                                },
                                width=32,
                                height=32,
                                clicked_fn=self._on_assign_selected,
                                tooltip="Assign skeleton from selection",
                            )
                            self._assign_skeleton_button.identifier = "assign_skeleton_button"
                            ui.Button(
                                "",
                                style={
                                    "Button": {
                                        "stack_direction": ui.Direction.TOP_TO_BOTTOM
                                    },
                                    "Button.Image": {
                                        "image_url": f"{self._icon_path}/focus.svg",
                                        "alignment": ui.Alignment.CENTER,
                                    },
                                    "Button.Label": {"alignment": ui.Alignment.CENTER},
                                },
                                width=32,
                                height=32,
                                clicked_fn=self._on_focus_skeleton,
                                tooltip="Focus on selected skeleton"
                            )
                        self._build_command_bar()

                        with ui.VStack():
                            with ui.ZStack(mouse_pressed_fn=self._on_outside_clicked_deselect_callback):
                                ui.Rectangle(style={"background_color": 0xFF2D2D2D})
                                with ui.HStack():
                                    ui.Spacer()
                                    self._rig_interactive_view = RigInteractiveView(self._rig)
                                    ui.Spacer()
                                self._select_rect = ui.Rectangle(style={"background_color": 0xAA000000})
                                self._select_label = ui.Label(
                                    "Select skeleton to configure.",
                                    style={
                                        "font_size": 36,
                                        "alignment": ui.Alignment.CENTER
                                    }
                                )

                                self._build_rig_bar()

                            with ui.VStack(height=10, style={"alignment": ui.Alignment.H_CENTER}):
                                ui.Separator()
                            self._retarget_pose_panel = RetargetPosePanel(
                                self._rig,
                                self._on_load_pose,
                                self._on_unload_pose,
                                self._on_clear_pose,
                                self._on_save_pose,
                                self._stage_info()
                            )

    def _on_simple_advanced_combo_changed(self, model, *args):
        selected_mode = model.get_item_value_model().get_value_as_int()
        if selected_mode == 0:
            self._rig.disable_secondary_group("Hands")
        else:
            self._rig.enable_secondary_group("Hands")

    def _show_optionals_context_menu(self, x: float, y: float, button: int, *args):
        if not button == 0:     # right mouse button only
            return

        # setup objects, this dictionary passed to all functions
        objects = {
            "menu_xpos": x,
            "menu_ypos": y,
        }

        head_menu_data = {
            "name": "Head",
            "checked_fn": partial(self._is_group_active, "Head"),
            "onclick_fn": partial(self._on_show_optionals_cb, "Head")
        }

        if not self._is_group_complete("Head"):
            head_menu_data["glyph"] = f"{self._icon_path}/warning_dark.svg"

        hands_menu_data = {
            "name": "Hands",
             "checked_fn": partial(self._is_group_active, "Hands"),
             "onclick_fn": partial(self._on_show_optionals_cb, "Hands")
        }

        if not self._is_group_complete("Hands"):
            hands_menu_data["glyph"] = f"{self._icon_path}/warning_dark.svg"

        menu_list = [
            head_menu_data,
            hands_menu_data,
        ]

        class MenuDelegate(DefaultMenuDelegate):
            def get_parameters(self, name, kwargs):
                if name == "tearable":
                    kwargs[name] = False

        # show menu
        omni.kit.widget.context_menu.get_instance().show_context_menu(
            "My test context menu",
            objects=objects,
            menu_list=menu_list,
            delegate=MenuDelegate()
        )

    # show_fn functions
    def is_prim_selected(self, objects: dict):
        return bool(objects["prim_list"])

    def _is_group_complete(self, group: str, *args) -> bool:
        """
        Return true if all tags in the group have been assigned joints.
        """
        group_tags = self._rig.get_tags_by_group(group)
        valid_tags = [x for x in group_tags if not x.joint == ""]
        return len(valid_tags) == len(group_tags)

    def _is_group_active(self, group: str, *args) -> bool:
        return group in self._rig.get_active_groups()

    def _on_show_optionals_cb(self, group_name: str, object: dict, *args):
        """
        Main callback for the optionals context menu.
        Used through partial().
        """
        if self._rig.is_group_enabled(group_name):
            self._rig.disable_secondary_group(group_name)
        else:
            self._rig.enable_secondary_group(group_name)

    def _on_outside_clicked_deselect_callback(self, x: float, y: float, button: int, *args):
        if self._rig_interactive_view:
            self._rig_interactive_view._on_outside_clicked_deselect_callback(x, y, button)

    def _on_tag_selected(self, tag_name, selected):
        # find the joint, and select it in the viewport
        joint_name = self._rig.get_joint(tag_name)
        # get full path from the joint_name
        skeleton = self._rig.skeleton
        if skeleton and joint_name != "":
            try:
                joint_token = get_joint_token_from_simple_joint(skeleton, joint_name)
                joint_path = skeleton.GetPrim().GetPath().AppendPath(joint_token)
                joint_prim = self._usd_context.get_stage().GetPrimAtPath(joint_path)
                if joint_prim:
                    self.select_prim_in_viewport(joint_prim, False, False)
            except Exception:
                pass

    def _on_tag_added(self, tag_name):
        self._rig_tree_view._refresh(self._rig.skeleton)

    def _on_tag_removed(self, tag_name):
        self._rig_tree_view._refresh(self._rig.skeleton)

    def _undo_redo_on_change(self, cmds):
        commands = ["SetSkeletonJointTagPairCommand", "SetSkeletonTagsCommand", "SetSkeletonUpForwardAxis",
                    "AutoSetupRetargetCommand", "ClearRetargetTagsCommand"]

        # this is called anytime this command is executed whether undo or redo or just plain execution
        # so this interfere with any addition or deletion of tags from UI since we have UI model Rig vs USD data
        # so we use this flag to differentiate UI execution vs undo or any other execution
        if not self._rig.executing:
            if any(name in commands for name in cmds):
                self._rig.refresh_tags()
                self._rebuild_window()

    def _sub_to_undo_redo(self):
        omni.kit.undo.subscribe_on_change(self._undo_redo_on_change)

    def _unsub_to_undo_redo(self):
        omni.kit.undo.unsubscribe_on_change(self._undo_redo_on_change)
