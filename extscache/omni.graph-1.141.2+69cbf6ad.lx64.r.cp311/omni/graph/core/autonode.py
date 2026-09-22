r"""Deprecated access to AutoNode - see omni.graph.core.create_node_type for the replacement.

  _____   ______  _____   _____   ______  _____         _______  ______  _____
 |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
 | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
 | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
 | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
 |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/

"""

from omni.graph.tools import DeprecatedImport as _DeprecatedImport  # noqa: wrong-import-order

from ._impl.autonode_deprecated.autonode import (
    AutoClass,
    AutoFunc,
    register_autonode_type_extension,
    unregister_autonode_type_extension,
)
from ._impl.autonode_deprecated.data_typing import TypeConversion as AutoNodeTypeConversion
from ._impl.autonode_deprecated.event import IEventStream
from ._impl.autonode_deprecated.type_definitions import AutoNodeDefinitionGenerator, AutoNodeDefinitionWrapper

_DeprecatedImport(
    "AutoNode features are now part of the main omni.graph.core module."
    " See help(omni.graph.core.create_node_type) for more details"
)

__all__ = [
    "AutoClass",
    "AutoFunc",
    "AutoNodeDefinitionGenerator",
    "AutoNodeDefinitionWrapper",
    "AutoNodeTypeConversion",
    "IEventStream",
    "register_autonode_type_extension",
    "unregister_autonode_type_extension",
]
