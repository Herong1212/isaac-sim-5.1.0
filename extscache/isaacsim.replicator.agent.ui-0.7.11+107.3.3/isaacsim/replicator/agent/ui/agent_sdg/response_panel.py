from typing import List

import carb
from isaacsim.replicator.agent.core.response.core import ResponsePickAgent
from isaacsim.replicator.agent.core.config_file.defines import ResponseProperty, CommandResponseProperty
from isaacsim.replicator.agent.core.simulation import SimulationManager
from omni.metropolis.utils.config_file.property import ListPropertyGroup
from omni.metropolis.utils.ui_util import UIUtil, MinimalStringListModel
from omni.metropolis.utils.type_util import TypeUtil
from omni.metropolis.utils.triggers.ui_util import UITriggerHelper
from ..settings import *
from ..ui_util import *


def command_list_to_str(command_list: List[str]) -> str:
    if not command_list:
        return ""
    cmd_str = ""
    for cmd in command_list:
        cmd_str += (cmd + "\n")
    return cmd_str

def command_str_to_list(command_str: str) -> List[str]:
    if not command_str:
        return []
    return command_str.split("\n")


class ResponsePanel:

    def __init__(self, events, variables):
        self._variables = variables
        self._events = events
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(self.refresh_list_data)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(self.refresh_list_data)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED].append(self.refresh_list_data)
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._frame = None
        self._model = None
        self._delegate = None
        self._treeview = None

    def build_ui_frame(self):
        if self._frame == None:
            self._frame = ui.CollapsableFrame(
                title="Response",
                height=0,
                collapsed=True,
                style=get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                build_header_fn = lambda collapsed, title: UIUtil.build_collapsable_frame_header_with_image(collapsed, title,
                                                            "${omni.metropolis.utils}/data/ui_icons/Create Menu/icoAnimationClipTake.svg")
            )
            self.build_ui()

    def build_ui(self):
        with self._frame:
            with ui.VStack(height=0):
                self._model = ResponsePanel.UIResponseListModel()
                self._delegate = ResponsePanel.UIResponseListDelegate()
                self._treeview = ui.TreeView(
                    self._model,
                    delegate = self._delegate,
                    root_visible=False,
                    header_visible=True,
                )
                self.refresh_list_data()
                ui.Spacer(height=10)
                with ui.HStack(spacing=60):
                    add_btn = ui.Button(text=f"{UIUtil.get_plus_glyph()} Add", width=55, height=10, spacing=3)
                    add_btn.set_clicked_fn(self.on_add_btn)
                    del_btn = ui.Button(text=f"{UIUtil.get_minus_glyph()} Del", width=55, height=10, spacing=3)
                    del_btn.set_clicked_fn(self.on_del_btn)

    def on_add_btn(self):
        response_list : ListPropertyGroup = self._sim_manager.get_config_file_property_group("response", "response_list")
        if not response_list:
            return
        new_response = CommandResponseProperty()
        new_response.setup_by_default()
        response_list.add_to_list(new_response)
        self.refresh_list_data()

    def on_del_btn(self):
        response_list : ListPropertyGroup = self._sim_manager.get_config_file_property_group("response", "response_list")
        if not response_list:
            return
        if len(self._treeview.selection) == 0:
            carb.log_warn("No responses selected to delete.")
            return
        for select in self._treeview.selection:
            response_list.remove_from_list(select.response_prop)
        self.refresh_list_data()

    def refresh_list_data(self):
        self._model.load_response_list(self._sim_manager.get_config_file_property_group("response", "response_list"))

    class UIResponseItem(ui.AbstractItem):
        def __init__(self, item: ResponseProperty):
            super().__init__()
            self._model_changed_fn_list = []
            # Save the response property
            self.response_prop = item
            # UI models
            value_dict = self.response_prop.get_resolved_value()
            pick_agent_options = [str(p.value) for p in ResponsePickAgent]
            self.model_dict = {
                "name": ui.SimpleStringModel(value_dict["name"]),
                "priority": ui.SimpleIntModel(value_dict["priority"]),
                "pick_agent": MinimalStringListModel(pick_agent_options, pick_agent_options.index(value_dict["pick_agent"])),
                "resume": ui.SimpleBoolModel(value_dict["resume"]),
                "position": ui.SimpleStringModel(str(value_dict["position"]))
            }
            # Register UI edit callbacks
            self.model_dict["name"].add_end_edit_fn(lambda m: self._on_value_changed("name", m.get_value_as_string()))
            self.model_dict["priority"].add_end_edit_fn(lambda m: self._on_value_changed("priority", m.get_value_as_int()))
            self.model_dict["pick_agent"].add_item_changed_fn(lambda m, i: self._on_value_changed("pick_agent", m.get_selection()))
            self.model_dict["resume"].add_value_changed_fn(lambda m: self._on_value_changed("resume", m.get_value_as_bool()))
            self.model_dict["position"].add_end_edit_fn(lambda m: self._on_value_changed(
                "position",
                TypeUtil.str_to_carb_float3(m.get_value_as_string())
            ))

            # Handle CommandResponseProperty
            if isinstance(self.response_prop, CommandResponseProperty):
                self.model_dict["commands"] = ui.SimpleStringModel(command_list_to_str(item.get_resolved_value()["commands"]))
                self.model_dict["commands"].add_end_edit_fn(lambda m: self._on_value_changed(
                    "commands",
                    command_str_to_list(m.get_value_as_string())
                ))

            # Triggers
            self.setup_trigger_models()

        def setup_trigger_models(self):
            value_dict = self.response_prop.get_resolved_value().copy()
            self.trigger_helper = UITriggerHelper(value_dict["trigger"])
            self.trigger_helper.create_ui_models()
            self.trigger_helper.add_trigger_type_changed_fn(self._on_trigger_type_changed)
            self.trigger_helper.add_trigger_value_changed_fn(self._on_trigger_value_changed)

        def _on_trigger_type_changed(self, trigger_value_dict: dict):
            # Update to Property
            self._on_trigger_value_changed(trigger_value_dict)
            # Notify
            self._notify_model_changed()

        def _on_trigger_value_changed(self, trigger_value_dict: dict):
            value_dict = self.response_prop.get_resolved_value().copy()
            value_dict["trigger"] = trigger_value_dict
            self.response_prop.set_value(value_dict)

        def _on_value_changed(self, value_name, value):
            value_dict = self.response_prop.get_resolved_value().copy()
            value_dict[value_name] = value
            self.response_prop.set_value(value_dict)

        def get_model_by_name(self, name):
            return self.model_dict[name]

        def add_model_changed_fn(self, fn: callable):
            self._model_changed_fn_list.append(fn)

        def _notify_model_changed(self):
            for fn in self._model_changed_fn_list:
                fn(self)

    class UIResponseListModel(ui.AbstractItemModel):
        def __init__(self):
            super().__init__()
            self._children = []

        def load_response_list(self, response_list_prop_group : ListPropertyGroup):
            self._children.clear()
            if response_list_prop_group:
                self._children = [ResponsePanel.UIResponseItem(r) for r in response_list_prop_group.data_group]
                for item in self._children:
                    item.add_model_changed_fn(lambda m: self._item_changed(m))
            self._item_changed(None)

        def get_item_children(self, item):
            if item is not None:
                # Since we are doing a flat list, we return the children of root only.
                # If it's not root we return.
                return []
            return self._children

        def get_item_value_model_count(self, item):
            return 1 # Column count

    class UIResponseListDelegate(ui.AbstractItemDelegate):
        def __init__(self):
            super().__init__()

        def build_header(self, column_id):
            ui.Label("Responses", height=30)

        def build_widget(self, model, item, column_id, level, expanded):
            with ui.VStack(spacing=5):
                response_item : ResponsePanel.UIResponseItem = item
                with ui.HStack(spacing=5):
                    ui.Label(response_item.response_prop.name)
                with ui.HStack(spacing=5):
                    ui.Label("\tName", width=120)
                    ui.StringField(response_item.get_model_by_name("name"))
                with ui.HStack(spacing=5):
                    ui.Label("\tPriority", width=120)
                    ui.IntField(response_item.get_model_by_name("priority"))
                with ui.HStack(spacing=5):
                    ui.Label("\tPick Agent Rule", width=120)
                    ui.ComboBox(response_item.get_model_by_name("pick_agent"))
                with ui.HStack(spacing=5):
                    ui.Label("\tResume", width=120)
                    ui.CheckBox(response_item.get_model_by_name("resume"))
                with ui.HStack(spacing=5):
                    ui.Label("\tPosition", width=120)
                    ui.StringField(response_item.get_model_by_name("position"))
                if isinstance(response_item.response_prop, CommandResponseProperty):
                    with ui.HStack(spacing=5):
                        ui.Label("\tCommands", width=120, alignment=ui.Alignment.TOP)
                        ui.StringField(
                            model= response_item.get_model_by_name("commands"),
                            height=40,
                            multiline=True
                        )
                response_item.trigger_helper.create_ui()
