from dataclasses import dataclass, field
from pxr import Gf
from typing import List
import omni.kit.app
import os
import carb
from isaacsim.anim.robot.agent.base_agent import BaseAgent
from isaacsim.anim.robot.agent.agent_controller import AgentController
from isaacsim.anim.robot.path_planner import NavMeshPathPlanner, PathPlanner
from omni.metropolis.utils.isaac_sim_util import get_isaac_sim_asset_root_path
from isaacsim.storage.native import get_assets_root_path

# Path to the Nova Carter joints animation clips
# TODO: Cache the extension path
EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("isaacsim.anim.robot")
TURN_RIGHT_ANIM_PATH = os.path.join(EXT_PATH, "data/nova_carter/turn_right")
TURN_LEFT_ANIM_PATH = os.path.join(EXT_PATH, "data/nova_carter/turn_left")
FORWARD_ANIM_PATH = os.path.join(EXT_PATH, "data/nova_carter/forward")


@dataclass
class NovaCarter(BaseAgent):
    """
    Nova Carter agent is based on the Isaac Sim Nova Carter asset.
    It has 6 joints that can be animated.
    Wheels and caster swivels are attached to the chassis, and the caster wheels are attached to the caster swivels.
    """

    agent_name: str = "Nova Carter"
    linear_velocity: float = 0.5
    forward_vec: Gf.Vec3d = Gf.Vec3d(1, 0, 0)
    angular_velocity: float = 30.0
    joints: List[str] = field(
        default_factory=lambda: [
            "/chassis_link/wheel_right",
            "/chassis_link/wheel_left",
            "/chassis_link/caster_swivel_left",
            "/chassis_link/caster_swivel_right",
            "/chassis_link/caster_swivel_left/caster_wheel_left",
            "/chassis_link/caster_swivel_right/caster_wheel_right",
        ]
    )
    drive_base: str = "differential"
    path_planner: PathPlanner = field(default_factory=NavMeshPathPlanner)
    animation_paths: dict[str, str] = field(
        default_factory=lambda: {
            "turn_left": TURN_LEFT_ANIM_PATH,
            "turn_right": TURN_RIGHT_ANIM_PATH,
            "forward": FORWARD_ANIM_PATH,
        }
    )
    asset_path: str = field(default_factory=lambda: _get_nova_carter_asset_path())

    # Children class won't automatically call the parent class's __post_init__() method
    # So we need to call it manually
    def __post_init__(self):
        super().__post_init__()
        # Add more states and transitions


def _get_nova_carter_asset_path() -> str:
    """
    Get the Nova Carter asset path with proper error handling.
    
    Returns:
        str: The asset path for the Nova Carter USD file.
        
    Raises:
        RuntimeError: If Isaac Sim asset root path is not available.
    """
    isaac_sim_root = get_isaac_sim_asset_root_path()
    if isaac_sim_root is None:
        carb.log_warn("Failed to get Isaac Sim asset root path directly from the setting. Use fallback from isaacsim.storage.native. ")
        return f"{get_assets_root_path()}/Isaac/Samples/AnimRobot/nova_carter.usd"
    return f"{isaac_sim_root}/Isaac/Samples/AnimRobot/nova_carter.usd"


# Custom Command classes


# Custom Controller class
class NovaCarterController(AgentController):
    def on_init(self):
        # Set up the agent to control
        super().on_init(agent=NovaCarter(prim=self.prim))

        # Update animation parameters if needed

        # Load the agent specific command class
