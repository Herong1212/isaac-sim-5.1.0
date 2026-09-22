## Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from typing import List, Optional
import carb
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
from carb.input import KeyboardInput
from .. import SearchField
import omni.kit.app
import omni.appwindow
from pathlib import Path

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")


class MyTestCase(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

    # After running each test
    async def tearDown(self):
        self._search_field.destroy()
        self._window.destroy()
        self._window = None
        await super().tearDown()

    async def test_general(self):
        """Testing general look of SearchField"""
        search_string = "General Test"
        await self._emulate_search_field("general", search_string)

        self.assertTrue(self._search_field.visible)
        self.assertTrue(self._search_field.enabled)
        self.assertEqual(self._search_count, 1)
        self.assertEqual(self._result, [search_string.split(" ")])

        window_ref = ui_test.WindowRef(self._window, "")
        close_ref = window_ref.find_all(f"**/Button[*].identifier=='search_word_button'")[0]
        await close_ref.click()
        self.assertEqual(self._search_field.search_words, ["", "Test"])

        # Clear input
        await omni.kit.app.get_app().next_update_async()
        clear_ref = ui_test.WidgetRef(self._search_field._clear_button, "", window=self._window)
        await clear_ref.click()
        self.assertEqual(self._search_field.search_words, [])

    async def test_subscribe(self):
        """Testing SearchField in subscribe mode"""
        search_string = "Search With Subscribe"
        await self._emulate_search_field("subscribe", search_string, subscribe_edit_changed=True)

        self.assertEqual(self._search_count, len(search_string))
        for i in range(len(search_string)):
            expected_search_words = search_string[:i+1].split(" ")
            if not expected_search_words[-1]:
                expected_search_words = expected_search_words[:-1]
            self.assertEqual(self._result[i], expected_search_words)

    async def test_no_token(self):
        """Testing SearchField with no token"""
        search_string = "Search With No Token"
        await self._emulate_search_field("no_token", search_string, show_tokens=False)

        self.assertEqual(self._search_count, 1)
        self.assertEqual(self._result, [search_string.split(" ")])

    async def test_with_suggestions(self):
        search_string = "sugg"
        suggestions = ["this", "is", "a", "suggestion", "test"]
        await self._emulate_search_field("suggestions", search_string, height=60, press_enter=False, suggestions=suggestions)
        self.assertEqual(self._search_field.suggestions, suggestions )
        self.assertEqual(self._search_field.max_suggestions, 10)
        self.assertEqual(self._search_field.suggestions, self._search_field._suggest_window.suggestions)
        self.assertEqual(self._search_field.max_suggestions, self._search_field._suggest_window.max_suggestions)

    async def test_no_separator(self):
        """Testing SearchField with no separator"""
        search_string = "hello world"
        await self._emulate_search_field("no_separator", search_string, show_tokens=False, separator=None)

        self.assertEqual(self._search_count, 1)
        self.assertEqual(self._result, [[search_string]])

    async def _emulate_search_field(self, output: str, search_string: str, height=40, press_enter: bool = True, **search_field_kwargs):
        self._init_result()
        self._window = await self.create_test_window(width=400, height=height)
        with self._window.frame:
            self._search_field = SearchField(on_search_fn=self._on_search, **search_field_kwargs)

        await omni.kit.app.get_app().next_update_async()
        # Enable mouse and keyboard input
        app_window = omni.appwindow.get_default_app_window()
        for device in [carb.input.DeviceType.KEYBOARD, carb.input.DeviceType.MOUSE]:
            app_window.set_input_blocking_state(device, None)

        # Emulate input
        widget = ui_test.WidgetRef(self._search_field._search_field, "", window=self._window)
        # Here cannot use widget.input because cannot set delay_every_n_symbols
        human_delay_speed = 2
        # get focus
        await widget.click(human_delay_speed=human_delay_speed)
        await ui_test.wait_n_updates(human_delay_speed)
        # select input
        await widget.double_click(human_delay_speed=human_delay_speed)
        await ui_test.wait_n_updates(human_delay_speed)
        await ui_test.emulate_char_press(search_string, delay_every_n_symbols=1)
        if press_enter:
            await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)

        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(f"{output}.png")

    async def finalize_test(self, golden_image_name):
        return await super().finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_image_name, threshold=0.03)

    def _on_search(self, search_words: Optional[List[str]]):
        if search_words is not None:
            self._result.append(search_words)
            self._search_count += 1

    def _init_result(self):
        self._result = []
        self._search_count = 0
