## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from ..quicklayout import QuickLayout
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
import json
import omni.kit
import omni.ui as ui
import os
import tempfile
from omni.kit.mainwindow import get_main_window

CURRENT_PATH = Path(__file__).parent.joinpath("../../../../data")
ROOT_WINDOW_NAME = "DockSpace"


class TestQuickLayout(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")
        self._dump_workspace = ui.Workspace.dump_workspace()

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        ui.Workspace.restore_workspace(self._dump_workspace)
        await super().tearDown()

    async def test_floating(self):
        ui.Workspace.clear()

        window_left = ui.Window("Left", width=100, height=100, position_x=10, position_y=10)
        window_right = ui.Window("Right", width=100, height=100, position_x=120, position_y=10)

        await omni.kit.app.get_app().next_update_async()

        temp_file = Path(tempfile.gettempdir()).joinpath("workspace_" + next(tempfile._get_candidate_names()) + ".json")
        QuickLayout.save_file(f"{temp_file}")

        with open(f"{temp_file}") as json_file:
            data = json.load(json_file)

        os.remove(f"{temp_file}")

        left_pos = 0
        right_pos = 0
        for win in data:
            if "title" in win:
                if win["title"] == "Left":
                    left_pos = win['position_x']
                elif win["title"] == "Right":
                    right_pos = win['position_x']

        # self.assertEqual(len(data), 3)  # Not true if test_restore is run first
        self.assertEqual(left_pos, 10.0)
        self.assertEqual(right_pos, 120.0)

    async def test_docking(self):
        ui.Workspace.clear()

        window_left = ui.Window("Left2", width=100, height=100, position_x=10, position_y=10)
        window_right = ui.Window("Right2", width=100, height=100, position_x=120, position_y=10)
        target_window = ui.Workspace.get_window(ROOT_WINDOW_NAME)

        await omni.kit.app.get_app().next_update_async()

        window_left.dock_in(target_window, ui.DockPosition.SAME)
        window_right.dock_in(window_left, ui.DockPosition.RIGHT, 0.5)

        await omni.kit.app.get_app().next_update_async()

        temp_file = Path(tempfile.gettempdir()).joinpath("workspace_" + next(tempfile._get_candidate_names()) + ".json")
        QuickLayout.save_file(f"{temp_file}")

        with open(f"{temp_file}") as json_file:
            data = json.load(json_file)

        os.remove(f"{temp_file}")

        self.assertEqual(len(data[0]["children"]), 2)
        self.assertIn(data[0]["children"][0]["position"], ["LEFT", "RIGHT"])
        self.assertIn(data[0]["children"][1]["position"], ["LEFT", "RIGHT"])

    async def test_restore(self):
        data = [
            {
                "children": [
                    {
                        "children": [
                            {
                                "dock_id": 1,
                                "height": 100,
                                "selected_in_dock": True,
                                "title": "LeftDocked",
                                "visible": True,
                                "width": 100,
                            }
                        ],
                        "dock_id": 1,
                        "position": "LEFT",
                    },
                    {
                        "children": [
                            {
                                "dock_id": 2,
                                "height": 100,
                                "selected_in_dock": False,
                                "title": "RightDocked",
                                "visible": True,
                                "width": 100,
                            }
                        ],
                        "dock_id": 2,
                        "position": "RIGHT",
                    },
                ],
                "dock_id": 0,
            }
        ]

        await self.create_test_area()

        window_left = ui.Window("LeftDocked")
        with window_left.frame:
            ui.Rectangle(style={"background_color": 0xFFF07E4D})

        window_right = ui.Window("RightDocked")
        with window_right.frame:
            ui.Rectangle(style={"background_color": 0xFF7DF0A6})

        await omni.kit.app.get_app().next_update_async()

        temp_file = Path(tempfile.gettempdir()).joinpath("workspace_" + next(tempfile._get_candidate_names()) + ".json")

        # Save data to json file and open it in QuickLayout
        with open(f"{temp_file}", "w") as json_file:
            json.dump(data, json_file, sort_keys=True, indent=2)
        QuickLayout.load_file(f"{temp_file}")

        await omni.kit.app.get_app().next_update_async()

        # for code coverage. Real QuickLayout.compare_file test is in omni.kit.test_suite.layout as it needs windows
        QuickLayout.compare_file(f"{temp_file}")

        # We don't test tab bar
        window_left.dock_tab_bar_visible = False
        window_right.dock_tab_bar_visible = False

        os.remove(f"{temp_file}")

        await self.finalize_test(golden_img_dir=self._golden_img_dir)
