import os
import pathlib

import carb
import carb.settings
import omni.ui as ui
import omni.client
from omni.mdl import pymdlsdk
from omni.ui import color as cl

from .. import material_config_utils
from . material_config_widget import EditableListItemDelegate, EditableListModel, EditableListWidget


class MdlPathItem(ui.AbstractItem):
    _URLPREFIXES = ("omniverse://", "http://", "https://")

    def __init__(self, text):
        super().__init__()

        path = ""
        if not omni.client.is_local_url(text) and omni.client.is_valid_url(text):
            path = text
        else:
            path = pathlib.PurePath(text).as_posix()

        self.name_model = ui.SimpleStringModel(path)


class MdlDefaultPathListModel(ui.AbstractItemModel):
    SOURCE_MDL_SYSTEM_PATH = 0
    SOURCE_MDL_USER_PATH = 1
    SOURCE_ADDITIONAL_SYSTEM_PATHS = 2
    SOURCE_ADDITIONAL_USER_PATHS = 3
    SOURCE_RENDERER_REQUIRED = 4
    SOURCE_RENDERER_TEMPLATES = 5

    def __init__(self, mode):
        super().__init__()

        self._SETTING_NAME_MAP = {
            self.SOURCE_ADDITIONAL_SYSTEM_PATHS: "/app/mdl/additionalSystemPaths",
            self.SOURCE_ADDITIONAL_USER_PATHS: "/app/mdl/additionalUserPaths",
            self.SOURCE_RENDERER_REQUIRED: "/renderer/mdl/searchPaths/required",
            self.SOURCE_RENDERER_TEMPLATES: "/renderer/mdl/searchPaths/templates"
        }

        _FN_MAP = {
            self.SOURCE_MDL_SYSTEM_PATH: self._get_paths_from_mdl_config,
            self.SOURCE_MDL_USER_PATH: self._get_paths_from_mdl_config,
            self.SOURCE_ADDITIONAL_SYSTEM_PATHS: self._get_paths_from_array_setting,
            self.SOURCE_ADDITIONAL_USER_PATHS: self._get_paths_from_array_setting,
            self.SOURCE_RENDERER_REQUIRED: self._get_paths_from_setting,
            self.SOURCE_RENDERER_TEMPLATES: self._get_paths_from_setting
        }

        self._items = []
        paths = _FN_MAP[mode](mode)
        for path in paths:
            self._items.append(MdlPathItem(path))

    def _get_omni_neuray_api(self):
            import omni.mdl.neuraylib

            neuraylib = omni.mdl.neuraylib.get_neuraylib()
            ineuray = neuraylib.getNeurayAPI()
            neuray = pymdlsdk.attach_ineuray(ineuray)

            return neuray

    def _get_paths_from_mdl_config(self, mode):
        neuray = self._get_omni_neuray_api()

        paths = []
        with neuray.get_api_component(pymdlsdk.IMdl_configuration) as cfg:
            if mode == self.SOURCE_MDL_SYSTEM_PATH:
                num_paths = cfg.get_mdl_system_paths_length()
                if num_paths:
                    for i in range(0, num_paths):
                        paths.append(cfg.get_mdl_system_path(i))

            elif mode == self.SOURCE_MDL_USER_PATH:
                num_paths = cfg.get_mdl_user_paths_length()
                if num_paths:
                    for i in range(0, num_paths):
                        paths.append(cfg.get_mdl_user_path(i))
            else:
                pass

        return paths

    def _get_paths_from_array_setting(self, mode):
        settings = carb.settings.get_settings()
        paths = settings.get(self._SETTING_NAME_MAP[mode])

        return paths if paths else []

    def _get_paths_from_setting(self, mode):
        settings = carb.settings.get_settings()

        pathStr = settings.get(self._SETTING_NAME_MAP[mode])
        paths = []
        if pathStr:
            paths = pathStr.split(";")

        return paths

    def get_item_children(self, item):
        if item is not None:
            return []

        return self._items

    def get_item_value_model_count(self, item):
        return 1

    def get_item_value_model(self, item, column_id):
        if item and isinstance(item, MdlPathItem):
            return item.name_model

    def get_items(self):
        return self._items


class MdlDefaultPathListWidget():
    _TREEVIEW_STYLE = {
        "TreeView.Item": {
            "margin": 3,
            "font_size": 16.0,
            "color": cl("#777777")
        }
    }
    _FRAME_STYLE = {
        "CollapsableFrame": {
            "margin": 0,
            "padding": 3,
            "border_width": 0,
            "border_radius": 0,
            "secondary_color": cl("#2c2e2e")
        }
    }

    def __init__(self, **kwargs):
        self._models = {}

        entries = [
            ["Standard System Paths", MdlDefaultPathListModel.SOURCE_MDL_SYSTEM_PATH],
            ["Additional System Paths", MdlDefaultPathListModel.SOURCE_ADDITIONAL_SYSTEM_PATHS],
            ["Standard User Paths", MdlDefaultPathListModel.SOURCE_MDL_USER_PATH],
            ["Additional User Paths", MdlDefaultPathListModel.SOURCE_ADDITIONAL_USER_PATHS],
            ["Renderer Required", MdlDefaultPathListModel.SOURCE_RENDERER_REQUIRED],
            ["Renderer Templates", MdlDefaultPathListModel.SOURCE_RENDERER_TEMPLATES]
        ]
        with ui.VStack(height=0):
            for entry in entries:
                model = MdlDefaultPathListModel(entry[1])
                if not model.get_items():
                    continue  # do not add widget if it is empty
                self._add_path_list_widget(entry[0], model)
                self._models[entry[1]] = model

    def _add_path_list_widget(self, title, model):
        with ui.CollapsableFrame(title, collapsed=True, style=self._FRAME_STYLE):
            with ui.ScrollingFrame(height=100):
                view = ui.TreeView(
                    model,
                    header_visible=False,
                    root_visible=False,
                    style=self._TREEVIEW_STYLE
                )
                # do not allow select items
                view.set_selection_changed_fn(lambda i: view.clear_selection())


class MdlCustomPathListModel(EditableListModel):
    def __init__(self, setting_path):
        super().__init__(
            MdlPathItem,
            setting_path
        )

    def populate_items(self):
        pathStr = self._settings.get(self._setting_path)
        paths = pathStr.split(";") if pathStr else []

        self._items.clear()
        for path in paths:
            if not path:
                continue
            self._items.append(self._item_class(path))

        self._item_changed(None)

    def find_path(self, path):
        pp = pathlib.PurePath(path)

        for item in self._items:
            ip = pathlib.PurePath(item.name_model.as_string)
            if pp == ip:
                return ip.as_posix()
        return ""

    def sanity_check_paths(self):
        bad_paths = []
        for item in self._items:
            path = item.name_model.as_string
            if omni.client.is_valid_url(path):
                continue  # pass nucleus paths always
            if not os.path.exists(path):
                bad_paths.append(path)

        return bad_paths

    def save_entries_to_settings(self):
        pathStrs = [item.name_model.as_string for item in self._items]
        self._settings.set(material_config_utils.SETTING_SEARCHPATHS_CUSTOM, pathStrs)
        pathStr = ";".join(pathStrs)
        self._settings.set(self._setting_path, pathStr)

    def save_to_material_config_file(self):
        material_config_utils.save_carb_setting_to_config_file(
            "/app/mdl/nostdpath",
            "/options/noStandardPath"
        )
        material_config_utils.save_carb_setting_to_config_file(
            self._setting_path,
            "/searchPaths/custom",
            is_paths=True
        )


class MdlCustomPathListWidget(EditableListWidget):
    def __init__(self):
        super().__init__(
            MdlCustomPathListModel,
            EditableListItemDelegate,
            "/renderer/mdl/searchPaths/custom",
            150
        )

    def on_file_picker_apply_clicked(self, filename, dirname, selections):
        file_picker_selection = f"{dirname}{filename}"

        if self._model.find_path(file_picker_selection):
            try:
                import omni.kit.notification_manager as nm

                nm.post_notification(
                    "Path already exists in the list.",
                    status=nm.NotificationStatus.INFO,
                    hide_after_timeout=False
                )
                return
            except ModuleNotFoundError:
                return

        self._model.add_entry(file_picker_selection)

    def on_add_new_entry_button_clicked(self):
        self._view.clear_selection()
        try:
            from omni.kit.window.file_importer import get_file_importer

            file_importer = get_file_importer()
            if file_importer:
                file_importer.show_window(
                    title="Add New Search Path",
                    import_button_label="Select",
                    show_only_folders=True,
                    file_extension_types=[("*.*", "All files")],
                    import_handler=self.on_file_picker_apply_clicked,
                )
        except ModuleNotFoundError:
            pass

    def on_save_button_clicked(self):
        bad_paths = self._model.sanity_check_paths()
        if bad_paths:
            try:
                import omni.kit.notification_manager as nm

                paths = "\n".join(bad_paths)

                ok_button = nm.NotificationButtonInfo(
                    "OK",
                    on_complete=lambda: super().on_save_button_clicked()
                )
                cancel_button = nm.NotificationButtonInfo(
                    "Cancel",
                    on_complete=None
                )
                nm.post_notification(
                    f"Path(s) below do not exist. Continue?\n\n{paths}",
                    status=nm.NotificationStatus.WARNING,
                    button_infos=[ok_button, cancel_button],
                    hide_after_timeout=False
                )
            except ModuleNotFoundError:
                super().on_save_button_clicked()
        else:
            super().on_save_button_clicked()
