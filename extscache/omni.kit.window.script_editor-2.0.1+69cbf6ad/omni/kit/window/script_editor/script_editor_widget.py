import asyncio
from typing import Optional

import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor
from omni.kit.window.popup_dialog import MessageDialog

from .editor_tab import Tab
from .editor_tab_collection import TabCollection
from .log_view import LogItem, LogView

SETTING_EXECUTE_IN_TEMPFILE = "/exts/omni.kit.window.script_editor/executeInTempFile"
SETTING_CLEAR_AFTER_EXECUTE = "persistent/exts/omni.kit.window.script_editor/clearAfterExecute"
SETTING_EXECUTE_ON_RELOAD = "/persistent/exts/omni.kit.window.script_editor/executeOnReload"


class ScriptEditorWidget:
    def __init__(self, extension_id: str):
        self._extension_id = extension_id
        self._run_hotkey_text = "Ctrl + Enter"
        self._run_text = "Run"
        self._tabs: Optional[TabCollection] = None
        self._update_future = None
        self._sub_update = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            observer_name="[ext: omni.kit.window.script_editor] ScriptEditorWidget::Update",
            on_event=self.__on_update,
        )
        self._has_run_error = False
        self._settings = carb.settings.get_settings()

        self._build_ui()

    def destroy(self) -> None:
        self._log_view.destroy()
        self._sub_update = False
        if self._update_future and not self._update_future.done():
            self._update_future.cancel()
            self._update_future = None

    def _build_ui(self) -> None:
        with ui.VStack():
            # Log view
            self._log_view = LogView(height=ui.Percent(25))
            self._log_model = self._log_view.model
            ui.Spacer(height=10)
            ui.Separator(height=0)
            ui.Spacer(height=8)

            # Editor tabs
            self._tabs = TabCollection()
            ui.Spacer(height=6)

            # Run button and status information
            with ui.HStack(height=0):
                self._btn_run = ui.Button(
                    f"{self._run_text} ({self._run_hotkey_text})",
                    width=0,
                    identifier="execute_script",
                    clicked_fn=self.execute_script,
                )
                ui.Spacer()
                self._status_label = ui.Label("", width=0)
                ui.Spacer(width=20)

    @property
    def current_tab(self) -> Optional[Tab]:
        return self._tabs.current_tab if self._tabs else None

    @property
    def current_editor(self) -> Optional[TextEditor]:
        return self.current_tab.text_editor if self.current_tab else None

    def add_tab(self) -> None:
        if self._tabs:
            self._tabs.add_tab()

    def close_tab(self) -> None:
        if self._tabs:
            self._tabs.close_tab()

    def undo(self) -> None:
        if self.current_editor:
            self.current_editor.undo()

    def redo(self) -> None:
        if self.current_editor:
            self.current_editor.redo()

    def copy(self) -> None:
        if self.current_editor:
            self.current_editor.copy()

    def cut(self) -> None:
        if self.current_editor:
            self.current_editor.cut()

    def delete(self) -> None:
        if self.current_editor:
            self.current_editor.delete()

    def paste(self) -> None:
        if self.current_editor:
            self.current_editor.paste()

    def select_all(self) -> None:
        if self.current_editor:
            self.current_editor.select_all()

    def load_script(self, filename: str) -> None:
        if self._tabs:
            self._tabs.load_script(filename)

    def save_script(self, filename) -> None:
        if self._tabs:
            self._tabs.save_script(filename)

    def execute_script(self) -> None:
        asyncio.ensure_future(self._execute_script_async())

    def get_script_path(self) -> str:
        return self._tabs.get_script_path() if self._tabs else ""

    def set_palette(self, palette: TextEditor.Palette) -> None:
        if self._tabs:
            self._tabs.set_palette(palette)

    def load_content(self, content: str) -> None:
        if self.current_editor:
            self.current_editor.text = content

    def refresh_ui(self) -> None:
        if self._log_view:
            self._log_view.refresh_ui()
        if self._tabs:
            self._tabs.refresh_ui()

    def get_last_log_text(self) -> str:
        return self._log_view.latest_log if self._log_view else ""

    def _reload_script(self) -> None:
        if self.current_tab:
            self.current_tab.reload_script()
        if self._settings.get(SETTING_EXECUTE_ON_RELOAD):
            asyncio.ensure_future(self._execute_script_async())

    async def _execute_script_async(self) -> None:
        current_tab = self.current_tab
        if current_tab:
            self._log_model.set_on_log_error(self._on_log_error)
            self._has_run_error = False
            omni.kit.app.get_app_interface().get_python_scripting().execute_string(
                current_tab.text_editor.selected_text if current_tab.text_editor.selected_text else current_tab.text,
                f"executing: {current_tab.name}...",
                self._settings.get(SETTING_EXECUTE_IN_TEMPFILE),
            )
            # Wait for execution result
            await omni.kit.app.get_app().next_update_async()
            if not self._has_run_error:
                current_tab.clean_error_marks()
                if not current_tab.filename and self._settings.get(SETTING_CLEAR_AFTER_EXECUTE):
                    current_tab.text = ""
            self._log_model.set_on_log_error(None)
            self._log_view.scroll_to_end()

    def _on_log_error(self, item: LogItem) -> None:
        # Truncate error message to do not know callstack from _execute_script_async
        self._has_run_error = True
        texts = item.text.split("\n")
        found = False
        for index, text in enumerate(texts):
            if text.lstrip().startswith(__file__):
                found = True
                break
        if found:
            item.text = "\n".join(texts[:index])
        current_tab = self.current_tab
        if current_tab:
            current_tab.apply_error_message(item.text)

    def __on_update(self, e: carb.eventdispatcher.Event) -> None:
        current_tab = self.current_tab
        if current_tab and self._update_future is None:
            # Run in async to make sure not block update thread
            self._update_future = asyncio.ensure_future(self.__update_async(current_tab))

    async def __update_async(self, current_tab: Tab) -> None:
        editor = current_tab.text_editor

        # Run button label
        self._run_text = "Run Selected" if editor.selected_text else "Run"
        self._btn_run.text = f"{self._run_text} ({self._run_hotkey_text})"

        # Edit status
        cursor = editor.cursor_position
        self._status_label.text = f"Ln {cursor[0]}, Col {cursor[1]}    {'Ovr' if editor.overwrite else 'Ins'}    {str(editor.syntax).split('.')[-1].capitalize()}"

        if current_tab.file_changed:
            if not current_tab.dirty:
                self._reload_script()
            else:
                current_tab.reset_file_modified()

                def __overwrite(dialog: MessageDialog, edit_tab: Tab):
                    dialog.hide()
                    if edit_tab == self.current_tab:
                        self._reload_script()
                    else:
                        edit_tab.reload_script()
                    edit_tab.text_editor.reset_edited()
                    self._update_future = None

                def __ignore(dialog: MessageDialog):
                    dialog.hide()
                    self._update_future = None

                # popup to overwrite or ignore
                dialog = MessageDialog(
                    title=f"{omni.kit.ui.get_custom_glyph_code('${glyphs}/exclamation.svg')}",
                    message="File was modified on disk.\nWould you like to overwrite your changes?",
                    ok_label="Overwrite",
                    cancel_label="Ignore",
                    ok_handler=lambda d, t=current_tab: __overwrite(d, t),
                    cancel_handler=__ignore,
                )
                dialog.show()
                return

        self._update_future = None
