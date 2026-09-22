# Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import shutil
import tempfile
from pathlib import Path

import omni.kit.app
import omni.kit.test
import omni.usd
from omni.vdb_timesample_editor import TimeSampleEditor
from pxr import Sdf, Usd

CURRENT_PATH = Path(__file__).parent.parent.parent.parent
DATA_DIR = CURRENT_PATH.joinpath("data")

TEST_DATA_NAME = "mdlanimation.usda"
PRIM_PATH = "/World/Looks/OmniVolumeDensity/Shader"
ATTR_NAME = "inputs:volume_density_texture"
ASSET_PATH = "@./v02/Explosion_VDB_Cache.%d.vdb@"


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestTimeSampleEditor(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            tmp_path = str(Path(tmpdir).joinpath(TEST_DATA_NAME))
            file_path = str(DATA_DIR.joinpath(TEST_DATA_NAME))
            shutil.copy(file_path, tmp_path)
            stage = Usd.Stage.Open(tmp_path)
            usd_context = omni.usd.get_context()
            await usd_context.attach_stage_async(stage)
            stage = usd_context.get_stage()
            self.assertTrue(stage)
            prim = stage.GetPrimAtPath(PRIM_PATH)
            self.assertTrue(prim and prim.IsValid())
            self._attr = prim.GetAttribute(ATTR_NAME)
            self.assertTrue(self._attr and self._attr.IsValid())
            self._editor = TimeSampleEditor()
            self._editor.show(self._attr.GetPath())
            self.assertTrue(self._editor)

    # After running each test
    async def tearDown(self):
        self._editor.close()
        await omni.usd.get_context().close_stage_async()

    async def test_create_timesamples(self):
        self._editor.path.model.set_value(ASSET_PATH)
        self._editor.begin.model.set_value(5)
        self._editor.step.model.set_value(0.5)
        self._editor.first.model.set_value(1)
        self._editor.last.model.set_value(2)
        self._editor.zeros.model.set_value(1)

        self._editor._create_time_samples()

        text_lines = self._editor.text_editor.text_lines

        self.assertEqual(len(text_lines), 2)

        self.assertEqual(text_lines[0], "5.0: @./v02/Explosion_VDB_Cache.01.vdb@")
        self.assertEqual(text_lines[1], "5.5: @./v02/Explosion_VDB_Cache.02.vdb@")

    async def test_load_timesamples(self):
        text_lines = self._editor.text_editor.text_lines
        self.assertEqual(len(text_lines), 50)
        self.assertEqual(text_lines[0], "0: @./v02/Explosion_VDB_Cache.1.vdb@")

    async def test_save_timesamples(self):
        def test_line(line, time_code, asset):
            self._editor.text_editor.text = line
            result = self._editor._save_time_samples()
            self.assertTrue(result)
            time_samples = self._attr.GetMetadata("timeSamples")
            self.assertTrue(time_samples)
            self.assertEqual(time_samples[time_code], Sdf.AssetPath(asset))

        test_line("1:@./v02/Explosion_VDB_Cache@somewhere.00.vdb@", 1, "./v02/Explosion_VDB_Cache@somewhere.00.vdb")
        test_line(" 1.1a : @C:/v02/Explosion_VDB_Cache.00.vdb@", 1.1, "C:/v02/Explosion_VDB_Cache.00.vdb")

    async def test_clear_timesamples(self):
        self._editor._clear_time_samples()

        await omni.kit.app.get_app().next_update_async()

        time_samples = self._attr.GetMetadata("timeSamples")
        self.assertFalse(time_samples)
