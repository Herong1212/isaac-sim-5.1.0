import omni.kit.test
import unittest
import omni.client
import omni.kit.app
from ..utils import *
import os
import toml
from unittest.mock import patch, mock_open, AsyncMock


class MockResponse:
    def __init__(self, mock_response):
        self.response = mock_response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        pass

class TestUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.mock_response = AsyncMock()

    async def tearDown(self):
        self.mock_response = None

    def mock_get(self, url):
        return MockResponse(self.mock_response)

    @patch("omni.kit.widget.cache_indicator.utils.os_pck_default_path")
    @patch("omni.kit.widget.cache_indicator.utils.carb.log_info")
    def test_get_pck_install_folder_with_default_path(self, mock_log_info, mock_os_pck_default_path):
        with patch.dict(os.environ, {"OMNICLIENT_HUB_EXE": ""}):
            mock_os_pck_default_path.return_value = "/default/path"
            result = get_pck_install_folder("", "/non/existent/path")
            self.assertEqual(result, "/default/path")
            mock_log_info.assert_called_with("omniverse.toml config file does not exist")

    @patch("omni.kit.widget.cache_indicator.utils.os_pck_default_path")
    @patch("omni.kit.widget.cache_indicator.utils.carb.log_info")
    def test_get_pck_install_folder_with_env_variable(self, mock_log_info, mock_os_pck_default_path):
        with patch.dict(os.environ, {"OMNICLIENT_HUB_EXE": "/env/path"}):
            result = get_pck_install_folder("", "/non/existent/path")
            self.assertEqual(result, "/env/path")
            mock_log_info.assert_called_with("OmniClient Hub folder found in environment variable (OMNICLIENT_HUB_EXE): /env/path")

    @patch("omni.kit.widget.cache_indicator.utils.os_pck_default_path")
    @patch("omni.kit.widget.cache_indicator.utils.carb.log_info")
    @patch("omni.kit.widget.cache_indicator.utils.toml.load")
    @patch("builtins.open", new_callable=mock_open, read_data='[paths]\nlibrary_root = "/toml/path"')
    @patch("os.path.exists", return_value=True)
    def test_get_pck_install_folder_with_toml_config(self, mock_exists, mock_open, mock_toml_load, mock_log_info, mock_os_pck_default_path):
        with patch.dict(os.environ, {"OMNICLIENT_HUB_EXE": ""}):
            mock_toml_load.return_value = toml.loads('[paths]\nlibrary_root = "/toml/path"')
            result = get_pck_install_folder("", "/existent/path")
            mock_log_info.assert_called_with("Found library_root in omniverse.toml: /toml/path")

    @patch("omni.kit.widget.cache_indicator.utils.os_pck_default_path")
    @patch("omni.kit.widget.cache_indicator.utils.carb.log_info")
    @patch("omni.kit.widget.cache_indicator.utils.toml.load")
    @patch("builtins.open", new_callable=mock_open, read_data='[paths]\nlibrary_root = ""')
    @patch("os.path.exists", return_value=False)
    def test_get_pck_install_folder_with_empty_toml_config(self, mock_exists, mock_open, mock_toml_load, mock_log_info, mock_os_pck_default_path):
        with patch.dict(os.environ, {"OMNICLIENT_HUB_EXE": ""}):
            mock_os_pck_default_path.return_value = "/default/path"
            mock_toml_load.return_value = toml.loads('[paths]\nlibrary_root = ""')
            result = get_pck_install_folder("", "/existent/path")
            self.assertEqual(result, "/default/path")
            mock_log_info.assert_called_with("omniverse.toml config file does not exist")

    @patch("omni.kit.widget.cache_indicator.utils.carb.log_warn")
    @patch("omni.kit.widget.cache_indicator.utils.carb.log_error")
    def test_log_http_error_404(self, mock_log_error, mock_log_warn):
        error = HTTPError(url=None, code=404, msg="Not Found", hdrs=None, fp=None)
        log_http_error(error, "TestResource")
        mock_log_warn.assert_called_once_with("TestResource was not found. May be a permission issue. Error: $HTTP Error 404: Not Found")

    @patch("omni.kit.widget.cache_indicator.utils.carb.log_warn")
    @patch("omni.kit.widget.cache_indicator.utils.carb.log_error")
    def test_log_http_error_500(self, mock_log_error, mock_log_warn):
        error = HTTPError(url=None, code=500, msg="Internal Server Error", hdrs=None, fp=None)
        log_http_error(error, "TestResource")
        mock_log_error.assert_called_once_with("TestResource was not found. May be a permission issue. Error: $HTTP Error 500: Internal Server Error")

    @patch("platform.system", return_value="Windows")
    def test_is_windows_true(self, mock_platform_system):
        self.assertTrue(is_windows())
        mock_platform_system.assert_called_once()

    @patch("platform.system", return_value="Linux")
    def test_is_windows_false(self, mock_platform_system):
        self.assertFalse(is_windows())
        mock_platform_system.assert_called_once()

    @unittest.skipIf(platform.system().lower() != "windows", "")
    @patch("subprocess.Popen")
    @patch("omni.kit.widget.cache_indicator.utils.is_windows", return_value=True)
    def test_run_process_windows(self, mock_is_windows, mock_popen):
        args = ["echo", "Hello, World!"]
        run_process(args)
        mock_popen.assert_called_once_with(args, close_fds=False, creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP)

    @unittest.skipIf(platform.system().lower() == "windows", "")
    @patch("subprocess.Popen")
    @patch("omni.kit.widget.cache_indicator.utils.is_windows", return_value=False)
    def test_run_process_non_windows(self, mock_is_windows, mock_popen):
        args = ["echo", "Hello, World!"]
        run_process(args)
        mock_popen.assert_called_once_with(args, close_fds=False)

    @patch("platform.system", return_value="Windows")
    def test_os_pck_default_path_windows(self, mock_platform_system):
        expected_path = os.path.join(Path.home(), "AppData", "Local", "ov", "pkg")
        self.assertEqual(os_pck_default_path(), expected_path)
        mock_platform_system.assert_called_once()

    @patch("platform.system", return_value="Linux")
    def test_os_pck_default_path_linux(self, mock_platform_system):
        expected_path = os.path.join(Path.home(), ".local", "share", "ov", "pkg")
        self.assertEqual(os_pck_default_path(), expected_path)
        mock_platform_system.assert_called_once()

    @patch("platform.system", return_value="Darwin")
    def test_os_pck_default_path_mac(self, mock_platform_system):
        expected_path = os.path.join(Path.home(), ".local", "share", "ov", "pkg")
        self.assertEqual(os_pck_default_path(), expected_path)
        mock_platform_system.assert_called_once()

    @patch('aiohttp.ClientSession', autospec=True)
    async def test_get_token_with_valid_api_key(self, mock_client_session):
        self.mock_response.ok = True
        self.mock_response.json.return_value = {
            "token": "test_token"
        }
        
        api_key = "valid_api_key"
        org = "test_org"
        team = "test_team"
        mock_client_session.return_value.__aenter__.return_value.get = self.mock_get
        token = await get_token(api_key, org, team)
        
        self.assertEqual(token, "test_token")
        self.mock_response.json.assert_called_once()

    @patch('aiohttp.ClientSession', autospec=True)
    async def test_get_token_with_empty_api_key(self, mock_client_session):
        api_key = ""
        org = "test_org"
        team = "test_team"
        token = await get_token(api_key, org, team)
        
        self.assertEqual(token, "")

    @patch('aiohttp.ClientSession', autospec=True)
    @patch("omni.kit.widget.cache_indicator.utils.carb.log_error")
    async def test_get_token_general_exception(self, mock_log_error, mock_client_session):
        self.mock_response.ok = False
        self.mock_response.status = 401
        
        api_key = "invalid_api_key"
        org = "test_org"
        team = "test_team"
        mock_client_session.return_value.__aenter__.return_value.get = self.mock_get
        token = await get_token(api_key, org, team)
        
        self.assertEqual(token, None)
