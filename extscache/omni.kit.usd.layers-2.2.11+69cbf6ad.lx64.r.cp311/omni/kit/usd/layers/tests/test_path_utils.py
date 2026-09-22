import omni.kit.test
import omni.usd

from omni.kit.usd.layers._impl.path_utils import PathUtils


class TestPathUtils(omni.kit.test.AsyncTestCase):
    def test_is_omni_path(self):
        path = "omniverse://test-server/invalid_path"
        self.assertTrue(PathUtils.is_omni_objects_enabled_path(path))
        path = "c:/file.usd"
        self.assertFalse(PathUtils.is_omni_objects_enabled_path(path))
