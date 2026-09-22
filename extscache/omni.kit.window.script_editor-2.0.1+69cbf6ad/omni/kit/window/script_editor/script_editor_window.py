# Copyright (c) 2018-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ScriptEditorWindow"]

import asyncio
import copy
from typing import Dict, List, Optional

import carb.input
import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor
from omni.ui import constant as fl

from .script_editor_menu import MenuOptions
from .script_editor_widget import SETTING_CLEAR_AFTER_EXECUTE, SETTING_EXECUTE_ON_RELOAD, ScriptEditorWidget
from .snippets import load_snippets
from .style import MENU_STYLE, WINDOW_STYLE

EDITOR_PALETTE_MAP = {
    "Dark": TextEditor.Palette.Dark,
    "Light": TextEditor.Palette.Light,
    "Retro Blue": TextEditor.Palette.RetroBlue,
}
FONT_SIZE_LIST = [12, 14, 16, 18, 20, 22, 26, 32, 36, 40, 44, 48, 52]
SETTING_FONT_NAME = "/persistent/exts/omni.kit.window.script_editor/font"
SETTING_FONT_SIZE = "/persistent/exts/omni.kit.window.script_editor/fontSize"
SETTING_PALETTE = "/persistent/exts/omni.kit.window.script_editor/editorPalette"


class ScriptEditorWindow(ui.Window):
    """The Script Editor window"""

    TITLE = "Script Editor"

    def __init__(self, extension_id: str):
        self._extension_id = extension_id
        self._settings = carb.settings.get_settings()
        self._script_editor_widget: Optional[ScriptEditorWidget] = None
        self._loaded_snippets: Dict[str, List[Dict]] = None

        super().__init__(
            self.TITLE, width=800, height=600, flags=ui.WINDOW_FLAGS_MENU_BAR, raster_policy=ui.RasterPolicy.NEVER, focus_policy=ui.FocusPolicy.FOCUS_ON_HOVER
        )

        font_name = self._settings.get(SETTING_FONT_NAME)
        self._additional_style = (
            {
                "TextEditor": {"font": font_name, "font_size": fl.script_editor_font_size},
            }
            if font_name
            else {}
        )
        fl.script_editor_font_size = fl.shade(self._get_font_size())
        self._set_style()
        self.frame.set_build_fn(self._build_ui)

    def destroy(self) -> None:
        self._sub_update = None

        if self._script_editor_widget:
            self._script_editor_widget.destroy()
            self._script_editor_widget = None

        super().destroy()

    def _build_ui(self) -> None:
        with self.frame:
            self._script_editor_widget = ScriptEditorWidget(self._extension_id)

        # Dark is default palette, do not need to set
        palette = self._get_editor_palette()
        if palette != "Dark":
            self._set_editor_palette(palette)

        self._loaded_snippets = load_snippets()
        self._menu_option = MenuOptions(
            load_script=self._script_editor_widget.load_script,
            save_script=self._script_editor_widget.save_script,
            get_file_path=self._script_editor_widget.get_script_path,
        )

        self.menu_bar.menu_compatibility = False
        # Here window menu bar does not use default style in omni.ui, have to set it
        self.menu_bar.set_style(MENU_STYLE)
        self._build_menus()

        self.__input = carb.input.acquire_input_interface()
        app_window = omni.appwindow.get_default_app_window()
        self.__keyboard = app_window.get_keyboard()
        self._sub_update = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            observer_name="[ext: omni.kit.window.script_editor] ScriptEditorWindow::Update",
            on_event=self.__on_update,
        )

    def _build_menus(self) -> None:
        # Here we do not use MenuItemDescription for hotkey, because hotkey does not work if text editor in edit mode
        self.menu_bar.clear()
        with self.menu_bar:
            with ui.Menu("File"):
                ui.MenuItem("Open", hotkey_text = "Alt + O", triggered_fn = self._menu_option.menu_open)
                ui.MenuItem("Save", hotkey_text = "Alt + S", triggered_fn = self._menu_option.menu_save)
                ui.MenuItem("Save As...", hotkey_text = "Shift + Alt + S", triggered_fn = self._menu_option.menu_save_as)
            with ui.Menu("Tab"):
                ui.MenuItem("Add Tab", hotkey_text = "Ctrl + N", triggered_fn = self._script_editor_widget.add_tab)
                ui.MenuItem("Close Tab", hotkey_text = "Ctrl + W", triggered_fn = self._script_editor_widget.close_tab)
            with ui.Menu("Edit"):
                ui.MenuItem("Undo", hotkey_text = "Ctrl + Z", triggered_fn = self._script_editor_widget.undo)
                ui.MenuItem("Redo", hotkey_text = "Ctrl + Y", triggered_fn = self._script_editor_widget.redo)
                ui.MenuItem("Copy", hotkey_text = "Ctrl + C", triggered_fn = self._script_editor_widget.copy)
                ui.MenuItem("Cut", hotkey_text = "Ctrl + X", triggered_fn = self._script_editor_widget.cut)
                ui.MenuItem("Del", hotkey_text = "Del", triggered_fn = self._script_editor_widget.delete)
                ui.MenuItem("Paste", hotkey_text = "Ctrl + V", triggered_fn = self._script_editor_widget.paste)
                ui.MenuItem("Select All", hotkey_text = "Ctrl + A", triggered_fn = self._script_editor_widget.select_all)
            with ui.Menu("Options"):
                ui.MenuItem("Clear After Execute", triggered_fn = self._toggle_clear_after_execute, checkable = True, checked = self._is_clear_after_execute())
                ui.MenuItem("Execute File On Reload", triggered_fn = self._toggle_execute_file_on_reload, checkable = True, checked = self._is_execute_file_on_reload())
                with ui.Menu("Editor Palette"):
                    for palette in EDITOR_PALETTE_MAP:
                        ui.MenuItem(palette, checkable = True, checked = self._get_editor_palette() == palette, triggered_fn = lambda p=palette: self._set_editor_palette(p))
                with ui.Menu("Font Size"):
                    for size in FONT_SIZE_LIST:
                        ui.MenuItem(str(size), checkable = True, checked = self._get_font_size() == size, triggered_fn = lambda s=size: self._set_font_size(s))
            with ui.Menu("Snippets"):
                for category, snippets in self._loaded_snippets.items():
                    with ui.Menu(category):
                        for snippet in snippets:
                            ui.MenuItem(snippet["name"], triggered_fn = lambda c=snippet["content"]: self._script_editor_widget.load_content(c))

    def _set_style(self) -> None:
        window_style = copy.deepcopy(WINDOW_STYLE)
        window_style.update(self._additional_style)
        self.frame.set_style(window_style)

    def _get_font_size(self) -> int:
        return self._settings.get(SETTING_FONT_SIZE)

    def _set_font_size(self, size: int) -> None:
        old = ui.FloatStore.find("script_editor_font_size")
        if old == size:
            return

        ui.FloatStore.store("script_editor_font_size", size)
        self.__refresh_ui()

        self._settings.set(SETTING_FONT_SIZE, size)
        self._rebuild_menus()

    def __refresh_ui(self) -> None:
        # Refresh UI when font size changed
        async def __refresh_ui_async():
            await omni.kit.app.get_app().next_update_async()
            self._set_style()
            self._script_editor_widget.refresh_ui()

        asyncio.ensure_future(__refresh_ui_async())

    def _is_clear_after_execute(self) -> bool:
        return self._settings.get(SETTING_CLEAR_AFTER_EXECUTE)

    def _toggle_clear_after_execute(self) -> None:
        value = self._is_clear_after_execute()
        self._settings.set(SETTING_CLEAR_AFTER_EXECUTE, not value)
        self._rebuild_menus()

    def _is_execute_file_on_reload(self) -> bool:
        return self._settings.get(SETTING_EXECUTE_ON_RELOAD)

    def _toggle_execute_file_on_reload(self) -> None:
        value = self._is_execute_file_on_reload()
        self._settings.set(SETTING_EXECUTE_ON_RELOAD, not value)
        self._rebuild_menus()

    def _set_editor_palette(self, palette_name: str) -> None:
        if self._script_editor_widget:
            self._script_editor_widget.set_palette(EDITOR_PALETTE_MAP[palette_name])
        self._settings.set(SETTING_PALETTE, palette_name)
        self._rebuild_menus()

    def _get_editor_palette(self) -> str:
        return self._settings.get(SETTING_PALETTE)
    
    def _rebuild_menus(self) -> None:
        async def __refresh_menus_async():
            await omni.kit.app.get_app().next_update_async()
            self._build_menus()

        asyncio.ensure_future(__refresh_menus_async())

    def __on_update(self, e: carb.eventdispatcher.Event) -> None:
        # Here handle keyboard input to make sure it also works when text editor in edit mode
        key_modifiers = 0
        if self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.LEFT_ALT) or self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.RIGHT_ALT):
            key_modifiers |= carb.input.KEYBOARD_MODIFIER_FLAG_ALT
        if self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.LEFT_SHIFT) or self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.RIGHT_SHIFT):
            key_modifiers |= carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT
        if self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.LEFT_CONTROL) or self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.RIGHT_CONTROL):
            key_modifiers |= carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL
            
        if self.visible and self.focused:

            def is_key_pressed(key: carb.input.KeyboardInput) -> bool:
                return self.__input.get_keyboard_button_flags(self.__keyboard, key) & carb.input.BUTTON_FLAG_PRESSED

            if key_modifiers == carb.input.KEYBOARD_MODIFIER_FLAG_ALT:
                if is_key_pressed(carb.input.KeyboardInput.O):
                    self._menu_option.menu_open()
                elif is_key_pressed(carb.input.KeyboardInput.S):
                    self._menu_option.menu_save()
            elif key_modifiers == carb.input.KEYBOARD_MODIFIER_FLAG_ALT + carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT:
                if is_key_pressed(carb.input.KeyboardInput.S):
                    self._menu_option.menu_save_as()
            elif key_modifiers == carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL:
                if is_key_pressed(carb.input.KeyboardInput.N):
                    self._script_editor_widget.add_tab()
                elif is_key_pressed(carb.input.KeyboardInput.W):
                    self._script_editor_widget.close_tab()
                elif is_key_pressed(carb.input.KeyboardInput.A):
                    self._script_editor_widget.select_all()
                elif is_key_pressed(carb.input.KeyboardInput.ENTER):
                    self._script_editor_widget.execute_script()
