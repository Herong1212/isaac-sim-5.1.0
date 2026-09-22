# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import asyncio
import omni.ext
import carb.settings
import carb.windowing
import omni.appwindow

from typing import List, Tuple, Callable, Dict
from functools import partial, lru_cache
from carb import log_warn, events, eventdispatcher
from omni.kit.window.filepicker import FilePickerDialog, UI_READY_GLOBAL_EVENT
from omni.kit.widget.filebrowser import FileBrowserItem
from . import ImportOptionsDelegate
import omni.client

g_singleton = None

WINDOW_NAME = "File Importer"

# BEGIN-DOC-file_postfix_options
DEFAULT_FILE_POSTFIX_OPTIONS = [
    None,
    "anim",
    "cache",
    "curveanim",
    "geo",
    "material",
    "project",
    "seq",
    "skel",
    "skelanim",
]
# END-DOC-file_postfix_options


# BEGIN-DOC-file_extension_types
DEFAULT_FILE_EXTENSION_TYPES = [
    # this intentionally restricts the extension listing to native USD file types
    # rather than all supported Sdf File Formats. See OM-76297 for details.
    ("*.usd, *.usda, *.usdc, *.usdz", "USD Files"),
    ("*.*", "All files"),
]
# END-DOC-file_extension_types

# cache usd file exts since it is costly
_usd_file_exts = None


@lru_cache()
def _get_windowing() -> carb.windowing.IWindowing:
    try:
        return carb.windowing.acquire_windowing_interface()
    except RuntimeError:
        # OVC: RuntimeError: Failed to acquire interface: card::windowing::IWindowing
        return None

def _get_usd_file_exts():
    global _usd_file_exts

    if _usd_file_exts is None:
        # the Code bellow is taking ~100ms, so it needs to be delayed to the latest moment possible
        default_usd_file_exts = ["usd", "usda", "usdc", "usdz"]
        try:
            import omni.usd
            usd_file_exts = omni.usd.readable_usd_file_exts()
        except Exception:
            try:
                import pxr.Sdf
                usd_file_exts = pxr.Sdf.FileFormat.FindAllFileFormatExtensions()
            except Exception:
                usd_file_exts = default_usd_file_exts
        _usd_file_exts = [(f"*.{ext_str}", f"{ext_str.upper()} Files") for ext_str in usd_file_exts]

    return _usd_file_exts


def on_filter_item(filter_fn: Callable[[str], bool], dialog: FilePickerDialog, item: FileBrowserItem, show_only_folders: bool = True) -> bool:
    """
    Filter the items shown in the import file picker dialog.
    Args:
        dialog (FilePickerDialog): The import file dialog.
        show_only_folders (bool): Whether only folder should be show.
        item (FileBrowserItem): The file browser item show in import file dialog.
    Returns:
        True if item could show in dialog. Otherwise Flase.
    """
    if item and not item.is_folder:
        # OM-96626: Add show_only_folders option to file importer
        if show_only_folders:
            return False
        if filter_fn:
            return filter_fn(item.path or '', dialog.get_file_postfix(), dialog.get_file_extension())
    return True


def on_import(import_fn: Callable[[str, str, List[str]], None], dialog: FilePickerDialog, filename: str, dirname: str,
    hide_window_on_import: bool = True, should_validate: bool = False):
    """
    Called when import file, it's a wrapper to import_fn.
    Args:
        import_fn (Callable): The callback to handle the import,
            filename being the name of the file, and dirname being the containing directory path with an ending slash.  Function signature is
            import_fn(filename: str, dirname: str, extension: str, selections: List[str]) -> None
        dialog (FilePickerDialog): The import file dialog.
        filename (str): Name of the target file, excluding filename extension.
        dirname (str): The target folder name to import to.
    Keyword Args:
        hide_window_on_import (bool):Whether hide the dialog when import.
        should_validate (bool): Whether filename validation should be performed.
    """
    _save_default_settings({'directory': dirname})
    selections = dialog.get_current_selections() or []
    full_url = omni.client.combine_urls(dirname + "/", filename)

    # OMPE-49994: File path validation should be done asynchronously to avoid blocking the main thread
    async def async_import(full_url, hide_window_on_import, import_fn, filename, dirname, selections):
        # OM-39070: should only perform validation when specified, default to not validate
        if should_validate:
            # should not allow importing invalid file paths
            if not await _filepath_validation_handler(full_url):
                return

        if hide_window_on_import:
            dialog.hide()

        if import_fn:
            import_fn(filename, dirname, selections=selections)

    from omni.kit.async_engine import run_coroutine
    run_coroutine(async_import(full_url, hide_window_on_import, import_fn, filename, dirname, selections))


async def _filepath_validation_handler(filepath: str):
    """Validates the filename being imported exists asynchronously. This is to avoid blocking the main thread when stating."""
    result, _ = await omni.client.stat_async(filepath)
    if result != omni.client.Result.OK:
        msg = f"File path {filepath} is not valid, please re-enter or re-select the import path."
        try:
            import omni.kit.notification_manager as nm
            nm.post_notification(msg, status=nm.NotificationStatus.WARNING)
        except ModuleNotFoundError:
            import carb
            carb.log_warn(msg)
        return False
    return True

def _filename_validator(filename: str):
    """Validates filename has invalid chars."""
    # OM-119336:?<>|"are valid chars for url path
    invalid_chars = '*\t\n\r\x0b\x0c'
    if not filename:
        return False
    url = omni.client.break_url(filename)

    if any(c in invalid_chars for c in url.path):
        return False
    return True

# BEGIN-DOC-file_filter_handler
def default_filter_handler(filename: str, filter_postfix: str, filter_ext: str) -> bool:
    """
    Show only files whose names end with: *<postfix>.<ext>.
    Args:
        filename (str): The item's file name .
        filter_postfix (str): Whether file name match this filter postfix.
        filter_ext (str): Whether file name match this filter extension.
    Returns:
        True if file could show in dialog. Otherwise Flase.
    """
    if not filename:
        return True

    # Show only files whose names end with: *<postfix>.<ext>
    if filter_ext:
        # split comma separated string into a list:
        filter_exts = filter_ext.split(",") if isinstance(filter_ext, str) else filter_ext
        filter_exts = [x.replace(" ", "") for x in filter_exts]
        filter_exts = [x for x in filter_exts if x]

        # check if the file extension matches anything in the list:
        if not (
            "*.*" in filter_exts or
            any(filename.endswith(f.replace("*", "")) for f in filter_exts)
        ):
            # match failed:
            return False

    if filter_postfix:
        # strip extension and check postfix:
        filename = os.path.splitext(filename)[0]
        return filename.endswith(filter_postfix)

    return True
# END-DOC-file_filter_handler

def _save_default_settings(default_settings: Dict):
    settings = carb.settings.get_settings()
    default_settings_path = settings.get_as_string("/exts/omni.kit.window.file_importer/appSettings")
    settings.set_string(f"{default_settings_path}/directory", default_settings['directory'] or "")


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class FileImporterExtension(omni.ext.IExt):
    """A Standardized file import dialog."""
    def __init__(self):
        super().__init__()
        self._dialog = None
        self._title = None
        self._ui_ready = False
        self._ui_ready_event_sub = None
        self._current_servers = []

    def on_startup(self, ext_id):
        # Save away this instance as singleton for the editor window
        global g_singleton
        g_singleton = self

        # Listen for filepicker events
        self._destroy_task = None
        self._ui_ready_event_sub = eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="omni.kit.window.file_importer.extension",
            event_name=UI_READY_GLOBAL_EVENT,
            on_event=self._on_ui_ready
        )
        self._client_bookmarks_changed_subscription = omni.client.list_bookmarks_with_callback(self._on_client_bookmarks_changed)

    def show_window(self,
        title: str = None,
        width: int = 1080,
        height: int = 450,
        show_only_collections: List[str] = None,
        show_only_folders: bool = False,
        file_postfix_options: List[str] = None,
        file_extension_types: List[Tuple[str, str]] = None,
        file_filter_handler:Callable[[str, str, str], bool] = None,
        import_button_label: str = "Import",
        import_handler: Callable[[str, str, List[str]], None] = None,
        filename_url: str = None,
        file_postfix: str = None,
        file_extension: str = None,
        hide_window_on_import: bool = True,
        should_validate: bool = False,
        focus_filename_input: bool = True,
        allow_multi_files_selection: bool = False
    ):
        """
        Displays the import dialog with the specified settings.

        Keyword Args:
            title (str): The name of the dialog
            width (int): Width of the window (Default=1250)
            height (int): Height of the window (Default=450)
            show_only_collections (List[str]): Which of these collections, ["bookmarks", "omniverse", "my-computer"] to display.
            show_only_folders (bool): Show only folders in the list view.
            file_postfix_options (List[str]): A list of filename postfix options. Nvidia defaults.
            file_extension_types (List[Tuple[str, str]]): A list of filename extension options.  Each list
                element is a (extension name, description) pair, e.g. (".usd", "USD format"). Nvidia defaults.
            file_filter_handler (Callable): The filter handler that is called to decide whether or not to display a file.
                Function signature is filter_handler(filename: str, filter_postfix: str, filter_ext: str) -> bool
            import_button_label (str): Label for the import button (Default="Import")
            import_handler (Callable): The callback to handle the import, filename is the name of the file,
                and dirname being the containing directory path with a ending slash.  Function signature is
                import_handler(filename: str, dirname: str, selections: List[str]) -> None
            filename_url (str): Url of the file to import, if any.
            file_postfix (str): Sets selected postfix to this value if specified.
            file_extension (str): Sets selected extension to this value if specified.
            hide_window_on_import (bool): Whether the dialog hides on apply; if False, it means that whether to hide the
                dialog should be decided by import handler.
            should_validate (bool): Whether filename validation should be performed.

        """
        if self._dialog:
            self.destroy_dialog()

        # Load saved settings as defaults
        default_settings = self._load_default_settings()
        filename = None
        directory = default_settings.get('directory')
        settings = carb.settings.get_settings()
        enable_timestamp = settings.get_as_bool("exts/omni.kit.window.file_importer/enable_timestamp")

        if filename_url:
            directory, filename = os.path.split(filename_url)

        # OM-96962: Delay usd extension computation so it doesn't take up load time
        file_extension_types = file_extension_types or DEFAULT_FILE_EXTENSION_TYPES + _get_usd_file_exts()
        file_filter_handler = file_filter_handler or default_filter_handler

        self._title = title or WINDOW_NAME
        self._dialog = FilePickerDialog(
            self._title,
            width=width,
            height=height,
            splitter_offset=260,
            enable_file_bar=True,
            enable_filename_input=True,
            enable_checkpoints=True,
            enable_timestamp=enable_timestamp,
            show_detail_view=True,
            show_only_collections=show_only_collections or [],
            file_postfix_options=file_postfix_options,
            file_extension_options=file_extension_types,
            filename_changed_handler=partial(self._on_filename_changed, show_only_folders=show_only_folders),
            selection_changed_fn=partial(
                self._on_selection_changed, show_only_folders=show_only_folders,
                allow_multi_files_selection=allow_multi_files_selection
            ),
            apply_button_label=import_button_label,
            current_directory=directory,
            current_filename=filename,
            current_file_postfix=file_postfix,
            current_file_extension=file_extension,
            focus_filename_input=focus_filename_input, # OM-91056: file exporter should focus filename input field
            # OM-104306: file importer should open the file when a valid path is entered
            apply_path_handler=partial(
                self._on_apply_path,
                file_extension_types=file_extension_types,
                file_filter_handler=file_filter_handler,
            )
        )
        self._dialog.set_item_filter_fn(partial(on_filter_item, file_filter_handler, self._dialog, show_only_folders=show_only_folders))
        self._click_apply_handler = partial(
            on_import,
            import_handler,
            self._dialog,
            hide_window_on_import=hide_window_on_import,
            should_validate=should_validate
        )
        self._dialog.set_click_apply_handler(self._click_apply_handler)
        self._dialog.set_visibility_changed_listener(self._visibility_changed_fn)
        # OM-96626: Add show_only_folders option to file importer
        self._dialog._widget.file_bar.enable_apply_button(enable=show_only_folders)
        self._dialog.show()

    def _visibility_changed_fn(self, visible):
        async def destroy_dialog_async():
            # wait one frame, this is due to the one frame defer
            # in Window::_moveToMainOSWindow()
            await omni.kit.app.get_app().next_update_async()
            if self._dialog:
                self._dialog.destroy()
                self._dialog = None

            self._destroy_task = None

        if not visible:
            # Destroy the window, since we are creating new window in show_window
            if not self._destroy_task or self._destroy_task.done():
                self._destroy_task = asyncio.ensure_future(destroy_dialog_async())

    def _load_default_settings(self) -> dict:
        settings = carb.settings.get_settings()
        default_settings_path = settings.get_as_string("/exts/omni.kit.window.file_importer/appSettings")

        default_settings = {}
        directory = settings.get_as_string(f"{default_settings_path}/directory")
        if not omni.client.is_local_url(directory):
            default_settings['directory'] = ""
            mounted_servers = {}
            try:
                mounted_servers = settings.get_settings_dictionary("exts/omni.kit.window.content_browser/mounted_servers").get_dict()
            except Exception:
                pass
            mounted_servers = mounted_servers if mounted_servers else {}
            # OM-83885: Load default derectory only if it's server is in current servers
            for server in list(mounted_servers.values()) + self._current_servers:
                if directory.startswith(server):
                    default_settings['directory'] = directory
                    break
        else:
            default_settings['directory'] = directory
        return default_settings

    def _on_client_bookmarks_changed(self, client_bookmarks: Dict):
        self._current_servers = [url for name, url in client_bookmarks.items() if self._is_nucleus_server_url(url)]

    def _is_nucleus_server_url(self, url: str):
        if not url:
            return False
        broken_url = omni.client.break_url(url)
        if not omni.client.is_local_url(url) and broken_url.path == "/" and broken_url.host is not None:
            # Url of the form "omniverse://server_name/" should be recognized as server connection
            return True
        return False

    def _on_filename_changed(self, filename, show_only_folders=False):
        # OM-78341: Disable apply button if no file is selected, if we are not showing only folders
        if self._dialog and not show_only_folders:
            self._dialog._widget.file_bar.enable_apply_button(enable=_filename_validator(filename))

    def _on_selection_changed(
        self, selected: List[FileBrowserItem], show_only_folders=False,
        allow_multi_files_selection=False
    ):
        if self._dialog and not show_only_folders:
            if allow_multi_files_selection:
                enabled = True
                for selection in selected:
                    if selection._is_folder:
                        enabled = False
                        break
            else:
                enabled = len(selected) == 1 and not selected[0]._is_folder

            self._dialog._widget.file_bar.enable_apply_button(enable=enabled)

    def _on_ui_ready(self, event: eventdispatcher.Event):
        title = event["title"]
        if title == self._title:
            self._ui_ready = True

    def _on_apply_path(
            self, url: str,
            file_extension_types: List[Tuple[str, str]],
            file_filter_handler: Callable[[str, str, str], bool]):
        if not url:
            return
        result, entry = omni.client.stat(url)
        if result != omni.client.Result.OK:
            return
        # Ignore folders
        if (entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) != 0:
            # OMPRW-733 & OMPRW-734: Navigate to the folder when apply a folder path.
            self._dialog.navigate_to(url)
            return
        broken_url = omni.client.break_url(url)
        exts = ",".join([ext for ext, _ in file_extension_types])
        if file_filter_handler(broken_url.path, None, exts):
            dirname, filename = url.rsplit('/', 1)
            self._click_apply_handler(filename, dirname)
        else:
            self._dialog.navigate_to(url)

    @property
    def is_ui_ready(self) -> bool:
        return self._ui_ready

    @property
    def is_window_visible(self) -> bool:
        if self._dialog and self._dialog._window:
            return self._dialog._window.visible
        return False

    def hide_window(self):
        """Hides and destroys the dialog window."""
        self.destroy_dialog()

    def add_import_options_frame(self, name: str, delegate: ImportOptionsDelegate):
        """
        Adds a set of import options to the dialog.  Should be called after show_window.

        Args:
            name (str): Title of the options box.
            delegate (ImportOptionsDelegate): Subclasses specified delegate and overrides the
                _build_ui_impl method to provide a custom widget for getting user input.

        """
        if self._dialog:
            self._dialog.add_detail_frame_from_controller(name, delegate)

    def click_apply(self, filename_url: str = None, postfix: str = None, extension: str = None):
        """Helper function to progammatically execute the apply callback.  Useful in unittests"""
        if self._dialog:
            if filename_url:
                dirname, filename = os.path.split(filename_url)
                self._dialog.set_current_directory(dirname)
                self._dialog.set_filename(filename)
            if postfix:
                self._dialog.set_file_postfix(postfix)
            if extension:
                self._dialog.set_file_extension(extension)
            self._dialog._widget._file_bar._on_apply()

    def click_cancel(self, cancel_handler: Callable[[str, str], None] = None):
        """Helper function to progammatically execute the cancel callback.  Useful in unittests"""
        if cancel_handler:
            self._dialog._widget._file_bar._click_cancel_handler = cancel_handler
        self._dialog._widget._file_bar._on_cancel()

    async def select_items_async(self, url: str, filenames: List[str] = []) -> List[FileBrowserItem]:
        """Helper function to programatically select multiple items in filepicker. Useful in unittests."""
        if self._dialog:
            return await self._dialog._widget.api.select_items_async(url, filenames=filenames)
        return []

    def detach_from_main_window(self):
        """Detach the current file importer dialog from main window."""
        if self._dialog:
            self._dialog._window.move_to_new_os_window()

    def destroy_dialog(self):
        # handles the case for detached window
        if self._dialog:
            # there has no appwindow in OVC2 test
            if self._dialog._window and self._dialog._window.app_window:
                window = self._dialog._window.app_window.get_window()
                if window is not omni.appwindow.get_default_app_window().get_window():
                    windowing_interface = _get_windowing()
                    if windowing_interface:
                        windowing_interface.hide_window(window)

            self._dialog.set_item_filter_fn(None)
            self._dialog.set_click_apply_handler(None)
            self._dialog.set_visibility_changed_listener(None)
            self._dialog.destroy()
        self._dialog = None

        self._ui_ready = False
        if self._destroy_task:
            self._destroy_task.cancel()
        self._destroy_task = None

    def get_dialog(self):
        return self._dialog

    def on_shutdown(self):
        self.destroy_dialog()
        self._ui_ready_event_sub = None
        self._client_bookmarks_changed_subscription = None

        global g_singleton
        g_singleton = None


def get_instance():
    return g_singleton
