from datetime import datetime

from omni import ui
from omni.kit.widget.calendar import Calendar
from omni.kit.widget.examples import ExamplePage


class CalendarPage(ExamplePage):
    def __init__(self):
        super().__init__("Calendar")

    def destroy(self):
        self._calendar = None

    def build_page(self):
        with ui.VStack(spacing=5):
            ui.Label("Default:", height=20)
            date_time = datetime.now()
            self._calendar = Calendar(date_time)
