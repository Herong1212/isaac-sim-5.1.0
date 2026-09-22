# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import pathlib

import omni.kit.app
import omni.kit.test
import omni.usd
from pxr import Gf, Sdf

from ..scripts.usd_adapter import UsdStageAdapter

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
DATA_DIR = EXTENSION_FOLDER_PATH.joinpath("omni/kit/property/adapter/usd/tests/data")

TEST_STAGE_NAME = "cube"


class TestWrapper(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._stage = self._open_stage(TEST_STAGE_NAME)
        self._stage_adapter = UsdStageAdapter(self._stage)

        self._accumulated_changes = []
        self._callback_hit = False
        self._tracker = None

    async def tearDown(self):
        self._stage = None
        self._stage_adapter = None
        self._callback_hit = False

    # ============ REGISTRY TESTS ============

    # Create a change tracker, change an attribute on an object, and make sure the callback is hit.
    async def test_wrapper_callback(self):
        cube = self._stage.GetPrimAtPath("/World/Cube")
        cube_trans_attr = cube.GetAttribute("xformOp:translate")

        attr_names = ["xformOp:translate"]
        prim_paths = [cube.GetPath()]
        self._tracker = self._stage_adapter.CreateChangeTracker(attr_names, prim_paths, self._on_usd_changed)

        # Move the cube
        cube_trans_attr.Set(Gf.Vec3d(0, 200, 0))

        # Make sure the callback was hit
        self.assertTrue(self._callback_hit)
        self._cleanup_after_test(self._tracker)

    # Create a change tracker, change several attributes on an object, make sure the callback is hit, and make sure the changes match.
    async def test_wrapper_multiple_changes(self):
        cube = self._stage.GetPrimAtPath("/World/Cube")
        cube_trans_attr = cube.GetAttribute("xformOp:translate")
        cube_scale_attr = cube.GetAttribute("xformOp:scale")

        expected_changes = []
        expected_changes.append(Sdf.Path("/World/Cube.xformOp:translate"))
        expected_changes.append(Sdf.Path("/World/Cube.xformOp:scale"))

        attr_names = ["xformOp:translate", "xformOp:scale"]
        prim_paths = [cube.GetPath()]
        self._tracker = self._stage_adapter.CreateChangeTracker(attr_names, prim_paths, self._on_usd_changed)

        # Move and scale the cube
        cube_trans_attr.Set(Gf.Vec3d(0, 300, 0))
        cube_scale_attr.Set(Gf.Vec3d(2, 2, 2))

        # Test - Make sure the callback was hit
        self.assertTrue(self._callback_hit)

        # Test - Make sure the actual changes match the expected changes. Convert to sets so the order doesn't matter.
        self.assertTrue(set(expected_changes) == set(self._accumulated_changes))

        self._cleanup_after_test(self._tracker)

    # ============ UTILITY METHODS ============

    def _open_stage(self, stage_name: str):
        path = DATA_DIR.joinpath(stage_name + ".usda")
        usd_context = omni.usd.get_context()
        usd_context.open_stage(str(path))
        return usd_context.get_stage()

    def _on_usd_changed(self, notice, stage):
        self._accumulated_changes.append(notice.GetChangedInfoOnlyPaths()[0])
        self._callback_hit = True

    def _cleanup_after_test(self, tracker):
        tracker.destroy()
        self._callback_hit = False
        self._accumulated_changes.clear()
