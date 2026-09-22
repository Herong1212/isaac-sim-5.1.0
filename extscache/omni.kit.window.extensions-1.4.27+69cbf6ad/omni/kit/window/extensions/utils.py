# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# pylint: disable=protected-access, access-member-before-definition

"""This module provides utility functions for managing windows, extensions, subprocesses, settings, and clipboard operations within the omni.kit application environment."""

__all__ = [
    "ext_id_to_fullname",
    "open_in_vscode_if_enabled",
    "show_ok_popup",
    "show_user_input_popup",
]

import asyncio
import contextlib
import glob
import os
import platform
import shutil
import subprocess
from functools import lru_cache
from typing import Callable, Tuple

import carb
import carb.dictionary
import carb.settings
import omni.kit.commands


def call_once_with_delay(fn: Callable, delay: float):
    """Call function once after `delay` seconds.
    If this function called again before `delay` is passed the timer gets reset.

    Args:
        fn (Callable): The function to be called.
        delay (float): The time in seconds to wait before calling `fn`."""

    async def _delayed_refresh():
        await asyncio.sleep(delay)
        fn()

    with contextlib.suppress(Exception):
        fn._delay_call_task.cancel()

    fn._delay_call_task = asyncio.ensure_future(_delayed_refresh())


@lru_cache()
def is_windows():
    return platform.system().lower() == "windows"


def run_process(args):
    """Runs a subprocess with the provided arguments.

    Args:
        args (List[str]): The command line arguments for the subprocess."""
    print(f"running process: {args}")
    kwargs = {"close_fds": False}
    if is_windows():
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(args, **kwargs)  # pylint: disable=consider-using-with


def version_to_str(version: Tuple[int, int, int, str, str]) -> str:
    """Generate string `0.0.0-tag+tag`

    Args:
        version (Tuple[int, int, int, str, str]): Version info to convert to string.

    Returns:
        str: String representation of the version."""
    delimiters = ("", ".", ".", "-", "+")
    return "".join(f"{d}{v}" for d, v in zip(delimiters, version) if str(v) and v is not None)


def ext_id_to_fullname(ext_id: str) -> str:
    """Converts an extension ID to its full name.

    Args:
        ext_id (str): The unique identifier for the extension.

    Returns:
        str: The full name of the extension."""
    return omni.ext.get_extension_name(ext_id)


def ext_id_to_name_version(ext_id: str) -> Tuple[str, str]:
    """Convert 'omni.foo-tag-1.2.3' to 'omni.foo-tag' and '1.2.3'

    Args:
        ext_id (str): The unique identifier of the extension.

    Returns:
        Tuple[str, str]: A tuple containing the extension name and version."""
    a, b, *rest = ext_id.split("-")
    if b:
        if not b[0:1].isdigit():
            return f"{a}-{b}", "-".join(rest)
        return a, "-".join([b] + rest)
    return a, ""


def get_ext_info_dict(ext_manager, ext_info) -> Tuple[carb.dictionary.Item, bool]:
    """Gets a dictionary containing extension information.

    Args:
        ext_manager: The manager responsible for extensions.
        ext_info: Information about the specific extension.

    Returns:
        Tuple[carb.dictionary.Item, bool]: A tuple containing the extension dictionary and a boolean indicating existence.
    """
    ext_dict = ext_manager.get_extension_dict(ext_info["id"])
    if ext_dict is not None:
        return (ext_dict, True)
    return (ext_manager.get_registry_extension_dict(ext_info["package_id"]), False)


def get_setting(path, default=None):
    """Retrieves a setting value based on its path, or returns a default value if not found.

    Args:
        path (str): The path of the setting to retrieve.
        default: The default value to return if the setting is not found."""
    setting = carb.settings.get_settings().get(path)
    return setting if setting is not None else default


@contextlib.contextmanager
def change_setting(path, value):
    """Changes a setting value for the execution block and then reverts it back.

    This function is a context manager.
    """
    old_value = carb.settings.get_settings().get(path)
    carb.settings.get_settings().set(path, value)
    try:
        yield
    finally:
        carb.settings.get_settings().set(path, old_value)


def set_default_and_get_setting(path, default=None):
    """Sets a default value for a given setting path and retrieves the current setting.

    Args:
        path (str): The settings path to query.
        default: The default value to set if the setting isn't already set."""
    settings = carb.settings.get_settings()
    settings.set_default(path, default)
    return settings.get(path)


def clip_text(s, max_count=80):
    """Clips a text to a specified maximum length.

    Args:
        s (str): The string to be clipped.
        max_count (int, optional): The maximum allowed length of the string. Defaults to 80."""
    return s[:max_count] + ("..." if len(s) > max_count else "")


def open_file_using_os_default(path: str):  # pragma: no cover
    """Opens a file using the OS's default program.

    Args:
        path (str): The file system path to the file to be opened."""
    if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", path))
    elif platform.system() == "Windows":  # Windows
        os.startfile(path)  # noqa: PLE1101
    else:  # linux variants
        subprocess.call(("xdg-open", path))


def open_url(url):  # pragma: no cover
    """Opens the given URL in the default web browser.

    Args:
        url (str): The URL to be opened."""
    import webbrowser

    webbrowser.open(url)


def open_using_os_default(path: str):  # pragma: no cover
    """Opens the specified path using the OS default program.

    Args:
        path (str): The file or directory path to open."""
    if os.path.isfile(path):
        open_file_using_os_default(path)
    else:
        # open dir
        import webbrowser

        webbrowser.open(path)


def open_in_vscode(path: str):  # pragma: no cover
    """Opens the given file or directory in VSCode.

    Args:
        path (str): The file or directory path to open."""
    subprocess.call(["code", path], shell=is_windows())


@lru_cache()
def is_vscode_installed():  # pragma: no cover
    """is vscode installed."""
    try:
        cmd = ["code", "--version"]
        return (
            subprocess.call(
                cmd, shell=is_windows(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL
            )
            == 0
        )
    except FileNotFoundError:  # pragma: no cover
        return False


def _search_path_entry_up(path, entry, max_steps_up=3):
    for _ in range(0, max_steps_up + 1):
        if os.path.exists(os.path.join(path, entry)):
            return os.path.normpath(path)
        new_path = os.path.normpath(os.path.join(path, ".."))
        if new_path == path:
            break
        path = new_path
    return None


def open_in_vscode_if_enabled(path: str, prefer_vscode: bool = True):  # pragma: no cover
    """Opens the specified path in VSCode if preferred and installed, otherwise using the OS default.

    Args:
        path (str): The filesystem path to be opened.
        prefer_vscode (bool): Flag indicating if VSCode should be preferred."""
    if carb.settings.get_settings().get("/persistent/exts/omni.kit.window.extensions/openInVSCode"):
        if prefer_vscode and is_vscode_installed():
            # Search for .vscode folder few folders up to open project instead of just extension
            # 5 steps is enough for '_build/window/release/exts/omni.foo' for instance
            if os.path.isdir(path):
                path = _search_path_entry_up(path, ".vscode", max_steps_up=5) or path
            open_in_vscode(path)
        else:
            open_using_os_default(path)


def copy_text(text):
    """Copies the given text to the clipboard.

    Args:
        text (str): The text to be copied."""
    omni.kit.clipboard.copy(text)


def cleanup_folder(path):
    """Removes all files and folders within the specified directory.

    Args:
        path (str): The directory path to clean up."""
    try:
        for p in glob.glob(f"{path}/*"):
            if os.path.isdir(p):
                if omni.ext.is_link(p):
                    omni.ext.destroy_link(p)
                else:
                    shutil.rmtree(p)
            else:
                os.remove(p)
    except Exception as exc:  # pylint: disable=broad-except
        carb.log_warn(f"Unable to clean up files: {path}: {exc}")  # pragma: no cover


@lru_cache()
def get_extpath_git_ext():
    try:
        import omni.kit.extpath.git as git_ext

        return git_ext
    except ImportError:  # pragma: no cover
        return None


async def _load_popup_dialog_ext():
    app = omni.kit.app.get_app()
    manager = app.get_extension_manager()
    if not manager.is_extension_enabled("omni.kit.window.popup_dialog"):  # pragma: no cover
        manager.set_extension_enabled("omni.kit.window.popup_dialog", True)

        await app.next_update_async()
        await app.next_update_async()


async def show_ok_popup(title, message, **dialog_kwargs):  # pragma: no cover
    """Displays an OK popup dialog with a title and message.

    Args:
        title (str): The title of the popup.
        message (str): The content message of the popup.

    Keyword Args:
        disable_cancel_button (bool): If True, the cancel button will be hidden."""
    await _load_popup_dialog_ext()
    from omni.kit.window.popup_dialog import MessageDialog

    app = omni.kit.app.get_app()

    done = False

    def on_click(d):
        nonlocal done
        done = True

    dialog_kwargs.setdefault("disable_cancel_button", True)
    dialog = MessageDialog(title=title, message=message, ok_handler=on_click, **dialog_kwargs)

    dialog.show()

    while not done:
        await app.next_update_async()

    dialog.destroy()


async def show_user_input_popup(title, label, default):
    """Displays a popup dialog for user input.

    Args:
        title (str): The title of the popup dialog.
        label (str): The label displayed above the input field.
        default (str): The default value populated in the input field.
    """
    await _load_popup_dialog_ext()
    from omni.kit.window.popup_dialog import InputDialog

    app = omni.kit.app.get_app()

    value = None

    def on_click(dialog: InputDialog):
        nonlocal value
        value = dialog.get_value()

    dialog = InputDialog(
        message=title,
        pre_label=label,
        post_label="",
        default_value=default,
        ok_handler=on_click,
        ok_label="Ok",
    )

    dialog.show()

    while not value:
        await app.next_update_async()

    dialog.destroy()

    return value
