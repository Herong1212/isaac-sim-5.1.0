## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["FilePickerTestHelper"]
from typing import List
from omni.kit import ui_test
from omni.kit.widget.filebrowser import TREEVIEW_PANE, LISTVIEW_PANE, FileBrowserItem
from .widget import FilePickerWidget


class FilePickerTestHelper:
    """ Helper class for file picker test"""
    def __init__(self, widget: FilePickerWidget):
        self._widget = widget
        self._widget.api.view.filebrowser.navigation_model.sort_by_field = ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    @property
    def filepicker(self):
        """ Returns the file picker. """
        return self._widget

    async def toggle_grid_view_async(self, show_grid_view: bool):
        """ Toggle the grid view. """
        if self.filepicker and self.filepicker._view:
            self.filepicker._view.toggle_grid_view(show_grid_view)
            await ui_test.human_delay(10)

    async def get_item_async(self, treeview_identifier: str, name: str, pane: int = LISTVIEW_PANE):
        """
         Get item from TreeView or GridView.

         Args:
              treeview_identifier: Identifier of TreeView or GridView.
              name: Name of item to get.
              pane: Pane to return ( LISTVIEW_PANE TREEVIEW_PANE VGrid ).

         Returns:
              An AsyncResult that will resolve to the item if it exists or None if it doesn't exist.
        """
        # Return item from the specified pane, handles both tree and grid views
        if not self.filepicker:
            return
        if name:
            pane_widget = None
            if pane == TREEVIEW_PANE:
                pane_widget = ui_test.find_first(f"{self.filepicker._title}//Frame/**/TreeView[*].identifier=='{treeview_identifier}_folder_view'")
            elif self.filepicker._view.filebrowser.show_grid_view:
                # LISTVIEW selected + showing grid view
                pane_widget = ui_test.find_first(f"{self.filepicker._title}//Frame/**/VGrid[*].identifier=='{treeview_identifier}_grid_view'")
            else:
                # LISTVIEW selected + showing tree view

                pane_widget = ui_test.find_first(f"{self.filepicker._title}//Frame/**/TreeView[*].identifier=='{treeview_identifier}'")


            if pane_widget:
                widget = pane_widget.find_all(f"**/Label[*].text=='{name}'")[0]
                if widget:
                    widget.widget.scroll_here(0.5, 0.5)
                    await ui_test.human_delay(4)
                return widget
        return None

    async def select_items_async(self, url: str, filenames: List[str] = []) -> List[FileBrowserItem]:
        """Helper function to programatically select multiple items in filepicker. Useful in unittests."""
        if not self.filepicker:
            return []
        await self.filepicker.api.navigate_to_async(url)
        return await self.filepicker.api.select_items_async(url, filenames=filenames)

    async def get_pane_async(self, treeview_identifier: str, pane: int = LISTVIEW_PANE):
        """
         Get the pane widget that corresponds to the treeview.

         Args:
              treeview_identifier: Identifier of the treeview to look for.
              pane: Pane to use for the search.

         Returns:
              An widget instance of TreeView or GridView.
        """
        # Return the specified pane widget, handles both tree and grid views
        if not self.filepicker:
            return
        pane_widget = None
        if pane == TREEVIEW_PANE:
            pane_widget = ui_test.find_first(f"{self.filepicker._title}//Frame/**/TreeView[*].identifier=='{treeview_identifier}_folder_view'")
        elif self.filepicker._view.filebrowser.show_grid_view:
            # LISTVIEW selected + showing grid view
            pane_widget = ui_test.find_first(f"{self.filepicker._title}//Frame/**/VGrid[*].identifier=='{treeview_identifier}_grid_view'")
        else:
            # LISTVIEW selected + showing tree view
            pane_widget = ui_test.find_first(f"{self.filepicker._title}//Frame/**/TreeView[*].identifier=='{treeview_identifier}'")

        if pane_widget:
            await ui_test.human_delay(4)
            return pane_widget
        return None