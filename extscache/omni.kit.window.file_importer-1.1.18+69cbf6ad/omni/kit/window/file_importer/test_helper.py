## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import asyncio
import omni.kit.app
import omni.kit.ui_test as ui_test

from typing import List, Dict, Callable
from omni.kit.widget.filebrowser import FileBrowserItem, LISTVIEW_PANE, TREEVIEW_PANE
from .extension import get_instance


class FileImporterTestHelper:
    """Test helper for the file import dialog"""

    # NOTE Since the file dialog is a singleton, use an async lock to ensure mutex access in unit tests.
    # During run-time, this is not a issue because the dialog is effectively modal.
    __async_lock = asyncio.Lock()

    async def __aenter__(self):
        await self.__async_lock.acquire()
        return self

    async def __aexit__(self, *args):
        self.__async_lock.release()

    async def wait_for_popup(self, timeout_frames: int = 20):
        """Waits for dialog to be ready"""
        file_importer = get_instance()
        if file_importer:
            for _ in range(timeout_frames):
                if file_importer.is_ui_ready:
                    for _ in range(4):
                        # Wait a few extra frames to settle before returning
                        await omni.kit.app.get_app().next_update_async()
                    return
                await omni.kit.app.get_app().next_update_async()
        raise Exception("Error: The file import window did not open.")

    async def click_apply_async(self, filename_url: str = None):
        """Helper function to progammatically execute the apply callback.  Useful in unittests"""
        file_importer = get_instance()
        if file_importer:
            file_importer.click_apply(filename_url=filename_url)
            await omni.kit.app.get_app().next_update_async()

    async def click_cancel_async(self, cancel_handler: Callable[[str, str], None] = None):
        """Helper function to progammatically execute the cancel callback.  Useful in unittests"""
        file_importer = get_instance()
        if file_importer:
            file_importer.click_cancel(cancel_handler=cancel_handler)
            await omni.kit.app.get_app().next_update_async()

    async def select_items_async(self, dir_url: str, names: List[str]) -> List[FileBrowserItem]:
        file_importer = get_instance()
        selections = []
        if file_importer:
            selections = await file_importer.select_items_async(dir_url, names)
        return selections

    async def get_config_menu_settings(self) -> Dict:
        """
        Returns settings from the config menu as a dictionary.

        Returns:
            Dict

        """
        import omni.kit.ui_test as ui_test
        import omni.ui as ui

        file_importer = get_instance()
        if file_importer:
            widget = file_importer._dialog._widget
            config_button = widget._tool_bar._config_button
            return config_button.values
        return {}

    async def set_config_menu_settings(self, settings: Dict):
        """
        Writes to settings of the config menu.

        """
        import omni.kit.ui_test as ui_test
        import omni.ui as ui

        file_importer = get_instance()
        if file_importer:
            widget = file_importer._dialog._widget
            config_button = widget._tool_bar._config_button
            config_button.values = settings

            # wait for dialog to update
            await ui_test.human_delay(50)

    async def get_item_async(self, treeview_identifier: str, name: str, pane: int = LISTVIEW_PANE):
        # Return item from the specified pane, handles both tree and grid views
        file_importer = get_instance()
        if not file_importer:
            return
        if name:
            pane_widget = None
            if pane == TREEVIEW_PANE:
                pane_widget = ui_test.find_all(f"{file_importer._title}//Frame/**/TreeView[*].identifier=='{treeview_identifier}_folder_view'")
            elif file_importer._dialog._widget._view.filebrowser.show_grid_view:
                # LISTVIEW selected + showing grid view
                pane_widget = ui_test.find_all(f"{file_importer._title}//Frame/**/VGrid[*].identifier=='{treeview_identifier}_grid_view'")
            else:
                # LISTVIEW selected + showing tree view
                pane_widget = ui_test.find_all(f"{file_importer._title}//Frame/**/TreeView[*].identifier=='{treeview_identifier}'")

            if pane_widget:
                widget = pane_widget[0].find(f"**/Label[*].text=='{name}'")
                if widget:
                    widget.widget.scroll_here(0.5, 0.5)
                    await ui_test.human_delay(4)
                return widget
        return None