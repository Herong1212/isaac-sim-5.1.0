# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import omni.kit.app
import carb
import carb.settings
import omni.client

from typing import List, Dict
from omni.kit.helper.file_utils import asset_types
from omni.kit.window.filepicker import FilePickerWidget
from omni.kit.widget.filebrowser import FileBrowserItem, LISTVIEW_PANE
from .api import ContentBrowserAPI
from .context_menu import ContextMenu, UdimContextMenu, CollectionContextMenu, BookmarkContextMenu, ConnectionContextMenu, LocalContextMenu
from .tool_bar import ToolBar
from .file_ops import get_file_open_handler, open_file, open_stage, drop_items
from .style import ICON_COMMON_PATH
from . import FILE_TYPE_USD, SETTING_ROOT, SETTING_PERSISTENT_CURRENT_DIRECTORY


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class ContentBrowserWidget(FilePickerWidget):
    """The Content Browser widget"""
    def __init__(self, **kwargs):
        # Retrieve settings
        settings = carb.settings.get_settings()

        # OM-75244: Remember the last browsed directory upon Content Browser open
        kwargs["treeview_identifier"] = kwargs.get('treeview_identifier', None)
        kwargs["settings_root"] = SETTING_ROOT
        kwargs["enable_checkpoints"] = settings.get_as_bool("exts/omni.kit.window.content_browser/enable_checkpoints")
        kwargs["enable_timestamp"] = settings.get_as_bool("exts/omni.kit.window.content_browser/enable_timestamp")
        if not kwargs.get("show_only_collections"):
            kwargs["show_only_collections"] = settings.get("exts/omni.kit.window.content_browser/show_only_collections")

        # Hard-coded configs
        kwargs["allow_multi_selection"] = True
        kwargs["enable_file_bar"] = False
        kwargs["drop_handler"] = lambda dst, src: drop_items(dst, [src])
        kwargs["item_filter_fn"] = self._item_filter_fn
        # OM-77963: Make use of environment variable to disable check for soft-delete features in Content Browser
        kwargs["enable_soft_delete"] = True if os.getenv("OMNI_FEATURE_SOFT_DELETE", "0") == "1" else False
        # OM-124342: Don't show details view in content browser
        kwargs["show_detail_view"] = settings.get_as_bool("/persistent/app/omniverse/content_browser/options_menu/show_details")

        # Additional fields
        self._visible_asset_types = []

        # Inject cusdtomized API
        self._content_browser_api = ContentBrowserAPI()
        kwargs["api"] = self._content_browser_api

        # Initialize and build the widget
        super().__init__("Content", **kwargs)

    def destroy(self):
        super().destroy()
        if self._visible_asset_types:
            self._visible_asset_types.clear()
            self._visible_asset_types = None

    def _build_tool_bar(self):
        """Overrides base builder, injects custom tool bar"""
        self._tool_bar = ToolBar(
            visited_history_size=20,
            current_directory_provider=lambda: self._view.get_root(LISTVIEW_PANE),
            branching_options_handler=self._api.find_subdirs_with_callback,
            apply_path_handler=self._open_and_navigate_to,
            toggle_bookmark_handler=self._api.toggle_bookmark_from_path,
            config_values_changed_handler=lambda _: self._apply_config_options(),
            filter_values_changed_handler=lambda _: self._apply_filter_options(),
            begin_edit_handler=self._on_begin_edit,
            prefix_separator="://",
            search_delegate=self._default_search_delegate,
            enable_soft_delete=self._enable_soft_delete,
        )

    def _build_checkpoint_widget(self):
        """Overrides base builder, adds items to context menu"""
        super()._build_checkpoint_widget()

        # Sets checkpoint widget for future context menu registration.
        self._content_browser_api._set_checkpoint_widget(self._checkpoint_widget)

        # Add context menu to checkpoints
        def on_restore_checkpoint(cp: "CheckpointItem", model: "CheckpointModel"):
            path = model.get_url()
            restore_path = path + "?" + cp.entry.relative_path
            model.restore_checkpoint(path, restore_path)

        # Create checkpoints context menu
        self._checkpoint_widget.add_context_menu(
            "Open",
            f"{ICON_COMMON_PATH}/icoOpen.svg",
            lambda menu, cp: (open_file(cp.get_full_url()) if cp else None),
            None,
            index=0,
        )
        self._checkpoint_widget.add_context_menu(
            "Open With Payloads Disabled",
            f"{ICON_COMMON_PATH}/icoOpenPayloadsDisabled.svg",
            lambda menu, cp: (open_file(cp.get_full_url(), load_all=False) if cp else None),
            None,
            index=1,
        )
        self._checkpoint_widget.add_context_menu(
            "", "", None, None,
            index=98,
        )
        self._checkpoint_widget.add_context_menu(
            "Restore Checkpoint",
            f"{ICON_COMMON_PATH}/icoRestore.svg",
            lambda menu, cp: on_restore_checkpoint(cp, self._checkpoint_widget._model),
            lambda menu, cp: 1 if (cp and cp.get_relative_path()) else 0,
            index=99,
        )

        # Open checkpoint file on double click
        self._checkpoint_widget.set_mouse_double_clicked_fn(
            lambda b, k, cp: (open_file(cp.get_full_url()) if cp else None))

    def _build_context_menus(self):
        """Overrides base builder, injects custom context menus"""
        self._context_menus = dict()
        self._context_menus['item'] = ContextMenu(view=self._view, checkpoint=self._checkpoint_widget)
        self._context_menus['list_view'] = ContextMenu(view=self._view, checkpoint=self._checkpoint_widget)
        self._context_menus['collection'] = CollectionContextMenu(view=self._view)
        self._context_menus['connection'] = ConnectionContextMenu(view=self._view)
        self._context_menus['bookmark'] = BookmarkContextMenu(view=self._view)
        self._context_menus['udim'] = UdimContextMenu(view=self._view)
        self._context_menus['local'] = LocalContextMenu(view=self._view)

        # Register open handler for usd files
        if self._api:
            self._api.add_file_open_handler("usd", open_stage, FILE_TYPE_USD)

    def _get_mounted_servers(self) -> Dict:
        """Overrides base getter, returns mounted server dict from settings"""
        # OM-85963 Fixes flaky unittest: test_mount_default_servers.  Purposely made this a function in order to inject test data.
        settings = carb.settings.get_settings()
        mounted_servers = {}
        try:
            mounted_servers = settings.get_settings_dictionary("exts/omni.kit.window.content_browser/mounted_servers").get_dict()
        except Exception:
            pass
        # OM-71835: Auto-connect server specified in the setting. We normally don't make the connection on startup
        # due to possible delays; however, we make this exception to facilitate the streaming workflows.
        return mounted_servers, True

    def _on_mouse_double_clicked(self, pane: int, button: int, key_mod: int, item: FileBrowserItem):
        if not item:
            return
        if button == 0 and not item.is_folder:
            if self._timestamp_widget:
                url = self._timestamp_widget.get_timestamp_url(item.path)
            else:
                url = item.path

            open_file(url)

    def _on_selection_changed(self, pane: int, selected: List[FileBrowserItem] = []):
        super()._on_selection_changed(pane, selected)

        if self._api:
            self._api._notify_selection_subs(pane, selected)

        # OM-75244: record the last browsed directory
        settings = carb.settings.get_settings()
        settings.set(SETTING_PERSISTENT_CURRENT_DIRECTORY, self._current_directory)

    def _open_and_navigate_to(self, url: str):
        if not url:
            return
        # Make sure url is normalized before trying to open as file.
        url = omni.client.normalize_url(url.strip())
        if get_file_open_handler(url):
            # If there's a suitable file open handler then execute in a separate thread
            open_file(url)
        # Navigate to the file location
        self._api.navigate_to(url)

    def _apply_filter_options(self):
        map_filter_options = {
            "audio": asset_types.ASSET_TYPE_SOUND,
            "materials": asset_types.ASSET_TYPE_MATERIAL,
            "scripts": asset_types.ASSET_TYPE_SCRIPT,
            "textures": asset_types.ASSET_TYPE_IMAGE,
            "usd": asset_types.ASSET_TYPE_USD,
            "volumes": asset_types.ASSET_TYPE_VOLUME,
        }

        visible_types = []
        settings = self._tool_bar.filter_values
        for label, visible in settings.items():
            if visible:
                visible_types.append(map_filter_options[label])

        self._visible_asset_types = visible_types
        self._refresh_ui()

    def _item_filter_fn(self, item: FileBrowserItem) -> bool:
        """
        Default item filter callback. Returning True means the item is visible.

        Args:
            item (:obj:`FileBrowseritem`): Item in question.

        Returns:
            bool

        """
        # Show items of unknown asset types?
        asset_type = asset_types.get_asset_type(item.path)

        if not self._visible_asset_types:
            # Visible asset types not specified
            if asset_type == asset_types.ASSET_TYPE_UNKNOWN:
                return self._show_unknown_asset_types
            else:
                return True

        return asset_type in self._visible_asset_types
