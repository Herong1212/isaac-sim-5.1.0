import omni.kit.test
import omni.usd
from omni.kit.widget.layers.path_utils import PathUtils


class TestPathUtils(omni.kit.test.AsyncTestCase):
    def test_utils(self):
        path = "omniverse://test-server/invalid_path"
        self.assertTrue(PathUtils.is_omni_objects_enabled_path(path))
        path = "c:/file.usd"
        self.assertFalse(PathUtils.is_omni_objects_enabled_path(path))

    def test_is_live_layer(self):
        path = "omniverse://test-server/test.live"
        self.assertTrue(PathUtils.is_omni_live(path))
        path = "c:/file.usd"
        self.assertFalse(PathUtils.is_omni_live(path))
