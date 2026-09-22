"""Tools that support interacting with the .ogn format, including parsing and creation.

General tools can be imported directly with the top level import:

.. code-block:: python

    import omni.graph.tools.ogn as ogn
    help(ogn)
"""

from ._impl.node_generator.attributes.AttributeManager import AttributeManager
from ._impl.node_generator.attributes.management import (
    ALL_ATTRIBUTE_TYPES,
    ATTRIBUTE_UNION_GROUPS,
    expand_attribute_union_groups,
    get_attribute_manager,
    get_attribute_manager_type,
    split_attribute_type_name,
    supported_attribute_type_names,
)
from ._impl.node_generator.code_generation import code_generation
from ._impl.node_generator.generate_cpp import generate_cpp
from ._impl.node_generator.generate_documentation import generate_documentation
from ._impl.node_generator.generate_python import generate_python
from ._impl.node_generator.generate_template import generate_template
from ._impl.node_generator.generate_test_imports import generate_test_imports
from ._impl.node_generator.generate_tests import generate_tests
from ._impl.node_generator.generate_usd import generate_usd
from ._impl.node_generator.keys import (
    AttributeKeys,
    CategoryTypeValues,
    CudaPointerValues,
    ExclusionTypeValues,
    GraphSetupKeys,
    IconKeys,
    LanguageTypeValues,
    MemoryTypeValues,
    MetadataKeys,
    NodeTypeKeys,
    TestKeys,
)
from ._impl.node_generator.nodes import NodeGenerationError
from ._impl.node_generator.parse_scheduling import SchedulingHints
from ._impl.node_generator.utils import (
    CarbLogError,
    DebugError,
    ParseError,
    UnimplementedError,
    to_cpp_comment,
    to_python_comment,
    to_usd_comment,
    to_usd_docs,
)
from ._impl.type_name_conversions import DataTypeError, DataTypeNameRepresentation, convert_type_name

__all__ = [
    "ALL_ATTRIBUTE_TYPES",
    "ATTRIBUTE_UNION_GROUPS",
    "AttributeKeys",
    "AttributeManager",
    "CarbLogError",
    "CategoryTypeValues",
    "code_generation",
    "convert_type_name",
    "CudaPointerValues",
    "DataTypeError",
    "DataTypeNameRepresentation",
    "DebugError",
    "ExclusionTypeValues",
    "expand_attribute_union_groups",
    "generate_cpp",
    "generate_documentation",
    "generate_python",
    "generate_template",
    "generate_test_imports",
    "generate_tests",
    "generate_usd",
    "get_attribute_manager_type",
    "get_attribute_manager",
    "GraphSetupKeys",
    "IconKeys",
    "LanguageTypeValues",
    "MemoryTypeValues",
    "MetadataKeys",
    "NodeGenerationError",
    "NodeTypeKeys",
    "ParseError",
    "SchedulingHints",
    "split_attribute_type_name",
    "supported_attribute_type_names",
    "TestKeys",
    "to_cpp_comment",
    "to_python_comment",
    "to_usd_comment",
    "to_usd_docs",
    "UnimplementedError",
]

# AutoNode functionality is not generally available yet
from ._impl.autonode_generator.registry import FunctionRegistry  # noqa: F401

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
from ._impl.node_generator.attributes.management import validate_attribute_type_name  # noqa: F401
from ._impl.node_generator.attributes.naming import ATTR_NAME_REQUIREMENT  # noqa: F401
from ._impl.node_generator.attributes.naming import ATTR_UI_NAME_REQUIREMENT  # noqa: F401
from ._impl.node_generator.attributes.naming import INPUT_GROUP  # noqa: F401
from ._impl.node_generator.attributes.naming import INPUT_NS  # noqa: F401
from ._impl.node_generator.attributes.naming import OUTPUT_GROUP  # noqa: F401
from ._impl.node_generator.attributes.naming import OUTPUT_NS  # noqa: F401
from ._impl.node_generator.attributes.naming import STATE_GROUP  # noqa: F401
from ._impl.node_generator.attributes.naming import STATE_NS  # noqa: F401
from ._impl.node_generator.attributes.naming import assemble_attribute_type_name  # noqa: F401
from ._impl.node_generator.attributes.naming import attribute_name_as_python_property  # noqa: F401
from ._impl.node_generator.attributes.naming import attribute_name_in_namespace  # noqa: F401
from ._impl.node_generator.attributes.naming import attribute_name_without_port  # noqa: F401
from ._impl.node_generator.attributes.naming import check_attribute_name  # noqa: F401
from ._impl.node_generator.attributes.naming import check_attribute_ui_name  # noqa: F401
from ._impl.node_generator.attributes.naming import is_input_name  # noqa: F401
from ._impl.node_generator.attributes.naming import is_output_name  # noqa: F401
from ._impl.node_generator.attributes.naming import is_state_name  # noqa: F401
from ._impl.node_generator.attributes.naming import namespace_of_group  # noqa: F401
from ._impl.node_generator.attributes.NumericAttributeManager import NumericAttributeManager  # noqa: F401
from ._impl.node_generator.attributes.parsing import attributes_as_usd  # noqa: F401
from ._impl.node_generator.attributes.parsing import separate_ogn_role_and_type  # noqa: F401
from ._impl.node_generator.attributes.parsing import usd_type_name  # noqa: F401
from ._impl.node_generator.generate_test_imports import import_file_contents  # noqa: F401
from ._impl.node_generator.nodes import NODE_NAME_REQUIREMENT  # noqa: F401
from ._impl.node_generator.nodes import NODE_UI_NAME_REQUIREMENT  # noqa: F401
from ._impl.node_generator.nodes import NodeInterface  # noqa: F401
from ._impl.node_generator.nodes import NodeInterfaceWrapper  # noqa: F401
from ._impl.node_generator.nodes import check_node_language  # noqa: F401
from ._impl.node_generator.nodes import check_node_name  # noqa: F401
from ._impl.node_generator.nodes import check_node_ui_name  # noqa: F401
from ._impl.node_generator.OmniGraphExtension import OmniGraphExtension  # noqa: F401
from ._impl.node_generator.utils import _EXTENDED_TYPE_ANY as EXTENDED_TYPE_ANY  # noqa: F401
from ._impl.node_generator.utils import _EXTENDED_TYPE_REGULAR as EXTENDED_TYPE_REGULAR  # noqa: F401
from ._impl.node_generator.utils import _EXTENDED_TYPE_UNION as EXTENDED_TYPE_UNION  # noqa: F401
from ._impl.node_generator.utils import OGN_PARSE_DEBUG  # noqa: F401
from ._impl.node_generator.utils import GeneratorConfiguration  # noqa: F401
from ._impl.node_generator.utils import check_memory_type  # noqa: F401

# By placing this in an internal list and exporting the list the backward compatibility code can make use of it
# to allow access to the now-internal objects in a way that looks like they are still published.
_HIDDEN = [
    "assemble_attribute_type_name",
    "ATTR_NAME_REQUIREMENT",
    "ATTR_UI_NAME_REQUIREMENT",
    "attribute_name_as_python_property",
    "attribute_name_in_namespace",
    "attribute_name_without_port",
    "attributes_as_usd",
    "check_attribute_name",
    "check_attribute_ui_name",
    "check_memory_type",
    "check_node_language",
    "check_node_name",
    "check_node_ui_name",
    "EXTENDED_TYPE_ANY",
    "EXTENDED_TYPE_REGULAR",
    "EXTENDED_TYPE_UNION",
    "FunctionRegistry",
    "GeneratorConfiguration",
    "import_file_contents",
    "INPUT_GROUP",
    "INPUT_NS",
    "is_input_name",
    "is_output_name",
    "is_state_name",
    "namespace_of_group",
    "NODE_NAME_REQUIREMENT",
    "NODE_UI_NAME_REQUIREMENT",
    "NodeInterface",
    "NodeInterfaceWrapper",
    "NumericAttributeManager",
    "OGN_PARSE_DEBUG",
    "ogn_to_sdf",
    "OmniGraphExtension",
    "OUTPUT_GROUP",
    "OUTPUT_NS",
    "sdf_to_ogn",
    "separate_ogn_role_and_type",
    "STATE_GROUP",
    "STATE_NS",
    "usd_type_name",
    "validate_attribute_type_name",
]

# ==============================================================================================================
#   _____   ______  _____   _____   ______  _____         _______  ______  _____
#  |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
#  | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
#  | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
#  | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
#  |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
#
# Although we have a zero-deprecation policy these are exports that we are no longer actively developing and
# only passively supporting. Most will issue a deprecation warning if used.
from ._impl.deprecated.ogn_sdf import ogn_to_sdf, sdf_to_ogn  # noqa: E402,F401 - want deprecated imports together
