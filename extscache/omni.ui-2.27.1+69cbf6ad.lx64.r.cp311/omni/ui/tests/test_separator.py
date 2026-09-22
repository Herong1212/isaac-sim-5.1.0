## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
import omni.kit.app
import omni.ui as ui
from functools import partial


class TestSeparator(OmniUiTest):
    """Testing ui.Menu"""

    async def test_general(self):
        """Testing general properties of ui.Menu"""

        window = await self.create_test_window()

        with window.frame:
            ui.Spacer()

        shown = [False, False]

        def on_shown(index, s):
            shown[index] = s

        self.menu_h = ui.Menu("Test Hidden Context Menu", shown_changed_fn=partial(on_shown, 0))
        self.menu_v = ui.Menu("Test Visible Context Menu", shown_changed_fn=partial(on_shown, 1))

        with self.menu_h:
            ui.Separator()
            ui.MenuItem("Hidden 1")
            ui.Separator("Hidden 1")
            ui.MenuItem("Hidden 2")
            ui.Separator("Hidden 2")
            ui.MenuItem("Hidden 3")
            ui.Separator()

        with self.menu_v:
            ui.Separator()
            ui.MenuItem("Test 1")
            ui.Separator("Separator 1")
            ui.MenuItem("Test 2")
            ui.Separator("Separator 2")
            ui.MenuItem("Test 3")
            ui.Separator()

        # No menu is shown
        self.assertIsNone(ui.Menu.get_current())

        self.menu_h.show_at(0, 0)
        self.menu_v.show_at(0, 0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Check the callback is called
        self.assertFalse(shown[0])
        self.assertTrue(shown[1])
        # Check the property
        self.assertFalse(self.menu_h.shown)
        self.assertTrue(self.menu_v.shown)
        # Check the current menu
        self.assertEqual(ui.Menu.get_current(), self.menu_v)

        await self.finalize_test()

    async def test_general_modern(self):
        """Testing general properties of ui.Menu"""

        window = await self.create_test_window()

        with window.frame:
            ui.Spacer()

        self.menu_v = ui.Menu("Test Visible Context Menu Modern", menu_compatibility=0)

        with self.menu_v:
            ui.Separator()
            ui.MenuItem("Test 1")
            ui.Separator("Separator 1")
            ui.MenuItem("Test 2")
            ui.Separator("Separator 2")
            ui.MenuItem("Test 3")
            ui.Separator()

        self.menu_v.show_at(0, 0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

        self.menu_v.destroy()
        self.menu_v = None
