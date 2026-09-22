# from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.kit.test


class TestSequencerCore(omni.kit.test.AsyncTestCaseFailOnLogError):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass


# TODO:
# extension.py:
# Test SequencerExt.default_attr is empty after on_startup
# Test g_singleton is None after on_shutdown
