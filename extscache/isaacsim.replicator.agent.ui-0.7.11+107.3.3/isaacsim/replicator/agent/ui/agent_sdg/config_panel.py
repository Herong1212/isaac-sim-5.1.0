import carb
import asyncio
import omni.kit.app
import omni.replicator.core as rep
from isaacsim.replicator.agent.core.config_file.default import ConfigFileDefault
from isaacsim.replicator.agent.core.simulation import SimulationManager
from isaacsim.replicator.agent.ui.settings import *
from isaacsim.replicator.agent.ui.agent_sdg.sensor_stack import SensorStack
from isaacsim.replicator.agent.ui.ui_util import *
from isaacsim.replicator.agent.ui.agent_sdg.command_manager import CharacterCommandManager, RobotCommandManager
from omni.metropolis.utils.ui_util import UIUtil

SAVE_BTN_TEXT = "Save"
UNSAVE_BTN_TEXT = "*Save"
FRAME_RATE = 30

DG_BTN_START = "Start Data Generation"
DG_BTN_STOP = "Stop Data Generation"


class ConfigPanel:
    """
    Configuration File Panel in the PeopleSDG window.
    - Display the 'global' section in the config file format.
    - Manage data sync with the core extension.
    - Handle the menubar callback to load default scenes.
    """

    def __init__(self, events, variables):
        self._variables = variables
        self._events = events
        self._events[GLOBAL_EVENTS.MENU_LOAD_SCENE].append(self.on_load_menu_scene)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(self._on_config_file_loaded)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(self._on_config_file_failed_loading)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED].append(self._on_config_file_loaded)

        self._settings = carb.settings.get_settings()
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]
        self._frame = None
        self._collapsable_frame = None
        self._sensor_stack = SensorStack(self._events, self._variables)
        self._folder_picker_stringfield = None
        self._folder_picker_btn = None
        self._folder_picker_goto = None
        self._seed_field = None
        self._sim_length_second_field = None
        self._sim_length_frame_field = None

        self._asset_path_field = None
        self._asset_path_btn = None
        self._asset_path_goto = None
        self._save_btn = None
        self._dg_btn = None
        self.dg_sub = None

    def on_load_menu_scene(self, usd):
        # Fetch config file
        config_file = self._sim_manager.get_config_file()
        if not self._sim_manager.get_config_file():
            carb.log_error("No config file is loaded. Open scene from menu fails")
            return
        # Update the scene asset in config file
        prop = config_file.get_property("scene", "asset_path")
        prop.set_value(usd)
        # Update UI
        self._on_config_file_loaded()
        # Load scene directly
        from isaacsim.replicator.agent.core.stage_util import StageUtil

        StageUtil.open_stage(usd, False)

    def on_start(self):
        """Load existing of default config file to UI"""
        config_file = self._sim_manager.get_config_file()
        if config_file is not None:
            # Do not load
            self._folder_picker_stringfield.model.set_value(config_file.file_path)
            self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED]()
            return
        default_config_file_path = ConfigFileDefault.get_default_config_file_path()
        self.load_config_file(default_config_file_path)

    def load_config_file(self, config_file_path):
        # Update file path UI
        self._folder_picker_stringfield.model.set_value(config_file_path)
        # Load config file
        load_succeed = self._sim_manager.load_config_file(config_file_path)
        # Trigger events
        if load_succeed:
            self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED]()
        else:
            self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING]()

    def update_UI(self):
        self.update_UI_global_setting()
        self.update_UI_save_button()
        self.update_UI_button_enabled()
        self.update_UI_scene_asset_path()

    def update_UI_scene_asset_path(self):
        prop = self._sim_manager.get_config_file_property("scene", "asset_path")
        # Update field
        set_property_to_ui(self._asset_path_field, prop)
        # Update button enabled
        enabled = prop is not None
        self._asset_path_btn.enabled = enabled

    def update_UI_global_setting(self):
        # Update UI
        config_file = self._sim_manager.get_config_file()
        if not config_file:
            set_property_to_ui(self._seed_field, None)
            set_property_to_ui(self._sim_length_second_field, None)
            set_property_to_ui(self._sim_length_frame_field, None)
        else:
            set_property_to_ui(self._seed_field, config_file.get_property("global", "seed"))
            set_property_to_ui(self._sim_length_frame_field, config_file.get_property("global", "simulation_length"))
            self._on_sim_length_frames_edited(self._sim_length_frame_field)

    def update_UI_button_enabled(self):
        config_file = self._sim_manager.get_config_file()
        enabled = config_file is not None
        self._dg_btn.enabled = enabled
        self._save_btn.enabled = enabled
        self._reload_btn.enabled = enabled

    def update_UI_save_button(self):
        config_file = self._sim_manager.get_config_file()
        if not config_file or not config_file.is_dirty():
            self._save_btn.text = SAVE_BTN_TEXT
        else:
            self._save_btn.text = UNSAVE_BTN_TEXT

    def _on_config_file_loaded(self):
        # Update UI
        self.update_UI()
        # Monitor config file update
        config_file = self._sim_manager.get_config_file()
        config_file.register_update_func(lambda _: self.update_UI_save_button())

    def _on_config_file_failed_loading(self):
        # Message
        carb.log_error("Loading config file fails.")
        # Self UI
        self.update_UI()

    def _on_dg_btn(self):
        if self._dg_btn.text == DG_BTN_START:
            self.dg_sub = self._sim_manager.register_data_generation_callback(lambda e: self._on_dg_btn())
            asyncio.ensure_future(self._sim_manager.run_data_generation_async(will_wait_until_complete=True))
            self._dg_btn.text = DG_BTN_STOP
        else:
            self.dg_sub = None
            rep.orchestrator.stop()
            self._dg_btn.text = DG_BTN_START

    def _ui_load_config_file_callback(self, filename, path):
        # Load yaml file
        new_path = os.path.join(path, filename)
        self.load_config_file(new_path)

    def _save_btn_callback(self):
        if self._sim_manager.save_config_file():
            self.update_UI_save_button()
            self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED]()

    def _save_as_btn_callback(self):
        def on_selected(filename, path):
            if filename:
                carb.log_error(
                    "Expect folder selection but received file selection. Please select a folder to save config and command files."
                )
                file_picker.hide()
                return
            character_command_list = CharacterCommandManager.get_instance().get_commands_list()
            robot_command_list = RobotCommandManager.get_instance().get_commands_list()
            if self._sim_manager.save_as_config_file(path, character_command_list, robot_command_list):
                self._folder_picker_stringfield.model.set_value(self._sim_manager.get_config_file().file_path)
                self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED]()  # Manually trigger a reload
            file_picker.hide()

        def on_canceled(a, b):
            file_picker.hide()

        def filter_folder(item):
            if not item or item.is_folder:
                return True
            return False

        file_picker = FilePickerDialog(
            "Select Folder to Save As",
            allow_multi_selection=False,
            apply_button_label="Select",
            click_apply_handler=lambda a, b: on_selected(a, b),
            click_cancel_handler=lambda a, b: on_canceled(a, b),
            item_filter_fn=filter_folder,
            enable_versioning_pane=True,
        )

    def _on_config_file_path_edited(self, model):
        cur_path = self._variables[GLOBAL_VARIABLES.CONFIG_FILE_PATH]
        new_path = model.get_value_as_string()
        if new_path != cur_path:
            self._ui_load_config_file_callback(new_path, "")

    def _on_asset_picked(self, filename, path):
        prop = self._sim_manager.get_config_file_property("scene", "asset_path")
        set_ui_to_property(self._asset_path_field, prop)

    def _on_asset_path_edited(self, model):
        prop = self._sim_manager.get_config_file_property("scene", "asset_path")
        set_ui_to_property(self._asset_path_field, prop)

    def _on_sim_length_seconds_edited(self, ui_element):
        self._sim_length_frame_field.model.set_value(round(ui_element.model.get_value_as_float(), 2) * FRAME_RATE)
        set_ui_to_property(
            self._sim_length_frame_field,
            self._sim_manager.get_config_file_property("global", "simulation_length"),
        )

    def _on_sim_length_frames_edited(self, ui_element):
        self._sim_length_second_field.model.set_value(ui_element.model.get_value_as_int() / FRAME_RATE)
        set_ui_to_property(
            self._sim_length_frame_field,
            self._sim_manager.get_config_file_property("global", "simulation_length"),
        )

    def build_ui(self):
        with self._frame:
            with ui.HStack():
                ui.Spacer(width=10)
                with ui.VStack(spacing=0, height=0):
                    ui.Spacer(height=15)
                    self._folder_picker_stringfield, self._folder_picker_btn, self._folder_picker_goto = build_folder_picker(
                        label="Config File Path",
                        dialog_title="Select A Configuration File",
                        default_val="",
                        file_extension_type=FOLDER_PICKER_TYPE.YAML,
                        on_folder_picked=self._ui_load_config_file_callback,
                    )
                    self._folder_picker_stringfield.model.add_end_edit_fn(self._on_config_file_path_edited)

                    ui.Spacer(height=10)
                    with ui.HStack(spacing=0):
                        ui.Spacer(width=120)
                        self._reload_btn = ui.Button(text="Set Up Simulation")
                        self._reload_btn.set_clicked_fn(self.set_up_simulation_callback)
                        ui.Spacer(width=5)
                        self._save_btn = ui.Button(text=SAVE_BTN_TEXT, width=100, height=30, alignment=ui.Alignment.CENTER)
                        self._save_btn.set_clicked_fn(self._save_btn_callback)
                        ui.Spacer(width=10)

                    ui.Spacer(height=5)
                    with ui.HStack(spacing=0):
                        ui.Spacer(width=120)
                        self._dg_btn = ui.Button(text=DG_BTN_START)
                        self._dg_btn.set_clicked_fn(self._on_dg_btn)
                        ui.Spacer(width=5)
                        self._save_as_btn = ui.Button(text="Save As", width=100, height=30, alignment=ui.Alignment.CENTER)
                        self._save_as_btn.set_clicked_fn(self._save_as_btn_callback)
                        self._save_as_btn.set_tooltip(
                            "This button will save the config file and the command files for the agents. Please enter a folder path instead of filename to store these files."
                        )
                        ui.Spacer(width=10)

                    ui.Spacer(height=5)

            with self._collapsable_frame:
                with ui.VStack(spacing=10, height=0):
                    with ui.HStack(alignment=ui.Alignment.CENTER):
                        self._asset_path_field, self._asset_path_btn, self._asset_path_goto = build_folder_picker(
                            "Scene Asset Path", "Select A USD Scene", "", FOLDER_PICKER_TYPE.USD, self._on_asset_picked
                        )
                        self._asset_path_field.model.add_end_edit_fn(self._on_asset_path_edited)

                    with ui.HStack(alignment=ui.Alignment.CENTER):
                        ui.Label("Seed", width=UI_DISTANCE)
                        self._seed_field = ui.IntField()
                        self._seed_field.model.add_end_edit_fn(
                            lambda m: set_ui_to_property(
                                self._seed_field, self._sim_manager.get_config_file_property("global", "seed")
                            )
                        )

                    with ui.HStack(alignment=ui.Alignment.CENTER):
                        ui.Label("Simulation Length", width=UI_DISTANCE)
                        with ui.ZStack():
                            self._sim_length_frame_field = ui.IntField()
                            with ui.HStack(style={"Label": {"color": 0xFF777777}}):
                                ui.Label("frames", alignment=ui.Alignment.RIGHT_CENTER)
                                ui.Spacer(width=5)
                            self._sim_length_frame_field.model.add_end_edit_fn(
                                lambda m: self._on_sim_length_frames_edited(self._sim_length_frame_field)
                            )
                        ui.Label("=", width=50, alignment=ui.Alignment.CENTER)
                        with ui.ZStack():
                            self._sim_length_second_field = ui.FloatField(precision=2)
                            with ui.HStack(style={"Label": {"color": 0xFF777777}}):
                                ui.Label("seconds", alignment=ui.Alignment.RIGHT_CENTER)
                                ui.Spacer(width=5)
                            self._sim_length_second_field.model.add_end_edit_fn(
                                lambda m: self._on_sim_length_seconds_edited(self._sim_length_second_field)
                            )

                    UIUtil.add_separator("Add Sensors")
                    self._sensor_stack.build_ui()


    def build_ui_frame(self):
        if self._frame == None:
            self._frame = ui.Frame()
            self._collapsable_frame = ui.CollapsableFrame(
                title="SDG Setup",
                height=0,
                collapsed=False,
                style=get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                build_header_fn = lambda collapsed, title: UIUtil.build_collapsable_frame_header_with_image(collapsed, title,
                                                            "${omni.metropolis.utils}/data/ui_icons/Create Menu/icoEnvironments.svg")
            )
            self.build_ui()

    def set_up_simulation_callback(self):
        if self._sim_manager.get_config_file() is None:
            carb.log_warn("Config file is not loaded. Set up simulation fails.")
            return
        self._sim_manager.set_up_simulation_from_config_file()
