import os
import tempfile
import omni.kit.test
import omni.client
import omni.kit.app
import omni.ui
import toml
import aiohttp
import platform
import time

from unittest.mock import patch
from ..cache_state_menu import CacheStateMenu, CacheStateDelegate, UIState
from unittest.mock import patch, MagicMock, AsyncMock


class MockResponse:
    def __init__(self, mock_response):
        self.response = mock_response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        pass

class TestCacheStateDelegate(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.delegate = CacheStateDelegate(True, True)
        self.mock_response = AsyncMock()

    async def tearDown(self):
        self.delegate.destroy()
        self.delegate = None
        self.mock_response = None

    def mock_get(self, url):
        return MockResponse(self.mock_response)

    async def test_check_version(self):
        await self.delegate.check_new_version()
        res = await self.delegate.check_latest_hub_version(self.delegate.ngc_resource)
        self.assertIsNotNone(res)

    @patch("omni.kit.widget.cache_indicator.utils.carb.log_error")
    @patch("omni.kit.widget.prompt.Prompt")
    @patch("omni.kit.widget.cache_indicator.utils.get_token")
    @patch("omni.kit.widget.cache_indicator.cache_state_menu.CacheStateDelegate.check_latest_hub_version")
    @patch("omni.kit.widget.cache_indicator.cache_state_menu.CacheStateDelegate.get_correct_file")
    @patch("omni.kit.widget.cache_indicator.cache_state_menu.CacheStateDelegate.download_file")
    async def test_on_download_hub(self, mock_download_file, mock_get_correct_file, mock_check_latest_hub_version, mock_get_token, mock_prompt, mock_log_error):
        # Arrange
        mock_get_token.return_value = "mock_token"
        mock_check_latest_hub_version.return_value = "2024.1.0"
        mock_get_correct_file.return_value = "omni_hub.windows-x86_64@2024.1.0.zip"
        mock_download_file.return_value = None

        # Act
        await self.delegate._on_download_hub()

        # Assert
        mock_check_latest_hub_version.assert_called_once_with(self.delegate.ngc_resource)
        mock_get_correct_file.assert_called_once_with(self.delegate.ngc_resource, "2024.1.0")
        mock_download_file.assert_called_once()

    @patch("omni.kit.widget.cache_indicator.utils.carb.log_error")
    @patch("omni.kit.widget.cache_indicator.cache_state_menu.CacheStateDelegate.create_session_with_headers")
    async def test_download_file(self, mock_create_session_with_headers, mock_log_error):
        # Arrange
        self.mock_response = mock_create_session_with_headers.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value
        self.mock_response.ok = True
        self.mock_response.read.return_value = b"file_content"
        resource = "test_resource"
        version = "1.0.0"
        filename = "test_file.zip"
        download_to = os.path.join(tempfile.gettempdir(), "test_file.zip")

        # Act
        await self.delegate.download_file(resource, version, filename, download_to)

        # Assert
        mock_create_session_with_headers.assert_called_once_with(self.delegate.ngc_token)

    @patch('platform.system', return_value='Windows')
    @patch('aiohttp.ClientSession', autospec=True)
    async def test_get_correct_file(self, mock_client_session, mock_platform_system):
        # Arrange
        self.mock_response.ok = True
        self.mock_response.json.return_value = {
            "recipeFiles": [
                {
                    "sizeInBytes": 72942649,
                    "path": "omni_hub.windows-x86_64@2024.1.0-beta.6+30030c02.zip",
                    "createdDate": "2024-11-25T20:22:12.751Z"
                },
                {
                    "sizeInBytes": 72942649,
                    "path": "omni_hub.windows-x86_64@2024.1.0-beta.5+30030c02.zip",
                    "createdDate": "2024-11-24T20:22:12.751Z"
                }
            ]
        }
        mock_client_session.return_value.__aenter__.return_value.get = self.mock_get
        ngc_resource = "test_resource"
        hub_version = "2024.1.0"

        # Act
        result = await self.delegate.get_correct_file(ngc_resource, hub_version)
        self.assertEqual(result, "omni_hub.windows-x86_64@2024.1.0-beta.6+30030c02.zip")
        self.mock_response.json.assert_called_once()

    @patch("omni.kit.widget.cache_indicator.utils.carb.log_error")
    @patch('platform.system', return_value='Linux')
    @patch('aiohttp.ClientSession', autospec=True)
    async def test_get_correct_file_no_matching_files(self, mock_client_session, mock_platform_system, mock_log_error):
        self.mock_response.ok = True
        self.mock_response.json.return_value = {
            "recipeFiles": [
                {
                    "sizeInBytes": 72942649,
                    "path": "omni_hub.windows-x86_64@2024.1.0-beta.6+30030c02.zip",
                    "createdDate": "2024-11-25T20:22:12.751Z"
                }
            ]
        }
        ngc_resource = "test_resource"
        hub_version = "2024.5.0"
        mock_client_session.return_value.__aenter__.return_value.get = self.mock_get
        result = await self.delegate.get_correct_file(ngc_resource, hub_version)

        self.assertEqual(result, "")
        self.mock_response.json.assert_called_once()

    @patch("omni.kit.widget.prompt.Prompt")
    async def test_prompt_for_confirmation_to_quit(self, mock_prompt):
        mock_prompt_instance = mock_prompt.return_value
        mock_prompt_instance.show = MagicMock()
        mock_prompt_instance.hide = MagicMock()

        await self.delegate._prompt_for_confirmation_to_quit("1.0.0")

        mock_prompt.assert_called_once()
        mock_prompt_instance.show.assert_called_once()

    @patch("webbrowser.open")
    @patch('aiohttp.ClientSession', autospec=True)
    async def test_on_settings_open_success(self, mock_client_session, mock_webbrowser_open):
        # Arrange
        self.mock_response.ok = True
        self.mock_response.status = 200
        self.mock_response.reason = "OK"
        mock_webbrowser_open.return_value = None
        mock_client_session.return_value.__aenter__.return_value.get = self.mock_get
        # Act
        await self.delegate._on_settings_open()

        # Assert
        url = await self.delegate.get_hub_settings_url()
        mock_webbrowser_open.assert_called_once_with(url)

    @patch("webbrowser.open")
    @patch("omni.kit.widget.cache_indicator.cache_state_menu.CacheStateDelegate.create_session_with_headers")
    async def test_on_settings_open_failure(self, mock_create_session_with_headers, mock_webbrowser_open):
        # Arrange
        self.mock_response = mock_create_session_with_headers.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value
        self.mock_response.ok = False
        self.mock_response.status = 404
        self.mock_response.reason = "Not Found"
        mock_webbrowser_open.return_value = None

        # Act
        await self.delegate._on_settings_open()

        # Assert
        mock_create_session_with_headers.assert_called_once_with(self.delegate.ngc_token)
        mock_webbrowser_open.assert_not_called()

    @patch("omni.client.get_hub_http_uri_async", return_value=(omni.client.Result.OK, "http://testuri:14090"))
    async def test_get_hub_settings_url_success(self, mock_get):
        url = await self.delegate.get_hub_settings_url()
        self.assertEqual(url, "http://testuri:14090")

    @patch("omni.client.get_hub_http_uri_async", return_value=(None, "http://testuri:14090"))
    async def test_get_hub_settings_url_no_client_result(self, mock_get):
        url = await self.delegate.get_hub_settings_url()
        # should return default url
        self.assertEqual(url, "http://127.0.0.1:14090")


class TestCacheStateDelegateToggleUIState(omni.kit.test.AsyncTestCase):
    def setUp(self):
        self.delegate = CacheStateDelegate(True, True)
        self.delegate.build_item(None)

    def tearDown(self):
        self.delegate.destroy()
        self.delegate = None

    def test_toggle_ui_state_hub_not_detected(self):
        self.delegate.toggle_ui_state(UIState.HUB_NOT_DETECTED)
        self.assertFalse(self.delegate._hub_label0.visible)
        self.assertFalse(self.delegate._hub_label1.visible)
        self.assertFalse(self.delegate._hub_settings_button.visible)
        self.assertTrue(self.delegate._hub_not_detected_button.visible)
        self.assertFalse(self.delegate._hub_update_button.visible)
        self.assertFalse(self.delegate._is_downloading_label.visible)
        self.assertFalse(self.delegate._progress_bar.visible)
        self.assertFalse(self.delegate._is_installed_label.visible)
        self.assertEqual(self.delegate._widget_width, 200)

    def test_toggle_ui_state_hub_installing(self):
        self.delegate.toggle_ui_state(UIState.HUB_INSTALLING)
        self.assertFalse(self.delegate._hub_label0.visible)
        self.assertFalse(self.delegate._hub_label1.visible)
        self.assertFalse(self.delegate._hub_settings_button.visible)
        self.assertFalse(self.delegate._hub_not_detected_button.visible)
        self.assertFalse(self.delegate._hub_update_button.visible)
        self.assertTrue(self.delegate._is_downloading_label.visible)
        self.assertFalse(self.delegate._progress_bar.visible)
        self.assertFalse(self.delegate._is_installed_label.visible)
        self.assertEqual(self.delegate._widget_width, 200)

    def test_toggle_ui_state_hub_running(self):
        self.delegate.toggle_ui_state(UIState.HUB_RUNNING)
        self.assertTrue(self.delegate._hub_label0.visible)
        self.assertTrue(self.delegate._hub_label1.visible)
        self.assertTrue(self.delegate._hub_settings_button.visible)
        self.assertFalse(self.delegate._hub_not_detected_button.visible)
        self.assertFalse(self.delegate._hub_update_button.visible)
        self.assertFalse(self.delegate._is_downloading_label.visible)
        self.assertFalse(self.delegate._progress_bar.visible)
        self.assertFalse(self.delegate._is_installed_label.visible)
        self.assertEqual(self.delegate._widget_width, 40)

    def test_toggle_ui_state_hub_update_detected(self):
        self.delegate.toggle_ui_state(UIState.HUB_UPDATE_DETECTED)
        self.assertFalse(self.delegate._hub_label0.visible)
        self.assertFalse(self.delegate._hub_label1.visible)
        self.assertFalse(self.delegate._hub_settings_button.visible)
        self.assertFalse(self.delegate._hub_not_detected_button.visible)
        self.assertTrue(self.delegate._hub_update_button.visible)
        self.assertFalse(self.delegate._is_downloading_label.visible)
        self.assertFalse(self.delegate._progress_bar.visible)
        self.assertFalse(self.delegate._is_installed_label.visible)
        self.assertEqual(self.delegate._widget_width, 200)

    def test_toggle_ui_state_hub_installed(self):
        self.delegate.toggle_ui_state(UIState.HUB_INSTALLED)
        self.assertFalse(self.delegate._hub_label0.visible)
        self.assertFalse(self.delegate._hub_label1.visible)
        self.assertFalse(self.delegate._hub_settings_button.visible)
        self.assertFalse(self.delegate._hub_not_detected_button.visible)
        self.assertFalse(self.delegate._hub_update_button.visible)
        self.assertFalse(self.delegate._is_downloading_label.visible)
        self.assertFalse(self.delegate._progress_bar.visible)
        self.assertTrue(self.delegate._is_installed_label.visible)
        self.assertEqual(self.delegate._widget_width, 200)


class TestCacheStateMenu(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.cache_state_menu = CacheStateMenu()

    async def tearDown(self):
        self.cache_state_menu = None

    @patch("omni.client.get_hub_version_with_callback")
    def test_initialize(self, mock_get_hub_version_with_callback):
        self.cache_state_menu._initialize()
        mock_get_hub_version_with_callback.assert_called_once()

    @patch("omni.kit.menu.utils.add_menu_items")
    def test_register_menu_widgets(self, mock_add_menu_items):
        self.cache_state_menu.register_menu_widgets()
        mock_add_menu_items.assert_called_once()

    @patch("omni.kit.menu.utils.remove_menu_items")
    def test_unregister_menu_widgets(self, mock_remove_menu_items):
        self.cache_state_menu.register_menu_widgets()
        self.cache_state_menu.unregister_menu_widgets()
        mock_remove_menu_items.assert_called_once()

    @patch("aiohttp.ClientSession.head")
    async def test_on_update(self, mock_head):
        mock_head.return_value.__aenter__.return_value.status = 200
        self.cache_state_menu._all_cache_apis = ["http://mock_cache_api/ping"]
        self.cache_state_menu._cache_state_delegate = MagicMock()
        self.cache_state_menu._last_time_check = time.monotonic() - 31

        self.cache_state_menu._on_update(0)
        for i in range(4):
            await omni.kit.app.get_app().next_update_async()
        self.cache_state_menu._cache_state_delegate.toggle_ui_state.assert_called_once_with(UIState.HUB_NOT_DETECTED)

    @patch("os.path.exists", return_value=True)
    @patch("toml.load")
    def test_load_cache_config(self, mock_toml_load, mock_os_path_exists):
        mock_toml_load.return_value = {
            "connection_library": {
                "proxy_dict": "http://mock_cache_source_api#http://mock_cache_target_api"
            }
        }
        self.cache_state_menu._load_cache_config()
        self.assertTrue(self.cache_state_menu._cache_enabled)

    @patch("omni.client.get_hub_version_with_callback")
    def test_get_hub_version_cb(self, mock_get_hub_version_with_callback):
        self.cache_state_menu._cache_state_delegate = MagicMock()
        self.cache_state_menu._get_hub_version_cb(omni.client.Result.OK, "2024.1.0")
        self.assertTrue(self.cache_state_menu._hub_enabled)
        self.cache_state_menu._cache_state_delegate.update_cache_state.assert_called_once()

    @patch("os.environ.get", return_value=None)
    def test_load_all_cache_server_apis(self, mock_os_environ_get):
        config_contents = {
            "connection_library": {
                "proxy_dict": "http://mock_cache_source_api#http://mock_cache_target_api"
            }
        }
        result = self.cache_state_menu._load_all_cache_server_apis(config_contents)
        self.assertIn("http://mock_cache_target_api/ping", result)
