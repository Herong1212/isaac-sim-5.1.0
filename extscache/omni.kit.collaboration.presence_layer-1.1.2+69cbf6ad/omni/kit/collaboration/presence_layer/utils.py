# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb

from .constants import *
from pxr import Sdf, Usd, UsdGeom


class CarbProfilerScope:  # pragma: no cover
    def __init__(self, id, name):
        self._id = id
        self._name = name

    def __enter__(self):
        carb.profiler.begin(self._id, self._name)

    def __exit__(self, type, value, trace):
        carb.profiler.end(self._id)


@carb.profiler.profile
def get_user_id_from_path(path: Sdf.Path):
    prefixes = path.GetPrefixes()
    if len(prefixes) < 2:
        return None

    # "/{SESSION_SHARED_LAYER_ROOT_NAME}/_{self.user_id}"
    # Premove the prefix _ to get real user id.
    user_id = prefixes[1].name[1:]

    return user_id


def is_local_builtin_camera(path: Sdf.Path):
    """
    Checks if it's local builtin camera. If so, it will return the corresponding builtin camera
    name for bound camera property.
    """

    path = Sdf.Path(path)
    return LOCAL_BUILT_IN_CAMERA_PATH_TO_SHARED_NAME.get(path, None)


def get_user_shared_root_path(user_id: str) -> Sdf.Path:
    # The prefix "_" is used to make sure the id is valid for identifier
    return SESSION_SHARED_LAYER_ROOT_PATH.AppendElementString(f"_{user_id}")


def get_bound_camera_property_path(user_id: str) -> Sdf.Path:
    shared_root_path = get_user_shared_root_path(user_id)

    return shared_root_path.AppendProperty(SESSION_SHARED_BOUND_CAMERA_PROPERTY_NAME)


def get_selection_property_path(user_id: str) -> Sdf.Path:
    shared_root_path = get_user_shared_root_path(user_id)

    return shared_root_path.AppendProperty(SESSION_SHARED_SELECTION_PROPERTY_NAME)


def get_following_user_property_path(user_id: str) -> Sdf.Path:
    shared_root_path = get_user_shared_root_path(user_id)

    return shared_root_path.AppendProperty(SESSION_SHARED_FOLLOWING_USER_PROPERTY_NAME)


def get_or_create_property_spec(layer, property_path, typename, is_custom=True):
    property_spec = layer.GetAttributeAtPath(property_path)
    if property_spec and property_spec.typeName != typename:
        carb.log_verboase(f"Type of property {property_spec} does not match: {property_spec.typeName}, {typename}.")
        prim_spec = layer.GetPrimAtPath(property_path.GetPrimPath())
        if prim_spec:
            prim_spec.RemoveProperty(property_spec)
        property_spec = None

    if not property_spec:
        Sdf.JustCreatePrimAttributeInLayer(
            layer, property_path, typename, isCustom=is_custom
        )
        property_spec = layer.GetAttributeAtPath(property_path)

    return property_spec
