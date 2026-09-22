"""pybind11 carb.physics.stageupdate bindings"""
from __future__ import annotations
import omni.physics.stageupdate.bindings._physicsStageUpdateNode
import typing

__all__ = [
    "IPhysicsStageUpdateNode",
    "acquire_physics_stage_update_node_interface",
    "release_physics_stage_update_node_interface",
    "release_physics_stage_update_node_scripting"
]


class IPhysicsStageUpdateNode():
    def attach_node(self) -> None: 
        """
        Attach the Physics StageUpdateNode to IStageUpdate
        """
    def block_timeline_events(self, arg0: bool) -> None: 
        """
        Blocks time line events (play, resume, stop)
        """
    def detach_node(self) -> None: 
        """
        Detach the Physics StageUpdateNode to IStageUpdate
        """
    def is_node_attached(self) -> bool: 
        """
        Check if StageUpdateNode is attached to IStageUpdate

        Returns:
            bool: True if attached.
        """
    def timeline_events_blocked(self) -> bool: 
        """
        Check if time line events (play, resume, stop) are blocked

        Returns:
            bool: True if blocked.
        """
    pass
def acquire_physics_stage_update_node_interface(plugin_name: str = None, library_path: str = None) -> IPhysicsStageUpdateNode:
    pass
def release_physics_stage_update_node_interface(arg0: IPhysicsStageUpdateNode) -> None:
    pass
def release_physics_stage_update_node_scripting(arg0: IPhysicsStageUpdateNode) -> None:
    pass
