# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest
from pxr import UsdShade


class TestBundleWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        await arrange_windows()

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

    # Test(s)
    async def test_bundle_ui(self):
        usd_context = omni.usd.get_context()

        test_file_path = self._usd_path.joinpath("bundle.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()
        stage = usd_context.get_stage()

        for prim_path in [
            "/World/Cube",
            "/World/Cone",
            "/World/OmniSound",
            "/World/Camera",
            "/World/DomeLight",
            "/World/Scope",
            "/World/Xform",
            "/World/Looks/PreviewSurface",
            "/World/Looks/PreviewSurface/Shader",
            "/World/nvidia_boy/SkelRoot/Skeleton",
            "/World/nvidia_boy/SkelRoot",
            "/World/AmbientSound",
        ]:
            await self.docked_test_window(
                window=self._w._window,
                width=450,
                height=995,
                restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
                restore_position=ui.DockPosition.BOTTOM,
            )

            # Select the prim.
            usd_context.get_selection().set_selected_prim_paths([prim_path], True)
            await ui_test.human_delay(50)
            prim = stage.GetPrimAtPath(prim_path)
            prim_type = prim.GetTypeName().lower()

            if prim.IsA(UsdShade.Material):
                for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
                    w.widget.collapsed = True

                    if (w.widget.title in ["Material and Shader", "Shader"]) or ("Surface" in w.widget.title):
                        w.widget.collapsed = False

            # Need to wait for an additional frames for omni.ui rebuild to take effect
            await ui_test.human_delay(10)

            await self.finalize_test(
                golden_img_dir=self._golden_img_dir, golden_img_name=f"test_bundle_ui_{prim_type}.png", zero_mouse=True
            )

            # allow window to be restored to full size
            await ui_test.human_delay(50)

        # select nothing for code coverage
        usd_context.get_selection().set_selected_prim_paths([], True)
        await ui_test.human_delay(10)
