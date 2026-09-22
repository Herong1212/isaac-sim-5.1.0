import asyncio
from typing import List, Optional

import omni.ui as ui
from omni.kit.widget.text_editor import TextEditor

from .editor_tab import Tab


class TabCollection:
    "Collection for editor tabs"

    def __init__(self):
        self._tabs: List[Tab] = []
        self._current_tab_index: int = -1
        self._default_palette = TextEditor.Palette.Dark

        self._build_ui()
        self.add_tab()

    @property
    def current_tab(self) -> Optional[Tab]:
        return self._tabs[self._current_tab_index] if len(self._tabs) > self._current_tab_index >= 0 else None

    @property
    def current_editor(self) -> Optional[TextEditor]:
        return self.current_tab.text_editor if self.current_tab else None

    def add_tab(self, filename: Optional[str] = None) -> Tab:
        index = 0
        while True:
            found = any(editor_tab.index == index for editor_tab in self._tabs)
            if found:
                index += 1
            else:
                break

        editor_tab = Tab(
            index, filename=filename, on_clicked_fn=self._on_header_clicked, on_close_fn=self._on_close_tab
        )
        with self._header_container:
            editor_tab.build_header()

        with self._edit_container:
            editor_tab.build_editor(palette=self._default_palette)

        self._tabs.append(editor_tab)
        self._set_selected(len(self._tabs) - 1)

        return editor_tab

    def close_tab(self) -> None:
        if self._current_tab_index >= 0:
            self._close_tab(self._current_tab_index)

    def load_script(self, filename: str) -> None:
        """Load external file as current editor text"""
        if not filename:
            return
        for index, editor in enumerate(self._tabs):
            if editor.filename == filename:
                editor.reload_script()
                self._set_selected(index)
                return

        editor_tab = self.add_tab()
        if editor_tab.load_script(filename):
            editor_tab.filename = filename
        else:
            # Remove empty tab if failed to open a file
            self._close_tab(self._tabs.index(editor))

    def save_script(self, filename: str) -> None:
        """Save the current editor text to external file"""
        current_tab = self.current_tab
        if current_tab:
            current_tab.save_script(filename)

    def get_script_path(self) -> Optional[str]:
        current_tab = self.current_tab
        return current_tab.filename if current_tab else None

    def set_palette(self, palette: TextEditor.Palette) -> None:
        self._default_palette = palette
        for tab in self._tabs:
            tab.text_editor.palette = palette

    def refresh_ui(self) -> None:
        for tab in self._tabs:
            tab.refresh_ui()

    def _build_ui(self) -> None:
        with ui.VStack():
            with ui.ZStack(height=0):
                self._header_container = ui.HStack(spacing=5, height=0)
                with ui.VStack():
                    ui.Spacer()
                    ui.Separator(height=0)
            ui.Spacer(height=10)
            self._edit_container = ui.ZStack()

    def _set_selected(self, index: int) -> None:
        if self._current_tab_index >= 0:
            self._tabs[self._current_tab_index].set_active(False)

        self._current_tab_index = index
        if self._current_tab_index >= 0:
            self._tabs[self._current_tab_index].set_active(True)

    def _on_header_clicked(self, editor_tab: Tab) -> None:
        index = self._tabs.index(editor_tab)
        self._set_selected(index)

    def _on_close_tab(self, editor_tab: Tab) -> None:
        # To avoid rebuild ui, just remove from list and set invisible
        index = self._tabs.index(editor_tab)
        self._close_tab(index)

    def _close_tab(self, index: int) -> None:
        self._tabs[index].visible = False
        self._tabs[index].text = ""
        del self._tabs[index]

        if self._current_tab_index == index:
            if len(self._tabs) == 0:
                # The last one to be closed

                async def _add_tab_async():
                    self.add_tab()

                asyncio.ensure_future(_add_tab_async())
            else:
                self._current_tab_index = -1
                next = index - 1 if index > 0 else index
                self._set_selected(next)
