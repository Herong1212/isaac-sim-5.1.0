## Copyright (c) 2018-2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from ..scripts.extension import get_main_window
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.kit.mainwindow
import omni.kit.test
import omni.ui as ui
import carb.settings

from pathlib import Path

GOLDEN_IMAGE_PATH = Path(omni.kit.test.get_test_output_path()).resolve().absolute()

class Test(OmniUiTest):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_dockspace(self):
        """Checking mainwindow is initialized"""
        self.assertIsNotNone(get_main_window())

        await omni.kit.app.get_app().next_update_async()
        main_dockspace = ui.Workspace.get_window("DockSpace")
        self.assertIsNotNone(main_dockspace)

    async def test_windows(self):
        """Testing windows"""
        await self.create_test_area()

        width = ui.Workspace.get_main_window_width()
        height = ui.Workspace.get_main_window_height()
        window1 = ui.Window("Viewport", width=width, height=height)
        window2 = ui.Window("Viewport", width=width, height=height)
        window3 = ui.Window("Something Else", width=width, height=height)

        with window1.frame:
            ui.Rectangle(style={"background_color": ui.color.indigo})

        with window2.frame:
            ui.Label("NVIDIA")

        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=GOLDEN_IMAGE_PATH)

        for i in range(3):
            await omni.kit.app.get_app().next_update_async()
