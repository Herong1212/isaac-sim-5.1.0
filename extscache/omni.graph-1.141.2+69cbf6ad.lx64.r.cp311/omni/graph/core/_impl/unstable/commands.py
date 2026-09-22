from omni.kit.commands import register_all_commands_in_module as _register_commands

from .compound_commands import (  # noqa: F401
    CreateCompoundNodeTypeCommand,
    CreateCompoundNodeTypeInput,
    CreateCompoundNodeTypeOutput,
    RemoveCompoundNodeTypeInput,
    RemoveCompoundNodeTypeOutput,
)
from .subgraph_compound_commands import (  # noqa: F401
    CreateCompoundSubgraphCommand,
    CreateCompoundSubgraphInputCommand,
    CreateCompoundSubgraphOutputCommand,
    PromoteUnconnectedToCompoundSubgraphCommand,
    RemoveCompoundSubgraphAttributeCommand,
    RenameCompoundSubgraphAttributeCommand,
    RenameCompoundSubgraphCommand,
    ReplaceWithCompoundSubgraphCommand,
)

__all__ = ["cmds"]

cmds = _register_commands(__name__)
