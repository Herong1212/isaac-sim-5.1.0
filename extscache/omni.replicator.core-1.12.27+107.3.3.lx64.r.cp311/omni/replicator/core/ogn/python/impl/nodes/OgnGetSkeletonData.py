# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import carb
import carb.profiler
import numpy as np
import omni.graph.core as og
import omni.kit
import omni.syntheticdata as sd
import omni.timeline
import omni.usd
import usdrt
import warp as wp
from pxr import Gf, Semantics, Usd, UsdGeom, UsdSemantics, UsdSkel, Vt


def get_wp_array(ptr, shape, strides, dtype, source_device, target_device):
    wp_arr = wp.types.array(
        dtype=dtype,
        shape=shape,
        strides=strides,
        ptr=ptr,
        device=source_device,
        requires_grad=False,
    )
    if source_device != target_device:
        output_wp_arr = wp.empty_like(wp_arr, device=target_device)
        wp.copy(output_wp_arr, wp_arr)
        return output_wp_arr
    return wp_arr


def get_device(device_idx):
    if device_idx < 0:
        return "cpu"
    return f"cuda:{device_idx}"


class OgnGetSkeletonDataInternalState:
    def __init__(self):
        self._skel_to_skel_root = {}
        self._joint_to_skel_root = {}
        self._skel_root_to_num_joints = {}
        self._skel_roots = set()

    def add_joint_count_to_skel_root(self, skel_root, count) -> None:
        self._skel_root_to_num_joints[skel_root] = count

    def add_skel_entry(self, skel, skel_root) -> None:
        self._skel_to_skel_root[skel] = skel_root

    def add_joint_entry(self, joint, skel_root) -> None:
        self._joint_to_skel_root[joint] = skel_root

    def add_skel_root(self, skel_root) -> None:
        if skel_root not in self._skel_roots:
            self._skel_roots.add(skel_root)

    def get_root_of_joint(self, joint) -> str:
        if joint in self._joint_to_skel_root:
            return self._joint_to_skel_root[joint]
        return ""

    def get_root_of_skel(self, skel) -> str:
        if skel in self._skel_to_skel_root:
            return self._skel_to_skel_root[skel]
        return ""

    def get_skel_root_to_joint_count(self, skel_root) -> int:
        if skel_root in self._skel_root_to_num_joints:
            return self._skel_root_to_num_joints[skel_root]
        return 0

    def has_skel_root_entry(self, skel_root) -> bool:
        return skel_root in self._skel_roots


@carb.profiler.profile
def _ftheta_distortion(ftheta, x):
    """F-Theta distortion."""
    return ftheta["poly_a"] + x * (
        ftheta["poly_b"]
        + x * (ftheta["poly_c"] + x * (ftheta["poly_d"] + x * (ftheta["poly_e"] + x * ftheta["poly_f"])))
    )


@carb.profiler.profile
def _get_view_params(db):
    world_to_view = np.array(db.inputs.cameraViewTransform).reshape(4, 4)
    stage = omni.usd.get_context().get_stage()
    render_product = db.inputs.renderProductPath
    render_product_prim = stage.GetPrimAtPath(render_product)
    width, height = render_product_prim.GetAttribute("resolution").Get()
    projection_type = db.inputs.cameraModel

    if projection_type == "fisheyePolynomial":
        ftheta = {
            "width": db.inputs.cameraFisheyeNominalWidth,
            "height": db.inputs.cameraFisheyeNominalHeight,
            "cx": db.inputs.cameraFisheyeOpticalCentre[0],
            "cy": db.inputs.cameraFisheyeOpticalCentre[1],
            "poly_a": db.inputs.cameraFisheyePolynomial[0],
            "poly_b": db.inputs.cameraFisheyePolynomial[1],
            "poly_c": db.inputs.cameraFisheyePolynomial[2],
            "poly_d": db.inputs.cameraFisheyePolynomial[3],
            "poly_e": db.inputs.cameraFisheyePolynomial[4],
            "poly_f": db.inputs.cameraFisheyePolynomial[5],
            "max_fov": db.inputs.cameraFisheyeMaxFOV,
        }
        ftheta["edge_fov"] = _ftheta_distortion(ftheta, ftheta["width"] / 2)
        ftheta["c_ndc"] = np.array(
            [
                (ftheta["cx"] - ftheta["width"] / 2) / ftheta["width"],
                (ftheta["height"] / 2 - ftheta["cy"]) / ftheta["width"],
            ]
        )
    else:
        ftheta = None
    try:
        view_to_world = np.linalg.inv(np.array(world_to_view))
    except np.linalg.LinAlgError:
        carb.log_warn("Can't invert world_to_view matrix!")
        view_to_world = np.array(world_to_view)

    return {
        "view_to_world": view_to_world,
        "world_to_view": np.array(world_to_view),
        "projection_type": projection_type,
        "ftheta": ftheta,
        "width": width,
        "height": height,
        "aspect_ratio": width / height,
        "clipping_range": db.inputs.cameraNearFar,
        "horizontal_aperture": db.inputs.cameraAperture[0],
        "focal_length": db.inputs.cameraFocalLength,
        "projection_matrix": db.inputs.cameraProjection.reshape(4, 4),
    }


@carb.profiler.profile
def _convert_to_pxr_list(fabric_gf_list):
    result = []
    for i in fabric_gf_list:
        result.append(usdrt.Gf.convertToPxr(i))
    return result


@carb.profiler.profile
def _get_skelroot_prim_from_skeleton(stage, skel_prim_path):
    # Find SkelRoot prim from Skeleton by traversing upwards until pesudo root.
    skel_prim = stage.GetPrimAtPath(skel_prim_path)
    curr_prim = skel_prim.GetParent()

    while not curr_prim.IsPseudoRoot():
        if curr_prim.GetTypeName() == "SkelRoot":
            return curr_prim
        curr_prim = curr_prim.GetParent()

    return None


@carb.profiler.profile
def _get_parent_indices(joints):
    joint_parent_map = {}

    for joint in joints:
        joint_array = joint.split("/")

        if len(joint_array) == 1:
            joint_parent_map[joint_array[0]] = None
        else:
            joint_parent_map[joint_array[-1]] = joint_array[-2]

    new_joints = list(joint_parent_map.keys())
    parent_indices = [new_joints.index(j) for j in (list(joint_parent_map.values())[1:])]
    parent_indices = [-1] + parent_indices
    return parent_indices


@carb.profiler.profile
def get_asset_path_from_prim_path(prim_path):
    stage = omni.usd.get_context().get_stage()
    if prim_path:
        prim = stage.GetPrimAtPath(str(prim_path))
    else:
        raise ValueError("Prim path can not be empty!")

    if prim.IsValid():
        asset_path = omni.usd.get_composed_references_from_prim(prim)[0][0].assetPath
    else:
        raise ValueError(f"Prim with path `{prim_path}` is invalid!")

    return asset_path


@carb.profiler.profile
def get_anim_variant_from_prim_path(char_anim_dup_path):
    """Get animation variant path"""
    if not char_anim_dup_path:
        raise ValueError(f"Path `{char_anim_dup_path}` is invalid")
    stage = omni.usd.get_context().get_stage()
    dup_prim = stage.GetPrimAtPath(str(char_anim_dup_path))
    var_select = None
    # search chilid node has variatntSets name animationVariant
    for child in dup_prim.GetChildren():
        if child.GetPrimTypeInfo().GetTypeName() == "Xform":
            if child.HasVariantSets:
                var_set = child.GetVariantSet("animationVariant")
                var_select = var_set.GetVariantSelection()
                if var_select:
                    break
    return var_select


@carb.profiler.profile
def compute_2d_translations(points, view_params, skel_data):
    # Compute world-to-image transforms given translation points
    if np.linalg.det(view_params["world_to_view"]) == 0.0:
        carb.log_warn("View matrix determinant is 0.0, can't calculate 2D joint translations!")
        skel_data["translations_2d"] = []
        skel_data["in_view"] = False
    else:
        joint_pos2d = sd.helpers.world_to_image(points, None, view_params)[:, :2]

        joint_pos2d *= np.array([view_params["width"], view_params["height"]])
        skel_data["translations_2d"] = joint_pos2d.tolist()

        # Check if the current skeleton is in view of the viewport
        skel_data["in_view"] = not (
            np.any(joint_pos2d[:, 0] < 0)
            or np.any(joint_pos2d[:, 0] > view_params["width"])
            or np.any(joint_pos2d[:, 1] < 0)
            or np.any(joint_pos2d[:, 1] > view_params["height"])
        )


@carb.profiler.profile
def get_world_transform_for_ag_character(ag_character):
    # This function is currently not used for future support for omni.anim.graph.core's get_character api
    """Obtain the LocalToWorld Transformations excluding scale of a given
    SkelRoot.
    """
    pos = carb.Float3()
    rot = carb.Float4()
    ag_character.get_world_transform(pos, rot)
    return pos, rot


@carb.profiler.profile
def compute_local_to_world_transforms_fabric(fabric_data, root_paths):
    # TODO: Parallelize with warp/cuda to improve efficiency
    for root_path in root_paths:
        world_pos = (
            fabric_data[root_path]["world_position"] if fabric_data[root_path]["world_position"] else usdrt.Gf.Vec3d(0)
        )
        world_ori = (
            fabric_data[root_path]["world_orientation"]
            if fabric_data[root_path]["world_orientation"]
            else usdrt.Gf.Quatf(1)
        )
        world_scl = (
            fabric_data[root_path]["world_scale"] if fabric_data[root_path]["world_scale"] else usdrt.Gf.vec3f(1)
        )

        # Combine the transforms
        scale = usdrt.Gf.Matrix4d()
        rot = usdrt.Gf.Matrix4d()

        scale.SetScale(world_scl)
        rot.SetRotate(world_ori)

        view_to_world = scale * rot
        view_to_world.SetTranslateOnly(world_pos)
        fabric_data[root_path]["local_to_world"] = view_to_world


@carb.profiler.profile
def get_animation(usd_stage, usd_skel_prim):
    skel_anim_paths = None
    if usd_skel_prim.HasAPI(UsdSkel.BindingAPI):
        skel_anim_paths = UsdSkel.BindingAPI(usd_skel_prim).GetAnimationSourceRel().GetTargets()
    if skel_anim_paths:
        return UsdSkel.Animation.Get(usd_stage, skel_anim_paths[0])
    elif usd_skel_prim.GetRelationship("skel:animationSource").GetTargets():
        animation_path = usd_skel_prim.GetRelationship("skel:animationSource").GetTargets()[0]
        return UsdSkel.Animation.Get(usd_stage, animation_path)

    # If no animation set is found, return nothing save static prim data
    return None


@carb.profiler.profile
def get_animation_fabric(usdrt_stage, usdrt_skel_prim):
    if not usdrt_skel_prim.IsValid():
        return None
    skel_anim_paths = None
    if usdrt_skel_prim.HasAPI(usdrt.UsdSkel.BindingAPI):
        skel_anim_paths = usdrt.UsdSkel.BindingAPI(usdrt_skel_prim).GetAnimationSourceRel().GetTargets()
    if skel_anim_paths:
        return usdrt.UsdSkel.Animation(usdrt_stage.GetPrimAtPath(str(skel_anim_paths[0])))
    elif usdrt_skel_prim.GetRelationship("skel:animationSource").GetTargets():
        animation_path = usdrt_skel_prim.GetRelationship("skel:animationSource").GetTargets()[0]
        return usdrt.UsdSkel.Animation(usdrt_stage.GetPrimAtPath(str(animation_path)))
    # If no animation set is found, return nothing save static prim data
    return None


@carb.profiler.profile
def add_rest_transforms(skel_data, skel_rest_transforms, local_to_world_transform, parents):
    # TODO: Move code to warp to improve efficiency
    joint_local_rest_rotations = []
    joint_local_rest_translations = []

    joint_rest_global_transforms = Vt.Matrix4dArray(len(skel_rest_transforms))
    joint_rest_global_translations = Vt.Vec3dArray(len(skel_rest_transforms))

    # Extract local rest rotations and translations
    for i, transform in enumerate(skel_rest_transforms):
        rest_quat = skel_rest_transforms[i].ExtractRotation().GetQuat()
        joint_local_rest_rotations.append(np.concatenate(([rest_quat.GetReal()], np.array(rest_quat.GetImaginary()))))
        joint_local_rest_translations.append(np.array(skel_rest_transforms[i].ExtractTranslation()))

        if parents[i] < 0:
            joint_rest_global_transforms[i] = transform
        else:
            joint_rest_global_transforms[i] = transform * joint_rest_global_transforms[parents[i]]

    # Extract global rest transforms and translations
    for i, transform in enumerate(joint_rest_global_transforms):
        joint_rest_global_transforms[i] = transform * local_to_world_transform
        joint_rest_global_translations[i] = joint_rest_global_transforms[i].ExtractTranslation()

    # Save the rest transforms to skeleton data
    skel_data["rest_global_translations"] = np.array(joint_rest_global_translations).tolist()
    skel_data["rest_local_rotations"] = np.array(joint_local_rest_rotations).tolist()
    skel_data["rest_local_translations"] = np.array(joint_local_rest_translations).tolist()
    return joint_rest_global_translations


@carb.profiler.profile
def use_skeleton_joints_for_global_transforms(skel_data, skel_prim_path, skel_jnt_attrs, is_fabric):
    # Compute global transforms and translations
    joint_global_translations = _get_skel_joints_global_translations(skel_prim_path, skel_jnt_attrs, is_fabric)
    joint_local_rotations = _get_skel_joints_local_rotations(skel_prim_path, skel_jnt_attrs, is_fabric)

    skel_data["global_translations"] = joint_global_translations.tolist()
    skel_data["local_rotations"] = joint_local_rotations.tolist()
    return joint_global_translations


@carb.profiler.profile
def get_fabric_joint_data(fabric_data, joints, joint_translations, joint_rotations, joint_scales, state):
    for i, joint in enumerate(joints):
        root_path = state.get_root_of_joint(joint)
        if not root_path:
            continue
        num_joints = state.get_skel_root_to_joint_count(root_path)
        if "joint_translations" not in fabric_data[root_path]:
            fabric_data[root_path]["joint_translations"] = Vt.Vec3dArray(num_joints)
            fabric_data[root_path]["joint_translations_index"] = 0

        if "joint_rotations" not in fabric_data[root_path]:
            fabric_data[root_path]["joint_rotations"] = Vt.Vec4fArray(num_joints)
            fabric_data[root_path]["joint_rotations_index"] = 0
        if "joint_scales" not in fabric_data[root_path]:
            fabric_data[root_path]["joint_scales"] = Vt.Vec3dArray(num_joints)
            fabric_data[root_path]["joint_scales_index"] = 0

        translation_index = fabric_data[root_path]["joint_translations_index"]
        rotation_index = fabric_data[root_path]["joint_rotations_index"]
        scale_index = fabric_data[root_path]["joint_scales_index"]

        fabric_data[root_path]["joint_translations"][translation_index] = Gf.Vec3d(
            joint_translations[i][0], joint_translations[i][1], joint_translations[i][2]
        )
        list_rotation = joint_rotations[i].tolist()
        fabric_data[root_path]["joint_rotations"][rotation_index] = Gf.Vec4f(
            list_rotation[0], list_rotation[1], list_rotation[2], list_rotation[3]
        )
        list_scale = joint_scales[i].tolist()
        fabric_data[root_path]["joint_scales"][scale_index] = Gf.Vec3d(list_scale[0], list_scale[1], list_scale[2])
        fabric_data[root_path]["joint_translations_index"] += 1
        fabric_data[root_path]["joint_rotations_index"] += 1
        fabric_data[root_path]["joint_scales_index"] += 1


@carb.profiler.profile
def get_joint_global_translations(skel_data, joint_local_transforms, local_to_world_transform, parents):
    # Compute local and global joint transforms
    joint_global_transforms = Vt.Matrix4dArray(len(joint_local_transforms))
    joint_global_translations = Vt.Vec3dArray(len(joint_local_transforms))
    joint_local_rotations = []

    # Compute local translations and rotations
    for i, transform in enumerate(joint_local_transforms):
        local_quat = transform.ExtractRotation().GetQuaternion()
        joint_local_rotations.append(np.concatenate(([local_quat.GetReal()], np.array(local_quat.GetImaginary()))))
        if parents[i] < 0:
            joint_global_transforms[i] = transform
        else:
            joint_global_transforms[i] = transform * joint_global_transforms[parents[i]]
    # Compute global transforms and translations
    for i, transform in enumerate(joint_global_transforms):
        joint_global_transforms[i] = transform * local_to_world_transform
        joint_global_translations[i] = joint_global_transforms[i].ExtractTranslation()

    joint_global_translations = np.array(joint_global_translations)

    skel_data["global_translations"] = joint_global_translations.tolist()
    skel_data["local_rotations"] = np.array(joint_local_rotations).tolist()
    return joint_global_translations


@carb.profiler.profile
def process_skel_data(skels_data, db):
    # TODO: Deprecate this node to Legacy and create a fast equivalent node that doesn't dump json (expensive operation)
    output_json = json.dumps(skels_data)
    db.outputs.skeletonData = output_json  # Deprecated OM-77982

    # Need to reshape parents, translation and rotation arrays on writer end
    db.outputs.numSkeletons = len(skels_data)
    skeleton_parents = np.concatenate(np.array([s["skeleton_parents"] for s in skels_data], dtype=object))
    db.outputs.skeletonParents = np.array(skeleton_parents, dtype=int)
    db.outputs.skeletonParentsSizes = [len(s["skeleton_parents"]) for s in skels_data]
    rest_global_translations = np.concatenate(
        np.array([s["rest_global_translations"] for s in skels_data], dtype=object)
    )
    db.outputs.restGlobalTranslations = np.array(rest_global_translations, dtype=np.double)
    db.outputs.restGlobalTranslationsSizes = [len(s["rest_global_translations"]) for s in skels_data]
    rest_local_rotations = np.concatenate(np.array([s["rest_local_rotations"] for s in skels_data], dtype=object))
    db.outputs.restLocalRotations = np.array(rest_local_rotations, dtype=np.double)
    db.outputs.restLocalRotationsSizes = [len(s["rest_local_rotations"]) for s in skels_data]
    rest_local_translations = np.concatenate(np.array([s["rest_local_translations"] for s in skels_data], dtype=object))
    db.outputs.restLocalTranslations = np.array(rest_local_translations, dtype=np.double)
    db.outputs.restLocalTranslationsSizes = [len(s["rest_local_translations"]) for s in skels_data]
    db.outputs.skelName = [str(s["skel_name"]) for s in skels_data]
    db.outputs.skelPath = [str(s["skel_path"]) for s in skels_data]
    db.outputs.assetPath = [str(s.get("asset_path", "None")) for s in skels_data]
    db.outputs.animationVariant = [str(s.get("animation_variant", "None")) for s in skels_data]
    global_translations = [
        s for skel in skels_data if "global_translations" in skel for s in skel["global_translations"]
    ]
    db.outputs.globalTranslations = np.array(global_translations, dtype=np.double)
    db.outputs.globalTranslationsSizes = [len(s.get("global_translations", [])) for s in skels_data]

    db.outputs.localRotations = [s for skel in skels_data if "local_rotations" in skel for s in skel["local_rotations"]]
    db.outputs.localRotationsSizes = [len(s.get("local_rotations", [])) for s in skels_data]

    # Skeleton Joints: all the types go into one large string for each skeleton (backwards compatibility)
    db.outputs.skeletonJoints = [str(s["skeleton_joints"]) for s in skels_data if "skeleton_joints" in s]

    db.outputs.translations2d = [s for skel in skels_data if "translations_2d" in skel for s in skel["translations_2d"]]
    db.outputs.translations2dSizes = [len(s.get("translations_2d", [])) for s in skels_data]

    db.outputs.jointOcclusions = [
        s for skel in skels_data if "joint_occlusions" in skel for s in skel["joint_occlusions"]
    ]
    db.outputs.jointOcclusionsSizes = [len(s.get("joint_occlusions", [])) for s in skels_data]

    # Occlusion types: all the types go into one large string for each skeleton (backwards compatibility)
    db.outputs.occlusionTypes = [str(s["occlusion_types"]) for s in skels_data if "occlusion_types" in s]
    db.outputs.occlusionTypesSizes = [len(s.get("occlusion_types", [])) for s in skels_data]

    db.outputs.inView = [s["in_view"] for s in skels_data if "in_view" in s]


@carb.profiler.profile
def get_fabric_data(db, stage):
    if len(db.inputs.fabricPrims) == 0:
        return {}

    fabric_data = {}
    state = db.shared_state
    fabric_root_paths = db.inputs.fabricPrims

    # Get mapping from Skeleton to SkelRoot prims
    for root_prim_path in fabric_root_paths:
        if state.has_skel_root_entry(root_prim_path):
            continue

        prim = stage.GetPrimAtPath(root_prim_path)
        skel_root = UsdSkel.Root(prim)
        cache = UsdSkel.Cache()
        cache.Populate(skel_root, Usd.PrimDefaultPredicate)
        binding = cache.ComputeSkelBindings(skel_root, Usd.PrimDefaultPredicate)
        if binding:
            skel = binding[0].GetSkeleton()
            skel_path = str(skel.GetPath())
            state.add_skel_entry(skel_path, root_prim_path)
        else:
            continue

        # Get mappings from Joint to SkelRoot
        usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        skel_anim_fabric = get_animation_fabric(usdrt_stage, usdrt_stage.GetPrimAtPath(skel_path))
        num_joints = 0
        if skel_anim_fabric:
            joints = skel_anim_fabric.GetJointsAttr()
            if not joints.IsValid():
                continue
            joints = joints.Get()
            for joint in joints:
                num_joints += 1
                # Use the skel prim path as root instead of the animation prim path, because multiple
                # skel prims can be bound to the same animation source
                state.add_joint_entry(skel_path + "/" + joint, root_prim_path)

        state.add_joint_count_to_skel_root(root_prim_path, num_joints)
        state.add_skel_root(root_prim_path)

    # Populate fabric skelroot data
    for i, root_prim_path in enumerate(fabric_root_paths):
        fabric_data[root_prim_path] = {}
        fabric_data[root_prim_path]["world_position"] = usdrt.Gf.Vec3d(db.inputs.primWorldPositions[i])
        fabric_data[root_prim_path]["world_orientation"] = usdrt.Gf.Quatf(db.inputs.primWorldOrientations[i])
        fabric_data[root_prim_path]["world_scale"] = usdrt.Gf.Vec3d(
            db.inputs.primWorldScales[i][0], db.inputs.primWorldScales[i][1], db.inputs.primWorldScales[i][2]
        )

    return fabric_data


class OgnGetSkeletonData:
    @staticmethod
    def internal_state():
        return OgnGetSkeletonDataInternalState()

    @staticmethod
    def compute(db) -> bool:
        if not db.inputs.renderProductPath:
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        # Load stage and current time
        skel_prim_paths = db.inputs.prims

        if not skel_prim_paths:
            db.outputs.exec = og.ExecutionAttributeState.ENABLED

            # Set outputs to empty values
            db.outputs.numSkeletons = 0
            db.outputs.skeletonParents = []
            db.outputs.skeletonParentsSizes = []
            db.outputs.restGlobalTranslations = []
            db.outputs.restGlobalTranslationsSizes = []
            db.outputs.restLocalRotations = []
            db.outputs.restLocalRotationsSizes = []
            db.outputs.restLocalTranslations = []
            db.outputs.restLocalTranslationsSizes = []
            db.outputs.skelName = []
            db.outputs.skelPath = []
            db.outputs.assetPath = []
            db.outputs.animationVariant = []
            db.outputs.globalTranslations = []
            db.outputs.globalTranslationsSizes = []
            db.outputs.localRotations = []
            db.outputs.localRotationsSizes = []
            db.outputs.skeletonJoints = []
            db.outputs.translations2d = []
            db.outputs.translations2dSizes = []
            db.outputs.jointOcclusions = []
            db.outputs.jointOcclusionsSizes = []
            db.outputs.occlusionTypes = []
            db.outputs.occlusionTypesSizes = []
            db.outputs.inView = []
            return True

        # Get instance segmentation semantics data
        instance_segmentation_strides = db.inputs.instanceSegmentationStrides
        instance_data = get_wp_array(
            db.inputs.instanceSegmentationPtr,
            shape=(db.inputs.instanceSegmentationHeight, db.inputs.instanceSegmentationWidth),
            dtype=wp.uint32,
            strides=(instance_segmentation_strides[1], instance_segmentation_strides[0]),
            source_device=get_device(db.inputs.instanceSegmentationCudaDeviceIndex),
            target_device="cpu",
        ).numpy()
        instance_semantic_ids = db.inputs.instanceSegmentationIds
        instance_semantics_data = db.inputs.instanceSegmentationSemantics
        instance_seg_paths = db.inputs.instanceSegmentationLabels
        # If colorized, need convert ids to uint32
        if len(instance_semantic_ids) == 4 * len(instance_semantics_data):
            instance_semantic_ids = instance_semantic_ids.astype(np.uint8).view(np.uint32)

        instance_semantics = {}
        for i, id in enumerate(instance_semantic_ids):
            instance_semantics[id] = {}
            if i >= len(instance_semantics_data):
                break
            semantics = instance_semantics_data[i].split(":")
            if len(semantics) == 2:
                instance_semantics[id][semantics[0]] = semantics[1]

        usd_stage = omni.usd.get_context().get_stage()
        usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())

        # Check if there is data in Fabric
        fabric_data = get_fabric_data(db, usd_stage)
        state = db.shared_state

        # Compute fabric LocalToWorldTransforms if valid
        compute_local_to_world_transforms_fabric(fabric_data, db.inputs.fabricPrims)

        # Get every joint's translation, rotation, and scale
        get_fabric_joint_data(
            fabric_data,
            db.inputs.fabricJoints,
            db.inputs.jointWorldPositions,
            db.inputs.jointWorldOrientations,
            db.inputs.jointWorldScales,
            state,
        )

        # Get timestamp from usd timeline
        time_iface = omni.timeline.acquire_timeline_interface()
        cur_time = time_iface.get_current_time()
        fps = time_iface.get_time_codes_per_seconds()
        timestamp = cur_time * fps

        # Get view params
        view_params = _get_view_params(db)
        skels_data = []

        # Reshape instance data to fit view parameter's height and width
        inst_data = instance_data.view(np.uint32).reshape(view_params["height"], view_params["width"], -1)

        # Iterate through all the skeleton prims found in the scene and obtain their corresponding skeleton data
        for skel_prim_path in skel_prim_paths:
            # Skip invisible skeletons
            if UsdGeom.Imageable(usd_stage.GetPrimAtPath(skel_prim_path)).ComputeVisibility() == "invisible":
                continue

            # Get Skelroot from input or fabric stage
            skelroot_prim = None
            skelroot_prim_fabric = None
            skelroot_prim_path = state.get_root_of_skel(skel_prim_path)
            if not skelroot_prim_path:
                skelroot_prim = _get_skelroot_prim_from_skeleton(usd_stage, skel_prim_path)
                if skelroot_prim and skelroot_prim.IsValid():
                    skelroot_prim_path = skelroot_prim.GetPath()
                    skelroot_prim_fabric = usdrt_stage.GetPrimAtPath(str(skelroot_prim_path))

            # Get Skeleton
            skel_prim = usd_stage.GetPrimAtPath(skel_prim_path)
            skel_prim_fabric = usdrt_stage.GetPrimAtPath(skel_prim_path)
            skel = UsdSkel.Skeleton(skel_prim)
            skel_fabric = usdrt.UsdSkel.Skeleton(skel_prim_fabric) if skel_prim_fabric.IsValid() else None

            skel_data = {}

            # Obtain skeleton name and path
            skel_data["skel_name"] = skel_fabric.GetPrim().GetName() if skel_fabric else skel.GetPrim().GetName()
            skel_data["skel_path"] = (
                str(skel_fabric.GetPrim().GetPath()) if skel_fabric else str(skel.GetPrim().GetPath())
            )

            # Get joint list and parent indices
            skel_jnt_attrs = (
                list(skel_fabric.GetJointsAttr().Get()) if skel_fabric else list(skel.GetJointsAttr().Get())
            )
            skel_data["skeleton_joints"] = skel_jnt_attrs
            parents = _get_parent_indices(skel_jnt_attrs)
            skel_data["skeleton_parents"] = parents

            # Get local to world transform from SkelRoot
            local_to_world_transform = None
            # First try to get from upstream fabric data (OgnGetSkeletonAttributes)
            if skelroot_prim_path in fabric_data and "local_to_world" in fabric_data[skelroot_prim_path]:
                local_to_world_transform = usdrt.Gf.convertToPxr(fabric_data[skelroot_prim_path]["local_to_world"])
            if local_to_world_transform is None and skelroot_prim_fabric and skelroot_prim_fabric.IsValid():
                local_to_world_transform = usdrt.Gf.convertToPxr(
                    usdrt.Rt.Xformable(skelroot_prim_fabric).GetFabricHierarchyWorldMatrixAttr().Get(timestamp)
                )
            if local_to_world_transform is None and skelroot_prim and skelroot_prim.IsValid():
                local_to_world_transform = UsdGeom.Xform(skelroot_prim).ComputeLocalToWorldTransform(timestamp)
            if local_to_world_transform is None and skel_prim_fabric.IsValid():
                local_to_world_transform = usdrt.Gf.convertToPxr(
                    usdrt.Rt.Xformable(skel_prim_fabric).GetFabricHierarchyWorldMatrixAttr().Get(timestamp)
                )
            if local_to_world_transform is None:
                # Fallback to use Skeleton prim if SkelRoot is not found
                local_to_world_transform = UsdGeom.Xform(skel_prim).ComputeLocalToWorldTransform(timestamp)
            if not local_to_world_transform:
                # In case world transform is not obtained from above
                local_to_world_transform = Gf.Matrix4d()
                local_to_world_transform.SetIdentity()

            # Get skel rest transform
            skel_rest_transforms = None
            if skel_fabric:
                skel_rest_transforms = _convert_to_pxr_list(skel_fabric.GetRestTransformsAttr().Get())
            else:
                skel_rest_transforms = skel.GetRestTransformsAttr().Get()

            # Add rest local and global tranforms with skel rest transforms
            joint_rest_global_translations = add_rest_transforms(
                skel_data, skel_rest_transforms, local_to_world_transform, parents
            )

            # FIXME:: Handle case of Fabric skeleton
            # Add custom label keys and value for skeleton data
            char_prim_path = skel.GetPrim().GetPath().pathString
            try:
                skel_data["asset_path"] = get_asset_path_from_prim_path(char_prim_path)
            except Exception:
                skel_data["asset_path"] = None

            try:
                skel_data["animation_variant"] = get_anim_variant_from_prim_path(char_prim_path)
            except Exception:
                skel_data["animation_variant"] = None

            # Get local and global joint transforms
            joint_global_translations = None
            # - First see if useSkelJoints is on
            if db.inputs.useSkelJoints:
                joint_global_translations = use_skeleton_joints_for_global_transforms(
                    skel_data, skel_prim_path, skel_jnt_attrs, is_fabric=skel_prim_fabric.IsValid()
                )
            # - Next check if joint transforms are in input data
            elif (
                skelroot_prim_path in fabric_data
                and "joint_translations" in fabric_data[skelroot_prim_path]
                and "joint_rotations" in fabric_data[skelroot_prim_path]
                and "joint_scales" in fabric_data[skelroot_prim_path]
            ):
                joint_translations = fabric_data[skelroot_prim_path]["joint_translations"]
                joint_rotations = fabric_data[skelroot_prim_path]["joint_rotations"]
                joint_scales = fabric_data[skelroot_prim_path]["joint_scales"]

                joint_local_transforms = []
                for i in range(len(joint_translations)):
                    rotation = Gf.Rotation(
                        Gf.Quatd(
                            joint_rotations[i][3],
                            Gf.Vec3d(joint_rotations[i][0], joint_rotations[i][1], joint_rotations[i][2]),
                        )
                    )
                    joint_local_transforms.append(
                        Gf.Transform(
                            translation=joint_translations[i], rotation=rotation, scale=joint_scales[i]
                        ).GetMatrix()
                    )

                joint_global_translations = get_joint_global_translations(
                    skel_data, joint_local_transforms, local_to_world_transform, parents
                )

            # - Next try get from Fabric animation
            if joint_global_translations is None:
                anim_fabric = get_animation_fabric(usdrt_stage, skel_prim_fabric)

                if anim_fabric:
                    t = list(anim_fabric.GetTranslationsAttr().Get())  # _Gf.Vec3f
                    r = list(anim_fabric.GetRotationsAttr().Get())  # _Gf.Quatf
                    s = list(anim_fabric.GetScalesAttr().Get())  # _Gf.Vec3h

                    joint_count = len((anim_fabric.GetJointsAttr().Get()))
                    joint_local_transforms = []
                    for i in range(joint_count):
                        translation = Gf.Vec3d(t[i][0], t[i][1], t[i][2])
                        # real = =Gf.Rotation(Gf.Quatd(r[i].GetReal(), r[i].GetImaginary()))
                        real = r[i].GetReal()
                        rt_imaginary = r[i].GetImaginary()
                        imaginary = Gf.Vec3d(rt_imaginary[0], rt_imaginary[1], rt_imaginary[2])
                        rotation = Gf.Rotation(Gf.Quatd(real, imaginary))
                        scale = Gf.Vec3d(s[i][0], s[i][1], s[i][2])

                        joint_local_transforms.append(
                            Gf.Transform(translation=translation, rotation=rotation, scale=scale).GetMatrix()
                        )
                    joint_global_translations = get_joint_global_translations(
                        skel_data, joint_local_transforms, local_to_world_transform, parents
                    )

            # - Next try get from USD animation
            if joint_global_translations is None:
                anim = get_animation(usd_stage, skel_prim.GetPrim())
                if anim:
                    skel_cache = UsdSkel.Cache()
                    anim_query = skel_cache.GetAnimQuery(anim)
                    joint_local_transforms = anim_query.ComputeJointLocalTransforms(timestamp)
                    joint_global_translations = get_joint_global_translations(
                        skel_data, joint_local_transforms, local_to_world_transform, parents
                    )

            # - If all above fails, fallback to use rest pose and move on to next skeleton
            if joint_global_translations is None:
                compute_2d_translations(joint_rest_global_translations, view_params, skel_data)
                skels_data.append(skel_data)
                continue

            # Compute 2d world-to-image points
            compute_2d_translations(joint_global_translations, view_params, skel_data)

            # Calculate occlusions
            skel_occlusions = [False] * len(skel_data["skeleton_joints"])
            occlusion_types = ["None"] * len(skel_data["skeleton_joints"])

            # Find out where the semantic data is in the skeleton
            prim = skel_prim
            while prim != usd_stage.GetPseudoRoot() and not (
                prim.HasAPI(Semantics.SemanticsAPI) or prim.HasAPI(UsdSemantics.LabelsAPI)
            ):
                prim = prim.GetParent()

            if not prim.HasAPI(Semantics.SemanticsAPI) and not prim.HasAPI(UsdSemantics.LabelsAPI):
                prim = skel_prim

            # Check that the pixel at the joint position matches the instance ID of the character
            for j, pos in enumerate(skel_data["translations_2d"]):
                if pos[1] >= inst_data.shape[0] or pos[0] >= inst_data.shape[1] or pos[0] < 0 or pos[1] < 0:
                    continue
                seg_value = inst_data[int(pos[1]), int(pos[0])].squeeze()

                matches = np.where(instance_semantic_ids == seg_value)[0]

                occluded = True
                occlusion_type = "None"
                for match in matches:
                    if instance_seg_paths[match] == "UNLABELLED":
                        occluded = False
                        occlusion_type = "N/A"
                    if instance_seg_paths[match].startswith(str(prim.GetPath())):
                        occluded = False
                        break
                if occluded:
                    occlusion_type = instance_semantics[int(seg_value)]

                skel_occlusions[j] = occluded
                occlusion_types[j] = occlusion_type

            skel_data["joint_occlusions"] = skel_occlusions.copy()
            skel_data["occlusion_types"] = occlusion_types.copy()

            # Add skeleton data to dictionary
            skels_data.append(skel_data)

        if skels_data:
            process_skel_data(skels_data, db)
        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        return True


def _get_skel_joints_global_translations(skel_prim_path: str, skelJnt_attrs: list, is_fabric: bool = False):
    global_translations = []
    skelJnt_prims = get_skel_joints_prim_path(skel_prim_path, skelJnt_attrs, is_fabric)
    for prim in skelJnt_prims:
        if is_fabric:
            pos_fabric = usdrt.Rt.Xformable(prim).GetWorldPositionAttr().Get()
            global_translations.append(usdrt.Gf.convertToPxr(pos_fabric))
        else:
            xform = UsdGeom.Xformable(prim)
            global_mtrx = xform.ComputeLocalToWorldTransform(0)
            translation = global_mtrx.ExtractTranslation()
            global_translations.append(translation)
    return np.array(global_translations)


def _get_skel_joints_local_rotations(skel_prim_path: str, skelJnt_attrs: list, is_fabric: bool = False):
    local_rotations = []
    skelJnt_prims = get_skel_joints_prim_path(skel_prim_path, skelJnt_attrs, is_fabric)
    for prim in skelJnt_prims:
        if is_fabric:
            matrix_fabric = usdrt.Rt.Xformable(prim).GetLocalMatrixAttr().Get()
            local_quat = usdrt.Gf.Transform(matrix_fabric).GetRotation().GetQuat()
            rotation = np.concatenate(([local_quat.GetReal()], np.array(local_quat.GetImaginary())))
            local_rotations.append(rotation)
        else:
            xform = UsdGeom.Xformable(prim)
            local_mtrx = xform.GetLocalTransformation()
            local_quat = local_mtrx.ExtractRotation().GetQuaternion()
            rotation = np.concatenate(([local_quat.GetReal()], np.array(local_quat.GetImaginary())))
            local_rotations.append(rotation)
    return np.array(local_rotations)


def get_global_translations(prims):
    global_translations = []
    for prim in prims:
        xform = UsdGeom.Xformable(prim)
        global_mtrx = xform.ComputeLocalToWorldTransform(0)
        translation = global_mtrx.ExtractTranslation()
        global_translations.append(translation)
    return global_translations


def get_local_rotations(prims):
    local_rotations = []
    for prim in prims:
        xform = UsdGeom.Xformable(prim)
        local_mtrx = xform.GetLocalTransformation()
        local_quat = local_mtrx.ExtractRotation().GetQuaternion()
        rotation = np.concatenate(([local_quat.GetReal()], np.array(local_quat.GetImaginary())))
        local_rotations.append(rotation)
    return local_rotations


def get_skel_joints_prim_path(skel_prim_path: str, skelJnt_attrs: list, is_fabric: bool = False):
    skelJnt_prims = []
    context = omni.usd.get_context()
    stage = usdrt.Usd.Stage.Attach(context.get_stage_id()) if is_fabric else context.get_stage()
    skelJnt_prim_paths = [f"{skel_prim_path}/{jnt}" for jnt in skelJnt_attrs]
    for path in skelJnt_prim_paths:
        if is_valid_prim_path(path, stage, is_fabric):
            skelJnt_prims.append(stage.GetPrimAtPath(path))
        else:
            carb.log_error(f"Invalid prim path: {path}")

    return skelJnt_prims


def is_valid_prim_path(prim_path, stage, is_fabric=False):
    if not isinstance(prim_path, str):
        return False
    if stage is None:
        context = omni.usd.get_context()
        if is_fabric:
            stage = usdrt.Usd.Stage.Attach(context.get_stage_id())
        else:
            stage = context.get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    return prim.IsValid()
