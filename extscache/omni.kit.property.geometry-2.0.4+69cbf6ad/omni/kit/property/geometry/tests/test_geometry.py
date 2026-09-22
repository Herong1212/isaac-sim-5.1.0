## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest
from pxr import UsdGeom


class TestGeometryWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests/golden_img"
        )
        self._usd_path = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests"
        )

        import omni.kit.window.property as p

        self._w = p.get_window()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_geometry_ui(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=700,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("geometry_test.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await omni.kit.app.get_app().next_update_async()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_geometry_ui.png", zero_mouse=True
        )

    async def test_geometry_mixed_ui(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=700,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("geometry_test.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await omni.kit.app.get_app().next_update_async()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube", "/World/Looks"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_geometry_mixed_ui.png", zero_mouse=True
        )

    async def test_custom_visual_attribute_ui(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=800,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("geometry_test.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await omni.kit.app.get_app().next_update_async()

        def is_cube(prim):
            return prim.IsA(UsdGeom.Cube)

        omni.kit.property.geometry.register_custom_visual_attribute("foo", "Foo", "bool", False, is_cube)
        omni.kit.property.geometry.register_custom_visual_attribute("bar", "Bar", "int", 1234, is_cube)

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_geometry_ui_custom.png", zero_mouse=True
        )

        # Clean up
        omni.kit.property.geometry.deregister_custom_visual_attribute("foo")
        omni.kit.property.geometry.deregister_custom_visual_attribute("bar")

        await ui_test.human_delay(10)
        await omni.kit.app.get_app().next_update_async()
