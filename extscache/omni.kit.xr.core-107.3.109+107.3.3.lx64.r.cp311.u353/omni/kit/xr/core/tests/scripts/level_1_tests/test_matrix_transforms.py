# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.kit.xr.core.test_utils as test_utils
import omni.usd
from omni.kit.xr.core import XRUtils
from pxr import Gf, UsdGeom


class TestMatrixTransforms(omni.kit.test.AsyncTestCase):
    def get_epsilon(self):
        _EPSILON = 1e-7
        return _EPSILON

    @test_utils.opened_usd_stage()
    async def test_unit_matrix_transforms(self):
        """Test various local and world matrix transformations"""

        self.test_world_transforms()
        self.test_local_transforms()
        self.test_reorient_transform_up_right()
        self.test_reorient_transform_no_roll()

    def test_world_transforms(self):
        stage = omni.usd.get_context().get_stage()

        xformGeomParent = UsdGeom.Xform.Define(stage, "/parent")
        xformGeomChild = UsdGeom.Xform.Define(stage, "/parent/child")

        xformPrimParent = xformGeomParent.GetPrim()
        xformPrimChild = xformGeomChild.GetPrim()

        vec3Translation = Gf.Vec3d(10, 0, 0)
        # Rotate position onto the Z axis, where 270 == -90 degrees.
        rotation = Gf.Rotation(Gf.Vec3d.YAxis(), 270)

        translateMat = Gf.Matrix4d().SetTranslate(vec3Translation)
        rotateMat = Gf.Matrix4d().SetRotate(rotation)
        newMat = translateMat * rotateMat

        XRUtils.get_singleton().set_world_transform_matrix(xformPrimParent, newMat)
        parentMat = XRUtils.get_singleton().get_world_transform_matrix(xformPrimParent)

        # Validate setting and getting world matrices are working as expected.
        self.assertTrue(
            Gf.IsClose(newMat, parentMat, self.get_epsilon()),
            f"Set/Get world matrix mismatch:\n {newMat} != {parentMat}",
        )

        # Validate parenting is working correctly where the child has the same values as the parent.
        childMat = XRUtils.get_singleton().get_world_transform_matrix(xformPrimChild)
        self.assertTrue(
            Gf.IsClose(newMat, childMat, self.get_epsilon()),
            f"Parent matrix not propagating to child:\n {newMat} != {childMat}",
        )

        childPos = childMat.ExtractTranslation()
        childRot = childMat.ExtractRotation()

        # The child's position should be rotated based on the parent's rotation.
        vec3RotatedTranslation = rotation.TransformDir(vec3Translation)

        self.assertTrue(
            Gf.IsClose(vec3RotatedTranslation, childPos, self.get_epsilon()),
            f"Incorrect child position propagation:\n {vec3RotatedTranslation} != {childPos}",
        )

        self.assertTrue(
            Gf.IsClose(rotation.GetAxis(), childRot.GetAxis(), self.get_epsilon())
            or Gf.IsClose(rotation.GetAxis(), -childRot.GetAxis(), self.get_epsilon()),
            f"Incorrect child rotation axis propagation:\n {rotation.GetAxis()} != {childRot.GetAxis()}",
        )
        self.assertTrue(
            Gf.IsClose(rotation.GetAngle(), childRot.GetAngle(), self.get_epsilon())
            or Gf.IsClose(rotation.GetAngle(), 360 - childRot.GetAngle(), self.get_epsilon()),
            f"Incorrect child rotation angle propagation:\n {rotation.GetAngle()} != {childRot.GetAngle()}",
        )

        stage.RemovePrim(xformPrimParent.GetPath())
        stage.RemovePrim(xformPrimChild.GetPath())

    def test_local_transforms(self):
        stage = omni.usd.get_context().get_stage()

        xformGeomParent = UsdGeom.Xform.Define(stage, "/parent")
        xformGeomChild = UsdGeom.Xform.Define(stage, "/parent/child")

        xformPrimParent = xformGeomParent.GetPrim()
        xformPrimChild = xformGeomChild.GetPrim()

        vec3Translation = Gf.Vec3d(10, 0, 0)
        # Rotate position onto the Z axis, where 270 == -90 degrees.
        rotation = Gf.Rotation(Gf.Vec3d.YAxis(), 270)

        translateMat = Gf.Matrix4d().SetTranslate(vec3Translation)
        rotateMat = Gf.Matrix4d().SetRotate(rotation)
        newMat = translateMat * rotateMat

        XRUtils.get_singleton().set_local_transform_matrix(xformPrimParent, newMat)
        localParentMat = XRUtils.get_singleton().get_local_transform_matrix(xformPrimParent)

        # Validate setting and getting local matrices are working as expected.
        self.assertTrue(
            Gf.IsClose(newMat, localParentMat, self.get_epsilon()),
            f"Set/Get local matrix mismatch:\n {newMat} != {localParentMat}",
        )

        # Set child matrix with just translation
        XRUtils.get_singleton().set_local_transform_matrix(xformPrimChild, Gf.Matrix4d().SetTranslate(vec3Translation))
        localChildMat = XRUtils.get_singleton().get_local_transform_matrix(xformPrimChild)

        localChildPos = localChildMat.ExtractTranslation()
        localChildRot = localChildMat.ExtractRotation()

        # Compare child's local transform to what we set. There should only be the translation applied - no rotation from parent.
        self.assertTrue(
            Gf.IsClose(localChildPos, vec3Translation, self.get_epsilon()),
            f"Expected child local translation of {vec3Translation}, got {localChildPos}",
        )
        self.assertTrue(
            Gf.IsClose(localChildRot.GetAxis(), Gf.Vec3d(1, 0, 0), self.get_epsilon()),
            f"Expected no local rotation, got {localChildRot.GetAxis()}",
        )
        self.assertTrue(
            Gf.IsClose(localChildRot.GetAngle(), 0, self.get_epsilon()),
            f"Expected no local rotation, got {localChildRot.GetAngle()}",
        )

        # Test the child's local transform gets applied to world transform.
        worldChildMat = XRUtils.get_singleton().get_world_transform_matrix(xformPrimChild)
        worldChildPos = worldChildMat.ExtractTranslation()

        vec3RotatedTranslation = rotation.TransformDir(vec3Translation)

        # Parent and child xform both have a local transform of vec3Translation. That means child's location should be double.
        self.assertTrue(
            Gf.IsClose(worldChildPos, 2 * vec3RotatedTranslation, self.get_epsilon()),
            f"Expected child world position of {2 * vec3RotatedTranslation}, got {worldChildPos}",
        )

        # Skip testing world rotation. This is already handled in another test

        stage.RemovePrim(xformPrimParent.GetPath())
        stage.RemovePrim(xformPrimChild.GetPath())

    # Orthonormal Matrix where the Forward vector is the Z axis rotated -45 deg around the X axis.
    def _get_mat_rotated_neg_45_deg_on_X(self, vecOffset) -> Gf.Matrix4d:
        forwardVec = Gf.Vec3d(0, 1, 1).GetNormalized()
        rightVec = Gf.Vec3d.XAxis()
        upVec = Gf.Cross(forwardVec, rightVec)

        rotMat = Gf.Matrix3d()
        rotMat.SetRow(0, rightVec)
        rotMat.SetRow(1, upVec)
        rotMat.SetRow(2, forwardVec)

        return Gf.Matrix4d(rotMat, vecOffset)

    # Orthonormal Matrix where the Up vector is the Y axis rotated -45 deg around Z axis.
    def _get_mat_rotated_neg_45_deg_on_Z(self, vecOffset) -> Gf.Matrix4d:
        forwardVec = Gf.Vec3d.ZAxis()
        upVec = Gf.Vec3d(1, 1, 0).GetNormalized()
        rightVec = Gf.Cross(forwardVec, upVec)

        rotMat = Gf.Matrix3d()
        rotMat.SetRow(0, rightVec)
        rotMat.SetRow(1, upVec)
        rotMat.SetRow(2, forwardVec)

        return Gf.Matrix4d(rotMat, vecOffset)

    # Per the function comments for 'reorient_transform_matrix_up_right': "This function reorients a matrix to have its up vector point up".
    def test_reorient_transform_up_right(self):
        IS_Y_UP = True

        reOrientedMat = XRUtils.get_singleton().reorient_transform_matrix_up_right(Gf.Matrix4d(), IS_Y_UP)
        self.assertTrue(
            Gf.IsClose(reOrientedMat, Gf.Matrix4d(), self.get_epsilon()),
            f"Identity Matrix should have no effect. Got: {reOrientedMat}",
        )

        # Try with a matrix rotating Up around X.
        mat = self._get_mat_rotated_neg_45_deg_on_X(Gf.Vec3d(1, 1, 1))
        self.assertFalse(
            Gf.IsClose(mat.GetRow(1), Gf.Vec4d.YAxis(), self.get_epsilon()),
            f"(Rot X) Expected Up vector to point away from Y. Got: {mat.GetRow(1)}",
        )

        reOrientedMat = XRUtils.get_singleton().reorient_transform_matrix_up_right(mat, IS_Y_UP)
        self.assertTrue(
            Gf.IsClose(reOrientedMat.ExtractRotationMatrix(), Gf.Matrix3d(), self.get_epsilon()),
            f"(Rot X) Expected reoriented matrix to be identity (no rotation). Got: {reOrientedMat}",
        )

        # Try with a matrix rotating Up around Z.
        mat = self._get_mat_rotated_neg_45_deg_on_Z(Gf.Vec3d(1, 1, 1))
        self.assertFalse(
            Gf.IsClose(mat.GetRow(1), Gf.Vec4d.YAxis(), self.get_epsilon()),
            f"(Rot Z) Expected Up vector to point away from Y. Got: {mat.GetRow(1)}",
        )

        reOrientedMat = XRUtils.get_singleton().reorient_transform_matrix_up_right(mat, IS_Y_UP)
        self.assertTrue(
            Gf.IsClose(reOrientedMat.ExtractRotationMatrix(), Gf.Matrix3d(), self.get_epsilon()),
            f"(Rot Z) Expected reoriented matrix to be identity (no rotation). Got: {reOrientedMat}",
        )

    # Per the function comments for 'reorient_transform_matrix_no_roll': "This function reorients a matrix to have its roll removed so right vector is level."
    def test_reorient_transform_no_roll(self):
        IS_Y_UP = True

        reOrientedMat = XRUtils.get_singleton().reorient_transform_matrix_no_roll(Gf.Matrix4d(), IS_Y_UP)
        self.assertTrue(
            Gf.IsClose(reOrientedMat, Gf.Matrix4d(), self.get_epsilon()),
            f"Identity Matrix should have no effect. Got: {reOrientedMat}",
        )

        # Try with a matrix rotating Up around X.
        # Note: This matrix does not have any roll and so it should not diverge when trying to remove roll.
        mat = self._get_mat_rotated_neg_45_deg_on_X(Gf.Vec3d(1, 1, 1))
        reOrientedMat = XRUtils.get_singleton().reorient_transform_matrix_no_roll(mat, IS_Y_UP)

        self.assertTrue(
            Gf.IsClose(mat, reOrientedMat, self.get_epsilon()),
            f"Matrix has no roll so the reoriented matrix should not have changed.\n {mat} != {reOrientedMat}",
        )

        # Try with a matrix rotating Up around Z.
        mat = self._get_mat_rotated_neg_45_deg_on_Z(Gf.Vec3d(1, 1, 1))
        reOrientedMat = XRUtils.get_singleton().reorient_transform_matrix_no_roll(mat, IS_Y_UP)
        self.assertTrue(
            Gf.IsClose(reOrientedMat.ExtractRotationMatrix(), Gf.Matrix3d(), self.get_epsilon()),
            f"Expected reoriented matrix to be identity (no rotation). Got: {reOrientedMat}",
        )
