import omni.kit.test
import omni.usd

from ..utils import *


class TestUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_editor_check(self):
        checker = EditorCheck()
        self.assertIsNotNone(checker)
        self.assertFalse(checker.has_editor)

    async def test_uniform_absolute_path(self):
        # create prim first
        self.assertEqual(uniform_absolute_path("/test/obj"), "/test/obj")
        self.assertEqual(uniform_absolute_path("c:/test/obj"), "C:/test/obj")
        self.assertEqual(uniform_absolute_path("omniverse://test/obj\\"), "omniverse://test/obj/")
        self.assertEqual(uniform_absolute_path("\\test\\obj"), "/test/obj")
        self.assertEqual(uniform_absolute_path("c:\\test\\obj"), "C:/test/obj")
        self.assertEqual(uniform_absolute_path("omniverse:\\test\\obj\\"), "omniverse:/test/obj/")
        self.assertEqual(uniform_absolute_path("omniverse:\\test\\..\\obj\\"), "omniverse:/obj/")
