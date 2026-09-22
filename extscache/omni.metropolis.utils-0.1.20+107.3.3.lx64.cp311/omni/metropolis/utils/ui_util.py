import os
import asyncio
import pprint
import ast
from enum import Enum
import omni.kit
import omni.ui as ui
from omni.ui import color as cl
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.searchfield import SearchField
from omni.kit.menu.utils import MenuItemDescription
import omni.kit.window.content_browser as content
import omni.kit.app
from pathlib import Path
import carb
from .config_file.property import *


EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("omni.metropolis.utils")


class Color:
    ERROR = 0xFF5863EC # Red for error values
    DIRTY = 0xFFFFC880 # Yellow for dirty values


class UIUtil:
    # ============== UI Layout ===============
    async def load_layout(layout_file: str, keep_windows_open=False):
        try:
            from omni.kit.quicklayout import QuickLayout

            # few frames delay to avoid the conflict with the layout of omni.kit.mainwindow
            for i in range(3):
                await omni.kit.app.get_app().next_update_async()
            QuickLayout.load_file(layout_file, keep_windows_open)

            # few frames delay to load the window first
            for i in range(3):
                await omni.kit.app.get_app().next_update_async()

        except Exception as exc:
            pass
            QuickLayout.load_file(layout_file, keep_windows_open)

    def open_action_and_event_data_generation_layout():
        layout_file = Path(EXT_PATH).joinpath("data/layouts/action_and_event_data_generation.json")
        if not os.path.exists(layout_file):
            carb.log_warn(f"Layout file {layout_file} does not exist")
        return asyncio.ensure_future(UIUtil.load_layout(str(layout_file)))

    # ============== UI Menu ===============
    def switch_menu_visibility(window: ui.Window):
        window.visible = not window.visible

    def match_window_visible_with_tick(visible, menu_item_description: MenuItemDescription):
        menu_item_description.ticked_value = visible

    def make_kit_menu_item_description(
        ext_id: str, name: str, onclick_fn, onclick_fn_param, action_name: str = ""
    ) -> MenuItemDescription:
        """Easily replace the onclick_fn with onclick_action when creating a menu description

        Args:
            ext_id (str): The extension you are adding the menu item to.
            name (str): Name of the menu item displayed in UI.
            onclick_fn (Function): The function to run when clicking the menu item.
            onclick_fn_param: the parameter to be passed to onclick_fn
            action_name (str): name for the action, in case ext_id+name don't make a unique string


        Note:
            ext_id + name + action_name must concatenate to a unique identifier.

        """
        action_unique = f'{ext_id.replace(" ", "_")}{name.replace(" ", "_")}{action_name.replace(" ", "_")}'
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_action(ext_id, action_unique)
        action_registry.register_action(ext_id, action_unique, onclick_fn)
        return MenuItemDescription(name=name, onclick_action=(ext_id, action_unique, onclick_fn_param))

    # ============== UI Component ===============

    def add_separator(text: str):
        """Create a separator line with a text label

        Args:
            text (str): The text to display on the separator line
        """
        with ui.VStack():
            ui.Spacer(height=3)
            with ui.HStack(height=16, spacing=16):
                ui.Label(text, name="separator", width=0, style={"color": ui.color.grey})
                ui.Line(style={"color": ui.color.grey})
            ui.Spacer(height=2)

    def build_collapsable_frame_header_with_image(collapsed: bool, title: str, image_path: str):
        """build a collapsable frame header with an image

        Args:
            collapsed (bool): Whether the frame is collapsed
            title (str): The title to display on the header
            image_path (str): The path to the image to display on the header

        Note:
            this function is to be used with ui.CollapsableFrame as build_header_fn
        """
        with ui.HStack(alignment=ui.Alignment.LEFT, height=20):
            if collapsed:
                ui.Spacer(width=6)
                with ui.VStack(height=20, width=10, alignment=ui.Alignment.CENTER):
                    ui.Spacer(height=6)
                    ui.Triangle(width=8, height=8,alignment=ui.Alignment.RIGHT_CENTER, style={"background_color": ui.color(0xFFCCCC)})
                ui.ImageWithProvider(image_path, width=40, height=20)

            else:
                ui.Spacer(width=6)
                with ui.VStack(height=20, width=10, alignment=ui.Alignment.CENTER):
                    ui.Spacer(height=6)
                    ui.Triangle(width=8, height=8,alignment=ui.Alignment.CENTER_BOTTOM, style={"background_color": ui.color(0xFFCCCC)})
                ui.ImageWithProvider(image_path, width=40, height=20)
            ui.Label(title, style_type_name_override="DetailFrame.Header.Label")

    def create_model_for_value(value: any) -> ui.AbstractValueModel:
        if isinstance(value, int):
            return ui.SimpleIntModel(value)
        elif isinstance(value, float):
            return ui.SimpleFloatModel(value)
        elif isinstance(value, bool):
            return ui.SimpleBoolModel(value)
        elif isinstance(value, str):
            return ui.SimpleStringModel(value)
        # TODO:: craete value model for List
        else:
            carb.log_warn(f"Unspported value type {type(value)}. Will use string model.")
            return ui.SimpleStringModel(value)

    def create_field_for_model(model: ui.AbstractItemModel):
        if isinstance(model, ui.SimpleIntModel):
            return ui.IntField(model)
        elif isinstance(model, ui.SimpleFloatModel):
            return ui.FloatField(model)
        elif isinstance(model, ui.SimpleBoolModel):
            return ui.CheckBox(model)
        elif isinstance(model, ui.SimpleStringModel):
            return ui.StringField(model)
        # TODO:: create ui for list
        else:
            carb.log_warn(f"Unspported value model type {type(model)}. Will use StringField.")
            return ui.StringField(model)

    def get_value_from_model(model: ui.AbstractValueModel):
        if isinstance(model, ui.SimpleIntModel):
            return model.as_int
        elif isinstance(model, ui.SimpleFloatModel):
            return model.as_float
        elif isinstance(model, ui.SimpleBoolModel):
            return model.as_bool
        elif isinstance(model, ui.SimpleStringModel):
            return model.as_string
        else:
            carb.log_warn(f"Unspported value model {type(model)}. Will use string.")
            return model.as_string


    # ============== UI Glyph ===============
    def get_plus_glyph():
        return ui.get_custom_glyph_code("${glyphs}/menu_add.svg")

    def get_minus_glyph():
        return ui.get_custom_glyph_code("${glyphs}/menu_minus.svg")

    def get_folder_glyph():
        return ui.get_custom_glyph_code("${glyphs}/folder.svg")

    def get_trash_glyph():
        return ui.get_custom_glyph_code("${glyphs}/trash.svg")

    def get_save_glyph():
        return ui.get_custom_glyph_code("${glyphs}/save.svg")

    def get_find_glyph_path():
        return "${omni.metropolis.utils}/data/ui_icons/find.svg"

# TODO:: [METROPERF-941] make all metrosim extensions refer to this style
class UIStyleUtil:
    COLOR_BLACK = 0x0
    COLOR_ERROR = 0xFF5863EC
    COLOR_DIRTY = 0xFFFFC880
    COLOR_BTN   = 0xFFCECECE
    BOUNDING_RADIUS = 1.5
    UI_DISTANCE = 120
    STRING_FIELD_WIDTH = 300

    DEFAULT_WINDOW_STYLE = {
        "ActionsView": {
            "background_color": cl.actions_background,
            "scrollbar_size": 10,
            "background_selected_color": 0x109D905C,  # Same in stage window
            "secondary_selected_color": 0xFFB0703B,  # column resize
            "secondary_color": cl.actions_text,  # column splitter
        },
        "ActionsView:selected": {
            "background_color": cl.actions_background_selected,
        },
        "ActionsView.Row.Background": {"background_color": cl.actions_row_background},
        "ActionsView.Header.Background": {"background_color": cl.actions_column_header_background},
        "ActionsView.Header.Text": {"color": cl.actions_text, "margin": 4},
        "ActionsView.Item.Text": {"color": cl.actions_text, "margin": 4},
        "ActionsView.Item.Text:selected": {"color": cl.actions_background},
        "ActionsView.Item.Icon.Background": {
            "background_color": cl.actions_item_icon_expand_background,
            "border_radius": 2,
        },
        "ActionsView.Item.Icon.Background:selected": {"background_color": cl.actions_background},
        "ActionsView.Item.Icon.Text": {"color": cl.actions_background},
        "ActionsView.Item.Icon.Text:selected": {"color": cl.actions_text},
    }


    @classmethod
    def get_collapsable_frame_style(cls):
        return {
            "border_radius": cls.BOUNDING_RADIUS * 2,
            "border_color": cls.COLOR_BLACK,
            "border_width": 1,
            "padding": 6,
        }


class UIFolderPickerUtil:
    class FOLDER_PICKER_TYPE(Enum):  # noqa
        YAML = 1
        TXT = 2
        FOLDER = 3
        USD = 4
        JSON = 5

    @classmethod
    def build_folder_picker(cls, label, dialog_title, default_val, file_extension_type, on_folder_picked, on_file_save = None):  # noqa
        """
        Build a folder picker. Supports four types of files: yaml, text, folder, usd/usda.
        Return the created string field and folder icon (button).
        """

        def open_folder_picker():
            def on_selected(filename, path):
                if file_extension_type != cls.FOLDER_PICKER_TYPE.FOLDER and (filename is None or filename == ""):
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
            if file_extension_type == cls.FOLDER_PICKER_TYPE.YAML:
                extension_option = ("*.yaml", "Yaml File")
                filter_fn = filter_yaml
            elif file_extension_type == cls.FOLDER_PICKER_TYPE.TXT:
                extension_option = ("*.txt", "Plain Text File")
                filter_fn = filter_txt
            elif file_extension_type == cls.FOLDER_PICKER_TYPE.FOLDER:
                extension_option = ""
                filter_fn = filter_folder
            elif file_extension_type == cls.FOLDER_PICKER_TYPE.USD:
                extension_option = ("*.usd; *.usda; *.usdc", "Universal Scene Description")
                filter_fn = filter_usd
            elif file_extension_type == cls.FOLDER_PICKER_TYPE.JSON:
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
                                    style={"color": UIStyleUtil.COLOR_BTN})

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


class UIConfigFileUtil:

    @classmethod
    def set_property_to_ui(cls, ui_element, prop: Property):
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
                ui_element._on_search_fn = lambda m: cls.set_ui_to_property(ui_element, prop)
            else:
                ui_element.model.set_value(prop.get_value())
        # Update style
        cls.adjust_background_color(ui_element, prop)

    @classmethod
    def set_ui_to_property(cls, ui_element, prop: Property):
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
        cls.adjust_background_color(ui_element, prop)

    @classmethod
    def adjust_background_color(cls, ui_element, prop: Property):
        # Searchfield will not change its color
        if isinstance(ui_element, SearchField):
            return
        # Update style based on its type
        style = ui.Style.get_instance().default["Field"].copy()
        if prop and prop.is_value_error():
            style["color"] = UIStyleUtil.COLOR_ERROR  # Red (ABGR format)
        elif prop and prop.is_value_dirty():
            style["color"] = UIStyleUtil.COLOR_DIRTY  # Light Blue (ABGR format)
        ui_element.set_style(style)


# ============== Minimal List Model (useful for ComboBox) ===============

class MinimalStringListItem(ui.AbstractItem):
    def __init__(self, text):
        super().__init__()
        self.model = ui.SimpleStringModel(text)


class MinimalStringListModel(ui.AbstractItemModel):
    def __init__(self, items, index = 0):
        super().__init__()
        self._current_index = ui.SimpleIntModel(index)
        self._current_index.add_value_changed_fn(lambda a: self._item_changed(None))
        self.set_item_children(items)

    def set_item_children(self, item_list):
        self._items = []
        if item_list:
            for item in item_list:
                self._items.append(MinimalStringListItem(str(item)))
        self._item_changed(None)

    def get_item_children(self, item=None):
        return self._items

    def get_item_value_model(self, item=None, column_id=None):
        if item is None:
            return self._current_index
        return item.model

    def get_selection(self) -> str:
        if not self._items:
            return None
        idx = self._current_index.get_value_as_int()
        if idx < 0 or idx >= len(self._items):
            return None
        return self._items[idx].model.get_value_as_string()

    def set_selection(self, index) -> str:
        if index == self._current_index.get_value_as_int():
            return
        if index < 0 or index >= len(self._items):
            return None
        self._current_index.set_value(index)