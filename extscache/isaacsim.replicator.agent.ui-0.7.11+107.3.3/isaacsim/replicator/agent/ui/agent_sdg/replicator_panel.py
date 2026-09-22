import asyncio
import ast

import carb
import omni.kit.app
from isaacsim.replicator.agent.core.config_file.defines import *
from isaacsim.replicator.agent.core.data_generation.writers import (
    get_writers_tooltips,
    get_writers_allow_basic_writers_params,
)
from isaacsim.replicator.agent.core.data_generation.writers.writer import IRABasicWriter
from isaacsim.replicator.agent.core.simulation import SimulationManager
from isaacsim.replicator.agent.ui.settings import *
from isaacsim.replicator.agent.ui.ui_util import *
from omni.metropolis.utils.ui_util import UIUtil, MinimalStringListModel

default_custom_writer_name = "MyCustomWriter"
default_custom_writer_parameter = {"rgb": True, "joint": False}


class ReplicatorPanel:
    """
    Replicator Panel in the PeopleSDG window.
    - Display 'replicator' section in the config file format.
    - Also provide option to take in custom writer and its parameter.
    """

    def __init__(self, events, variables):
        self._events = events
        self._variables = variables
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(self.update_UI)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(self.update_UI)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED].append(self.update_UI)
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._frame = None
        self._writer_param_stack = None
        self._writer_combo_box = None
        # Internal states
        self._basic_writer_collapsed = True
        # Cache values
        self._writer_tooltips = get_writers_tooltips()
        self._basic_writer_params = IRABasicWriter.basic_params_values()

    def _on_supported_writer_parameter_changed(self, param, value):
        selection_group: SelectionPropertyGroup = self._sim_manager.get_config_file_property_group(
            "replicator", "writer_selection"
        )
        if not selection_group or not selection_group.is_setup():
            return
        # Update param dict
        origin_value = selection_group.content_prop.get_value().copy()
        origin_value[param] = value
        selection_group.content_prop.set_value(origin_value)

    def _on_writer_selection_changed(self):
        selection_group: SelectionPropertyGroup = self._sim_manager.get_config_file_property_group(
            "replicator", "writer_selection"
        )
        if not selection_group or not selection_group.is_setup():
            return
        old_index = selection_group.get_current_index()
        index = self._writer_combo_box.model._current_index.get_value_as_int()
        selection_group.set_selection(index)
        if selection_group.is_custom_selection() and old_index != index:
            selection_group.setup_by_custom_value(default_custom_writer_name, default_custom_writer_parameter)
        self.refresh_writer_param_UI()

    def _build_writer_one_param_UI(self, param, value, label_name=None):
        with ui.HStack():
            if not label_name:
                label_name = param
            ui.Label("\t" + label_name, width=UI_DISTANCE + 120)
            if type(value) is bool:
                cb = ui.CheckBox()
                cb.model.set_value(value)
                cb.model.add_value_changed_fn(
                    lambda m, p=param: self._on_supported_writer_parameter_changed(p, m.get_value_as_bool())
                )
            elif type(value) is int:
                intField = ui.IntField(width=300)
                intField.model.set_value(value)
                intField.model.add_end_edit_fn(
                    lambda m, p=param: self._on_supported_writer_parameter_changed(p, m.get_value_as_int())
                )
            elif type(value) is float:
                floatField = ui.StringField(width=300)
                floatField.model.set_value(value)
                floatField.model.add_end_edit_fn(
                    lambda m, p=param: self._on_supported_writer_parameter_changed(p, m.get_value_as_float())
                )
            else:  # All other types will be displayed as string
                strField = ui.StringField(width=STRING_FIELD_WIDTH)
                strField.model.set_value(str(value))
                strField.model.add_end_edit_fn(
                    lambda m, p=param: self._on_supported_writer_parameter_changed(p, m.get_value_as_string())
                )

    async def refresh_supported_writer_UI(self):
        selection_group: SelectionPropertyGroup = self._sim_manager.get_config_file_property_group(
            "replicator", "writer_selection"
        )
        writer_prop = selection_group.selection_prop
        parameters_prop = selection_group.content_prop
        writer = writer_prop.get_value()
        params = parameters_prop.get_value()
        derive_params = {k: v for k, v in params.items() if k not in self._basic_writer_params}
        # Clear last display
        self._writer_param_stack.clear()
        await omni.kit.app.get_app().next_update_async()
        # Set up tooltip
        self._writer_combo_box.set_tooltip(self._writer_tooltips[writer])
        # Populate parameter UI
        with self._writer_param_stack:
            # Display output path on top
            self._folder_picker_field, self._folder_picker_btn, self._folder_picker_goto = build_folder_picker(
                label="Output Directory",
                dialog_title="Select A Output Directory",
                default_val=params["output_dir"],
                file_extension_type=FOLDER_PICKER_TYPE.FOLDER,
                on_folder_picked=lambda a, b:
                    self._on_supported_writer_parameter_changed("output_dir", b),
            )
            self._folder_picker_field.model.set_value(params["output_dir"])
            self._folder_picker_field.model.add_end_edit_fn(lambda m: self._on_supported_writer_parameter_changed("output_dir", m.get_value_as_string()))

            ui.Spacer(height=10)
            UIUtil.add_separator("Add Annotators")
            ui.Spacer(height=5)
            # Writer params defined by IRA built-in writers
            for param, value in derive_params.items():
                if param == "output_dir":
                    continue
                self._build_writer_one_param_UI(param, value)
            # Populate BasicWriter UI if needed
            allow_basic_writers_dict = get_writers_allow_basic_writers_params()
            if not allow_basic_writers_dict[writer]:
                return

            def on_basic_writer_collapse_changed(collapse: bool):
                self._basic_writer_collapsed = collapse

            basic_writer_collapse_frame = ui.CollapsableFrame("More", collapsed=self._basic_writer_collapsed)
            basic_writer_collapse_frame.set_collapsed_changed_fn(on_basic_writer_collapse_changed)
            with basic_writer_collapse_frame:
                with ui.VStack(spacing=5):
                    for param, value in self._basic_writer_params.items():
                        if param == "output_dir":
                            continue
                        self._build_writer_one_param_UI(param, params[param])

    async def refresh_custom_writer_UI(self):
        selection_group: SelectionPropertyGroup = self._sim_manager.get_config_file_property_group(
            "replicator", "writer_selection"
        )
        writer_prop = selection_group.selection_prop
        parameters_prop = selection_group.content_prop
        # Clear last display
        self._writer_param_stack.clear()
        await omni.kit.app.get_app().next_update_async()
        # Set up tooltip
        self._writer_combo_box.set_tooltip("")
        # Populate custom writer name and param field
        with self._writer_param_stack:
            with ui.HStack():
                ui.Label("Writer Name", width=UI_DISTANCE)
                self._name_field = ui.StringField(width=STRING_FIELD_WIDTH)
                set_property_to_ui(self._name_field, writer_prop)
                self._name_field.model.add_end_edit_fn(lambda m: set_ui_to_property(self._name_field, writer_prop))
            with ui.HStack():
                ui.Label("Parameters", width=UI_DISTANCE)
                self._param_field = ui.StringField(height=60, width=STRING_FIELD_WIDTH, multiline=True)
                set_property_to_ui(self._param_field, parameters_prop)
                self._param_field.model.add_end_edit_fn(
                    lambda m: set_ui_to_property(self._param_field, parameters_prop)
                )

    def refresh_writer_param_UI(self):
        selection_group: SelectionPropertyGroup = self._sim_manager.get_config_file_property_group(
            "replicator", "writer_selection"
        )
        if not selection_group or not selection_group.is_setup():
            return
        if selection_group.is_custom_selection():
            asyncio.ensure_future(self.refresh_custom_writer_UI())
        else:
            asyncio.ensure_future(self.refresh_supported_writer_UI())

    def build_ui_frame(self):
        if self._frame == None:
            self._frame = ui.CollapsableFrame(
                title="Replicator",
                height=0,
                collapsed=False,
                style=get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                build_header_fn = lambda collapsed, title: UIUtil.build_collapsable_frame_header_with_image(collapsed, title,
                                                            "${omni.metropolis.utils}/data/ui_icons/Stage/icoAOV.svg")

            )

    def update_UI(self):
        selection_group: SelectionPropertyGroup = self._sim_manager.get_config_file_property_group(
            "replicator", "writer_selection"
        )
        self._frame.rebuild()
        with self._frame:
            with ui.VStack(spacing=5, height=0):
                if selection_group is not None and selection_group.is_setup():
                    # Set up combo box
                    supported_writer_list = selection_group.get_all_selection_values()
                    with ui.HStack():
                        ui.Label("Writer", width=UI_DISTANCE)
                        self._writer_combo_box = ui.ComboBox(
                            MinimalStringListModel(supported_writer_list + ["Custom"]), style={"font_size": 14}
                        )
                    self._writer_combo_box.model._current_index.set_value(selection_group.get_current_index())
                    self._writer_combo_box.model.add_item_changed_fn(lambda m, i: self._on_writer_selection_changed())
                    # Set up writer param UI
                    self._writer_param_stack = ui.VStack(spacing=5)
                    self.refresh_writer_param_UI()
                else:
                    self._writer_combo_box = ui.ComboBox(MinimalStringListModel([]), style={"font_size": 14})
