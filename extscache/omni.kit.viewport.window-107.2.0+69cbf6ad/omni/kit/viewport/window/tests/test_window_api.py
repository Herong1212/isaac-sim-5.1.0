## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["TestWindowAPI"]

from pathlib import Path

import carb
import omni.kit.test
import omni.usd
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest

from omni.kit.viewport.window import ViewportWindow, get_viewport_window_instances

CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.viewport.window}/data"))

TEST_WIDTH, TEST_HEIGHT = 360, 240
NUM_DEFAULT_WINDOWS = 0


class TestWindowAPI(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")

        self.assertNoViewportWindows()

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    def assertNoViewportWindows(self):
        self.assertEqual(NUM_DEFAULT_WINDOWS, sum(1 for x in get_viewport_window_instances()))

    async def test_new_window(self):
        """Test basic creartion of a ViewportWindow"""

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
        self.assertIsNotNone(vp_window)
        self.assertEqual('', vp_window.viewport_api.usd_context_name)
        self.assertEqual(1 + NUM_DEFAULT_WINDOWS, sum(1 for x in get_viewport_window_instances()))

        await self.wait_n_updates(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

        # Test no Window are reachable after destruction
        vp_window.destroy()
        del vp_window
        self.assertNoViewportWindows()

    async def _test_post_message(self, vp_callback, golden_img_name: str):
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        settings = carb.settings.get_settings()
        try:
            # These 0 avoid a fade-in fade-out animation, but also test that zero is valid (no divide by zero)
            settings.set('/app/viewport/toastMessage/fadeIn', 0)
            settings.set('/app/viewport/toastMessage/fadeOut', 0)
            # Keep the message for a short amount of time
            settings.set('/app/viewport/toastMessage/seconds', 0.5)
            # Need to show the Viewport Hud globally, it contains the scroll speed
            settings.set('/app/viewport/forceHideFps', False)
            settings.destroy_item("/persistent/app/viewport/TestWindow/Viewport0")

            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)

            vp_callback(vp_window)
            await self.wait_n_updates()
            await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)

        finally:
            # Restore to default state
            settings.set('/app/viewport/toastMessage/seconds', 3)
            settings.set('/app/viewport/toastMessage/fadeIn', 0.5)
            settings.set('/app/viewport/toastMessage/fadeOut', 0.5)
            settings.set("/app/viewport/forceHideFps", True)

            # Test no Window are reachable after destruction
            if vp_window:
                vp_window.destroy()
                del vp_window
            self.assertNoViewportWindows()

    async def test_post_message(self):
        """Test the legacy post-message API works for a single line"""
        def vp_callback(vp_window):
            vp_window._post_toast_message("My First Message", "message_id.0")

        await self._test_post_message(vp_callback, golden_img_name="single_messages.png")

    async def test_post_multiple_messages(self):
        """Test the legacy post-message API works for multiple lines"""
        def vp_callback(vp_window):
            # The _skip_update are important to test the possibility in a real app
            # a code-path that can trigger when toast-messages are added at random
            # times in the event loop.  It is not testing an API, rather knows about internals
            #
            layer = vp_window._find_viewport_layer('Toast Message', 'stats')
            vp_window._post_toast_message("My First Message", "message_id.0")
            layer._skip_update({})
            vp_window._post_toast_message("My Second Message", "message_id.1")
            layer._skip_update({})
            vp_window._post_toast_message("My Third Message", "message_id.2")
            layer._skip_update({})
            vp_window._post_toast_message("My First Message Changed", "message_id.0")
            layer._skip_update({})

        await self._test_post_message(vp_callback, golden_img_name="multiple_messages.png")

    async def test_post_message_no_background(self):
        """Test the legacy post-message API works without a background"""
        def vp_callback(vp_window):
            vp_window._post_toast_message("Message with no BG", "message_id.0")

        settings = carb.settings.get_settings()
        try:
            settings.set("/persistent/app/viewport/ui/background/opacity", 0.0)
            await self._test_post_message(vp_callback, golden_img_name="single_messages_no_bg.png")
        finally:
            settings.destroy_item("/persistent/app/viewport/ui/background/opacity")

    async def test_new_window_custom_context(self):
        """Test instantiating a ViewportWindow to non-default omni.UsdContext"""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_context_name = 'TestContext'
        usd_context = omni.usd.create_context(usd_context_name)
        vp_window = ViewportWindow(f'Custom UsdContext {usd_context_name}', usd_context_name=usd_context_name, width=TEST_WIDTH, height=TEST_HEIGHT)

        self.assertIsNotNone(vp_window)

        self.assertEqual(usd_context, vp_window.viewport_api.usd_context)
        self.assertEqual(usd_context_name, vp_window.viewport_api.usd_context_name)
        # This should equal 0, as it retrieves only ViewportWindow on UsdContext ''
        self.assertEqual(0 + NUM_DEFAULT_WINDOWS, sum(1 for x in get_viewport_window_instances()))
        # This should equal 1, as it retrieves only ViewportWindow on UsdContext 'TestContext'
        self.assertEqual(1 + NUM_DEFAULT_WINDOWS, sum(1 for x in get_viewport_window_instances(usd_context_name)))
        # This should also equal 1, as it retrieves -all- ViewportWindow on any UsdContext
        self.assertEqual(1 + NUM_DEFAULT_WINDOWS, sum(1 for x in get_viewport_window_instances(None)))

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

        # Test no Window are reachable after destruction
        vp_window.destroy()
        del vp_window
        self.assertNoViewportWindows()

    async def test_new_window_add_frame(self):
        """Test add_frame API for a ViewportWindow instance"""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        vp_window = None
        settings = carb.settings.get_settings()
        settings.set("/rtx/post/backgroundZeroAlpha/enabled", True)

        try:
            vp_window = ViewportWindow('TestWindowWithFrame', width=TEST_WIDTH, height=TEST_HEIGHT)

            custom_frame = vp_window.get_frame('custom_frame')
            # Test the frame is returned from a second call with the same name
            self.assertEqual(custom_frame, vp_window.get_frame('custom_frame'))

            with custom_frame:
                ui.Rectangle(width=TEST_WIDTH, height=TEST_HEIGHT / 2, style_type_name_override='CustomFrame')

            vp_window.set_style({
                'ViewportBackgroundColor': {'background_color': 0xffff0000},
                'CustomFrame': {'background_color': 0xff0000ff},
            })

            await self.wait_n_updates(6)
            await self.finalize_test(golden_img_dir=self._golden_img_dir)

        finally:
            settings.destroy_item("/rtx/post/backgroundZeroAlpha/enabled")

            # Test no Window are reachable after destruction
            if vp_window:
                vp_window.destroy()
                del vp_window
            self.assertNoViewportWindows()

    async def test_viewport_widget_api(self):
        """Test ViewportWidget and ViewportAPI accessors on a ViewportWindow instance"""

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        vp_window = ViewportWindow('TestWindowWithFrame', width=TEST_WIDTH, height=TEST_HEIGHT)
        self.assertIsNotNone(vp_window.viewport_widget)
        self.assertIsNotNone(vp_window.viewport_widget.display_delegate)

        # Test no Window are reachable after destruction
        vp_window.destroy()
        del vp_window
        self.assertNoViewportWindows()

        # Unblocks devices again
        await self.finalize_test_no_image()

    async def __test_hud_memory_info(self, settings, mem_types):
        settings.set("/exts/omni.kit.viewport.window/hud/memoryTypes", [mt.lower() for mt in mem_types])

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)
        vp_window = ViewportWindow('TestWindowHudMemory', width=TEST_WIDTH, height=TEST_HEIGHT)
        found_layers = [vp_window._find_viewport_layer(f"{mt} Memory") is not None for mt in mem_types]
        vp_window.destroy()
        del vp_window

        for found in found_layers:
            self.assertTrue(found)
        self.assertNoViewportWindows()

    async def test_hud_memory_info(self):
        """Test ability to change label of Viewport HUD memory"""

        settings = carb.settings.get_settings()
        try:
            settings.set("/app/viewport/forceHideFps", False)
            await self.__test_hud_memory_info(settings, ["Host"])
            await self.__test_hud_memory_info(settings, ["Process"])
            await self.__test_hud_memory_info(settings, ["Device", "Process"])
        finally:
            # Reset to known prior defaults by delting these items
            settings.destroy_item("/exts/omni.kit.viewport.window/hud/memoryTypes")
            settings.set("/app/viewport/forceHideFps", True)
            await self.finalize_test_no_image()
