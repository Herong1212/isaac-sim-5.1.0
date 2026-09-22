# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import sys
import carb
import omni.ui as ui
import asyncio
import omni.client

from omni.kit.mainwindow import get_main_window
from omni.kit.widget.filebrowser import *
from functools import partial


class FileBrowserView:
    SERVER_TYPE_FILESYSTEM = "fileSystem"
    SERVER_TYPE_NUCLEUS = "nucleus"

    def __init__(self, title: str, **kwargs):
        self._title = title
        self._filebrowser = None
        self._item_menu = None
        self._server_menu = None
        self._style = self._init_style()

        self._layout = kwargs.get("layout", LAYOUT_DEFAULT)
        self._tooltip = kwargs.get("tooltip", False)
        self._allow_multi_selection = kwargs.get("allow_multi_selection", True)

    def build_ui(self):
        """ """
        main_window = get_main_window()
        self._menu_bar = main_window.get_main_menu_bar()
        self._menu_bar.set_style(self._style["MenuBar"])
        self._menu_bar.visible = True

        options = [
            ("Split Panes", LAYOUT_SPLIT_PANES, False),
            ("Single Pane Slim", LAYOUT_SINGLE_PANE_SLIM, False),
            ("Single Pane Wide", LAYOUT_SINGLE_PANE_WIDE, False),
            ("Grid View", LAYOUT_SPLIT_PANES, True),
        ]
        with ui.VStack(spacing=10):
            with ui.HStack(height=30):
                collection = ui.RadioCollection()
                for option in options:
                    button = ui.RadioButton(text=option[0], radio_collection=collection, width=120)
                    button.set_clicked_fn(partial(self._build_filebrowser, option[1], option[2]))
                ui.Spacer()
            self._frame = ui.Frame()

        self._build_filebrowser(LAYOUT_DEFAULT)
        asyncio.ensure_future(self._dock_window(self._title, ui.DockPosition.SAME))

    def _build_filebrowser(self, layout: int, show_grid: bool = False):
        if self._filebrowser:
            self._filebrowser.destroy()

        with self._frame:
            self._filebrowser = FileBrowserWidget(
                "Omniverse",
                layout=layout,
                tooltip=self._tooltip,
                allow_multi_selection=self._allow_multi_selection,
                show_grid_view=show_grid,
                mouse_pressed_fn=lambda pane, b, keymod, item, x, y: self._on_mouse_pressed(b, item),
            )
            # Initialize interface with this default list of connections
            self.add_connection("C:", "C:")
            self.add_connection("ov-content", "omniverse://ov-content")

    def add_connection(self, name: str, path: str):
        asyncio.ensure_future(self._add_connection(name, path))

    def _init_style(self) -> dict:
        style = {
            "MenuBar": {
                "background_color": 0xFF23211F,
                "background_selected_color": 0x664F4D43,
                "color": 0xFFAAAAAA,
                "border_width": 0.5,
                "border_color": 0xFF8A8777,
                "padding": 8,
            }
        }
        return style

    def _on_mouse_pressed(self, button: ui.Button, item: FileBrowserItem):
        if button == 1:
            if self._filebrowser.is_root_of_model(item):
                self._show_server_menu(item)
            else:
                self._show_item_menu(item)

    def _show_server_menu(self, item: FileBrowserItem):
        if not self._server_menu:
            self._server_menu = ui.Menu("server-menu")
        self._server_menu.clear()
        with self._server_menu:
            ui.MenuItem("Connection Menu")
        self._server_menu.show()

    def _show_item_menu(self, item: FileBrowserItem):
        if not self._item_menu:
            self._item_menu = ui.Menu("item-menu")
        self._item_menu.clear()
        with self._item_menu:
            ui.MenuItem("Item Info")
            ui.Separator()
            ui.MenuItem(item.name)
            ui.MenuItem(item.path)
        self._item_menu.show()

    def _refresh_ui(self, item: FileBrowserItem = None):
        if self._filebrowser:
            self._filebrowser.refresh_ui(item)

    # ---------------------------------------------- Event Handlers ----------------------------------------------

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

    async def _add_connection(self, name: str, path: str):
        try:
            await self._stat_path(path)
        except Exception as e:
            carb.log_warn(f"{e}")

        if path.startswith("omniverse://"):
            model_creator = NucleusModel
        else:
            model_creator = FileSystemModel

        # Append the new model of desired server type
        server = model_creator(name, path)
        self._filebrowser.add_model_as_subtree(server)

        self._refresh_ui()

    async def _stat_path(self, path: str, timeout: int = 3.0) -> omni.client.ListEntry:
        """ Return stats for path if valid """
        if not path:
            return False, None
        path = path.replace("\\", "/")

        try:
            result, stats = await asyncio.wait_for(omni.client.stat_async(path), timeout=timeout)
        except asyncio.TimeoutError:
            raise RuntimeWarning(f"Error unable to stat '{path}': Timed out after {timeout} secs.")
        except Exception as e:
            raise RuntimeWarning(f"Error unable to stat '{path}': {e}")

        if result != omni.client.Result.OK:
            raise RuntimeWarning(f"Error unable to stat '{path}': {result}")

        return stats


if __name__ == "__main__":
    window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
    window = ui.Window("DemoFileBrowser", width=1000, height=500, flags=window_flags)
    with window.frame:
        view = FileBrowserView("DemoFileBrowser")