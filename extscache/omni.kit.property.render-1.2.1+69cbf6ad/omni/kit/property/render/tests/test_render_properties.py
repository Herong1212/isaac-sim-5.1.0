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
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest


class TestRenderPropertiesWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        import omni.kit.window.property as p

        self._w = p.get_window()

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        test_data_path = pathlib.Path(extension_path).joinpath("data").joinpath("tests")

        self.__golden_img_dir = test_data_path.absolute().joinpath("golden_img").absolute()
        self.__usd_path = str(test_data_path.joinpath("render_prim_test.usda").absolute())

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def __test_render_prim_ui(self, prim_name):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=650,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        await usd_context.open_stage_async(self.__usd_path)
        await wait_stage_loading()

        # NOTE: cannot do DomeLight as it contains a file path which is build specific
        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths([f"/World/RenderTest/{prim_name}"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(golden_img_dir=self.__golden_img_dir, golden_img_name=f"test_{prim_name}_ui.png")

    # Test(s)
    async def test_rendersettings_ui(self):
        await self.__test_render_prim_ui("rendersettings1")

    async def test_renderproduct_ui(self):
        await self.__test_render_prim_ui("renderproduct1")

    async def test_rendervar_ui(self):
        await self.__test_render_prim_ui("rendervar1")
