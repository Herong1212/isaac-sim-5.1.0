## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestActionsAndHotkeys']

import omni.kit.actions.core
from omni.kit.test import AsyncTestCase
from ..actions import set_camera


class TestActionsAndHotkeys(AsyncTestCase):
    async def setUp(self):
        self.extension_id = "omni.kit.viewport.actions"

    async def wait_n_updates(self, n_frames: int = 3):
        app = omni.kit.app.get_app()
        for _ in range(n_frames):
            await app.next_update_async()

    async def test_find_registered_action(self):
        action_registry = omni.kit.actions.core.get_action_registry()

        action = action_registry.get_action(self.extension_id, "perspective_camera")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "top_camera")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "front_camera")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "right_camera")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_rtx_rendermode")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "set_viewport_resolution")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_camera_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_light_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_grid_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_axis_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_selection_hilight_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_bounding_box_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_global_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_viewport_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_hud_fps_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_hud_resolution_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_hud_progress_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_hud_camera_speed_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_hud_memory_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_hud_visibility")
        self.assertIsNotNone(action)

        action = action_registry.get_action(self.extension_id, "toggle_wireframe")
        self.assertIsNotNone(action)

    async def test_action_return_values(self):
        """Test the return valus for actions match expected cases."""
        await omni.usd.get_context().new_stage_async()
        action_registry = omni.kit.actions.core.get_action_registry()

        test_keys = ["scene/lights", "guide/grid", "guide/axis"]
        try:
            action = action_registry.get_action(self.extension_id, "toggle_camera_visibility")
            self.assertIsNotNone(action)
            # First toggle, should return key as camera's are visible by default
            result = action.execute()
            self.assertEqual(result, "scene/cameras")

            # Re-run making invisible again, should do nothing as nothing was toggled
            result = action.execute(visible=False)
            self.assertEqual(result, None)

            # Re-run making visible again, should return the type that was toggled
            result = action.execute(visible=True)
            self.assertEqual(result, "scene/cameras")

            action = action_registry.get_action(self.extension_id, "toggle_viewport_visibility")
            self.assertIsNotNone(action)

            result = action.execute(keys=test_keys)
            self.assertEqual(result, test_keys)

            # Re-run making invisible again, should do nothing as nothing was toggled
            result = action.execute(keys=test_keys, visible=False)
            self.assertEqual(result, [])

            # Re-run making visible again, should return the type that was toggled
            sub_keys = [test_keys[0], test_keys[2]]
            result = action.execute(keys=sub_keys, visible=True)
            self.assertEqual(result, sub_keys)

            # Test API to pass sequence of visibility bools (should return nothing as [0] and [2] are vis, and [1] is invis)
            result = action.execute(keys=test_keys, visible=[True, False, True])
            self.assertEqual(result, [])

            # Test API to pass sequence of visibility bools (should return type of [1] as it is toggling to visible
            result = action.execute(keys=test_keys, visible=[True, True, True])
            self.assertEqual(result, [test_keys[1]])

            action = action_registry.get_action(self.extension_id, "toggle_wireframe")
            self.assertIsNotNone(action)
            # First toggle, should change from "default" to "wireframe"
            result = action.execute()
            self.assertEqual(result, "wireframe")

            # Re-run, should change fron "wireframe" to "default"
            result = action.execute()
            self.assertEqual(result, "default")

            action = action_registry.get_action(self.extension_id, "top_camera")
            self.assertIsNotNone(action)

            result = action.execute()
            self.assertTrue(result)

            action = action_registry.get_action(self.extension_id, "front_camera")
            self.assertIsNotNone(action)

            result = action.execute()
            self.assertTrue(result)

            result = set_camera("/randomCamera")  # Test for a camera that doesn't exist
            self.assertFalse(result)

        finally:
            # Return everything to known startup state
            action_registry.get_action(self.extension_id, "toggle_camera_visibility").execute(visible=True)
            action_registry.get_action(self.extension_id, "toggle_viewport_visibility").execute(keys=test_keys, visible=True)
            action_registry.get_action(self.extension_id, "perspective_camera").execute()

    async def test_toggle_show_by_type_visibility(self):
        """Test that the toggle_show_by_type_visibility action works as expected"""
        import carb.settings
        settings = carb.settings.get_settings()
        original_display_exclusion = settings.get("/exts/omni.kit.viewport.menubar.display/showByType/exclude_list")

        await omni.usd.get_context().new_stage_async()
        action_registry = omni.kit.actions.core.get_action_registry()

        try:
            action = action_registry.get_action(self.extension_id, "toggle_show_by_type_visibility")
            self.assertIsNotNone(action)

            # Test with exlusion types
            settings.set("/exts/omni.kit.viewport.menubar.display/showByType/exclude_list", ["Skeletons"])
            result = action.execute(visible=None)
            self.assertEqual(result, ["scene/cameras", "scene/lights", "scene/audio"])

            # Toggle all back to default state
            result = action.execute(visible=None)
            self.assertEqual(result, ["scene/cameras", "scene/lights", "scene/audio"])

            # Toggle one type
            action = action_registry.get_action(self.extension_id, "toggle_camera_visibility")
            self.assertIsNotNone(action)
            result = action.execute()
            self.assertEqual(result, "scene/cameras")

            # Toggle all should only change the camera back to visible
            result = action.execute(visible=None)
            self.assertEqual(result, "scene/cameras")

        finally:
            settings.set("/exts/omni.kit.viewport.menubar.display/showByType/exclude_list", original_display_exclusion)

    async def test_hud_action_overrides_parent_visibility(self):
        """Test that toggling any HUD item to visible will force the parent to visible"""
        from omni.kit.viewport.utility import get_active_viewport_window
        import carb.settings

        try:
            vp_window = get_active_viewport_window()
            self.assertIsNotNone(vp_window)
            self.assertIsNotNone(vp_window.viewport_api)

            settings = carb.settings.get_settings()
            hud_vis_path = f"/persistent/app/viewport/{vp_window.viewport_api.id}/hud/visible"
            settings.set(hud_vis_path, False)
            await self.wait_n_updates()
            self.assertFalse(settings.get(hud_vis_path))

            action_registry = omni.kit.actions.core.get_action_registry()
            action = action_registry.get_action(self.extension_id, "toggle_hud_visibility")
            self.assertIsNotNone(action)

            action.execute(visible=True, use_setting=True)

            # Should have forced the parent item back to True
            await self.wait_n_updates()
            self.assertTrue(settings.get(hud_vis_path))

        finally:
            pass