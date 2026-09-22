# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
from pathlib import Path
from typing import List, Type, Union

import carb.settings
import omni.kit.app
import omni.kit.test
import omni.ui as ui
import omni.usd
from omni.kit.manipulator.tool.snap import SnapProviderManager
from omni.kit.manipulator.tool.snap import settings_constants as c
from omni.kit.manipulator.tool.snap.builtin_snap_tools import (
    GRID_SNAP_NAME, PRIM_SNAP_NAME, SURFACE_SNAP_NAME)
from omni.kit.viewport.utility import get_active_viewport_and_window

from ..menu import SnapMenu

TEST_DATA_PATH = Path(
    f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests"
)


class TestSnap(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._app = omni.kit.app.get_app()
        self._context = omni.usd.get_context()
        self._settings = carb.settings.get_settings()

    async def tearDown(self):
        pass

    async def _test_provider(
        self,
        Gf: Type,
        provider_names: Union[str, List[str]],
        desired,
        locations=[(-0.5, 0.5, 0), (-0.5, -0.5, 0),
                   (0.5, 0.5, 0), (0.5, -0.5, 0)],
        epsilons: dict[int:float] = None,
        repeat_frame: int = 1,
    ):
        provider_names = provider_names if isinstance(
            provider_names, list) else [provider_names]
        self._settings.set(c.SNAP_PROVIDER_NAME_SETTING_PATH, provider_names)
        self._settings.set(c.CONFORM_TO_TARGET_SETTING_PATH, True)

        event = asyncio.Event()
        snap_result = {}

        self._snap_manager.on_began(excluded_paths=[])

        def on_snapped(**kwargs):
            nonlocal snap_result
            snap_result = kwargs
            event.set()

        for i, ndc_location in enumerate(locations):
            for _ in range(repeat_frame):
                event.clear()
                ret = self._snap_manager.get_snap_pos(
                    xform=Gf.Matrix4d(1.0), ndc_location=ndc_location, scene_view=None, on_snapped=on_snapped
                )
                self.assertTrue(ret)
                await event.wait()

                # emulate viewport drag
                await self._app.next_update_async()

            # set to False to log snap_result without failing
            if True:
                desired_result = desired[i]

                epsilon = 1e-1

                if epsilons is not None:
                    if i in epsilons:
                        epsilon = epsilons[i]

                for key, value in desired_result.items():
                    if isinstance(value, Gf.Vec3d) or isinstance(value, float):
                        self.assertTrue(
                            Gf.IsClose(
                                value, snap_result[key], epsilon), f"{value} is not close to {snap_result[key]}"
                        )
                    elif isinstance(value, Gf.Rotation):
                        self.assertTrue(Gf.IsClose(
                            value.GetAxis(), snap_result[key].GetAxis(), epsilon))
                        self.assertTrue(Gf.IsClose(
                            value.GetAngle(), snap_result[key].GetAngle(), epsilon))
                    else:
                        self.assertEqual(value, snap_result[key])
            else:
                print(snap_result)

            self._snap_manager.on_ended()

    async def _test_builtin_snap_providers_with_gf_type(self, Gf: Type):
        usd_path = TEST_DATA_PATH.absolute().resolve().joinpath(
            "usd").joinpath("snap_test.usda")
        success, error = await self._context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)

        resolution = 512
        viewport_api, viewport_window = get_active_viewport_and_window()
        if viewport_window and viewport_api:
            viewport_window.flags = viewport_window.flags | ui.WINDOW_FLAGS_NO_TITLE_BAR

            viewport_window.position_x = 0
            viewport_window.position_y = 0
            viewport_window.width = resolution
            viewport_window.height = resolution
            viewport_window.viewport_api.resolution = (resolution, resolution)
        else:
            self.assertTrue(False, "viewport_api or viewport_window is None")

        # wait until at least 2 frames are rendered otherwise no snap result will return
        await viewport_api.wait_for_rendered_frames(2)

        self._snap_manager = SnapProviderManager(viewport_api=viewport_api)

        # Test prim snap
        desired = [
            {
                "path": "/World/Cube",
                "position": Gf.Vec3d(-25.0, 0.0, 0.0),
                "orient": Gf.Rotation(Gf.Vec3d(1.0, 0.0, 0.0), 180.0),
            },
            {
                "path": "/World/Cube",
                "position": Gf.Vec3d(-25.0, 0.0, 0.0),
                "orient": Gf.Rotation(Gf.Vec3d(1.0, 0.0, 0.0), 180.0),
            },
            {
                "path": "/World/Cube_01",
                "position": Gf.Vec3d(50.0, -100.0, -100.0),
                "orient": Gf.Rotation(Gf.Vec3d(0.0, 1.0, 0.0), 180.0),
            },
            {
                "path": "/World/Cube_01",
                "position": Gf.Vec3d(50.0, -100.0, -100.0),
                "orient": Gf.Rotation(Gf.Vec3d(0.0, 1.0, 0.0), 180.0),
            },
        ]
        await self._test_provider(Gf, PRIM_SNAP_NAME, desired)

        # Test surface snap
        desired = [
            {
                "path": "/World/Cube",
                "position": Gf.Vec3d(-39.5, 200.0, 144.2),
            },
            {
                "path": "/World/Cube",
                "position": Gf.Vec3d(-39.5, 144.2, 200.0),
            },
            {
                "path": "/World/Cube_01",
                "position": Gf.Vec3d(78.2, 100.0, -10.6),
            },
            {
                "path": "/World/Cube_01",
                "position": Gf.Vec3d(78.7, -11.8, 100.0),
            },
        ]
        await self._test_provider(Gf, SURFACE_SNAP_NAME, desired, epsilons={2: 1.5, 3: 0.5})

        # Test grid snap
        desired = [
            {"position": Gf.Vec3d(-100.0, 0.0, -200.0)},
            {"position": Gf.Vec3d(-100.0, 0.0, 100.0)},
            {"position": Gf.Vec3d(100.0, 0.0, -200.0)},
            {"position": Gf.Vec3d(100.0, 0.0, 100.0)},
        ]
        await self._test_provider(Gf, GRID_SNAP_NAME, desired)

        # Test multi snap
        # grid + prim
        desired = [
            {"position": Gf.Vec3d(-100.0, 0.0, 200.0)},
            {
                "path": "/World/Cube",
                "position": Gf.Vec3d(-25.0, 0.0, 0.0),
                "orient": Gf.Rotation(Gf.Vec3d(1.0, 0.0, 0.0), 180.0),
            },
            {
                "path": "/World/Cube_01",
                "position": Gf.Vec3d(50.0, -100.0, -100.0),
                "orient": Gf.Rotation(Gf.Vec3d(0.0, 1.0, 0.0), 180.0),
            },
            {"position": Gf.Vec3d(300.0, 0.0, -400.0)},
        ]
        await self._test_provider(
            Gf,
            [GRID_SNAP_NAME, PRIM_SNAP_NAME],
            desired,
            locations=[
                (-0.9, -0.9, 0),
                (-0.5, -0.5, 0),
                (0.5, 0.5, 0),
                (0.9, 0.9, 0),
            ],  # make sure the location is within (-1, 1), otherwise prim snap exits early and test will give false negative result.
            repeat_frame=4,  # emulate viewport drag
        )

    async def test_builtin_snap_providers_pxr_gf(self):
        import pxr.Gf
        await self._test_builtin_snap_providers_with_gf_type(pxr.Gf)

    async def test_builtin_snap_providers_usdrt_gf(self):
        import usdrt.Gf
        await self._test_builtin_snap_providers_with_gf_type(usdrt.Gf)

    async def test_options_menu(self):
        snap_menu = SnapMenu()

        def _test_suffix(suffix: str):
            options_menu = snap_menu.get_options_menu(suffix=suffix)
            self.assertIsNotNone(options_menu)
            options_model = options_menu.model
            options_model.reset()
            self.assertFalse(options_model.dirty)

        _test_suffix("translate")
        _test_suffix("rotate")
        _test_suffix("scale")
