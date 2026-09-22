import carb
from pxr import Gf
from isaacsim.anim.robot.state_machine import StateMachine
from isaacsim.anim.robot.agent.base_agent import BaseAgent
from isaacsim.anim.robot.drive import OmniDirectionalDrive, DifferentialDrive
from omni.metropolis.utils.simulation_util import SimulationUtil


class Command:
    """
    Base class for all commands. It handles basic command execution logic and timing.

    Attributes:
        command (str): The command string.
        agent (BaseAgent): The agent that the command is executed on.
        state_machine (StateMachine): The state machine that the command is executed on.
        is_done (bool): Whether the command is done.
        time_passed (float): The time passed since the command was started.
        start_frame (float): The frame at which the command was started.
    """

    def __init__(self, command: str, agent: BaseAgent, state_machine: StateMachine) -> None:
        self.command: str = command
        self._agent: BaseAgent = agent
        self._state_machine: StateMachine = state_machine
        self.is_done: bool = False
        self.time_passed: float = 0
        self.start_frame = SimulationUtil.get_current_timecode()

    def update(self, dt):
        """
        Update the command's state and animation.

        Args:
            dt (float): The time passed since the last update.
        """
        self._state_machine.update()  # State Machine handles the animation update

    def force_quit_command(self):
        self.is_done = True
        self._state_machine.transition_to_state("idle")


class Idle(Command):
    """
    Command for the agent to idle.

    Attributes:
        duration (float): The duration of the idle command.
    """

    def __init__(self, command: str, agent: BaseAgent, state_machine: StateMachine) -> None:
        super().__init__(command=command, agent=agent, state_machine=state_machine)
        self.__duration = float(self.command[0])
        self._state_machine.set_state("idle")

    def update(self, dt):
        """
        Update the command's state and animation.

        Args:
            dt (float): The time passed since the last update.
        """
        super().update(dt)

        self.time_passed += dt
        # If the command has been active for the duration, set the command as done
        if self.time_passed >= self.__duration:
            self.is_done = True


class MoveTo(Command):
    """
    Command for the agent to move to a specific position.

    Attributes:
        target_position (list[float]): The target position of the command.
    """

    def __init__(self, command: str, agent: BaseAgent, state_machine: StateMachine) -> None:
        super().__init__(command=command, agent=agent, state_machine=state_machine)
        current_position = carb.Float3(list(self._agent.prim.GetAttribute("xformOp:translate").Get()))

        # Parse and validate coordinates
        coords_str = self.command.strip()
        if not coords_str:
            raise ValueError("Empty coordinate string provided")

        coord_parts = coords_str.split()
        if len(coord_parts) != 3:
            raise ValueError(f"Expected exactly 3 coordinates (x, y, z), got {len(coord_parts)}")

        try:
            coords = [float(coord) for coord in coord_parts]
        except ValueError as e:
            raise ValueError(f"Invalid coordinate value: {e}")

        # Check for NaN or infinity values
        for i, coord in enumerate(coords):
            if not (coord == coord):  # NaN check
                raise ValueError(f"NaN value found in coordinate {i}")
            if coord == float('inf') or coord == float('-inf'):
                raise ValueError(f"Infinity value found in coordinate {i}")

        target_position = carb.Float3(coords)


        # Register the robot to the GlobalCharacterPositionManager
        # Some lightweight test agents may not have a bbox attribute; default to radius 0.0.
        agent_bbox = getattr(self._agent, "bbox", None)
        if agent_bbox is not None:
            agent_size = agent_bbox.GetRange().GetSize()
            # Radius is half of the diagonal length of the bounding box
            radius = Gf.Vec2d(agent_size[:2]).GetLength() / 2
        else:
            radius = 0.0

        self._path = self._agent.path_planner.get_path_points(current_position, target_position, radius)
        self._path.pop(0)  # Remove the first point from the path as it is the current position

        # Different drive bases have different path planning logic
        # Currently only omni-directional drive and differential drive are supported
        self._drive_base = (
            OmniDirectionalDrive(self._agent, self._state_machine)
            if self._agent.drive_base == "omni_directional"
            else DifferentialDrive(self._agent, self._state_machine)
        )

    def update(self, dt):
        """
        Update the command's state and animation.

        Args:
            dt (float): The time passed since the last update.
        """
        super().update(dt)

        # The Drive base class handles the path planning logic
        if self._path and self._path[0]:
            self._drive_base.update(self._path, dt)
        else:
            self.is_done = True
            return
