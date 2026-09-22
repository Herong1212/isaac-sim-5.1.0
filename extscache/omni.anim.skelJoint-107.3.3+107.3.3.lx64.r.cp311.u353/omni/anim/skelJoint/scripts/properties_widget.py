# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.usd
import omni.ui as ui
from pxr import Sdf, Usd, UsdSkel, Tf
import OmniSkelSchema, RetargetingSchema
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
from omni.kit.window.property.templates import HORIZONTAL_SPACING
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutProperty
from omni.kit.property.usd.relationship import RelationshipTargetPicker
from omni.kit.property.usd import PrimPathWidget
import omni.kit.notification_manager as nm

from .utils import *
from . import styles

from enum import Enum


class JointShapeType(Enum):
    BOX = 0
    SPHERE = 1
    CAPSULE = 2


class OmniSkelProperties:
    def __init__(self):
        self.on_startup()

    def on_startup(self):
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            self._omni_skel_widget = OmniSkelPropertiesWidget("Animation and Pose Modes")
            w.register_widget(
                "prim",
                "SkelJoint",
                self._omni_skel_widget
            )

    def on_shutdown(self):
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            if self._omni_skel_widget is not None:
                w.unregister_widget("prim", "SkelJoint")
                self._omni_skel_widget.destroy()
                self._omni_skel_widget = None


class OmniSkelPropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title: str):
        super().__init__(title, collapsed=False)
        self._add_button_menus = []
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "SkelJoint/Add Joint Limits",
                show_fn=self.on_show_menu_add_joint_limits,
                onclick_fn=self.on_click_menu_add_joint_limits,
            )
        )
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "SkelJoint/Remove Joint Limits",
                show_fn=self.on_show_menu_remove_joint_limits,
                onclick_fn=self.on_click_menu_remove_joint_limits,
            )
        )
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "SkelJoint/Joint Box Shape",
                show_fn=self.on_show_menu_add_shape,
                onclick_fn=lambda payload: self.on_click_menu_add_shape(payload, JointShapeType.BOX),
            )
        )
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "SkelJoint/Joint Sphere Shape",
                show_fn=self.on_show_menu_add_shape,
                onclick_fn=lambda payload: self.on_click_menu_add_shape(payload, JointShapeType.SPHERE),
            )
        )
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "SkelJoint/Joint Capsule Shape",
                show_fn=self.on_show_menu_add_shape,
                onclick_fn=lambda payload: self.on_click_menu_add_shape(payload, JointShapeType.CAPSULE),
            )
        )
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "Animation/Skeletal Animation",
                show_fn=self.on_show_menu_add_animation,
                onclick_fn=self.on_click_menu_add_animation
            )
        )
        self._rest_apply_button_animation_mode = None
        self._retarget_apply_button = None
        self._rest_apply_button = None
        self._rel_picker = None
        self._anim_source_widget_items = []

        self._skel_notice = None

        self._skel_prim = None

    def destroy(self):
        from omni.kit.property.usd import PrimPathWidget
        for menu in self._add_button_menus:
            PrimPathWidget.remove_button_menu_entry(menu)
        self._add_button_menus = []
        self._rest_apply_button_animation_mode = None
        self._retarget_apply_button = None
        self._rest_apply_button = None
        if self._rel_picker is not None:
            self._rel_picker.clean()
            self._rel_picker = None

    # joint limits
    def on_show_menu_add_joint_limits(self, objects: dict):
        """
        When a prim is right-clicked, show joint-limit menus if prim
        is a joint and doesn't alread have limit attributes
        """
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        has_joint = False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if prim.IsA(OmniSkelSchema.OmniJoint):
                has_joint = True
                # possible bug -> even if one of the selected joints already has limits, we don't display the manu at all
                if prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI):
                    return False
        if has_joint:  # has joint and none of them applied JointLimitsAPI
            return True
        return False

    def on_click_menu_add_joint_limits(self, payload: PrimSelectionPayload):
        """
        Add joint limits attributes to selected prims if
        they're joints and don't already have limits
        """
        if payload is None:
            return Sdf.Path.emptyPath
        stage = payload.get_stage()
        if stage is None:
            stage = omni.usd.get_context().get_stage()
        prim_paths = payload.get_paths()
        target_paths = []
        for path in prim_paths:
            prim = stage.GetPrimAtPath(path)
            if prim and prim.IsA(OmniSkelSchema.OmniJoint):
                if not prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI):
                    target_paths.append(path)
        if len(target_paths) > 0:
            omni.kit.commands.execute(
                "ApplyOmniSkelJointLimitsAPICommand",
                paths=target_paths,
                select_prim=True,
                stage=stage
            )
        return target_paths

    def on_show_menu_remove_joint_limits(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        has_joint = False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if prim.IsA(OmniSkelSchema.OmniJoint):
                has_joint = True
                # possible bug -> even if one of the selected joints doesn't have limits, we don't display the manu at all
                if not prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI):
                    return False
        if has_joint:  # has joint and all of them applied JointLimitsAPI
            return True
        return False

    def on_click_menu_remove_joint_limits(self, payload: PrimSelectionPayload):
        if payload is None:
            return Sdf.Path.emptyPath
        stage = payload.get_stage()
        if stage is None:
            stage = omni.usd.get_context().get_stage()
        prim_paths = payload.get_paths()
        target_paths = []
        for path in prim_paths:
            prim = stage.GetPrimAtPath(path)
            if prim and prim.IsA(OmniSkelSchema.OmniJoint):
                if prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI):
                    target_paths.append(path)
        if len(target_paths) > 0:
            omni.kit.commands.execute("RemoveOmniSkelJointLimitsAPICommand", paths=target_paths, stage=stage)
        return target_paths

    # shape
    def on_show_menu_add_shape(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if prim.IsA(OmniSkelSchema.OmniJoint):
                return True
        return False

    def on_click_menu_add_shape(self, payload: PrimSelectionPayload, shape_type: JointShapeType):
        if payload is None:
            return Sdf.Path.emptyPath
        stage = payload.get_stage()
        if stage is None:
            stage = omni.usd.get_context().get_stage()
        prim_paths = payload.get_paths()
        target_paths = []
        shape_path_dict = {
            JointShapeType.BOX: "BoxShape",
            JointShapeType.SPHERE: "SphereShape",
            JointShapeType.CAPSULE: "CapsuleShape",
        }
        for path in prim_paths:
            prim = stage.GetPrimAtPath(path)
            if prim and prim.IsA(OmniSkelSchema.OmniJoint):
                shape_path = prim.GetPath().AppendPath(shape_path_dict[shape_type])
                target_paths.append(omni.usd.get_stage_next_free_path(stage, shape_path, False))
        if shape_type == JointShapeType.BOX:
            omni.kit.commands.execute("CreateOmniSkelJointBoxShapeCommand", paths=target_paths, select_prim=True, stage=stage)
        elif shape_type == JointShapeType.SPHERE:
            omni.kit.commands.execute("CreateOmniSkelJointSphereShapeCommand", paths=target_paths, select_prim=True, stage=stage)
        elif shape_type == JointShapeType.CAPSULE:
            omni.kit.commands.execute("CreateOmniSkelJointCapsuleShapeCommand", paths=target_paths, select_prim=True, stage=stage)
        return target_paths

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            if prim.IsA(OmniSkelSchema.OmniSkelBaseType) or prim.HasAPI(OmniSkelSchema.OmniSkelBaseAPI) or prim.IsA(OmniSkelSchema.OmniJoint):
                return True
        return False

    def get_additional_kwargs(self, ui_prop: UsdPropertyUiEntry):
        additional_label_kwargs = None
        additional_widget_kwargs = None
        joint_limit_attr_list = OmniSkelSchema.OmniJointLimitsAPI.GetSchemaAttributeNames()
        joint_list = OmniSkelSchema.OmniJoint.GetSchemaAttributeNames()
        if ui_prop.attr_name in joint_limit_attr_list:
            additional_widget_kwargs = {"model_kwargs": {"auto_target_session_layer_def": False}}
        if ui_prop.attr_name in joint_list:
            additional_widget_kwargs = {"enabled": False}
        if ui_prop.attr_name == "skel:animationSource":
            return None, {"target_picker_filter_type_list": [UsdSkel.Animation], "targets_limit": 1}
        return additional_label_kwargs, additional_widget_kwargs

    def on_show_menu_add_animation(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if not prim.HasAPI(UsdSkel.BindingAPI) and prim.IsA(UsdSkel.Skeleton):
                return True
        return False

    def on_click_menu_add_animation(self, payload: PrimSelectionPayload):
        if payload is None:
            return Sdf.Path.emptyPath
        payload_paths = payload.get_paths()
        omni.kit.commands.execute("ApplySkelBindingAPICommand", paths=payload_paths)


    def _on_reset_to_binding(self):
        skeleton = UsdSkel.Skeleton(self._skel_prim)
        (t, r, s, ro) = get_bind_poses(skeleton)
        omni.kit.commands.execute("SetJointPosesCommand", skeleton_path = self._skel_prim.GetPath(), stage = self._skel_prim.GetStage(), translations = t, rotations = r, scales = s, rotation_orders = ro)

    def _on_apply_joint_retarget_pose_to_skeleton(self):
        anchor_prim = self._get_prim(self._payload[-1])
        skel_prim = Usd.Prim()
        if anchor_prim.IsA(UsdSkel.Skeleton):
            skel_prim = anchor_prim
        if skel_prim:
            omni.kit.commands.execute("ApplyJointRetargetPoseToSkeletonCommand", skeleton_path=skel_prim.GetPath())

    def _on_apply_joint_rest_pose_to_skeleton(self):
        anchor_prim = self._get_prim(self._payload[-1])
        skel_prim = Usd.Prim()
        if anchor_prim.IsA(UsdSkel.Skeleton):
            skel_prim = anchor_prim
        if skel_prim:
            omni.kit.commands.execute("ApplyJointRestPoseToSkeletonCommand", skeleton_path=skel_prim.GetPath())

    def _customize_props_layout(self, props):
        anchor_prim = self._get_prim(self._payload[-1])
        self._stage = anchor_prim.GetStage()

        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            if anchor_prim.IsA(UsdSkel.Skeleton):
                self._skel_prim = anchor_prim
                self._create_skel_widget()
            else:
                CustomLayoutProperty("retargetTranslation", "Retarget Translation")
                CustomLayoutProperty("retargetRotation", "Retarget Rotation")
                CustomLayoutProperty("retargetScale", "Retarget Scale")
                CustomLayoutProperty("restTranslation", "Rest Translation")
                CustomLayoutProperty("restRotation", "Rest Rotation")
                CustomLayoutProperty("restScale", "Rest Scale")
                CustomLayoutProperty("bindTranslation", "Bind Translation")
                CustomLayoutProperty("bindRotation", "Bind Rotation")
                CustomLayoutProperty("bindScale", "Bind Scale")
                CustomLayoutProperty("swingHorizontalAngle", "Swing H")
                CustomLayoutProperty("swingVerticalAngle", "Swing V")
                CustomLayoutProperty("twistMaximumAngle", "Twist Max")
                CustomLayoutProperty("twistMinimumAngle", "Twist Min")
                CustomLayoutProperty("axis", "Axis")
                CustomLayoutProperty("radius", "Radius")
                CustomLayoutProperty("height", "Height")
                CustomLayoutProperty("size", "Size")
                CustomLayoutProperty("offsetRotation", "Offset Rotation")
                CustomLayoutProperty("enabled")

        return frame.apply(props)

    def _create_skel_widget(self):
        with ui.VStack(spacing=HORIZONTAL_SPACING):
            with ui.HStack(spacing=HORIZONTAL_SPACING * 2):
                self.skel_mode_img = ui.Image(width=150, style=styles.SKEL_MODE_ANIM_STYLE)
                with ui.VStack(spacing=HORIZONTAL_SPACING):
                    self._mode_radio_col = ui.RadioCollection()
                    self._mode_radio_col.model.add_value_changed_fn(lambda m: self._on_skel_transform_mode_change(m))

                    # Animation Pose
                    # -------------------------------------------------------------------------------------
                    with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                        self._create_colored_box(color=styles.COLORS["GREEN"])
                        self._anim_radio_btn = self._create_radio_btn(
                            name="Animation",
                            collection=self._mode_radio_col,
                        )
                        self._anim_radio_btn.identifier = "anim_radio_btn"

                    # Animation target
                    with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                        self._create_animation_source_field()

                    # Retarget Pose
                    # -------------------------------------------------------------------------------------
                    if self._skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                        # ui.Label("No ControlRigAPI found!")
                        with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                            self._create_colored_box(color=styles.COLORS["PURPLE"])
                            self._retarget_radio_btn = self._create_radio_btn(
                                name="Retarget Pose",
                                collection=self._mode_radio_col,
                            )
                            self._retarget_radio_btn.identifier = "retarget_radio_btn"

                            # save, copy, paste buttons
                            with ui.HStack(spacing=2, width=88):
                                self._save_retarget_btn = ui.Button(
                                    height=24,
                                    style=styles.SAVE_BTN_STYLE,
                                    clicked_fn=self._on_save_retarget_pose,
                                    tooltip="Set current character pose as its Retarget pose."
                                )
                                self._save_retarget_btn.identifier = "save_retarget_btn"
                                ui.Spacer(width=6)
                                self._revert_retarget_btn = ui.Button(
                                    height=24,
                                    style=styles.REVERT_BTN_STYLE,
                                    clicked_fn=self._on_revert_retarget_pose,
                                    tooltip="Revert current character pose to its last saved Retarget pose."
                                )
                                self._revert_retarget_btn.identifier = "revert_retarget_btn"
                            ui.Spacer()

                            # reset button
                            with ui.HStack(spacing=0, width=26):
                                self._reset_retarget_btn = ui.Button(
                                    style=styles.RESET_BTN_STYLE,
                                    clicked_fn=self._on_reset_retarget_pose,
                                    tooltip="Sets current character pose to its ititial Bind pose."
                                )
                                self._reset_retarget_btn.identifier = "reset_retarget_btn"

                            ui.OffsetLine(self._revert_retarget_btn, self._reset_retarget_btn, width=0, bound_offset=2, style={"color": styles.COLORS["GREY"]})
                    else:
                        # add an invisible radio button for retargetting so radio collection indices won't break
                        with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                            self._create_radio_btn(name="Retarget Pose", collection=self._mode_radio_col).visible = False

                    # Rest Pose
                    # -------------------------------------------------------------------------------------
                    with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                        self._create_colored_box(color=styles.COLORS["PINK"])
                        self._rest_radio_btn = self._create_radio_btn(
                            name="Rest Pose",
                            collection=self._mode_radio_col
                        )
                        self._rest_radio_btn.identifier = "rest_radio_btn"

                        # save, copy, paste buttons
                        with ui.HStack(spacing=2, width=88):
                            self._save_rest_btn = ui.Button(
                                height=24,
                                style=styles.SAVE_BTN_STYLE,
                                clicked_fn=self._on_save_rest_pose,
                                tooltip="Set current character pose as its Rest pose."
                            )
                            self._save_rest_btn.identifier = "save_rest_btn"
                            ui.Spacer(width=6)
                            self._revert_rest_btn = ui.Button(
                                height=24,
                                style=styles.REVERT_BTN_STYLE,
                                clicked_fn=self._on_revert_rest_pose,
                                tooltip="Revert current character pose to its last saved Rest pose."
                            )
                            self._revert_rest_btn.identifier = "revert_rest_btn"
                        ui.Spacer()

                        # reset button
                        with ui.HStack(spacing=0, width=26):
                            self._reset_rest_btn = ui.Button(
                                style=styles.RESET_BTN_STYLE,
                                clicked_fn=self._on_reset_rest_pose,
                                tooltip="Sets current character pose to its ititial Bind pose."
                            )
                            self._reset_rest_btn.identifier = "reset_rest_btn"

                        ui.OffsetLine(self._revert_rest_btn, self._reset_rest_btn, width=0, bound_offset=2, style={"color": styles.COLORS["GREY"]})

                    # Default Bind Pose
                    # -------------------------------------------------------------------------------------
                    with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                        self._create_colored_box(color=styles.COLORS["CYAN"])
                        self._bind_radio_btn = self._create_radio_btn(
                            name="Default Bind Pose",
                            collection=self._mode_radio_col,
                        )
                        self._bind_radio_btn.identifier = "bind_radio_btn"
                        ui.Spacer()

                    # set last selected pose
                    if self._skel_prim.HasAuthoredCustomDataKey("TransformMode"):
                        transform_mode = self._skel_prim.GetCustomDataByKey("TransformMode")
                        self._mode_radio_col.model.set_value(transform_mode)

        # show/hide buttons
        self._refresh_buttons_visibility()

    def _refresh_buttons_visibility(self):
        if self._skel_prim:
            skeleton = UsdSkel.Skeleton(self._skel_prim)

            # retarget save/revert buttons
            if self._skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                if is_joint_poses_matching_retarget_poses(skeleton):
                    self._save_retarget_btn.enabled = False
                    self._revert_retarget_btn.enabled = False
                else:
                    self._save_retarget_btn.enabled = True
                    self._revert_retarget_btn.enabled = True

            # rest save/revert buttons
            if is_joint_poses_matching_rest_poses(skeleton):
                self._save_rest_btn.enabled = False
                self._revert_rest_btn.enabled = False
            else:
                self._save_rest_btn.enabled = True
                self._revert_rest_btn.enabled = True

            # retarget reset button
            if self._skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                if is_retarget_poses_matching_bind_poses(skeleton):
                    self._reset_retarget_btn.enabled = False
                else:
                    self._reset_retarget_btn.enabled = True

            # rest reset button
            if is_rest_poses_matching_bind_poses(skeleton):
                self._reset_rest_btn.enabled = False
            else:
                self._reset_rest_btn.enabled = True

    def _create_animation_source_field(self):
        if not self._skel_prim.IsA(UsdSkel.Skeleton):
            return

        if not self._skel_prim.HasAPI(UsdSkel.BindingAPI):
            with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                label = ui.Label("No skeletal animation API found.", style={"font_size": 14})
                btn = ui.Button(
                    text="Add One",
                    clicked_fn=lambda: omni.kit.commands.execute("ApplySkelBindingAPICommand", paths=[self._skel_prim.GetPath()])
                )
                self._anim_source_widget_items = [label, btn]
        else:
            with ui.HStack(spacing=HORIZONTAL_SPACING, height=0):
                targets = self._skel_prim.GetRelationship("skel:animationSource").GetTargets()
                target = targets[0].pathString if targets else ""
                self._anim_field = ui.StringField(read_only=True, style=styles.ANIM_FIELD_STYLE)
                self._anim_field.model.set_value(target)
                self._rel_picker = RelationshipTargetPicker(
                    stage=self._skel_prim.GetStage(),
                    filter_type_list=[UsdSkel.Animation],
                    filter_lambda=None,
                    additional_widget_kwargs={},
                )
                pick_btn = ui.Button(
                    width=20,
                    height=20,
                    style=styles.BROWSE_BTN_STYLE,
                    clicked_fn=self._on_pick_anim_source
                )

                locate_btn = ui.Button(
                    width=20,
                    height=20,
                    style=styles.LOCATE_BTN_STYLE,
                    clicked_fn=self._on_locate_anim_source
                )
                self._anim_source_widget_items = [self._anim_field, pick_btn, locate_btn]

    def _create_colored_box(self, color):
        with ui.VStack(spacing=0, width=0):
            ui.Spacer()
            with ui.HStack(spacing=0, width=0):
                ui.Spacer()
                ui.Rectangle(width=10, height=10, style={"background_color": color})
                ui.Spacer()
            ui.Spacer()

    def _create_radio_btn(self, name, collection, clicked_fn=None):
        with ui.HStack(spacing=0, width=0):
            btn = ui.RadioButton(
                text=name,
                radio_collection=collection,
                width=140,
                image_width=25,
                style=styles.RADIO_STYLE,
                clicked_fn=clicked_fn,
            )
        return btn

    def _on_pick_anim_source(self):
        self._rel_picker.show(
            targets_limit=1,
            on_targets_selected=self._on_anim_source_selected
        )

    def _on_anim_source_selected(self, selected_prims):
        relationship = self._skel_prim.GetRelationship("skel:animationSource")
        omni.kit.commands.execute("SetRelationshipTargets", relationship=relationship, targets=selected_prims)

    def _on_locate_anim_source(self):
        anim_source = self._anim_field.model.get_value_as_string()
        if not Sdf.Path.IsValidPathString(anim_source):
            return
        anim_source_p = self._stage.GetPrimAtPath(anim_source)
        if anim_source_p:
            omni.usd.get_context().get_selection().set_selected_prim_paths([anim_source], True)

    def _on_save_rest_pose(self):
        # actual work
        self._on_apply_joint_rest_pose_to_skeleton()

        # activate current mode
        self._mode_radio_col.model.set_value(2)

        # hide save button
        self._save_rest_btn.enabled = False

        # display message to user
        nm.post_notification("Rest Pose Saved")

    def _on_revert_rest_pose(self):
        # actual work
        # we don't have a revert command, as a workaround we switch to bind pose and back to this pose
        self._mode_radio_col.model.set_value(0)

        # reset has probably changed the pose, activate save button (should listen to USD changes instead)
        self._save_rest_btn.enabled = True

        # activate current mode
        self._mode_radio_col.model.set_value(2)

        # display message to user
        nm.post_notification("Rest Pose Changes Were Discarded")

    def _on_reset_rest_pose(self):
        # activate current mode
        self._mode_radio_col.model.set_value(2)

        # actual work (needs to happen after mode is set, because changing mode will change the pose)
        self._on_reset_to_binding()

        # after resetting, disable this reset button to indicate pose has been reset
        self._reset_rest_btn.enabled = False

        # reset has probably changed the pose, activate save button (should listen to USD changes instead)
        self._save_rest_btn.enabled = True
        self._revert_rest_btn.enabled = True

        # display message to user
        nm.post_notification("Rest Pose was Reset")

    def _on_save_retarget_pose(self):
        # actual work
        self._on_apply_joint_retarget_pose_to_skeleton()

        # activate current mode
        self._mode_radio_col.model.set_value(1)

        # hide save button
        self._save_retarget_btn.enabled = False

        # display message to user
        nm.post_notification("Retarget Pose Saved")

    def _on_revert_retarget_pose(self):
        # actual work
        # we don't have a revert command, as a workaround we switch to bind pose and back to this pose
        self._mode_radio_col.model.set_value(0)
        # activate current mode
        self._mode_radio_col.model.set_value(1)

        # display message to user
        nm.post_notification("Retarget Pose Changes Were Discarded")

    def _on_reset_retarget_pose(self):
        # activate current mode
        self._mode_radio_col.model.set_value(1)

        # actual work (needs to happen after mode is set, because changing mode will change the pose)
        self._on_reset_to_binding()

        # after resetting, disable this reset button to indicate pose has been reset
        self._reset_retarget_btn.enabled = False

        # reset has probably changed the pose, activate save/revert buttons
        self._save_retarget_btn.enabled = True
        self._revert_retarget_btn.enabled = True

        # display message to user
        nm.post_notification("Retarget Pose was Reset")

    def _on_skel_transform_mode_change(self, model):
        if self._skel_prim is None:
            return

        idx = model.get_value_as_int()

        # actual work
        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=self._skel_prim.GetPath(),
            transform_mode=idx
        )

        # show animation field only when in anim mode
        if idx == 0:
            for item in self._anim_source_widget_items:
                item.enabled = True
        else:
            for item in self._anim_source_widget_items:
                item.enabled = False

        # change mode icon
        self.skel_mode_img.set_style(
            [
                styles.SKEL_MODE_ANIM_STYLE,
                styles.SKEL_MODE_RETARGET_STYLE,
                styles.SKEL_MODE_REST_STYLE,
                styles.SKEL_MODE_BIND_STYLE,
            ][idx]
        )

        # show/hide buttons
        self._refresh_buttons_visibility()
