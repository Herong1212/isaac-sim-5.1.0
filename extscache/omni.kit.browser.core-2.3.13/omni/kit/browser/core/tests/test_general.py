import omni.kit.test
from omni.kit.browser.core import create_drop_helper


class TestGeneral(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_general(self):
        # No viewport enabled, always None
        helper = create_drop_helper()
        self.assertIsNone(helper)
