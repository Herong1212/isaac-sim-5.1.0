## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from unittest.mock import Mock, call
from ..widget import BrowserBar


class TestBrowserBar(OmniUiTest):
    """Testing PathField.set_path"""
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_nav_buttons(self):
        """Testing navigation buttons"""
        window = await self.create_test_window()
        mock_path_handler = Mock()

        with window.frame:
            under_test = BrowserBar(apply_path_handler=mock_path_handler)

        for path in ["one", "two", "three", "two", "three"]:
            under_test.set_path(path)
        self.assertEqual(under_test.path, "three/")
        self.assertEqual(under_test._visited_history.size(), 5)
        self.assertEqual(under_test._visited_queue.size(), 3)

        under_test._prev_button.call_clicked_fn()
        self.assertEqual(under_test.path, "two/")

        under_test._prev_button.call_clicked_fn()
        self.assertEqual(under_test.path, "three/")

        under_test._prev_button.call_clicked_fn()
        under_test._prev_button.call_clicked_fn()
        self.assertEqual(under_test.path, "one/")
        self.assertFalse(under_test._prev_button.enabled)

        for _ in range(4):
            under_test._next_button.call_clicked_fn()
        self.assertEqual(under_test.path, "three/")
        self.assertFalse(under_test._next_button.enabled)

        self.assertEqual(
            mock_path_handler.call_args_list,
            [call('two'), call('three'), call('two'), call('one'), call('two'), call('three'), call('two'), call('three')]
        )

    async def test_nav_menu(self):
        """Testing navigation menu"""
        window = await self.create_test_window()
        mock_path_handler = Mock()

        with window.frame:
            under_test = BrowserBar(apply_path_handler=mock_path_handler)

        for path in ["one", "two", "three"]:
            under_test.set_path(path)
        self.assertEqual(under_test.path, "three/")

        model = under_test._visited_menu.model
        self.assertEqual(model, under_test._visited_queue)

        model.selected_index = 2
        self.assertEqual(under_test.path, "one/")
        # selecting one of navigation menu browse to that path, and will appear as the most recent visited history
        self.assertFalse(under_test._next_button.enabled)

        under_test.set_path("four")
        self.assertEqual(model.selected_index, 0)
        self.assertEqual(under_test.path, "four/")
