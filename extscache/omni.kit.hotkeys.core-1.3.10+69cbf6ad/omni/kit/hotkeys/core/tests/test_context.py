from typing import List
import omni.kit.test

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from omni.kit.hotkeys.core import get_hotkey_context
import carb.settings

SETTING_HOTKEY_CURRENT_CONTEXT = "/exts/omni.kit.hotkeys.core/context"


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestContext(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._settings = carb.settings.get_settings()

    # After running each test
    async def tearDown(self):
        pass

    async def test_empty(self):
        context = get_hotkey_context()
        self.assertEqual(self._settings.get(SETTING_HOTKEY_CURRENT_CONTEXT), "")
        self.assertIsNone(context.get())
        self.assertIsNone(context.pop())

    async def test_push_pop(self):
        max_contexts = 10
        context_names: List[str] = [f"context_{i}" for i in range(max_contexts)]

        context = get_hotkey_context()
        for name in context_names:
            context.push(name)
            self.assertEqual(self._settings.get(SETTING_HOTKEY_CURRENT_CONTEXT), name)
            self.assertEqual(context.get(), name)

        for i in range(max_contexts):
            self.assertEqual(context.pop(), context_names[-(i + 1)])
            if i == max_contexts - 1:
                current = None
            else:
                current = context_names[-(i + 2)]
            self.assertEqual(context.get(), current)
            self.assertEqual(self._settings.get(SETTING_HOTKEY_CURRENT_CONTEXT), current if current else "")

        self.assertIsNone(context.pop())

    async def test_clean(self):
        max_contexts = 10
        context_names: List[str] = [f"context_{i}" for i in range(max_contexts)]

        context = get_hotkey_context()
        for name in context_names:
            context.push(name)

        context.clean()
        self.assertEqual(self._settings.get(SETTING_HOTKEY_CURRENT_CONTEXT), "")
        self.assertIsNone(context.get())
        self.assertIsNone(context.pop())
