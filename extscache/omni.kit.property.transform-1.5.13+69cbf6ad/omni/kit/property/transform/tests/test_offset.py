## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from pathlib import Path

import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.usd
from carb.input import KeyboardInput
from omni.ui.tests.test_base import OmniUiTest
from pxr import Gf


class TestTransformOffset(OmniUiTest):
    async def setUp(self):
        await super().setUp()

        extension_root_folder = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        )
        self._usd_path = extension_root_folder.joinpath("data/test_data")

        import omni.kit.window.property as p

        self._w = p.get_window()

    async def tearDown(self):
        await super().tearDown()

    async def test_offset_mode(self):
        usd_context = omni.usd.get_context()

        test_file_path = self._usd_path.joinpath("offset_test.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await omni.kit.app.get_app().next_update_async()

        stage = usd_context.get_stage()

        self.assertIsNotNone(stage)

        prim = stage.GetPrimAtPath(f"{stage.GetDefaultPrim().GetPath()}/Cube")
        self.assertTrue(prim.IsValid())

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths([str(prim.GetPath())], True)

        # Let UI build
        # (Note: I'm not sure why we need to wait more than a few frames, but empirically
        # this seems to be the case. So just wait 20 frames to make sure UI is there.)
        await ui_test.wait_n_updates(20)

        button = ui_test.find("Property//Frame/**/Button[*].identifier=='offset_mode_toggle'")
        stack = ui_test.find("Property//Frame/**/HStack[*].identifier=='translate_stack'")

        # We should be able to find the mode toggle button,
        # but until we're in offset mode we should not have any offset fields
        self.assertIsNotNone(button)
        self.assertIsNone(stack)

        await button.click()
        await ui_test.wait_n_updates(20)

        # Now we're in offset mode.
        stack = ui_test.find("Property//Frame/**/HStack[*].identifier=='translate_stack'")
        self.assertIsNotNone(stack)
        # Here's a funny thing -- the double-click clicks the center of the ui element by default.
        # That amounts to setting offsets in Y.
        # Rather than work around that, we're just going to use the Y component for our offset.

        # XXX for some reason, using field.input doesn't give the desired results here --
        # the field's text isn't selected after double-clicking, so we end up entering
        # "0.0100" instead of "100".
        # As a workaround, we'll just break input down into its components (double-click, enter characters,
        # hit enter), with the addition of three backspaces to clear the field's default "0.0"
        await stack.click()
        await stack.double_click()
        await ui_test.human_delay(10)
        for _ in range(3):
            await ui_test.emulate_keyboard_press(KeyboardInput.BACKSPACE)
        await ui_test.emulate_char_press("100")
        await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)

        transform = omni.usd.get_world_transform_matrix(prim)
        self.assertTrue(transform.ExtractTranslation() == Gf.Vec3d(0.0, 100.0, 0.0))

        # Apply another offset, then check the prim's translation
        await stack.double_click()
        await ui_test.human_delay(10)
        for _ in range(3):
            await ui_test.emulate_keyboard_press(KeyboardInput.BACKSPACE)
        await ui_test.emulate_char_press("*2")
        await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)

        transform = omni.usd.get_world_transform_matrix(prim)
        self.assertTrue(transform.ExtractTranslation() == Gf.Vec3d(0.0, 200.0, 0.0))

        # Click and drag field, the check the prim's translation
        drag_vector = stack.center
        drag_vector.x = drag_vector.x + 100
        await ui_test.human_delay(30)
        await ui_test.emulate_mouse_drag_and_drop(stack.center, drag_vector)
        await ui_test.wait_n_updates(2)

        transform = omni.usd.get_world_transform_matrix(prim)
        self.assertTrue(transform.ExtractTranslation() == Gf.Vec3d(0.0, 201.0, 0.0))

        # Finally, toggle offset mode again so subsequent tests will not start in offset mode
        await button.click()
        await ui_test.wait_n_updates(20)
