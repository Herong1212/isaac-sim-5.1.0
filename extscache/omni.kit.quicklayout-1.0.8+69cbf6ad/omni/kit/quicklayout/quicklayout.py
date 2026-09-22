# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from omni.ui.workspace_utils import CompareDelegate
import carb
import carb.tokens
import json
import omni.client
from omni.kit.notification_manager import post_notification, NotificationStatus
import omni.ui as ui
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omni.kit.widget.filebrowser import FileBrowserItem

class QuickLayout:
    """Namespace that has the methods to load and save the layout"""

    def __init__(self):
        self._dialog = None

    def destroy(self): # pragma: no cover
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None

    def __on_filter_item(self, item: "FileBrowserItem") -> bool:
        if not item or item.is_folder:
            return True
        if self._dialog.current_filter_option == 0:
            # Show only files with listed extensions
            if item.path.endswith(".json"):
                return True
            else:
                return False
        else:
            # Show All Files (*)
            return True

    @staticmethod
    def __get_workspace_dir() -> str:
        """Return the workspace file"""
        token = carb.tokens.get_tokens_interface()
        dir = token.resolve("${data}")
        # FilePickerDialog needs the capital drive. In case it's linux, the
        # first letter will be / and it's still OK.
        dir = dir[:1].upper() + dir[1:]
        return dir

    @staticmethod
    def __get_workspace_file() -> str:
        """Return the workspace file"""
        dir = QuickLayout.__get_workspace_dir()
        return f"{dir}/user.layout.json"

    def __on_apply_save(self, filename: str, dir: str):
        """Called when the user presses the Save button in the dialog"""
        # Get the file extension from the filter
        if self._dialog.current_filter_option == 0 and not filename.lower().endswith(".json"):
            filename += ".json"

        self._dialog.hide()
        self.save_file(omni.client.combine_urls(dir if dir.endswith("/") else dir+"/", filename))

    def __on_apply_load(self, filename, dir):
        """Called when the user presses the Load button in the dialog"""
        self._dialog.hide()
        self.load_file(omni.client.combine_urls(dir if dir.endswith("/") else dir+"/", filename))

    @staticmethod
    def save_file(workspace_file: str):
        """Save the layout to the workspace file"""
        workspace_dump = ui.Workspace.dump_workspace()
        payload = bytes(json.dumps(workspace_dump, sort_keys=True, indent=2).encode("utf-8"))
        result = omni.client.write_file(workspace_file, payload)
        if result != omni.client.Result.OK: # pragma: no cover
            carb.log_error(f"[quicklayout] The workspace cannot be written to {workspace_file}, error code: {result}")
            return
        carb.log_info(f"[quicklayout] The workspace saved to {workspace_file}")

    @staticmethod
    def load_file(workspace_file: str, keep_windows_open=False):
        """Load the layout from the workspace file"""
        result, _, content = omni.client.read_file(workspace_file)

        if result != omni.client.Result.OK: # pragma: no cover
            if result == omni.client.Result.ERROR_NOT_FOUND:
                message = f"[quicklayout] The workspace file {workspace_file} does not exist. You must save a quick layout first before attempting to load."
                post_notification(message, status=NotificationStatus.WARNING)
                carb.log_warn(message)
                return

            carb.log_error(f"[quicklayout] Can't read the workspace file {workspace_file}, error code: {result}")
            return

        data = json.loads(memoryview(content).tobytes().decode("utf-8"))
        ui.Workspace.restore_workspace(data, keep_windows_open)

        carb.log_info(f"[quicklayout] The workspace is loaded from {workspace_file}")

    @staticmethod
    def compare_file(workspace_file: str, compare_delegate: CompareDelegate=CompareDelegate()):
        """Load the layout from the workspace file"""
        result, _, content = omni.client.read_file(workspace_file)

        if result != omni.client.Result.OK: # pragma: no cover
            carb.log_error(f"[quicklayout] Can't read the workspace file {workspace_file}, error code: {result}")
            return

        data = json.loads(memoryview(content).tobytes().decode("utf-8"))
        result = ui.Workspace.compare_workspace(data, compare_delegate=compare_delegate)
        carb.log_info(f"[quicklayout] compared {workspace_file} with workspace")
        return result

    def save(self, menu: str, value: bool):
        """Save layout with the dialog"""
        # Remove previously opened dialog
        self.destroy()

        try:
            from omni.kit.window.filepicker import FilePickerDialog
            self._dialog = FilePickerDialog(
                "Select File to Save Layout",
                apply_button_label="Save",
                current_directory=QuickLayout.__get_workspace_dir(),
                click_apply_handler=self.__on_apply_save,
                item_filter_options=["JSON Files (*.json)", "All Files (*)"],
                item_filter_fn=self.__on_filter_item,
            )
        except ImportError:
            carb.log_info(f"[quicklayout] Can't import filepicker for save layout with the dialog")

    def load(self, menu: str, value: bool):
        """Load layout with the dialog"""
        # Remove previously opened dialog
        self.destroy()

        try:
            from omni.kit.window.filepicker import FilePickerDialog
            self._dialog = FilePickerDialog(
                "Select File to Load Layout",
                apply_button_label="Load",
                current_directory=QuickLayout.__get_workspace_dir(),
                click_apply_handler=self.__on_apply_load,
                item_filter_options=["JSON Files (*.json)", "All Files (*)"],
                item_filter_fn=self.__on_filter_item,
            )
        except ImportError:
            carb.log_info(f"[quicklayout] Can't import filepicker for load layout with the dialog")

    @staticmethod
    def quick_save(menu: str, value: bool):
        workspace_file = QuickLayout.__get_workspace_file()
        QuickLayout.save_file(workspace_file)

    @staticmethod
    def quick_load(menu: str, value: bool):
        workspace_file = QuickLayout.__get_workspace_file()
        QuickLayout.load_file(workspace_file)
