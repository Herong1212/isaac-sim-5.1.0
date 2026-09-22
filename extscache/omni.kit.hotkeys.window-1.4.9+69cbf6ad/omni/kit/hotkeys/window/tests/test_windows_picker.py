import omni.kit.app
from omni.kit.test import AsyncTestCase

from ..window.windows_picker import WindowsPicker


class TestWindowsPicker(AsyncTestCase):
    async def setUp(self):
        self._selected_title = ""

    async def test_general(self):

        def on_selected(window_title: str):
            self._selected_title = window_title

        window = WindowsPicker(width=800, height=600, on_selected_fn=on_selected)
        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        window._search_field.search_words = ["hot"]    # noqa: PLW0212
        await omni.kit.app.get_app().next_update_async()
        items = window._windows_model.get_item_children()    # noqa: PLW0212
        window._actions_view.selection = [item for item in items if item.window_title == "Hotkeys"]    # noqa: PLW0212
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._selected_title, "Hotkeys")
