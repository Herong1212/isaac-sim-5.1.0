from typing import Any

from omni.kit.test import AsyncTestCase
import omni.usd

from ..drag_and_drop_registry import DragAndDropRegistry
from ..stage_drag_and_drop_handler import StageDragAndDropHandler
from ..stage_model import StageModel

class TestStageDragDropHandler(AsyncTestCase):
    async def test_drag_drop_registry(self):

        def test_filter(source: Any) -> bool:
            return isinstance(source, str) and source.startswith("Test::")

        def test_handler(source: Any, target_item: Any) -> None:
                self._dropped += 1
                return

        self._dropped = 0
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()
        drop_handler = StageDragAndDropHandler(StageModel(stage))
        source = "Test:://test.usd"

        # For custom url, unaccepted
        self.assertFalse(drop_handler.drop_accepted(None, source))

        # Register new drop handler, drop accepted
        DragAndDropRegistry().register_drop_handler("test", test_filter, test_handler)
        self.assertTrue(drop_handler.drop_accepted(None, source))

        drop_handler.drop(None, source)
        self.assertEqual(self._dropped, 1)

        # Drop handler unregistered, custom url unaccepted again
        DragAndDropRegistry().deregister_drop_handler("test")
        self.assertFalse(drop_handler.drop_accepted(None, source))