# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ToolBar"]
from typing import Optional

import omni.ui as ui
import carb.settings

from omni.kit.widget.browser_bar import BrowserBar
from omni.kit.window.popup_dialog import InputDialog, MessageDialog, FormDialog
from omni.kit.widget.filebrowser import FileBrowserItem

from carb import log_warn
from .style import get_style, ICON_PATH
from .config_button import ConfigButton


class ToolBar:
    SAVED_SETTINGS_OPTIONS_MENU = "/persistent/app/omniverse/filepicker/options_menu"

    """
    Build a ToolBar for file picker widget.

    Keyword Arguments:
        current_directory_provider (Optional[Callable]): A provider for the current directory.
        branching_options_handler (Optional[Callable]): A handler for branching options.
        apply_path_handler (Optional[Callable]): A handler for applying a path.
        toggle_bookmark_handler (Optional[Callable]): A handler for toggling bookmarks.
        config_values_changed_handler (Optional[Callable]): A handler for handling changes in configuration values.
        begin_edit_handler (Optional[Callable]): A handler for starting an edit operation.
        prefix_separator (Optional[str]): A separator for prefixes.
        enable_soft_delete (bool): A flag indicating whether soft delete is enabled (default: False).
        search_delegate (Optional[SearchDelegate]): A delegate for search functionality.
        modal (bool): A flag indicating whether the toolbar is modal (default: False).
    """
    def __init__(self, **kwargs):
        self._browser_bar: BrowserBar = None
        self._bookmark_button: ui.Button = None
        self._bookmarked: bool = False
        self._config_button: Optional[ConfigButton] = None

        self._current_directory_provider = kwargs.get("current_directory_provider", None)
        self._branching_options_handler = kwargs.get("branching_options_handler", None)
        self._apply_path_handler = kwargs.get("apply_path_handler", None)
        self._toggle_bookmark_handler = kwargs.get("toggle_bookmark_handler", None)
        self._config_values_changed_handler = kwargs.get("config_values_changed_handler", None)
        self._begin_edit_handler = kwargs.get("begin_edit_handler", None)
        self._prefix_separator = kwargs.get("prefix_separator", None)
        self._enable_soft_delete = kwargs.get("enable_soft_delete", False)
        self._search_delegate = kwargs.get("search_delegate", None)
        self._modal = kwargs.get("modal", False)
        self._search_frame = None
        self._build_ui()

    def _build_ui(self):
        with ui.HStack(height=0, style=get_style(), style_type_name_override="ToolBar"):
            with ui.ZStack():
                with ui.HStack():
                    ui.Spacer(width=48)
                    ui.Rectangle(style_type_name_override="ToolBar.Field")
                with ui.HStack():
                    with ui.VStack():
                        ui.Spacer()
                        self._browser_bar = BrowserBar(
                            visited_history_size=20,
                            branching_options_handler=self._branching_options_handler,
                            apply_path_handler=self._apply_path_handler,
                            prefix_separator=self._prefix_separator,
                            modal=self._modal,
                            begin_edit_handler=self._begin_edit_handler,
                        )
                        ui.Spacer()
                    with ui.VStack(width=20):
                        ui.Spacer()
                        self._bookmark_button = ui.Button(
                            image_url=f"{ICON_PATH}/bookmark_grey.svg",
                            image_width=18,
                            image_height=18,
                            height=18,
                            style_type_name_override="ToolBar.Button",
                            clicked_fn=lambda: self._on_toggle_bookmark(self._current_directory_provider()),
                        )
                        ui.Spacer()

            ui.Spacer(width=2)
            with ui.HStack(width=300):
                self._search_frame = ui.Frame()
                if self._search_delegate:
                    with self._search_frame:
                        self._search_delegate.build_ui()
                else:
                    self._search_frame.visible = False

            self._build_widgets()

            with ui.VStack(width=0):
                ui.Spacer()
                self._config_button = ConfigButton(self._enable_soft_delete, on_value_changed_fn=self._config_values_changed_handler)
                ui.Spacer()

    def _build_widgets(self):
        # For Content window to build filter button
        pass

    def _on_toggle_bookmark(self, item: FileBrowserItem):
        if not item:
            return

        def on_okay_clicked(dialog: InputDialog, item: FileBrowserItem, is_bookmark: bool):
            if self._toggle_bookmark_handler:
                if is_bookmark:
                    name = dialog.get_value("name")
                    url = dialog.get_value("address")
                else:
                    name = item.name
                    url = item.path
                self._toggle_bookmark_handler(name, url, is_bookmark, is_folder=item.is_folder)
            dialog.hide()

        if self._bookmarked:
            dialog = MessageDialog(
                title="Delete bookmark",
                width=400,
                message=f"Are you sure about deleting the bookmark '{item.path}'?",
                ok_handler=lambda dialog, item=item: on_okay_clicked(dialog, item, False),
                ok_label="Yes",
                cancel_label="No",
            )
        else:
            default_name = (item.path or "").rstrip("/").rsplit("/")[-1]
            field_defs = [
                FormDialog.FieldDef("name", "Name:  ", ui.StringField, default_name, True),
                FormDialog.FieldDef("address", "Address:  ", ui.StringField, item.path),
            ]
            dialog = FormDialog(
                title="Add bookmark",
                width=400,
                ok_handler=lambda dialog, item=item: on_okay_clicked(dialog, item, True),
                field_defs=field_defs,
            )
        dialog.show(offset_x=-1, offset_y=24, parent=self._bookmark_button)

    @property
    def config_values(self):
        """
        Returns the values of the configuration button.

        Returns:
            Dict[str, bool]:  A dictionary of the configuration button values
        """
        return self._config_button.values if self._config_button else {}

    def set_config_value(self, name: str, value: bool):
        """
        Set a value for a config button.

        Args:
            name (str): The name of the value to set.
            value (bool): The value to set for the name.
        """
        if self._config_button:
            values = self._config_button.values
            values[name] = value
            self._config_button.values = values

    @property
    def path(self) -> str:
        """
        Path to the currently displayed file.

        Returns:
            str: Path to the currently displayed file or None if there is no browser bar.
        """
        if self._browser_bar:
            return self._browser_bar.path
        return None

    def set_path(self, path: str):
        """
        Sets the path to search for.

        Args:
            path (str): The path to search
        """
        if self._browser_bar:
            self._browser_bar.set_path(path)
            path = self._browser_bar.path  # In case browser bar modifies the path str in any way
        if self._search_delegate:
            self._search_delegate.search_dir = path

    @property
    def bookmarked(self) -> bool:
        """
        Whether or not the current path is bookmarked.

        Returns:
            bool: True if the current path is bookmarked else False.
        """
        return self._bookmarked

    def set_bookmarked(self, true_false: bool):
        """
        Set whether or not the bookmark image should be shown.

        Args:
            true_false (bool): True if the bookmark image should be shown else False.
        """
        self._bookmarked = true_false
        if self._bookmarked:
            self._bookmark_button.image_url = f"{ICON_PATH}/bookmark.svg"
        else:
            self._bookmark_button.image_url = f"{ICON_PATH}/bookmark_grey.svg"

    def set_search_delegate(self, delegate):
        """
        Sets a custom search delegate for the tool bar.

        Args:
            delegate (:obj:`SearchDelegate`): Object that creates the search widget.
        """
        if delegate is None:
            self._search_frame.visible = False
        else:
            with self._search_frame:
                try:
                    delegate.build_ui()
                    delegate.search_dir = self._browser_bar.path if self._browser_bar else None
                    self._search_delegate = delegate
                    self._search_frame.visible = True
                except Exception:
                    log_warn("Failed to build search widget")

    def destroy(self):
        """ Destroy the widget. """
        if self._browser_bar:
            self._browser_bar.destroy()
            self._browser_bar = None
        # NOTE: Dereference but do not call destroy on the search delegate because we don't own the object.
        self._search_delegate = None
        self._search_frame = None
        if self._config_button:
            self._config_button.destroy()
            self._config_button = None
        self._bookmark_button = None

        self._current_directory_provider = None
        self._branching_options_handler = None
        self._apply_path_handler = None
        self._toggle_bookmark_handler = None
        self._config_values_changed_handler = None
        self._begin_edit_handler = None
