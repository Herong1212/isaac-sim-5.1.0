# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestXRSceneView"]

import sys
import weakref

import omni.kit.commands
import omni.ui as ui
import omni.ui.scene as sc
import omni.usd
from omni.kit.xr.core.test_utils import TestVRProfile, XRUsdStage
from omni.ui import color as cl
from pxr import Sdf
from pxr.Gf import Vec3d

from .shared import XRSceneViewTest


class TestXRSceneView(XRSceneViewTest):
    async def test_unit_xr_scene_view_deletion_empty(self):
        """Test that the teardown procedure correctly causes the XRSceneView to be destroyed"""

        # Test that the object is garbage collected as expected using a weakref
        wr = weakref.ref(self._xr_scene_view)

        # Immediately tear down all the scene view setup
        await self.tear_down_scene_view()

        # We should not find a valid reference to the sceneview once it's been torn down
        self.assertIsNone(wr())

    async def test_xr_scene_view_deletion_with_ui(self):
        """Test that a small, valid scene view with UI gets cleaned up properly when the scene view is torn down."""
        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:  # type: ignore
            with sc.Transform():
                widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ALWAYS)
                with widget.frame:
                    with ui.VStack():
                        ui.Label("I'm Leaving", style={"font_size": 100})

        await self.wait_materials_loaded_async()
        await self.test_unit_xr_scene_view_deletion_empty()

    async def test_unit_xr_scene_ui_label(self):
        """Test XR Scene View with a simple UI label"""
        image_name = "ui_label"

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:  # type: ignore
            with sc.Transform():
                widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ALWAYS)
                with widget.frame:
                    with ui.VStack():
                        ui.Label("Hello, World", style={"font_size": 100})
                        ui.Label("~~ SceneViewUSD ~~", style={"font_size": 64})

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__)

    async def test_unit_xr_scene_ui_scene_change(self):
        """Ensure that items can be added to an XR Scene View after it's showing and they will appear"""
        image_name = "scene_change"

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:
            with sc.Transform():
                widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ALWAYS)
                with widget.frame:
                    with ui.VStack():
                        ui.Label("TESTING", style={"font_size": 100})
                        ui.Label("scene change", style={"font_size": 70})

        # Load a new USD stage to make sure the UI still shows
        async with XRUsdStage(keep_stage=True):
            self.set_viewport_camera(Vec3d(25, 25, 150), Vec3d(0, 0, 0))

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__)

    async def test_unit_xr_scene_ui_translated_widget(self):
        """Test that XR Scene View items support being colorized per-item"""
        image_name = "translated_widget"

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:  # type: ignore
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                widget = sc.Widget(400, 150, update_policy=sc.Widget.UpdatePolicy.ALWAYS)
                with widget.frame:
                    ui.Label("Y-Positive", style={"font_size": 100})

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__)

    async def test_unit_xr_scene_ui_colored_items(self):
        """Test that XR Scene View items support being colorized per-item"""
        image_name = "colored_items"

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:  # type: ignore
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 150, 0)):
                widget1 = sc.Widget(300, 150, update_policy=sc.Widget.UpdatePolicy.ALWAYS, color=cl.green)
                with widget1.frame:
                    ui.Label("GREEN", style={"font_size": 100})
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, -150, 0)):
                # cyan & magenta = blue
                widget2 = sc.Widget(300, 150, update_policy=sc.Widget.UpdatePolicy.ALWAYS, color=cl.cyan)
                with widget2.frame:
                    ui.Label("BLUE", style={"font_size": 100, "color": cl.magenta})

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__)

    async def test_unit_xr_scene_ui_no_reflections(self):
        """Test that XR Scene View items support being colorized per-item"""
        image_name = "no_reflections"

        assert self._xr_scene_view is not None
        with self._xr_scene_view.scene:  # type: ignore
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 30, 0)):
                widget = sc.Widget(600, 300, update_policy=sc.Widget.UpdatePolicy.ALWAYS)
                with widget.frame:
                    with ui.VStack():
                        ui.Label("No Reflections", style={"font_size": 100})

        plane_path = Sdf.Path("/World/GroundPlane")
        omni.kit.commands.execute("CreateMeshPrimWithDefaultXform", prim_type="Plane", prim_path=plane_path)

        stage = omni.usd.get_context().get_stage()
        plane_prim = stage.GetPrimAtPath(plane_path)
        plane_prim.GetAttribute("xformOp:scale").Set(Vec3d(10.0), 0)

        await self.wait_post_sync_async(self.UI_APPEARANCE_DELAY)

        async with TestVRProfile(self):
            await self.capture_and_compare_viewport_output_async(image_name, self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__)
