import asyncio
import carb
import omni.usd
import omni.ui as ui
from isaacsim.replicator.agent.core.simulation import SimulationManager
from isaacsim.replicator.agent.ui.agent_sdg.command_manager import CharacterCommandManager, RobotCommandManager
from isaacsim.replicator.agent.ui.ui_util import *
from omni.metropolis.utils.ui_util import MinimalStringListModel
from omni.kit.notification_manager import post_notification, NotificationStatus

SAVE_BTN_TEXT = "Save Commands"
UNSAVE_BTN_TEXT = "*Save Commands"


def command_list_to_string_input(command_list):
    output = ""
    if not command_list:
        return output
    for command in command_list:
        output = output + str(command)
        output = output + "\n"
    return output


class CommandEditor:
    """
    UI section for agent selection dropdown and command editor textbox.
    - Uses CommandManager for formatting commands.
    - Used by both Character Panel and Robot Panel.
    """

    def __init__(self, motherPanel, events, variables, agent_name):
        self._events = events
        self._variables = variables
        self.motherPanel = motherPanel
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(self._on_config_file_loaded)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(self._on_config_file_failed_loading)
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._agent_name = agent_name
        self._command_manager = self.get_command_manager_by_agent_name()
        self._agent_combo_box = None
        self._textbox = None
        self._randomize_btn = None

        self._folder_picker_field = None
        self._folder_picker_btn = None
        self._folder_picker_goto = None
        self._folder_picker_save = None

        self._command_saved = True
        self._timeline = omni.timeline.get_timeline_interface()
        self._subs = [
            self._timeline.get_timeline_event_stream().create_subscription_to_pop(self.on_timeline_event),
        ]

        self._build_ui()

    def destroy(self):
        self._subs = []

    def _build_ui(self):
        with self.motherPanel:
            with ui.VStack(spacing=10):
                with ui.HStack():
                    self._folder_picker_field, self._folder_picker_btn, self._folder_picker_goto, self._folder_picker_save = build_folder_picker(
                        label="Command File",
                        dialog_title="Select A Command File",
                        default_val="",
                        file_extension_type=FOLDER_PICKER_TYPE.TXT,
                        on_folder_picked=lambda a, b: self.on_command_path_changed(),
                        on_file_save=lambda: self._on_save_commands(),
                    )
                    self._folder_picker_field.model.add_end_edit_fn(lambda m: self.on_command_path_changed())
                    self._folder_picker_goto.set_mouse_pressed_fn(lambda x, y, b, _: self._goto_command_file())

                with ui.HStack():
                    ui.Spacer(width=UI_DISTANCE)
                    self._randomize_btn = ui.Button(text="Generate Random Commands")
                    self._randomize_btn.set_clicked_fn(self._on_generate_random_commands)

                with ui.HStack():
                    ui.Label(self._agent_name.capitalize(), width=UI_DISTANCE)
                    self._minimal_model = MinimalStringListModel([])
                    self._agent_combo_box = ui.ComboBox(
                        self._minimal_model, style={"font_size": 16}
                    )
                    self._agent_combo_box.model.add_item_changed_fn(self._on_combo_changed)

                with ui.HStack():
                    ui.Label("Command", width=UI_DISTANCE)
                    self._textbox = ui.StringField(height=100, multiline=True)
                    self._textbox.model.add_value_changed_fn(self._on_textbox_changed)

    def on_command_path_changed(self):
        # Update config file
        prop = self._sim_manager.get_config_file_property(self._agent_name, "command_file")
        set_ui_to_property(self._folder_picker_field, prop)

    def _goto_command_file(self):
        command_file_path = self._sim_manager.get_config_file_valid_value(self._agent_name, "command_file")
        if command_file_path:
            content.get_content_window().navigate_to(command_file_path)
        else:
            carb.log_error(f"Command file path is not set for {self._agent_name}")

    def _on_config_file_loaded(self):
        config_file = self._sim_manager.get_config_file()
        # Monitor command file property
        prop = config_file.get_property(self._agent_name, "command_file")
        if prop:
            prop.register_update_func(lambda _: self._on_command_file_changed())
        # Manual trigger for update
        self._on_command_file_changed()

        # Update UI
        set_property_to_ui(self._folder_picker_field, prop)
        # Update button enabled
        enabled = prop is not None
        self._folder_picker_btn.enabled = enabled

    def _on_config_file_failed_loading(self):
        # Manual trigger for update
        self._on_command_file_changed()

    def _on_command_file_changed(self):
        # Reload commands into command manager
        command_list = self.load_commands_by_agent_name()
        self._command_manager.set_commands(command_list)
        # Refresh UI
        self.refresh_combo_box()
        self.update_save_state(True)
        self.update_UI_button_enabled()

    def refresh_combo_box(self):
        agent_list = self._command_manager.get_agent_list()
        if not agent_list:
            self._textbox.enabled = False
            self._agent_combo_box.model.set_item_children([])
        else:
            self._textbox.enabled = True
            self._agent_combo_box.model.set_item_children(agent_list)
        self._agent_combo_box.model._current_index.set_value(0)

    def update_save_state(self, is_saved):
        self._command_saved = is_saved
        # Refresh button text
        if not self._command_saved:
            self._folder_picker_save.set_style({"color": COLOR_DIRTY})
        else:
            self._folder_picker_save.set_style({"color": COLOR_BTN})

    def on_timeline_event(self, event):
        if event.type == int(omni.timeline.TimelineEventType.PLAY):
            if self._command_saved == False:
                post_notification(
                    f"{self._agent_name} command is not saved!",
                    status=NotificationStatus.WARNING,
                )

    def update_UI_button_enabled(self):
        value = self._sim_manager.get_config_file_valid_value(self._agent_name, "command_file")
        enabled = value is not None
        self._folder_picker_save.enabled = enabled
        self._randomize_btn.enabled = enabled

    def _on_combo_changed(self, model, item):
        if model.get_item_children():
            value = model.get_item_value_model()
            selected_item = value.get_value_as_int()
            selected_item = model.get_item_children()[selected_item]
            selected_item = model.get_item_value_model(selected_item)
            selected_agent_name = selected_item.get_value_as_string()
        else:
            selected_agent_name = None
        # Display command for selected agent
        self._command_manager.set_selected_agent(selected_agent_name)
        command_list = self._command_manager.get_selected_agent_command_without_name()
        self._textbox.model.set_value(command_list_to_string_input(command_list))

    def _on_textbox_changed(self, model):
        # Sync UI value to command manager
        string_block = str(model.get_value_as_string())
        commandlist = string_block.splitlines()
        currentList = self._command_manager.get_selected_agent_command_without_name()
        if commandlist == currentList:
            return
        self._command_manager.set_selected_agent_command_without_name(commandlist)
        # Update save state
        self.update_save_state(False)

    def _on_save_commands(self):
        save_succeed = self.save_commands_by_agent_name()
        self.update_save_state(save_succeed)

    def _on_generate_random_commands(self):
        async def gen_commands():
            task = asyncio.create_task(self.generate_random_commands_by_agent_name())
            await task
            commands = task.result()
            # Update command manager
            self._command_manager.set_commands(commands)
            # Refresh UI
            self.refresh_combo_box()
            self.update_save_state(False)

        asyncio.ensure_future(gen_commands())

    def get_command_manager_by_agent_name(self):
        if self._agent_name == "character":
            return CharacterCommandManager.get_instance()
        elif self._agent_name == "robot":
            return RobotCommandManager.get_instance()
        else:
            return None

    def load_commands_by_agent_name(self):
        if self._agent_name == "character":
            return self._sim_manager.load_commands()
        elif self._agent_name == "robot":
            return self._sim_manager.load_robot_commands()
        else:
            return None

    async def generate_random_commands_by_agent_name(self):
        if self._agent_name == "character":
            return await self._sim_manager.generate_random_commands()
        elif self._agent_name == "robot":
            return await self._sim_manager.generate_random_robot_commands()

    def save_commands_by_agent_name(self):
        if self._agent_name == "character":
            return self._sim_manager.save_commands(self._command_manager.get_commands_list())
        elif self._agent_name == "robot":
            return self._sim_manager.save_robot_commands(self._command_manager.get_commands_list())
        else:
            return False
