## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import omni.kit.app
import omni.kit.test
import omni.usd
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_stage_loading, arrange_windows


class TestEnableCreateMenu(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows()
        await omni.usd.get_context().new_stage_async()
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_enable_create_menu(self):
        settings = carb.settings.get_settings()
        def reset_prim_creation():
            settings.set("/app/primCreation/hideShapes", False)
            settings.set("/app/primCreation/enableMenuShape", True)
            settings.set("/app/primCreation/enableMenuLight", True)
            settings.set("/app/primCreation/enableMenuAudio", True)
            settings.set("/app/primCreation/enableMenuCamera", True)
            settings.set("/app/primCreation/enableMenuScope", True)
            settings.set("/app/primCreation/enableMenuXform", True)

        def verify_menu(menu_dict: dict, mesh:bool, shape:bool, light:bool, audio:bool, camera:bool, scope:bool, xform:bool):
            self.assertEqual("Mesh" in menu_dict, mesh)
            self.assertEqual("Shape" in menu_dict, shape)
            self.assertEqual("Light" in menu_dict, light)
            self.assertEqual("Audio" in menu_dict, audio)
            self.assertEqual("Camera" in menu_dict["_"], camera)
            self.assertEqual("Scope" in menu_dict["_"], scope)
            self.assertEqual("Xform" in menu_dict["_"], xform)

        async def test_menu(mesh:bool, shape:bool, light:bool, audio:bool, camera:bool, scope:bool, xform:bool):
            # right click on viewport
            await ui_test.find("Viewport").right_click()
            await ui_test.human_delay(10)

            #get context menu as dict
            menu_dict = await ui_test.get_context_menu()
            omni.kit.context_menu.close_menu()

            # verify
            verify_menu(menu_dict['Create'], mesh, shape, light, audio, camera, scope, xform)
            await ui_test.human_delay(10)

        try:
            # verify default
            reset_prim_creation()
            await test_menu(mesh=True, shape=True, light=True, audio=True, camera=True, scope=True, xform=True)

            # verify hide shapes
            reset_prim_creation()
            settings.set("/app/primCreation/hideShapes", True)
            await test_menu(mesh=True, shape=False, light=True, audio=True, camera=True, scope=True, xform=True)

            reset_prim_creation()
            settings.set("/app/primCreation/enableMenuShape", False)
            await test_menu(mesh=True, shape=False, light=True, audio=True, camera=True, scope=True, xform=True)

            # verify hide light
            reset_prim_creation()
            settings.set("/app/primCreation/enableMenuLight", False)
            await test_menu(mesh=True, shape=True, light=False, audio=True, camera=True, scope=True, xform=True)

            # verify hide audio
            reset_prim_creation()
            settings.set("/app/primCreation/enableMenuAudio", False)
            await test_menu(mesh=True, shape=True, light=True, audio=False, camera=True, scope=True, xform=True)

            # verify hide camera
            reset_prim_creation()
            settings.set("/app/primCreation/enableMenuCamera", False)
            await test_menu(mesh=True, shape=True, light=True, audio=True, camera=False, scope=True, xform=True)

            # verify hide scope
            reset_prim_creation()
            settings.set("/app/primCreation/enableMenuScope", False)
            await test_menu(mesh=True, shape=True, light=True, audio=True, camera=True, scope=False, xform=True)

            # verify hide xform
            reset_prim_creation()
            settings.set("/app/primCreation/enableMenuXform", False)
            await test_menu(mesh=True, shape=True, light=True, audio=True, camera=True, scope=True, xform=False)
        finally:
            reset_prim_creation()
