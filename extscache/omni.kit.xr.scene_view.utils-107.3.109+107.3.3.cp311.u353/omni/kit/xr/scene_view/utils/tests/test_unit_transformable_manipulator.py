# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestTransformableManipulator", "TestTransformableManipulatorVisual"]

import math
import weakref

import carb
import pxr.Gf
from omni import ui
from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.core import XRSceneView
from omni.kit.xr.scene_view.utils import SceneViewUtils, TransformableManipulator, WidgetComponent
from omni.ui import color

from .base_sceneview_test import BaseSceneViewTest, BaseUiTest, _LabelWithBackground


class TestTransformableManipulatorVisual(BaseSceneViewTest):
    async def test_unit_transformable_manipulator_can_move(self):
        """Test visually that contained UI moves in space"""

        manipulator: TransformableManipulator
        utils = SceneViewUtils(XRSceneView)
        with utils.scene_view.scene:
            manipulator = TransformableManipulator()
            widget_component = WidgetComponent(
                _LabelWithBackground,
                widget_kwargs={"text": "VISUAL", "background": color(0.7, 0.7, 0.0)},
            )
            manipulator.add_component(widget_component)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(
                "transformable_manipulator_start",
                self.ACCEPTABLE_GOLDEN_THRESHOLD,
                __name__,
            )

            manipulator.translation = carb.Float3(25, 75, 0)
            await self.wait_post_sync_async()

            await self.capture_and_compare_viewport_output_async(
                "transformable_manipulator_end",
                self.ACCEPTABLE_GOLDEN_THRESHOLD,
                __name__,
            )


class TestTransformableManipulator(BaseUiTest):
    WIDGET_TYPE = ui.Widget

    async def test_unit_clean_lifecycle(self):
        container_ref = weakref.ref(self.container)
        model_ref = weakref.ref(self.model)
        manipulator_ref = weakref.ref(self.manipulator)
        widget_ref = weakref.ref(self.widget_component)

        self._drop_members()

        await self.wait_post_sync_async(5)

        # Make sure everything is finalized after being dropped
        self.assertIsNone(container_ref())
        self.assertIsNone(manipulator_ref())
        self.assertIsNone(widget_ref())
        self.assertIsNone(model_ref())

    async def test_unit_model_and_transform_model_match(self):
        self.assertEqual(self.model, self.manipulator.model)

    async def test_unit_model_sanity(self):
        self.assertIsNone(self.model.get_item("GARBAGE"))
        self.assertEqual(len(self.model.get_as_floats(None)), 0)

    async def _run_model_sanity_helper(
        self,
        manipulator_property_name: str,
        model_item_name: str,
        target_vals: list[float],
        expected_vals: list[float] | None = None,
    ):
        expected_len = len(target_vals)
        expected_vals = expected_vals or target_vals
        target_obj = carb.Float3(*target_vals)
        setattr(self.manipulator, manipulator_property_name, target_obj)

        item_from_name = self.model.get_item(model_item_name)
        item_from_prop = getattr(self.model, model_item_name)
        self.assertEqual(item_from_name, item_from_prop)

        property_readback = getattr(self.manipulator, manipulator_property_name)
        model_floats = item_from_prop.floats
        self.assertEqual(len(model_floats), expected_len)
        for i in range(3):
            self.assertAlmostEqual(property_readback[i], target_obj[i])
            self.assertAlmostEqual(model_floats[i], expected_vals[i])

    async def test_integration_model_translation(self):
        await self._run_model_sanity_helper("translation", "translation", [3, 7, 11])

    async def test_integration_model_rotation(self):
        degree_vals = [30, 60, 90]
        radian_vals = [math.radians(v) for v in degree_vals]
        await self._run_model_sanity_helper("rotation_degrees", "rotation", degree_vals, radian_vals)

        await self._run_model_sanity_helper("rotation_radians", "rotation", radian_vals)

    async def test_integration_model_scale(self):
        await self._run_model_sanity_helper("scale", "scale", [0.5, 1.0, 1.5])

    @staticmethod
    def _make_gf_transform():
        gf_transform = pxr.Gf.Transform()
        gf_transform.SetTranslation(pxr.Gf.Vec3d(1, 2, 3))
        gf_transform.SetRotation(pxr.Gf.Rotation().SetAxisAngle(pxr.Gf.Vec3d(0, 1, 0), 45.0))
        gf_transform.SetScale(pxr.Gf.Vec3d(2, 2, 2))
        return gf_transform

    async def test_integration_model_matrix_from_components(self):
        gf_transform = self._make_gf_transform()
        gf_matrix: pxr.Gf.Matrix4d = gf_transform.GetMatrix()

        self.manipulator.translation = carb.Float3([1, 2, 3])
        self.manipulator.rotation_degrees = carb.Float3([0, 45, 0])
        self.manipulator.scale = carb.Float3([2, 2, 2])

        matrix_item_from_name = self.model.get_item("matrix")
        matrix_item_from_prop = self.model.matrix_item
        self.assertEqual(matrix_item_from_name, matrix_item_from_prop)

        model_floats = matrix_item_from_prop.floats
        self.assertEqual(len(model_floats), 16)

        await self.wait_post_sync_async(3)

        idx = 0
        for r in range(4):
            matrix_row = gf_matrix.GetRow(r)
            for i in range(4):
                self.assertAlmostEqual(
                    model_floats[idx],
                    matrix_row[i],
                    None,
                    f"Error in row {r}, index {i}",
                )
                idx += 1

    async def test_integration_model_components_from_matrix(self):
        gf_transform = self._make_gf_transform()
        gf_matrix = gf_transform.GetMatrix()

        matrix_floats = []
        for r in range(4):
            matrix_row = gf_matrix.GetRow(r)
            for i in range(4):
                matrix_floats.append(matrix_row[i])

        matrix_item = self.model.matrix_item
        self.model.set_floats(matrix_item, matrix_floats)

        translation = gf_matrix.ExtractTranslation()
        rotation = gf_matrix.ExtractRotation().Decompose(
            pxr.Gf.Vec3d(1, 0, 0),
            pxr.Gf.Vec3d(0, 1, 0),
            pxr.Gf.Vec3d(0, 0, 1),
        )
        scale = pxr.Gf.Vec3d(*(v.GetLength() for v in gf_matrix.ExtractRotationMatrix()))

        for i in range(3):
            self.assertAlmostEqual(self.manipulator.translation[i], translation[i])
            self.assertAlmostEqual(self.manipulator.rotation_degrees[i], rotation[i])
            self.assertAlmostEqual(self.manipulator.scale[i], scale[i])

    async def test_integration_model_scene_matrix_sanity(self):
        pass
