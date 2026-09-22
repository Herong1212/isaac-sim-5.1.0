# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import ast
import carb
import carb.events
import omni.kit.app
import omni.ui as ui
from isaacsim.replicator.agent.ui.settings import *
from isaacsim.replicator.agent.ui.ui_util import *
from isaacsim.replicator.agent.core.randomization.randomizer import CommandTransitionMap
from isaacsim.replicator.agent.core.simulation import SimulationManager
from isaacsim.replicator.agent.core.randomization.character_randomizer import CharacterRandomizer
from omni.metropolis.utils.ui_util import UIUtil


class CommandRandomizationPanel:
    def __init__(self, events, variables):
        self._events = events
        self._variables = variables
        self._frame = None
        self._model: CommandRandomizationPanel.UITransitionMapModel = None
        self._delegate: CommandRandomizationPanel.UITransitionMapDelegate = None
        self._treeview = None
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._character_randomizer: CharacterRandomizer = self._sim_manager.get_character_randomizer()

    def shutdown(self):
        pass

    def build_ui_frame(self, e=None):
        self._frame = ui.CollapsableFrame(
            title="Command Randomization",
            collapsed=False,
            style=get_collapsable_frame_style(),
            name="subFrame",
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        )
        self._build_transition_map_ui()

    def _build_transition_map_ui(self, e=None):
        with self._frame:
            with ui.VStack():
                # Transition map file picker
                with ui.HStack(height=30):
                    self._folder_picker_stringfield, self._folder_picker_btn, self._folder_picker_goto = build_folder_picker(
                        label="Transition Map File",
                        dialog_title="Select A Command Transition Map File",
                        default_val="",
                        file_extension_type=FOLDER_PICKER_TYPE.JSON,
                        on_folder_picked=self._load_file_callback,
                    )
                    self._folder_picker_stringfield.model.add_end_edit_fn(self._on_file_path_edit)
                    curr_path = self._character_randomizer.get_command_transition_map_path()
                    self._folder_picker_stringfield.model.set_value(curr_path)
                # Build transition map treeview
                self._model = CommandRandomizationPanel.UITransitionMapModel(self._character_randomizer)
                self._delegate = CommandRandomizationPanel.UITransitionMapDelegate()
                self._treeview = ui.TreeView(
                    self._model,
                    delegate=self._delegate,
                    column_widths=[160, 80, ui.Fraction(1.0)],
                    root_visible=False,
                    header_visible=True,
                )
                ui.Spacer(height=10)
                # Buttons
                with ui.HStack(spacing=30, height=30):
                    ui.Button(f"{UIUtil.get_plus_glyph()} Add", width=120).set_clicked_fn(self._on_add_btn)
                    ui.Button(f"{UIUtil.get_minus_glyph()} Del", width=120).set_clicked_fn(self._on_remove_btn)
                    ui.Button("Save", width=120).set_clicked_fn(self._character_randomizer.save_command_transition_map)

    def _load_file_callback(self, filename, path):
        new_path = filename if not path else f"{path}/{filename}"
        self._character_randomizer.load_command_transition_map(new_path)
        self._model.load_transition_map()

    def _on_file_path_edit(self, model):
        curr_path = self._character_randomizer.get_command_transition_map_path()
        new_path = model.get_value_as_string()
        if curr_path != new_path:
            self._load_file_callback(new_path, "")

    def _on_add_btn(self):
        transition_map = self._character_randomizer.get_command_transition_map()
        transition_map.add_command(command_name="", weight=0.0, transitions={})
        self._model.load_transition_map()

    def _on_remove_btn(self):
        if len(self._treeview.selection) == 0:
            carb.log_warn("Please select a command to remove.")
            return
        transition_map = self._character_randomizer.get_command_transition_map()
        for select in self._treeview.selection:
            cmd_name = select.name_model.get_value_as_string()
            transition_map.remove_command(cmd_name)
        self._model.load_transition_map()

    class UICommandItem(ui.AbstractItem):
        def __init__(self, item: CommandTransitionMap.Command):
            super().__init__()
            self.command = item
            self.name_model = ui.SimpleStringModel(item.name)
            self.weight_model = ui.SimpleFloatModel(item.weight)
            self.transitions_model = ui.SimpleStringModel(str(item.transitions))  # Temporarliy display it as String
            # Register UI edit callbacks
            self.name_model.add_end_edit_fn(self._on_name_edit)
            self.weight_model.add_end_edit_fn(self._on_weight_edit)
            self.transitions_model.add_end_edit_fn(self._on_transitions_edit)

        def get_name_model(self):
            return self.name_model

        def get_weight_model(self):
            return self.weight_model

        def get_transitions_model(self):
            return self.transitions_model

        def _on_name_edit(self, m):
            self.command.name = m.get_value_as_string()

        def _on_weight_edit(self, m):
            self.command.weight = m.get_value_as_float()

        def _on_transitions_edit(self, m):
            try:
                dict_data = ast.literal_eval(m.get_value_as_string())
                self.command.transitions = dict_data
            except:
                carb.log_error("Unable to parse string into dict format, please try again.")
                m.set_value(str(self.command.transitions))

    class UITransitionMapModel(ui.AbstractItemModel):
        def __init__(self, character_randomizer: CharacterRandomizer):
            super().__init__()
            self._character_randomizer = character_randomizer
            self._children = []
            self.load_transition_map()

        def load_transition_map(self):
            self._children.clear()
            transition_map = self._character_randomizer.get_command_transition_map()
            commands = transition_map.get_all_commands()
            self._children = [CommandRandomizationPanel.UICommandItem(cmd) for cmd in commands]
            self._item_changed(None)

        def get_item_children(self, item):
            if item is not None:
                return []
            return self._children

        def get_item_value_model_count(self, item):
            return 3  # Column count

    class UITransitionMapDelegate(ui.AbstractItemDelegate):
        def __init__(self):
            super().__init__()

        def build_header(self, column_id):
            height = 30
            if column_id == 0:
                ui.Label("Command Name", height=height)
            elif column_id == 1:
                ui.Label("Weight", height=height)
            elif column_id == 2:
                ui.Label("Transitions", height=height)

        def build_widget(self, model, item, column_id, level, expanded):
            stack = ui.ZStack(height=30)
            with stack:
                if not isinstance(item, CommandRandomizationPanel.UICommandItem):
                    ui.Label("item is not UICommandItem.")
                else:
                    commandItem: UICommandItem = item
                    if column_id == 0:
                        with ui.HStack(alignment=ui.Alignment.BOTTOM):
                            model = commandItem.get_name_model()
                            ui.StringField(model)
                    elif column_id == 1:
                        with ui.HStack(alignment=ui.Alignment.BOTTOM):
                            model = commandItem.get_weight_model()
                            ui.FloatField(model)
                    elif column_id == 2:
                        model = commandItem.get_transitions_model()
                        ui.StringField(model)
