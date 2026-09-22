# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import weakref
from omni.kit.window.content_browser import get_content_window
from omni.kit.window.filepicker import FilePickerDialog


class DemoContentBrowserClient:
    """
    Example that demonstrates how to add custom actions to the content browser.
    """

    def __init__(self):
        # Get the Content extension object. Same as: omni.kit.window.content_browser.get_extension()
        # Keep as weakref to guard against the extension being removed at any time. If it is removed,
        # then invoke appropriate handler; in this case the destroy method.
        self._content_browser_ref = weakref.ref(get_content_window(), lambda ref: self.destroy())
        self._init_context_menu()

    def _init_context_menu(self):
        def file_extension_of(path: str, exts: [str]):
            _, ext = os.path.splitext(path)
            return ext in exts

        content_browser = self._content_browser_ref()
        if not content_browser:
            return

        # Add these items to the context menu and target to USD file types.
        content_browser.add_context_menu(
            "Collect Asset",
            "spinner.svg",
            lambda menu, path: self._collect_asset(path),
            lambda path: file_extension_of(path, [".usd"]),
        )
        content_browser.add_context_menu(
            "Convert Asset",
            "menu_insert_sublayer.svg",
            lambda menu, path: self._convert_asset(path),
            lambda path: file_extension_of(path, [".usd"]),
        )

        # Add these items to the list view menu and target to USD file types.
        content_browser.add_listview_menu(
            "Echo Selected", "spinner.svg", lambda menu, path: self._echo_selected(path), None
        )

        # Add these items to the list view menu and target to USD file types.
        content_browser.add_import_menu(
            "My Custom Import", "spinner.svg", lambda menu, path: self._import_stuff(path), None
        )

    def _collect_asset(self, path: str):
        print(f"Collecting asset {path}.")

    def _convert_asset(self, path: str):
        print(f"Converting asset {path}.")

    def _echo_selected(self, path: str):
        content_browser = self._content_browser_ref()
        if content_browser:
            print(f"Current directory is {path}.")
            selections = content_browser.get_current_selections(pane=1)
            print(f"TreeView selections = {selections}")
            selections = content_browser.get_current_selections(pane=2)
            print(f"ListView selections = {selections}")

    def _import_stuff(self, path: str):
        def on_apply(dialog: FilePickerDialog, filename: str, dirname: str):
            dialog.hide()
            print(f"Importing: {dirname}/{filename}")

        dialog = FilePickerDialog(
            "Download Files",
            width=800,
            height=400,
            splitter_offset=260,
            enable_filename_input=False,
            current_directory="Downloads",
            grid_view_scale=1,
            apply_button_label="Import",
            click_apply_handler=lambda filename, dirname: on_apply(dialog, filename, dirname),
            click_cancel_handler=lambda filename, dirname: dialog.hide(),
        )
        dialog.show()

    def destroy(self):
        content_browser = self._content_browser_ref()
        if content_browser:
            content_browser.delete_context_menu("Collect Asset")
            content_browser.delete_context_menu("Convert Asset")
            content_browser.delete_listview_menu("Echo Selected")
            content_browser.delete_import_menu("My Custom Import")
            self._content_browser_ref = None


if __name__ == "__main__":
    DemoContentBrowserClient()
