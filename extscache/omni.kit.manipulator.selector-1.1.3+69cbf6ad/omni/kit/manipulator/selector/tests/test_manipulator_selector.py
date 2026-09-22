# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.test
import inspect
import logging
import os
from pathlib import Path

import sys
import unittest

import carb
import carb.input
import carb.settings
import omni.kit.commands
import omni.kit.ui_test as ui_test
import omni.kit.undo
import omni.usd
from omni.kit.manipulator.prim.core import Constants as prim_c
from omni.kit.manipulator.transform import Constants as transform_c
from omni.kit.test_helpers_gfx.compare_utils import ComparisonMetric, capture_and_compare
from omni.kit.ui_test import Vec2
from omni.ui.tests.test_base import OmniUiTest

CURRENT_PATH = Path(f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data")
OUTPUTS_DIR = Path(omni.kit.test.get_test_output_path()).resolve().absolute()

logger = logging.getLogger(__name__)


class TestSelector(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._context = omni.usd.get_context()
        self._selection = self._context.get_selection()
        self._settings = carb.settings.get_settings()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests").joinpath("golden")
        self._usd_scene_dir = CURRENT_PATH.absolute().resolve().joinpath("tests").joinpath("usd")

        await self._setup()

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def _snapshot(self, golden_img_name: str = "", threshold: float = 2e-4):
        await ui_test.human_delay()

        test_fn_name = ""
        for frame_info in inspect.stack():
            if os.path.samefile(frame_info[1], __file__):
                test_fn_name = frame_info[3]

        golden_img_name = f"{test_fn_name}.{golden_img_name}.png"

        # Because we're testing RTX renderered pixels, use a better threshold filter for differences
        diff = await capture_and_compare(
            golden_img_name,
            threshold=threshold,
            output_img_dir=OUTPUTS_DIR,
            golden_img_dir=self._golden_img_dir,
            metric=ComparisonMetric.MEAN_ERROR_SQUARED,
        )

        self.assertLessEqual(
            diff,
            threshold,
            f"The generated image {golden_img_name} has a difference of {diff}, but max difference is {threshold}",
        )

    async def _setup(
        self,
        scene_file: str = "test_scene.usda",
        enable_toolbar: bool = False,
    ):
        usd_path = self._usd_scene_dir.joinpath(scene_file)
        success, error = await self._context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)

        # move the mouse out of the way
        await ui_test.emulate_mouse_move(Vec2(0, 0))
        await ui_test.human_delay()

        self._settings.set(prim_c.MANIPULATOR_PLACEMENT_SETTING, prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT)
        self._settings.set(transform_c.TRANSFORM_MOVE_MODE_SETTING, transform_c.TRANSFORM_MODE_GLOBAL)
        self._settings.set(transform_c.TRANSFORM_ROTATE_MODE_SETTING, transform_c.TRANSFORM_MODE_GLOBAL)
        self._settings.set(transform_c.TRANSFORM_OP_SETTING, transform_c.TRANSFORM_OP_MOVE)
        self._settings.set("/app/viewport/snapEnabled", False)
        self._settings.set("/persistent/app/viewport/snapToSurface", False)
        self._settings.set("/exts/omni.kit.manipulator.prim.core/tools/enabled", enable_toolbar)

    async def test_multi_manipulator_selector(self):
        from .test_manipulator import TransformManipulatorRegistry

        # Select the /Cube, should show default manipulator
        self._selection.set_selected_prim_paths(["/Cube"], True)
        await ui_test.human_delay()
        await self._snapshot("default_mesh")

        # Select the /Xform, should show default manipulator
        self._selection.set_selected_prim_paths(["/World"], True)
        await ui_test.human_delay()
        await self._snapshot("default_xform")

        # Register the test manipulator that is specialized for Mesh
        test_manipulator = TransformManipulatorRegistry()

        await ui_test.human_delay()

        # Select the /Cube, should show overridden manipulator
        self._selection.set_selected_prim_paths(["/Cube"], True)
        await ui_test.human_delay()
        await self._snapshot("overridden_mesh")

        # Select the /Xform, should still show default manipulator as it's not a mesh
        self._selection.set_selected_prim_paths(["/World"], True)
        await ui_test.human_delay()
        await self._snapshot("default_xform")

        # Remove the overridden manipulator
        test_manipulator.destroy()
        test_manipulator = None

        # Select the /Cube, should revert back to default manipulator
        self._selection.set_selected_prim_paths(["/Cube"], True)
        await ui_test.human_delay()
        await self._snapshot("default_mesh")
