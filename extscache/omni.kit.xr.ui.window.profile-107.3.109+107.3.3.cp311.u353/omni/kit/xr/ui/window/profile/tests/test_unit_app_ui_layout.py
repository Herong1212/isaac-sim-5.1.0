# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import pathlib
import platform

import carb
import omni.kit.app as app
import omni.kit.xr.core.test_utils as test_utils
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest


class TestWindowLayout(OmniUiTest):

    _golden_img_dir = (
        pathlib.Path(app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
        / "data"
        / "tests"
        / "golden_img"
    ).absolute()

    _xcr_runtime_json_path = test_utils.tests_directories.get_xcr_runtime_json()
    _openxr_active_runtime_json_setting_name = "/persistent/xr/system/openxr/activeRuntimeJSON"
    _openxr_runtime_setting_name = "/persistent/xr/system/openxr/runtime"

    async def _test_unit_app_ui_layout(self, window_title, test_image, profile_name):
        await omni.kit.app.get_app().next_update_async()
        window = omni.ui.Workspace.get_window(window_title)
        window.frame.rebuild()
        await self.docked_test_window(
            window=window,
            width=480,
            height=480,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )
        await ui_test.human_delay(50)
        await self.finalize_test(
            use_log=True,
            golden_img_dir=self._golden_img_dir,
            golden_img_name=test_image,
        )

    async def test_ui_layout_vr(self):
        carb.settings.get_settings().set(
            self._openxr_active_runtime_json_setting_name,
            self._xcr_runtime_json_path,
        )
        carb.settings.get_settings().set(self._openxr_runtime_setting_name, "custom")
        await self._test_unit_app_ui_layout("VR", "test_ui_layout_vr.png", "vr")

    async def test_ui_layout_with_oxr_error_vr(self):
        carb.settings.get_settings().set(self._openxr_runtime_setting_name, "custom")
        carb.settings.get_settings().set(self._openxr_active_runtime_json_setting_name, "WRONG_JSON_PATH")
        await self._test_unit_app_ui_layout("VR", "test_ui_layout_with_oxr_error_vr.png", "vr")

    async def test_ui_layout_ar(self):
        carb.settings.get_settings().set(
            self._openxr_active_runtime_json_setting_name,
            self._xcr_runtime_json_path,
        )
        carb.settings.get_settings().set(self._openxr_runtime_setting_name, "custom")
        await self._test_unit_app_ui_layout("AR", "test_ui_layout_ar.png", "ar")

    async def test_ui_layout_with_oxr_error_ar(self):
        carb.settings.get_settings().set(self._openxr_runtime_setting_name, "custom")
        carb.settings.get_settings().set(self._openxr_active_runtime_json_setting_name, "WRONG_JSON_PATH")
        await self._test_unit_app_ui_layout("AR", "test_ui_layout_with_oxr_error_ar.png", "ar")

    async def test_ui_layout_tabletar(self):
        await self._test_unit_app_ui_layout("Tablet AR", "test_ui_layout_tabletar.png", "tabletar")
