from __future__ import annotations
import omni.stageupdate._stageupdate
import typing
import carb._carb

__all__ = [
    "IStageUpdate",
    "StageUpdate",
    "StageUpdateNode",
    "acquire_stage_update_interface"
]


class IStageUpdate():
    def destroy_stage_update(self, name: str) -> bool: 
        """
        Destroys the StageUpdate with the given name if nothing references it. Does not release the default StageUpdate.

        Args:
            name of the StageUpdate.

        Returns:
            True if a StageUpdate was deleted, False otherwise. The latter happens when the StageUpdate does not exist, it is in use, or it is the default StageUpdate.
        """
    def get_stage_update(self, name: str = '') -> StageUpdate: 
        """
        Returns the StageUpdate with the given name or creates a new if it does not exist.

        Args:
            name: The name of the StageUpdate.

        Returns:
            StageUpdate object.
        """
    pass
class StageUpdate():
    def create_stage_update_node(self, display_name: str, on_attach_fn: typing.Callable[[int, float], None] = None, on_detach_fn: typing.Callable[[], None] = None, on_update_fn: typing.Callable[[float, float], None] = None, on_prim_add_fn: typing.Callable[[str], None] = None, on_prim_or_property_change_fn: typing.Callable[[str], None] = None, on_prim_remove_fn: typing.Callable[[str], None] = None, on_raycast_fn: typing.Callable[[carb._carb.Float3, carb._carb.Float3, bool], None] = None) -> StageUpdateNode: ...
    def get_stage_update_nodes(self) -> tuple: ...
    def set_stage_update_node_enabled(self, index: int, enabled: bool) -> None: 
        """
        Toggle Simulation Node enable/disable.

        Args:
            index (int): Simulation Node index in tuple, returned by `get_stage_update_nodes`.
            enabled(bool): Enable/disable toggle. 
        """
    def set_stage_update_node_order(self, index: int, order: int) -> None: 
        """
        Change Simulation Node order.

        Args:
            index (int): Simulation Node index in tuple, returned by `get_stage_update_nodes`.
            order(int): Order to sort on. 
        """
    def subscribe_to_stage_update_node_change_events(self, fn: typing.Callable[[], None]) -> carb._carb.Subscription: 
        """
        Subscribes to Simulation Node(s) change events.

        Event is triggered when nodes are added, removed, toggled.

        See :class:`.Subscription` for more information on subscribing mechanism.

        Args:
            fn: The callback to be called on change.

        Returns:
            The subscription holder.
        """
    pass
class StageUpdateNode():
    pass
def acquire_stage_update_interface(plugin_name: str = None, library_path: str = None) -> IStageUpdate:
    pass
