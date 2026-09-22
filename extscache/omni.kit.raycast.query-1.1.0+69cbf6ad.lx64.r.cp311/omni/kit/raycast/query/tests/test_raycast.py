# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
from pathlib import Path

import carb
import carb.settings
import omni.kit.app
import omni.kit.commands
import omni.kit.raycast.query
from omni.kit.raycast.query import utils as rq_utils
import omni.kit.test
import omni.usd
from omni import ui
import omni.kit.ui_test as ui_test
from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window
from pxr import Gf, UsdGeom

SETTING_SECTION_ENABLED = "/rtx/sectionPlane/enabled"
SETTING_SECTION_PLANE = "/rtx/sectionPlane/plane"
DATA_PATH = Path(
    carb.tokens.get_tokens_interface().resolve("${omni.kit.raycast.query}/data")
)
USD_FILES = DATA_PATH.joinpath("tests").joinpath("usd")


class TestRaycast(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.get_settings()
        self._app = omni.kit.app.get_app()
        self._context = omni.usd.get_context()
        self._raycast = omni.kit.raycast.query.acquire_raycast_query_interface()

    async def tearDown(self):
        pass

    async def _setup_simple_scene(self):
        await self._context.new_stage_async()
        stage = self._context.get_stage()
        self.assertTrue(stage)

        CUBE_PATH = "/Cube"

        cube = UsdGeom.Cube.Define(stage, CUBE_PATH)
        UsdGeom.XformCommonAPI(cube.GetPrim()).SetTranslate(Gf.Vec3d(123.45, 0, 0))

        return cube

    async def _setup_complex_scene(self):
        await self._context.new_stage_async()
        stage = self._context.get_stage()
        self.assertTrue(stage)

        cube1 = UsdGeom.Cube.Define(stage, "/Cube1")
        UsdGeom.XformCommonAPI(cube1.GetPrim()).SetTranslate(Gf.Vec3d(-1, 0, -1))

        cube2 = UsdGeom.Cube.Define(stage, "/Cube2")
        UsdGeom.XformCommonAPI(cube2.GetPrim()).SetTranslate(Gf.Vec3d(1, 0, 1))

        cube3 = UsdGeom.Cube.Define(stage, "/Cube3")
        UsdGeom.XformCommonAPI(cube3.GetPrim()).SetTranslate(Gf.Vec3d(-1, 0, 3))

        return [cube1, cube2, cube3]

    async def test_single_raycast_query(self):
        await self._setup_simple_scene()
        viewport_api = get_active_viewport()

        await viewport_api.wait_for_rendered_frames(5)

        ray = omni.kit.raycast.query.Ray((1000, 0, 0), (-1, 0, 0))
        future = asyncio.Future()

        def callback(ray, result):
            future.set_result(result)

        self._raycast.submit_raycast_query(ray, callback)

        result = await future

        self.assertTrue(result.valid)
        self.assertTrue(
            Gf.IsClose(Gf.Vec3d(*result.hit_position), Gf.Vec3d(124.45, 0, 0), 1e-4)
        )
        self.assertTrue(Gf.IsClose(result.hit_t, 875.551, 1e-4))
        self.assertTrue(Gf.IsClose(Gf.Vec3d(*result.normal), Gf.Vec3d(1, 0, 0), 1e-4))
        self.assertEqual(result.get_target_usd_path(), "/Cube")

    async def test_ray_with_section_tool(self):
        """Test if raycast section plane awareness"""
        await self._context.new_stage_async()

        # Set up a scene with 2 large flattened cubes as floors, one is 3m higher the other
        cube_bottom_path = "/World/Cube_bottom"
        omni.kit.commands.create(
            "CreatePrim",
            prim_type="Cube",
            prim_path=cube_bottom_path,
            select_new_prim=False,
        ).do()

        omni.kit.commands.create(
            "TransformPrimSRTCommand",
            path=cube_bottom_path,
            new_scale=Gf.Vec3d(1000, 1, 1000),
        ).do()

        cube_top_path = "/World/Cube_top"
        cube_top_height = 300.0
        omni.kit.commands.create(
            "CreatePrim",
            prim_type="Cube",
            prim_path=cube_top_path,
            select_new_prim=False,
        ).do()

        omni.kit.commands.create(
            "TransformPrimSRTCommand",
            path=cube_top_path,
            new_scale=Gf.Vec3d(1000, 1, 1000),
            new_translation=Gf.Vec3d(0, cube_top_height, 0),
        ).do()

        await self._app.next_update_async()

        section_plane_height = 150
        self._settings.set(SETTING_SECTION_ENABLED, True)
        self._settings.set(SETTING_SECTION_PLANE, [0, -1, 0, section_plane_height])

        async def submit_ray_and_wait_for_result(ray):
            future = asyncio.Future()

            def callback(ray, result):
                future.set_result(result)

            self._raycast.submit_raycast_query(ray, callback)

            return await future

        #### Test 1, ray origin is culled, and direction points away from section plane ####
        ray = omni.kit.raycast.query.Ray((0, section_plane_height + 10, 0), (0, 1, 0))
        result = await submit_ray_and_wait_for_result(ray)

        # no valid result should return
        self.assertFalse(result.valid)

        #### Test 1.1, ray origin is culled, and direction points away from section plane, but no section awareness ####
        ray = omni.kit.raycast.query.Ray(
            (0, section_plane_height + 10, 0), (0, 1, 0), adjust_for_section=False
        )
        result = await submit_ray_and_wait_for_result(ray)

        # ray should hit Top Cube even though it's culled
        self.assertTrue(result.valid)
        self.assertAlmostEqual(result.hit_position[1], cube_top_height - 1.0)

        #### Test 2, ray origin is culled, but direction points towards section plane ####
        ray = omni.kit.raycast.query.Ray((0, cube_top_height + 20, 0), (0, -1, 0))
        result = await submit_ray_and_wait_for_result(ray)

        # ray should skip top Cube and hit bottom Cube
        self.assertTrue(result.valid)
        self.assertAlmostEqual(result.hit_position[1], 1.0)

        #### Test 2.1, ray origin is culled, but direction points towards section plane, but no section awareness ####
        ray = omni.kit.raycast.query.Ray(
            (0, cube_top_height + 20, 0), (0, -1, 0), adjust_for_section=False
        )
        result = await submit_ray_and_wait_for_result(ray)

        # ray should hit top Cube even though it's culled
        self.assertTrue(result.valid)
        self.assertAlmostEqual(result.hit_position[1], cube_top_height + 1.0)

        #### Test 3, ray origin is not culled, but direction points towards section plane ####
        ray = omni.kit.raycast.query.Ray((0, section_plane_height - 10, 0), (0, 1, 0))
        result = await submit_ray_and_wait_for_result(ray)

        # no valid result should return
        self.assertFalse(result.valid)

        #### Test 4, ray origin is not culled, and direction points away from section plane ####
        ray = omni.kit.raycast.query.Ray((0, section_plane_height - 10, 0), (0, -1, 0))
        result = await submit_ray_and_wait_for_result(ray)

        # ray should hit bottom Cube
        self.assertTrue(result.valid)
        self.assertAlmostEqual(result.hit_position[1], 1.0)

        self._settings.set(SETTING_SECTION_ENABLED, False)

    async def test_raycast_from_mouse_ndc(self):
        await self._context.new_stage_async()

        omni.kit.commands.create(
            "CreatePrim",
            prim_type="Cube",
            prim_path="/World/Cube",
            select_new_prim=False,
        ).do()

        omni.kit.commands.create(
            "TransformPrimSRTCommand",
            path="/World/Cube",
            new_scale=Gf.Vec3d(1000, 1, 1000),
        ).do()

        viewport_api = get_active_viewport()
        await viewport_api.wait_for_rendered_frames(5)

        future = asyncio.Future()

        def callback(ray, result):
            future.set_result(result)

        rq_utils.raycast_from_mouse_ndc(
            (0, 0),
            viewport_api,
            callback,
        )

        result = await future
        self.assertTrue(result.valid)
        self.assertTrue(
            Gf.IsClose(Gf.Vec3d(*result.hit_position), Gf.Vec3d(1, 1, 1), 1e-4)
        )
        self.assertTrue(Gf.IsClose(result.hit_t, 863.2943, 1e-4))
        self.assertTrue(Gf.IsClose(Gf.Vec3d(*result.normal), Gf.Vec3d(0, 1, 0), 1e-4))
        self.assertEqual(result.get_target_usd_path(), "/World/Cube")

    async def test_viewport_drag_and_drop(self):
        await self._context.new_stage_async()
        stage = self._context.get_stage()
        # Create a floor
        floor = UsdGeom.Cube.Define(stage, "/World/floor")
        UsdGeom.XformCommonAPI(floor.GetPrim()).SetTranslate(Gf.Vec3d(0, 100, 0))
        UsdGeom.XformCommonAPI(floor.GetPrim()).SetScale(Gf.Vec3f(500, 1, 500))

        await ui_test.wait_n_updates(10)

        # Create an area in test window as drag source
        drag_window_size = 80
        drag_source_window = ui.Window(
            "TestDrag", width=drag_window_size, height=drag_window_size
        )
        with drag_source_window.frame:
            stack = ui.ZStack()
            with stack:
                ui.Rectangle(width=drag_window_size, height=drag_window_size)

        def on_drag():
            return str(USD_FILES.joinpath("test_drag_drop.usda"))

        stack.set_drag_fn(on_drag)

        # Layout window
        app_window = omni.appwindow.get_default_app_window()
        window_width = app_window.get_width()
        window_height = app_window.get_height()
        vp_window = get_active_viewport_window()
        vp_width = int(window_width / 2)
        vp_height = int(window_height / 2)
        vp_window.position_x = 0
        vp_window.position_y = 0
        vp_window.width = vp_width
        vp_window.height = vp_height
        drag_source_window.position_x = 0
        drag_source_window.position_y = vp_height + 10
        drag_source_window.focus()
        await ui_test.wait_n_updates(10)

        # Drag and drop
        rect = ui_test.find("TestDrag//Frame/**/Rectangle[*]")
        await ui_test.human_delay(20)
        vp_center = ui_test.Vec2(
            int(vp_window.position_x + vp_window.width / 2),
            int(vp_window.position_y + vp_window.height / 2),
        )
        await rect.drag_and_drop(vp_center)
        await ui_test.human_delay(20)

        # Check dropped prim
        dropped_path = "/test_drag_drop"
        droped_prim = stage.GetPrimAtPath(dropped_path)
        self.assertTrue(droped_prim)

        world_mtx = omni.usd.get_world_transform_matrix(droped_prim)
        dropped_pos = world_mtx.ExtractTranslation()
        # Expected height = floor height + floor thickess
        self.assertTrue(Gf.IsClose(dropped_pos[1], 101.0, 1e-2))
        await ui_test.human_delay(20)

        if drag_source_window:
            drag_source_window.destroy()
            del drag_source_window

    async def test_raycast_sequence(self):
        await self._setup_simple_scene()
        viewport_api = get_active_viewport()

        await viewport_api.wait_for_rendered_frames(5)

        ray = omni.kit.raycast.query.Ray((1000, 0, 0), (-1, 0, 0))

        seq_id = self._raycast.add_raycast_sequence()
        self.assertNotEqual(seq_id, -1)

        result = self._raycast.submit_ray_to_raycast_sequence(seq_id, ray)
        self.assertEqual(result, omni.kit.raycast.query.Result.SUCCESS)

        while True:
            (error, seq_ray, result) = (
                self._raycast.get_latest_result_from_raycast_sequence(seq_id)
            )
            if error == omni.kit.raycast.query.Result.SUCCESS:
                if result.valid:
                    self.assertEqual(seq_ray, ray)
                    self.assertTrue(
                        Gf.IsClose(
                            Gf.Vec3d(*result.hit_position), Gf.Vec3d(124.45, 0, 0), 1e-4
                        )
                    )
                    self.assertTrue(Gf.IsClose(result.hit_t, 875.551, 1e-4))
                    self.assertTrue(
                        Gf.IsClose(Gf.Vec3d(*result.normal), Gf.Vec3d(1, 0, 0), 1e-4)
                    )
                    self.assertEqual(result.get_target_usd_path(), "/Cube")
                    break

            await self._app.next_update_async()

        result = self._raycast.remove_raycast_sequence(seq_id)
        self.assertEqual(result, omni.kit.raycast.query.Result.SUCCESS)

    async def test_raycast_sequence_array(self):
        await self._setup_complex_scene()
        viewport_api = get_active_viewport()

        await viewport_api.wait_for_rendered_frames(5)

        ray1 = omni.kit.raycast.query.Ray(
            (-1, 0, -3), (0, 0, 1), 0, 4
        )  # This ray will hit cube1
        ray2 = omni.kit.raycast.query.Ray(
            (-1, 0, 1), (1, 0, 0)
        )  # This ray will hit cube2
        ray3 = omni.kit.raycast.query.Ray(
            (1, 0, 3), (-1, 0, 0)
        )  # This ray will hit cube3
        ray4 = omni.kit.raycast.query.Ray(
            (1, 0, -1), (1, 0, 0)
        )  # This ray won't hit anything
        ray_array = [ray1, ray2, ray3, ray4]

        seq_id = self._raycast.add_raycast_sequence()
        self.assertNotEqual(seq_id, -1)

        # Optional. The python API submit_ray_to_raycast_sequence_array will set the size automatically.
        # In C++ API, the size needs to be set explicitly.
        # result = self._raycast.set_raycast_sequence_array_size(seq_id, len(ray_array))
        # self.assertEqual(result, omni.kit.raycast.query.Result.SUCCESS)

        result = self._raycast.submit_ray_to_raycast_sequence_array(seq_id, ray_array)
        self.assertEqual(result, omni.kit.raycast.query.Result.SUCCESS)

        expected_hit_positions = [
            Gf.Vec3d(-1, 0, -2),
            Gf.Vec3d(0, 0, 1),
            Gf.Vec3d(0, 0, 3),
            # No hit for ray4
        ]

        expected_hit_normals = [
            Gf.Vec3d(0, 0, -1),
            Gf.Vec3d(-1, 0, 0),
            Gf.Vec3d(1, 0, 0),
            # No hit for ray4
        ]

        while True:
            (error, seq_rays, results) = (
                self._raycast.get_latest_result_from_raycast_sequence_array(seq_id)
            )
            if error == omni.kit.raycast.query.Result.SUCCESS:
                valid_results = [False] * len(ray_array)

                for i, ray in enumerate(ray_array):
                    seq_ray = seq_rays[i]
                    result = results[i]

                    if result.valid:
                        valid_results[i] = True

                        self.assertEqual(seq_ray, ray)
                        self.assertTrue(
                            Gf.IsClose(
                                Gf.Vec3d(*result.hit_position),
                                expected_hit_positions[i],
                                1e-4,
                            ),
                            f"{result.hit_position} != {expected_hit_positions[i]}",
                        )
                        self.assertTrue(
                            Gf.IsClose(
                                Gf.Vec3d(*result.normal), expected_hit_normals[i], 1e-4
                            ),
                            f"{result.normal} != {expected_hit_normals[i]}",
                        )
                        self.assertEqual(result.get_target_usd_path(), f"/Cube{i+1}")

                if valid_results == [True, True, True, False]:
                    break

            await self._app.next_update_async()

        result = self._raycast.remove_raycast_sequence(seq_id)
        self.assertEqual(result, omni.kit.raycast.query.Result.SUCCESS)

