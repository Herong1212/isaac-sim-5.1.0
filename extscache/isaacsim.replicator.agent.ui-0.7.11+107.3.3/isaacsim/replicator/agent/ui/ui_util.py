# flake8: noqa

import ast
import pprint
import os
from enum import Enum

import carb
import omni.ui as ui
from omni.kit.window.filepicker import FilePickerDialog
from omni.metropolis.utils.config_file.property import Property
from omni.kit.widget.searchfield import SearchField
from omni.metropolis.utils.ui_util import UIUtil
import omni.anim.navigation.core as nav
import omni.kit.window.content_browser as content
import asyncio



# ============== Style ====================

COLOR_BLACK = 0x0
COLOR_ERROR = 0xFF5863EC
COLOR_DIRTY = 0xFFFFC880
COLOR_BTN   = 0xFFCECECE
BOUNDING_RADIUS = 1.5
UI_DISTANCE = 120
STRING_FIELD_WIDTH = 300

def get_collapsable_frame_style():
    return {
        "border_radius": BOUNDING_RADIUS * 2,
        "border_color": COLOR_BLACK,
        "border_width": 1,
        "padding": 6,
    }


# ============== Folder Picker Template ===============
class FOLDER_PICKER_TYPE(Enum):  # noqa
    YAML = 1
    TXT = 2
    FOLDER = 3
    USD = 4
    JSON = 5


def build_folder_picker(label, dialog_title, default_val, file_extension_type, on_folder_picked, on_file_save = None):  # noqa
    """
    Build a folder picker. Supports four types of files: yaml, text, folder, usd/usda.
    Return the created string field and folder icon (button).
    """

    def open_folder_picker():
        def on_selected(filename, path):
            if file_extension_type != FOLDER_PICKER_TYPE.FOLDER and (filename is None or filename == ""):
                return
            if open_folder_picker.file_picker:
                open_folder_picker.file_picker.hide()
                open_folder_picker.file_picker = None
            full_path = os.path.join(path, filename)
            strField.model.set_value(full_path)
            on_folder_picked(filename, path)

        def on_canceled(a, b):
            if open_folder_picker.file_picker:
                open_folder_picker.file_picker.hide()
                open_folder_picker.file_picker = None

        def filter_yaml(item):
            if not item or item.is_folder:
                return True
            return item.path.endswith(".yaml")

        def filter_txt(item):
            if not item or item.is_folder:
                return True
            return item.path.endswith(".txt")

        def filter_folder(item):
            if not item or item.is_folder:
                return True
            return False

        def filter_usd(item):
            if not item or item.is_folder:
                return True
            return item.path.endswith(".usd") or item.path.endswith(".usda") or item.path.endswith(".usdc")

        def filter_json(item):
            if not item or item.is_folder:
                return True
            return item.path.endswith(".json")

        extension_option = None
        filter_fn = None
        if file_extension_type == FOLDER_PICKER_TYPE.YAML:
            extension_option = ("*.yaml", "Yaml File")
            filter_fn = filter_yaml
        elif file_extension_type == FOLDER_PICKER_TYPE.TXT:
            extension_option = ("*.txt", "Plain Text File")
            filter_fn = filter_txt
        elif file_extension_type == FOLDER_PICKER_TYPE.FOLDER:
            extension_option = ""
            filter_fn = filter_folder
        elif file_extension_type == FOLDER_PICKER_TYPE.USD:
            extension_option = ("*.usd; *.usda; *.usdc", "Universal Scene Description")
            filter_fn = filter_usd
        elif file_extension_type == FOLDER_PICKER_TYPE.JSON:
            extension_option = ("*.json", "Json File")
            filter_fn = filter_json
        else:
            extension_option = ""
            filter_fn = filter_folder

        # Avoid opening multiple file picker (Not sure if gc will take care of it)
        if open_folder_picker.file_picker is not None:
            open_folder_picker.file_picker.hide()
            open_folder_picker.file_picker = None

        open_folder_picker.file_picker = FilePickerDialog(
            dialog_title,
            allow_multi_selection=False,
            apply_button_label="Select",
            click_apply_handler=lambda a, b: on_selected(a, b),  # noqa
            click_cancel_handler=lambda a, b: on_canceled(a, b),  # noqa
            item_filter_fn=filter_fn,
            file_extension_options=[extension_option],
            enable_versioning_pane=True,
        )

    async def locate_file():
        current_file = strField.model.get_value_as_string()
        content.get_content_window().navigate_to(current_file)

    open_folder_picker.file_picker = None

    with ui.HStack(alignment=ui.Alignment.CENTER):
        ui.Label(label, width=120)
        strField = ui.StringField(height=20)  # noqa

        if on_file_save:
            ui.Spacer(width=10)
            btn_save = ui.Label(f"{UIUtil.get_save_glyph()}",
                                width=15,
                                mouse_pressed_fn=lambda x, y, b, _: on_file_save(),
                                style={"color": COLOR_BTN})

        ui.Spacer(width=10)
        btn_select = ui.Label(f"{UIUtil.get_folder_glyph()}",
                              width=15,
                              mouse_pressed_fn=lambda x, y, b, _: open_folder_picker())

        ui.Spacer(width=10)
        btn_goto = ui.Image(f"{UIUtil.get_find_glyph_path()}",
                            width=15,
                            mouse_pressed_fn=lambda x, y, b, _: asyncio.ensure_future(locate_file()))
        ui.Spacer(width=10)

    if on_file_save:
        return [strField, btn_select, btn_goto, btn_save]
    else:
        return [strField, btn_select, btn_goto]


# ============== Helper Function ===============
def adjust_background_color(ui_element, prop: Property):
    # Searchfield will not change its color
    if isinstance(ui_element, SearchField):
        return

    # Update style based on its type
    style = ui.Style.get_instance().default["Field"].copy()
    if prop and prop.is_value_error():
        style["color"] = COLOR_ERROR  # Red (ABGR format)
    elif prop and prop.is_value_dirty():
        style["color"] = COLOR_DIRTY  # Light Blue (ABGR format)
    ui_element.set_style(style)

def set_property_to_ui(ui_element, prop: Property):
    """
    Helper function to set Property value to UI model properly.
    """
    if not ui_element:
        return
    # Update value
    if prop is None:
        ui_element.enabled = False
        ui_element.model.set_value(None)
    else:
        ui_element.enabled = True
        if isinstance(ui_element, ui.StringField):
            if prop.get_value_type() == dict:  # Formatting for dict
                str_value = pprint.pformat(prop.get_value(), width=30)
                ui_element.model.set_value(str_value)
            else:
                ui_element.model.set_value(str(prop.get_value()))  # string field can display any type
        elif isinstance(ui_element, SearchField):
            # Without the following, setting searchwords will trigger set_ui_to_property
            ui_element._on_search_fn = None
            ui_element.search_words = prop.get_value()
            ui_element._on_search_fn = lambda m: set_ui_to_property(ui_element, prop)
        else:
            ui_element.model.set_value(prop.get_value())
    # Update style
    adjust_background_color(ui_element, prop)


def set_ui_to_property(ui_element, prop: Property):
    """
    Helper function to update value in UI model to Property.
    """
    if prop is None:
        return
    value = None
    if prop.get_value_type() == int:
        value = ui_element.model.get_value_as_int()
    elif prop.get_value_type() == float:
        value = ui_element.model.get_value_as_float()
    elif prop.get_value_type() == str:
        value = ui_element.model.get_value_as_string()
    elif prop.get_value_type() == bool:
        value = ui_element.model.get_value_as_bool()
    elif prop.get_value_type() == list:
        if isinstance(ui_element, SearchField):
            searchfield_words = [word for word in ui_element.search_words if word != ""]
            value = searchfield_words
        else:
            try:
                # Split by comma and clean up whitespace
                str_value = ui_element.model.get_value_as_string()
                value = [word.strip() for word in str_value.split(",") if word.strip()]
            except:
                carb.log_warn(
                    f"Unable to parse '{ui_element.model.get_value_as_string()}' as a list."
                    f"Please check if format is correct."
                )
                return
    elif prop.get_value_type() == dict:
        try:
            str_value = ui_element.model.get_value_as_string()
            value = ast.literal_eval(str_value)
        except:
            carb.log_warn(
                f"Unable to update '{ui_element.model.get_value_as_string()}' to config file. "
                f"Please check if format is correct."
            )
            return
    else:
        value = ui_element.model.get_value_as_string()
    prop.set_value(value)
    # Update style
    adjust_background_color(ui_element, prop)

def update_navmesh_area_suggestions(searchfield: SearchField):
    """
    Update the suggestions of the searchfield based on the available navmesh areas.

    Args:
        searchfield: The searchfield to update the suggestions for.
    """
    navmesh_areas = nav.acquire_interface().get_area_names()
    searchfield.suggestions = [area for area in navmesh_areas if area not in searchfield.search_words]

# ============== Global Events and Variables ==============
class GLOBAL_VARIABLES(Enum):  # noqa
    CONFIG_FILE_IS_LOADED = 0  # bool
    CONFIG_FILE_PATH = 1  # str
    CORE_SIM_MANAGER = 6  # isaacsim.replicator.agent.SimulationManager
    ROBOT_COMMAND_FILE_MODIFIED = 11  # bool


class GLOBAL_EVENTS(Enum):  # noqa
    CONFIG_FILE_LOADED = 0  # f()
    CONFIG_FILE_MODIFIED = 1  # f(key = None)
    CONFIG_FILE_SAVED = 2  # f()


    MENU_LOAD_SCENE = 6  # f(usd_path : str)

    CONFIG_FILE_FAILED_LOADING = 7  # F()

    ROBOT_COMMAND_FILE_MODIFIED = 8  # f()
    COMMAND_FILE_SWITCH_ROBOT = 9  # f()
    ROBOT_COMMAND_FILE_CHANGE = 10  # f() command file path change


class EventHandler(list):
    """
    Event handler represent by a list of callable objects.
    """

    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)
