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
import omni.kit.app
import carb.settings
import carb.windowing

from typing import List, Tuple, Callable, Dict
from functools import partial
from carb import log_warn, eventdispatcher
from omni.kit.window.filepicker import FilePickerDialog, UI_READY_GLOBAL_EVENT
from omni.kit.widget.filebrowser import FileBrowserItem
from . import ExportOptionsDelegate

g_singleton = None

WINDOW_NAME = "File Exporter"

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
    ("*.usd", "Can be Binary or Ascii"),
    ("*.usda", "Human-readable text format"),
    ("*.usdc", "Binary format"),
]
# END-DOC-file_extension_types

def on_filter_item(dialog: FilePickerDialog, show_only_folders: True, item: FileBrowserItem) -> bool:
    """
    Filter the items shown in the export file picker dialog.
    Args:
        dialog (FilePickerDialog): The export file dialog.
        show_only_folders (bool): Whether only folder should be show.
        item (FileBrowserItem): The file browser item show in export file dialog.
    Returns:
        True if item could show in dialog. Otherwise Flase.
    """
    if item and not item.is_folder:
        if show_only_folders:
            return False
        else:
            return file_filter_handler(item.path or '', dialog.get_file_postfix(), dialog.get_file_extension())
    return True


def on_export(
    export_fn: Callable[[str, str, str, List[str]], None],
    dialog: FilePickerDialog,
    filename: str,
    dirname: str,
    should_validate: bool = False,
):
    """
    Called when export file, it's a wrapper to export_fn.
    Args:
        export_fn (Callable): The callback to handle the export,
            filename being the name of the file, and dirname being the containing directory path with an ending slash. Function signature is
            export_fn(filename: str, dirname: str, extension: str, selections: List[str]) -> None
        dialog (FilePickerDialog): The export file dialog.
        filename (str): Name of the target file, excluding filename extension.
        dirname (str): The target folder name to export to.
    Keyword Args:
        should_validate (bool): Whether filename validation should be performed.
    """
    # OM-64312: should only perform validation when specified, default to not validate
    if should_validate:
        # OM-58150: should not allow saving with a empty filename
        if not _filename_validation_handler(filename):
            return

    file_postfix = dialog.get_file_postfix()
    file_extension = dialog.get_file_extension()
    _save_default_settings({'directory': dirname})
    selections = dialog.get_current_selections() or []
    dialog.hide()

    def normalize_filename_parts(filename, file_postfix, file_extension) -> Tuple[str, str]:
        splits = filename.split('.')
        keep = len(splits) - 1

        # leaving the dynamic writable usd file exts strip logic here, in case writable exts are loaded at runtime
        try:
            import omni.usd
            if keep > 0 and splits[keep] in omni.usd.writable_usd_file_exts():
                keep -= 1
        except Exception:
            pass

        # OM-84454: strip out file extensions from filename if the current filename ends with any of the file extensions
        # available in the current instance of dialog
        available_options = [item.lstrip("*.") for item, _ in dialog.get_file_extension_options()]
        if keep > 0 and splits[keep] in available_options:
            keep -= 1
        # strip out postfix from filename
        if keep > 0 and splits[keep] in dialog.get_file_postfix_options():
            keep -= 1

        basename = '.'.join(splits[:keep+1]) if keep >= 0 else ""

        extension = ""
        if file_postfix:
            extension += f".{file_postfix}"
        if file_extension:
            extension += f"{file_extension.strip('*')}"
        return basename, extension

    if export_fn:
        basename, extension = normalize_filename_parts(filename, file_postfix, file_extension)
        export_fn(basename, dirname, extension=extension, selections=selections)

def file_filter_handler(filename: str, filter_postfix: str, filter_ext: str) -> bool:
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
    if not filter_ext:
        return True
    filter_ext = filter_ext.replace('*', '')
    # Show only files whose names end with: *<postfix>.<ext>
    if not filter_ext:
        filename = os.path.splitext(filename)[0]
    elif filename.endswith(filter_ext):
        filename = filename[:-len(filter_ext)].strip('.')
    else:
        return False
    if not filter_postfix or filename.endswith(filter_postfix):
        return True
    return False

def _save_default_settings(default_settings: Dict):
    settings = carb.settings.get_settings()
    default_settings_path = settings.get_as_string("/exts/omni.kit.window.file_exporter/appSettings")
    settings.set_string(f"{default_settings_path}/directory", default_settings['directory'] or "")


def _filename_validation_handler(filename):
    """Validates the filename being exported. Currently only checking if it's empty."""
    if not filename:
        msg = "Filename is empty! Please specify the filename first."
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
    invalid_chars = '/\\:*?"<>|\t\n\r\x0b\x0c'
    if not filename:
        return False
    if any(c in invalid_chars for c in filename):
        return False
    return True


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class FileExporterExtension(omni.ext.IExt):
    """A Standardized file export dialog."""
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
        self._ui_ready_event_sub = eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="omni.kit.window.file_exporter.extension",
            event_name=UI_READY_GLOBAL_EVENT,
            on_event=self._on_ui_ready
        )
        self._client_bookmarks_changed_subscription = omni.client.list_bookmarks_with_callback(self._on_client_bookmarks_changed)
        self._destroy_dialog_task = None

    def show_window(
        self,
        title: str = None,
        width: int = 1080,
        height: int = 450,
        show_only_collections: List[str] = None,
        show_only_folders: bool = False,
        file_postfix_options: List[str] = None,
        file_extension_types: List[Tuple[str, str]] = None,
        export_button_label: str = "Export",
        export_handler: Callable[[str, str, str, List[str]], None] = None,
        filename_url: str = None,
        file_postfix: str = None,
        file_extension: str = None,
        should_validate: bool = False,
        enable_filename_input: bool = True,
        focus_filename_input: bool = True, # OM-91056: file exporter should focus filename input field
        click_cancel_handler: Callable[[str, str], None] = None,
    ):
        """
        Displays the export dialog with the specified settings.

        Keyword Args:
            title (str): The name of the dialog
            width (int): Width of the window (Default=1250)
            height (int): Height of the window (Default=450)
            show_only_collections (List[str]): Which of these collections, ["bookmarks", "omniverse", "my-computer"] to display.
            show_only_folders (bool): Show only folders in the list view.
            file_postfix_options (List[str]): A list of filename postfix options. Nvidia defaults.
            file_extension_types (List[Tuple[str, str]]): A list of filename extension options.  Each list
                element is a (extension name, description) pair, e.g. (".usdc", "Binary format"). Nvidia defaults.
            export_button_label (str): Label for the export button (Default="Export")
            export_handler (Callable): The callback to handle the export, filename is the name of the file,
                and dirname being the containing directory path with an ending slash. Function signature is
                export_handler(filename: str, dirname: str, extension: str, selections: List[str]) -> None
            filename_url (str): Url of the target file, excluding filename extension.
            file_postfix (str): Sets selected postfix to this value if specified.
            file_extension (str): Sets selected extension to this value if specified.
            should_validate (bool): Whether filename validation should be performed.
            enable_filename_input (bool): Whether filename field input is enabled, default to True.
            click_cancel_handler (Callable[[str, str], None]): The callback to handle click of the cancel button.
        """
        if self._dialog:
            self.destroy_dialog()

        # Load saved settings as defaults
        default_settings = self._load_default_settings()
        basename = ""
        directory = default_settings.get('directory')

        if filename_url:
            dirname, filename = os.path.split(filename_url)
            basename = os.path.basename(filename)
            # override directory name only if explicitly given from filename_url
            if dirname:
                directory = dirname

        file_postfix_options = file_postfix_options or DEFAULT_FILE_POSTFIX_OPTIONS
        file_extension_types = file_extension_types or DEFAULT_FILE_EXTENSION_TYPES

        def _on_cancel(file_name: str, dir_name: str):
            if click_cancel_handler:
                click_cancel_handler(file_name, dir_name)

            self._dialog.hide()

        self._title = title or WINDOW_NAME
        self._dialog = FilePickerDialog(
            self._title,
            width=width,
            height=height,
            splitter_offset=260,
            enable_file_bar=True,
            enable_filename_input=enable_filename_input,
            enable_checkpoints=False,
            show_detail_view=True,
            show_only_collections=show_only_collections or [],
            file_postfix_options=file_postfix_options,
            file_extension_options=file_extension_types,
            filename_changed_handler=partial(self._on_filename_changed, show_only_folders=show_only_folders),
            apply_button_label=export_button_label,
            current_directory=directory,
            current_filename=basename,
            current_file_postfix=file_postfix,
            current_file_extension=file_extension,
            focus_filename_input=focus_filename_input,
            click_cancel_handler=_on_cancel
        )
        self._dialog.set_item_filter_fn(partial(on_filter_item, self._dialog, show_only_folders))
        self._dialog.set_click_apply_handler(
            partial(on_export, export_handler, self._dialog, should_validate=should_validate)
        )
        self._dialog.set_visibility_changed_listener(self._visibility_changed_fn)
        # don't disable apply button if we are showing folders only
        self._dialog._widget.file_bar.enable_apply_button(enable=show_only_folders)
        if show_only_folders:
            self._dialog._widget.file_bar.label_name = "Folder name"
        else:
            self._dialog._widget.file_bar.label_name = "File name"
        self._dialog.show()

    def _visibility_changed_fn(self, visible: bool):
        async def destroy_dialog_async():
            # wait one frame, this is due to the one frame defer
            # in Window::_moveToMainOSWindow()
            try:
                await omni.kit.app.get_app().next_update_async()
                if self._dialog:
                    self._dialog.destroy()
                    self._dialog = None
            finally:
                self._destroy_dialog_task = None

        if not visible:
            # Destroy the window, since we are creating new window in show_window
            if not self._destroy_dialog_task or self._destroy_dialog_task.done():
                self._destroy_dialog_task = asyncio.ensure_future(
                    destroy_dialog_async()
                )

    def _load_default_settings(self) -> Dict:
        settings = carb.settings.get_settings()
        default_settings_path = settings.get_as_string("/exts/omni.kit.window.file_exporter/appSettings")

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
        if self._dialog and self._dialog._widget and not show_only_folders:
            self._dialog._widget.file_bar.enable_apply_button(enable=_filename_validator(filename))

    def _on_ui_ready(self, event: eventdispatcher.Event):
        title = event["title"]
        if title == self._title:
            self._ui_ready = True

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

    def add_export_options_frame(self, name: str, delegate: ExportOptionsDelegate):
        """
        Adds a set of export options to the dialog.  Should be called after show_window.

        Args:
            name (str): Title of the options box.
            delegate (ExportOptionsDelegate): Subclasses specified delegate and overrides the
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
        if self._dialog and self._dialog._window:
            main_window = omni.appwindow.get_default_app_window().get_window()
            dialog_main_window = self._dialog._window.app_window.get_window()
            # OM-105857: Don't hide the app's main window
            if dialog_main_window is not main_window:
                carb.windowing.acquire_windowing_interface().hide_window(dialog_main_window)

        if self._dialog:
            self._dialog.destroy()
        self._dialog = None
        self._ui_ready = False
        if self._destroy_dialog_task:
            self._destroy_dialog_task.cancel()
        self._destroy_dialog_task = None

    def on_shutdown(self):
        self.destroy_dialog()
        self._ui_ready_event_sub = None
        self._client_bookmarks_changed_subscription = None

        global g_singleton
        g_singleton = None


def get_instance():
    return g_singleton
