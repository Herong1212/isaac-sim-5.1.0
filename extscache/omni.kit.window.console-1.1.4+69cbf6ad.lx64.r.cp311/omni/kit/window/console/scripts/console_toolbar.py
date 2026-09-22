from functools import partial
from typing import Callable, List, Optional

import carb.logging
import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.kit.widget.filter import FilterButton
from omni.kit.widget.options_menu import OptionItem, OptionCustom, OptionLabelMenuItemDelegate, OptionSeparator

from .log_view import LogView

SETTING_LOG_SOURCES = "/persistent/app/extensions/console/sources"

class ToolbarButton(ui.Button):
    def __init__(self, name: str, tooltip: str, clicked_fn: callable, text: str = "", visible: bool=True):
        """
        Button in toolbar.

        Args:
            name (str): Button name. Used for style.
            tooltip (str): Button tooltip.
            clicked_fn (callable): Callback when button clicked.
            text (str): Button text. Default "" means no text displayed.
        """
        super().__init__(
            text,
            width=22,
            image_width=17,
            name=name,
            style_type_name_override="Toolbar.Button",
            clicked_fn=clicked_fn,
            tooltip=tooltip,
            visible=visible,
        )


class SearchField:
    def __init__(self, on_input_changed_fn: Callable[[str], None]):
        """
        Search field in toolbar.

        Args:
            on_input_changed_fn (Callable[[str], None]): Callabck when input value changed.
        """
        self.__model = ui.SimpleStringModel()
        with ui.ZStack(width=0):
            ui.StringField(self.__model, width=180, style_type_name_override="Toolbar.SearchField")
            self._hint = ui.Label("Search", style_type_name_override="Toolbar.SearchField.hint")

        self.__on_input_changed_fn = on_input_changed_fn
        self.__sub = self.__model.subscribe_value_changed_fn(self.__on_input_changed)

    def destroy(self):
        self.__sub = None

    def __on_input_changed(self, model: ui.SimpleStringModel):
        self._hint.visible = model.as_string == ""
        if self.__on_input_changed_fn:
            self.__on_input_changed_fn(model.as_string)


class ConsoleToolbar:
    def __init__(self, log_view: LogView, cmd_input_visible_model: ui.SimpleBoolModel):
        """
        Toolbar in console window.

        Args:
            log_view (LogView): Log view.
            cmd_input_visible_model (ui.SimpleBoolModel): Model for visibility of command input field.
        """
        self._log_view = log_view
        self.__settings = carb.settings.get_settings()
        self.__cmd_input_visible_model = cmd_input_visible_model
        self.__sub_warnings = self._log_view.warnings_model.subscribe_value_changed_fn(self.__on_warning_changed)
        self.__sub_errors = self._log_view.errors_model.subscribe_value_changed_fn(self.__on_error_changed)
        self._filter_button: Optional[FilterButton] = None
        self._log_buttons: List[ToolbarButton] = []

        self._build_ui()
        self._set_log_level(self._log_view.log_level)

    def destroy(self):
        """Destroy toolbar"""
        self._search_field.destroy()
        if self._filter_button:
            self._filter_button.destroy()

        self.__sub_warnings = None
        self.__sub_errors = None
        self.__sub_filter = None
        self.__sub_source = None
        
    def _build_ui(self):
        show_open_log_buttons = carb.settings.get_settings().get("/exts/omni.kit.window.console/showOpenLogButtons")
        with ui.HStack(height=22, style_type_name_override="Toolbar.Frame"):
            ToolbarButton("clear", "Clear Console", self._log_view.clear)
            ToolbarButton("open_log", "Open Log File", self._open_log_file, visible=show_open_log_buttons)
            ToolbarButton("open_folder", "Open Log Folder", self._open_log_folder, visible=show_open_log_buttons)
            self._command_button = ToolbarButton("command", "Enable Command Field", self._show_command_input, text=">_")

            ui.Spacer()

            self._build_filter_button()
            self._log_buttons = [
                ToolbarButton("verbose", "Verbose", partial(self._set_log_level, carb.logging.LEVEL_VERBOSE)),
                ToolbarButton("info", "Info", partial(self._set_log_level, carb.logging.LEVEL_INFO)),
                ToolbarButton("warning", "Warning", partial(self._set_log_level, carb.logging.LEVEL_WARN), text=self.__get_warnings_button_text()),
                ToolbarButton("error", "Error", partial(self._set_log_level, carb.logging.LEVEL_ERROR), text=self.__get_errors_button_text()),
            ]

            ui.Spacer(width=3)

            self._search_field = SearchField(self._log_view.search)

    def _build_filter_button(self):
        with ui.VStack(width=0):
            ui.Spacer()
            self._filter_button = FilterButton(self._build_filter_items())
            ui.Spacer()

        self.__sub_source = self.__settings.subscribe_to_tree_change_events(SETTING_LOG_SOURCES, self.__on_source_changed)

    def _build_filter_items(self) -> List[OptionItem]:
        sources = self.__settings.get(SETTING_LOG_SOURCES)
        if sources:
            items = [
                OptionCustom(
                    build_fn=lambda: ui.MenuItem(
                        "Select All",
                        delegate=OptionLabelMenuItemDelegate(),
                        triggered_fn=self.__on_select_all_sources,
                        hide_on_click=False
                    )
                ),
                OptionCustom(
                    build_fn=lambda: ui.MenuItem(
                        "Select None",
                        delegate=OptionLabelMenuItemDelegate(),
                        triggered_fn=self.__on_clear_all_sources,
                        hide_on_click=False)
                ),
                OptionSeparator(),
            ]
            items.extend([
                OptionItem(
                    name=source,
                    default=True,
                    setting_path=f"{SETTING_LOG_SOURCES}/{source}",
                    # on_value_changed_fn=lambda value: self._console_model.refresh_logs(),
                )
                for source, value in sources.items()
            ])
            return items
        else:
            return []
        
    def __on_select_all_sources(self):
        for source, value in self.__settings.get(SETTING_LOG_SOURCES).items():
            self.__settings.set(f"{SETTING_LOG_SOURCES}/{source}", True)

    def __on_clear_all_sources(self):
        for source, value in self.__settings.get(SETTING_LOG_SOURCES).items():
            self.__settings.set(f"{SETTING_LOG_SOURCES}/{source}", False)
        
    def __on_source_changed(self, tree_item, changed_item, event_type):
        if event_type == carb.settings.ChangeEventType.CREATED:

            async def rebuild_filter_items():
                await omni.kit.app.get_app().next_update_async()
                filter_items = self._build_filter_items()
                self._filter_button.model.rebuild_items(filter_items)

            import asyncio
            if self._filter_button and self._filter_button.model:
                asyncio.ensure_future(rebuild_filter_items())


    def _open_log_file(self):
        log_file = self.__get_log_file()
        if log_file:
            import webbrowser
            webbrowser.open(log_file)

    def _open_log_folder(self):
        log_file = self.__get_log_file()
        if log_file:
            log_file = log_file.replace("\\", "/")
            file_name = log_file.split("/")[-1]
            folder = log_file[: len(log_file) - len(file_name)]
            import webbrowser
            webbrowser.open(folder)

    def __get_log_file(self) -> str:
        return carb.settings.get_settings().get("/log/file")

    def _show_command_input(self):
        # Here only set command input visible model and button status
        self.__cmd_input_visible_model.set_value(not self.__cmd_input_visible_model.as_bool)
        self._command_button.tooltip = "Disable Command Field" if self.__cmd_input_visible_model.as_bool else "Enable Command Field"
        self._command_button.checked = self.__cmd_input_visible_model.as_bool

    def _set_log_level(self, level: int) -> None:
        # Update log buttons
        index = level - carb.logging.LEVEL_VERBOSE
        for btn in self._log_buttons[:index]:
            btn.checked = False
        for btn in self._log_buttons[index:]:
            btn.checked = True

        self._log_view.set_log_level(level)

    def __on_warning_changed(self, _) -> None:
        index = carb.logging.LEVEL_WARN - carb.logging.LEVEL_VERBOSE
        if index < len(self._log_buttons):
            self._log_buttons[index].text = self.__get_warnings_button_text()

    def __on_error_changed(self, _) -> None:
        index = carb.logging.LEVEL_ERROR - carb.logging.LEVEL_VERBOSE
        if index < len(self._log_buttons):
            self._log_buttons[index].text = self.__get_errors_button_text()

    def __get_warnings_button_text(self) -> str:
        return " " + str(self._log_view.warnings_model.as_int)
    
    def __get_errors_button_text(self) -> str:
        return " " + str(self._log_view.errors_model.as_int)
