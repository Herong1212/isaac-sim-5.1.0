# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['TransformAccumulator']

from pxr import Gf


class TransformAccumulator:
    def __init__(self, initial_xform: Gf.Matrix4d):
        self.__inverse_xform = initial_xform.GetInverse() if initial_xform else None

    def get_rotation_axis(self, up_axis: Gf.Vec3d):
        if up_axis:
            return self.__inverse_xform.TransformDir(up_axis)
        else:
            return self.__inverse_xform.TransformDir(Gf.Vec3d(0, 1, 0))

    def get_translation(self, amount: Gf.Vec3d):
        return Gf.Matrix4d().SetTranslate(amount)

    def get_tumble(self, degrees: Gf.Vec3d, center_of_interest: Gf.Vec3d, up_axis: Gf.Vec3d):
        # Rotate around proper scene axis
        rotate_axis = self.get_rotation_axis(up_axis)

        # Move to center_of_interest, rotate and move back
        # No need for identity, all SetXXX methods will do that for us
        translate = Gf.Matrix4d().SetTranslate(-center_of_interest)
        # X-Y in ui/mouse are swapped so x-move is rotate around Y, and Y-move is rotate around X
        rotate_x = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), degrees[1]))
        rotate_y = Gf.Matrix4d().SetRotate(Gf.Rotation(rotate_axis, degrees[0]))
        return translate * rotate_x * rotate_y * translate.GetInverse()

    def get_look(self, degrees: Gf.Vec3d, up_axis: Gf.Vec3d):
        # Rotate around proper scene axis
        rotate_axis = self.get_rotation_axis(up_axis)

        # X-Y in ui/mouse are swapped so x-move is rotate around Y, and Y-move is rotate around X
        rotate_x = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), degrees[1]))
        rotate_y = Gf.Matrix4d().SetRotate(Gf.Rotation(rotate_axis, degrees[0]))
        return rotate_x * rotate_y
