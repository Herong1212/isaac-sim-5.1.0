## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import pathlib

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import get_test_data_path, wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest


class TestLightWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

        usd_path = pathlib.Path(get_test_data_path(__name__))
        self._golden_img_dir = usd_path.absolute().joinpath("golden_img").absolute()
        self._usd_path = usd_path.absolute()

        import omni.kit.window.property as p

        self._w = p.get_window()

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        await wait_stage_loading()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    # Test(s)
    async def test_light_ui(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=650,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("light_test.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # NOTE: cannot do DomeLight as it contains a file path which is build specific
        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/DistantLight"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_light_ui.png", zero_mouse=True
        )
