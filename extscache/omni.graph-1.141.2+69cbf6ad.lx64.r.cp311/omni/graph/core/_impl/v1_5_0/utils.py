r"""Deprecated utilities

  _____   ______  _____   _____   ______  _____         _______  ______  _____
 |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
 | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
 | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
 | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
 |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/

"""

from typing import Any, List, Tuple, Union

import carb
import omni.graph.core as og
from pxr import Sdf, Usd

# Object type hints are now available in typing.py
NODE_TYPE_HINTS = Union[str, og.Node, Usd.Prim, None]  # type: ignore
NODE_TYPE_OR_LIST = Union[NODE_TYPE_HINTS, List[NODE_TYPE_HINTS]]
ATTRIBUTE_TYPE_HINTS = Union[str, og.Attribute, Usd.Attribute]  # type: ignore
ATTRIBUTE_TYPE_OR_LIST = Union[ATTRIBUTE_TYPE_HINTS, List[ATTRIBUTE_TYPE_HINTS]]
ATTRIBUTE_TYPE_TYPE_HINTS = Union[str, og.Type]
ATTRIBUTE_VALUE_PAIR = Tuple[ATTRIBUTE_TYPE_HINTS, Any]
ATTRIBUTE_VALUE_PAIRS = Union[ATTRIBUTE_VALUE_PAIR, List[ATTRIBUTE_VALUE_PAIR]]
EXTENDED_ATTRIBUTE_TYPE_HINTS = Union[og.AttributePortType, Tuple[og.AttributePortType, Union[str, List[str]]]]
GRAPH_TYPE_HINTS = Union[str, Sdf.Path, og.Graph, None]  # type: ignore
GRAPH_TYPE_OR_LIST = Union[GRAPH_TYPE_HINTS, List[GRAPH_TYPE_HINTS]]


# ================================================================================
def get_omnigraph():
    """Returns the current OmniGraph.
    Deprecated as there is no longer the notion of a 'current' graph
    """
    carb.log_warn("get_omnigraph() is deprecated and will be removed - use og.ObjectLookup.graph() instead")

    for context in og.get_compute_graph_contexts():
        return context.get_graph()

    raise ValueError("OmniGraph is not currently available")


# ====================================================================================================
def l10n(msg):
    """Wrapper for l10n for when it gets implemented.
    Deprecated - implementation is not on the plan and usage is spotty.
    """
    return msg
