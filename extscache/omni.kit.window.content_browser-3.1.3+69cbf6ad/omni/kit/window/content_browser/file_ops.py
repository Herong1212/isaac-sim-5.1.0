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
import omni.client
import carb.settings
import omni.kit.notification_manager
import omni.kit.app

from typing import Callable, List, Union
from datetime import datetime
from functools import lru_cache, partial
from collections import OrderedDict, namedtuple
from carb import log_warn, log_info
from typing import Callable, List
from omni.kit.helper.file_utils import asset_types
from omni.kit.widget.filebrowser import FileBrowserItem, is_clipboard_cut, save_items_to_clipboard, clear_clipboard, FileBrowserItemFields
from omni.kit.window.file_exporter import get_file_exporter
from omni.kit.window.filepicker import ConfirmItemDeletionDialog, get_user_folders_dict, FilePickerView, move_items
from .prompt import Prompt
from . import FILE_TYPE_USD, FILE_TYPE_IMAGE, FILE_TYPE_SOUND, FILE_TYPE_TEXT, FILE_TYPE_VOLUME
import pathlib

FileOpenAction = namedtuple("FileOpenAction", "name open_fn matching_type")

_file_open_dict = OrderedDict()


@lru_cache()
def __get_input() -> carb.input.IInput:
    return carb.input.acquire_input_interface()


def _is_ctrl_down() -> bool:
    input = __get_input()
    return (
        input.get_keyboard_value(None, carb.input.KeyboardInput.LEFT_CONTROL)
        + input.get_keyboard_value(None, carb.input.KeyboardInput.RIGHT_CONTROL)
        > 0
    )


def add_file_open_handler(name: str, open_fn: Callable, file_type: Union[int, Callable]) -> str:
    """
    Registers callback/handler to open a file of matching type.

    Args:
        name (str): Unique name of handler.
        open_fn (Callable): This function is executed when a matching file is selected for open, i.e. double clicked,
            right mouse menu open, or url submitted to browser bar.  Function signature: void open_fn(url: str).
        file_type (Union[int, func]): Can either be an enumerated int that is one of: [FILE_TYPE_USD,
            FILE_TYPE_IMAGE, FILE_TYPE_SOUND, FILE_TYPE_TEXT, FILE_TYPE_VOLUME] or a more general boolean function
            that returns True if this function should be activated on the given file.  Function
            signature: bool file_type(url: str).

    Returns:
        str: Name if successful, None otherwise.

    """
    global _file_open_dict
    if name:
        _file_open_dict[name] = FileOpenAction(name, open_fn, file_type)
        return name
    else:
        return None


def delete_file_open_handler(name: str):
    """
    Unregisters the named file open handler.

    Args:
        name (str): Name of the handler.

    """
    global _file_open_dict
    if name and name in _file_open_dict:
        _file_open_dict.pop(name)


def get_file_open_handler(url: str) -> Callable:
    """
    Returns the matching file open handler for the given item.

    Args:
        url str: The url of the item to open.

    """
    if not url:
        return None
    broken_url = omni.client.break_url(url)

    # Note: It's important that we use an ordered dict so that we can search by order
    # of insertion.
    global _file_open_dict
    for _, tup in _file_open_dict.items():
        _, open_fn, file_type = tup
        if isinstance(file_type, Callable):
            if file_type(broken_url.path):
                return open_fn
        else:
            asset_type = {
                FILE_TYPE_USD: asset_types.ASSET_TYPE_USD,
                FILE_TYPE_IMAGE: asset_types.ASSET_TYPE_IMAGE,
                FILE_TYPE_SOUND: asset_types.ASSET_TYPE_SOUND,
                FILE_TYPE_TEXT: asset_types.ASSET_TYPE_SCRIPT,
                FILE_TYPE_VOLUME: asset_types.ASSET_TYPE_VOLUME,
            }.get(file_type, None)

            if asset_type and asset_types.is_asset_type(broken_url.path, asset_type):
                return open_fn

    return None


def copy_items(dst_item: FileBrowserItem, src_paths: List[str]):
    try:
        from omni.kit.notification_manager import post_notification
    except Exception:
        post_notification = log_warn

    if dst_item and src_paths:
        try:
            def on_copied(results):
                for result in results:
                    if isinstance(result, Exception):
                        post_notification(str(result))
            # prepare src_paths and dst_paths for copy items
            dst_paths = []
            dst_root = dst_item.path
            dst_root_path_obj = pathlib.Path(dst_root)
            skip_paths = []

            for src_path in src_paths:
                # OMFP-2928: Avoid copying parent to child
                src_path_obj = pathlib.Path(src_path)
                if src_path_obj == dst_root_path_obj or src_path_obj in dst_root_path_obj.parents:
                    skip_paths.append(src_path)
                    continue
                rel_path = os.path.basename(src_path)
                dst_paths.append(f"{dst_root}/{rel_path}")

            if len(skip_paths) > 0:
                omni.kit.notification_manager.post_notification(
                    f"The destination({dst_root}) is a subfolder of source folders:\n\t" + "\n\t".join(skip_paths),
                    status=NotificationStatus.WARNING
                )

            copy_items_with_callback(src_paths, dst_paths, on_copied)

        except Exception as e:
            log_warn(f"Error encountered during copy: {str(e)}")


def copy_items_with_callback(src_paths: List[str], dst_paths: List[str], callback: Callable = None, copy_callback: Callable[[str, str, omni.client.Result], None] = None):
    """
    Copies items. Upon success, executes the given callback.

    Args:
        src_pathss ([str]): Paths of items to download.
        dst_paths ([str]): Destination paths.
        callback (func): Callback to execute upon success.  Function signature is void callback(List[Union[Exception, str]).
        copy_callback (func): Callback per every copy. Function signature is void callback([str, str, omni.client.Result]).

    Raises:
        :obj:`Exception`

    """
    if not (dst_paths and src_paths):
        return

    tasks = []
    # should not get here, but just to be safe, if src_paths and dst_paths are not of the same length, don't copy
    if len(src_paths) != len(dst_paths):
        carb.log_warn(
            f"Cannot copy items from {src_paths} to {dst_paths}, source and destination paths should match in number.")
        return

    for src_path, dst_path in zip(src_paths, dst_paths):
        tasks.append(copy_item_async(src_path, dst_path, callback=copy_callback))
    try:
        async def exec_tasks_async(tasks, callback=callback):
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError:
                return
            except Exception:
                # Since we're returning exceptions, we should never hit this case
                return
            else:
                if callback:
                    callback(results)
        asyncio.ensure_future(exec_tasks_async(tasks, callback=callback))
    except Exception:
        raise


async def copy_item_async(src_path: str, dst_path: str, timeout: float = 300.0, callback: Callable[[str, str, omni.client.Result], None] = None) -> str:
    """
    Async function.  Copies item (recursively) from one path to another. Note: this function simply
    uses the copy function from omni.client and makes no attempt to optimize for copying from one
    Omniverse server to another.  For that, use the Copy Service.  Example usage:
    await copy_item_async("my_file.usd", "C:/tmp", "omniverse://ov-content/Users/me")

    Args:
        src_path (str): Source path to item being copied.
        dst_path (str): Destination path to copy the item.
        timeout (float): Number of seconds to try before erroring out.  Default 10.
        callback (func): Callback to copy result.

    Returns:
        str: Destination path name

    Raises:
        :obj:`RuntimeWarning`: If error or timeout.

    """
    if isinstance(timeout, (float, int)):
        timeout = max(300, timeout)
    try:
        # OM-67900: add source url in copied item checkpoint
        src_checkpoint = None
        result, entries = await omni.client.list_checkpoints_async(src_path)
        if result == omni.client.Result.OK and entries:
            src_checkpoint = entries[-1].relative_path

        checkpoint_msg = f"Copied from {src_path}"
        if src_checkpoint:
            checkpoint_msg = f"{checkpoint_msg}?{src_checkpoint}"

        result, _ = await omni.client.stat_async(dst_path)
        if result == omni.client.Result.OK:
            dst_name = os.path.basename(dst_path)
            async def on_overwrite(dialog):
                result = await asyncio.wait_for(
                    omni.client.copy_async(
                        src_path,
                        dst_path,
                        behavior=omni.client.CopyBehavior.OVERWRITE,
                        message=checkpoint_msg),
                    timeout=timeout)
                if callback:
                    callback(src_path, dst_path, result)
                dialog.hide()

            def on_cancel(dialog):
                dialog.hide()

            dialog = ConfirmItemDeletionDialog(
                title="Confirm File Overwrite",
                message="You are about to overwrite",
                items=[FileBrowserItem(dst_path, FileBrowserItemFields(dst_name, datetime.now(), 0, 0), is_folder=False)],
                ok_handler=lambda dialog: asyncio.ensure_future(on_overwrite(dialog)),
                cancel_handler=lambda dialog: on_cancel(dialog),
            )
            dialog.show()
        else:
            result = await asyncio.wait_for(omni.client.copy_async(src_path, dst_path, message=checkpoint_msg), timeout=timeout)
            if callback:
                callback(src_path, dst_path, result)
    except asyncio.TimeoutError:
        raise RuntimeWarning(f"Error unable to copy '{src_path}' to '{dst_path}': Timed out after {timeout} secs.")
    except Exception as e:
        raise RuntimeWarning(f"Error copying '{src_path}' to '{dst_path}': {e}")

    if result != omni.client.Result.OK:
        raise RuntimeWarning(f"Error copying '{src_path}' to '{dst_path}': {result}")

    return dst_path


def drop_items(dst_item: FileBrowserItem, src_paths: List[str], callback: Callable = None, force_drop=False):
    # src_paths is a list of str but when multiple items are selected, the str was a \n joined path string, so
    # we need to re-construct the src_paths
    paths = src_paths[0].split("\n")

    # remove any udim_sequence as that are not real files
    for path in paths.copy():
        if asset_types.is_udim_sequence(path):
            paths.remove(path)
    if not paths:
        return

    # OM-52387: drag and drop is now move instead of copy;
    # Additionally, drag with ctrl down would be copy similar to windows file explorer
    if not force_drop and _is_ctrl_down():
        copy_items(dst_item, paths)
    else:
        # warn user for move operation since it will overwrite items with the same name in the dst folder
        from omni.kit.window.popup_dialog import MessageDialog

        def on_okay(dialog: MessageDialog, dst_item: FileBrowserItem, paths: List[str], callback: Callable=None):
            move_items(dst_item, paths, callback=callback)
            dialog.hide()

        warning_msg = f"This will replace any file with the same name in {dst_item.path}."
        dialog = MessageDialog(
            title="MOVE",
            message="Do you really want to move these files?",
            warning_message=warning_msg,
            ok_handler=lambda dialog, dst_item=dst_item, paths=paths, callback=callback: on_okay(
            dialog, dst_item, paths, callback),
            ok_label="Confirm",
        )
        dialog.show()


def cut_items(src_items: List[FileBrowserItem], view: FilePickerView):
    if not src_items:
        return

    save_items_to_clipboard(src_items, is_cut=True)
    # to maintain the left treeview pane selection, only update listview for filebrowser
    view._filebrowser.refresh_ui(listview_only=True)


def paste_items(dst_item: FileBrowserItem, src_items: List[FileBrowserItem], view: FilePickerView, force_drop: bool=False):
    src_paths = [item.path for item in src_items]
    # if currently the clipboard is for cut operation, then use move
    if is_clipboard_cut():
        def _on_cut_pasted(dst_item, src_items, view):
            # sync up item changes for src and dst items
            to_update = set([dst_item])
            for item in src_items:
                to_update.add(item.parent)
            for item in to_update:
                view._filebrowser._models.sync_up_item_changes(item)

            # clear clipboard and update item style
            clear_clipboard()
            view._filebrowser.refresh_ui(listview_only=True)

        drop_items(dst_item, ["\n".join(src_paths)], callback=lambda: _on_cut_pasted(dst_item, src_items, view), force_drop=force_drop)
    # else use normal copy
    else:
        copy_items(dst_item, src_paths)


def open_file(url: str, load_all=True):
    async def open_file_async(open_fn: Callable, url: str, load_all=True):
        result, entry = await omni.client.stat_async(url)
        if result == omni.client.Result.OK:
            # OM-57423: Make sure this is not a folder
            is_folder = (entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) > 0
            if is_folder:
                return

        if open_fn:
            import inspect

            sig = inspect.signature(open_fn)
            if sig and "load_all" in sig.parameters:
                if asyncio.iscoroutinefunction(open_fn):
                    await open_fn(url, load_all)
                else:
                    open_fn(url, load_all)
                return

            if asyncio.iscoroutinefunction(open_fn):
                await open_fn(url)
            else:
                open_fn(url)

    open_fn = get_file_open_handler(url)
    if open_fn:
        asyncio.ensure_future(open_file_async(open_fn, url, load_all))


# Register file open handler for USD's
def open_stage(url, load_all=True):
    result, entry = omni.client.stat(url)
    if result == omni.client.Result.OK:
        read_only = entry.access & omni.client.AccessFlags.WRITE == 0
    else:
        read_only = False

    if read_only:
        def _open_with_edit_layer():
            open_stage_with_new_edit_layer(url, load_all)

        def _open_original_stage():
            asyncio.ensure_future(open_stage_async(url, load_all))

        _show_readonly_usd_prompt(_open_with_edit_layer, _open_original_stage)
    else:
        asyncio.ensure_future(open_stage_async(url, load_all))


async def open_stage_async(url: str, load_all=True):
    """
    Async function for opening a USD file.

    Args:
        url (str): Url to file.

    """
    try:
        import omni.kit.window.file

        if load_all:
            open_loadset = omni.usd.UsdContextInitialLoadSet.LOAD_ALL
        else:
            open_loadset = omni.usd.UsdContextInitialLoadSet.LOAD_NONE

        omni.kit.window.file.open_stage(url, open_loadset)
    except Exception as e:
        log_warn(str(e))
    else:
        log_info(f"Success! Opened '{url}'.\n")


def open_stage_with_new_edit_layer(url: str, load_all=True):
    """
    Async function for opening a USD file, then creating a new layer.

    Args:
        url (str): Url to file.

    """
    try:
        import omni.usd
        import omni.kit.window.file

        if load_all:
            open_loadset = omni.usd.UsdContextInitialLoadSet.LOAD_ALL
        else:
            open_loadset = omni.usd.UsdContextInitialLoadSet.LOAD_NONE

        omni.kit.window.file.open_with_new_edit_layer(url, open_loadset)
    except Exception as e:
        log_warn(str(e))
    else:
        log_info(f"Success! Opened '{url}' with new edit layer.\n")


def download_items(selections: List[FileBrowserItem]):
    if not selections:
        return

    def on_download(src_items: List[FileBrowserItem], filename: str, dirname: str):
        if ':/' in filename or filename.startswith('\\\\'):
            # Filename is a pasted fullpath.  The first test finds paths that start with 'C:/' or 'omniverse://';
            # the second finds MS network paths that start like '\\analogfs\VENDORS\...'
            dst_root = os.path.dirname(filename)
        else:
            dst_root = os.path.dirname(f"{(dirname or '').rstrip('/')}/{filename}")
        # OM-65721: When downloading a single item, should use the filename provided
        dst_name = None
        # for single item, rename by user input
        if len(src_items) == 1:
            dst_name = os.path.basename(filename)
            _, src_ext = os.path.splitext(src_items[0].path)
            # make sure ext is included if user didn't input it
            # TODO: here the assumption is that we don't want to download a file as another file format, so
            # appending if the filename input didn't end with the current ext
            if not dst_name.endswith(src_ext):
                dst_name = dst_name + src_ext

        if src_items and dst_root:
            # prepare src_paths and dst_paths for download items
            src_paths = []
            dst_paths = []
            for src_item in src_items:
                src_paths.append(src_item.path)
                dst_root = dst_root.rstrip("/")
                if dst_name:
                    dst_path = f"{dst_root}/{dst_name}"
                # if not specified, or user typed in an empty name, use the source path basename instead
                else:
                    dst_path = f"{dst_root}/{os.path.basename(src_item.path)}"
                dst_paths.append(dst_path)

            try:
                # Callback to handle exceptions
                def __notify(results: List[Union[Exception, str]]):
                    for result in results:
                        if isinstance(result, Exception):
                            omni.kit.notification_manager.post_notification(str(result))

                # Callback to handle copy result
                def __copy_notify(src: str, dst: str, result: omni.client.Result):
                    if result == omni.client.Result.OK:
                        omni.kit.notification_manager.post_notification(f"{src} downloaded")
                    else:
                        omni.kit.notification_manager.post_notification(f"Error copying '{src}' to '{dst}': {result}")

                copy_items_with_callback(src_paths, dst_paths, callback=__notify, copy_callback=__copy_notify)
            except Exception as e:
                log_warn(f"Error encountered during download: {str(e)}")

    file_exporter = get_file_exporter()
    if file_exporter:
        # OM-65721: Pre-populate the filename field for download; use original file/folder name for single selection
        # and "<multiple selected>" to indicate multiple items are selected (in this case downloaded item will use)
        # their source names
        # TODO: Is it worth creating a constant (either on this class or in this module) for this?
        selected_filename = "<multiple selected>"
        is_single_selection = len(selections) == 1
        if is_single_selection:
            _, selected_filename = os.path.split(selections[0].path)

        # OM-73142: Resolve to the actual download directory
        download_dir = get_user_folders_dict().get("Downloads", "")

        file_exporter.show_window(
            title="Download Files",
            show_only_collections=["my-computer"],
            file_postfix_options=[None],
            file_extension_types=[("*", "All files")],
            export_button_label="Save",
            export_handler=lambda filename, dirname, **kwargs: on_download(selections, filename, dirname),
            filename_url=f"{download_dir}/{selected_filename}",
            enable_filename_input=is_single_selection,
            # OM-99158: Fix issue with apply button disabled when multiple items are selected for download
            show_only_folders=True,
        )


_open_readonly_usd_prompt = None

def _show_readonly_usd_prompt(ok_fn, middle_fn):
    global _open_readonly_usd_prompt
    _open_readonly_usd_prompt = Prompt(
        "Opening a Read Only File",
        "",
        [
            ("Open With New Edit Layer", "open_edit_layer.svg", ok_fn),
            ("Open Original File", "pencil.svg", middle_fn),
        ],
        modal=False
    )
    _open_readonly_usd_prompt.show()
