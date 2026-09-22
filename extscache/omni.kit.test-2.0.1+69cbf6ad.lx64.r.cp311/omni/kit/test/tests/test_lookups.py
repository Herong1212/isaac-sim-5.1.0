"""Test the functionality used by the test runner."""
from unittest import mock

import omni.kit.app
import omni.kit.test
from omni.kit.test.ext_utils import get_module_to_extension_map, extension_from_test_name
from omni.kit.test.exttests import _find_latest_valid_ext_id


class TestLookups(omni.kit.test.AsyncTestCase):
    async def test_lookups(self):
        """Oddly self-referencing test that uses the test runner test lookup utility to confirm that the utility
        finds this test.
        """
        manager = omni.kit.app.get_app().get_extension_manager()
        my_extension_id = manager.get_enabled_extension_id("omni.kit.test")

        module_map = get_module_to_extension_map()
        self.assertTrue("omni.kit.test" in module_map)
        extension_info = module_map["omni.kit.test"]
        self.assertEqual((my_extension_id, True), extension_info)

        this_test_info = extension_from_test_name("omni.kit.test.TestLookups.test_lookups", module_map)
        self.assertIsNotNone(this_test_info)
        this_test_info_no_module = tuple(e for i, e in enumerate(this_test_info) if i != 2)
        self.assertEqual((my_extension_id, True, False), this_test_info_no_module)

    async def test_find_latest_valid_ext_id(self):
        """Test the function that finds the latest valid extension id."""
        ext_def = "omni.kit.example"
        match_version_as_string = True

        # Mock the extension manager
        manager = mock.Mock()

        # The mocked values are perpared so that the remote considers 1.1.0 is the latest valid version,
        # and the local considers 1.2.0 is the latest valid version.
        #
        # Case 1: use_registry = True, get the result from remote (i.e., manager.get_registry_extension_dict())
        manager.fetch_extension_versions.return_value = [
            {"id": "omni.kit.example-1.2.0"},
            {"id": "omni.kit.example-1.1.0"},
            {"id": "omni.kit.example-1.0.0"},
        ]
        yanked = {
            "omni.kit.example-1.2.0": True,
            "omni.kit.example-1.1.0": False,
            "omni.kit.example-1.0.0": False,
        }
        manager.get_registry_extension_dict.side_effect = lambda ext_id: mock.Mock(get_dict=lambda: {"package": {"yanked": yanked[ext_id]}})
        manager.get_extension_dict.return_value = mock.Mock(get_dict=lambda: {"package": {"yanked": False}})

        ext_id = _find_latest_valid_ext_id(ext_def, match_version_as_string, True, manager)
        self.assertEqual(ext_id, "omni.kit.example-1.1.0")

        # Case 2: use_registry = True, get the result from local (i.e., manager.get_extension_dict())
        manager.get_registry_extension_dict.return_value = None
        manager.get_registry_extension_dict.side_effect = None

        ext_id = _find_latest_valid_ext_id(ext_def, match_version_as_string, True, manager)
        self.assertEqual(ext_id, "omni.kit.example-1.2.0")

        # Case 3: use_registry = True, no valid result
        manager.get_extension_dict.return_value = None
        manager.get_extension_dict.side_effect = None

        ext_id = _find_latest_valid_ext_id(ext_def, match_version_as_string, True, manager)
        self.assertIsNone(ext_id)

        # Case 4: use_registry = False, the remote is not referenced
        manager.get_registry_extension_dict.side_effect = lambda ext_id: mock.Mock(get_dict=lambda: {"package": {"yanked": yanked[ext_id]}})
        manager.get_extension_dict.return_value = mock.Mock(get_dict=lambda: {"package": {"yanked": False}})

        ext_id = _find_latest_valid_ext_id(ext_def, match_version_as_string, False, manager)
        self.assertEqual(ext_id, "omni.kit.example-1.2.0")