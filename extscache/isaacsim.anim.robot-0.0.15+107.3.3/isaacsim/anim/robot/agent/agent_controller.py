import gc

import carb
import omni
import omni.client
from isaacsim.anim.robot.command import Idle, MoveTo
from isaacsim.anim.robot.settings import CommandSettings, SimulationSettings
from isaacsim.anim.robot.state_machine import StateMachine
from omni.anim.people.scripts.global_character_position_manager import GlobalCharacterPositionManager
from omni.anim.people.settings import AgentEvent
from omni.kit.scripting import BehaviorScript
from omni.metropolis.utils.file_util import TextFileUtil
from omni.metropolis.utils.math_util import MathUtil
from omni.metropolis.utils.usd_util import USDUtil
from pxr import Gf, Sdf, UsdGeom

from .base_agent import BaseAgent


class AgentController(BehaviorScript):
    """
    The base animation controller class for managing agent behaviors.
    This class is responsible for managing the state machine, animations, and command execution for the agent.
    """

    def on_init(self, agent: BaseAgent | None = None):
        """
        This function is called when the script is attached to the prim in the stage.

        Args:
            agent (BaseAgent): The agent dataclass to be managed by the controller.
        """
        self._name = str(self.prim_path).split("/")[-1]  # name to be used in a command file
        if agent is None:
            self.agent: BaseAgent = BaseAgent(prim=self.prim)
        else:
            self.agent: BaseAgent = agent

        # Initialize the commands
        self.current_command = None
        self._command_file_path = carb.settings.get_settings().get(CommandSettings.command_file_path)
        self.commands: list[str] = []

        # Initialize state machine configuration
        self.state_machine: StateMachine = StateMachine(self.agent)
        self.__setup_state_machine()
        self.state_machine.set_state("idle")
        self.__setup_animations()

        # Map commands to class
        self.command_to_class_inst = {"Idle": Idle}
        self.command_to_class_inst["GoTo"] = MoveTo

        # Communication with IRA and OAP
        # Publish the robot position for collision avoidance
        self._agent_position_manager = GlobalCharacterPositionManager.get_instance()

        # Register the robot to the IRA AgentManager
        self._dynamic_avoidance = carb.settings.get_settings().get(SimulationSettings.dynamic_avoidance)

    def on_destroy(self):
        """
        This function is called when the script is dettached from the prim in the stage or when the prim is deleted.
        """
        self.state_machine.cleanup()
        gc.collect()

    def on_play(self):
        """
        This function is called when the simulation starts.
        """
        # Settings needs to be setup before play
        self.__setup_settings()
        # Store the translation and orient before play
        self._init_translate, self._init_orient = USDUtil.get_prim_pos_and_rot_as_quat(self.prim)
        # Load the commands
        self.commands = self.read_commands_from_file(self._command_file_path)
        # Register the robot to the IRA AgentManager
        command_info = {"agent_name": self._name, "prim_path": str(self.prim_path)}
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=AgentEvent.AgentRegistered,
            payload=command_info,
        )

        if self._dynamic_avoidance:
            # Register the robot to the GlobalCharacterPositionManager
            agent_size = self.agent.bbox.GetRange().GetSize()
            # Radius is the diagonal length of the bounding box
            radius = Gf.Vec2d(agent_size[:2]).GetLength() / 2
            self._agent_position_manager.set_character_radius(str(self.prim_path), radius)
            self.__publish_robot_position(0)

    def on_stop(self):
        """
        This function is called when the simulation stops.
        """
        # Recover initial pose
        self.prim.GetAttribute("xformOp:translate").Set(self._init_translate)
        self.prim.GetAttribute("xformOp:orient").Set(self._init_orient)
        # Recover initial joint poses
        for joint_prim_path, (translate, orient) in self.agent.init_joint_poses.items():
            self.stage.GetPrimAtPath(joint_prim_path).GetAttribute("xformOp:translate").Set(translate)
            self.stage.GetPrimAtPath(joint_prim_path).GetAttribute("xformOp:orient").Set(orient)

        # Reset state
        self.commands = []
        self.current_command = None
        self.state_machine.set_state("idle")

    def on_update(self, current_time: float, delta_time: float):
        """
        This function is called every frame.

        Args:
            current_time (float): The current time in the simulation.
            delta_time (float): The time since the last frame.
        """
        if self._dynamic_avoidance:
            self.__publish_robot_position(delta_time)

        # Handle command completion
        if self.current_command:
            if self.current_command.is_done:
                self.current_command = None
            else:
                self.current_command.update(delta_time)
                return

        # Process next command if available
        if self.commands:
            command_str = self.commands.pop(0)  # Remove and get first command
            command_class, *args = command_str.split(maxsplit=1)  # More efficient splitting
            command_args = args[0] if args else ""

            try:
                command_constructor = self.command_to_class_inst[command_class]
                self.current_command = command_constructor(
                    command=command_args, agent=self.agent, state_machine=self.state_machine
                )
            except KeyError:
                carb.log_error(f"Unknown command class: {command_class}")
            except Exception as e:
                carb.log_error(f"Error creating command {command_class}: {e}")

    def __setup_state_machine(self) -> None:
        """Configure the state machine with states and transitions."""
        for state in self.agent.states:
            self.state_machine.add_state(state)

        for from_state, to_states in self.agent.transitions.items():
            for to_state in to_states:
                self.state_machine.states[from_state].add_transition(to_state, lambda x, state=to_state: x == state)

    def __setup_animations(self) -> None:
        """Setup the animations for the state machine."""
        carb.log_info(f"setting up animations for {self.agent.agent_name}")
        for state, path in self.agent.animation_paths.items():
            carb.log_info(f"setting up animation for state {state}, path: {path}")
            animation_path = self.prim_path.AppendPath(state)
            root_prim = UsdGeom.Xform.Define(self.stage, animation_path).GetPrim()
            result, list_entries = omni.client.list(path)
            if result != omni.client.Result.OK:
                carb.log_error("LOADING " + path + " FAILED!")
                return

            for list_entry in list_entries:
                try:
                    prim_path = Sdf.Path(f"{str(root_prim.GetPath())}/{list_entry.relative_path.split('.')[0]}")
                    usd_file_path = f"{path}/{list_entry.relative_path}"
                    prim_spec = Sdf.CreatePrimInLayer(self.stage.GetRootLayer(), prim_path)
                    prim_spec.specifier = Sdf.SpecifierDef

                    if omni.client.is_local_url(usd_file_path) and not omni.client.is_local_url(
                        self.stage.GetRootLayer().identifier
                    ):
                        usd_file_path = omni.client.normalize_url(omni.client.make_file_url_if_possible(usd_file_path))

                    prim_spec.payloadList.Prepend(Sdf.Payload(usd_file_path))
                except Exception as e:
                    carb.log_error(f"Failed to load animation {list_entry.relative_path}: {e}")

            self.state_machine.add_animation_to_state(state, animation_path)

    def __setup_settings(self) -> None:
        """Setup the settings for the agent."""
        self._dynamic_avoidance = carb.settings.get_settings().get(SimulationSettings.dynamic_avoidance)
        self._command_file_path = carb.settings.get_settings().get(CommandSettings.command_file_path)

    def __publish_robot_position(self, delta_time):
        """
        Publish the robot position for collision avoidance.
        """
        gf_pos, gf_orient = USDUtil.get_prim_pos_and_rot_as_quat(self.prim)
        self._agent_position_manager.set_character_current_pos(str(self.prim_path), carb.Float3(gf_pos))
        if self.state_machine.is_in_state("forward"):
            forward_vec = MathUtil.rotate_and_normalize_vector(Gf.Rotation(gf_orient), self.agent.forward_vec)
            future_pos = carb.Float3(gf_pos + forward_vec * self.agent.linear_velocity * delta_time)
            self._agent_position_manager.set_character_future_pos(str(self.prim_path), future_pos)
        else:
            self._agent_position_manager.set_character_future_pos(str(self.prim_path), carb.Float3(gf_pos))

    def read_commands_from_file(self, file_path):
        """
        Read the agent commands from the file.

        Args:
            file_path (str): The path to the file containing the commands.

        Returns:
            list[str]: The list of commands.
            This list contains the commands only for this agent and will not have the agent name.
        """
        content = TextFileUtil.read_text_file(file_path).splitlines()
        if content is None:
            return []

        return [" ".join(line.split(" ")[1:]) for line in content if line.strip().split(" ")[0] == self.prim.GetName()]

    # inject commands to robot's command list
    def inject_command(self, command_list, executeImmediately=False):
        cmd_array = [
            " ".join(command_line.split(" ")[1:])
            for command_line in command_list
            if command_line.strip().split(" ")[0] == self.prim.GetName()
        ]
        # TODO: first original command will be discarded
        self.commands[0:0] = cmd_array

    def get_agent_name(self):
        return self._name

    # force the agent to end current command
    def end_current_command(self):
        if self.current_command is not None:
            self.current_command.force_quit_command()

    # get robot's position
    def get_current_position(self):
        return carb.Float3(USDUtil.get_prim_pos(self.prim))
