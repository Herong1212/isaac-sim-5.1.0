# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from .draw_scene_viewport import DrawSceneViewport
from .skel_selection_combo import MinimalItem, SkeletonSelection

import carb
import omni.kit.notification_manager as nm
import omni.kit.undo
import omni.stageupdate
import omni.timeline
import omni.ui as ui
import omni.usd
from omni.anim.retarget.core import has_retarget_setup
from omni.anim.retarget.core.scripts.utils import (
    convert_matrix_to_trans_rots,
    convert_trans_rots_to_pxr
)

from omni.kit.viewport.utility import get_active_viewport_window

from pxr import Gf, Sdf, Usd, UsdGeom, UsdSkel, Vt
from typing import Any, Callable, List

__button_styles__ = {
    "Button": {},
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


def make_visible(prim, visible):
    geom = UsdGeom.Imageable(prim)
    if visible:
        geom.MakeVisible()
    else:
        geom.MakeInvisible()


def post_skeleton_message(skeleton, title, description, in_status=nm.NotificationStatus.INFO):
    message = (
        "{}({}): {} ".format(title, str(skeleton.GetPrim().GetPath()), description)
    )
    nm.post_notification(message, status=in_status, duration=7)


def post_missing_tag_message(skeleton):
    message = (
        "Missing Tag: {} does not contain retarget tags. Make sure to set up the tags. ".format(str(skeleton.GetPrim().GetPath()))
    )
    nm.post_notification(message, status=nm.NotificationStatus.WARNING, duration=7)


class AssetLoaderHelper:
    def __init__(self):
        # save file link, asset path
        # if the asset exists, return, if not reload
        self._assets = {}
        self._reference_skeleton = None
        self._default_prim = None

    def __del__(self):
        self._assets = {}
        self._reference_skeleton = None
        self._default_prim = None

    def visible(self, skel_prim):
        # if skel_prim is same as reference_skeleton, we show the assets
        if skel_prim == self._reference_skeleton:
            make_visible(self._default_prim, True)

    def invisible(self, skel_prim):
        # if skel_prim is same as reference_skeleton, we show the assets
        if skel_prim == self._reference_skeleton:
            make_visible(self._default_prim, False)

    def load_asset(self, file_path, search_skeleton):
        prim_path = Sdf.Path()

        stage = omni.usd.get_context().get_stage()
        # current up axis
        up_axis = UsdGeom.GetStageUpAxis(stage)
        # we already have it
        # look for the prim
        if file_path in self._assets.keys():
            prim_path = self._assets[file_path]
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                return prim

        # if not, we'll insert layer and look for the asset
        # we only allow one asset in one file
        # create sub layer
        session_layer = stage.GetSessionLayer()

        omni.kit.commands.execute(
            "CreateSublayerCommand",
            layer_identifier=session_layer.identifier,
            sublayer_position=-1,
            new_layer_path=file_path,
            transfer_root_content=False,
            create_or_insert=False,
            layer_name="")

        def get_all_descendents(prim, output=[]):
            prim_children = prim.GetChildren()
            if prim_children:
                for child in prim_children:
                    output.append(child)
                    get_all_descendents(child, output)
            return output

        new_layer = Sdf.Layer.Find(file_path)
        if new_layer and len(new_layer.rootPrims) > 0 and new_layer.defaultPrim in new_layer.rootPrims:
            # we assume this new one is in the Y up and if scene is Z up, we have to rotate
            prims = []
            prim_spec = new_layer.rootPrims[new_layer.defaultPrim]
            default_prim = stage.GetPrimAtPath(prim_spec.path)
            if search_skeleton:
                xform = UsdGeom.XformCommonAPI(default_prim)
                if xform:
                    if up_axis == "Z":
                        # rotate 90 along X
                        xform.SetRotate(Gf.Vec3f(90.0, 0, 0))
                    xform.SetTranslate(Gf.Vec3d(-200, 0, 0))

            # hide from stage view
            default_prim.SetMetadata("hide_in_stage_window", True)
            make_visible(default_prim, False)
            if search_skeleton:
                if UsdSkel.Skeleton(default_prim):
                    self._assets[file_path] = default_prim.GetPath()
                    self._reference_skeleton = default_prim
                    self._default_prim = default_prim
                    return default_prim
            else:
                if UsdSkel.Animation(default_prim):
                    self._assets[file_path] = default_prim.GetPath()
                    return default_prim

            # or search descendents
            get_all_descendents(default_prim, prims)
            for p in prims:
                if search_skeleton:
                    if UsdSkel.Skeleton(p):
                        self._assets[file_path] = p.GetPath()
                        self._reference_skeleton = p
                        self._default_prim = default_prim
                        return p
                else:
                    if UsdSkel.Animation(p):
                        self._assets[file_path] = p.GetPath()
                        return p
        else:
            carb.log_error(
                "Retargeting preview: invalid scenen layer set up. Make sure you have default prim in the scene."
            )
        return None

    def set_animation(self, skeleton, anim):
        stage = omni.usd.get_context().get_stage()

        if skeleton:
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(session_layer)):
                UsdSkel.BindingAPI(skeleton).GetAnimationSourceRel().SetTargets([anim.GetPath()])


__asset_loader_helper__ = AssetLoaderHelper()


class AnimationSync:
    """ This preview works for one skeleton at a time if there is anyone active,
    it will display currently retargeting from A to B """
    def __init__(self):
        # save animation data
        # create new animation data in session layer
        self._source_skeleton = None
        self._target_skeleton = None
        self._saved_animation_source = None
        self._preview_animation = None
        self._retarget_controller = None
        self._source_skeleton_vis_attribute = ""

    def __del__(self):
        self._skeleton = None
        self._saved_animation_source = None
        self._preview_animation = None
        self._retarget_controller = None

    def update(self):
        if (self._source_skeleton and self._target_skeleton):
            stage = omni.usd.get_context().get_stage()
            time_code = omni.timeline.get_timeline_interface().get_current_time() * stage.GetTimeCodesPerSecond()
            # copy source transform
            source_skel_cache = UsdSkel.Cache()
            source_skel_query = source_skel_cache.GetSkelQuery(self._source_skeleton)
            source_transforms = source_skel_query.ComputeJointLocalTransforms(time_code)
            source_translations, source_rotations = convert_matrix_to_trans_rots(source_transforms)
            # retarget
            target_translations: List[carb.Float3] = []
            target_rotations: List[carb.Float4] = []
            target_translations, target_rotations = self._retarget_controller.retarget(source_translations, source_rotations)
            if len(target_translations) == 0:
                carb.log_warn("Preview: Retarget has failed")
                return

            # update target skeleton
            stage = self._target_skeleton.GetPrim().GetStage()
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(session_layer)):
                vt_translations, vt_rotations, vt_scales = convert_trans_rots_to_pxr(target_translations, target_rotations)
                self._preview_animation.GetTranslationsAttr().Set(Vt.Vec3fArray(vt_translations), Usd.TimeCode.Default())
                self._preview_animation.GetRotationsAttr().Set(Vt.QuatfArray(vt_rotations), Usd.TimeCode.Default())
                self._preview_animation.GetScalesAttr().Set(Vt.Vec3hArray(vt_scales), Usd.TimeCode.Default())

    # todo: have to listen to scene change? So that if they disappear, what do we do?
    def enable(self, source_skeleton, target_skeleton):
        if self._source_skeleton == source_skeleton and self._target_skeleton == target_skeleton:
            return
        # restore before saves next one if it hasn't been disabled for some reason
        if (self._target_skeleton):
            self.disable()
        if (target_skeleton and source_skeleton):
            self._target_skeleton = target_skeleton
            self._source_skeleton = source_skeleton
            # first save the current existing information from target skeleton
            # save the existing animation source
            skel_prim = target_skeleton.GetPrim()
            self._saved_animation_source = None
            # create new animation in session layer if it doesn't exist the current animation source in the
            stage = skel_prim.GetStage()
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(session_layer)):
                if skel_prim.HasAPI(UsdSkel.BindingAPI):
                    bindingAPI = UsdSkel.BindingAPI(target_skeleton)
                    relationship = bindingAPI.GetAnimationSourceRel()
                    if relationship:
                        targets = relationship.GetTargets()
                        if len(targets) > 0:
                            self._saved_animation_source = targets[0]
                else:
                    # we still have to create binding API for previewing, so create it now
                    UsdSkel.BindingAPI.Apply(skel_prim)
                # create animation
                preview_animation_path = skel_prim.GetPath().AppendElementString("preview_retarget_skel_animation")
                preview_animation_prim = stage.GetPrimAtPath(preview_animation_path)
                if preview_animation_prim is None or not preview_animation_prim.IsValid():
                    preview_animation_prim = stage.DefinePrim(preview_animation_path, "SkelAnimation")

                self._preview_animation = UsdSkel.Animation(preview_animation_prim)
                self._preview_animation.GetJointsAttr().Set(target_skeleton.GetJointsAttr().Get())
                UsdSkel.BindingAPI(target_skeleton).CreateAnimationSourceRel().SetTargets([preview_animation_path])
                global __asset_loader_helper__
                __asset_loader_helper__.visible(self._source_skeleton.GetPrim())
            # prepare for syncing animation
            self._retarget_controller = omni.anim.retarget.core.RetargetController(
                None,
                self._source_skeleton.GetPath().pathString,
                -1,
                self._target_skeleton.GetPath().pathString
            )

    def disable(self):
        if (self._target_skeleton and self._source_skeleton):
            skel_prim = self._target_skeleton.GetPrim()
            stage = skel_prim.GetStage()
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(session_layer)):
                preview_animation_path = skel_prim.GetPath().AppendElementString("preview_retarget_skel_animation")
                UsdSkel.BindingAPI(self._target_skeleton).GetAnimationSourceRel().ClearTargets(True)
                global __asset_loader_helper__
                __asset_loader_helper__.invisible(self._source_skeleton.GetPrim())
            # recover old reference in default layer, not in session layer
            if (self._saved_animation_source and preview_animation_path != self._saved_animation_source):
                UsdSkel.BindingAPI(self._target_skeleton).GetAnimationSourceRel().SetTargets([self._saved_animation_source])
            self._target_skeleton = None
            self._source_skeleton = None
            self._saved_animation_source = None
            self._preview_animation = None
            self._retarget_controller = None


class FacingPanel:
    def __init__(self, rig, facing_forward_axis_box, facing_up_axis_box, ext_id, is_window_visible: callable):
        self._draw_facing_viewport = None
        self._facing_forward_axis_box = facing_forward_axis_box
        self._facing_up_axis_box = facing_up_axis_box
        self._rig = rig
        rig.register_skeleton_changed(self._skeleton_changed)
        # draw facing feature

        # Get the active (which at startup is the default Viewport)
        viewport_window = get_active_viewport_window()

        # Issue an error if there is no Viewport
        if not viewport_window:
            carb.log_warn(f"No Viewport Window to add {ext_id} scene to")
            return

        self._draw_facing_viewport = DrawSceneViewport(viewport_window, ext_id, is_window_visible)

    def __del__(self):
        if self._rig:
            self._rig.unregister_skeleton_changed(self._skeleton_changed)
        self._rig = None
        if self._draw_facing_viewport:
            self._draw_facing_viewport.destroy()
            self._draw_facing_viewport = None
        self._slider_registry = None

    def _skeleton_changed(self, skeleton):
        if self._draw_facing_viewport:
            self._draw_facing_viewport.set_skeleton(skeleton)
        if skeleton:
            self.set_draw_up_axis(True)
            self.set_draw_forward_axis(True)
        else:
            self.set_draw_up_axis(False)
            self.set_draw_forward_axis(False)

    def _build_facing(self):
        stack_style = {
            "margin": 0,
        }

        combo_style = {
            "ComboBox": {
                "border_radius": 0,
            }
        }

        with ui.HStack():
            ui.Label(
                "Up Axis",
                width=50,
                height=30,
                tooltip="The direction of where character's head is from the hips",
                style={
                    "padding": 0,
                    "margin-top": 4,
                    "margin-right": 0,
                    "margin-left": 0,
                }
            )

            # use click button
            with ui.HStack(style=stack_style):
                self._up_vis_image = ui.Image(
                    "",
                    width=20,
                    height=20,
                    alignment=ui.Alignment.H_CENTER,
                )

                self._up_combo_box = ui.ComboBox(self._facing_up_axis_box, width=50, height=30, style=combo_style)

        with ui.HStack():
            ui.Label(
                "Forward Axis",
                width=75,
                height=30,
                tooltip="The direction of where character is facing horizontally."
            )

            with ui.HStack(style=stack_style):
                self._forward_vis_image = ui.Image(
                    "",
                    width=20,
                    height=20,
                    alignment=ui.Alignment.H_CENTER
                )

                self._forward_combo_box = ui.ComboBox(self._facing_forward_axis_box, width=50, height=30, style=combo_style)

        ## leaving this here for editing
        # ui.Button(" * ", width=30, height=30, clicked_fn=self._on_save_clicked, style=__button_styles__)

        self.set_draw_up_axis(False)
        self.set_draw_forward_axis(False)
        self._update_images()

    def _on_save_clicked(self, *args):
        import os
        import json

        index = 1
        filepath = f"W:/temp/out.{index:04d}.json"
        while os.path.exists(filepath):
            index += 1
            filepath = f"W:/temp/out.{index:04d}.json"

        data = {
            "mappings": [[x, y.joint] for x, y in self._rig._tags.items()]
        }

        with open(filepath, "w") as fp:
            fp.write('{\n\t"mappings": [\n')
            for name, tag in self._rig._tags.items():
                fp.write(f'\t\t["{name}", "{tag.joint}"],\n')
            fp.write("\t]\n}\n")

    def _get_up_combo_value(self) -> Any:
        return abs(self._facing_up_axis_box.value()) % 3

    def _get_forward_combo_value(self) -> Any:
        return abs(self._facing_forward_axis_box.value()) % 3

    def _rebuild_ui(self):
        with ui.VStack():
            self._build_facing()

    def _update_images(self):
        images = [
            "resources/icons/transform_x.png",
            "resources/icons/transform_y.png",
            "resources/icons/transform_z.png",
        ]

        self._up_vis_image.set_style({"image_url": images[self._get_up_combo_value()], "image_width": 12, "image_height": 12, "padding": 0})
        self._forward_vis_image.set_style({"image_url": images[self._get_forward_combo_value()], "image_width": 12, "image_height": 12, "padding": 0})

    def set_up_axis(self, up_axis):
        self._update_images()
        if self._draw_facing_viewport:
            self._draw_facing_viewport.set_up_axis(up_axis)

    def set_forward_axis(self, forward_axis):
        self._update_images()
        if self._draw_facing_viewport:
            self._draw_facing_viewport.set_forward_axis(forward_axis)

    def on_toggle_vis_up(self, b):
        if b == 0:
            # toggle
            if self._rig.skeleton:
                draw = not self._up_draw
            else:
                draw = False
            self.set_draw_up_axis(draw)

    def set_draw_up_axis(self, enable):
        self._up_draw = enable
        if self._draw_facing_viewport:
            self._draw_facing_viewport.set_draw_up_axis(self._up_draw)

    def on_toggle_vis_forward(self, b):
        if b == 0:
            # toggle
            if self._rig.skeleton:
                draw = not self._forward_draw
            else:
                draw = False
            self.set_draw_forward_axis(draw)

    def set_draw_forward_axis(self, enable):
        self._forward_draw = enable
        if self._draw_facing_viewport:
            self._draw_facing_viewport.set_draw_forward_axis(self._forward_draw)


class RetargetPosePanel:
    def __init__(self, rig, on_load_pose, on_unload_pose, on_clear_pose, on_save_pose, stageinfo):
        self._rig = rig
        self._source_skeleton = None
        self._target_skeleton = None
        self._on_load_pose = on_load_pose
        self._on_unload_pose = on_unload_pose
        self._on_clear_pose = on_clear_pose
        self._on_save_pose = on_save_pose
        self._stage_info = stageinfo
        self._enable_retarget_pose = False
        _, self._ref_skeleton_name, self._ref_skeleton_path = self._rig.get_reference_skeleton()
        rig.register_skeleton_changed(self.on_skeleton_changed)
        self._rebuild_ui()

    def __del__(self):
        if (self._rig):
            self._rig.unregister_skeleton_changed(self.on_skeleton_changed)

        self._load_pose_button = None
        self._auto_pose_button = None
        self._reset_pose_button = None
        self._save_pose_button = None
        self._skeleton_combo_box = None
        self._skeleton_combo_box_ui = None
        self._stage_info = None

    def on_update(self, t, dt):
        # update button status
        valid = (self._source_skeleton is not None and self._target_skeleton is not None and self._source_skeleton.GetPrim().GetPath() != self._target_skeleton.GetPrim().GetPath())
        self.enable_button(self._auto_pose_button, valid)

    def _rebuild_ui(self):
        global __button_styles__
        self._load_pose_button = None
        self._auto_pose_button = None
        self._reset_pose_button = None
        self._save_pose_button = None
        self._skeleton_combo_box_ui = None
        with ui.VStack():
            with ui.HStack():
                ui.Spacer(width=5)
                ui.Label(
                    " Retarget Pose ",
                    width=50,
                    tooltip="Retarget Pose is default pose for the retargeter. \nBest to match with the skeleton's retarget pose of the motions you want to use."
                )
                ui.Spacer()
                self._load_pose_button = ui.Button(
                    "Auto Pose",
                    width=80,
                    height=30,
                    clicked_fn=self._on_auto_pose,
                    style=__button_styles__
                )
                self._load_pose_button = ui.Button(
                    "View",
                    width=60,
                    height=30,
                    clicked_fn=self.toggle_pose,
                    style=__button_styles__
                )
                self._reset_pose_button = ui.Button(
                    "Reset",
                    width=60,
                    height=30,
                    clicked_fn=self._on_clear_pose,
                    style=__button_styles__
                )

                self._reset_pose_button.identifier = "reset_pose_button"
                self._save_pose_button = ui.Button(
                    "Apply",
                    width=60,
                    height=30,
                    clicked_fn=self._on_save_pose,
                    style=__button_styles__
                )
                with ui.VStack():
                    ui.Spacer(height=5)
                    self._skeleton_combo_box = SkeletonSelection(
                        self._on_select_source_skeleton_prim,
                        "Match with...",
                        self._stage_info,
                        self._on_combo_box_add,
                        self._on_combo_box_set
                    )
                    self._skeleton_combo_box_ui = ui.ComboBox(self._skeleton_combo_box)
                self._auto_pose_button = ui.Button(
                    "Match",
                    width=60,
                    height=30,
                    clicked_fn=self._apply_auto_pose,
                    style=__button_styles__
                )

    def _apply_auto_pose(self):
        """based on the skeleton selected we generate the auto pose and users can decided to save it or not"""
        if (self._source_skeleton is None or self._target_skeleton is None):
            return
        # this is different than the one below - because it saves to the target pose
        # auto_pose(self._source_skeleton.GetPath().pathString, self._target_skeleton.GetPath().pathString)
        # self._on_load_pose()
        if not has_retarget_setup(self._source_skeleton.GetPrim()):
            post_missing_tag_message(self._source_skeleton)
            return
        if not has_retarget_setup(self._target_skeleton.GetPrim()):
            post_missing_tag_message(self._target_skeleton)
            return
        self.enable_button(self._auto_pose_button, False)

        retarget_controller = omni.anim.retarget.core.RetargetController(None, self._source_skeleton.GetPath().pathString, -1, self._target_skeleton.GetPath().pathString)
        if retarget_controller:
            target_translations: List[carb.Float3] = []
            target_rotations: List[carb.Float4] = []
            target_translations, target_rotations = retarget_controller.auto_pose()
            # now update to usd skeleton
            if len(target_translations) == 0:
                return
            skeleton = self._target_skeleton
            skel_prim = skeleton.GetPrim()
            # if we don't have retarget transform, we go through rest transform and bind transform
            joints_attr = skeleton.GetJointsAttr()
            if not joints_attr:
                return
            vt_translations, vt_rotations, vt_scales = convert_trans_rots_to_pxr(target_translations, target_rotations)
            joints = joints_attr.Get()
            omni.kit.undo.begin_group()
            transforms = []
            if joints:
                for i in range(len(vt_translations)):
                    matrix = Gf.Matrix4d(1.0)
                    matrix.SetTranslateOnly(Gf.Vec3d(vt_translations[i]))
                    matrix.SetRotateOnly(Gf.Quatd(vt_rotations[i]))
                    transforms.append(matrix)
                    omni.kit.commands.execute(
                        "TransformPrim",
                        path=skel_prim.GetPath().AppendPath(Sdf.Path(joints[i])),
                        new_transform_matrix=matrix
                    )
                # save using transforms function - since this should be applied from the data
                omni.kit.commands.execute(
                    "SaveRetargetPoseTransformCommand",
                    skel_paths=[skel_prim.GetPath()],
                    transforms=transforms
                )
                post_skeleton_message(
                    skeleton, "Match Pose", "current pose is matched to selected skeleton")
            else:
                carb.log_error("Retarget Transform \"{}\" doesn't exist.".format(skel_prim.Get_Path().pathString))
                post_skeleton_message(
                    skeleton, "Match Pose", "failed to match to selected skeleton", nm.NotificationStatus.WARNING)
            omni.kit.undo.end_group()
        self.enable_button(self._auto_pose_button, True)

    # ensure current skeleton
    def _on_select_source_skeleton_prim(self, index, skeleton_path):
        if index > 0:
            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(skeleton_path)
            if prim:
                self._source_skeleton = UsdSkel.Skeleton(prim)
        else:
            self._source_skeleton = None

    def on_skeleton_changed(self, skeleton):
        self._target_skeleton = skeleton
        # reset retarget pose button
        self._enable_retarget_pose = False
        self._load_pose_button.text = "View"

    def _on_combo_box_add(self):
        if self._ref_skeleton_name is not None:
            return [MinimalItem(self._ref_skeleton_name)]

    def _on_combo_box_set(self, index, string):
        global __asset_loader_helper__
        if string == self._ref_skeleton_name:
            prim = __asset_loader_helper__.load_asset(self._ref_skeleton_path, True)
            if prim:
                return prim.GetPath()

    def enable_button(self, button: ui.Button, enable):
        if button.enabled != enable:
            button.enabled = enable
            if enable:
                button.name = ""
            else:
                button.name = "disabled"

    def toggle_pose(self):
        self._enable_retarget_pose = not self._enable_retarget_pose

        if self._enable_retarget_pose:
            self._on_load_pose()
            self._load_pose_button.text = "Hide"
        else:
            self._on_unload_pose()
            self._load_pose_button.text = "View"

    def _on_auto_pose(self):
        self._rig.auto_setup()


class AutoSetupPanel:
    def __init__(self, on_auto_setup: Callable):
        self._on_auto_setup = on_auto_setup
        self._rebuild_ui()

    def __del__(self):
        self._on_auto_setup = None

    def _rebuild_ui(self):
        global __checkbox_styles__

        with ui.VStack():
            with ui.HStack():
                ui.Spacer(width=10)
                ui.Label("Auto Setup", width=30, tooltip="Automate the set up.")
                ui.Spacer()
                ui.Button("Retarget", width=166, height=30, clicked_fn=self._on_retarget_clicked, style=__button_styles__)


    def _on_retarget_clicked(self):
        self._on_auto_setup()
