# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pxr import Sdf

SESSION_SHARED_USER_LAYER = "shared_data/users.live"
SESSION_SHARED_LAYER_ROOT_PATH = Sdf.Path("/__session_shared_data__")
SESSION_SHARED_PERSPECTIVE_CAMERA_NAME = "perspective"
SESSION_SHARED_FRONT_CAMERA_NAME = "front"
SESSION_SHARED_LEFT_CAMERA_NAME = "left"
SESSION_SHARED_RIGHT_CAMERA_NAME = "right"
SESSION_SHARED_BOUND_CAMERA_PROPERTY_NAME = "bound_camera"
SESSION_SHARED_FOLLOWING_USER_PROPERTY_NAME = "following_user"
SESSION_SHARED_SELECTION_PROPERTY_NAME = "selected_prim_paths"

SHARED_BUILT_IN_CAMERA_LIST = [
    SESSION_SHARED_PERSPECTIVE_CAMERA_NAME,
    SESSION_SHARED_FRONT_CAMERA_NAME,
    SESSION_SHARED_LEFT_CAMERA_NAME,
    SESSION_SHARED_RIGHT_CAMERA_NAME
]

LOCAL_BUILT_IN_CAMERA_PATH_TO_SHARED_NAME = {
    Sdf.Path("/OmniverseKit_Persp"): SESSION_SHARED_PERSPECTIVE_CAMERA_NAME,
    Sdf.Path("/OmniverseKit_Top"): SESSION_SHARED_FRONT_CAMERA_NAME,
    Sdf.Path("/OmniverseKit_Front"): SESSION_SHARED_LEFT_CAMERA_NAME,
    Sdf.Path("/OmniverseKit_Right"): SESSION_SHARED_RIGHT_CAMERA_NAME,
}

SHARED_NAME_TO_LOCAL_BUILT_IN_CAMERA_PATH = {
    SESSION_SHARED_PERSPECTIVE_CAMERA_NAME: Sdf.Path("/OmniverseKit_Persp"),
    SESSION_SHARED_FRONT_CAMERA_NAME: Sdf.Path("/OmniverseKit_Top"),
    SESSION_SHARED_LEFT_CAMERA_NAME: Sdf.Path("/OmniverseKit_Front"),
    SESSION_SHARED_RIGHT_CAMERA_NAME: Sdf.Path("/OmniverseKit_Right"),
}

LOCAL_SESSION_LAYER_SHARED_DATA_ROOT_PATH = Sdf.Path("/OmniverseLiveSessionSharedData")

LAYER_SUBSCRIPTION_ORDER = -1 << 31  # make sure this runs before anything else
