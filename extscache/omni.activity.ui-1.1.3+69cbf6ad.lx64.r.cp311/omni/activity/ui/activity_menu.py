import carb.input
import omni.client
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.filepicker import FilePickerDialog

import json
import os


class ActivityMenuOptions:
    def __init__(self, **kwargs):
        self._pick_folder_dialog = None
        self._current_filename = None
        self._current_dir = None
        self.load_data = kwargs.pop("load_data", None)
        self.get_save_data = kwargs.pop("get_save_data", None)

    def destroy(self):
        if self._pick_folder_dialog:
            self._pick_folder_dialog.destroy()

    def __menu_save_apply_filename(self, filename: str, dir: str):
        """Called when the user presses "Save" in the pick filename dialog"""

        # don't accept as long as no filename is selected
        if not filename or not dir:
            return

        if self._pick_folder_dialog:
            self._pick_folder_dialog.hide()

        # add the file extension if missing
        extension = filename.split(".")[-1]
        filter = "json" if self._pick_folder_dialog and self._pick_folder_dialog.current_filter_option else "activity"
        if extension != filter:
            filename = filename + "." + filter

        self._current_filename = filename
        self._current_dir = dir

        # add a trailing slash for the client library
        if dir[-1] != os.sep:
            dir = dir + os.sep
        current_export_path = omni.client.combine_urls(dir, filename)

        self.save(current_export_path)

    def __menu_open_apply_filename(self, filename: str, dir: str):
        """Called when the user presses "Open" in the pick filename dialog"""

        # don't accept as long as no filename is selected
        if not filename or not dir:
            return
        if self._pick_folder_dialog:
            self._pick_folder_dialog.hide()

        # add a trailing slash for the client library
        if dir[-1] != os.sep:
            dir = dir + os.sep

        current_path = omni.client.combine_urls(dir, filename)
        if omni.client.stat(current_path)[0] != omni.client.Result.OK:
            # add the file extension if missing

            extension = filename.split(".")[-1]
            filter = "json" if self._pick_folder_dialog and self._pick_folder_dialog.current_filter_option else "activity"
            if extension != filter:
                filename = filename + "." + filter
                current_path = omni.client.combine_urls(dir, filename)
                if omni.client.stat(current_path)[0] != omni.client.Result.OK:
                    # Still can't find
                    return

        self._current_filename = filename
        self._current_dir = dir

        self.load(current_path)

    def __menu_filter_files(self, item: FileBrowserItem) -> bool:
        """Used by pick folder dialog to hide all the files"""
        if not item or item.is_folder:
            return True

        filter = ".json" if self._pick_folder_dialog and self._pick_folder_dialog.current_filter_option else ".activity"
        if item.path.endswith(filter):
            return True
        else:
            return False

    def menu_open(self):
        """Open "Open" dialog"""
        if self._pick_folder_dialog:
            self._pick_folder_dialog.destroy()

        self._pick_folder_dialog = FilePickerDialog(
            "Open...",
            allow_multi_selection=False,
            apply_button_label="Open",
            click_apply_handler=self.__menu_open_apply_filename,
            item_filter_options=["ACTIVITY file (*.activity)", "JSON file (*.json)"],
            item_filter_fn=self.__menu_filter_files,
            current_filename=self._current_filename,
            current_directory=self._current_dir,
        )

    def menu_save(self):
        """Open "Save" dialog"""
        if self._pick_folder_dialog:
            self._pick_folder_dialog.destroy()

        self._pick_folder_dialog = FilePickerDialog(
            "Save As...",
            allow_multi_selection=False,
            apply_button_label="Save",
            click_apply_handler=self.__menu_save_apply_filename,
            item_filter_options=["ACTIVITY file (*.activity)", "JSON file (*.json)"],
            item_filter_fn=self.__menu_filter_files,
            current_filename=self._current_filename,
            current_directory=self._current_dir,
        )

    def save(self, filename: str):
        """Save the current model to external file"""
        data = self.get_save_data()
        if not data:
            return
        payload = bytes(json.dumps(data, sort_keys=True, indent=4).encode("utf-8"))
        if not payload:
            return
        # Save to the file
        result = omni.client.write_file(filename, payload)
        if result != omni.client.Result.OK:
            carb.log_error(f"[omni.activity.ui] The activity cannot be written to {filename}, error code: {result}")
            return
        carb.log_info(f"[omni.activity.ui] The activity saved to {filename}")

    def load(self, filename: str):
        """Load the model from the file"""
        result, _, content = omni.client.read_file(filename)

        if result != omni.client.Result.OK:
            carb.log_error(f"[omni.activity.ui] Can't read the activity file {filename}, error code: {result}")
            return

        data = json.loads(memoryview(content).tobytes().decode("utf-8"))

        self.load_data(data)
