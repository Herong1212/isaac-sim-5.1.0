## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestActionsAndHotkeys']

import random
import omni.kit.actions.core
import omni.appwindow
import omni.usd
import carb
import omni.ui as ui
from omni.kit.test import AsyncTestCase
from omni.kit.test_suite.helpers import arrange_windows
from ..actions import is_ui_hidden

class TestActionsAndHotkeys(AsyncTestCase):
    async def setUp(self):
        self.extension_id = "omni.kit.ui.actions"
        await arrange_windows()
        await self.wait_n_updates(10)

    async def wait_n_updates(self, n_frames: int = 3):
        app = omni.kit.app.get_app()
        for _ in range(n_frames):
            await app.next_update_async()

    async def test_ui_toggling(self):
        """Test that ui toggles visibility and fullscreen correctly"""
        await omni.usd.get_context().new_stage_async()
        action_registry = omni.kit.actions.core.get_action_registry()

        self.assertTrue(is_ui_hidden())

        action = action_registry.get_action(self.extension_id, "toggle_ui")
        self.assertIsNotNone(action)

        result = action.execute()
        # Make sure it was hidden when toggled
        self.assertFalse(is_ui_hidden())

        result = action.execute()
        # Make sure it is unhidden again after toggling again
        self.assertTrue(is_ui_hidden())

        action = action_registry.get_action(self.extension_id, "toggle_fullscreen")
        self.assertIsNotNone(action)

        await self.wait_n_updates(10)
        # Make sure we're not fullscreen already
        self.assertFalse(omni.appwindow.get_default_app_window().is_fullscreen())
        result = action.execute()
        await self.wait_n_updates(10)
        # Make sure we are in fullscreen now
        self.assertTrue(omni.appwindow.get_default_app_window().is_fullscreen())
        result = action.execute()
        await self.wait_n_updates(10)
        # Make sure we are back out of fullscreen
        self.assertFalse(omni.appwindow.get_default_app_window().is_fullscreen())

    async def test_ui_toggling_interactions(self):
        """Test that ui toggles visibility and fullscreen correctly & windows don't get messed up"""
        await omni.usd.get_context().new_stage_async()
        action_registry = omni.kit.actions.core.get_action_registry()

        if is_ui_hidden():
            action_registry.get_action(self.extension_id, "toggle_ui").execute()
            await self.wait_n_updates(10)

        self.assertFalse(is_ui_hidden())
        self.assertFalse(omni.appwindow.get_default_app_window().is_fullscreen())

        workspace_dump = ui.Workspace.dump_workspace()

        # randomly toggle UI & fullscreen to test toggle_ui and toggle_fullscreen and verify windows are not messed up
        for i in range(1, 100):
            val = random.randint(0, 300)

            if val > 200:
                action = action_registry.get_action(self.extension_id, "toggle_fullscreen")
            elif val > 50:
                action = action_registry.get_action(self.extension_id, "toggle_ui")
            else:
                action = action_registry.get_action(self.extension_id, "cancel_fullscreen_ui")

            action.execute()
            print(f"iteration {i} \"{action.description}\"")
            await self.wait_n_updates(10)

        # make sure fullscreen is canceled
        if omni.appwindow.get_default_app_window().is_fullscreen():
            action_registry.get_action(self.extension_id, "toggle_fullscreen").execute()
            await self.wait_n_updates(10)

        # make sure ui is shown
        if is_ui_hidden():
            action_registry.get_action(self.extension_id, "toggle_ui").execute()
            await self.wait_n_updates(10)

        # everything should be back to normal. Check windows still look good
        result = ui.Workspace.compare_workspace(workspace_dump)
        self.assertEqual(result, [])
