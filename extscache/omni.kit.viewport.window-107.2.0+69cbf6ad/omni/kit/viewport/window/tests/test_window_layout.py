## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["TestWindowLayout"]

from pathlib import Path

import carb
import omni.kit.app
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.ui_test import emulate_mouse_move_and_click, emulate_mouse_move, Vec2

EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests").resolve().absolute()

TEST_WIDTH, TEST_HEIGHT = 360, 240


class TestWindowLayout(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self.sub_test_name = {
            1: "baseline",
            2: "custom_entries",
            3: "flat_single",
            4: "flat_list",
        }[carb.settings.get_settings().get("/exts/omni.kit.viewport.window/testLayout")]

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_menu_items(self):
        """Test that changing attribute that affect projection work when time-sampled."""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        # Move to "Viewport menu" and click
        await self.wait_n_updates()
        await emulate_mouse_move_and_click(Vec2(10, 10))
        # Move to show "Viewport" sub menu
        await emulate_mouse_move(Vec2(80, 40))
        await self.wait_n_updates()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH,
                                 test_name=f"test_menu_items_{self.sub_test_name}",
                                 hide_menu_bar=False)

    # TODO: Test clicking does proper Viewport layout
    async def __test_menu_items(self):
        """Test ViewportWindow creation is layed out in proper order with proper names."""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)
        y_pos = [45, 67, 90, 112, 135]
        for y in y_pos:
            # Move to "Viewport menu" and click
            await self.wait_n_updates()
            await emulate_mouse_move_and_click(Vec2(10, 10))
            # Move to show "Viewport" sub menu
            await emulate_mouse_move(Vec2(80, 40))
            await self.wait_n_updates()

            # Move to show "Viewport" sub menu
            await emulate_mouse_move_and_click(Vec2(160, y))
            await self.wait_n_updates()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH,
                                 test_name=f"test_menu_items_{self.sub_test_name}",
                                 hide_menu_bar=False)
