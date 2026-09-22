# flake8: noqa
import asyncio
import json
from pathlib import Path

import carb
import numpy as np
import omni.anim.navigation.core as nav
import omni.client
import omni.kit
import omni.usd
from omni.metropolis.utils.debug_util import DebugPrint
from omni.metropolis.utils.file_util import CommandFileUtil, FileUtil
from omni.metropolis.utils.semantics_util import SemanticsUtils
from pxr import Sdf

import NavSchema

from omni.metropolis.utils.config_file.core import ConfigFile
from .data_generation.data_generation import DataGeneration
from .randomization.camera_randomizer import CameraRandomizer
from .randomization.carter_randomizer import CarterRandomizer
from .randomization.character_randomizer import CharacterRandomizer
from .randomization.randomizer_util import RandomizerUtil
from .randomization.iw_hub_randomizer import IwHubRandomizer
from .response.core import AgentResponseManager
from .settings import AssetPaths, PrimPaths, BehaviorScriptPaths, Settings, GlobalValues
from .stage_util import CameraUtil, CharacterUtil, RobotUtil, StageUtil, AgentUtil
from .incident_bridge import IncidentBridge

FRAME_RATE = 30

OMNI_ANIM_PEOPLE_COMMAND_PATH = "/exts/omni.anim.people/command_settings/command_file_path"
ANIM_ROBOT_COMMAND_PATH = "/exts/isaacsim.anim.robot/command_settings/command_file_path"

dp = DebugPrint(Settings.DEBUG_PRINT, "SimulationManager")


class SimulationManager:
    """
    Simulation Manager class that takes in config file to set up simulation accordingly.
    """

    SET_UP_SIMULATION_DONE_EVENT = "isaacsim.replicator.agent.SET_UP_SIMULATION_DONE"
    DATA_GENERATION_DONE_EVENT = "isaacsim.replicator.agent.DATA_GENERATION_DONE_EVENT"

    def __init__(self):
        self.character_assets_list = (
            []
        )  # List of all characters inside the character asset folders, provided by config file
        self.available_character_list = []  # Character list after filtering and shuffling
        # Config file variables
        self.config_file: ConfigFile = None
        # Randomizers
        self._character_randomizer = CharacterRandomizer(0)
        self._nova_carter_randomizer = CarterRandomizer(0)
        self._iw_hub_randomizer = IwHubRandomizer(0)
        self._camera_randomizer = CameraRandomizer(0)
        self._agent_positions = []
        # State variables for assets loading
        self._load_stage_handle = None
        # Incident bridge
        self._incident_bridge = IncidentBridge()
        self._dg = None
        self._dg_task = None

    # ========= Set Up Characters/Robots =========

    def load_filters(self):
        """
        Load the filters from the asset folder
        The filter must be a json file named "filter" and located in the asset root directory
        """
        if not self.config_file:
            return None
        prop = self.config_file.get_property("character", "asset_path")
        if not prop:
            carb.log_error("Unable to get character asset path. Will not load filter file.")
            return None
        if prop.is_value_error():
            carb.log_error("Character asset path has error. Will not load filter file.")
            return None
        file_path = prop.get_resolved_value()
        # Making sure that the path ends with a slash
        if file_path[-1] != "/":
            file_path += "/"
        file_path += "filter.json"
        result, _, content = omni.client.read_file(file_path)
        data = {}
        if result == omni.client.Result.OK:
            data = json.loads(memoryview(content).tobytes().decode("utf-8"))
        # Handling the case if the file does not exist
        else:
            carb.log_warn("Filter file does not exist. Asset filtering will not function.")
            return None
        return data  # noqa

    def spawn_character_by_idx(self, spawn_location, spawn_rotation, idx):
        """
        Spawns character according to index in the character folder list at provided spawn_location and spawn_rotation.
        Ensures duplicate characters are not spawned, until all character assets have been utilized.
        If all character assets have been utilized, duplicates will be spawned.
        """
        # Character name
        char_name = CharacterUtil.get_character_name_by_index(idx)
        # Characters will be spawned in the same order again if all unique assets are used
        list_len = len(self.available_character_list)
        if list_len == 0:
            carb.log_error("Unable to spawn character due to no character assets found.")
            return None
        # Loop the list if there are multiple characters
        idx = idx % list_len  # noqa
        # The character assets are randomly sorted by global seed when the assets is selected
        # This draws the character based on the index, producing a deterministic result
        char_asset_name = self.available_character_list[idx]
        prop = self.config_file.get_property("character", "asset_path")
        if prop.is_value_error():
            carb.log_error("Unable to spawn character due to invalid character asset path.")
            return None
        asset_root_path = prop.get_resolved_value()
        character_folder = f"{asset_root_path}/{char_asset_name}"
        # Get the usd present in the character folder
        character_usd_name = self._get_character_usd_in_folder(character_folder)
        if not character_usd_name:
            carb.log_error("Unable to spawn character due to no character usd present in folder.")
            return None
        character_usd_path = f"{character_folder}/{character_usd_name}"
        # Spawn character
        return CharacterUtil.load_character_usd_to_stage(character_usd_path, spawn_location, spawn_rotation, char_name)

    def _get_character_usd_in_folder(self, character_folder_path):
        result, folder_list = omni.client.list(character_folder_path)
        if result != omni.client.Result.OK:
            carb.log_error(f"Unable to read character folder path at {character_folder_path}")
            return None
        for item in folder_list:
            if item.relative_path.endswith(".usd"):
                return item.relative_path
        carb.log_error(f"Unable to file a .usd file in {character_folder_path} character folder")
        return None

    def read_character_asset_list(self):
        """
        Read character assets into list according to the character asset path in config file
        """
        prop = self.config_file.get_property("character", "asset_path")
        if not prop:
            return
        if prop.is_value_error():
            carb.log_error("Unable to get character assets from character asset path.")
            return
        assets_root_path = prop.get_resolved_value()
        # List all files in characters directory
        result, folder_list = omni.client.list(f"{assets_root_path}/")
        if result != omni.client.Result.OK:
            carb.log_error("Unable to get character assets from character asset path.")
            self.character_assets_list = []
            return
        # Prune items from folder list that are not directories.
        pruned_folder_list = [
            folder.relative_path
            for folder in folder_list
            if (folder.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) and not folder.relative_path.startswith(".")
        ]
        if pruned_folder_list is None or len(pruned_folder_list) == 0:
            self.character_assets_list = []
            return
        # Prune folders that do not have usd inside
        pruned_usd_folder_list = []
        for folder in pruned_folder_list:
            result, file_list = omni.client.list(f"{assets_root_path}/{folder}/")
            for file in file_list:
                post_fix = file.relative_path[file.relative_path.rfind(".") + 1 :].lower()
                if post_fix in ("usd", "usda"):
                    pruned_usd_folder_list.append(folder)
                    break
        # Prune the default biped character
        biped_name = AssetPaths.default_biped_asset_name()
        if biped_name in pruned_usd_folder_list:
            pruned_usd_folder_list.remove(biped_name)
        # Prune exclusive folders
        exclusive_character_folders = AssetPaths.exclusive_character_folders()
        for folder in exclusive_character_folders:
            if folder in pruned_usd_folder_list:
                pruned_usd_folder_list.remove(folder)
        self.character_assets_list = pruned_usd_folder_list

    def refresh_available_character_asset_list(self):
        """
        Set avaliable character asset list by filtering and shuffling the character assets list.
        """
        if len(self.character_assets_list) == 0:
            self.available_character_list = []
            return
        prop = self.config_file.get_property("character", "filters")
        labels = prop.get_resolved_value()
        self.available_character_list = self.character_assets_list.copy()
        filters = self.load_filters()
        self.filter_character_asset_list(filters, labels)
        self.shuffle_character_asset_list()

    def shuffle_character_asset_list(self):
        """
        Deterministically shuffle the order of characters in the available asset list.
        """
        # Nothing to do for empty or single-item lists
        if not self.available_character_list or len(self.available_character_list) <= 1:
            return
        # Resolve and validate seed
        seed = self.get_config_file_valid_value("global", "seed")
        if seed is None:
            carb.log_warn("Shuffle character asset list fails due to invalid global seed.")
            return
        # Create RNG and shuffle
        seed_value = RandomizerUtil.handle_overflow(seed)
        rng = np.random.default_rng(seed_value)
        self.available_character_list = rng.permutation(self.available_character_list).tolist()

    def filter_character_asset_list(self, filters, labels):
        """
        Given labels, return character assets with these labels
        """
        # Filter file does not exist, skip the filtering
        if filters is not None:
            filtered = self.available_character_list
            for label in labels:
                if label in filters:
                    filtered = [char for char in filtered if char in filters[label]]
                # Handle non-existent labels
                else:
                    if label != "" and label != " ":  # noqa
                        carb.log_warn(
                            f'Invalid character filter label: "{label}". Available labels: {", ".join(filters.keys())}'
                        )
                        labels.remove(label)
            self.available_character_list = filtered

    @dp.debug_func
    def setup_python_scripts_to_robot(self, robot_list, robot_type):
        """
        Add behavior script to all characters in stage
        """
        script_path = BehaviorScriptPaths.robot_behavior_script_path(robot_type)
        dp.print(f"To use behavior script: {script_path}.")
        for prim in robot_list:
            omni.kit.commands.execute("ApplyScriptingAPICommand", paths=[Sdf.Path(prim.GetPrimPath())])
            attr = prim.GetAttribute("omni:scripting:scripts")
            # Get the corresponding robot script
            attr.Set([f"{script_path}"])
            dp.print(f"Set up python script for robot, prim = {prim.GetPrimPath()}.")

    def refresh_randomizers(self):
        """
        Refresh randomizers with global seed.
        """
        prop = self.config_file.get_property("global", "seed")
        if prop.is_value_error():
            carb.log_error("Refresh randomizers fails due to invalid global seed.")
            return
        seed = prop.get_resolved_value()
        self._character_randomizer.update_seed(seed)
        self._camera_randomizer.update_seed(seed)
        self._nova_carter_randomizer.update_seed(seed)
        self._iw_hub_randomizer.update_seed(seed)

    # ========= Config File =========

    def load_config_file(self, file_path):
        """
        Load config file object by input file path.
        """
        self.config_file = GlobalValues.config_file_format.load_config_file(file_path)
        if not self.config_file:
            carb.log_error(f"Config file cannot be loaded from: {file_path}.")
            return False
        self._on_config_file_loaded()
        return True

    def _on_config_file_loaded(self):
        # Register property listeners
        self.register_property_listeners()
        # Self refresh
        self.refresh_randomizers()
        self.read_character_asset_list()
        self.refresh_available_character_asset_list()
        # Response refresh
        AgentResponseManager.get_instance().reset()

    def save_config_file(self):
        if not self.config_file:
            carb.log_error("Unable to save config file due to no loaded config file.")
            return False
        if not self.config_file.save():
            return False
        self._on_config_file_loaded()
        return True

    def save_as_config_file(self, folder_path, commands_list, robot_commands_list):
        if not self.config_file:
            carb.log_error("Unable to save as config file due to no config file is loaded.")
            return False
        # New file paths
        folder_path = Path(folder_path)
        new_config_file_path = str(folder_path / "config.yaml")
        new_cmd_file_path = str(folder_path / "command.txt")
        new_robot_cmd_file_path = str(folder_path / "robot_command.txt")
        # Create and point to new command files
        cmd_prop = self.get_config_file_property("character", "command_file")
        if cmd_prop:
            CommandFileUtil.save_command_file(new_config_file_path, new_cmd_file_path, commands_list)
            cmd_prop.set_value(new_cmd_file_path)
        robot_cmd_prop = self.get_config_file_property("robot", "command_file")
        if robot_cmd_prop:
            CommandFileUtil.save_command_file(new_config_file_path, new_robot_cmd_file_path, robot_commands_list)
            robot_cmd_prop.set_value(new_robot_cmd_file_path)
        # Save this current config file
        if not self.config_file.save_as(new_config_file_path):
            return False
        # Load the new config file
        return self.load_config_file(new_config_file_path)


    def get_config_file(self):
        return self.config_file

    def clear_config_file(self):
        self.config_file = None

    def register_property_listeners(self):
        """
        Register listeners for config file properties to update internal states accordingly.
        """

        def on_global_seed_update(new_val):
            self.refresh_randomizers()
            self.refresh_available_character_asset_list()

        def on_character_asset_update(new_val):
            self._character_randomizer.reset()
            self.read_character_asset_list()
            self.refresh_available_character_asset_list()

        def on_character_filter_update(new_val):
            self._character_randomizer.reset()
            self.refresh_available_character_asset_list()

        def try_register_prop_update(section_name, prop_name, func):
            prop = self.config_file.get_property(section_name, prop_name)
            if prop:
                prop.register_update_func(func)

        def on_character_command_file_update(new_val):
            self.setup_anim_people_command_from_config_file()

        def on_robot_command_file_update(new_val):
            self.setup_anim_people_robot_command_from_config_file()

        # Global section
        try_register_prop_update("global", "seed", on_global_seed_update)
        # Character section
        try_register_prop_update("character", "asset_path", on_character_asset_update)
        try_register_prop_update("character", "filters", on_character_filter_update)
        try_register_prop_update("character", "command_file", on_character_command_file_update)
        # Robot section
        try_register_prop_update("robot", "command_file", on_robot_command_file_update)

    def get_config_file_property(self, section_name, property_name):
        """
        Get Property from loaded config file.
        Return None if config file is not loaded.
        """
        if not self.config_file:
            return None
        return self.config_file.get_property(section_name, property_name)

    def get_config_file_property_group(self, section_name, property_group_name):
        """
        Get PropertyGroup from loaded config file.
        Return None if config file is not loaded.
        """
        if not self.config_file:
            return None
        return self.config_file.get_property_group(section_name, property_group_name)

    def get_config_file_valid_value(self, section_name, property_name):
        """
        Get a valid Property value from loaded config file.
        Return None if Property cannot be fetched or its value is error.
        """
        prop = self.get_config_file_property(section_name, property_name)
        if not prop or prop.is_value_error() or not prop.is_setup():
            return None
        return prop.get_resolved_value()

    def get_config_file_section(self, section_name):
        if not self.config_file:
            return None
        return self.config_file.get_section(section_name)

    # ========= Characters/Robots Commands =========

    def load_commands(self):
        command_file_path = self.get_config_file_valid_value("character", "command_file")
        if command_file_path:
            return CommandFileUtil.load_command_file(self.config_file.file_path, command_file_path)
        else:
            return []

    def load_robot_commands(self):
        command_file_path = self.get_config_file_valid_value("robot", "command_file")
        if command_file_path:
            return CommandFileUtil.load_command_file(self.config_file.file_path, command_file_path)
        else:
            return []

    def save_commands(self, commands_list):
        command_file_path = self.get_config_file_valid_value("character", "command_file")
        if command_file_path:
            return CommandFileUtil.save_command_file(self.config_file.file_path, command_file_path, commands_list)
        else:
            carb.log_warn(
                "Unable to save character commands due to not getting character command file from config file."
            )
            return False

    def save_robot_commands(self, robot_commands_list):
        command_file_path = self.get_config_file_valid_value("robot", "command_file")
        if command_file_path:
            return CommandFileUtil.save_command_file(self.config_file.file_path, command_file_path, robot_commands_list)
        else:
            carb.log_warn("Unable to save robot commands due to not getting robot command file from config file.")
            return False

    async def generate_random_commands(self):
        """
        Generate random character commands by the current config file.
        """
        global_seed = self.get_config_file_valid_value("global", "seed")
        duration: float = self.get_config_file_valid_value("global", "simulation_length") / FRAME_RATE
        agent_count = self.get_config_file_valid_value("character", "num")
        navigation_area = self.get_config_file_valid_value("character", "navigation_area")
        if not global_seed:
            carb.log_error("Unable to generate random commands due to invalid seed in config file.")
            return []
        if not duration:
            carb.log_error("Unable to generate random commands due to invalid duration in config file.")
            return []
        if agent_count is None:
            carb.log_error("Unable to generate random commands due to invalid character number in config file.")
            return []
        else:
            task = asyncio.create_task(
                self._character_randomizer.generate_character_commands(
                    global_seed, duration, agent_count, navigation_area
                )
            )
            await task
            return task.result()

    # @dp.debug_func
    async def generate_random_robot_commands(self):
        """
        Generate random robot commands by the current config file.
        """
        seed = self.get_config_file_valid_value("global", "seed")
        duration: float = self.get_config_file_valid_value("global", "simulation_length") / FRAME_RATE
        nova_carter_count = self.get_config_file_valid_value("robot", "nova_carter_num")
        iw_hub_count = self.get_config_file_valid_value("robot", "iw_hub_num")
        navigation_area = self.get_config_file_valid_value("robot", "navigation_area")
        if not seed:
            carb.log_error("Unable to generate robot commands due to invalid seed in config file.")
            return []
        if not duration:
            carb.log_error("Unable to generate robot commands due to invalid simulation length in config file.")
            return []
        commands = []
        if nova_carter_count is not None:
            task = asyncio.create_task(
                self._nova_carter_randomizer.generate_robot_commands(
                    seed, duration, "Nova_Carter", nova_carter_count, navigation_area
                )
            )
            await task
            commands += task.result()
        else:
            carb.log_error("Unable to generate nova careter commands due to invalid nova carter number.")
        if iw_hub_count is not None:
            task = asyncio.create_task(
                self._iw_hub_randomizer.generate_robot_commands(seed, duration, "iw_hub", iw_hub_count, navigation_area)
            )
            await task
            commands += task.result()
        else:
            carb.log_error("Unable to generate iw.hub commands due to invalid iw.hub number.")
        # dp.print(f"Commands = {commands}")
        return commands

    # ========= Data Generation =========

    def register_data_generation_callback(self, on_event: callable):
        return carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=SimulationManager.DATA_GENERATION_DONE_EVENT, on_event=on_event,
            observer_name="isaacsim/replicator/agent/core/simulation/ON_DATA_GENERATION_DONE"
        )

    async def run_data_generation_async(self, will_wait_until_complete):
        if not self.config_file:
            carb.log_error("Config file is not loaded. Start data generation fails.")
            return

        sim_length = self.get_config_file_valid_value("global", "seed")
        if not sim_length:
            carb.log_error("Simulation Length is invalid. Start data generation fails.")
            return

        self._dg = DataGeneration(self.config_file)
        self._dg.register_recorder_done_callback(self._data_generation_done_callback)

        writer_selection_group = self.config_file.get_property_group( "replicator", "writer_selection")
        output_dir = writer_selection_group.content_prop.get_resolved_value()["output_dir"]

        # use the empty output dir to stand for the none output writer.
        if output_dir :
            self._incident_bridge.start_recording(output_dir)

        await self._dg.run_async(will_wait_until_complete)

    def _data_generation_done_callback(self):
        """
        Release handle when data generation is finished.
        """
        # Clean up reference
        self._dg = None
        self._dg_task = None
        # Incident report
        # Check whether recording is activated:
        if self._incident_bridge.is_recording():
            self._incident_bridge.end_recording()
        # Mark complete
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=SimulationManager.DATA_GENERATION_DONE_EVENT,
            payload={}
        )
        carb.log_info("One data generation completes.")

    # ========= Set Up Simulation by Config File =========

    def set_up_simulation_from_config_file(self):
        self.load_scene_from_config_file()

    def register_set_up_simulation_done_callback(self, on_event: callable):
        return carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=SimulationManager.SET_UP_SIMULATION_DONE_EVENT, on_event=on_event,
            observer_name="isaacsim/replicator/agent/core/simulation/ON_SET_UP_SIMULATION_DONE"
        )

    def load_scene_from_config_file(self):
        """
        Load scene by config file and triggers load assets when scene is loaded.
        """
        scene_path = self.get_config_file_valid_value("scene", "asset_path")
        if not scene_path:
            carb.log_error("Unable to load scene due to missing scene path in config file.")
            return
        if scene_path != omni.usd.get_context().get_stage_url():
            # refresh randomizer and available character list in case global seed hasn't changed
            self.refresh_randomizers()
            self.refresh_available_character_asset_list()

            # Load scene done callback
            def load_scene_from_config_file_callback(event):
                # Release stage handle
                self._load_stage_handle = None
                # Load assets other than scene
                self.load_assets_to_scene()

            # Subscribe stage event
            self._load_stage_handle = carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOADED),
                on_event=load_scene_from_config_file_callback,
                observer_name="isaacsim/replicator/agent/core/simulation/ON_ASSETS_LOADED",
            )
            try:
                carb.log_info(f"To load scene from config file: {scene_path}")
                StageUtil.open_stage(scene_path)
            except:
                # Release event handle and do not procceed loading assets
                carb.log_error(f"Load scene ({scene_path}) fails. No assets will be loaded.")
                self._load_stage_handle = None
        else:
            # Skip loading stage. Load assets other than scene
            carb.log_info("The current scene matches the scene path in config file. Scene loading is skipped.")
            self._character_randomizer.reset()
            self._nova_carter_randomizer.reset()
            self._iw_hub_randomizer.reset()
            self.load_assets_to_scene()

    def load_assets_to_scene(self):
        """
        Trigger navemsh baking and load characters, robots and cameras.
        """

        async def try_bake_navmesh():
            # Load assets other than scene
            # It first makes sure nav mesh is ready, then load cameras and characters in navmesh ready callback
            _inav = nav.acquire_interface()
            _inav.start_navmesh_baking_and_wait()
            navmesh = _inav.get_navmesh()
            if navmesh is None:
                carb.log_error(
                    "NavMesh building failed. Please check whether the stage has a valid NavmeshVolume. "
                    "Will not load assets to scene."
                )
                return

            # When nav mesh is ready, load cameras and characters by config file.
            # Cameras are loaded at the end because their positions are affected by characters.
            if self.get_config_file_section("robot"):
                self.load_robot_from_config_file()
                self.setup_anim_people_robot_command_from_config_file()
            else:
                carb.log_info("No robot section in the config file. Skip robot setup.")

            if self.get_config_file_section("character"):
                self.load_characters_from_config_file()
                self.setup_all_characters()
                self.setup_anim_people_command_from_config_file()
            else:
                carb.log_info("No character section in the config file. Skip character setup.")

            if self.get_config_file_section("event"):
                self.setup_incidents_from_config_file()
            else:
                carb.log_info("No incident section in the config file. Skip incident setup.")

            response_section = self.get_config_file_section("response")
            if response_section:
                AgentResponseManager.get_instance().reset()
                AgentResponseManager.get_instance().setup_responses_from_config_file(response_section)
            else:
                carb.log_info("No response section in the config file. Skip agent response setup.")

            self.load_camera_from_config_file()
            # Mark complete
            carb.eventdispatcher.get_eventdispatcher().dispatch_event(
                event_name=SimulationManager.SET_UP_SIMULATION_DONE_EVENT,
                payload={}
            )

        asyncio.ensure_future(try_bake_navmesh())

    @dp.debug_func
    def load_robot_by_type(self, robot_type, randomizer):
        property_name = robot_type.lower() + "_num"

        # Validate robot count from config
        robot_count = self.get_config_file_valid_value("robot", property_name)
        if robot_count is None:
            carb.log_error(f"Robot loading failed: Invalid or missing {robot_type} count in config file.")
            return

        # Check if robots already exist in stage
        robot_count_in_stage = len(RobotUtil.get_robots_in_stage(robot_type_name=robot_type))
        if robot_count <= robot_count_in_stage:
            carb.log_info(f"{robot_type} robots already exist in stage ({robot_count_in_stage}/{robot_count}). Skipping spawn.")
            return

        # Set up agent randomizer
        all_agents_pos = AgentUtil.get_all_agents_positions()
        randomizer.update_agent_positions(all_agents_pos)

        # Get stage and paths
        stage = omni.usd.get_context().get_stage()
        parent_path = PrimPaths.robots_parent_path()
        spawn_area = self.get_config_file_valid_value("robot", "spawn_area")

        # Spawn robots
        for i in range(robot_count):
            robot_name = RobotUtil.get_robot_name_by_index(robot_type, i)
            robot_path = parent_path + "/" + robot_name
            robot_prim = stage.GetPrimAtPath(robot_path)

            if not robot_prim.IsValid():
                new_pos = randomizer.get_random_position(spawn_area)
                robot_prim = RobotUtil.spawn_robot(robot_type, new_pos, 0, robot_path)
                if robot_prim:
                    carb.log_info(f"Spawned {robot_type} robot at {robot_path}")
                else:
                    carb.log_error(f"Failed to spawn {robot_type} robot at {robot_path}")
            else:
                carb.log_info(f"{robot_type} robot already exists: {robot_path}")

            # Apply NavMesh API
            omni.kit.commands.execute("ApplyNavMeshAPICommand", prim_path=robot_path, api=NavSchema.NavMeshExcludeAPI)
            dp.print(f"Robot is spawned, type = {robot_type}, prim = {robot_path}")

    def load_robot_from_config_file(self):
        """
        Load robots from config file. Return if no load is needed.
        """
        # Validate required config values
        seed = self.get_config_file_valid_value("global", "seed")
        if not seed:
            carb.log_error("Robot loading failed: Invalid or missing seed in config file.")
            return

        # Load different robot types
        self.load_robot_by_type("Nova_Carter", self._nova_carter_randomizer)
        self.load_robot_by_type("iw_hub", self._iw_hub_randomizer)

        # Set up loaded robots
        self.setup_robot_by_type("Nova_Carter")
        self.setup_robot_by_type("iw_hub")

    def setup_robot_by_type(self, robot_type):
        """
        Set up all robots in stage (python script, semantic)
        """
        robot_prims_list = RobotUtil.get_robots_in_stage(count=-1, robot_type_name=robot_type)
        self.setup_python_scripts_to_robot(robot_prims_list, robot_type)
        SemanticsUtils.add_update_prim_metrosim_semantics(robot_prims_list, type_value="class", name=robot_type.lower())

    def load_camera_from_config_file(self):
        """
        Load to enough cameras by config file.
        Loaded camera will aim to one of the character if it is present.
        Return if no load is needed.
        """
        camera_group = self.get_config_file_property_group("sensor", "camera_group")
        if not camera_group:
            return
        cam_prop = camera_group.get_property("camera_num")
        if not cam_prop:
            return
        cam_count = cam_prop.get_value() if cam_prop.is_setup() else None
        if cam_count is None:
            # Show warning here since camera number can be optional
            carb.log_warn("Unable to load cameras due to no camera number in config file.")
            return
        if cam_count == 0:
            return
        seed = self.get_config_file_valid_value("global", "seed")
        if seed is None:
            carb.log_error("Unable to load cameras due to invalid seed in config file.")
            return
        # Make sure camera root prim exist
        stage = omni.usd.get_context().get_stage()
        parent_path = PrimPaths.cameras_parent_path()
        if not stage.GetPrimAtPath(parent_path).IsValid():
            omni.kit.commands.execute(
                "CreatePrimCommand", prim_type="Xform", prim_path=parent_path, select_new_prim=False
            )
        # Get all required camera infos from randomizer
        character_prim_list = CharacterUtil.get_characters_root_in_stage(count_invisible=False)
        character_list = [prim.GetPath() for prim in character_prim_list]
        camera_transforms = self._camera_randomizer.get_random_camera_transforms(cam_count, character_list)
        focal_lengths = self._camera_randomizer.get_random_camera_focallength_list(cam_count)
        # Make sure all required cameras exist
        for i in range(cam_count):
            cam_name = CameraUtil.get_camera_name_by_index(i)
            cam_path = f"{parent_path}/{cam_name}"
            if not stage.GetPrimAtPath(cam_path).IsValid():
                cam_prim = CameraUtil.spawn_camera(cam_path)
                pos, rot = camera_transforms[i]
                CameraUtil.set_camera(cam_prim, pos, rot, focal_lengths[i])


    def setup_anim_people_command_from_config_file(self):
        """
        Link character command file to omni.anim.people.
        """
        command_file_path = self.get_config_file_valid_value("character", "command_file")
        if command_file_path:
            target_path = FileUtil.get_absolute_path(self.config_file.file_path, command_file_path)
            carb.settings.get_settings().set(OMNI_ANIM_PEOPLE_COMMAND_PATH, target_path)
            carb.log_info(f"Character command file is set to: {command_file_path}.")
        else:
            carb.log_error(f"Unable to set up character command file: {command_file_path}.")

    def setup_incidents_from_config_file(self):
        self._incident_bridge.setup_incident_from_config(self.config_file)

    def setup_anim_people_robot_command_from_config_file(self):
        """
        Link the robot command file to IAR.
        """
        command_file_path = self.get_config_file_valid_value("robot", "command_file")
        if command_file_path:
            target_path = FileUtil.get_absolute_path(self.config_file.file_path, command_file_path)
            carb.settings.get_settings().set(ANIM_ROBOT_COMMAND_PATH, target_path)
            carb.log_info(f"Robot command file is set to: {command_file_path}.")
        else:
            carb.log_error(f"Unable to set up robot command file: {command_file_path}.")

    def load_characters_from_config_file(self):
        """
        Load characters from config file.
        Load default biped character when needed.
        """
        # Validate required config values
        seed = self.get_config_file_valid_value("global", "seed")
        if not seed:
            carb.log_error("Character loading failed: Invalid or missing seed in config file.")
            return
        character_count = self.get_config_file_valid_value("character", "num")
        if character_count is None:
            carb.log_error("Character loading failed: Invalid or missing character count in config file.")
            return
        # Make sure skeleton and animation loaded
        # Set up agent randomizer
        agents_pos = AgentUtil.get_all_agents_positions()
        self._character_randomizer.update_agent_positions(agents_pos)

        # Get stage and paths
        stage = omni.usd.get_context().get_stage()
        parent_path = PrimPaths.characters_parent_path()
        spawn_area = self.get_config_file_valid_value("character", "spawn_area")
        for i in range(character_count):
            character_name = CharacterUtil.get_character_name_by_index(i)
            character_path = f"{parent_path}/{character_name}"
            character_prim = stage.GetPrimAtPath(character_path)
            if not character_prim.IsValid():
                new_pos = self._character_randomizer.get_random_position(spawn_area)
                character_prim = self.spawn_character_by_idx(new_pos, 0, i)
                if not character_prim:
                    carb.log_error(f"Failed to spawn character {character_name}.")
                    continue
                carb.log_info(f"Spawned character {character_name} at position {new_pos}.")
            else:
                carb.log_info(f"Character already exists: {character_path}")

            # Apply NavMesh API
            omni.kit.commands.execute(
                "ApplyNavMeshAPICommand", prim_path=character_path, api=NavSchema.NavMeshExcludeAPI
            )

    def setup_all_characters(self):
        """
        Set up all characters in stage (anim graph, python script, semantic)
        """
        biped_prim = CharacterUtil.load_default_biped_to_stage()
        character_list = CharacterUtil.get_characters_in_stage()
        CharacterUtil.setup_animation_graph_to_character(
            character_list, CharacterUtil.get_anim_graph_from_character(biped_prim)
        )
        CharacterUtil.setup_python_scripts_to_character(character_list, BehaviorScriptPaths.behavior_script_path())
        SemanticsUtils.add_update_prim_metrosim_semantics(character_list, type_value="class", name="character")

    def get_character_randomizer(self) -> CharacterRandomizer:
        return self._character_randomizer
