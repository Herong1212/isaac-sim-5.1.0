## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.kit.app
import omni.client

from unittest.mock import patch, Mock
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import get_test_data_path
from .. import get_content_window


class TestNavigate(AsyncTestCase):
    """Testing ContentBrowserWidget.open_and_navigate_to"""
    async def setUp(self):
        await ui_test.find("Content").focus()

    async def tearDown(self):
        pass

    async def test_file_found_and_opened(self):
        """Testing when navigating to USD file, opens it"""
        content_browser = get_content_window()
        under_test = content_browser.window.widget
        url = get_test_data_path(__name__, "4Lights.usda")

        mock_open_stage = Mock()
        with patch("omni.kit.window.content_browser.file_ops.get_file_open_handler", return_value=mock_open_stage):
            # patch("omni.kit.window.content_browser.widget.open_stage") as mock_open_stage:
            under_test._open_and_navigate_to(url)
            await ui_test.human_delay(4)
        mock_open_stage.assert_called_once_with(omni.client.normalize_url(url))

    async def test_file_with_spaces_found_and_opened(self):
        """Testing file with surrounding spaces is correctly found"""
        content_browser = get_content_window()
        under_test = content_browser.window.widget
        url = "    " + get_test_data_path(__name__, "4Lights.usda") + "    "

        mock_open_stage = Mock()
        with patch("omni.kit.window.content_browser.file_ops.get_file_open_handler", return_value=mock_open_stage):
            under_test._open_and_navigate_to(url)
            await ui_test.human_delay(4)
        mock_open_stage.assert_called_once_with(omni.client.normalize_url(url.strip()))

    async def test_folder_found_not_opened(self):
        """Testing when navigating to folder with USD extension, doesn't open it"""
        content_browser = get_content_window()
        under_test = content_browser.window.widget
        url = get_test_data_path(__name__, "folder.usda")

        mock_open_stage = Mock()
        with patch("omni.kit.window.content_browser.file_ops.get_file_open_handler", return_value=mock_open_stage):
            under_test._open_and_navigate_to(url)
            await ui_test.human_delay(4)
        mock_open_stage.assert_not_called()

    async def test_invalid_usd_path_still_opened(self):
        """Testing that even if a USD path is invalid, we still try to open it"""
        content_browser = get_content_window()
        under_test = content_browser.window.widget
        url = get_test_data_path(__name__, "not-found.usda")

        mock_open_stage = Mock()
        with patch("omni.kit.window.content_browser.file_ops.get_file_open_handler", return_value=mock_open_stage):
            under_test._open_and_navigate_to(url)
            await ui_test.human_delay(4)
        mock_open_stage.assert_called_once_with(omni.client.normalize_url(url.strip()))
