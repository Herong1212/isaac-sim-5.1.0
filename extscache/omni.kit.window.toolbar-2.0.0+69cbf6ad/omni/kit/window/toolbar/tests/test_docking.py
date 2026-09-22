# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path
import omni.appwindow
import omni.kit.app
import omni.kit.test
import omni.kit.window.toolbar
import omni.ui as ui
import omni.kit.ui_test as ui_test
from omni.ui.tests.test_base import OmniUiTest

from omni.kit.ui_test import emulate_mouse_move, emulate_mouse_move_and_click, Vec2

from omni.kit.widget.toolbar.tests.helpers import reset_toolbar_settings

CURRENT_PATH = Path(__file__).parent
GOLDEN_IMAGE_DIR = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data", "tests", "golden_img").absolute()

class ToolbarDockingTest(OmniUiTest):
    async def setUp(self):
        await super().setUp()

        reset_toolbar_settings()

        self._main_dockspace = ui.Workspace.get_window("DockSpace")
        self._toolbar_handle = ui.Workspace.get_window(omni.kit.window.toolbar.Toolbar.WINDOW_NAME)
        self._toolbar_handle.undock()

        # Move mouse to origin
        await emulate_mouse_move(Vec2(0, 0))
        await ui_test.human_delay(10)

    async def test_docking_vertical(self):
        """Test vertical docking behavior."""
        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.LEFT)
        await ui_test.human_delay(10)

        await self.finalize_test(golden_img_dir=GOLDEN_IMAGE_DIR, golden_img_name="v_dock.png")

    async def test_docking_horizontal(self):
        """Test horizontal docking behavior."""
        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.TOP)
        await ui_test.human_delay(10)

        await self.finalize_test(golden_img_dir=GOLDEN_IMAGE_DIR, golden_img_name="h_dock.png")

    async def test_docking_vertical_context_menu(self):
        """Test vertical docking behavior showing context menu."""
        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.LEFT)
        await ui_test.human_delay(10)

        await emulate_mouse_move_and_click(Vec2(35, 135), right_click=True)
        await ui_test.human_delay(10)

        await self.finalize_test(golden_img_dir=GOLDEN_IMAGE_DIR, golden_img_name="v_dock_menu.png")

    async def test_docking_horizontal_context_menu(self):
        """Test horizontal docking behavior showing context menu."""
        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.TOP)
        await ui_test.human_delay(10)

        await emulate_mouse_move_and_click(Vec2(125, 35), right_click=True)
        await ui_test.human_delay(10)

        await self.finalize_test(golden_img_dir=GOLDEN_IMAGE_DIR, golden_img_name="h_dock_menu.png")

    async def test_docking_vertical_grab_context_menu(self):
        """Test vertical docking behavior showing grabber context menu."""
        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.LEFT)
        await ui_test.human_delay(10)

        await emulate_mouse_move_and_click(Vec2(15, 35), right_click=True)
        await ui_test.human_delay(10)

        # sometimes the menu appears 1 pixel lower than expected
        await self.finalize_test(golden_img_dir=GOLDEN_IMAGE_DIR, golden_img_name="v_dock_grab_menu.png", threshold=0.07)
