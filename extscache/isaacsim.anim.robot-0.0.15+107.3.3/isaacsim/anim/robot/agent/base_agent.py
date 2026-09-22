from dataclasses import dataclass, field
from pxr import Sdf, Usd, Gf, UsdGeom
from typing import List
from isaacsim.anim.robot.path_planner import PathPlanner
import carb
import omni.client


@dataclass
class BaseAgent:
    """
    Base class for all agents.
    All agents should inherit from this class and override the __post_init__() method.

    Args:
        prim: the USD prim of the agent.
        agent_name: the name of the agent.
        linear_velocity: the linear velocity of the agent. Unit is m/s.
        angular_velocity: the angular velocity of the agent. Unit is deg/s.
        forward_vec: the forward vector of the agent.
        joints: the joints that can be animated for the agent.
        prim_path: the path of the prim of the agent.
        stage: the USD stage of the agent.
        joint_prims: the USD prims of the joints of the agent.
        init_joint_poses: the initial poses of the joints of the agent.
        drive_base: the drive base of the agent.
        states: the states of the agent.
        transitions: the state transition graph of the agent.
        animation_paths: the paths to the animation files. It's a map from joint name to animation file path.
        bbox: the bounding box of the agent.
        asset_path: the path to the asset of the agent. If this is set, the asset will be loaded automatically.
    """

    prim: Usd.Prim
    agent_name: str = "Base Agent"
    linear_velocity: float = 1.0
    angular_velocity: float = 45.0
    forward_vec: Gf.Vec3d = Gf.Vec3d(1, 0, 0)
    joints: List[str] = field(default_factory=list)
    prim_path: Sdf.Path = field(init=False)
    stage: Usd.Stage = field(init=False)
    joint_prims: List[Usd.Prim] = field(default_factory=list, init=False)
    init_joint_poses: dict[str, tuple[Gf.Vec3d, Gf.Quatd]] = field(default_factory=dict, init=False)
    drive_base: str = "omni_directional"
    path_planner: PathPlanner = field(default_factory=PathPlanner)
    states = ["idle", "turn_left", "turn_right", "forward"]
    transitions = {
        "idle": ["turn_left", "turn_right", "idle", "forward"],
        "turn_left": ["forward"],
        "turn_right": ["forward"],
        "forward": ["turn_left", "turn_right", "idle"],
    }
    animation_paths: dict[str, str] = field(default_factory=lambda: {})
    bbox: Gf.BBox3d = field(default_factory=Gf.BBox3d, init=False)
    asset_path: str = field(default_factory=str, init=False)

    def __post_init__(self) -> None:
        """
        Initialize the agent after dataclass initialization.
        Validates the prim, sets up the USD path and stage, records the joint prims and initial joint poses.
        """
        # Validate whether the prim is valid and active
        if not self.prim.IsValid():
            carb.log_error("Non-valid prim for agent " + self.agent_name)
            return
        if not self.prim.IsActive():
            carb.log_error("Non-active prim for agent " + self.agent_name)
            return

        # prim_path and stage can be inferred from the prim
        self.prim_path = self.prim.GetPath()
        self.stage = self.prim.GetStage()

        # Automatically load the asset if the asset path is provided
        if self.asset_path and self.asset_path != "":
            # handles local path and Omniverse path
            if omni.client.is_local_url(self.asset_path) and not omni.client.is_local_url(self.stage.GetRootLayer().identifier):
                self.asset_path = omni.client.normalize_url(omni.client.make_file_url_if_possible(self.asset_path))

            # Only add reference if the asset is not already referenced
            if self.prim.GetMetadata("references") is not None:
                references = [ref.GetAssetPath() for ref in self.prim.GetMetadata("references").GetAddedOrExplicitItems()]
                if self.asset_path not in references:
                    self.prim.GetReferences().AddReference(self.asset_path)
            else:
                self.prim.GetReferences().AddReference(self.asset_path)

        # Automatically get all the joint prims of the agent and record their initial poses
        # Initial poses will be used to reset the joint poses when the simulation stops
        self.joint_prims = [self.stage.GetPrimAtPath(str(self.prim_path) + joint) for joint in self.joints]
        for joint_prim in self.joint_prims:
            self.init_joint_poses[str(joint_prim.GetPrimPath())] = (
                joint_prim.GetAttribute("xformOp:translate").Get(),
                joint_prim.GetAttribute("xformOp:orient").Get(),
            )

        # Get the bbox of the agent
        self.bbox = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"]).ComputeLocalBound(self.prim)
