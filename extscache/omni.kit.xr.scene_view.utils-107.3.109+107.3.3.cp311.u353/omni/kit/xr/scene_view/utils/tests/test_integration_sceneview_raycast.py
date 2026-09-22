# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TestSceneViewRaycast"]

import math
import os
import unittest
from typing import List

import numpy as np
from carb import Float3
from omni import ui
from omni.kit.xr.core import XRCore, XRRay, XRRayQueryResult
from omni.kit.xr.core.test_utils import TestVRProfile
from omni.kit.xr.scene_view.core import InputButtonMap, InputType, XRSceneView
from omni.kit.xr.scene_view.utils.manipulator_components.widget_component import WidgetComponent
from omni.kit.xr.scene_view.utils.ui_container import UiContainer

from .base_sceneview_test import BaseSceneViewTest


class _TestWidget(ui.Widget):
    def __init__(self):
        super().__init__()

        ui.Button("Button")


class TestSceneViewRaycast(BaseSceneViewTest):
    DEFAULT_WIDTH: int = 600
    DEFAULT_HEIGHT: int = 200

    async def setUp(self):
        await super().setUp()
        await self._create_test_widget()

    async def _create_test_widget(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        """
        Create the default UI widget for this test, with optional custom width and height parameters,
        and wait for any required delays to make sure it shows up in time.

        :param width: (optional) the width of the UI widget
        :param height: (optional) the height of the UI widget
        """
        self._test_widget = UiContainer(WidgetComponent(_TestWidget, width, height))
        await self.wait_materials_loaded_async()
        await self.wait_post_sync_async(self.TEX_SYNC_FRAMES)

    @staticmethod
    def _gen_spherical_rays(radius: float, z_offset: float, target_offset: float) -> List[XRRay]:
        """
        Generate rays along the edge of a sphere between -1.5 and 1.5 radians from the positive-z
        point, pointing towards the center of the sphere.

        An offset is applied to the direction target in order encourage the test to use imperfect
        directional rays so that all rays are likely to be hitting slightly different points along
        the target surface.

        The angle interval is related to PI to try to ensure that imperfect angles are generated
        in case that causes raycast failures.

        :param radius: how far to extend the "direction" part of the ray out from the center
        :param z_offset: how far back along the z-axis to originate the rays
        :param target_offset: an offset along the z-axis to push the rays' target (otherwise they will all target the origin)
        :return:
        """
        rays: List[XRRay] = []
        interval = math.pi / 10
        for theta in np.arange(-1.5, 1.5, interval):
            for phi in np.arange(-1.5, 1.5, interval):
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.sin(theta) * math.sin(phi)
                z = radius * math.cos(theta)

                ray_origin = [x, y, z + z_offset]
                ray_direction = [-x, -y, -z - z_offset + target_offset]
                rays.append(XRRay(ray_origin, ray_direction))
        return rays

    @staticmethod
    def _gen_area_rays(z_offset: float, width: float = DEFAULT_WIDTH, height: float = DEFAULT_HEIGHT) -> List[XRRay]:
        """
        Generate a list of XRRays spread across a 2D area (X/Y), offset along Z, pointing along
        the negative Z-axis.

        The offset interval includes PI in order to try and create imperfect intervals between the
        rays in case that causes raycast failures.

        :param z_offset: offset along the z-axis for all of the rays
        :param width: x-dimension of the area along which to generate rays
        :param height: y-dimension of the area along which to generate rays
        :return: the List[XRRay] containing the generated rays
        """
        # Subtract 5 from the edges to allow for transparency around the widget.
        half_height = height / 2 - 5
        half_width = width / 2 - 5

        # Generate rays across the whole surface, using a less regular interval in case regular intervals
        # work more reliable, we can catch the irregular ones
        rays: List[XRRay] = []
        interval = math.pi + 10
        for y in np.arange(-half_height, half_height, interval):
            for x in np.arange(-half_width, half_width, interval):
                rays.append(XRRay([0, 0, z_offset], [-x, -y, -z_offset], 0, 1000))
        return rays

    async def _validate_rays(self, rays: List[XRRay]) -> int:
        """
        Use the supplied rays to generate raycasts, then submit one each frame and count
        how many rays result in invalid or non-hit results.

        :param rays: the list of rays to submit and test
        :return: the number of missed/failed raycasts
        """
        current_idx: int = 0
        failed_hits: int = 0

        def _raycast_callback(_ray: XRRay, result: XRRayQueryResult):
            nonlocal current_idx
            nonlocal failed_hits

            if not result.valid:
                failed_hits += 1
                print(f"Detected failed raycast at index {current_idx}")
            current_idx += 1

        for ray in rays:
            XRCore.get_singleton().submit_raycast_query(ray, _raycast_callback)
            await self.wait_post_sync_async(1)

        await self.wait_post_sync_async(3)
        return failed_hits

    async def _validate_rays_as_ui_input(self, rays: List[XRRay]) -> int:
        """
        Use the supplied rays to generate raycasts AND input sent to the UI system, then
        submit one each frame and count how many rays result in invalid or non-hit results.

        :param profile: the current XRProfile
        :param rays: the list of rays to submit and test
        :return: the number of missed/failed raycasts
        """
        failed_hits: int = 0

        def _raycast_callback(_ray: XRRay, result: XRRayQueryResult):
            if not result.valid:
                nonlocal failed_hits
                failed_hits += 1

        for ray in rays:
            origin: Float3 = ray.origin  # type: ignore
            forward: Float3 = ray.forward  # type: ignore

            assert type(self._test_widget.scene_view) is XRSceneView
            self._test_widget.scene_view.input_event_stream.push(
                InputType.WorldSpaceMovement, payload={"origin": origin, "direction": forward}
            )
            await self.wait_post_sync_async(1)
            XRCore.get_singleton().submit_raycast_query(ray, _raycast_callback)

        await self.wait_post_sync_async(3)

        return failed_hits

    async def test_integration_raycast_ui_hits(self):
        """
        Test a handful of pre-made, simple raycasts as a quick sanity check
        """
        async with TestVRProfile(self):
            rays = [
                XRRay([0, 0, 1], [0, 0, -1], 0.0, 100),
                XRRay([25, 0, 1], [0, 0, -1], 0.0, 100),
                XRRay([0, 25, 1], [0, 0, -1], 0.0, 100),
                XRRay([-25, 0, 1], [0, 0, -1], 0.0, 100),
                XRRay([0, -25, 1], [0, 0, -1], 0.0, 100),
            ]
            failed_hits: int = await self._validate_rays(rays)

            self.assertEqual(failed_hits, 0)

    async def test_integration_raycast_ui_many_angles(self):
        """
        Test raycasts arranged at angles
        """
        async with TestVRProfile(self):
            rays: List[XRRay] = self._gen_spherical_rays(50, 200, -5)
            failed_hits: int = await self._validate_rays(rays)

            self.assertEqual(failed_hits, 0)

    async def test_integration_raycast_ui_whole_surface(self):
        """
        Test raycasts arranged along the whole surface
        """
        async with TestVRProfile(self):
            rays: List[XRRay] = self._gen_area_rays(20)
            failed_hits: int = await self._validate_rays(rays)

            self.assertEqual(failed_hits, 0)

    async def test_integration_raycast_ui_with_input_spherical_origin(self):
        """
        Test raycasts arranged at angles while also pushing input to the UI system
        """
        async with TestVRProfile(self) as profile:
            rays: List[XRRay] = self._gen_spherical_rays(50, 200, -5)

            failed_hits: int = await self._validate_rays_as_ui_input(rays)
            self.assertEqual(failed_hits, 0)

    async def test_integration_raycast_ui_with_input_whole_surface(self):
        """
        Test raycasts arranged along the whole surface while also pushing input to the UI system
        """
        async with TestVRProfile(self):
            rays: List[XRRay] = self._gen_area_rays(20)

            failed_hits: int = await self._validate_rays_as_ui_input(rays)
            self.assertEqual(failed_hits, 0)

    # async def test_integration_raycast_ui_playback(self):
    #     """
    #     Test an actual recorded VR session to ensure that ad-hoc, real-world rays don't cause
    #     raycast misses to occur in ways that the generated tests can't catch.
    #     """
    #     golden_image_source = __name__
    #     recordings_source_extension = "omni.kit.xr.scene_view.utils"
    #
    #     async with TestVRProfile(self):
    #         await self.load_stage_async(str(self.get_usd_directory().joinpath("UIRaycast/cube_close_to_vr_start.usd")))
    #         await self.wait_post_sync_async(100)
    #
    #         # recording_file_path = str(
    #         #     self.get_recording_directory(recordings_source_extension).joinpath(
    #         #         "ui_input_replay.json"
    #         #     )
    #         # )
    #         await self.capture_and_compare_stereo_output_async("ui_raycast_test_base", 0.001, golden_image_source)
    #         await self.wait_post_sync_async(50)
    #
    #         images = [
    #             (200, "ui_raycast_test_1"),
    #             (300, "ui_raycast_test_2"),
    #             (300, "ui_raycast_test_3"),
    #             (300, "ui_raycast_test_4"),
    #         ]
    #
    #         await self.run_playback(
    #             str(
    #                 self.get_recording_directory(recordings_source_extension).joinpath(
    #                     "ui_input_replay.json"
    #                 )
    #             ),
    #             images,  # list of image tuples
    #             0.003,
    #             golden_image_source,
    #         )
    #
    #         # event = asyncio.Event()
    #         # waiter_task = asyncio.create_task(self.wait_until_event_set(event))
    #         #
    #         # await self.play_recording_file(recording_file_path, "testvr", event)
    #         await self.wait_post_sync_async(5)
    #
    #         # await waiter_task
    #
    #     # Ensure we run through at least a full cycle
    #     await self.wait_post_sync_async(3)
    #     self.assertEqual(self.get_current_profile_name(), "")
