# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb
import omni.kit.app
import omni.kit.test
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, wait_stage_loading


class TestEnableCreateMenu(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await omni.usd.get_context().new_stage_async()
        await wait_stage_loading()

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

        def verify_menu(mesh: bool, shape: bool, light: bool, audio: bool, camera: bool, scope: bool, xform: bool):
            menu_widget = ui_test.get_menubar()
            menu_widgets = []
            for w in menu_widget.find_all("**/"):
                if isinstance(w.widget, (ui.Menu, ui.MenuItem)) and w.widget.text.strip() != "placeholder":
                    menu_widgets.append(w.widget.text)

            self.assertEqual("Mesh" in menu_widgets, mesh)
            self.assertEqual("Shape" in menu_widgets, shape)
            self.assertEqual("Light" in menu_widgets, light)
            self.assertEqual("Audio" in menu_widgets, audio)
            self.assertEqual("Camera" in menu_widgets, camera)
            self.assertEqual("Scope" in menu_widgets, scope)
            self.assertEqual("Xform" in menu_widgets, xform)

        async def test_menu(mesh: bool, shape: bool, light: bool, audio: bool, camera: bool, scope: bool, xform: bool):
            omni.kit.menu.create.rebuild_menus()
            verify_menu(mesh, shape, light, audio, camera, scope, xform)

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
