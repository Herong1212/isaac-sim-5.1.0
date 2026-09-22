## Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path

import omni.kit.window.property
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, get_test_data_path, open_stage, select_prims
from omni.kit.ui_test.query import WindowRef
from omni.ui.tests.test_base import OmniUiTest


class TestLayerDeletionUI(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows()

        self._golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        # hide content window
        content_window = ui.Workspace.get_window("Content")
        if content_window:
            content_window.visible = False
            await ui_test.human_delay()

        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Layer Path", True)

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

        # show content window
        content_window = ui.Workspace.get_window("Content")
        if content_window and content_window.visible is not None:
            content_window.visible = True
            await ui_test.human_delay()

    async def test_layer_deletion(self):
        await open_stage(get_test_data_path(__name__, "layer_cube.usda"))

        await select_prims(["/World/Cone", "/World/Cube"])
        await ui_test.human_delay()

        await ui_test.find("Layer//Frame/**/Label[*].text=='layer_cone.usda'").right_click()
        await ui_test.human_delay()
        await ui_test.select_context_menu("Remove Layer")
        await ui_test.human_delay()

        # can't use ui_test.find as window title has glyph
        for win in ui.Workspace.get_windows():
            if "Removing Layer" in win.title:
                widget = WindowRef(win, "Removing Layer")
                await widget.find("**/Button[*].identifier=='confirm_button'").click()

        # after remove layer only "/World/Cube" should be in property window as "/World/Cone" was deleted with the layer
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="post_layer_delete_1.png")
        await ui_test.human_delay(50)

        # select empty layer
        await ui_test.find("Layer//Frame/**/Label[*].text=='layer_empty.usda'").click()
        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="post_layer_delete_2.png")

        # delete empty later
        await ui_test.find("Layer//Frame/**/Label[*].text=='layer_empty.usda'").right_click()
        await ui_test.human_delay()
        await ui_test.select_context_menu("Remove Layer")
        await ui_test.human_delay(10)

        # window should of refreshed and be showing root layer
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="post_layer_delete_3.png")
        await ui_test.human_delay(10)
