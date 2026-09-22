# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from enum import Enum

from pxr import Gf


# Enums
class CreateType(Enum):
    INSTANCES = 1
    COPIES = 2


class ArrayType(Enum):
    GROUP = 1
    ORDERED_SEQUENCE = 2
    RANDOM_SEQUENCE = 3


ALLOWED_INSTANCE_TYPES = ["Xform"]

# Parameter Names
PREVIEW = "preview"
COUNT = "count"
TWO_D_COUNT = "2d_count"
THREE_D_COUNT = "3d_count"
INC_TRANSLATE = "inc_translate"
INC_ROTATE = "inc_rotate"
INC_SCALE = "inc_scale"
TOT_TRANSLATE = "tot_translate"
TOT_ROTATE = "tot_rotate"
TOT_SCALE = "tot_scale"
TWO_D_OFFSET = "2d_offset"
THREE_D_OFFSET = "3d_offset"
TOT_TWO_D_OFFSET = "tot_2d_offset"
TOT_THREE_D_OFFSET = "tot_3d_offset"
TOT_TRANSLATE_TOGGLE = "tot_translate_toggle"
TOT_ROTATE_TOGGLE = "tot_rotate_toggle"
TOT_SCALE_TOGGLE = "tot_scale_toggle"
TOT_TWO_D_OFFSET_TOGGLE = "tot_2d_offset_toggle"
TOT_THREE_D_OFFSET_TOGGLE = "tot_3d_offset_toggle"
CREATE_TYPE = "create_type"
ARRAY_TYPE = "array_type"
ARRAY_GROUP_RESULT = "array_group_result"
LINKED_SCALE_TOGGLE = "linked_scale"
LINKED_SCALE = "linked_scale_reference"
REORIENT_ROTATION = "reorient"
AUTO_SELECT_CREATED = "auto_select_created"
RANDOM_ORDER_SEED = "random_order_seed"

# Parameter Defaults
PREVIEW_DEFAULT = True
COUNT_DEFAULT = 10
INC_TRANSLATE_DEFAULT = Gf.Vec3d(0)
INC_ROTATE_DEFAULT = Gf.Vec3d(0)
INC_SCALE_DEFAULT = Gf.Vec3d(0)
TOT_TRANSLATE_DEFAULT = Gf.Vec3d(0)
TOT_ROTATE_DEFAULT = Gf.Vec3d(0)
TOT_SCALE_DEFAULT = Gf.Vec3d(0)
TOT_TRANSLATE_TOGGLE_DEFAULT = False
TOT_ROTATE_TOGGLE_DEFAULT = False
TOT_SCALE_TOGGLE_DEFAULT = False
TWO_D_COUNT_DEFAULT = 1
THREE_D_COUNT_DEFAULT = 1
TWO_D_OFFSET_DEFAULT = Gf.Vec3d(0)
THREE_D_OFFSET_DEFAULT = Gf.Vec3d(0)
TOT_TWO_D_OFFSET_DEFAULT = Gf.Vec3d(0)
TOT_THREE_D_OFFSET_DEFAULT = Gf.Vec3d(0)
TOT_TWO_D_OFFSET_TOGGLE_DEFAULT = False
TOT_THREE_D_OFFSET_TOGGLE_DEFAULT = False
CREATE_TYPE_DEFAULT = CreateType.INSTANCES
ARRAY_TYPE_DEFAULT = ArrayType.GROUP
ARRAY_GROUP_RESULT_DEFAULT = False
REORIENT_ROTATION_DEFAULT = False
LINKED_SCALE_TOGGLE_DEFAULT = False
LINKED_SCALE_DEFAULT = Gf.Vec3d(0)
AUTO_SELECT_CREATED_DEFAULT = False
RANDOM_ORDER_SEED_DEFAULT = 0
