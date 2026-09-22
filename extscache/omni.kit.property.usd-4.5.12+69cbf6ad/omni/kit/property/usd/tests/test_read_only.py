## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, protected-access
from pathlib import Path

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, get_test_data_path
from omni.ui.tests.test_base import OmniUiTest


class TestReadOnly(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        await arrange_windows()

        self._golden_img_dir = get_test_data_path(__name__, "golden_img")

        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Materials on selected models", True)

        import omni.kit.window.property as p

        self._w = p.get_window()

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    async def test_read_only(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=600,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        await usd_context.open_stage_async(get_test_data_path(__name__, "usd/read_only.usda"))
        await omni.kit.app.get_app().next_update_async()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Sphere"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=Path(self._golden_img_dir), golden_img_name="test_read_only.png", zero_mouse=True
        )
