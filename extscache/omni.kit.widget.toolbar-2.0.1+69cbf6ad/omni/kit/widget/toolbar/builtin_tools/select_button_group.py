# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SelectButtonGroup"]

import pathlib

import carb.input
import omni.kit.app
import omni.kit.context_menu
import omni.kit.widget.context_menu
import omni.ui as ui
from carb.input import KeyboardInput as Key
from omni.kit.widget.options_menu import OptionsMenu, OptionsModel, OptionItem, OptionSeparator, OptionRadios
from pxr import Kind

from ..hotkey import Hotkey
from ..widget_group import WidgetGroup
from .models.select_include_ref_model import SelectIncludeRefModel
from .models.select_mode_model import SelectModeModel
from .models.select_no_kinds_model import SelectNoKindsModel
from .models.area_select_occluded_objects_model import SelectOccludedObjectsModel
from .models.transform_mode_model import TransformModeModel

SELECT_PRIM_MODE_TOOL_NAME = "Prim"
SELECT_MODEL_MODE_TOOL_NAME = "Model"
SELECT_TOOL_NAME = "Select"
LIGHT_TYPES = "type:CylinderLight;type:DiskLight;type:DistantLight;type:DomeLight;type:GeometryLight;type:Light;type:RectLight;type:SphereLight"
SELECT_MODE_BUTTON_ENABLED_SETTING_PATH = "/exts/omni.kit.widget.toolbar/SelectionButton/SelectMode/enabled"


def get_extension_folder_path() -> pathlib.Path:
    return pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("omni.kit.widget.toolbar"))


class SelectButtonGroup(WidgetGroup):
    def __init__(self):
        super().__init__()
        self._input = carb.input.acquire_input_interface()
        self._select_mode_model = SelectModeModel()
        self._select_no_kinds_model = SelectNoKindsModel()
        self._select_include_ref_model = SelectIncludeRefModel()
        self._select_op_model = TransformModeModel(TransformModeModel.TRANSFORM_OP_SELECT)
        self._select_occluded_objects_model = None
        self._select_op_menu_entry = None
        self._custom_types = []
        self._settings = carb.settings.get_settings()
        self._icon_path = str(get_extension_folder_path() / "data" / "icon")

        self._settings = carb.settings.get_settings()
        self._select_mode_button = None
        self._mode_hotkey = None
        self._options_model: Optional[OptionsModel] = None
        self._options_menu: Optional[OptionsMenu] = None
        self._occludsion_model: Optional[OptionsModel] = None
        self._occludsion_menu: Optional[OptionsMenu] = None
        self._include_references_item: Optional[OptionItem] = None
        self._include_prims_with_no_kind_item: Optional[OptionItem] = None
        if self._settings.get("/exts/omni.kit.widget.toolbar/SelectionButton/OccludedObjects/enabled"):
            self._select_occluded_objects_model = SelectOccludedObjectsModel()
        if self._settings.get(SELECT_MODE_BUTTON_ENABLED_SETTING_PATH):
            def hotkey_change():
                current_mode = self._select_mode_model.get_value_as_string()
                if current_mode == "models" or current_mode == "kind:model.ALL":
                    self._select_mode_model.set_value("type:ALL")
                else:
                    self._select_mode_model.set_value("kind:model.ALL")
                self._update_selection_mode_button()

            def on_select_mode_hotkey_changed(hotkey: str):
                self._select_mode_button.tooltip = self._get_select_mode_tooltip()

            self._mode_hotkey = Hotkey(
                "toolbar::select_mode",
                Key.T,
                hotkey_change,
                lambda: self._select_mode_button.enabled and self._is_in_context(),
                on_hotkey_changed_fn=on_select_mode_hotkey_changed,
            )

        # only replace the tooltip part so that "Paint Select" registered from select brush can still have correct label
        def on_select_hotkey_changed(hotkey: str):
            self._select_op_button.tooltip = (
                self._select_op_button.tooltip.rsplit("(", 1)[0] + f"({self._select_hotkey.get_as_string('Q')})"
            )

        self._select_hotkey = Hotkey(
            "toolbar::select",
            Key.Q,
            lambda: self._select_op_button.model.set_value(True),
            lambda: self._select_op_button.enabled and self._is_in_context()
            and self._input.get_mouse_value(None, carb.input.MouseInput.RIGHT_BUTTON)
            == 0,
            on_hotkey_changed_fn=lambda hotkey: on_select_hotkey_changed(hotkey),
        )

    def get_style(self):
        style = {
            "Button.Image::select_mode": {"image_url": "${glyphs}/toolbar_select_prim.svg"},
            "Button.Image::select_op_models": {"image_url": "${glyphs}/toolbar_select_models.svg"},
            "Button.Image::select_op_prims": {"image_url": "${glyphs}/toolbar_select_prims.svg"},

            "Button.Image::all_prim_types": {"image_url": f"{self._icon_path}/all_prim_types.svg"},
            "Button.Image::meshes": {"image_url": f"{self._icon_path}/meshes.svg"},
            "Button.Image::lights": {"image_url": f"{self._icon_path}/lights.svg"},
            "Button.Image::cameras": {"image_url": f"{self._icon_path}/cameras.svg"},
            "Button.Image::model_kinds": {"image_url": f"{self._icon_path}/model_kinds.svg"},
            "Button.Image::assembly": {"image_url": f"{self._icon_path}/assembly.svg"},
            "Button.Image::group": {"image_url": f"{self._icon_path}/group.svg"},
            "Button.Image::component": {"image_url": f"{self._icon_path}/component.svg"},
            "Button.Image::sub_component": {"image_url": f"{self._icon_path}/sub_component.svg"},
            "Button.Image::payload_reference": {"image_url": f"{self._icon_path}/payload_reference.svg"},
            "Button.Image::custom_kind": {"image_url": f"{self._icon_path}/custom_kind.svg"},
            "Button.Image::custom_type": {"image_url": f"{self._icon_path}/custom_type.svg"},
        }
        return style

    def create(self, default_size):

        def on_select_mode_change(model):
            self._update_selection_mode_button()
            if self._include_references_item:
                self._include_references_item.enabled = self._enable_no_kinds_option(None)
            if self._include_prims_with_no_kind_item:
                self._include_prims_with_no_kind_item.enabled = self._enable_no_kinds_option(None)

        result = {}
        if self._settings.get(SELECT_MODE_BUTTON_ENABLED_SETTING_PATH):
            self._select_mode_button = ui.ToolButton(
                model=self._select_mode_model,
                name="select_mode",
                tooltip=self._get_select_mode_tooltip(),
                width=default_size,
                height=default_size,
                mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, "select_mode"),
                mouse_released_fn=lambda x, y, b, _: self._on_mouse_released(b),
            )
            self._model_changed_sub = self._select_mode_model.subscribe_value_changed_fn(on_select_mode_change)
            result["select_mode"] = self._select_mode_button

        with ui.ZStack(width=0, height=0):
            self._select_op_button = ui.ToolButton(
                model=self._select_op_model,
                name=self._get_select_op_button_name(self._select_mode_model),
                tooltip=self._get_select_tooltip(),
                width=default_size,
                height=default_size,
                checked=self._select_op_model.get_value_as_bool(),
                mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, "select_op"),
                mouse_released_fn=lambda x, y, b, _: self._on_mouse_released(b),
            )

            # Follow the pattern here (ZStack + _build_flyout_indicator) for other buttons if they want dynamic flyout indicator
            self._select_op_menu_sub = self._build_flyout_indicator(default_size, default_size, "select_op")
            result["select_op"] = self._select_op_button

        self._update_selection_mode_button()
        return result

    def clean(self):
        super().clean()
        self._select_mode_button = None
        self._select_op_button = None
        self._select_mode_model.clean()
        self._select_mode_model = None
        self._select_no_kinds_model.clean()
        self._select_no_kinds_model = None
        if self._select_occluded_objects_model:
            self._select_occluded_objects_model.clean()
        self._select_occluded_objects_model = None
        self._select_include_ref_model.clean()
        self._select_include_ref_model = None
        self._select_op_model.clean()
        self._select_op_model = None
        self._model_changed_sub = None
        if self._mode_hotkey:
            self._mode_hotkey.clean()
        self._mode_hotkey = None
        self._select_hotkey.clean()
        self._select_hotkey = None
        if self._options_menu:
            self._options_menu.destroy()
            self._options_menu = None
        if self._occludsion_menu:
            self._occludsion_menu.destroy()
            self._occludsion_menu = None
        self._options_model = None
        self._occludsion_model = None
        self._include_references_item = None
        self._include_prims_with_no_kind_item = None

    def _get_select_op_button_name(self, model):
        return "select_op_prims" if model.get_value_as_bool() else "select_op_models"

    def _get_select_tooltip(self):
        return f"{SELECT_TOOL_NAME} ({self._select_hotkey.get_as_string('Q')})"

    def _get_select_mode_button_name(self):
        mode_name = {
            "type:ALL": "all_prim_types",
            "type:Mesh": "meshes",
            LIGHT_TYPES: "lights",
            "type:Camera": "cameras",
            "kind:model.ALL": "model_kinds",
            "kind:assembly": "assembly",
            "kind:group": "group",
            "kind:component": "component",
            "kind:subcomponent": "sub_component",
            "ref:reference;ref:payload": "custom_type",
        }
        mode = self._select_mode_model.get_value_as_string()
        if mode in mode_name:
            return mode_name[mode]
        else:
            if mode[:4] == "kind":
                return "custom_kind"
            else:
                return "custom_type"

    def _get_select_mode_tooltip(self):
        mode_data = {
            "type:ALL": "All Prim Types",
            "type:Mesh": "Meshes",
            LIGHT_TYPES: "Lights",
            "type:Camera": "Camera",
            "kind:model.ALL": "All Model Kinds",
            "kind:assembly": "Assembly",
            "kind:group": "Group",
            "kind:component": "Component",
            "kind:subcomponent": "Subcomponent",
            "ref:reference;ref:payload": "Subcomponent",
        }
        mode = self._select_mode_model.get_value_as_string()
        if mode in mode_data:
            tooltip = mode_data[mode]
        else:
            if mode[:4] == "kind":
                tooltip = "Custom Kind"
            else:
                tooltip = "Custom type"

        return tooltip + f" ({self._mode_hotkey.get_as_string('T')})"

    def _usd_kinds(self):
        return ["model", "assembly", "group", "component", "subcomponent"]

    def _enable_no_kinds_option(self, b):
        mode = self._select_mode_model.get_value_as_string()
        return mode[:4] == "kind"

    def _usd_kinds_display(self):
        return self._usd_kinds()[1:]

    def _plugin_kinds(self):
        all_kinds = set(Kind.Registry.GetAllKinds())
        return all_kinds - set(self._usd_kinds())

    def _create_selection_list(self, selections):
        results = ""
        delimiter = ";"
        first_selection = True
        for s in selections:
            if not first_selection:
                first_selection = True
            else:
                results += delimiter
            results += s
        return results

    def _update_selection_mode_button(self):
        if self._select_mode_button:
            self._select_mode_button.name = self._get_select_mode_button_name()
            self._select_mode_button.tooltip = self._get_select_mode_tooltip()

        if self._select_op_button:
            self._select_op_button.name = self._get_select_op_button_name(self._select_mode_model)

    def _build_select_menu_model(self):
        radios = [
            ("Select by Type", None),
            ("All Prim Types", "type:ALL"),
            ("Meshes", "type:Mesh"),
            ("Lights", LIGHT_TYPES),
            ("Camera", "type:Camera"),
        ]
        if self._custom_types:
            for name, types in self._custom_types:
                radios.append((name, types))
        radios.extend(
            [
                ("Select by Model Kind", None),
                ("All Model Kinds", "kind:model.ALL"),
                ("Assembly", "kind:assembly"),
                ("Group", "kind:group"),
                ("Component", "kind:component"),
                ("Subcomponent", "kind:subcomponent"),
            ]
        )
        plugin_kinds = self._plugin_kinds()
        if (len(plugin_kinds)) > 0:
            for k in plugin_kinds:
                radios.append(str(k).capitalize(), f"kind:{k}")

        self._include_prims_with_no_kind_item = OptionItem("Include Prims with no Kind", default=True, hide_on_click=True, model=self._select_no_kinds_model, enabled=self._enable_no_kinds_option(None))
        self._include_references_item = OptionItem("Include References and Payloads", default=True, hide_on_click=True, model=self._select_include_ref_model, enabled=self._enable_no_kinds_option(None))

        items = [
            OptionRadios(radios, model=self._select_mode_model, default=SelectModeModel.PICKING_MODE_DEFAULT,),
            OptionSeparator(),
            self._include_prims_with_no_kind_item,
            self._include_references_item,
        ]
        if self._options_model is None:
            self._options_model = OptionsModel("Select Mode", items)
        else:
            self._options_model.rebuild_items(items)

    def _build_options_menu(self):
        self._build_select_menu_model()
        self._options_menu = OptionsMenu(self._options_model)

    def _build_op_menu(self):
        items = [
            OptionItem("Area Select Occluded Objects", default=False, hide_on_click=True, model=self._select_occluded_objects_model)
        ]
        if self._occludsion_model is None:
            self._occludsion_model = OptionsModel("Select Op", items)
        else:
            self._occludsion_model.rebuild_items(items)

        self._occludsion_menu = OptionsMenu(self._occludsion_model)

    def _invoke_context_menu(self, button_id: str, min_menu_entries: int = 1):
        """
        Function to invoke context menu.

        Args:
            button_id: button_id of the context menu to be invoked.
            min_menu_entries: minimal number of menu entries required for menu to be visible (default 1).
        """
        if button_id == "select_mode":
            self._build_options_menu()
            self._options_menu.show_by_widget(self._select_mode_button, alignment=ui.Alignment.RIGHT_TOP)
        elif button_id == "select_op" and self._select_occluded_objects_model:
            self._build_op_menu()
            self._occludsion_menu.show_by_widget(None, alignment=ui.Alignment.RIGHT_TOP)

    def add_custom_select_type(self, entry_name: str, selection_types: list):
        selection = []
        for s in selection_types:
            selection.append(f"type:{s}")
        selection_string = self._create_selection_list(selection)
        self._custom_types.append((entry_name, selection_string))
        if self._options_model:
            self._build_select_menu_model()

    def remove_custom_select(self, entry_name):
        for index, entry in enumerate(self._custom_types):
            if entry[0] == entry_name:
                del self._custom_types[index]
                if self._options_model:
                    self._build_select_menu_model()
                return
