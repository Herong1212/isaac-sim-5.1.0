# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["FilePickerWidget"]
import os
import asyncio
import omni.kit.app
import omni.ui as ui
import omni.client
import carb.settings
from carb.eventdispatcher import get_eventdispatcher

from functools import partial
from carb import log_warn
from omni.kit.widget.filebrowser import (
    FileBrowserItem,
    FileBrowserUdimItem,
    LAYOUT_SPLIT_PANES,
    TREEVIEW_PANE,
    LISTVIEW_PANE,
)
try:
    from omni.kit.widget.versioning import CheckpointWidget
    have_versioning = True
except ModuleNotFoundError:
    have_versioning = False
from typing import List, Tuple, Dict, Callable
from .api import FilePickerAPI
from .context_menu import ContextMenu, CollectionContextMenu, BookmarkContextMenu, LocalContextMenu, UdimContextMenu, ConnectionContextMenu
from .tool_bar import ToolBar
from .file_bar import FileBar
from .model import FilePickerModel
from .style import get_style, ICON_COMMON_PATH
from .utils import exec_after_redraw, get_user_folders_dict, SingletonTask
from .detail_view import DetailView
from .option_box import OptionBox
from .view import FilePickerView
from .timestamp import TimestampWidget
from . import UI_READY_GLOBAL_EVENT, SETTING_ROOT

SHOW_ONLY_COLLECTIONS = "/exts/omni.kit.window.filepicker/show_only_collections"
DETAIL_WIDTH_INIT = "/exts/omni.kit.window.filepicker/detail_width_init"
DETAIL_WIDTH_MIN = "/exts/omni.kit.window.filepicker/detail_width_min"
DETAIL_WIDTH_MAX = "/exts/omni.kit.window.filepicker/detail_width_max"


class FilePickerWidget:
    """
    An embeddable UI widget for browsing the filesystem and taking action on a selected file.
    Includes a browser bar for keyboard input with auto-completion for navigation of the tree
    view.  For similar but different options, see also :obj:`FilePickerDialog` and :obj:`FilePickerView`.

    Args:
        title (str): Widget title. Default None.

    Keyword Args:
        layout (int): The overall layout of the window, one of: {LAYOUT_SPLIT_PANES, LAYOUT_SINGLE_PANE_SLIM,
            LAYOUT_SINGLE_PANE_WIDE, LAYOUT_DEFAULT}. Default LAYOUT_SPLIT_PANES.
        current_directory (str): View is set to display this directory. Default None.
        current_filename (str): Filename is set to this value. Default None.
        splitter_offset (int): Position of vertical splitter bar. Default 300.
        show_grid_view (bool): Displays grid view in the intial layout. Default True.
        grid_view_scale (int): Scales grid view, ranges from 0-5. Default 2.
        show_only_collections (List[str]): List of collections to display, any combination of ["bookmarks",
            "omniverse", "my-computer"]. If None, then all are displayed. Default None.
        allow_multi_selection (bool): Allows multiple selections. Default False.
        click_apply_handler (Callable): Function that will be called when the user accepts
            the selection. Function signature:
            void apply_handler(file_name: str, dir_name: str).
        click_cancel_handler (Callable): Function that will be called when the user clicks
            the cancel button. Function signature:
            void cancel_handler(file_name: str, dir_name: str).
        apply_button_label (str): Alternative label for the apply button. Default "Okay".
        cancel_button_label (str): Alternative label for the cancel button. Default "Cancel".
        enable_file_bar (bool): Enables/disables file bar.  Default True.
        enable_filename_input (bool): Enables/disables filename input. Default True.
        file_postfix_options (List[str]): A list of filename postfix options.  Default [].
        file_extension_options (List[Tuple[str, str]]): A list of filename extension options.  Each list
            element is an (extension name, description) pair, e.g. (".usdc", "Binary format").  Default [].
        item_filter_options (List[str]): OBSOLETE. Use file_postfix_options & file_extension_options instead.
            A list of filter options to determine which files should be listed.  For example: ['usd', 'wav']. Default None.
        item_filter_fn (Callable): This user function should return True if the given tree view
            item is visible, False otherwise. To base the decision on which filter option is
            currently chosen, use the attribute filepicker.current_filter_option.  Function
            signature: bool item_filter_fn(item: :obj:`FileBrowserItem`)
        error_handler (Callable): OBSOLETE. This function is called with error messages when appropriate.
            It provides the calling app a way to display errors on top of writing them to the
            console window. Function signature: void error_handler(message: str).
        show_detail_view (bool): Display the details pane.
        enable_versioning_pane (bool): OBSOLETE. Use enable_checkpoints instead.
        enable_checkpoints (bool): Whether the checkpoints, a.k.a. versioning pane should be displayed. Default False.
        enable_timestamp (bool): Whether the show timestamp panel. need show with checkpoint, Default False.
        options_pane_build_fn (Callable[[List[FileBrowserItem]], bool]): OBSOLETE, add options in a detail frame instead.
        options_pane_width (Union[int, omni.ui.Percent]): OBSOLETE.
        selection_changed_fn (Callable[[List[FileBrowserItem]]]): Selections has changed.
        treeview_identifier (str): widget identifier for treeview, only used by tests.
        enable_tool_bar (bool): Enables/disables tool bar.  Default True.
        enable_zoombar (bool): Enables/disables filename input. Default True.
        save_grid_view (bool): Save grid view mode if toggled. Default True.
        apply_path_handler (Callable): Function that will be called when the user entered
            in the path field. Function Signature:
            void apply_path_handler(url: str)
    """

    def __init__(self, title: str, **kwargs):
        self._title = title
        self._api = None
        self._view = None
        self._tool_bar = None
        self._file_bar = None
        self._detail_pane = None
        self._detail_view = None
        self._detail_splitter = None
        self._context_menus = dict()
        self._checkpoint_widget = None
        self._option_box = None     # OBSOLETE. Provided for backward compatibility
        self._timestamp_widget = None

        settings = carb.settings.get_settings()
        self._layout = kwargs.get("layout", LAYOUT_SPLIT_PANES)
        # OM-103188: Add default open directory to filepicker
        self._current_directory = kwargs.get("current_directory")
        if not self._current_directory:
            self._current_directory = settings.get("/exts/omni.kit.window.filepicker/default_open_directory")
        self._current_filename = kwargs.get("current_filename", None)

        # OM-66270: Record show grid view and grid view scale settings in between sessions
        self._settings_root = kwargs.get("settings_root", SETTING_ROOT)
        show_grid_view = settings.get(f"/persistent{self._settings_root}show_grid_view")
        grid_view_scale = settings.get(f"/persistent{self._settings_root}grid_view_scale")
        if show_grid_view is None:
            show_grid_view = settings.get_as_bool(f"{self._settings_root}/show_grid_view") or True
        if grid_view_scale is None:
            grid_view_scale = 2
        self._show_grid_view = kwargs.get("show_grid_view", show_grid_view)
        self._grid_view_scale = kwargs.get("grid_view_scale", grid_view_scale)
        self._save_grid_view = kwargs.get("save_grid_view", True)
        self._detail_width_init = settings.get(DETAIL_WIDTH_INIT)
        self._detail_width_min = settings.get(DETAIL_WIDTH_MIN)
        self._detail_width_max = settings.get(DETAIL_WIDTH_MAX)

        self._show_only_collections = kwargs.get("show_only_collections", None)
        if not self._show_only_collections:
            # If not set show_only_collections, use the setting value instead
            self._show_only_collections = settings.get(SHOW_ONLY_COLLECTIONS)
        self._allow_multi_selection = kwargs.get("allow_multi_selection", False)
        self._apply_button_label = kwargs.get("apply_button_label", "Okay")
        self._click_apply_handler = kwargs.get("click_apply_handler", None)
        self._cancel_button_label = kwargs.get("cancel_button_label", "Cancel")
        self._click_cancel_handler = kwargs.get("click_cancel_handler", None)
        self._enable_file_bar = kwargs.get("enable_file_bar", True)
        self._enable_tool_bar = kwargs.get("enable_tool_bar", True)
        self._enable_zoombar = kwargs.get("enable_zoombar", True)
        self._enable_filename_input = kwargs.get("enable_filename_input", True)
        self._focus_filename_input = kwargs.get("focus_filename_input", False)
        self._file_postfix_options = kwargs.get("file_postfix_options", [])
        self._current_file_postfix = kwargs.get("current_file_postfix", None)
        self._file_extension_options = kwargs.get("file_extension_options", [])
        self._filename_changed_handler = kwargs.get("filename_changed_handler", None)
        self._current_file_extension = kwargs.get("current_file_extension", None)
        self._item_filter_options = kwargs.get("item_filter_options", None)
        self._item_filter_fn = kwargs.get("item_filter_fn", None)
        self._show_detail_view = kwargs.get("show_detail_view", True)
        self._enable_checkpoints = have_versioning and (kwargs.get("enable_checkpoints", False) or kwargs.get("enable_versioning_pane", False))
        self._enable_timestamp = kwargs.get("enable_timestamp", False) and self._enable_checkpoints
        self._options_pane_build_fn = kwargs.get("options_pane_build_fn", None)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._treeview_identifier = kwargs.get("treeview_identifier", None)
        self._drop_handler = kwargs.get("drop_handler", None)
        self._enable_soft_delete = kwargs.get("enable_soft_delete", False)
        self._modal = kwargs.get("modal", False)
        try:
            from omni.kit.widget.search_delegate import SearchField
            self._default_search_delegate = SearchField(self._on_search)
        except ModuleNotFoundError:
            self._default_search_delegate = None
        self._init_view_task = None
        self._show_unknown_asset_types = False
        self._show_thumbnails_folders = False

        window = kwargs.get("window", None)
        if window:
            self._window_size = (window.width, window.height)
        else:
            self._window_size = (1000, 600)  # Set to default window size if window not specified
        self._splitter_offset = (kwargs.get("splitter_offset", 300), self._detail_width_init)

        self._model = kwargs.get("model", FilePickerModel())
        self._api = kwargs.get("api", FilePickerAPI())
        self._apply_path_handler = kwargs.get('apply_path_handler', self._api.navigate_to)
        self._build_ui()

    @property
    def api(self) -> FilePickerAPI:
        """:obj:`FilePickerAPI`: Provides API methods to this widget."""
        return self._api

    @property
    def model(self):
        """ Returns the model of this widget."""
        return self._model

    @property
    def file_bar(self) -> FileBar:
        """:obj:`FileBar`: Returns the file bar widget."""
        return self._file_bar

    @property
    def current_filter_option(self) -> int:
        """OBSOLETE int: Index of current filter option, range 0 .. num_filter_options."""
        return self._file_bar.current_filter_option if self._file_bar else -1

    def set_item_filter_fn(self, item_filter_fn: Callable[[str], bool]):
        """
        Sets the item filter function.

        Args:
            item_filter_fn (Callable): Signature is bool fn(item: FileBrowserItem)

        """
        self._item_filter_fn = item_filter_fn

    def set_click_apply_handler(self, click_apply_handler: Callable[[str, str], None]):
        """
        Sets the function to execute upon clicking apply.

        Args:
            click_apply_handler (Callable): Callback with filename being the name of the file, and dirname being the containing directory path with an ending slash.
                Signature is fn(filename: str, dirname: str) -> None

        """
        self._click_apply_handler = click_apply_handler
        if self._file_bar:
            self._file_bar.set_click_apply_handler(self._click_apply_handler)

    def get_selected_filename_and_directory(self) -> Tuple[str, str]:
        """ Get the current directory and filename that has been selected or entered into the filename field"""
        if self._file_bar:
            return self._file_bar.filename, self._file_bar.directory
        return "", ""

    def destroy(self):
        """Destructor."""
        self._selection_changed_fn = None
        self._options_pane_build_fn = None
        self._filename_changed_handler = None
        if self._init_view_task:
            self._init_view_task.cancel()
            self._init_view_task = None
        if self._initial_navigation_task:
            self._initial_navigation_task.cancel()
            self._initial_navigation_task = None
        if self._api:
            self._api.destroy()
            self._api = None
        if self._tool_bar:
            self._tool_bar.destroy()
            self._tool_bar = None
        if self._file_bar:
            self._file_bar.destroy()
            self._file_bar = None
        if self._detail_view:
            self._detail_view.destroy()
            self._detail_view = None
        self._detail_pane = None
        self._detail_splitter = None
        if self._model:
            self._model.destroy()
            self._model = None
        if self._view:
            self._view.destroy()
            self._view = None
        if self._context_menus:
            self._context_menus.clear()
        if self._checkpoint_widget:
            self._checkpoint_widget.destroy()
            self._checkpoint_widget = None
        if self._option_box:
            self._option_box.destroy()
            self._option_box = None
        if self._timestamp_widget:
            self._timestamp_widget.destroy()
            self._timestamp_widget = None
        self._item_filter_fn = None
        self._click_apply_handler = None
        self._click_cancel_handler = None
        self._window = None
        self._ui_ready_event_sub = None

    def _build_ui(self):
        with ui.VStack(spacing=2, style=get_style()):
            if self._enable_tool_bar:
                self._build_tool_bar()

            with ui.HStack():
                with ui.ZStack():
                    with ui.HStack():
                        self._build_filepicker_view()
                        ui.Spacer(width=2)

                    self._detail_splitter = ui.Placer(
                        offset_x=self._window_size[0]-self._splitter_offset[1],
                        drag_axis=ui.Axis.X,
                        draggable=True,
                    )
                    with self._detail_splitter:
                        ui.Rectangle(width=4, style_type_name_override="Splitter")
                    self._detail_splitter.set_offset_x_changed_fn(self._on_detail_splitter_dragged)

                # Right panel
                self._detail_pane = ui.VStack()
                with self._detail_pane:
                    self._build_detail_view()

            if self._enable_file_bar:
                self._build_file_bar()

        # Create context menus
        self._build_context_menus()

        # The API object encapsulates the API methods.
        self._api.model = self._model
        self._api.view = self._view
        self._api.tool_bar = self._tool_bar
        self._api.file_view = self._file_bar
        self._api.detail_view = self._detail_view
        self._api.context_menu = self._context_menus.get('item')
        self._api.listview_menu = self._context_menus.get('list_view')

        if self._show_detail_view and self._tool_bar:
            self._tool_bar.set_config_value("show_details", True)

        self._init_view_task = exec_after_redraw(lambda d=self._current_directory, f=self._current_filename: self._init_view(d, f))
        self._initial_navigation_task = None
        # Listen for ui ready event
        self._ui_ready = False
        self._ui_ready_event_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.window.filepicker.widget",
            event_name=UI_READY_GLOBAL_EVENT,
            on_event=self._on_ui_ready
        )

    def _build_filepicker_view(self):
        self._view = FilePickerView(
            "filepicker",
            layout=self._layout,
            splitter_offset=self._splitter_offset[0],
            show_grid_view=self._show_grid_view,
            show_recycle_widget=self._enable_soft_delete,
            grid_view_scale=self._grid_view_scale,
            on_toggle_grid_view_fn=self._on_toggle_grid_view if self._save_grid_view else None,
            on_scale_grid_view_fn=self._on_scale_grid_view,
            show_only_collections=self._show_only_collections,
            tooltip=True,
            allow_multi_selection=self._allow_multi_selection,
            mouse_pressed_fn=self._on_mouse_pressed,
            mouse_double_clicked_fn=self._on_mouse_double_clicked,
            selection_changed_fn=self._on_selection_changed,
            drop_handler=self._drop_handler,
            item_filter_fn=self._item_filter_handler,
            icon_provider=self._model.get_icon,
            thumbnail_provider=self._model.get_thumbnail,
            badges_provider=self._model.get_badges,
            treeview_identifier=self._treeview_identifier,
            enable_zoombar=self._enable_zoombar,
        )
        self._model.collections = self._view.collections

    def _build_tool_bar(self):
        self._tool_bar = ToolBar(
            visited_history_size=20,
            current_directory_provider=lambda: self._view.get_root(LISTVIEW_PANE),
            branching_options_handler=self._api.find_subdirs_with_callback,
            apply_path_handler=self._apply_path_handler,
            toggle_bookmark_handler=self._api.toggle_bookmark_from_path,
            config_values_changed_handler=lambda _: self._apply_config_options(),
            begin_edit_handler=self._on_begin_edit,
            prefix_separator="://",
            search_delegate=self._default_search_delegate,
            enable_soft_delete=self._enable_soft_delete,
            modal=self._modal,
        )

    def _build_detail_view(self):
        self._detail_view = DetailView()
        if self._options_pane_build_fn:
            # NOTE: DEPRECATED - Left here for backwards compatibility
            def build_option_box(build_fn: Callable):
                self._option_box = OptionBox.create_option_box(build_fn)

            self._detail_view.add_detail_frame(
                "Options", None,
                partial(build_option_box, self._options_pane_build_fn),
                selection_changed_fn=lambda selected: OptionBox.on_selection_changed(self._option_box, selected),
                destroy_fn=lambda selected: OptionBox.delete_option_box(self._option_box, selected)
            )

        if self._enable_checkpoints:
            self._detail_view.add_detail_frame(
                "Checkpoints", None,
                self._build_checkpoint_widget,
                selection_changed_fn=lambda selected: CheckpointWidget.on_model_url_changed(self._checkpoint_widget, selected),
                destroy_fn=lambda: CheckpointWidget.delete_checkpoint_widget(self._checkpoint_widget))

        if self._enable_timestamp:
            def on_timestamp_check_changed(full_url: str):
                self._api.set_filename(full_url)

            def build_timestamp_widget():
                self._timestamp_widget = TimestampWidget.create_timestamp_widget()
                self._timestamp_widget.add_on_check_changed_fn(on_timestamp_check_changed)

            self._detail_view.add_detail_frame(
                "TimeStamp", None,
                build_timestamp_widget,
                selection_changed_fn=lambda selected: TimestampWidget.on_selection_changed(self._timestamp_widget, selected),
                destroy_fn=lambda: TimestampWidget.delete_timestamp_widget(self._timestamp_widget))

    def _build_checkpoint_widget(self):
        def on_checkpoint_selection_changed(cp):
            if cp:
                self._api.set_filename(cp.get_full_url())
                if self._timestamp_widget:
                    self._timestamp_widget.check = False

        self._checkpoint_widget = CheckpointWidget.create_checkpoint_widget()
        self._checkpoint_widget.add_on_selection_changed_fn(on_checkpoint_selection_changed)
        if self._timestamp_widget:
            self._checkpoint_widget.set_on_list_checkpoint_fn(self._timestamp_widget.on_list_checkpoint)
            self._timestamp_widget.set_checkpoint_widget(self._checkpoint_widget)

        # Add context menu to checkpoints
        def on_copy_url(cp):
            omni.kit.clipboard.copy(cp.get_full_url() if cp else "")

        def on_copy_version(cp):
            omni.kit.clipboard.copy(cp.comment or "")

        self._checkpoint_widget.add_context_menu(
            "Copy URL",
            f"{ICON_COMMON_PATH}/icoLink.svg",
            lambda menu, cp: on_copy_url(cp),
            None
        )
        self._checkpoint_widget.add_context_menu(
            "Copy Description",
            f"{ICON_COMMON_PATH}/icoCopyPrim.svg",
            lambda menu, cp: on_copy_version(cp),
            lambda menu, cp: 1 if (cp and cp.get_relative_path()) else 0,
        )

    def _build_file_bar(self):
        self._file_bar = FileBar(
            style=get_style(),
            enable_filename_input=self._enable_filename_input,
            filename_changed_handler=self._on_filename_changed,
            file_postfix_options=self._file_postfix_options,
            file_postfix=self._current_file_postfix,
            file_extension_options=self._file_extension_options,
            file_extension=self._current_file_extension,
            item_filter_options=self._item_filter_options,
            filter_option_changed_handler=self._refresh_ui,
            current_directory_provider=self._api.get_current_directory,
            apply_button_label=self._apply_button_label,
            click_apply_handler=self._click_apply_handler,
            cancel_button_label=self._cancel_button_label,
            click_cancel_handler=self._click_cancel_handler,
            focus_filename_input=self._focus_filename_input,
        )

    def _build_context_menus(self):
        # Build context menus
        self._context_menus = dict()
        self._context_menus['item'] = ContextMenu(view=self._view, checkpoint=self._checkpoint_widget)
        self._context_menus['list_view'] = ContextMenu(view=self._view, checkpoint=self._checkpoint_widget)
        self._context_menus['collection'] = CollectionContextMenu(view=self._view)
        self._context_menus['connection'] = ConnectionContextMenu(view=self._view)
        self._context_menus['bookmark'] = BookmarkContextMenu(view=self._view)
        self._context_menus['udim'] = UdimContextMenu(view=self._view)
        self._context_menus['local'] = LocalContextMenu(view=self._view)

    def _init_view(self, current_directory: str, current_filename: str):
        """Initialize the view, runs after the view is ready."""
        # Mount servers
        mounted_servers, make_connection = self._get_mounted_servers()
        if mounted_servers:
            self._api.add_connections(mounted_servers)
            if make_connection:
                # OM-71835: Auto-connect specified server specified in the setting (to facilitate the streaming workflows).
                # Also, because we can only connect one server at a time, and it's done asynchronously, we do only the first
                # in the list.
                server_url = list(mounted_servers.values())[0]
                self._api.connect_server(server_url)

        # Mount local user folders
        user_folders = get_user_folders_dict()
        if user_folders:
            self._view.mount_user_folders(user_folders)

        self._api.subscribe_client_bookmarks_changed()

        self._apply_config_options()

        # Emit UI ready event
        omni.kit.app.queue_event(UI_READY_GLOBAL_EVENT, {"title": self._title})

    async def _initial_navigation_async(self, current_directory: str, current_filename: str):
        url = None
        if current_directory:
            url = current_directory
            if current_filename:
                if not url.endswith('/'):
                    url += '/'
                url += current_filename
        try:
            # OMPE-11887: No files exist under "omniverse://".
            # Navigating to a file under "omniverse://" will treat it as a server and prompt a sign-in dialog.
            # TODO: don't need to change here
            if current_directory != "omniverse://":
                # OMPE-43083: If used for exporter file, the file may not exist and navigate to file will cause unexpected warning,
                # so make sure file exists first
                result, _ = await omni.client.stat_async(url)
                if result == omni.client.Result.OK:
                    await self._api.navigate_to_async(url)
                else:
                    result, _ = await omni.client.stat_async(current_directory)
                    if result == omni.client.Result.OK:
                        await self._api.navigate_to_async(current_directory)

            if current_directory and self._api:
                self._api.set_current_directory(current_directory)
            if current_filename and self._api:
                self._api.set_filename(current_filename)
        except Exception as e:
            log_warn(f"Directory {current_directory} not reachable: {str(e)}")
        # For file importers or cases where we are creating a non-existing file, the navigation would fail so we need to
        # set the current directory and filename regardless
        finally:
            self._initial_navigation_task = None

    def _on_ui_ready(self, event):
        # make sure this is only executed once
        if self._ui_ready:
            return
        title = event["title"]

        if title == self._title:
            self._ui_ready = True

            # OM-49484: Create a cancellable task for initial navigation, and cancel if user browsed to a directory
            if not self._initial_navigation_task or self._initial_navigation_task.done():
                self._initial_navigation_task = asyncio.ensure_future(
                    self._initial_navigation_async(self._current_directory, self._current_filename)
                )

    def _on_begin_edit(self):
        # OM-49484: cancel initial navigation upon user edit for tool bar path field
        self._cancel_initial_navigation()

    def _cancel_initial_navigation(self):
        if self._ui_ready and self._initial_navigation_task:
            self._initial_navigation_task.cancel()
            self._initial_navigation_task = None

    def _get_mounted_servers(self) -> Tuple[Dict, bool]:
        """returns mounted server dict from settings"""
        settings = carb.settings.get_settings()
        mounted_servers = {}
        try:
            mounted_servers = settings.get_settings_dictionary("exts/omni.kit.window.filepicker/mounted_servers").get_dict()
        except AttributeError:
            pass
        return mounted_servers, False

    def _on_window_width_changed(self, new_width: int):
        self._window_size = (new_width, self._window_size[1])
        self._detail_splitter.offset_x = self._window_size[0] - self._splitter_offset[1]

    def _on_detail_splitter_dragged(self, position_x: int):
        new_offset = self._window_size[0] - position_x
        # Limit how far offset can move, otherwise will break
        self._splitter_offset = (self._splitter_offset[0], max(self._detail_width_min, min(self._detail_width_max, new_offset)))
        self._detail_splitter.offset_x = self._window_size[0] - self._splitter_offset[1]

    def _on_toggle_grid_view(self, show_grid_view):
        settings = carb.settings.get_settings()
        settings.set(f"/persistent{self._settings_root}show_grid_view", show_grid_view)

    def _on_scale_grid_view(self, scale_level):
        if scale_level is not None:
            settings = carb.settings.get_settings()
            settings.set(f"/persistent{self._settings_root}grid_view_scale", scale_level)

    def _on_mouse_pressed(self, pane: int, button: int, key_mod: int, item: FileBrowserItem):
        if button == 1:
            # Right mouse button: display context menu
            if item:
                # Mimics the behavior of Windows file explorer: On right mouse click, if item already
                # selected, then apply action to all selections; else, make item the sole selection.
                selected = self._view.get_selections(pane=pane)
                selected = selected if item in selected else [item]

                # TODO Managing context menus is considerably easier if items own the menu rather than
                # the parent widget. We should consider refactoring the pre-existing item subclasses.
                if isinstance(item, FileBrowserItem):
                    context_menu = item.context_menu
                    if context_menu:
                        context_menu.show(
                            item,
                            selected=selected,
                        )
                        return

                if self._view.is_collection_node(item):
                    # OM-75883: Show context menu for collection nodes
                    self._context_menus.get('collection').show(item)
                elif self._view.is_bookmark(item):
                    # OM-66726: Edit bookmarks similar to Navigator
                    self._context_menus.get('bookmark').show(item)
                elif isinstance(item, FileBrowserUdimItem):
                    self._context_menus.get('udim').show(item)
                elif self._view.is_connection_point(item):
                    self._context_menus.get('connection').show(item, selected=selected)
                elif self._view.is_local_point(item):
                    self._context_menus.get('local').show(item, selected=selected)
                else:
                    self._context_menus.get('item').show(
                        item,
                        selected=selected,
                    )
            else:
                item = self._view.get_root(pane)
                if item:
                    if pane == TREEVIEW_PANE:
                        # Skip treeview menu.
                        pass
                    elif pane == LISTVIEW_PANE:
                        self._context_menus.get('list_view').show(
                            item,
                            selected=self._view.get_selections(pane=LISTVIEW_PANE),
                        )

    def _on_mouse_double_clicked(self, pane: int, button: int, key_mod: int, item: FileBrowserItem):
        if not item:
            return
        if button == 0 and not item.is_folder:
            if self._click_apply_handler:
                if self._timestamp_widget:
                    url = self._timestamp_widget.get_timestamp_url(item.path)
                else:
                    url = item.path
                dirname = os.path.dirname(item.path).replace("\\", "/") + "/"
                filename = os.path.basename(url)
                self._click_apply_handler(filename, dirname)

    def _on_selection_changed(self, pane: int, selected: List[FileBrowserItem] = []):
        if not selected:
            return

        # OM-49484: Create a cancellable task for initial navigation, and cancel if user browsed to a directory
        self._cancel_initial_navigation()
        # OMFP-649: Need hide the loading icon when selection changed to make it clean and consistent.
        self.api.hide_loading_pane()

        item = selected[-1] or self._view.get_root()
        # Note: Below results in None when it's a search item

        # OM-66726: Content Browser should edit bookmarks similar to Navigator
        if self._view.is_bookmark(item):
            self._current_directory = os.path.dirname(item.path)

            def set_bookmark(path, _):
                # we cannot directly check is_bookmark(item.parent) because item.parent is a FS item, but
                # bookmark items are NucleusItem, so had to check path explicitly
                self._tool_bar.set_bookmarked(self._view.is_bookmark(None, path=path))
            self.api.navigate_to(item.path, callback=partial(set_bookmark, self._current_directory))

        dir_item = item if item.is_folder else item.parent
        # OMREQ-923: Only set the current directory for treeview pane in case of selection change.
        if dir_item and pane == TREEVIEW_PANE:
            self._api.set_current_directory(dir_item.path)
            self._tool_bar.set_bookmarked(self._view.is_bookmark(dir_item, path=dir_item.path))
            self._current_directory = dir_item.path

        if not item.is_folder:
            self._api.set_filename(item.path)

        if self._detail_view:
            self._detail_view.on_selection_changed(selected)

        if self._selection_changed_fn:
            self._selection_changed_fn(selected)

    def _on_filename_changed(self, filename: str):
        if self._detail_view:
            self._detail_view.on_filename_changed(filename)
        if self._filename_changed_handler:
            self._filename_changed_handler(filename)

    def _on_search(self, search_model):
        if self._view:
            exec_after_redraw(lambda: self._view.show_model(search_model))

    def _apply_config_options(self):
        settings = self._tool_bar.config_values if self._tool_bar else {}
        self._show_unknown_asset_types = not settings.get("hide_unknown")
        self._show_thumbnails_folders = not settings.get("hide_thumbnails")
        self._view.show_udim_sequence = settings.get("show_udim_sequence")
        self._show_deleted = settings.get("show_deleted")

        if self._detail_pane:
            self._detail_pane.visible = settings.get("show_details", True)
        if self._detail_splitter:
            self._detail_splitter.visible = settings.get("show_details", True)

        self._refresh_ui()

    def _item_filter_handler(self, item: FileBrowserItem) -> bool:
        """
        Item filter handler, wrapper for the custom handler if specified. Returns True if the item is visible.

        Args:
            item (:obj:`FileBrowseritem`): Item in question.

        Returns:
            bool

        """
        if not item:
            return False

        if item.is_deleted:
            if not self._show_deleted:
                return False

        # Does item belongs to the thumbnails folder?
        if item.is_folder:
            return self._show_thumbnails_folders if item.name == ".thumbs" else True
        elif not self._show_thumbnails_folders and "/.thumbs/" in item.path:
            return False

        # Run custom filter if specified, else the default filter
        if self._item_filter_fn:
            return self._item_filter_fn(item)

        return True

    def _refresh_ui(self, item: FileBrowserItem = None):
        if not self._view:
            return
        self._view.refresh_ui(item)
