# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# BEGIN-DOC-whole_demo
import os
import asyncio
import omni.ui as ui
import omni.usd as usd

from typing import List
from omni.kit.window.file_importer import get_file_importer, ImportOptionsDelegate


# BEGIN-DOC-import_options
class MyImportOptionsDelegate(ImportOptionsDelegate):
    def __init__(self):
        super().__init__(build_fn=self._build_ui_impl, destroy_fn=self._destroy_impl)
        self._widget = None

    def _build_ui_impl(self):
        self._widget = ui.Frame()
        with self._widget:
            with ui.VStack():
                with ui.HStack(height=24, spacing=2, style={"background_color": 0xFF23211F}):
                    ui.Label("Prim Path", width=0)
                    ui.StringField().model = ui.SimpleStringModel()
                ui.Spacer(height=8)

    def _destroy_impl(self, _):
        if self._widget:
            self._widget.destroy()
        self._widget = None
# END-DOC-import_options


# BEGIN-DOC-tagging_options
class MyTaggingOptionsDelegate(ImportOptionsDelegate):
    def __init__(self):
        super().__init__(
            build_fn=self._build_ui_impl,
            filename_changed_fn=self._filename_changed_impl,
            selection_changed_fn=self._selection_changed_impl,
            destroy_fn=self._destroy_impl
        )
        self._widget = None

    def _build_ui_impl(self, file_type: str=''):
        self._widget = ui.Frame()
        with self._widget:
            with ui.VStack():
                ui.Button(f"Tags for {file_type or 'unknown'} type", height=24)

    def _filename_changed_impl(self, filename: str):
        if filename:
            _, ext = os.path.splitext(filename)
            self._build_ui_impl(file_type=ext)

    def _selection_changed_impl(self, selections: List[str]):
        if len(selections) == 1:
            _, ext = os.path.splitext(selections[0])
            self._build_ui_impl(file_type=ext)

    def _destroy_impl(self, _):
        if self._widget:
            self._widget.destroy()
        self._widget = None
# END-DOC-tagging_options


class DemoFileImporterDialog:
    """
    Example that demonstrates how to invoke the file importer dialog.
    """
    def __init__(self):
        self._app_window: ui.Window = None
        self._import_options: ImportOptionsDelegate = None
        self._tagging_options: ImportOptionsDelegate = None
        self.build_ui()

    def build_ui(self):
        """ """
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
        self._app_window = ui.Window("File Importer", width=1000, height=500, flags=window_flags)
        with self._app_window.frame:
            with ui.VStack(spacing=10):
                with ui.HStack(height=30):
                    ui.Spacer()
                    button = ui.Button(text="Import File", width=120)
                    button.set_clicked_fn(self._show_dialog)
                    ui.Spacer()

        asyncio.ensure_future(self._dock_window("File Importer", ui.DockPosition.TOP))

    def _show_dialog(self):
        # BEGIN-DOC-get_instance
        # Get the singleton extension.
        file_importer = get_file_importer()
        if not file_importer:
            return
        # END-DOC-get_instance

        # BEGIN-DOC-show_window
        file_importer.show_window(
            title="Import File",
            import_handler=self.import_handler,
            #filename_url="omniverse://ov-rc/NVIDIA/Samples/Marbles/Marbles_Assets.usd",
        )
        # END-DOC-show_window

        # BEGIN-DOC-add_tagging_options
        self._tagging_options = MyTaggingOptionsDelegate()
        file_importer.add_import_options_frame("Tagging Options", self._tagging_options)
        # END-DOC-add_tagging_options

        # BEGIN-DOC-add_import_options
        self._import_options = MyImportOptionsDelegate()
        file_importer.add_import_options_frame("Import Options", self._import_options)
        # END-DOC-add_import_options

    def _hide_dialog(self):
        # Get the File Importer extension.
        file_importer = get_file_importer()
        if file_importer:
            file_importer.hide()

    # BEGIN-DOC-import_handler
    def import_handler(self, filename: str, dirname: str, selections: List[str] = []):
        # NOTE: Get user inputs from self._import_options, if needed.
        print(f"> Import '{filename}' from '{dirname}' or selected files '{selections}'")
    # END-DOC-import_handler

    async def _dock_window(self, window_title: str, position: ui.DockPosition, ratio: float = 1.0):
        frames = 3
        while frames > 0:
            if ui.Workspace.get_window(window_title):
                break
            frames = frames - 1
            await omni.kit.app.get_app().next_update_async()

        window = ui.Workspace.get_window(window_title)
        dockspace = ui.Workspace.get_window("DockSpace")

        if window and dockspace:
            window.dock_in(dockspace, position, ratio=ratio)
            window.dock_tab_bar_visible = False

    def destroy(self):
        if self._app_window:
            self._app_window.destroy()
            self._app_window = None


if __name__ == "__main__":
    view = DemoFileImporterDialog()
# END-DOC-whole_demo
