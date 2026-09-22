import sys
import unittest
import omni.kit.test
from unittest.mock import patch
from omni.kit.telemetry import should_enable_sentry, start_sentry, remove_sentry_pii_data
import copy
import unittest

class MockApp():

    def __init__(self, is_external=False):
        self.is_external = is_external

    def is_app_external(self):
        return self.is_external

    def get_app_name(self):
        return "test-app"

    def get_app_version(self):
        return "0.1.1"

    def get_app_environment(self):
        return "test"

    def get_kit_version(self):
        return "105.1"


mock_event = {
    "breadcrumbs": {
            "values": [
            {
                "timestamp": 1693940484.77857,
                "type": "subprocess",
                "category": "subprocess",
                "level": "info",
                "message": "'mklink /J \"S:\\\\Remix\\\\rtx-remix\\\\mods\\\\portal_rtx\\\\deps\" \"S:\\\\Remix\\\\rtx-remix\"'"
            }
            ]
        },
    'contexts': {'runtime': {'build': '3.10.13 (main, Sep  6 2023, 19:28:27) [GCC '
                               '7.3.1 20180303 (Red Hat 7.3.1-5)]',
                      'name': 'CPython',
                      'version': '3.10.13'}},
    'environment': 'production',
    'event_id': 'd4097ca1c6fa4d33ab95ce56cd48e890',
    'level': 'error',
    'logentry': {'message': "[Watcher] Failed to resolve USD Asset Identifier '../../../../../../capture/materials/AperturePBR_Opacity.mdl' from prim '/RootNode/meshes/mesh_4019D65FB9B7DF03/Looks/M_Fixture_Glados_Screen_A1_Screen/Shader'",
         "formatted": "[Watcher] Failed to resolve USD Asset Identifier '../../../../../../capture/materials/AperturePBR_Opacity.mdl' from prim '/RootNode/meshes/mesh_4019D65FB9B7DF03/Looks/M_Fixture_Glados_Screen_A1_Screen/Shader'",
          'params': []},
    'logger': 'omni.ext._impl._internal',
    'modules': {'pip': '21.2.1+nv1', 'setuptools': '65.5.1'},
    'platform': 'python',
    'release': 'omni.app.mini-0.1.1',
    'tags': {'app.environment': 'default',
      'app.kit_version': '105.2+.0.00Dev000.local',
      'app.name': 'omni.app.mini',
      'app.version': '0.1.1',
      'session_id': '771899758188315817'},
    'user': {'id': 'foo@nvidia.com'},
        "extra": {
            "filename": "C:\\buildAgent\\work\\kit\\kit\\source\\extensions\\omni.usd.core\\sharedlibs\\omni.usd\\UsdMaterialWatcher.cpp",
            "functionName": "load",
            "lineNumber": 332,
            "sys.argv": [
            "D:\\Repositories\\lightspeedrtx\\lightspeed-kit\\_build\\windows-x86_64\\release\\kit\\kit.exe",
            "D:\\Repositories\\lightspeedrtx\\lightspeed-kit\\_build\\windows-x86_64\\release\\apps/lightspeed.app.trex_dev.kit",
            "--/rtx/verifyDriverVersion/enabled=false",
            "--/app/extensions/registryEnabled=1",
            "--enable",
            "omni.kit.debug.pycharm",
            "--/exts/omni.kit.debug.pycharm/pycharm_location=C:\\Program Files\\JetBrains\\PyCharm 2023.2"
            ]
        },
}

class TestSentryExt(omni.kit.test.AsyncTestCase):

    def test_remove_pii_data(self):
        scrubbed_event = remove_sentry_pii_data(copy.deepcopy(mock_event), None)
        assert int(scrubbed_event["user"]["id"], 16), "User Id should be replaced by a hexadecimal key"
        self.assertEqual(scrubbed_event["logentry"]["message"], "[Watcher] Failed to resolve USD Asset Identifier /AperturePBR_Opacity.mdl' from prim /Shader'", "Message shouldn't have paths")
        self.assertEqual(scrubbed_event["breadcrumbs"]["values"][0]["message"], '\'mklink /J /deps" /rtx-remix"\'', "Message shouldn't have paths")
        self.assertEqual(scrubbed_event["extra"]["filename"], "/UsdMaterialWatcher.cpp", "Filename should only have last part")
        self.assertEqual(scrubbed_event["extra"]["sys.argv"][0], "/kit.exe", "Sys argv0 should only have kit")
        self.assertEqual(scrubbed_event["extra"]["sys.argv"][1], "/lightspeed.app.trex_dev.kit", "Sys argv1 should only have app")
        self.assertEqual(scrubbed_event["extra"]["sys.argv"][6], "--/exts/omni.kit.debug.pycharm/pycharm_location=/PyCharm 2023.2", "Sys argv6 should not have path to pycharm")

    def test_remove_pii_data_with_root_path(self):
        app_root_path = "_build/windows-x86_64/release"
        scrubbed_event = remove_sentry_pii_data(copy.deepcopy(mock_event), None, app_root_path=app_root_path)
        assert int(scrubbed_event["user"]["id"], 16), "User Id should be replaced by a hexadecimal key"
        self.assertEqual(scrubbed_event["logentry"]["message"], "[Watcher] Failed to resolve USD Asset Identifier /AperturePBR_Opacity.mdl' from prim /Shader'", "Message shouldn't have paths")
        self.assertEqual(scrubbed_event["breadcrumbs"]["values"][0]["message"], '\'mklink /J /deps" /rtx-remix"\'', "Message shouldn't have paths")
        self.assertEqual(scrubbed_event["extra"]["filename"], "/UsdMaterialWatcher.cpp", "Filename should only have last part")
        self.assertEqual(scrubbed_event["extra"]["sys.argv"][0], "/kit/kit.exe", "Sys argv0 should only have path off of /kit/") # removed due to the failure in kit CI pipeline execution
        self.assertEqual(scrubbed_event["extra"]["sys.argv"][1], "/apps/lightspeed.app.trex_dev.kit", "Sys argv1 should only have path off of /apps/") # removed due to the failure in kit CI pipeline execution
        self.assertEqual(scrubbed_event["extra"]["sys.argv"][6], "--/exts/omni.kit.debug.pycharm/pycharm_location=/PyCharm 2023.2", "Sys argv6 should not have path to pycharm")

    def test_should_enable_sentry(self):
        app = MockApp(is_external=False)
        settings = {}
        assert should_enable_sentry(app, settings) == False, "Shouldn't be enabled in external builds"

        app = MockApp(is_external=True)
        settings = {"/telemetry/enableSentry": True}

        assert should_enable_sentry(app, settings) == False, "Shouldn't be enabled in external builds if setting set"

        app = MockApp(is_external=False)
        settings = {"/telemetry/enableSentry": True}

        assert should_enable_sentry(app, settings) == True, "Should be enabled in internal builds if setting set"

        app = MockApp(is_external=False)
        settings = {"/telemetry/enableSentry": False}

        assert should_enable_sentry(app, settings) == False, "Shouldn't be enabled in internal builds if setting set"

    @patch('omni.kit.telemetry.sentry_extension._get_sentry_sdk')
    @patch('omni.kit.telemetry.sentry_extension._get_sentry_logging_integration')
    def test_start_sentry(self, mocked_sentry_sdk, mock_logging_integration):
        app = MockApp(is_external=False)
        settings = {"/telemetry/enableSentry": True}

        has_started = start_sentry(app, settings)
        assert has_started == True, "Sentry should have started"
