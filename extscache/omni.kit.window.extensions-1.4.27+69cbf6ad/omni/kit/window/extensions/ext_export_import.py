"""This module provides functionality to export and import extensions via a user interface in the omni.kit.window.extensions package."""

__all__ = []

import asyncio
import os

import carb
import carb.tokens
import omni.kit.app

from .common import get_omni_documents_path
from .utils import get_setting

# Store last user choosen folder for convenience between sessions
RECENT_EXPORT_PATH_KEY = "/persistent/exts/omni.kit.window.extensions/recentExportPath"


def _print_and_log(message):
    carb.log_info(message)
    print(message)


async def _ask_user_for_path(is_export: bool, apply_button_label="Choose", title=None):
    app = omni.kit.app.get_app()
    manager = app.get_extension_manager()
    if not manager.is_extension_enabled("omni.kit.window.filepicker"):
        manager.set_extension_enabled("omni.kit.window.filepicker", True)

        await app.next_update_async()
        await app.next_update_async()

    from omni.kit.window.file_exporter import get_file_exporter

    done = False
    choosen_path = None

    def on_click_cancel(f, d):
        nonlocal done
        done = True

    file_exporter = get_file_exporter()
    if not file_exporter:
        return ""

    if is_export:

        def on_click_open(filename: str, dirname: str, extension: str, selections):
            nonlocal done, choosen_path
            choosen_path = dirname
            done = True

        file_exporter.show_window(
            title or "Choose Folder",
            export_button_label=apply_button_label,
            export_handler=on_click_open,
            click_cancel_handler=on_click_cancel,
            show_only_folders=True,
            enable_filename_input=False,
        )
    else:

        def on_click_open(filename: str, dirname: str, extension: str, selections):
            nonlocal done, choosen_path
            choosen_path = os.path.join(dirname, f"{filename}{extension}")
            done = True

        file_exporter.show_window(
            title or "Choose Extension Zip Archive",
            export_button_label="Import",
            export_handler=on_click_open,
            click_cancel_handler=on_click_cancel,
            file_extension_types=[("*.zip", ".zip Archives (*.zip)")],
        )

    recent_path = get_setting(RECENT_EXPORT_PATH_KEY, None)
    if not recent_path:
        recent_path = get_omni_documents_path()

    while not done:
        await app.next_update_async()

    file_exporter.hide_window()

    if choosen_path:
        recent_path = os.path.dirname(choosen_path) if os.path.isfile(choosen_path) else choosen_path
        carb.settings.get_settings().set(RECENT_EXPORT_PATH_KEY, recent_path)

    return choosen_path


async def _export(ext_id: str):
    output = await _ask_user_for_path(is_export=True, apply_button_label="Export")

    if output:
        app = omni.kit.app.get_app()
        manager = app.get_extension_manager()
        archive_path = manager.pack_extension(ext_id, output)
        app.print_and_log(f"Extension: '{ext_id}' was exported to: '{archive_path}'")


async def _import():
    archive_path = await _ask_user_for_path(is_export=False, apply_button_label="Import")

    # Registry Local Cache Folder
    registry_cache = get_setting("/app/extensions/registryCacheFull", None)
    if not registry_cache:
        carb.log_error("Can't import extension, registry cache path is not set.")
        return

    if archive_path:
        omni.ext.unpack_extension(archive_path, registry_cache)
        omni.kit.app.get_app().print_and_log(f"Extension: '{archive_path}' was imported to: '{registry_cache}'")


def export_ext(ext_id: str):
    """Exports the specified extension.

    Args:
        ext_id (str): The identifier of the extension to export."""
    asyncio.ensure_future(_export(ext_id))


def import_ext():
    """Imports an extension from a user-selected zip archive.

    This function asynchronously triggers the import operation. It prompts the user to select an extension archive (.zip) using a file picker dialog. Once selected, it proceeds to unpack the extension into the registry cache folder. The function ensures the operation runs in the background without blocking the main thread.

    This is part of a larger system managing extensions, including exporting and maintaining a registry of available extensions.

    This function does not accept any arguments."""
    asyncio.ensure_future(_import())
