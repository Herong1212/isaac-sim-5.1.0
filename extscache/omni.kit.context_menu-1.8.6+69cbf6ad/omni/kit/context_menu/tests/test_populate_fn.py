## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import pathlib
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from pxr import Kind, Sdf, Gf
from omni.kit.test_suite.helpers import get_test_data_path, select_prims,  get_prims, wait_stage_loading, arrange_windows
from omni.kit.context_menu import ContextMenuExtension


class TestContextMenuPopulateFn(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_populate_context_menu(self):
        menu = {"name": "Entry 0"}
        entry0 = omni.kit.context_menu.add_menu(menu, "TEST", "NO_SEP_TEST")

        # add separator
        menu = {"name": ""}
        sep = omni.kit.context_menu.add_menu(menu, "TEST", "NO_SEP_TEST")

        menu = {
	        "name": "Entry 1",
	         "populate_fn": lambda *_: ContextMenuExtension.uiMenuItem("Entry 1")
        }
        entry1 = omni.kit.context_menu.add_menu(menu, "TEST", "NO_SEP_TEST")

        menu_list = omni.kit.context_menu.get_menu_dict("TEST", "NO_SEP_TEST")
        omni.kit.context_menu.get_instance().show_context_menu("TEST", {}, menu_list)
        await ui_test.human_delay()

        menu_dict = await ui_test.get_context_menu(get_all=True)
        self.assertEqual(menu_dict["_"], ['Entry 0', '', 'Entry 1'])
