# Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import os
import tempfile
import unittest
from pathlib import Path

import carb
import carb.settings
import numpy as np
import omni.kit.app
import omni.kit.test
import omni.volume
from omni.flowusd import _flowusd
from pxr import Usd, UsdGeom
from usdrt import Usd as UsdRT

from ..scripts import commands, common

CURRENT_PATH = Path(__file__).parent.parent.parent.parent
DATA_DIR = CURRENT_PATH.joinpath("data")

TEST_PRESET_NAME = "Fire"
TEST_PTS_FILENAME = "bunnyData.pts"
TEST_PRESET_FIRE = "/Fire/Fire.usda"
TEST_PRESET_WISPY_FIRE = "/Fire/WispyFire.usda"
TEST_VOLUME = "r067064"


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestCommands(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._fire_preset_path = commands.get_preset_url(TEST_PRESET_NAME)
        self._preset_path = "/World/" + TEST_PRESET_NAME

    # After running each test
    async def tearDown(self):
        self._presets_widget = None

    def setup_and_get_stage(self):
        stage = omni.usd.get_context().get_stage()
        self.assertTrue(stage)
        prim = stage.DefinePrim("/World")
        stage.SetDefaultPrim(prim)
        self.assertTrue(stage.HasDefaultPrim())
        return stage

    def _debugTraverse(self):
        stage = omni.usd.get_context().get_stage()
        iterator = iter(stage.TraverseAll())
        for prim in iterator:
            prim_path = str(prim.GetPrimPath())
            print(prim_path)

    async def test_have_fire_preset_usd(self):
        self.assertTrue(os.path.exists(self._fire_preset_path))

    async def test_preset_url(self):
        path1 = str(Path(self._fire_preset_path).resolve())
        path2 = str(Path(commands.get_preset_url(TEST_PRESET_NAME)).resolve())
        self.assertEqual(path1, path2)

    async def test_preset_command(self):
        """Fire preset is used by physics Force demo"""
        stage = self.setup_and_get_stage()

        omni.kit.commands.execute(
            "FlowCreatePresets",
            paths=["/World"],
            preset_name=TEST_PRESET_NAME,
        )

        preset_xform = stage.GetPrimAtPath(self._preset_path)
        self.assertTrue(preset_xform)

        # result = omni.kit.commands.execute(
        #     "FlowCreatePresets",
        #     paths=["/World"],
        #     preset_name="FooBar",
        #     create_copy=False,
        #     layer=1,
        # )

        # self.assertFalse(result[1][0])

    @unittest.skip("Obsolete test")
    async def test_streaming_point_cloud_preset(self):
        self.setup_and_get_stage()

        context = omni.usd.get_context()
        stage_rt = UsdRT.Stage.Attach(context.get_stage_id()) if context else None

        (result, presets_list) = omni.kit.commands.execute("FlowGetPointCloudPresets")
        self.assertTrue(result)
        self.assertTrue(presets_list)
        self.assertTrue(len(presets_list) > 0)

        # default point cloud preset
        self.assertTrue(common.PRESET_POINT_CLOUD_NATIVE in presets_list)

        for preset_name in presets_list:
            omni.kit.commands.execute("FlowCreatePointCloudPreset", paths=[], preset_name=preset_name)

            await omni.kit.app.get_app().next_update_async()

            has_point_cloud_preset = False

            paths = stage_rt.GetPrimsWithTypeName("FlowPointCloud") if stage_rt else []
            has_point_cloud_preset = len(paths) > 0

            self.assertTrue(has_point_cloud_preset)

    async def test_voxelize_points(self):

        await omni.usd.get_context().new_stage_async()

        path = str(DATA_DIR.joinpath(TEST_VOLUME + ".usd"))
        self.assertTrue(omni.usd.get_context().open_stage(path))

        stage = omni.usd.get_context().get_stage()
        points_prim = stage.GetPrimAtPath("/World/" + TEST_VOLUME)
        self.assertTrue(points_prim)
        self.assertEqual(points_prim.GetTypeName(), "Points")
        self.assertTrue(points_prim.HasAttribute("points"))
        points_attr = points_prim.GetAttribute("points")
        self.assertTrue(points_attr)
        self.assertTrue(points_prim.HasAttribute("primvars:displayColor"))
        colors_attr = points_prim.GetAttribute("primvars:displayColor")
        self.assertTrue(colors_attr)

        max_blocks = 32768
        cell_size = 1.0

        # fmt: off
        local_to_world = [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]
        # fmt: on

        iflow = _flowusd.acquire_flowusd_interface()
        nano_vdb_data = iflow.voxelize_points_and_sync_v2(
            np.array(points_attr.Get()),
            np.array(colors_attr.Get()),
            local_to_world,
            local_to_world,
            cell_size,
            max_blocks,
        )

        self.assertTrue(len(nano_vdb_data) == 5)
        grid_data = iflow.buffer_to_volume(nano_vdb_data[4])

        save_params = omni.volume.SaveVolumeParameters()
        save_params.flags = omni.volume.kNanoVDBCodecBlosc

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            out_path = tmpdir + "\\test_volume.nvdb"
            ivolume = omni.volume.get_volume_interface()
            self.assertTrue(ivolume.save_volume(grid_data, out_path, save_params))

        _flowusd.release_flowusd_interface(iflow)
