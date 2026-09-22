from typing import Optional

import carb.logging
import carb.settings
import omni.kit.clipboard
import omni.ui as ui

from .._console import ConsoleLogView

SETTING_LOG_LEVEL = "/persistent/app/extensions/console/filterLevel"


class LogView:
    def __init__(self):
        """
        Wrapper of ConsoleLogView to show/manager log view.
        """
        self.warnings_model = ui.SimpleIntModel()
        self.errors_model = ui.SimpleIntModel()
        self.sources_model = ui.SimpleStringModel()
        
        self.__settings = carb.settings.get_settings()
        self.log_level = self.__settings.get(SETTING_LOG_LEVEL) or carb.logging.LEVEL_WARN
        self.set_log_level(self.log_level)

        self._console_log_view = None
        self._context_menu: Optional[ui.Menu] = None

    def destroy(self):
        """Destroy log view"""
        self._update_sub = None

    def build_widget(self):
        self._console_log_view = ConsoleLogView(name="log")    
        self._console_log_view.set_mouse_pressed_fn(lambda x, y, btn, m: self.__on_mouse_pressed(btn))
        self._console_log_view.set_log_level(self.log_level)
        self._console_log_view.set_log_changed_fn(self.__on_log_changed)

    def set_log_level(self, level: int) -> None:
        """
        Set log level.

        Args:
            level (int): Log level. Could be carb.logging.LEVEL_XXX.
        """
        if level != self.log_level:
            self.log_level = level
            self.__settings.set(SETTING_LOG_LEVEL, level)
            if self._console_log_view:
                self._console_log_view.set_log_level(level)
        # Allow threshold log level switch between Info and Verbose
        # Set the level threshold to info (unless it's already verbose)
        # Even if the 'filterLevel' is higher (warning, for example) we still force the log level threshold to
        # Info so we can capture the messages to show in the list if the user later clicks the "Info" button.
        logging = carb.logging.acquire_logging()
        current_level_threshold = logging.get_level_threshold()
        expected_level_threshold = carb.logging.LEVEL_VERBOSE if level == carb.logging.LEVEL_VERBOSE else carb.logging.LEVEL_INFO
        if current_level_threshold != expected_level_threshold:
            logging.set_level_threshold(expected_level_threshold)

    def clear(self) -> None:
        """
        Clear log items, filters and counters.

        args requied for comm
        """
        if self._console_log_view:
            self._console_log_view.clear_log()

    def search(self, text: str) -> None:
        """
        Search logs by message text.

        Args:
            text (str): Message text to search logs.
        """
        if self._console_log_view:
            self._console_log_view.search(text)

    def __on_log_changed(self, verbose: int, info: int, warn: int, error: int):
        self.warnings_model.set_value(warn)
        self.errors_model.set_value(error)

    def __on_mouse_pressed(self, button: int):
        # Right click to show context menu
        if button == 1:
            if self._context_menu is None:
                self._context_menu = ui.Menu("###ConsoleContextMenu", menu_compatibility=False)
            else:
                self._context_menu.clear()

            with self._context_menu:
                ui.MenuItem("Select All", triggered_fn=self.__select_all_logs)

                selected = self._console_log_view.get_selected_log_count()
                if selected > 0:
                    ui.MenuItem("Copy Message" if selected == 1 else f"Copy {selected} Messages", triggered_fn=self.__copy_message)

            self._context_menu.show()

    def __select_all_logs(self):
        self._console_log_view.select_all_logs()
    
    def __copy_message(self):
        message = self._console_log_view.get_selected_log_string()
        omni.kit.clipboard.copy(message)
