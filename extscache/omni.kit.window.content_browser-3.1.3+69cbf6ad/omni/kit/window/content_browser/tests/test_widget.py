## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import omni.kit.test
import omni.client

from omni.kit import ui_test
from unittest.mock import patch
from ..widget import ContentBrowserWidget
from ..api import ContentBrowserAPI
from .. import get_content_window, SETTING_PERSISTENT_CURRENT_DIRECTORY

class TestContentBrowserWidget(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await ui_test.find("Content").focus()

    async def tearDown(self):
        # Clear all bookmarks saved by omni.client, as a result of mounting test servers
        pass

    async def wait_for_update(self, wait_frames=20):
        for _ in range(wait_frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_mount_default_servers(self):
        """Testing that the widget mounts the server specified from the settings"""
        content_browser = get_content_window()
        under_test = content_browser.window.widget
        test_servers = {"my-server": "omniverse://my-server", "her-server": "omniverse://her-server"}

        # Re-run init_view to confirm that the the widget adds the servers specified in
        # the settings.  OM-85963: Mock out all the actual calls to connect the servers because
        # they trigger a host of other actions, incl. callbacks on bookmarks changed, that make
        # this test unreliable.
        with patch.object(ContentBrowserWidget, "_get_mounted_servers", return_value=(test_servers, True)),\
            patch.object(ContentBrowserAPI, "add_connections") as mock_add_connections,\
            patch.object(ContentBrowserAPI, "connect_server") as mock_connect_server,\
            patch.object(ContentBrowserAPI, "subscribe_client_bookmarks_changed"):

            # Initialize the view and expect to mount servers
            under_test._init_view(None, None)

        # Check that widget attempted to add list of servers specified in settings
        mock_add_connections.assert_called_once_with(test_servers)

        # Check that widget attempted to connect to first server in list
        mock_connect_server.assert_called_once_with(test_servers['my-server'])
