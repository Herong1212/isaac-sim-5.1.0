import asyncio

from omni.ui.tests.test_base import OmniUiTest

from ..update_event_helper import Timer


class TestTimer(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._timer = Timer(1, self._on_timer)

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        self._timer.stop()
        self._timer = None

    async def test_play(self):
        self._timer.start()

        self.assertTrue(self._timer.running)

        await asyncio.sleep(1 + 0.1)

        self.assertFalse(self._timer.running)

    async def test_pause(self):
        self._timer.start()

        self.assertTrue(self._timer.running)

        await asyncio.sleep(0.5)

        self._timer.pause()

        await asyncio.sleep(0.5)

        self.assertTrue(self._timer.running)

        self._timer.resume()

        await asyncio.sleep(0.5 + 0.1)

        self.assertFalse(self._timer.running)

    def _on_timer(self):
        return False
