# =============================================================================================================================
# This submodule is work-in-progress and subject to change without notice
#  _    _  _____ ______         _______  __     ______  _    _ _____     ______          ___   _   _____  _____  _____ _  __
# | |  | |/ ____|  ____|     /\|__   __| \ \   / / __ \| |  | |  __ \   / __ \ \        / / \ | | |  __ \|_   _|/ ____| |/ /
# | |  | | (___ | |__       /  \  | |     \ \_/ / |  | | |  | | |__) | | |  | \ \  /\  / /|  \| | | |__) | | | | (___ | ' /
# | |  | |\___ \|  __|     / /\ \ | |      \   /| |  | | |  | |  _  /  | |  | |\ \/  \/ / | . ` | |  _  /  | |  \___ \|  <
# | |__| |____) | |____   / ____ \| |       | | | |__| | |__| | | \ \  | |__| | \  /\  /  | |\  | | | \ \ _| |_ ____) | . \
#  \____/|_____/|______| /_/    \_\_|       |_|  \____/ \____/|_|  \_\  \____/   \/  \/   |_| \_| |_|  \_\_____|_____/|_|\_|

from . import _omni_graph_core as __cpp_bindings
from ._impl.unstable.commands import cmds  # noqa: F401
from ._impl.unstable.subgraph_compound_commands import (  # noqa: F401
    validate_attribute_for_promotion_from_compound_subgraph,
    validate_nodes_for_compound_subgraph,
)

#  Import the c++ bindings from the _unstable submodule.
__bindings = []
for __bound_name in dir(__cpp_bindings._og_unstable):  # noqa PLW0212
    if not __bound_name.startswith("__"):
        if not __bound_name.startswith("_"):
            __bindings.append(__bound_name)
        globals()[__bound_name] = getattr(__cpp_bindings._og_unstable, __bound_name)  # noqa PLW0212


# For backward compatibility these are exposed here even though they were moved to the main namespace as part of
# exposing a stable interface.
INodeTypeForwarding = __cpp_bindings.INodeTypeForwarding
get_node_type_forwarding_interface = __cpp_bindings.get_node_type_forwarding_interface


__all__ = __bindings + [
    "cmds",
    "get_node_type_forwarding_interface",
    "INodeTypeForwarding",
    "validate_attribute_for_promotion_from_compound_subgraph",
    "validate_nodes_for_compound_subgraph",
]
