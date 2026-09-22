# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pxr import Gf

from . import array_const


class ArrayParams:
    # Consider changing dictionary to carb settings to make undo/redo easier
    # Dictionaries are not notified of value changes when the user runs an undo/redo command.

    def __init__(self):
        super().__init__()
        self.reset_to_defaults()

    # TODO: Find better way of assigning copies of Gf.Vec3d instead of casting
    # TODO: Need to offer a full reset or partial. Some values we might not want to reset like the options or preview
    def reset_to_defaults(self):
        self._values = {}
        self._values[array_const.PREVIEW] = array_const.PREVIEW_DEFAULT
        self._values[array_const.COUNT] = array_const.COUNT_DEFAULT
        self._values[array_const.INC_TRANSLATE] = Gf.Vec3d(array_const.INC_TRANSLATE_DEFAULT)
        self._values[array_const.INC_ROTATE] = Gf.Vec3d(array_const.INC_ROTATE_DEFAULT)
        self._values[array_const.INC_SCALE] = Gf.Vec3d(array_const.INC_SCALE_DEFAULT)
        self._values[array_const.TOT_TRANSLATE] = Gf.Vec3d(array_const.TOT_TRANSLATE_DEFAULT)
        self._values[array_const.TOT_ROTATE] = Gf.Vec3d(array_const.TOT_ROTATE_DEFAULT)
        self._values[array_const.TOT_SCALE_TOGGLE] = Gf.Vec3d(array_const.TOT_SCALE_DEFAULT)
        self._values[array_const.TOT_TRANSLATE_TOGGLE] = array_const.TOT_TRANSLATE_TOGGLE_DEFAULT
        self._values[array_const.TOT_ROTATE_TOGGLE] = array_const.TOT_ROTATE_TOGGLE_DEFAULT
        self._values[array_const.TOT_SCALE_TOGGLE] = array_const.TOT_SCALE_TOGGLE_DEFAULT
        self._values[array_const.TWO_D_COUNT] = array_const.TWO_D_COUNT_DEFAULT
        self._values[array_const.THREE_D_COUNT] = array_const.THREE_D_COUNT_DEFAULT
        self._values[array_const.TWO_D_OFFSET] = Gf.Vec3d(array_const.TWO_D_OFFSET_DEFAULT)
        self._values[array_const.TOT_TWO_D_OFFSET] = Gf.Vec3d(array_const.TOT_TWO_D_OFFSET_DEFAULT)
        self._values[array_const.THREE_D_OFFSET] = Gf.Vec3d(array_const.THREE_D_OFFSET_DEFAULT)
        self._values[array_const.TOT_THREE_D_OFFSET] = Gf.Vec3d(array_const.TOT_THREE_D_OFFSET_DEFAULT)
        self._values[array_const.TOT_TWO_D_OFFSET_TOGGLE] = array_const.TOT_TWO_D_OFFSET_TOGGLE_DEFAULT
        self._values[array_const.TOT_THREE_D_OFFSET_TOGGLE] = array_const.TOT_THREE_D_OFFSET_TOGGLE_DEFAULT
        self._values[array_const.CREATE_TYPE] = array_const.CREATE_TYPE_DEFAULT
        self._values[array_const.ARRAY_TYPE] = array_const.ARRAY_TYPE_DEFAULT
        self._values[array_const.ARRAY_GROUP_RESULT] = array_const.ARRAY_GROUP_RESULT_DEFAULT
        self._values[array_const.REORIENT_ROTATION] = array_const.REORIENT_ROTATION_DEFAULT
        self._values[array_const.LINKED_SCALE_TOGGLE] = array_const.LINKED_SCALE_TOGGLE_DEFAULT
        self._values[array_const.LINKED_SCALE] = array_const.LINKED_SCALE_DEFAULT
        self._values[array_const.AUTO_SELECT_CREATED] = array_const.AUTO_SELECT_CREATED_DEFAULT
        self._values[array_const.RANDOM_ORDER_SEED] = array_const.RANDOM_ORDER_SEED_DEFAULT

    def get_defaults(self):
        if not self._values:
            self.reset_to_defaults()
        return self._values
