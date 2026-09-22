"""Testing the existence of the extensions in the bundle"""

from pathlib import Path

import omni.kit
import toml


# ======================================================================
class _TestExtensions(omni.kit.test.AsyncTestCase):
    async def test_extensions(self):
        extension_mgr = omni.kit.app.get_app().get_extension_manager()
        self.assertIsNotNone(extension_mgr)

        # Rather than hardcode the list get it from the extension.toml so that the test adjusts when that list changes
        toml_file = Path(__file__).parent.parent.parent.parent.parent.parent / "config" / "extension.toml"
        with open(toml_file, "r", encoding="utf-8") as toml_fd:
            toml_contents = toml.load(toml_fd)

        dependencies = toml_contents["dependencies"]
        self.assertTrue(len(dependencies) > 3)

        for extension_name in dependencies.keys():
            self.assertTrue(extension_mgr.is_extension_enabled(extension_name))
