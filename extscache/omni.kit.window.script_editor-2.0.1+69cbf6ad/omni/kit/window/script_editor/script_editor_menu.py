import os

import omni.client
from omni.kit.window.file_exporter import get_file_exporter
from omni.kit.window.file_importer import get_file_importer


class MenuOptions:
    def __init__(self, **kwargs):
        self._dialog = None
        self._current_filename = None
        self._current_dir = None
        self.load_script = kwargs.pop("load_script", None)
        self.save_script = kwargs.pop("save_script", None)
        self.get_file_path = kwargs.pop("get_file_path", None)

    def destroy(self) -> None:
        if self._dialog:
            self._dialog.destroy_dialog()

    def __on_apply_save(
        self,
        filename: str,
        dir: str,
        extension: str,
        selections: list,
    ) -> None:
        """Called when the user press "Export" in the pick filename dialog"""
        # don't accept as long as no filename is selected
        if not filename or not dir:
            return

        # add the file extension if missing
        if not filename.lower().endswith(".py"):
            filename += ".py"

        self._current_filename = filename
        self._current_dir = dir

        # add a trailing slash for the client library
        if dir[-1] != os.sep:
            dir = dir + os.sep
        current_export_path = omni.client.combine_urls(dir, filename)

        self.save_script(current_export_path)

    def __on_apply_load(self, filename: str, dir: str, selections: list) -> None:
        """Called when the user press "Export" in the pick filename dialog"""

        # don't accept as long as no filename is selected
        if not filename or not dir:
            return

        # add a trailing slash for the client library
        if dir[-1] != os.sep:
            dir = dir + os.sep
        # OM-93082: Fix issue with omni.client.combine_urls will eat up the subfolder path for omniverse urls if
        #  the dirname is ending with "\" on windows
        dir = dir.replace("\\", "/")

        current_path = omni.client.combine_urls(dir, filename)
        if omni.client.stat(current_path)[0] != omni.client.Result.OK:
            # add the file extension if missing
            if self._dialog.current_filter_option == 0 and not filename.lower().endswith(".py"):
                filename += ".py"
                current_path = omni.client.combine_urls(dir, filename)
                if omni.client.stat(current_path)[0] != omni.client.Result.OK:
                    # Still can't find
                    return

        self._current_filename = filename
        self._current_dir = dir

        self.load_script(current_path)

    def __menu_filter_files(self, filename: str, filter_postfix: str, filter_ext: str) -> bool:
        if filter_ext == "*.py":
            # Show only files with listed extensions
            return filename.endswith(".py")
        else:
            # Show All Files (*)
            return True

    def menu_open(self) -> None:
        """Open "Open" dialog"""
        if self._dialog:
            self._dialog.destroy_dialog()

        self._dialog = get_file_importer()
        if self._dialog:
            open_path = ""
            if self._current_dir and self._current_filename:
                open_path = f"{self._current_dir}/{self._current_filename}"
            elif self._current_dir:
                open_path = self._current_dir
            elif self._current_filename:
                open_path = self._current_filename

            self._dialog.show_window(
                title="Open...",
                import_button_label="Open",
                import_handler=self.__on_apply_load,
                file_extension_types=[("*.py", "Python Files"), ("*", "All Files")],
                file_filter_handler=self.__menu_filter_files,
                filename_url=open_path,
            )

    def menu_save(self) -> None:
        file_path = self.get_file_path()
        if file_path:
            self.save_script(file_path)
        else:
            self.menu_save_as()

    def menu_save_as(self) -> None:
        """Open "Save As" dialog"""
        if self._dialog:
            self._dialog.destroy_dialog()

        self._dialog = get_file_exporter()
        if self._dialog:
            save_path = ""
            if self._current_dir and self._current_filename:
                save_path = f"{self._current_dir}/{self._current_filename}"
            elif self._current_dir:
                save_path = self._current_dir
            elif self._current_filename:
                save_path = self._current_filename

            self._dialog.show_window(
                title="Save As...",
                export_button_label="Save",
                export_handler=self.__on_apply_save,
                file_extension_types=[("*.py", "Python Files"), ("*", "All Files")],
                filename_url=save_path,
            )
