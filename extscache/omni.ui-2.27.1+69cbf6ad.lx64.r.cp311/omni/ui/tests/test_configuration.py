import glob, os

import omni.kit.test
import omni.kit.app


class ConfigurationTest(omni.kit.test.AsyncTestCase):
    async def test_pyi_file_present(self):
        # Check that omni.ui extension has _ui.pyi file generated
        manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = manager.get_enabled_extension_id("omni.ui")
        self.assertIsNotNone(ext_id)
        ext_path = manager.get_extension_path(ext_id)
        self.assertIsNotNone(ext_path)
        pyi_files = list(glob.glob(ext_path + "/**/_ui.pyi", recursive=True))
        self.assertEqual(len(pyi_files), 1)
