import carb
from pxr import Sdf, Usd
from omni.metropolis.utils.usd_util import USDUtil
from isaacsim.anim.robot.utils import get_translate_with_timecode, get_orient_with_timecode
from isaacsim.anim.robot.agent.base_agent import BaseAgent
from dataclasses import dataclass


@dataclass
class Animation:
    """
    A class that defines an animation.
    Attributes:
        name (str): Identifier for the animation
        root_path (str): USD path to the root of the animation data
        joint_to_animation (dict): Mapping between joint prims and their corresponding animation prims
        start_time (int): Starting frame of the animation (default: 0)
        end_time (int): Ending frame of the animation (default: 0)
        loop (bool): Whether the animation should loop when reaching the end (default: True)
    """

    name: str
    root_path: str
    # TODO: some joints can only rotate, while others can only translate. Define the type to improve the performance.
    joint_to_animation: dict[Usd.Prim, Usd.Prim]
    start_time: int = 0
    end_time: int = 0
    loop: bool = True


class State:
    """
    Represents a single state in the finite state machine for animation control.
    Each state can have its own animation and transitions to other states.
    """

    def __init__(self, name: str, animation_clip_path: str | None = None, persistent: bool = False) -> None:
        """
        Initialize a new state with a name and optional animation clip.

        Args:
            name: Unique identifier for this state
            animation_clip_path: Optional USD path to animation data
            persistent: If True, maintains joint positions when transitioning away
        """
        self.name = name
        self.persistent = persistent
        self.transitions: dict = {}

        # Animation Related
        self.animation_clip_path = animation_clip_path
        self.animation_prims_names: list[str] = []

        self.joint_to_animation: dict[Usd.Prim, Usd.Prim] = {}
        self.animation: Animation | None = None

    def add_transition(self, target_state: str, condition: callable) -> None:
        """
        Add a transition to another state with a condition.

        Args:
            target_state: Name of the state to transition to
            condition: Callable that returns bool, determines if transition is allowed
        """
        self.transitions[target_state] = condition

    def add_animation(self, agent: BaseAgent) -> None:
        """
        Configure animation data for this state by loading and mapping joint primitives.

        Args:
            agent: Robot/character agent whose joints will be animated

        Note:
            This method sets up the mapping between the agent's joints and their
            corresponding animation data in the USD stage.
        """
        if self.animation_clip_path:
            animation_root_prim = agent.stage.GetPrimAtPath(self.animation_clip_path)
            if not animation_root_prim.IsValid():
                carb.log_error(f"State '{self.name}' has no joint animation")
                return
            # Get all joint animation prims
            animation_prims = [prim for prim in animation_root_prim.GetChildren()]
            self.animation_prims_names = [prim.GetName() for prim in animation_prims]

            # Map each joint to its corresponding animation data
            for joint in agent.joint_prims:
                if joint.GetName() in self.animation_prims_names:
                    self.joint_to_animation[joint] = animation_prims[self.animation_prims_names.index(joint.GetName())]

            # Create an animation object
            self.animation = Animation(self.name, self.animation_clip_path, self.joint_to_animation)

        else:
            carb.log_error(f"State '{self.name}' has no animation clip path")

    def update_animation(
        self, root_path: str | None, start_time: int = 0, end_time: int = 0, loop: bool = True
    ) -> None:
        """
        Update the animation configuration for this state.

        Args:
            root_path: Optional new root path for the animation
            start_time: Starting frame of the animation (default: 0)
            end_time: Ending frame of the animation (default: 0)
            loop: Whether the animation should loop when reaching the end (default: True)
        """
        if root_path is None and self.animation_clip_path is None:
            carb.log_error(f"State '{self.name}' has no animation clip path")
            return

        if root_path is None:
            root_path = self.animation_clip_path

        self.animation = Animation(
            name=self.name,
            root_path=root_path,
            joint_to_animation=self.joint_to_animation,
            start_time=start_time,
            end_time=end_time,
            loop=loop,
        )

    def play(self, agent: BaseAgent, timecode: int) -> None:
        # TODO: the timecode should consider the stage timecode per second
        """
        Execute the animation for the current frame/timecode.

        Args:
            agent: Robot/character agent to animate
            timecode: Current frame number in the animation

        Note:
            Updates joint orientations and positions based on the animation data
            for the current timecode. Changes are applied within a USD change block
            for efficiency.
        """
        if self.animation:
            with Sdf.ChangeBlock(True):  # Batch USD changes for better performance
                for joint, source_prim in self.joint_to_animation.items():
                    if not USDUtil.is_a_valid_xform(source_prim):
                        carb.log_error(f"Joint '{joint.GetName()}' has no animation prim")
                        continue
                    # Get the orientation and position from the animation data
                    translate = get_translate_with_timecode(source_prim, timecode, self.animation.loop)
                    orient = get_orient_with_timecode(source_prim, timecode, self.animation.loop)
                    joint.GetAttribute("xformOp:orient").Set(orient)
                    joint.GetAttribute("xformOp:translate").Set(translate)

    def __str__(self) -> str:
        """
        Return a string representation of the state.
        Used for debugging.
        """
        result = f"State: {self.name}\n"
        result += f"  Animation clip: {self.animation_clip_path}\n"
        result += "  Transitions:\n"
        for target_state, condition in self.transitions.items():
            result += f"    {target_state}: {condition}\n"
        result += f"  Animation joints: {self.joint_to_animation.keys()}\n"
        return result

    def cleanup(self) -> None:
        """Release any resources held by the state"""
        self.joint_to_animation.clear()


class StateMachine:
    """
    A finite state machine implementation for managing animation states and transitions.
    Controls the flow between different animation states and handles state transitions
    based on defined conditions.

    The state machine maintains a collection of states and manages transitions between them,
    ensuring that animations play correctly and state changes occur only when valid
    conditions are met.

    Attributes:
        states (dict): Collection of all available states, mapped by name
        current_state (State | None): The currently active state
        current_state_frame (int): Frame counter for the current state's animation
        agent (BaseAgent): Reference to the robot/character being animated
    """

    def __init__(self, agent: BaseAgent) -> None:
        """
        Initialize the state machine for a specific agent.

        Args:
            agent: The robot/character agent whose animations will be managed
        """
        self.states: dict = {}  # Maps state names to State objects
        self.current_state: State | None = None
        self.current_state_frame = 0  # Tracks the current frame of animation
        self.agent = agent

    def is_in_state(self, state_name: str) -> bool:
        """
        Check if a specific state is currently active.

        Args:
            state_name: Name of the state to check

        Returns:
            bool: True if the specified state is currently active, False otherwise
        """
        return bool(self.current_state and self.current_state.name == state_name)

    def add_animation_to_state(
        self, state_name: str, animation_clip_path: str | None = None, loop: bool = True
    ) -> None:
        """
        Associate an animation clip with an existing state.

        Args:
            state_name: Name of the state to update
            animation_clip_path: USD path to the animation data
            loop: Whether the animation should loop when reaching the end

        Note:
            If the state doesn't exist, an error will be logged and no changes will be made
        """
        if state_name in self.states:
            self.states[state_name].animation_clip_path = animation_clip_path
            self.states[state_name].add_animation(self.agent)
        else:
            carb.log_error(f"State '{state_name}' does not exist.")

    def update_state_animation(
        self,
        state_name: str,
        animation_clip_path: str | None = None,
        start_time: int = 0,
        end_time: int = 0,
        loop: bool = True,
    ) -> None:
        """
        Update the animation configuration for an existing state.

        Args:
            state_name: Name of the state to update
            animation_clip_path: Optional new USD path for the animation
            start_time: Starting frame for the animation
            end_time: Ending frame for the animation
            loop: Whether the animation should loop

        Note:
            This allows for dynamic modification of animation parameters
            without creating a new state
        """
        if state_name in self.states:
            self.states[state_name].update_animation(animation_clip_path, start_time, end_time, loop)
        else:
            carb.log_error(f"State '{state_name}' does not exist.")

    def add_state(self, state_name: str, animation_clip: str | None = None) -> None:
        """
        Add a state to the state machine.

        Args:
            state_name: Unique identifier for the state
            animation_clip: Path to the animation clip
        """
        if state_name in self.states:
            carb.log_info(f"State '{state_name}' already exists. Will not add a new state.")
            return
        else:
            # If the state does not exist, create a new state
            state = State(state_name, animation_clip)
            self.states[state_name] = state

    def set_state(self, state_name: str) -> None:
        """
        Set the current state to the specified state.

        Args:
            state_name: Name of the state to set
        """
        if state_name in self.states:
            self.current_state = self.states[state_name]
            # Reset the current state frame
            self.current_state_frame = 0
        else:
            carb.log_error(f"State '{state_name}' does not exist.")

    def transition_to_state(self, state_name: str) -> None:
        """
        Transition to the specified state if conditions are met.

        Args:
            state_name: Name of the state to transition to
        """
        if not self.current_state:
            carb.log_error("Cannot transition: No current state")
            return

        if state_name not in self.current_state.transitions:
            carb.log_error(f"No transition defined from '{self.current_state.name}' to '{state_name}'")
            return

        condition = self.current_state.transitions[state_name]
        if condition(state_name):  # Check if transition condition is met
            self.set_state(state_name)

            # Recover the initial joint poses if the state is not persistent
            if not self.current_state.persistent:
                for joint_prim in self.current_state.joint_to_animation.keys():
                    translate, orient = self.agent.init_joint_poses[str(joint_prim.GetPrimPath())]
                    joint_prim.GetAttribute("xformOp:translate").Set(translate)
                    joint_prim.GetAttribute("xformOp:orient").Set(orient)
        else:
            carb.log_error(f"Transition condition from '{self.current_state.name}' to '{state_name}' not met")

    def update(self) -> None:
        """
        Execute a single frame update for the state machine's current animation.

        The method handles:
        - Animation playback through the current state's play() method
        - Frame counting for animation timing
        - Logging of the current state for debugging
        """
        if self.current_state:
            self.current_state.play(self.agent, self.current_state_frame)
            self.current_state_frame += 1  # Increment frame counter for next update
        else:
            carb.log_error("No current state")

    def __str__(self) -> str:
        """
        Return a string representation of the state machine.
        Used for debugging.
        """
        if not self.current_state:
            return "No current state\n"
        result = f"Current state: {self.current_state.name}\nCurrent frame: {self.current_state_frame}\n"
        for _, state in self.states.items():
            result += str(state)
        return result

    def cleanup(self) -> None:
        """Cleanup all states and resources"""
        for state in self.states.values():
            state.cleanup()
        self.states.clear()
        self.current_state = None
