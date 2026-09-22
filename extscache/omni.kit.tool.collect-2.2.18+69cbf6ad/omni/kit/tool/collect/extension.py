"""This module provides classes and functions to facilitate the USD asset collection workflow within Omniverse Kit by offering UI components and logic to collect USD files and their dependencies into a single directory."""

import os
import asyncio
import weakref
import omni
import omni.usd
import omni.client
import carb
import toml
from pathlib import Path
from urllib.parse import unquote
import omni.kit.notification_manager as nm

from urllib.parse import unquote
from typing import Callable, List
from omni.kit.widget.prompt import PromptButtonInfo, PromptManager
from omni.kit.usd.collect import Collector, FlatCollectionTextureOptions, DefaultPrimOnlyOptions
from .main_window import CollectMainWindow
from .progress_popup import ProgressPopup
from omni.kit.menu.utils import MenuItemDescription
from .actions import ActionManager, ACTION_COLLECT_STAGE
from .folder_collect_helper import FolderCollectHelper
from pxr import Sdf

g_singleton = None

ICON_PATH = Path(__file__).parent.absolute().parent.parent.parent.parent.joinpath("icons")


def get_instance():
    """Returns the singleton instance of the collect extension.

    Returns:
        The singleton instance of the collect extension."""
    global g_singleton
    return g_singleton

def _exists_sync(path):
    try:
        result, entry = omni.client.stat(path)
        return result == omni.client.Result.OK
    except Exception:
        return False

class PublicExtension(omni.ext.IExt):
    """A class to handle USD asset collection in Omniverse.

    This class provides methods to collect USD files and their dependencies into a single directory, handling individual USDs, multiple USDs, and USDs within folders. It integrates with Omniverse Kit extensions to enhance the user experience with context menus and progress popups, offering a seamless asset collection workflow within the content browser. The class ensures that only writable USD file types can be collected and provides informative popups for unsupported files or other user feedback.
    """

    def on_startup(self):
        """Initializes the menus and action on extension startup."""
        self._main_window = None
        self._context_menu_name = None
        self._multi_files_progress_popup = None
        self._register_menus()
        self._action_manager = ActionManager()
        self._action_manager.on_startup(self)
        self._checkpoint_menu_name = None
        self._folder_collect_helper = None

        global g_singleton
        g_singleton = self

    def on_shutdown(self):
        """Clean up the menus and destroy the collect window on extension shutdown."""
        global g_singleton
        g_singleton = None

        content_window = self.get_content_window()
        if content_window and self._context_menu_name:
            content_window.delete_context_menu(self._context_menu_name)
            self._context_menu_name = None

            content_window.delete_checkpoint_menu(self._checkpoint_menu_name)
            self._checkpoint_menu_name = None

        if self._main_window:
            self._main_window.destroy()
            self._main_window = None

        omni.kit.menu.utils.remove_menu_items(self._file_menu_list, "File")

        self._action_manager.on_shutdown()

    def collect(self, filepath: str, finish_callback: Callable[[], None] = None) -> None:
        """
        Collect a usd file.
        Args:
            filepath: Path to usd file to be collected.
        """
        if not omni.usd.is_usd_writable_filetype(filepath):
            self._show_file_not_supported_popup()
        else:
            self._show_main_window(filepath, finish_callback)

    def _is_folder(self, path):
        result, entry = omni.client.stat(path)
        return result == omni.client.Result.OK and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN

    def _register_menus(self):
        content_window = self.get_content_window()
        if content_window:

            self._context_menu_name = content_window.add_context_menu(
                "Collect Asset",
                f"{ICON_PATH}/icoCollect.svg",
                lambda b, c: self._on_context_menu_click(b, c),
                lambda path: omni.usd.is_usd_writable_filetype(path) or self._is_folder(path),
            )

            def on_show(_, checkpoint_item):
                checkpoint_url = checkpoint_item.url
                client_url = omni.client.break_url(checkpoint_url)
                return omni.usd.is_usd_writable_filetype(client_url.path)

            self._checkpoint_menu_name = content_window.add_checkpoint_menu(
                "Collect Checkpoint",
                f"{ICON_PATH}/icoCollect.svg",
                lambda b, c: self._on_checkpoint_menu_click(b, c.get_full_url()),
                on_show,
            )

        self._file_menu_list = [
            MenuItemDescription(
                name="Collect As...",
                glyph="none.svg",
                appear_after="Save Flattened As...",
                onclick_action=("omni.kit.tool.collect", ACTION_COLLECT_STAGE),
            )
        ]

        omni.kit.menu.utils.add_menu_items(self._file_menu_list, "File")

    def _get_collection_dir(self, folder, usd_file_name):
        result = ""
        stage_name = os.path.splitext(usd_file_name)[0]
        if not folder:
            content_window = self.get_content_window()
            if content_window:
                folder = content_window.get_current_directory()
        if folder and not folder.endswith("/"):
            folder += "/"

        if folder:
            folder = omni.client.normalize_url(folder)
            result = f"{folder}Collected_{stage_name}"
        else:
            result = f"Collected_{stage_name}"
        return unquote(result)

    def _show_folder_exist_popup(
        self,
        usd_path,
        collect_dir,
        usd_only,
        flat_collection,
        material_only,
        texture_option,
        finish_callback: Callable[[], None] = None,
        default_prim_only=False,
        default_prim_option=DefaultPrimOnlyOptions.ROOT_LAYER_ONLY,
        usda_to_usdc=False,
    ):
        def on_confirm():
            self._start_collecting(
                usd_path,
                collect_dir,
                usd_only,
                flat_collection,
                material_only,
                texture_option,
                finish_callback,
                default_prim_only,
                default_prim_option,
                usda_to_usdc,
            )

        def on_cancel():
            self._show_main_window(usd_path)

        PromptManager.post_simple_prompt(
            "Overwrite",
            "The target directory already exists, do you want to overwrite it?",
            PromptButtonInfo("Confirm", on_confirm),
            PromptButtonInfo("Cancel", on_cancel),
            modal=False,
        )

    def _start_collecting(
        self,
        usd_path,
        collect_folder,
        usd_only,
        flat_collection,
        material_only,
        texture_option,
        finish_callback: Callable[[], None] = None,
        default_prim_only=False,
        default_prim_option=DefaultPrimOnlyOptions.ROOT_LAYER_ONLY,
        usda_to_usdc=False,
    ):
        progress_popup = self._show_progress_popup()
        progress_popup.status_text = "Collecting dependencies..."
        collector = Collector(
            usd_path,
            collect_folder,
            usd_only,
            flat_collection,
            material_only,
            texture_option=FlatCollectionTextureOptions(texture_option),
            default_prim_only=default_prim_only,
            default_prim_option=DefaultPrimOnlyOptions(default_prim_option),
            convert_usda_to_usdc=usda_to_usdc,
        )

        collector_weakref = weakref.ref(collector)

        def on_cancel():
            carb.log_info("Cancelling collector...")
            if not collector_weakref():
                return

            collector_weakref().cancel()

        progress_popup.set_cancel_fn(on_cancel)

        def on_progress(step, total):
            progress_popup.status_text = f"Collecting USD {unquote(os.path.basename(usd_path))}..."
            progress_popup.progress = step
            progress_popup.total_steps = total

        def on_finish():
            if finish_callback:
                finish_callback()

            progress_popup.hide()

            self._refresh_current_directory()

            if self._main_window:
                self._main_window.set_collect_fn(None)

            if not collector_weakref():
                return
            collector_weakref().destroy()

        asyncio.ensure_future(collector.collect(on_progress, on_finish))

    def _show_main_window(self, usd_path, finish_callback: Callable[[], None] = None):
        if not self._main_window:
            self._main_window = CollectMainWindow(None, None)

        def on_collect(
            collect_folder,
            usd_only,
            flat_collection,
            material_only,
            texture_option,
            default_prim_only,
            default_prim_option,
            usda_to_usdc=False,
        ):
            existed = _exists_sync(collect_folder)
            if existed:
                self._show_folder_exist_popup(
                    usd_path,
                    collect_folder,
                    usd_only,
                    flat_collection,
                    material_only,
                    texture_option,
                    finish_callback,
                    default_prim_only,
                    default_prim_option,
                    usda_to_usdc,
                )
            else:
                self._start_collecting(
                    usd_path,
                    collect_folder,
                    usd_only,
                    flat_collection,
                    material_only,
                    texture_option,
                    finish_callback,
                    default_prim_only,
                    default_prim_option,
                    usda_to_usdc,
                )

        self._main_window.set_collect_fn(on_collect)

        usd_file_name = Sdf.Layer.GetDisplayNameFromIdentifier(usd_path)
        if Sdf.Layer.IsAnonymousLayerIdentifier(usd_path):
            usd_file_folder = None
        else:
            usd_file_folder = os.path.dirname(usd_path)
        default_folder = self._get_collection_dir(usd_file_folder, usd_file_name)
        self._main_window.show(default_folder)

    def _on_checkpoint_menu_click(self, menu, value):
        self.collect(value)

    def _on_context_menu_click(self, menu, value):
        content_window = self.get_content_window()
        if not content_window:
            self.collect(value)
        selections = content_window.get_current_selections()
        if len(selections) > 1:
            first_usd_path = selections[0]
            usd_file_name = Sdf.Layer.GetDisplayNameFromIdentifier(first_usd_path)
            stage_name = os.path.splitext(usd_file_name)[0]
            target_folder = os.path.dirname(first_usd_path) + "/"
            self.collect_multiple(selections, stage_name, target_folder)
        elif self._is_folder(value):
            self.collect_multiple_in_folder(value)
        else:
            self.collect(value)

    def _refresh_current_directory(self):
        content_window = self.get_content_window()
        if content_window:
            content_window.refresh_current_directory()

    def _show_progress_popup(self):
        progress_popup = ProgressPopup("Collecting")
        progress_popup.progress = 0
        progress_popup.show()

        return progress_popup

    def _show_file_not_supported_popup(self):
        nm.post_notification(
            "Only writable USD file format (.usd, usda, usdc, etc) can be collected currently.",
            status=nm.NotificationStatus.WARNING,
        )

    def get_content_window(self):
        """
        Retrieves the content window instance.

        Returns:
            :'obj': The content window instance.
        """
        try:
            import omni.kit.window.content_browser as content

            return content.get_content_window()
        except Exception as e:
            pass

        return None

    # Get the content folder path that in ov launcher's settings
    def get_content_folder(self):
        """
        Retrieves the content folder path that in ov launcher's settings.

        Returns:
            str: The content folder path.
        """
        try:
            global_config_path = carb.tokens.get_tokens_interface().resolve("${omni_global_config}")

            omniverse_config_path = os.path.join(global_config_path, "omniverse.toml").replace("\\", "/")
            contents = toml.load(omniverse_config_path)
            folder = contents.get("paths").get("content_root")
            if not folder.endswith("/"):
                folder += "/"
            folder = omni.client.normalize_url(folder)

            # Hard-decoding url currently since combine_urls will encode url
            folder = unquote(folder)

            folder.replace("\\", "/")
            return folder
        except:
            return None

    def collect_multiple(
        self, filepaths: str, folder_name: str, target_folder: str = "", finish_callback: Callable[[], None] = None
    ) -> None:
        """
        Collect usd files.
        Args:
            filepaths: Paths to usd file to be collected.
            folder_name: Target folder name to save collect files.
            target_folder: Target folder to save collect folder.
        """
        if len(filepaths) == 0:
            carb.log_warn("Collect paths' list is empty")
            return
        if target_folder == "":
            target_folder = self.get_content_folder()
        if not target_folder:
            carb.log_warn("Collect target folder is invalid")
            return
        if not omni.usd.is_usd_writable_filetype(filepaths[0]):
            self._show_file_not_supported_popup()
        else:
            self._show_main_multi_files_window(filepaths, folder_name, target_folder, finish_callback)

    def _show_main_multi_files_window(
        self, usd_paths, folder_name, target_folder, finish_callback: Callable[[], None] = None
    ):
        if not self._main_window:
            self._main_window = CollectMainWindow(None, None)

        def path_generator(paths):
            for path in paths:
                yield path

        path_provider = path_generator(usd_paths)
        total = len(usd_paths)
        current_index = 1

        def on_collect(
            collect_folder,
            usd_only,
            flat_collection,
            material_only,
            texture_option,
            default_prim_only,
            default_prim_option,
            usda_to_usdc=False,
        ):
            existed = _exists_sync(collect_folder)
            if existed:
                self._show_folder_exist_popup_for_multi_files(
                    current_index,
                    total,
                    path_provider,
                    collect_folder,
                    usd_only,
                    flat_collection,
                    material_only,
                    texture_option,
                    finish_callback,
                    default_prim_only,
                    default_prim_option,
                    usda_to_usdc,
                )
            else:
                self._start_collecting_multi_files(
                    current_index,
                    total,
                    path_provider,
                    collect_folder,
                    usd_only,
                    flat_collection,
                    material_only,
                    texture_option,
                    finish_callback,
                    default_prim_only,
                    default_prim_option,
                    usda_to_usdc,
                )

        self._main_window.set_collect_fn(on_collect)
        self._main_window.show(f"{target_folder}Collected_{folder_name}")

    def _show_folder_exist_popup_for_multi_files(
        self,
        current_index,
        total,
        path_provider,
        collect_dir,
        usd_only,
        flat_collection,
        material_only,
        texture_option,
        finish_callback,
        default_prim_only,
        default_prim_option=DefaultPrimOnlyOptions.ROOT_LAYER_ONLY,
        usda_to_usdc=False,
    ):
        def on_confirm():
            self._start_collecting_multi_files(
                current_index,
                total,
                path_provider,
                collect_dir,
                usd_only,
                flat_collection,
                material_only,
                texture_option,
                finish_callback,
                default_prim_only,
                default_prim_option,
                usda_to_usdc,
            )

        def on_cancel():
            self._main_window.show(collect_dir)

        PromptManager.post_simple_prompt(
            "Overwrite",
            "The target directory already exists, do you want to overwrite it?",
            PromptButtonInfo("Confirm", on_confirm),
            PromptButtonInfo("Cancel", on_cancel),
            modal=False,
        )

    def _get_multi_files_progress_popup(self):
        if not self._multi_files_progress_popup:
            self._multi_files_progress_popup = ProgressPopup("Collecting")
        return self._multi_files_progress_popup

    def _start_collecting_multi_files(
        self,
        current_index,
        total,
        path_provider,
        collect_dir,
        usd_only,
        flat_collection,
        material_only,
        texture_option,
        finish_callback,
        default_prim_only,
        default_prim_option=DefaultPrimOnlyOptions.ROOT_LAYER_ONLY,
        usda_to_usdc=False,
    ):
        try:
            current_usd_path = next(path_provider)
        except:
            return
        progress_popup = self._get_multi_files_progress_popup()
        progress_popup.show()
        progress_popup.status_text = f"Collecting {current_index}/{total}..."
        progress_popup.progress = current_index
        progress_popup.total_steps = total
        collector = Collector(
            current_usd_path,
            collect_dir,
            usd_only,
            flat_collection,
            material_only,
            texture_option=FlatCollectionTextureOptions(texture_option),
            default_prim_only=default_prim_only,
            default_prim_option=default_prim_option,
            convert_usda_to_usdc=usda_to_usdc,
        )

        collector_weakref = weakref.ref(collector)

        def on_cancel():
            carb.log_info("Cancelling collector...")
            # Set to an empty generator to end the recursion
            path_provider = lambda: (yield from [])
            if not collector_weakref():
                return

            collector_weakref().cancel()
            if self._folder_collect_helper:
                self._folder_collect_helper.destroy()
            self._folder_collect_helper = None

        progress_popup.set_cancel_fn(on_cancel)

        def on_progress(step, total):
            progress_popup.status_text = f"Collecting USD {os.path.basename(current_usd_path)}..."

        def on_finish():
            if collector_weakref():
                collector_weakref().destroy()
            if current_index < total:
                self._start_collecting_multi_files(
                    current_index + 1,
                    total,
                    path_provider,
                    collect_dir,
                    usd_only,
                    flat_collection,
                    material_only,
                    texture_option,
                    finish_callback,
                    default_prim_only,
                    default_prim_option,
                    usda_to_usdc,
                )
            else:
                if finish_callback:
                    finish_callback()
                progress_popup.hide()

                if self._main_window:
                    self._main_window.set_collect_fn(None)

                if not collector_weakref():
                    return
                collector_weakref().destroy()

        asyncio.ensure_future(collector.collect(on_progress, on_finish))

    def collect_multiple_in_folder(
        self,
        folder: str,
        target_name: str = "",
        target_folder: str = "",
        finish_get_files_callback: Callable[[], None] = None,
        finish_collect_callback: Callable[[], None] = None,
    ) -> None:
        """
        Collect all usd files in a folder.
        Args:
            folder: Paths to contain usd files to be collected.
            target_name: Target folder name to save collect files.
            target_folder: Target folder to save collect folder.
            finish_get_files_callback: Will called when finish get all files in folder.
            finish_collect_callback: Will called when finish collect all files in folder.
        """

        def collect_files_internal(filepaths: List[str]) -> None:
            nonlocal target_name
            nonlocal target_folder
            if not target_name:
                target_name = os.path.basename(folder)
            if not target_folder:
                target_folder = os.path.dirname(folder) + "/"
            self.collect_multiple(filepaths, target_name, target_folder, finish_callback=finish_collect_callback)

        self._folder_collect_helper = FolderCollectHelper(
            folder,
            omni.usd.is_usd_writable_filetype,
            collect_files_internal,
            finish_get_files_callback,
            self._get_multi_files_progress_popup(),
        )
