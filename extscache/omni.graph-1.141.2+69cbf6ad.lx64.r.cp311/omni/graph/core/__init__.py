"""
This file contains the interfaces that external Python scripts can use.
Import this file and use the APIs exposed below.

To get documentation on this module and methods import this file into a Python interpreter and run dir/help, like this:

.. code-block:: python

    import omni.graph.core as og
    help(og.get_graph_by_path)
"""

# fmt: off
# isort: off
import omni.core  # noqa: F401 (Required for proper resolution of ONI wrappers)
from omni.graph.tools import deprecated_constant_object as _deprecated_type  # For internal use

# Get the bindings into the module
from . import _omni_graph_core  # noqa: F401,PLW0406
from ._omni_graph_core import *

from ._impl.extension import _PublicExtension  # noqa: F401

from ._impl.attribute_types import get_port_type_namespace
from ._impl.attribute_values import AttributeDataValueHelper
from ._impl.attribute_values import AttributeValueHelper
from ._impl.attribute_values import WrappedArrayType
from ._impl.autonode import create_node_type, developer_mode_active, NodeTypeConstructionError, RUNTIME_MODULE_NAME
from ._impl.bundles import Bundle
from ._impl.bundles import BundleContainer
from ._impl.bundles import BundleContents
from ._impl.bundles import BundleChanges
from ._impl.bundles import BundleWriteBlock
from ._impl.commands import cmds
from ._impl.controller import Controller
from ._impl.data_wrapper import data_shape_from_type
from ._impl.data_wrapper import DataWrapper
from ._impl.data_wrapper import Device
from ._impl.data_view import DataView
from ._impl.database import Database
from ._impl.database import DynamicAttributeAccess
from ._impl.database import DynamicAttributeInterface
from ._impl.database import PerNodeKeys
from ._impl.dtypes import Dtype
from ._impl.errors import OmniGraphAttributeError
from ._impl.errors import OmniGraphError
from ._impl.errors import OmniGraphTypeError
from ._impl.errors import OmniGraphValueError
from ._impl.errors import ReadOnlyError
from ._impl.extension_information import ExtensionInformation
from ._impl.graph_controller import GraphController
from ._impl.inspection import OmniGraphInspector
from ._impl.node_controller import NodeController
from ._impl.object_lookup import ObjectLookup
from ._impl.runtime import RuntimeAttribute
from ._impl.settings import Settings
from ._impl.threadsafety_test_utils import ThreadsafetyTestUtils
from ._impl.traversal import traverse_downstream_graph
from ._impl.traversal import traverse_upstream_graph
from ._impl.type_resolution import resolve_base_coupled
from ._impl.type_resolution import resolve_fully_coupled
from ._impl.utils import attribute_value_as_usd
from ._impl.utils import get_graph_settings
from ._impl.utils import get_kit_version
from ._impl.utils import GraphSettings
from ._impl.utils import in_compute
from ._impl.utils import is_attribute_plain_data
from ._impl.utils import is_in_compute
from ._impl.utils import python_value_as_usd
from ._impl.utils import TypedValue

from . import typing
from . import _unstable

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
from ._impl.generate_ogn import generate_ogn_from_node
from ._impl.registration import PythonNodeRegistration
from ._impl.utils import load_example_file
from ._impl.utils import remove_attributes_if
from ._impl.utils import sync_to_usd

# ==============================================================================================================
# Soft-deprecated imports. Kept around for backward compatibility for one version.
#   _____   ______  _____   _____   ______  _____         _______  ______  _____
#  |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
#  | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
#  | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
#  | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
#  |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
#
from omni.graph.tools import RenamedClass as __RenamedClass  # pylint: disable=wrong-import-order
from omni.graph.tools.ogn import MetadataKeys as __MetadataKeys  # pylint: disable=wrong-import-order
MetadataKeys = __RenamedClass(__MetadataKeys, "MetadataKeys", "MetadataKeys has moved to omni.graph.tools.ogn")


# Ready for deletion, once omni.graph.window has removed its usage - OM-96121
def get_global_container_graphs() -> list[_omni_graph_core.Graph]:
    import carb
    carb.log_warn("get_global_container_graphs() has been deprecated - use get_global_orchestration_graphs() instead")
    return _omni_graph_core.get_global_orchestration_graphs()


# ==============================================================================================================
# The bindings may have internal (single-underscore prefix) and external symbols. To be consistent with our export
# rules the internal symbols will be part of the module but not part of the published __all__ list, and the external
# symbols will be in both.
__bindings = []
for __bound_name in dir(_omni_graph_core):
    # TODO: Right now the bindings and the core both define the same object type so they both can't be exported
    #       here so remove it from the bindings and it will be dealt with later.
    if __bound_name in ["Bundle"]:
        continue
    if not __bound_name.startswith("__"):
        if not __bound_name.startswith("_"):
            __bindings.append(__bound_name)
        globals()[__bound_name] = getattr(_omni_graph_core, __bound_name)

__all__ = __bindings + [
    "attribute_value_as_usd",
    "AttributeDataValueHelper",
    "AttributeValueHelper",
    "Bundle",
    "BundleChanges",
    "BundleContainer",
    "BundleContents",
    "BundleWriteBlock",
    "cmds",
    "Controller",
    "create_node_type",
    "data_shape_from_type",
    "Database",
    "DataView",
    "DataWrapper",
    "developer_mode_active",
    "Device",
    "Dtype",
    "DynamicAttributeAccess",
    "DynamicAttributeInterface",
    "ExtensionInformation",
    "get_graph_settings",
    "get_kit_version",
    "get_port_type_namespace",
    "GraphController",
    "GraphSettings",
    "in_compute",
    "is_attribute_plain_data",
    "is_in_compute",
    "MetadataKeys",
    "NodeController",
    "NodeTypeConstructionError",
    "ObjectLookup",
    "OmniGraphAttributeError",
    "OmniGraphError",
    "OmniGraphInspector",
    "OmniGraphTypeError",
    "OmniGraphValueError",
    "PerNodeKeys",
    "python_value_as_usd",
    "ReadOnlyError",
    "resolve_base_coupled",
    "resolve_fully_coupled",
    "RuntimeAttribute",
    "RUNTIME_MODULE_NAME",
    "Settings",
    "ThreadsafetyTestUtils",
    "traverse_downstream_graph",
    "traverse_upstream_graph",
    "TypedValue",
    "typing",
    "WrappedArrayType",
]

_HIDDEN = [
    "generate_ogn_from_node",
    "get_global_container_graphs",
    "PythonNodeRegistration",
    "load_example_file",
    "remove_attributes_if",
    "sync_to_usd",
]

# isort: on
# fmt: on
