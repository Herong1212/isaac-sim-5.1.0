## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.ui_test as ui_test
import omni.ui as ui
import omni.kit.app

from typing import List, Dict
from omni.kit.widget.filebrowser import FileBrowserItem
from .extension import get_instance


class ContentBrowserTestHelper:
    """Test helper for the content browser window"""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def toggle_grid_view_async(self, show_grid_view: bool):
        """
        Toggles the list view between the grid and tree layouts.

        Args:
            show_grid_view (bool): If True, set the layout to grid, otherwise tree.

        """
        content_browser = get_instance()
        if content_browser:
            content_browser.toggle_grid_view(show_grid_view)
            await ui_test.human_delay(10)

    async def navigate_to_async(self, url: str):
        """
        Navigates to the given url, expanding all parent directories along the path.

        Args:
            url (str): The url to navigate to.

        """
        content_browser = get_instance()
        if content_browser:
            await content_browser.navigate_to_async(url)

    async def get_item_async(self, url: str) -> FileBrowserItem:
        """
        Retrieves an item by its url.

        Args:
            url (str): Url of the item.

        Returns:
            FileBrowserItem

        """
        content_browser = get_instance()
        if content_browser:
            return await content_browser.api.model.find_item_async(url)
        return None

    async def select_items_async(self, dir_url: str, names: List[str]) -> List[FileBrowserItem]:
        """
        Selects display items by their names.

        Args:
            dir_url (str): Url of the parent folder.
            names (List[str]): Names of items to select.

        Returns:
            List[FileBrowserItem]: List of selected items.

        """
        content_browser = get_instance()
        selections = []
        if content_browser:
            selections = await content_browser.select_items_async(dir_url, names)
            await ui_test.human_delay(10)
        return selections

    async def _focus_treeview_items(self, treeview: ui.TreeView, names: List[str]):
        content_browser = get_instance()
        dir = content_browser.get_current_directory()
        items = await self.select_items_async(dir, names)
        # Treeview can only focus 1 item at a time.
        if len(items) >= 1:
            treeview.selection = []
            treeview.selection = [items[0]]
            treeview.dirty_widgets()
            await omni.kit.app.get_app().next_update_async()

    async def get_treeview_item_async(self, name: str, focus_treeview_items=True) -> ui_test.query.WidgetRef:
        """
        Retrieves the ui_test widget of the tree view item by name.

        Args:
            name (str): Label name of the widget.

        Returns:
            ui_test.query.WidgetRef

        """
        widgets = self.get_treeview_items_async([name], focus_treeview_items=focus_treeview_items)
        return widgets[0] if len(widgets) > 0 else None

    async def get_treeview_items_async(self, names: List[str], focus_treeview_items=True) -> ui_test.query.WidgetRef:
        """
        Retrieves the ui_test widgets of the tree view item by a list of names.

        Args:
            names (str): List of label names of their respective widget.
            focus_treeview_items (bool): True to focus on the treeview item, if there are multiple items, focus on the first one. Defaults to True.

        Returns:
            ui_test.query.WidgetRef

        """
        if len(names) > 0:
            tree_view = ui_test.find("Content//Frame/**/TreeView[*].identifier=='content_browser_treeview'")
            widgets = []
            for name in names:
                widget = tree_view.find(f"**/Label[*].text=='{name}'")
                if widget:
                    widgets.append(widget)

            if len(widgets) > 0 and focus_treeview_items:
                # widget.scroll_here doesn't work on tree view, we need to reset the selection to focus on the treeview item
                await self._focus_treeview_items(tree_view.widget, names)

            return widgets
        return []

    async def get_treeview_item_async(self, name: str, focus_treeview_items=True) -> ui_test.query.WidgetRef:
        """
        Retrieves the ui_test widget of the tree view item by name.

        Args:
            name (str): Label name of the widget.

        Returns:
            ui_test.query.WidgetRef

        """
        widgets = await self.get_treeview_items_async([name], focus_treeview_items=focus_treeview_items)
        return widgets[0] if len(widgets) > 0 else None

    async def get_gridview_item_async(self, name: str):
        # get content window widget ref in grid view
        if name:
            grid_view = ui_test.find("Content//Frame/**/VGrid[*].identifier=='content_browser_treeview_grid_view'")
            widget = grid_view.find(f"**/Label[*].text=='{name}'")
            if widget:
                widget.widget.scroll_here(0.5, 0.5)
                await ui_test.human_delay(10)
            return widget
        return None

    async def drag_and_drop_tree_view(self, url: str, names: List[str] = [], drag_target: ui_test.Vec2 = (0,0), human_delay_speed=10, focus_treeview_items=True):
        """
        Drag and drop items from the tree view.

        Args:
            url (str): Url of the parent folder.
            names (List[str]): Names of items to drag.
            drag_target (ui_test.Vec2): Screen location to drop the item.
            focus_treeview_items (bool): True to focus on the treeview item, if there are multiple items, focus on the first one. Defaults to True.

        """
        await self.toggle_grid_view_async(False)
        selections = await self.select_items_async(url, [])
        await ui_test.human_delay(10)
        selections = await self.select_items_async(url, names)
        if selections:
            widgets = await self.get_treeview_items_async([selection.name for selection in selections], focus_treeview_items=focus_treeview_items)
            if len(widgets) > 0:
                await widgets[0].drag_and_drop(drag_target, human_delay_speed=human_delay_speed)
                for i in range(human_delay_speed):
                    await omni.kit.app.get_app().next_update_async()

    async def refresh_current_directory(self):
        content_browser = get_instance()
        if content_browser:
            content_browser.refresh_current_directory()

    async def get_config_menu_settings(self) -> Dict:
        """
        Returns settings from the config menu as a dictionary.

        Returns:
            Dict

        """
        content_browser = get_instance()
        if content_browser:
            widget = content_browser._window._widget
            config_button = widget._tool_bar._config_button
            return config_button.values
        return {}

    async def set_config_menu_settings(self, settings: Dict):
        """
        Writes to settings of the config menu.

        """
        content_browser = get_instance()
        if content_browser:
            widget = content_browser._window._widget
            config_button = widget._tool_bar._config_button
            config_button.values = settings

            # wait for window to update
            await ui_test.human_delay(50)

    async def refresh_directory(self, url: str):
        item = await self.get_item_async(url)
        if item:
            content_browser = get_instance()
            if content_browser:
                content_browser.api.view.refresh_ui(item)

