"""
Expose the public interface for all commands that work with OmniGraph. All of the available commands are packaged
up into a single "cmds" object with any redundant "Command" suffix removed. This is how you would access any of
the OmniGraph commands:

.. code-block:: python

    import omni.graph.core as og
    og.cmds.CreateNode(graph=my_graph, node_path=my_node_path, node_type=my_node_type, create_usd=True)

You can list all available commands by inspecting the cmds object:

.. code-block:: python

    [cmd for cmd in dir(og.cmds) if not cmd.startswith("_")]
"""

from omni.kit.commands import register_all_commands_in_module as _register_commands

__all__ = ["cmds"]

from .compound_commands import ReplaceWithCompound  # noqa: F401
from .instancing_commands import ApplyOmniGraphAPICommand  # noqa: F401
from .instancing_commands import RemoveOmniGraphAPICommand  # noqa: F401

# ==============================================================================================================
# These are symbols that should technically be prefaced with an underscore because they are used internally but
# not part of the public API but that would cause a lot of refactoring work so for now they are just added to the
# module contents but not the module exports.
#   _    _ _____ _____  _____  ______ _   _
#  | |  | |_   _|  __ \|  __ \|  ____| \ | |
#  | |__| | | | | |  | | |  | | |__  |  \| |
#  |  __  | | | | |  | | |  | |  __| | . ` |
#  | |  | |_| |_| |__| | |__| | |____| |\  |
#  |_|  |_|_____|_____/|_____/|______|_| \_|
#
from .topology_commands import ChangeVariableTypeCommand  # noqa: F401
from .topology_commands import ConnectAttrsCommand  # noqa: F401
from .topology_commands import ConnectPrimCommand  # noqa: F401
from .topology_commands import CreateAttrCommand  # noqa: F401
from .topology_commands import CreateGraphAsNodeCommand  # noqa: F401
from .topology_commands import CreateNodeCommand  # noqa: F401
from .topology_commands import CreateSubgraphCommand  # noqa: F401
from .topology_commands import CreateVariableCommand  # noqa: F401
from .topology_commands import DeleteNodeCommand  # noqa: F401
from .topology_commands import DisconnectAllAttrsCommand  # noqa: F401
from .topology_commands import DisconnectAttrsCommand  # noqa: F401
from .topology_commands import DisconnectPrimCommand  # noqa: F401
from .topology_commands import RemoveAttrCommand  # noqa: F401
from .topology_commands import RemoveVariableCommand  # noqa: F401
from .topology_commands import ResolveAttrTypeCommand  # noqa: F401
from .topology_commands import _OGRestoreConnectionsOnUndo  # noqa: F401
from .value_commands import ChangePipelineStageCommand  # noqa: F401
from .value_commands import DisableGraphCommand  # noqa: F401
from .value_commands import DisableGraphUSDHandlerCommand  # noqa: F401
from .value_commands import DisableNodeCommand  # noqa: F401
from .value_commands import EnableGraphCommand  # noqa: F401
from .value_commands import EnableGraphUSDHandlerCommand  # noqa: F401
from .value_commands import EnableNodeCommand  # noqa: F401
from .value_commands import MapAttrCommand  # noqa: F401
from .value_commands import RenameNodeCommand  # noqa: F401
from .value_commands import RenameSubgraphCommand  # noqa: F401
from .value_commands import SetAttrCommand  # noqa: F401
from .value_commands import SetAttrDataCommand  # noqa: F401
from .value_commands import SetEvaluationModeCommand  # noqa: F401
from .value_commands import SetVariableTooltipCommand  # noqa: F401

# By placing this in an internal list and exporting the list the backward compatibility code can make use of it
# to allow access to the now-internal objects in a way that looks like they are still published.
_HIDDEN = [
    "_OGRestoreConnectionsOnUndo",
    "ApplyOmniGraphAPICommand",
    "ChangePipelineStageCommand",
    "ChangeVariableTypeCommand",
    "command_type_wrappers",
    "compound_commands",
    "ConnectAttrsCommand",
    "ConnectPrimCommand",
    "CreateAttrCommand",
    "CreateGraphAsNodeCommand",
    "CreateNodeCommand",
    "CreateSubgraphCommand",
    "CreateVariableCommand",
    "DeleteNodeCommand",
    "DisableGraphCommand",
    "DisableGraphUSDHandlerCommand",
    "DisableNodeCommand",
    "DisconnectAllAttrsCommand",
    "DisconnectAttrsCommand",
    "DisconnectPrimCommand",
    "EnableGraphCommand",
    "EnableGraphUSDHandlerCommand",
    "EnableNodeCommand",
    "instancing_commands",
    "RemoveAttrCommand",
    "RemoveOmniGraphAPICommand",
    "RemoveVariableCommand",
    "RenameNodeCommand",
    "RenameSubgraphCommand",
    "ReplaceWithCompound",
    "ResolveAttrTypeCommand",
    "SetAttrCommand",
    "SetAttrDataCommand",
    "SetEvaluationModeCommand",
    "SetVariableTooltipCommand",
    "topology_commands",
    "value_commands",
    "MapAttrCommand",
]

cmds = _register_commands(__name__)
