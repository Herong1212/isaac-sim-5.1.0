import shutil
import os
import unittest
import carb.settings
import omni.kit.test
import omni.kit.stage_templates
from pxr import UsdGeom
from omni.kit.window.preferences import PERSISTENT_SETTINGS_PREFIX
from omni.kit.test_suite.helpers import get_test_data_path


class TestUserScript(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    def _cleanup_slashes(self, path: str, is_directory: bool = False) -> str:
        path = os.path.normpath(path)
        if is_directory:
            if path[-1] != "/":
                path += "/"
        return path.replace("\\", "/")

    async def test_user_script(self):
        template_paths = carb.settings.get_settings().get(PERSISTENT_SETTINGS_PREFIX + "/app/newStage/templatePath")
        for path in template_paths:
            user_path = self._cleanup_slashes(carb.tokens.get_tokens_interface().resolve(path))+"/"
            src = get_test_data_path(__name__, "warmlights.py")
            dst = f"{user_path}/warmlights.py"
            shutil.copyfile(src, dst)
            try:
                self.assertFalse('warmlights' in omni.kit.stage_templates.get_stage_template_list()[0])
                omni.kit.stage_templates.load_user_templates()
                self.assertTrue('warmlights' in omni.kit.stage_templates.get_stage_template_list()[0])
            finally:
                os.remove(dst)
