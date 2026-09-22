# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import carb
import enum
import omni.usd
import omni.anim.skelJoint
import omni.timeline
import omni.kit.app
from pxr import Gf, Sdf, Usd, UsdGeom, UsdSkel
from pathlib import Path
import carb.settings
from typing import Callable, List, Optional, Tuple, Union

from .annotation.utils import extract_annotations
from .annotation.annotation_model import AnnotationSet
from .model.source_model import SourceModel, SourceItemModel, SourceSetModel
from . import zoom_handler
from .compatibility_utils import check_compatibility
from .usd_helper import copy_prim_to_stage, delete_prims, traverse_prim, get_material_bindings
from .preference import DEFAULT_PREVIEW_SKELETON_SETTING_PATH

# for typing only
from omni.anim.skelJoint.bindings._omni_anim_skelJoint import IOmniSkel


MODULE_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
PREVIEW_STAGE_ANIMROOT_PATH = '/World/Animations'
PREVIEW_STAGE_SOURCE_SKEL_PATH = '/World/SourceSkels'
PREVIEW_STAGE_SKELROOT_PATH = '/World/Character'
PREVIEW_STAGE_MATERIAL_PATH = '/World/Material/Root'
VIEWPORT_SETTINGS_PATH = '/persistent/exts/omni.anim.skelJoint/context/'
VIEWPORT_DISPLAYOPTIONS = '/skeletons/visible'
XFORM_OP_ROTATE_UNITSRESOLVE_ATTR = "xformOp:rotateX:unitsResolve"
XFORM_OP_SCALE_UNITSRESOLVE_ATTR = "xformOp:scale:unitsResolve"

class AnimationCompatibilty(enum.Enum):
    COMPATIBLE = 'Fully compatible'
    INCOMPATIBLE = 'Incompatible'
    PARTIAL = 'Partially compatible'

    def __str__(self):
        return str(self.value)


class SkeletonGeometry:
    def __init__(self):
        self._bbox = Gf.Range3d()
        self._height = 0
        self._root_joint_prim = None
        self._center = None
        self._center_offset = None
        self._up_axis = None

    @property
    def bbox(self) -> Gf.Range3d:
        """
        Bounding box in T-pose
        """
        return self._bbox

    @property
    def height(self) -> float:
        """
        Height of the bounding box in T-pose
        """
        return self._height

    @property
    def root_joint_prim(self) -> Usd.Prim:
        """
        Root joint prim.
        """
        return self._root_joint_prim

    @property
    def center(self) -> Gf.Vec3d:
        """
        Center of the bounding box in T-pose
        """
        return self._center

    @property
    def up_axis(self) -> Gf.Vec3d:
        """
        Up axis in T-pose
        """
        return self._up_axis

    @property
    def center_offset(self) -> Gf.Vec3d:
        """
        Offset vector between the root position and the center, in T-pose
        """
        return self._center_offset

    def get_root_position(self, time: Usd.TimeCode) -> Gf.Vec3d:
        """
        Root position at a given time
        """
        if not self._root_joint_prim:
            return None

        pos = self._root_joint_prim.GetAttribute('xformOp:translate').Get(time)
        if pos is not None:
            return pos

        # Try other attributes
        gprim = UsdGeom.Gprim.Get(self._root_joint_prim.GetStage(), self._root_joint_prim.GetPath())
        if gprim is not None:
            pos = gprim.ComputeLocalToWorldTransform(time).Transform(Gf.Vec3d(0, 0, 0))
            return pos
        return None

    def get_center(self, time: Usd.TimeCode) -> Gf.Vec3d:
        """
        Center of the bounding box at a given time
        """
        blank = Gf.Vec3d(0,0,0)
        result = self.get_root_position(time) or blank
        result += self.center_offset or blank
        return result

    def compute(self, skel_prim: Usd.Prim, up_axis: Optional[Gf.Vec3d] = None):
        """
        Compute the geometry of the skeleton

        Args:
            skel_prim (Usd.Prim): the skeleton root prim. Assumed to be in T-pose.
            up_axis (Optional[Gf.Vec3d]): the up-axis of the skeleton. If not specified, [0, 1, 0] will be used.
        """
        if skel_prim is None or not skel_prim.IsValid():
            return

        # OM-85112: compute_world_bbox ignores animation if we use Usd.TimeCode.Default(), so we use 0 for timecode
        self._bbox: Gf.Range3d = SkeletonGeometry.compute_world_bbox(skel_prim, 0)
        self._center = self._bbox.GetMidpoint()
        if up_axis is None:
            up_axis = Gf.Vec3d(0, 1, 0)
        else:
            up_axis = up_axis.GetNormalized()
        self._up_axis = up_axis
        self._height = abs(Gf.Dot(up_axis, self.bbox.GetCorner(0) - self.bbox.GetCorner(7)))

        stage = skel_prim.GetStage()
        joints = traverse_prim(stage, skel_prim.GetPath(), self._is_joint)
        if len(joints):
            self._root_joint_prim: Usd.Prim = stage.GetPrimAtPath(joints[-1])
            root_pos = self.get_root_position(Usd.TimeCode.Default())
        else:
            root_pos = Gf.Vec3d(0, 0, 0)

        self._center_offset = self._center - root_pos

    def _is_joint(self, prim: Usd.Prim, path) -> bool:
        return prim.GetTypeName() in ['OmniJoint']

    @staticmethod
    def compute_world_bbox(prim: Usd.Prim, time_code: Usd.TimeCode) -> Gf.Range3d:
        """
        Computes the world space bounding box of a prim

        Args:
            prim (Usd.Prim): The input prim.
            time_code (Usd.TimeCode): Time for which the bbox is computed.
        """
        purposes = [UsdGeom.Tokens.default_, UsdGeom.Tokens.render, UsdGeom.Tokens.guide]
        # Workaround: ComputeWorldBound seems to give the same result as ComputeLocalBound
        #             So we transform the local bbox manually
        bbox_local = UsdGeom.Imageable(prim).ComputeLocalBound(time_code, *purposes).GetBox()
        transform = UsdGeom.Imageable(prim).ComputeLocalToWorldTransform(time_code)
        transform.Transform(bbox_local.GetMin())
        world_min = transform.Transform(bbox_local.GetMin())
        world_max = transform.Transform(bbox_local.GetMax())
        return Gf.Range3d(world_min, world_max)


def _is_mesh(prim: Usd.Prim, _) -> bool:
    return prim.IsA(UsdGeom.Mesh)


def _is_skeleton(prim: Usd.Prim, _) -> bool:
    return prim.IsA(UsdSkel.Skeleton)


def _can_have_material(prim: Usd.Prim, _) -> bool:
    return _is_mesh(prim, None) or prim.IsA(UsdGeom.Subset)


class AnimPreviewModel:
    def __init__(self, preview_context_name: Optional[str] = None):
        """AnimPreviewModel constructor
        Args:
            preview_context_name (str): The name of a UsdContext the Viewport will be viewing.
        """

        # We may be given an already valid context, or we'll be creating and managing it ourselves
        if preview_context_name is None:
            preview_context_name = ''
        self._preview_context_name = preview_context_name
        preview_context = omni.usd.get_context(preview_context_name)
        self._timeline_name = preview_context_name
        if not preview_context:
            self._preview_context = omni.usd.create_context(preview_context_name)
            # make sure the new context uses a new timeline
            self._preview_context.set_timeline(self._timeline_name)
            """
            timeline = self._preview_context.get_timeline()
            # TODO: set these somewhere else?
            timeline.set_end_time(10)
            timeline.set_time_codes_per_second(30)
            """
            print("context created: " + preview_context_name)
        else:
            self._preview_context = preview_context
            if preview_context_name != '' and preview_context.get_timeline_name() == '':
                carb.log_error(f"AnimPreviewWindow: Context requires a separate timeline.")
        self._timeline = self._preview_context.get_timeline()

        self._preview_stage = None
        self._stage_active = False
        self._skeleton = None
        self._skeleton_geom: SkeletonGeometry = None
        self._is_skeleton_selected = False
        self._mesh_paths = None
        self._anim_root_path = None
        self._source_skel_root_path = None
        self._skeleton_root_path = None

        self._anim_source_model = SourceSetModel()
        self._anim_source_model.add_item_changed_fn(self._on_anim_source_item_changed)
        self._source_skel_source_model = SourceSetModel()
        self._skel_source_model = SourceSetModel()
        self._on_skel_changed_fn_id = self._skel_source_model.add_item_changed_fn(self._on_skel_source_item_changed)
        self._i_omniskel:IOmniSkel = omni.anim.skelJoint.acquire_interface()

        # TODO: settings/save?
        self._show_skeleton = True
        self._show_mesh = True

        self._settings = carb.settings.acquire_settings_interface()
        self._settings.set_default_bool(self.get_viewport_displayoptions_location(), True)

        self._external_skels = set()
        self._skel_up_axis = dict()

        self._src_time_codes_per_second_maps = dict()
        self._loaded_time_codes_per_second_maps = dict()

        self._clear_callbacks()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._skel_source_model.remove_item_changed_fn(self._on_skel_changed_fn_id)
        self._i_omniskel.remove_omni_skel(self._preview_context_name)
        self.remove_animations()
        self.remove_skeletons(keep_default=False)
        self._anim_source_model.destroy()
        self._anim_source_model = None
        self._source_skel_source_model.destroy()
        self._source_skel_source_model = None
        self._skel_source_model.destroy()
        self._skel_source_model = None
        self._clear_callbacks()
        self._anim_root_path = None
        self._source_skel_root_path = None
        self._skeleton_root_path = None
        self._skeleton_geom = None
        self._stage_active = False
        if self._preview_context:
            if self._preview_stage:
                self._preview_context.close_stage()
                self._preview_stage = None
            # We can't fully tear down everything yet, so just clear out any active stage
            self._preview_context.remove_all_hydra_engines()
            # This crashes now
            #omni.usd.destroy_context(self._preview_context_name)
            self._preview_context = None
            self._preview_context_name = None

    def _clear_callbacks(self):
        self._callback_stage_loaded = []
        self._callback_skeleton_loaded = []
        self._callback_skeleton_changed = []
        self._callback_animation_loaded = []
        self._callback_animation_changed = []

    def align_skel_up_axis_to_current_stage_up_axis(self, skel_root_path, skel_up_axis, original_rotate):
        current_stage = omni.usd.get_context().get_stage()
        current_up_axis = UsdGeom.GetStageUpAxis(current_stage)
        root_prim = self._preview_stage.GetPrimAtPath(skel_root_path)
        if not root_prim.IsValid():
            return
        UsdGeom.Xform.Define(self._preview_stage, root_prim.GetPath())
        if not root_prim.HasAttribute('xformOp:rotateXYZ'):
            UsdGeom.Xformable(root_prim).AddRotateXYZOp()
        rotate_attr = root_prim.GetAttribute('xformOp:rotateXYZ')

        if skel_up_axis == UsdGeom.Tokens.z and current_up_axis == UsdGeom.Tokens.y:
            rotate = Gf.Vec3d(original_rotate[0]-90, original_rotate[1], original_rotate[2])
        elif skel_up_axis == UsdGeom.Tokens.y and current_up_axis == UsdGeom.Tokens.z:
            rotate =  Gf.Vec3d(original_rotate[0]+90, original_rotate[1], original_rotate[2])
        elif skel_up_axis == current_up_axis:
            rotate = Gf.Vec3d(original_rotate[0],original_rotate[1],original_rotate[2])

        rotate_attr.Set(rotate)

    def sync_up_axis_with_current_stage(self):
        if not self._stage_active or self._preview_stage is None:
            return

        current_stage = omni.usd.get_context().get_stage()
        new_up_axis = UsdGeom.GetStageUpAxis(current_stage)
        new_meters_per_unit = UsdGeom.GetStageMetersPerUnit(current_stage) or 0.01
        UsdGeom.SetStageUpAxis(self._preview_stage, new_up_axis)
        UsdGeom.SetStageMetersPerUnit(self._preview_stage, new_meters_per_unit)
        erase_paths = []
        for skel_root_path in self._skel_up_axis:
            skel_up_axis, original_roate = self._skel_up_axis[skel_root_path]
            root_prim = self._preview_stage.GetPrimAtPath(skel_root_path)
            if not root_prim.IsValid():
                erase_paths.append(skel_root_path)
                continue
            self.align_skel_up_axis_to_current_stage_up_axis(skel_root_path, skel_up_axis, original_roate)
        for path in erase_paths:
            del self._skel_up_axis[path]

    def load_stage(self):
        """ Loads the default preview stage
        """
        print("Loading Preview Stage")
        self._stage_active = True
        stage_path = self._settings.get(DEFAULT_PREVIEW_SKELETON_SETTING_PATH)
        resolve_path = carb.tokens.get_tokens_interface().resolve(stage_path)
        # Open the preview stage in a new stage and copy it to the context
        # This is inefficient, but it prevents multiple contexts pointing to the same stage
        stage = Usd.Stage.Open(resolve_path)
        self._preview_context.new_stage()
        self._preview_stage = self._preview_context.get_stage()
        self.sync_up_axis_with_current_stage()

        copy_prim_to_stage(stage, '/World', self._preview_stage, '/World')
        self._anim_root_path = PREVIEW_STAGE_ANIMROOT_PATH + '/anim'
        self._preview_stage.DefinePrim(self.get_anim_root_path())
        self._source_skel_root_path = PREVIEW_STAGE_SOURCE_SKEL_PATH + "/skel"
        self._preview_stage.DefinePrim(self._source_skel_root_path)
        self._setup_default_skeleton()
        skel_root_path = self.get_skeleton_root_path()
        src_stage_up_axis = UsdGeom.GetStageUpAxis(stage)
        self._skel_up_axis[self.get_skeleton_root_path()] = (src_stage_up_axis, [0, 0, 0])
        self.align_skel_up_axis_to_current_stage_up_axis(skel_root_path, src_stage_up_axis, [0, 0, 0])
        self._i_omniskel.add_omni_skel(self._preview_context_name, omni.anim.skelJoint.FabricUseType.ON)

        for callback in self._callback_stage_loaded:
            callback()

    def has_animation(self) -> bool:
        """ Returns whether there is any animations loaded.
        """
        if not self._stage_active:
            return False
        animroot_prim = self._preview_stage.GetPrimAtPath(self.get_anim_root_path())
        return animroot_prim.IsValid() and len(animroot_prim.GetChildren()) > 0

    def remove_animations(self):
        """ Clears all animations from the preview stage.
        """
        if not self._stage_active:
            return

        if self._skeleton:
            with Usd.EditContext(self._preview_stage,
                    self._preview_stage.GetEditTargetForLocalLayer(self._preview_stage.GetRootLayer())):
                UsdSkel.BindingAPI(self._skeleton).CreateAnimationSourceRel().SetTargets([])

        if self._anim_source_model is not None:
            self._anim_source_model.clear()

        animroot_prim = self._preview_stage.GetPrimAtPath(PREVIEW_STAGE_ANIMROOT_PATH)
        for anim_prim in animroot_prim.GetChildren():
            self._preview_stage.RemovePrim(anim_prim.GetPrimPath())

        source_skel_root_prim = self._preview_stage.GetPrimAtPath(PREVIEW_STAGE_SOURCE_SKEL_PATH)
        for source_skel_prim in source_skel_root_prim.GetChildren():
            self._preview_stage.RemovePrim(source_skel_prim.GetPrimPath())

        self._source_skel_source_model.clear()

    def remove_skeletons(self, keep_default: bool = False):
        """ Clears all skeletons from the preview stage
        Args:
            keep_default (bool): Pass True to keep the default skeleton. Default value is True.
        """
        self.stop()

        # remove the current binding
        self._switch_preview_anim(None)

        self._i_omniskel.remove_omni_skel(self._preview_context_name)

        # re-active all skeletons so they show up during stage traversal
        if self._preview_stage:
            for skel in self._preview_stage.GetPrimAtPath(PREVIEW_STAGE_SKELROOT_PATH).GetAllChildren():
                skel.SetActive(True)

        # delete all prims, possibly excluding the default skeleton
        if self._preview_stage:
            path_to_ignore = None
            if keep_default and Sdf.Path(self._get_default_skeleton_root_path()) is not None:
                path_to_ignore = self._get_default_skeleton_root_path() + '/'

            def include_path(_, path) -> bool:
                if str(path) == PREVIEW_STAGE_SKELROOT_PATH or \
                    str(path) == self._get_default_skeleton_root_path() or \
                    (path_to_ignore is not None and str(path).startswith(path_to_ignore)):
                    return False
                return True

            def is_external(_, path):
                for p in self._external_skels:
                    if str(path).startswith(p):
                        return True
                return False

            def should_delete(stage, path):
                return include_path(stage, path) and not is_external(stage, path)

            paths_to_delete = traverse_prim(self._preview_stage,
                                            PREVIEW_STAGE_SKELROOT_PATH,
                                            should_delete)
            delete_prims(self._preview_stage, paths_to_delete)

        curr_external_path = None
        self._external_skels.clear()
        if self.skel_source_model:
            current_source = self.skel_source_model.get_current_source()
            if current_source and current_source.is_external:
                curr_external_path = self.skel_source_model.get_current_source().target_path_in_stage
        # external_url_backup = dict()
        # for source in self.skel_source_model.get_item_children(None):
        #     if source.model.is_external:
        #         external_url_backup[source.model.target_path_in_stage] = source.model.source_url

        # maintain source data structure
        if self._skel_source_model is not None:
            self._skel_source_model.clear()
            if keep_default:
                self._setup_default_skeleton()
            else:
                self._skeleton = None
                self._skeleton_root_path = None
            #self._setup_external_skeletons(external_url_backup, curr_external_path)
        else:
            self._skeleton = None
            self._skeleton_root_path = None

        self._mesh_paths = None  # remove mesh path cache, will be rebuilt
        self._i_omniskel.add_omni_skel(self._preview_context_name, omni.anim.skelJoint.FabricUseType.OFF)

    def _setup_default_skeleton(self):
        """ Initializes internal state such that the default skeleton is selected
        """
        self._skeleton_root_path = self._get_default_skeleton_root_path()
        skel_path = self.get_skeleton_root_path() + '/Root'
        self._skeleton = None
        default_skel_source = SourceModel()
        default_skel_source.set_source_path_in_stage(skel_path)
        default_skel_source.target_path_in_stage = skel_path
        default_skel_source.set_source_url(str(self._preview_context.get_stage_url()))
        default_skel_source.display_text = 'Default skeleton'
        if self._skel_source_model.get_current_source() is not None:
            self._skel_source_model.clear()
        self._skel_source_model.add_source(default_skel_source, set_current=True)

    def _setup_external_skeletons(self, external_urls, curr_external_skel: Optional[str]):
        for path in self.get_skeleton_paths():
            path = str(path)
            if path == self.get_skeleton_root_path():
                continue
            skel_source = SourceModel()
            skel_source.set_source_path_in_stage(path)
            skel_path = path + '/Root'
            skel_source.target_path_in_stage = skel_path
            if skel_path in external_urls:
                skel_source.set_source_url(external_urls[skel_path])
            set_current = skel_path == curr_external_skel
            self._external_skels.add(path)
            self._skel_source_model.add_source(skel_source, set_current=set_current)

    def get_skeleton(self) -> UsdSkel.Skeleton:
        return self._skeleton

    def get_viewport_settings_location(self) -> str:
        return VIEWPORT_SETTINGS_PATH + self._preview_context_name

    def get_viewport_displayoptions_location(self) -> str:
        return self.get_viewport_settings_location() + VIEWPORT_DISPLAYOPTIONS

    def set_show_active_bones(self, show_active: bool = True):
        if self.skeleton_prim and self.skeleton_prim.IsValid():
            def is_joint(prim: Usd.Prim, path) -> bool:
                return prim.GetTypeName() in ['OmniJoint']
            joint_prim_paths = traverse_prim(self._preview_stage, self.skeleton_prim.GetPath(), is_joint)
            attr_name = "omniJoint:animated"
            for joint_prim_path in joint_prim_paths:
                joint_prim = self._preview_stage.GetPrimAtPath(joint_prim_path)
                is_joint_active = False
                compatibility = self.get_compatibility()
                common_joints = compatibility[1] if compatibility else []
                for joint_name in common_joints:
                    if str(joint_prim_path).endswith(joint_name):
                        is_joint_active = True
                        break
                if show_active and is_joint_active:
                    if not joint_prim.HasAttribute(attr_name):
                        joint_prim.CreateAttribute(attr_name, Sdf.ValueTypeNames.Bool)
                    joint_prim.GetAttribute(attr_name).Set(True)
                else:
                    if joint_prim.HasAttribute(attr_name):
                        joint_prim.GetAttribute(attr_name).Set(False)

    def get_show_mesh(self):
        return self._show_mesh

    def set_show_mesh(self, value: bool = True):
        """ Sets the current mesh visible/invisible
        """
        self._show_mesh = value

        if self._preview_stage is None:
            return
        if self._mesh_paths is None or len(self._mesh_paths) == 0:
            self._mesh_paths = traverse_prim(self._preview_stage, self.get_skeleton_root_path(), _is_mesh)
            if len(self._mesh_paths) == 0:  # quick fix for the current preview stage
                self._mesh_paths = traverse_prim(self._preview_stage, PREVIEW_STAGE_SKELROOT_PATH, _is_mesh)
        vis_token = 'inherited' if value else 'invisible'
        for p in self._mesh_paths:
            prim = self._preview_stage.GetPrimAtPath(p)
            if prim.IsValid():
                prim.GetAttribute('visibility').Set(vis_token)

    def get_show_skeleton(self):
        return self._show_skeleton

    def set_show_skeleton(self, value: bool = True):
        """ Sets the current skeleton visible/invisible
        """
        self._show_skeleton = value

        self._settings.set(self.get_viewport_displayoptions_location(), value)

    def get_skeleton_bbox(self) -> Gf.Range3d:
        """ Returns the world space bounding box of the current skeleton
        """
        from .annotation.utils import time_to_timecode
        current_time = time_to_timecode(self._timeline.get_current_time(), self._timeline)
        skel_prim = self._preview_stage.GetPrimAtPath(self.get_skeleton_root_path())
        world_bbox = SkeletonGeometry.compute_world_bbox(skel_prim, current_time)
        return world_bbox

    def get_anim_root_path(self, create_new: bool = False) -> str:
        """ Returns the current path, or if create_new is True, returns the next available """
        if create_new:
            root = self._anim_root_path
            return str(omni.usd.get_stage_next_free_path(self._preview_stage, root, True))
        return self._anim_root_path

    def get_skeleton_root_path(self, create_new: bool = False) -> str:
        """ Returns the current path, or if create_new is True, returns the next available """
        if create_new:
            root = self._skeleton_root_path or self._get_default_skeleton_root_path()
            return str(omni.usd.get_stage_next_free_path(self._preview_stage, root, True))
        return self._skeleton_root_path

    def get_source_skeleton_root_path(self, create_new: bool = False) -> str:
        """ Returns the current path, or if create_new is True, returns the next available """
        if create_new:
            root = self._source_skel_root_path
            return str(omni.usd.get_stage_next_free_path(self._preview_stage, root, True))
        return self._source_skel_root_path

    def get_joint_prim_paths(self) -> List[Sdf.Path]:
        result = []
        if self.skeleton_prim:
            def is_joint(prim: Usd.Prim, path) -> bool:
                return prim.GetTypeName() in ['OmniJoint']
            result = traverse_prim(self._preview_stage, self.skeleton_prim.GetPath(), is_joint)
        return result

    def _get_default_skeleton_root_path(self) -> str:
        return PREVIEW_STAGE_SKELROOT_PATH + '/Root'

    def is_animation(self, prim: Usd.Prim) -> bool:
        """ Returns whether a prim is a supported skeleton animation
        """
        if prim is None or not prim.IsValid():
            return False
        return prim.IsA(UsdSkel.Animation)

    def is_skeleton(self, prim: Usd.Prim) -> bool:
        """ Returns whether a prim is a supported skeleton
        """
        if prim is None or not prim.IsValid():
            return False
        return prim.IsA(UsdSkel.Skeleton) or prim.GetTypeName() == 'SkelRoot'

    @property
    def is_skeleton_selected(self) -> bool:
        return self._is_skeleton_selected

    def select_skeleton(self, select: bool = True):
        """ Selects or unselects the current skeleton in the preview stage
        """
        if not self._preview_stage:
            self._is_skeleton_selected = select
            return
        if self._is_skeleton_selected == select:
            return
        self._is_skeleton_selected = select
        if select:
            selection = [self.get_skeleton_root_path()]
            skel_prim = self._preview_stage.GetPrimAtPath(self.get_skeleton_root_path())
            assert(skel_prim is not None)
            children = skel_prim.GetChildren()
            if len(children) > 0:
                selection.append(str(children[0].GetPath()))
            self._preview_context.get_selection().set_selected_prim_paths(selection, True)
        else:
            self._preview_context.get_selection().set_selected_prim_paths([], False)

    def get_skeleton_paths(self):
        """ Returns paths to all loaded skeletons in the preview stage.
        """
        if not self._stage_active:
            return []
        char_prim = self._preview_stage.GetPrimAtPath(PREVIEW_STAGE_SKELROOT_PATH)
        skeletons = []
        if char_prim is not None and char_prim.IsValid():
            for child in char_prim.GetAllChildren():
                prim_name = child.GetPath().MakeRelativePath(child.GetPath().GetParentPath())
                if str(prim_name).startswith('Root'):
                    skeletons.append(child.GetPath())
        return skeletons

    def _on_anim_source_item_changed(self, source: SourceSetModel, item: SourceItemModel):
        if item is not None:
            if source.get_current_source() == item.model:  # switch if changed item became current
                self._switch_preview_anim(item.model)

    def _on_skel_source_item_changed(self, source: SourceSetModel, item: SourceItemModel):
        if item is not None:
            self._switch_preview_skel(item.model)

    def _switch_preview_anim(self, source: SourceModel):
        target_list = []
        anim_prim = None
        if source is not None:
            anim_prim = self._preview_stage.GetPrimAtPath(source.target_path_in_stage)
            if anim_prim.IsValid():
                target_list = [source.target_path_in_stage]
        if self._skeleton is not None and self._skeleton.IsValid():
            with Usd.EditContext(self._preview_stage,
                    self._preview_stage.GetEditTargetForLocalLayer(self._preview_stage.GetSessionLayer())):
                UsdSkel.BindingAPI.Apply(self._skeleton)
                UsdSkel.BindingAPI(self._skeleton).CreateAnimationSourceRel().SetTargets(target_list)

        if len(target_list) > 0:
            self._update_time_ranges(anim_prim)

            for callback in self._callback_animation_changed:
                callback(
                    source_path=source.source_path_in_stage,
                    target_path=source.target_path_in_stage,
                    external_url=source.source_url,
                    annotations=source.payload
                )

    def _get_time_codes_per_second(self, anim_prim):
        curr_stage = omni.usd.get_context().get_stage()
        prim_stack = anim_prim.GetPrimStack()
        for prim_spec in prim_stack:
            if prim_spec.hasPayloads:
                payloads = []
                payloads += prim_spec.payloadList.prependedItems
                payloads += prim_spec.payloadList.explicitItems
                payloads += prim_spec.payloadList.addedItems
                payloads += prim_spec.payloadList.appendedItems
                payloads += prim_spec.payloadList.orderedItems
                for payload in payloads:
                    stage = Usd.Stage.Open(prim_spec.layer.ComputeAbsolutePath(payload.assetPath))
                    time_codes_per_second = float(stage.GetTimeCodesPerSecond())
                    return time_codes_per_second
        return float(curr_stage.GetTimeCodesPerSecond())

    def set_preview_anim(
        self,
        path: Union[str, Sdf.Path],
        stage_copy_from: Optional[Usd.Stage] = None,
        external_url: Optional[str] = None,
        load_annotations: bool = True,
        set_current: bool = True
    ) -> bool:
        """ Sets the preview animation
        Args:
            path: path to the animation prim
            stage_copy_from: stage where the animation prim is located.
            external_url: URL to the source file or None if the source is an open stage (e.g. the main)
            load_annotations: True to load annotations attached to the animation prim, if there's any.
            set_current: True to make the new item the current, False to simply add it to the list
        Returns:
            True on success, False otherwise
        """
        if not self._stage_active:
            self.load_stage()

        if stage_copy_from is None:
            stage_copy_from = omni.usd.get_context().get_stage()
        if stage_copy_from is None:
            carb.log_error('Preview set_preview_anim: Default stage is not accessible')
            return False

        anim_prim_path = str(path)

        # main stage, not preview context
        anim_prim = stage_copy_from.GetPrimAtPath(anim_prim_path)

        if anim_prim is None or not anim_prim.IsValid():
            carb.log_error('Prim {} is invalid'.format(anim_prim_path))
            return False
        if not self.is_animation(anim_prim):
            carb.log_error('Prim {} is not a skeleton animation'.format(anim_prim_path))
            return False

        def same_source(source: SourceModel) -> bool:
            return  source.source_url == external_url and \
                    source.source_path_in_stage == anim_prim_path and \
                    (source.is_external or (not source.is_external and source.exists_in_source_stage))
        matches = self._anim_source_model.find_source(same_source)
        if len(matches) == 0:
            with Usd.EditContext(self._preview_stage,
                                 self._preview_stage.GetEditTargetForLocalLayer(self._preview_stage.GetRootLayer())):

                target_path = Sdf.Path(anim_prim_path)
                anim_root_path = self.get_anim_root_path(True)  # True to avoid re-creation of the same prim
                self._src_time_codes_per_second_maps[anim_root_path] = self._get_time_codes_per_second(anim_prim)
                self._loaded_time_codes_per_second_maps[anim_root_path] = omni.usd.get_context().get_stage().GetTimeCodesPerSecond()
                self._anim_root_path = anim_root_path
                # self.remove_animations()  # do not remove them
                self._preview_stage.DefinePrim(anim_root_path)

                selected_path_postfix = target_path.MakeRelativePath(target_path.GetParentPath())
                target_path = Sdf.Path(anim_root_path).AppendChild(str(selected_path_postfix))
                copy_prim_to_stage(stage_copy_from, Sdf.Path(anim_prim_path), self._preview_stage, target_path)

                # Clear whatever bindings it had
                new_anim_prim = self._preview_stage.GetPrimAtPath(target_path)
                #new_anim_prim.RemoveProperty('animationSkelBinding:sourceSkeleton')

                source_skeleton_path = None
                source_skel_rel =  new_anim_prim.GetRelationship('animationSkelBinding:sourceSkeleton')
                if source_skel_rel is not None:
                    targets = source_skel_rel.GetTargets()
                    if targets and len(targets) > 0:
                        source_skeleton_path = targets[0]

                if source_skeleton_path is not None:
                    prim = stage_copy_from.GetPrimAtPath(source_skeleton_path)
                    skel = UsdSkel.Skeleton(prim)

                    def same_source_skeleton(source: SourceModel) -> bool:
                        return  source.source_url == external_url and \
                                source.source_path_in_stage == source_skeleton_path and \
                                (source.is_external or (not source.is_external and source.exists_in_source_stage))
                    matches = self._source_skel_source_model.find_source(same_source_skeleton)
                    target_skel_path = Sdf.Path.emptyPath
                    if len(matches) == 0:
                        prim_name = source_skeleton_path.name
                        skeleton_root = self.get_source_skeleton_root_path(True)
                        target_skel_path = Sdf.Path(skeleton_root).AppendChild(str(prim_name))
                        copy_prim_to_stage(stage_copy_from, Sdf.Path(source_skeleton_path), self._preview_stage, target_skel_path)

                        skel_prim = self._preview_stage.GetPrimAtPath(target_skel_path)
                        geom = UsdGeom.Imageable(skel_prim)
                        geom.MakeInvisible()

                        skel_source = SourceModel()
                        skel_source.set_source_path_in_stage(source_skeleton_path, stage_copy_from)
                        skel_source.target_path_in_stage = str(target_skel_path)
                        skel_source.set_source_url(external_url)
                        self._source_skel_source_model.add_source(source=skel_source, set_current=False)
                    else:
                        target_skel_path = matches[0][0].target_path_in_stage

                    if target_skel_path != Sdf.Path.emptyPath:
                        rel = new_anim_prim.CreateRelationship('animationSkelBinding:sourceSkeleton')
                        rel.SetTargets([target_skel_path])

                source = SourceModel()
                source.set_source_path_in_stage(str(anim_prim_path), stage_copy_from)
                source.target_path_in_stage = target_path
                source.set_source_url(external_url)
                source.payload = AnnotationSet(parent_anim=source, time_codes_per_second=self._src_time_codes_per_second_maps[anim_root_path])
                if load_annotations:
                    annotations = extract_annotations(anim_prim, source)
                    # The reason we attach the annoations as a "payload" to sources is that the animation may come
                    #   from an external file, and we don't want to reload the file to parse the annotation
                    #   when we switch clips.
                    source.payload.set_annotations(annotations)
                # NOTE: this triggers self._on_anim_source_item_changed
                self._anim_source_model.add_source(source=source, set_current=set_current)

                for callback in self._callback_animation_loaded:
                    callback(
                        source_path=anim_prim_path,
                        target_path=target_path,
                        source_stage=stage_copy_from,
                        external_url=external_url,
                        annotations=source.payload
                    )
        elif set_current:
            self._anim_source_model.set_current(matches[0][1])
            self._anim_root_path =\
                str(self._anim_source_model.get_current_source().target_path_in_stage.GetParentPath())

        return True

    def _update_time_ranges(self, selected_prim: Usd.Prim):
        """ Updates the start and end times of the timeline to match the skeleton animation
        Args:
            selected_prim: the animation prim
        """
        self.stop()

        def update(time_codes_per_second, t_min, t_max):
            start_time = t_min / float(time_codes_per_second)
            end_time = t_max / float(time_codes_per_second)
            self._timeline.set_time_codes_per_second(time_codes_per_second)
            self._timeline.set_zoom_range(start_time, end_time)
            self._timeline.set_start_time(start_time)
            self._timeline.set_end_time(end_time)
            zoom_state: zoom_handler.ZoomState = zoom_handler.ZoomHandler().get_zoom(self._preview_context_name)
            zoom_state.normal_range = zoom_handler.Range(t_min, t_max)
            zoom_state.clear_zoom()
            self.play()

        path = str(selected_prim.GetPath().GetParentPath())
        skel_anim = UsdSkel.Animation(selected_prim)
        has_samples, t_min, t_max = self.get_time_samples_interval(skel_anim)
        if not has_samples:
            t_min = 0
            t_max = 0
        if path in self._loaded_time_codes_per_second_maps:
            loaded_tcps = self._loaded_time_codes_per_second_maps[path]
            current_tcps = float(omni.usd.get_context().get_stage().GetTimeCodesPerSecond())
            t_min = t_min * loaded_tcps / current_tcps
            t_max = t_max * loaded_tcps / current_tcps
            update(current_tcps, t_min, t_max)
        else:
            time_codes_per_second = omni.usd.get_context().get_stage().GetTimeCodesPerSecond()
            update(time_codes_per_second, t_min, t_max)

    def reset_scene(self):
        """ Resets state to its default.
        """
        self.stop()
        start_time, end_time = 0, 0
        self._timeline.set_start_time(start_time)
        self._timeline.set_end_time(end_time)
        if self.stage_active:
            self.remove_animations()
            self.remove_skeletons()

    def _is_valid_skeleton(self, prim, path_str):
        """ Returns whether prim is a skeleton we support and can load
        """
        if prim is None or not prim.IsValid():
            # carb.log_error('Prim {} is invalid'.format(path_str))
            return False

        if prim.GetTypeName() == 'Skeleton':
            return True
        if prim.GetTypeName() != 'SkelRoot':
            # TODO: We need to test without throwing errors. Refactor the errors where needed.
            # carb.log_error('Prim {} is not a Skeleton or SkelRoot'.format(path_str))
            return False

        for child in Usd.PrimRange(prim):
            if child.GetTypeName() == 'Skeleton':
                return True

        # carb.log_warn('Prim {} has no Skeleton'.format(path_str))
        return False

    def _switch_preview_skel(self, source: SourceModel):
        assert(source is not None)

        self._i_omniskel.remove_omni_skel(self._preview_context_name)

        # remove current binding
        if self._skeleton is not None and self._skeleton.IsValid():
           self._switch_preview_anim(None)  # this removes the current binding

        # find new parent prim and activate it
        new_skel_prim = self._preview_stage.GetPrimAtPath(Sdf.Path(source.target_path_in_stage).GetParentPath())
        assert(new_skel_prim.IsValid())
        new_skel_prim.SetActive(True)

        # find new skeleton prim
        self._skeleton = None
        source_prim = self._preview_stage.GetPrimAtPath(source.target_path_in_stage)

        if not source_prim.IsValid():
            return

        # find skeleton
        if source_prim.GetTypeName() == 'Skeleton':
            self._skeleton = source_prim
        else:
            for child in Usd.PrimRange(source_prim):
                if child.GetTypeName() == 'Skeleton':
                    self._skeleton = child
                    break
        assert(self._skeleton is not None and self._skeleton.IsValid())

        skeleton_root_path = self.get_skeleton_root_path()
        # de-activate old skeleton if we are not setting the same skeleton
        if skeleton_root_path is not None and str(self._skeleton.GetPath().GetParentPath()) != skeleton_root_path:
            old_skel_prim = self._preview_stage.GetPrimAtPath(skeleton_root_path)
            if old_skel_prim.IsValid():
                old_skel_prim.SetActive(False)
        self._skeleton_root_path = str(Sdf.Path(source.target_path_in_stage).GetParentPath())

        # Clear the current animation, we'll set it later if needed
        self._switch_preview_anim(None)

        self._i_omniskel.add_omni_skel(self._preview_context_name, omni.anim.skelJoint.FabricUseType.OFF)
        self._mesh_paths = None

        asyncio.ensure_future(self._apply_anim())

        # OM-85112: we must caluclate geometry center after animation is applied
        asyncio.ensure_future(self.compute_geo_center())

        self.set_show_mesh(self._show_mesh)
        self.set_show_skeleton(self._show_skeleton)

        for callback in self._callback_skeleton_changed:
            callback(
                source_path=source.source_path_in_stage,
                target_path=source.target_path_in_stage
            )

    async def compute_geo_center(self):
        """
        OM-85112: Wait until animation is loaded completely before geometry bounds are calculated.
        this is because some geometries might have non-uniform scale values, which stretches
        the geo, but after animation is applied, the geometry gets fixed, so we can get the proper geo bounds
        """
        await omni.kit.app.get_app().next_update_async()
        self._skeleton_geom = SkeletonGeometry()
        self._skeleton_geom.compute(self._skeleton)

    async def _apply_anim(self):
        """ Applies the current animation to the current skeleton.
        """
        # A small delay is added to make it work when this is called right after skeleton loading.
        await omni.kit.app.get_app().next_update_async()

        if not self._stage_active:
            return
        animroot_prim = self._preview_stage.GetPrimAtPath(self.get_anim_root_path())
        if animroot_prim is not None and animroot_prim.IsValid():
            anims = animroot_prim.GetChildren()
            if anims is not None and len(anims) > 0:
                anim = anims[0]
                if self._skeleton:
                    with Usd.EditContext(self._preview_stage,
                            self._preview_stage.GetEditTargetForLocalLayer(self._preview_stage.GetSessionLayer())):
                        UsdSkel.BindingAPI(self._skeleton).CreateAnimationSourceRel().SetTargets([anim.GetPrimPath()])
        self._mesh_paths = None

    def set_preview_skeleton(
            self,
            path: Union[str, Sdf.Path],
            stage_copy_from: Optional[Usd.Stage] = None,
            external_url: Optional[str] = None,
        ) -> bool:
        """ Sets the preview skeleton
        Args:
            path: path to the animation prim
            stage_copy_from: stage where the skeleton prim is located. Pass None to specify the main stage.
            external_url: URL to the source file or None if the source is an open stage (e.g. the main)
        Returns:
            True on success, False otherwise
        """
        if not self._stage_active:
            self.load_stage()

        if stage_copy_from is None:
            stage_copy_from = omni.usd.get_context().get_stage()
        if stage_copy_from is None:
            carb.log_error('Default stage is not accessible')
            return False

        path_str = str(path)
        prim = stage_copy_from.GetPrimAtPath(Sdf.Path(path_str))
        if not self._is_valid_skeleton(prim, path_str):
            return False

        def same_source(source: SourceModel) -> bool:
            return  source.source_url == external_url and \
                    source.source_path_in_stage == path_str and \
                    (source.is_external or (not source.is_external and source.exists_in_source_stage))

        def get_resolve_data(prim: Usd.Prim, attr_name):
            cur_prim = prim
            while cur_prim:
                attr = cur_prim.GetAttribute(attr_name)
                if attr:
                    return attr.Get()
                cur_prim = cur_prim.GetParent()
            return None

        matches = self._skel_source_model.find_source(same_source)
        if len(matches) == 0:
            # avoid crashes during deletion of stage objects
            self._i_omniskel.remove_omni_skel(self._preview_context_name)

            # paste new skeleton
            prim_name = prim.GetPrimPath().MakeRelativePath(prim.GetPrimPath().GetParentPath())
            skeleton_root = self.get_skeleton_root_path(True)
            self._preview_stage.DefinePrim(Sdf.Path(skeleton_root))
            target_path = Sdf.Path(skeleton_root).AppendChild(str(prim_name))
            copy_prim_to_stage(stage_copy_from, prim.GetPath(), self._preview_stage, target_path)
            # need copy binding matrails
            for material_path in get_material_bindings(prim):
                copy_prim_to_stage(stage_copy_from, material_path, self._preview_stage, material_path)

            # clear translation of the inserted prim
            inserted_prim = self._preview_stage.GetPrimAtPath(target_path)
            if inserted_prim.HasAttribute('xformOp:translate'):
                inserted_prim.GetAttribute('xformOp:translate').Set(Gf.Vec3d(0, 0, 0))

            # adjust rotation
            up_axis = UsdGeom.GetStageUpAxis(stage_copy_from)
            root_prim = self._preview_stage.GetPrimAtPath(skeleton_root)

            rotate_x = get_resolve_data(prim, XFORM_OP_ROTATE_UNITSRESOLVE_ATTR) or 0
            self._skel_up_axis[skeleton_root] = (up_axis, [rotate_x, 0, 0])
            self.align_skel_up_axis_to_current_stage_up_axis(skeleton_root, up_axis, [rotate_x, 0, 0])

            scale = get_resolve_data(prim, XFORM_OP_SCALE_UNITSRESOLVE_ATTR)
            if scale is not None:
                if not root_prim.HasAttribute('xformOp:scale'):
                    UsdGeom.Xformable(root_prim).AddScaleOp()
                scale_attr = root_prim.GetAttribute("xformOp:scale")
                if scale_attr is not None:
                    scale_attr.Set(scale)

            source = SourceModel()
            source.set_source_path_in_stage(path_str, stage_copy_from)
            source.target_path_in_stage = str(inserted_prim.GetPath())
            source.set_source_url(external_url)
            # NOTE: this triggers _on_skel_source_item_changed
            self.skel_source_model.add_source(source=source, set_current=True)

            for callback in self._callback_skeleton_loaded:
                callback(source_path=path_str, target_path=self._skeleton.GetPath(), source_stage=stage_copy_from)
            if external_url is not None:
                self._external_skels.add(str(inserted_prim.GetPath().GetParentPath()))

        else:
            self._skel_source_model.set_current(matches[0][1])

        return True

    def get_time_samples_interval(self, skel_anim):
        """ Extracts time ranges from a skeleton animation.
        Args:
            skel_anim: a skeleton animation property
        Returns:
            bool: True if the animation has time samples
            float: start time in time codes
            float: end time in time codes
        """
        attribute_getters = ['GetTranslationsAttr', 'GetRotationsAttr', 'GetJointsAttr', 'GetScalesAttr']
        t_min, t_max = float('inf'), -float('inf')
        has_samples = False
        for attr in attribute_getters:
            getter = getattr(type(skel_anim), attr)
            skel_attr = getter(skel_anim)
            if skel_attr is not None:
                time_samples = skel_attr.GetTimeSamples()
                if time_samples is not None and len(time_samples) > 0:
                    has_samples = True
                    t_min = min(t_min, time_samples[0])
                    t_max = max(t_max, time_samples[-1])
        return has_samples, t_min, t_max

    def get_compatibility(self) -> Tuple[AnimationCompatibilty, List[str], List[str], List[str]]:
        """
        Returns the compatibility information of the current skeleton and animation a
        Tuple[AnimationCompatibilty, List[str], List[str], List[str]]
        The lists are, in order:
        - List of common joint names
        - List of joint names that are present only in the animation, i.e. they don't apply to the skeleton
        - List of joint names that are present only in the skeleton, i.e. they are not animated by the animation

        Return value is None is there's no skeleton or animation in the animation preview window.
        """
        anim_prim = self.animation_prim
        if anim_prim is None or self._skeleton is None:
            return None
        common_joints, anim_only_joints, skel_only_joints = check_compatibility(self._skeleton, anim_prim)
        compatibility = AnimationCompatibilty.INCOMPATIBLE
        if len(common_joints) > 0:  # need to have at least one joint in common for at least partial compatibility
            if len(anim_only_joints) == 0:  # all joints in the animation are present in the skeleton
                compatibility = AnimationCompatibilty.COMPATIBLE
            else:
                compatibility = AnimationCompatibilty.PARTIAL
        return [compatibility, common_joints, anim_only_joints, skel_only_joints]

    def add_to_stage(
        self,
        target_context: omni.usd.UsdContext,
        target_stage: Usd.Stage,
        source: SourceModel,
        as_payload: bool,
        prim_only: bool = True
    ):
        """
        Adds a source to a stage either by copying it or as payload.
        """
        if source is None or (not source.is_external and source.exists_in_source_stage):
            return
        target_context = omni.usd.get_context()
        target_stage = target_context.get_stage()
        if target_stage is None or self._preview_stage is None:
            return

        source_stage = self._preview_stage
        prim = source_stage.GetPrimAtPath(source.target_path_in_stage)
        if prim.IsValid():
            root = '/AnimationPreview_import'
            name = source.source_path_in_stage.split('/')[-1]
            target_path = Sdf.Path(root).AppendChild(name)
            target_path = omni.usd.get_stage_next_free_path(target_stage, target_path, True)
            if as_payload:
                if prim_only:
                    omni.kit.commands.execute(
                        'CreatePayloadCommand',
                        usd_context=target_context,
                        path_to=target_path,
                        asset_path=source.source_url,
                        prim_path=source.source_path_in_stage,
                        select_prim=True,
                    )
                else:
                    omni.kit.commands.execute(
                        'CreatePayloadCommand',
                        usd_context=target_context,
                        path_to=target_path,
                        asset_path=source.source_url,
                        select_prim=True,
                    )
            else:
                copy_prim_to_stage(source_stage, source.target_path_in_stage, target_stage, target_path)
                # When mesh rendering is off, all meshes are invisible, so we turn everything visible after insertion
                inserted_prims = traverse_prim(target_stage, target_path)
                vis_token = 'inherited'
                for path in inserted_prims:
                    prim = target_stage.GetPrimAtPath(path)
                    if prim.HasAttribute('visibility'):
                        prim.GetAttribute('visibility').Set(vis_token)
                # it was deleted but we re-add it to the stage
                if not source.is_external:
                    source.source_path_in_stage = target_path
                    source.set_removed(False)
                target_context.get_selection().set_selected_prim_paths([target_path], True)

    @property
    def anim_source_model(self) -> SourceSetModel:
        """
        The set of all animation sources
        """
        return self._anim_source_model

    @property
    def animation_prim(self) -> Usd.Prim:
        """
        The current animation prim, or None if there's no animation
        """
        current_source = self._anim_source_model.get_current_source()
        if current_source:
            animation_prim = self._preview_stage.GetPrimAtPath(current_source.target_path_in_stage)
            if animation_prim is not None and animation_prim.IsValid():
                return animation_prim
        return None

    @property
    def skel_source_model(self) -> SourceSetModel:
        """
        The set of all skeleton sources
        """
        return self._skel_source_model

    @property
    def skeleton_prim(self) -> Usd.Prim:
        """
        The current skeleton prim, or None if there's no skeleton (e.g. when the stage is not loaded)
        """
        return self._skeleton

    @property
    def skel_geometry(self) -> SkeletonGeometry:
        """
        A descriptor containing geometric properties of the skeleton, such as height
        """
        return self._skeleton_geom

    @property
    def annotation_model(self) -> AnnotationSet:
        """
        The set of annotations of the current animation
        """
        if self._anim_source_model is None or self._anim_source_model.get_current_source() is None:
            return None
        return self._anim_source_model.get_current_source().payload

    @property
    def timeline(self) -> omni.timeline.Timeline:
        """
        The timeline object
        """
        return self._timeline

    @property
    def timeline_name(self) -> str:
        """
        The name of the timeline object
        """
        return self._timeline_name

    @property
    def context_name(self) -> str:
        """
        Name of the preview USD context
        """
        return self._preview_context_name

    @property
    def context(self) -> omni.usd.UsdContext:
        """
        The USD context that is used by the preview window to store and visualize content
        """
        return self._preview_context

    @property
    def stage_active(self) -> bool:
        """
        Has the stage load process started?
        """
        return self._stage_active

    def stop(self):
        """
        Stops the timeline.
        """
        self._timeline.stop()

    def play(self):
        """
        Plays the timeline.
        """
        self._timeline.play()

    def pause(self):
        """
        Pauses the timeline.
        """
        self._timeline.pause()

    def register_stage_loaded(self, callback: Callable[[], None]):
        """
        Registers a new Callable that is called when the preview stage is loaded.
        """
        if (callback not in self._callback_stage_loaded):
            self._callback_stage_loaded.append(callback)

    def unregister_stage_loaded(self, callback):
        """
        Unregisters a callback that was set with register_stage_loaded.
        """
        if (callback in self._callback_stage_loaded):
            self._callback_stage_loaded.remove(callback)

    def register_skeleton_loaded(self, callback: Callable[[str, str, Usd.Stage], None]):
        """
        Registers a new Callable that is called when a new skeleton is loaded.

        Args:
            callback: Callback function with parameters
              - source_path (str): path to the source skeleton prim in its original stage
              - target_path (str): path to the new skeleton prim in the preview stage
              - source_stage (Usd.Stage): source stage of the skeleton prim
        """
        if (callback not in self._callback_skeleton_loaded):
            self._callback_skeleton_loaded.append(callback)

    def unregister_skeleton_loaded(self, callback):
        """
        Unregisters a callback that was set with register_skeleton_loaded.
        """
        if (callback in self._callback_skeleton_loaded):
            self._callback_skeleton_loaded.remove(callback)

    def register_animation_loaded(self, callback: Callable[[str, str, Usd.Stage, str, AnnotationSet], None]):
        """
        Registers a new Callable that is called when a new animation is loaded.

        Args:
            callback: Callback function with parameters
              - source_path (str): path to the source animation prim in its original stage
              - target_path (str): path to the new animation prim in the preview stage
              - source_stage (Usd.Stage): source stage of the animation prim
              - external_url (str): URL of the source file where the source prim came from,
                                    or None if it came from the main stage
              - annotations (AnnotationSet): annotations of the animation, or None
        """
        if (callback not in self._callback_animation_loaded):
            self._callback_animation_loaded.append(callback)

    def unregister_animation_loaded(self, callback):
        """
        Unregisters a callback that was set with register_animation_loaded.
        """
        if (callback in self._callback_animation_loaded):
            self._callback_animation_loaded.remove(callback)

    def register_skeleton_changed(self, callback: Callable[[str, str], None]):
        """
        Registers a new Callable that is called when the previewed skeleton is changed.

        Args:
            callback: Callback function with parameters
              - source_path (str): path to the source skeleton prim in its original stage
              - target_path (str): path to the skeleton prim in the preview stage
        """
        if (callback not in self._callback_skeleton_changed):
            self._callback_skeleton_changed.append(callback)

    def unregister_skeleton_changed(self, callback):
        """
        Unregisters a callback that was set with register_skeleton_changed.
        """
        if (callback in self._callback_skeleton_changed):
            self._callback_skeleton_changed.remove(callback)

    def register_animation_changed(self, callback: Callable[[str, str, str, AnnotationSet], None]):
        """
        Registers a new Callable that is called when the previewed animation is changed.

        Args:
            callback: Callback function with parameters
              - source_path (str): path to the source animation prim in its original stage
              - target_path (str): path to the animation prim in the preview stage
              - source_stage (Usd.Stage): source stage of the animation prim
              - external_url (str): URL of the source file where the source prim came from,
                                    or None if it came from the main stage
              - annotations (AnnotationSet): annotations of the animation, or None
        """
        if (callback not in self._callback_animation_changed):
            self._callback_animation_changed.append(callback)

    def unregister_animation_changed(self, callback):
        """
        Unregisters a callback that was set with register_animation_changed.
        """
        if (callback in self._callback_animation_changed):
            self._callback_animation_changed.remove(callback)
