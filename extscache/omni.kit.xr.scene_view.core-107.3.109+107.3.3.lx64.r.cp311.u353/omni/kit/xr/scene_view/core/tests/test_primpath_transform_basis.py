# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestPrimPathTransformBasis"]

import omni.ui as ui
import omni.ui.scene as sc
import omni.usd
from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.core import XRPrimPathTransformBasis
from pxr import Gf, Sdf, Usd, UsdGeom

from .shared import XRSceneViewTest


class TestPrimPathTransformBasis(XRSceneViewTest):
    sample_path = Sdf.Path("/World/test_prim")
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 0.5  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def _build_scene(self):
        stage: Usd.Stage = omni.usd.get_context().get_stage()  # type: ignore
        translate = Gf.Vec3d(0, 200, 0)
        transform = Gf.Matrix4d().SetTranslate(translate)
        xform: UsdGeom.Xform = UsdGeom.Xform.Define(stage, self.sample_path)  # type: ignore

        await self.wait_post_sync_async()

        self.assertTrue(xform)
        self.assertTrue(xform.GetPrim())

        xform_op = xform.AddTransformOp()  # type: ignore
        xform_op.Set(transform)

        await self.wait_post_sync_async()

    async def test_unit_primpath_transform_basis(self):
        """Ensure that transforms attached to a XRPrimPathTransformBasis are transformed to the correct world space"""
        image_name = "can_attach"

        await self._build_scene()

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:
            with sc.Transform():
                normal_widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                with normal_widget.frame:
                    with ui.VStack():
                        ui.Label("Normal Widget", style={"font_size": 100})

                # Add a transform to the stack that uses the PrimPath created in the scene as its
                # TransformBasis, meaning that with no offset specified, the widget should still
                # appear offset from the origin.
                with sc.Transform(basis=XRPrimPathTransformBasis(self.sample_path.pathString)):  # type: ignore
                    based_widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                    with based_widget.frame:
                        with ui.VStack():
                            ui.Label("Based Widget", style={"font_size": 100})

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__)

    async def test_unit_primpath_transform_cleanup(self):
        """Verify that, when a XRPrimPathTransformBasis is deleted, there are no leftover UI prims in the stage"""
        image_name_before = "with_both_prims"
        image_name_after = "no_leftover_prims"

        await self._build_scene()

        xform_a: sc.Transform
        xform_b: sc.Transform

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:
            xform_a = sc.Transform()
            with xform_a:
                normal_widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                with normal_widget.frame:
                    with ui.VStack():
                        ui.Label("Normal Widget", style={"font_size": 100})

            xform_b = sc.Transform(basis=XRPrimPathTransformBasis(self.sample_path.pathString))  # type: ignore
            with xform_b:
                # Add a transform to the stack that uses the PrimPath created in the scene as its
                # TransformBasis, meaning that with no offset specified, the widget should still
                # appear offset from the origin.
                based_widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                with based_widget.frame:
                    with ui.VStack():
                        ui.Label("Going Away", style={"font_size": 100})
        await self.wait_post_sync_async(3)
        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(
                image_name_before, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

        xform_b.clear()

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)
        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(
                image_name_after, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

    async def test_unit_primpath_transform_after_init(self):
        """Ensure that adding a XRPrimPathTransformBasis after initial scene creation works correctly"""
        image_name = "add_after_init"

        await self._build_scene()

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:
            with sc.Transform():
                normal_widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                with normal_widget.frame:
                    with ui.VStack():
                        ui.Label("Normal Widget", style={"font_size": 100})

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:
            # Create a small transform stack with a transform basis to ensure that items created
            # after the sceneview exists already will also work correctly
            with sc.Transform(basis=XRPrimPathTransformBasis(self.sample_path.pathString)):  # type: ignore
                based_widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ON_DEMAND)
                with based_widget.frame:
                    with ui.VStack():
                        ui.Label("Late Init Widget", style={"font_size": 100})

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__)
