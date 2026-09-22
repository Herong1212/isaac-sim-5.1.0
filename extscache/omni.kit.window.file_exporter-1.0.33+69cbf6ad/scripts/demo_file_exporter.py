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

from typing import List
from omni.kit.window.file_exporter import get_file_exporter, ExportOptionsDelegate


# BEGIN-DOC-export_options
class MyExportOptionsDelegate(ExportOptionsDelegate):
    def __init__(self):
        super().__init__(build_fn=self._build_ui_impl, destroy_fn=self._destroy_impl)
        self._widget = None

    def _build_ui_impl(self):
        self._widget = ui.Frame()
        with self._widget:
            with ui.VStack(style={"background_color": 0xFF23211F}):
                ui.Label("Checkpoint Description", alignment=ui.Alignment.CENTER)
                ui.Separator(height=5)
                model = ui.StringField(multiline=True, height=80).model
                model.set_value("This is my new checkpoint.")

    def _destroy_impl(self, _):
        if self._widget:
            self._widget.destroy()
        self._widget = None
# END-DOC-export_options


# BEGIN-DOC-tagging_options
class MyTaggingOptionsDelegate(ExportOptionsDelegate):
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

class DemoFileExporterDialog:
    """
    Example that demonstrates how to invoke the file exporter dialog.
    """
    def __init__(self):
        self._app_window: ui.Window = None
        self._export_options = ExportOptionsDelegate = None
        self._tag_options = ExportOptionsDelegate = None
        self.build_ui()

    def build_ui(self):
        """ """
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
        self._app_window = ui.Window("File Exporter", width=1000, height=500, flags=window_flags)
        with self._app_window.frame:
            with ui.VStack(spacing=10):
                with ui.HStack(height=30):
                    ui.Spacer()
                    button = ui.RadioButton(text="Export File", width=120)
                    button.set_clicked_fn(self._show_dialog)
                    ui.Spacer()

        asyncio.ensure_future(self._dock_window("File Exporter", ui.DockPosition.TOP))

    def _show_dialog(self):
        # BEGIN-DOC-get_instance
        # Get the singleton extension object, but as weakref to guard against the extension being removed. 
        file_exporter = get_file_exporter()
        if not file_exporter:
            return
        # END-DOC-get_instance

        # BEGIN-DOC-show_window
        file_exporter.show_window(
            title="Export As ...",
            export_button_label="Save",
            export_handler=self.export_handler,
            filename_url="omniverse://ov-rc/NVIDIA/Samples/Marbles/foo",
            show_only_folders=True,
            enable_filename_input=False,
        )
        # END-DOC-show_window

        # BEGIN-DOC-add_tagging_options
        self._tagging_options = MyTaggingOptionsDelegate()
        file_exporter.add_export_options_frame("Tagging Options", self._tagging_options)
        # END-DOC-add_tagging_options

        # BEGIN-DOC-add_export_options
        self._export_options = MyExportOptionsDelegate()
        file_exporter.add_export_options_frame("Export Options", self._export_options)
        # END-DOC-add_export_options

    def _hide_dialog(self):
        # Get the Content extension object. Same as: omni.kit.window.file_exporter.get_extension()
        # Keep as weakref to guard against the extension being removed at any time. If it is removed,
        # then invoke appropriate handler; in this case the destroy method.
        file_exporter = get_file_exporter()
        if file_exporter:
            file_exporter.hide()

    # BEGIN-DOC-export_handler
    def export_handler(self, filename: str, dirname: str, extension: str = "", selections: List[str] = []):
        # NOTE: Get user inputs from self._export_options, if needed.
        print(f"> Export As '{filename}{extension}' to '{dirname}' with additional selections '{selections}'")
    # END-DOC-export_handler

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
    view = DemoFileExporterDialog()
# END-DOC-whole_demo
