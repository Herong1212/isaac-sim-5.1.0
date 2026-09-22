# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pathlib import Path
from typing import Any

import carb
import carb.input
import carb.settings
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.ui as ui
import omni.usd
from omni.anim.navigation.core import NavMeshSettings
from omni.ui.tests.test_base import OmniUiTest
import NavSchema

from ..scripts.navmesh_menu import NavMeshMenu

EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))


class TestNavMeshWindow(OmniUiTest):
    async def setUp(self):
        self._settings = carb.settings.get_settings()
        self._usd_context = omni.usd.get_context()
        self._usd_scene_dir = (
            EXTENSION_FOLDER_PATH.absolute().resolve().joinpath("data").joinpath("tests").joinpath("usd")
        )

    async def test_navmesh_window(self):
        usd_path = self._usd_scene_dir.joinpath("TestNavMesh.usda")
        success, error = await self._usd_context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)
        print("----------------------------------------------------------")
        print(f'USD TEST SCENE PATH {str(usd_path)}')
        print("----------------------------------------------------------")
        self._stage = self._usd_context.get_stage()
        menu_widget = ui_test.get_menubar()
        # create navmesh volume
        await self._create_navmesh_volume_from_menu(menu_widget)
        # # edit(open) the NavMesh window from property window
        await self._edit_navmesh(self._stage, self._usd_context)
        # # interactions on the navmesh window
        await self._interact_with_sections_toolbar()
        await self._interact_with_baking()
        await self._interact_with_geometry_section(self._stage, self._usd_context)
        await self._interact_with_areas_section()
        await self._interact_with_bake_settings_section()
        await self._interact_with_preferences()

        # close the stage
        success, error = await self._usd_context.close_stage_async()
        self.assertTrue(success, error)

    async def test_obstacle_api(self):
        # todo
        pass

    async def _select_prims(self, paths, usd_context, val):
        usd_context.get_selection().set_selected_prim_paths(paths, val)
        await ui_test.human_delay()

    async def _change_setting_value(self, setting_identifier: str, input_value: Any, setting_path: str):
        widget = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**.identifier=='{setting_identifier}'")
        status = "Failed." if widget is None else "OK."
        print(f"Finding identifier {setting_identifier}: {status}")
        await widget.input(str(input_value))
        self.assertEqual(self._settings.get(setting_path), input_value)

    async def _change_setting_value_checkbox(self, setting_identifier: str, input_value: Any, setting_path: str):
        widget = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**.identifier=='{setting_identifier}'")
        status = "Failed." if widget is None else "OK."
        print(f"Finding identifier {setting_identifier}: {status}")
        await widget.click()
        if self._settings.get(setting_path) != input_value:
            await widget.click()
        self.assertEqual(self._settings.get(setting_path), input_value)

    async def _edit_navmesh(self, stage, usd_context):
        ui.Workspace.show_window("Property", True)
        # property window to front
        await ui_test.find("Property").focus()
        # select NavMeshVolume prim
        to_select = "/World/NavMeshVolume"
        await self._select_prims([to_select], usd_context, True)
        await ui_test.human_delay(10)
        # click the `Edit NavMesh` from the Property window
        button = ui_test.find("Property//Frame/**/Button[*].identifier=='edit_navmesh'")
        await button.click()
        await ui_test.human_delay(10)
        # test the window is open
        navmesh_window = ui.Workspace.get_window(NavMeshMenu.WINDOW_NAME)
        await self.docked_test_window(navmesh_window, width=512, height=512, block_devices=False)

    async def _create_navmesh_volume_from_menu(self, menu_widget):
        await menu_widget.find_menu("Create").click()
        await ui_test.human_delay(20)
        await menu_widget.find_menu("Navigation").click()
        await ui_test.human_delay(20)
        await menu_widget.find_menu("NavMesh Include Volume").click()
        await ui_test.human_delay(20)

    async def _interact_with_sections_toolbar(self):
        # click `Geometry`
        geometry_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='geometry'")
        await geometry_button.click()
        await ui_test.human_delay()
        # click `Areas`
        areas_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='areas'")
        await areas_button.click()
        await ui_test.human_delay()
        # click `Bake Settings`
        bake_settings_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='bake_settings'")
        await bake_settings_button.click()
        await ui_test.human_delay()

    async def _interact_with_baking(self):
        # autobake_checkbox = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**.identifier=='auto_bake'")
        # autobake_checkbox.click()
        # await ui_test.human_delay()
        # auto_bake = self._settings.get_as_bool(NavMeshSettings.AUTO_REBAKE_SETTING_PATH)
        # self.assertFalse(auto_bake)
        bake_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='start_baking'")
        await bake_button.click()
        await ui_test.human_delay()
        cancel_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='cancel_baking'")
        await cancel_button.click()
        await ui_test.human_delay()
        # autobake_checkbox.click()
        # await ui_test.human_delay()
        # self.assertTrue(auto_bake)
        # autobake_delay_input = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**.identifier=='auto_bake_delay'")
        # autobake_delay_input.input("2")
        # await ui_test.human_delay()
        # auto_bake_delay = self._settings.get_as_int(NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH)
        # self.assertEqual(auto_bake_delay, 2)
        # autobake_delay_input.input("1")
        # await ui_test.human_delay()
        # auto_bake_delay = self._settings.get_as_int(NavMeshSettings.AUTO_REBAKE_DELAY_SETTING_PATH)
        # self.assertEqual(auto_bake_delay, 1)

    async def _interact_with_geometry_section(self, stage, usd_context):
        geometry_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='geometry'")
        await geometry_button.click()
        await ui_test.human_delay()

        # include/exclude through navmesh window
        # exclude 2 meshes
        meshes_to_exclude = ["/World/Cone", "/World/Cube"]
        await self._select_prims(meshes_to_exclude, usd_context, True)
        await ui_test.human_delay()

        exclude_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='exclude_stage_selection'")
        await exclude_button.click()
        await ui_test.human_delay()

        # check the NavMeshExcludeAPI is applied to the prims
        for path in meshes_to_exclude:
            self.assertTrue(stage.GetPrimAtPath(path).HasAPI(NavSchema.NavMeshExcludeAPI))

        # include 2 meshes back
        meshes_to_include = ["/World/Cone", "/World/Cube_04"]
        await self._select_prims(meshes_to_include, usd_context, True)
        await ui_test.human_delay()

        include_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='include_stage_selection'")
        await include_button.click()
        await ui_test.human_delay()

        # check the NavMeshExcludeAPI is removed from the prims
        for path in meshes_to_include:
            self.assertFalse(stage.GetPrimAtPath(path).HasAPI(NavSchema.NavMeshExcludeAPI))
        # Cube should still have the schema
        self.assertTrue(stage.GetPrimAtPath("/World/Cube").HasAPI(NavSchema.NavMeshExcludeAPI))

    async def _interact_with_areas_section(self):
        # todo
        pass

    async def _interact_with_bake_settings_section(self):
        bake_settings_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='bake_settings'")
        await bake_settings_button.click()
        await ui_test.human_delay()
        await self._change_setting_value("setting_NavMeshBakeSettings_Agent_Min_Height", 50.0, NavMeshSettings.AGENT_MIN_HEIGHT_SETTING_PATH)
        await self._change_setting_value("setting_NavMeshBakeSettings_Agent_Max_Radius", 100.0, NavMeshSettings.AGENT_MAX_RADIUS_SETTING_PATH)

    async def _interact_with_preferences(self):
        preferences_button = ui_test.find(f"{NavMeshMenu.WINDOW_NAME}//Frame/**/Button[*].identifier=='preferences'")
        await preferences_button.click()
        await ui_test.human_delay()
