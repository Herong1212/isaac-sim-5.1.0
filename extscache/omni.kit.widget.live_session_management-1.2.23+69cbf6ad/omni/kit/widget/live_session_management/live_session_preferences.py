from .utils import QUICK_JOIN_ENABLED
from .utils import SESSION_LIST_SELECT, SESSION_LIST_SELECT_DEFAULT_SESSION, SESSION_LIST_SELECT_LAST_SESSION
import carb.settings
import omni.ui as ui
from omni.kit.widget.settings import SettingType
from omni.kit.window.preferences import PreferenceBuilder


class LiveSessionPreferences(PreferenceBuilder):
    SETTING_PAGE_NAME = "Live"

    def clear_widgets(self):
        self._checkbox_quick_join_enabled = None
        self._combobox_session_list_select = None

    def __init__(self):
        super().__init__(self.SETTING_PAGE_NAME)
        self.clear_widgets()

    def destroy(self):
        self.clear_widgets()

    def build(self):
        self.clear_widgets()
        with ui.VStack(height=0):
            with self.add_frame("Join"):
                with ui.VStack():
                    self._checkbox_quick_join_enabled = self.create_setting_widget(
                        "Quick Join Enabled",
                        QUICK_JOIN_ENABLED,
                        SettingType.BOOL,
                        tooltip="Quick Join, creates and joins a Default session and bypasses dialogs.",
                    )
                    ui.Spacer()
                    self._combobox_session_list_select = self.create_setting_widget_combo(
                        "Session List Select",
                        SESSION_LIST_SELECT,
                        [SESSION_LIST_SELECT_DEFAULT_SESSION, SESSION_LIST_SELECT_LAST_SESSION],
                    )
            ui.Spacer(height=10)
