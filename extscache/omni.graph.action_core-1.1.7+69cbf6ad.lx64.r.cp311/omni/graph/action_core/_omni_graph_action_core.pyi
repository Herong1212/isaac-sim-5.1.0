from __future__ import annotations
import omni.graph.action_core._omni_graph_action_core
import typing
import omni.core._core

__all__ = [
    "IActionGraph",
    "get_interface"
]


class IActionGraph(_IActionGraph, omni.core._core.IObject):
    """
    @brief Functions for implementing nodes which are used in ``Action Graph``.

    Nodes in ``Action Graph`` have special functionality which is not present in other graph types.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def end_latent_state(self) -> None: 
        """
        Indicate that the current execution flow should be un-blocked at the given node, if it is currently in a
        latent state. It is an error to call this function before calling startLatentState.

        warning: This should only be called from within a node compute function.

        Raises:
            RuntimeError: if not called during compute.
        """
    def get_execution_enabled(self, arg0: str) -> bool: 
        """
        Read the enabled state of an input execution attribute. An input attribute is considered enabled if it is
        connected to the upstream node that was computed immediately prior to the currently computing node.

        warning: This should only be called from within a node compute function.

        Args:
            name (string): The name of the attribute (eg. "inputs:execIn")

        Returns:
            bool: True if the given attribute is considered activated.
        """
    def get_latent_state(self) -> bool: 
        """
        Read the current latent state of the node. This state is set using start_latent_state and end_latent_state

        warning: This should only be called from within a node compute function.

        Returns:
            bool: True if the node is in a latent state.
        """
    def set_execution_enabled(self, arg0: str) -> None: 
        """
        Indicate that the given output attribute should be enabled, so that execution flow should continue
        along downstream networks.

        warning: This should only be called from within a node compute function.

        Args:
            name (string): The name of the attribute (eg. "outputs:execOut")

        Raises:
            RuntimeError: if not called during compute or the attribute is not found.
        """
    def set_execution_enabled_and_pushed(self, arg0: str) -> None: 
        """
        Indicate that the given output attribute should be enabled, and the current node should be pushed to the
        execution stack. This means that when the downstream execution flow has completed, this node will be
        popped from the execution stack and its compute function will be called again.

        warning: This should only be called from within a node compute function.

        Args:
            name (string): The name of the attribute (eg. "outputs:loopBody")

        Raises:
            RuntimeError: if not called during compute or the attribute is not found.
        """
    def start_latent_state(self) -> None: 
        """
        Indicate that the current execution flow should be blocked at the given node, and the node should be
        ticked every update of the Graph (compute function called), until it calls endLatentState.

        warning: This should only be called from within a node compute function.

        Raises:
            RuntimeError: if not called during compute, the node is already in a latent state, or the change has already been requested.
        """
    pass
class _IActionGraph(omni.core._core.IObject):
    pass
def get_interface() -> IActionGraph:
    """
    Access the IActionGraph interface. This may be more efficient than creating an instance each time it is needed.

    Returns:
        omni.graph.action.IActionGraph: The interface object
    """
