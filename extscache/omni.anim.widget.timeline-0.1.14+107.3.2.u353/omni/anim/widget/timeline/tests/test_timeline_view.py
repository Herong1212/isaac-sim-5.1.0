"Tests for frame range model"

from unittest import mock

import omni.kit.app
from omni import ui
from omni.anim.widget.timeline import TimelineView
from omni.kit.preferences.animation import TimeDisplay, g_time_display_model, set_time_display
from omni.kit.test.async_unittest import AsyncTestCase

_window_kwargs = {"width": 600, "height": 100}


class TestTimelineView(AsyncTestCase):
    async def setUp(self) -> None:
        set_time_display(TimeDisplay.FRAMES)
        default_window = ui.Window("Default Timeline", **_window_kwargs)
        with default_window.frame:
            self.timeline_view = TimelineView()
        default_window.visible = True
        await omni.kit.app.get_app().next_update_async()  # build window
        await omni.kit.app.get_app().next_update_async()  # build timeline view

        self.assertIsInstance(self.timeline_view, TimelineView)

    async def test_timeline_rebuild_on_time_display_change(self):
        with mock.patch.object(self.timeline_view, "rebuild", return_value=None) as mock_method:
            set_time_display(TimeDisplay.SECONDS)
            mock_method.assert_called_once()
