from isaacsim.anim.robot.command import Command
from isaacsim.anim.robot.state_machine import StateMachine
from dataclasses import dataclass, field
from pxr import Gf
from typing import List
import os
import omni.kit.app
import carb
from omni.metropolis.utils.isaac_sim_util import get_isaac_sim_asset_root_path
from isaacsim.storage.native import get_assets_root_path
from isaacsim.anim.robot.agent.base_agent import BaseAgent
from isaacsim.anim.robot.agent.agent_controller import AgentController
from isaacsim.anim.robot.path_planner import NavMeshPathPlanner, PathPlanner

# Path to the iw_hub joints animation clips
# TODO: Cache the extension path
EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("isaacsim.anim.robot")
TURN_RIGHT_ANIM_PATH = os.path.join(EXT_PATH, "data/iw_hub/turn_right")
TURN_LEFT_ANIM_PATH = os.path.join(EXT_PATH, "data/iw_hub/turn_left")
FORWARD_ANIM_PATH = os.path.join(EXT_PATH, "data/iw_hub/forward")
LIFT_UP_ANIM_PATH = os.path.join(EXT_PATH, "data/iw_hub/lift_up")
LIFT_DOWN_ANIM_PATH = os.path.join(EXT_PATH, "data/iw_hub/lift_down")


@dataclass
class IwHub(BaseAgent):
    """
    iw_hub agent is based on the Isaac Sim iw_hub asset.
    It has 6 joints that can be animated.
    Wheels and caster swivels are attached to the chassis, and the caster wheels are attached to the caster swivels.
    """

    agent_name: str = "iw_hub"
    linear_velocity: float = 0.5
    forward_vec: Gf.Vec3d = Gf.Vec3d(1, 0, 0)
    angular_velocity: float = 30.0
    joints: List[str] = field(
        default_factory=lambda: [
            "/chassis/lift",
            "/chassis/left_wheel",
            "/chassis/right_wheel",
            "/chassis/left_swivel/left_caster",
            "/chassis/right_swivel/right_caster",
            "/chassis/left_swivel",
            "/chassis/right_swivel",
        ]
    )
    path_planner: PathPlanner = field(default_factory=NavMeshPathPlanner)
    drive_base: str = "differential"
    animation_paths: dict[str, str] = field(
        default_factory=lambda: {
            "turn_left": TURN_LEFT_ANIM_PATH,
            "turn_right": TURN_RIGHT_ANIM_PATH,
            "forward": FORWARD_ANIM_PATH,
            "lift_up": LIFT_UP_ANIM_PATH,
            "lift_down": LIFT_DOWN_ANIM_PATH,
        }
    )
    asset_path: str = field(default_factory=lambda: _get_iw_hub_asset_path())

    # Children class won't automatically call the parent class's __post_init__() method
    # So we need to call it manually
    def __post_init__(self):
        super().__post_init__()
        # Add more states and transitions
        self.states.extend(["lift_up", "lift_down"])
        self.transitions["idle"].extend(["lift_up", "lift_down"])
        self.transitions["lift_up"] = ["idle"]
        self.transitions["lift_down"] = ["idle"]


def _get_iw_hub_asset_path() -> str:
    """
    Get the iw_hub asset path with proper error handling.
    
    Returns:
        str: The asset path for the iw_hub USD file.
        
    Raises:
        RuntimeError: If Isaac Sim asset root path is not available.
    """
    isaac_sim_root = get_isaac_sim_asset_root_path()
    if isaac_sim_root is None:
        carb.log_warn("Failed to get Isaac Sim asset root path directly from the setting. Use fallback from isaacsim.storage.native. ")
        return f"{get_assets_root_path()}/Isaac/Samples/AnimRobot/iw_hub.usd"
    return f"{isaac_sim_root}/Isaac/Samples/AnimRobot/iw_hub.usd"


# Custom Command classes
class LiftUp(Command):
    # TODO:There should be a command class that just play an animation and this can just inherit from it
    def __init__(self, command: str, agent: BaseAgent, state_machine: StateMachine) -> None:
        super().__init__(command=command, agent=agent, state_machine=state_machine)
        self._state_machine.set_state("lift_up")

    def update(self, dt):
        super().update(dt)

        self.time_passed += dt
        if self.time_passed >= 1.0:
            self.is_done = True
            self._state_machine.transition_to_state("idle")


class LiftDown(Command):
    def __init__(self, command: str, agent: BaseAgent, state_machine: StateMachine) -> None:
        super().__init__(command=command, agent=agent, state_machine=state_machine)
        self._state_machine.set_state("lift_down")

    def update(self, dt):
        super().update(dt)

        self.time_passed += dt
        if self.time_passed >= 1.0:
            self.is_done = True
            self._state_machine.transition_to_state("idle")


# Custom Controller class
class IwHubController(AgentController):
    def on_init(self):
        # Set up the agent to control
        super().on_init(agent=IwHub(prim=self.prim))

        # Update animation parameters if needed
        self.state_machine.update_state_animation("lift_up", loop=False)
        self.state_machine.update_state_animation("lift_down", loop=False)

        # Load the agent specific command class
        self.command_to_class_inst["LiftUp"] = LiftUp
        self.command_to_class_inst["LiftDown"] = LiftDown
