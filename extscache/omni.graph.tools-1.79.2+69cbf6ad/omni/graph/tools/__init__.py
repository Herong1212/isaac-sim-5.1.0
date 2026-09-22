"""Tools that support all of OmniGraph in general, and the .ogn format in particular.

General tools can be imported directly with the top level import:

.. code-block:: python

    import omni.graph.tools as ogt
    help(ogt.deprecated_function)

This module also supports a submodule just for the .ogn handling.

.. code-block:: python

    # Support for the parsing and creation of the .ogn format
    import omni.graph.tools.ogn as ogn
"""

from . import ogn
from ._impl.debugging import destroy_property, function_trace
from ._impl.deprecate import (
    DeprecatedClass,
    DeprecatedDictConstant,
    DeprecatedImport,
    DeprecatedStringConstant,
    DeprecateMessage,
    DeprecationError,
    DeprecationLevel,
    RenamedClass,
    deprecated_constant_object,
    deprecated_function,
)
from ._impl.extension import _PublicExtension  # noqa: F401
from ._impl.node_generator.attributes.naming import make_nice_name
from ._impl.node_generator.utils import IndentedOutput, shorten_string_lines_to
from ._impl.repo_tools.generate_node_metadata import build_directory_metadata, get_node_type_names_from_metadata

# ==============================================================================================================

__all__ = [
    "build_directory_metadata",
    "dbg",
    "dbg_eval",
    "dbg_gc",
    "dbg_ui",
    "deprecated_constant_object",
    "deprecated_function",
    "DeprecatedClass",
    "DeprecatedDictConstant",
    "DeprecatedImport",
    "DeprecatedStringConstant",
    "DeprecateMessage",
    "DeprecationError",
    "DeprecationLevel",
    "destroy_property",
    "function_trace",
    "get_node_type_names_from_metadata",
    "import_tests_in_directory",
    "IndentedOutput",
    "make_nice_name",
    "OGN_DEBUG",
    "RenamedClass",
    "shorten_string_lines_to",
    "supported_attribute_type_names",
]

# ==============================================================================================================
# Soft-deprecated imports. Kept around for backward compatibility for one version.
#   _____   ______  _____   _____   ______  _____         _______  ______  _____
#  |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
#  | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
#  | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
#  | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
#  |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
#
from ._impl.debugging import OGN_DEBUG, dbg, dbg_eval, dbg_gc, dbg_ui
from ._impl.node_generator.attributes.management import supported_attribute_type_names as _moved_to_ogn
from ._impl.node_generator.generate_test_imports import import_tests_in_directory


@deprecated_function("supported_attribute_type_names() has moved to omni.graph.tools.ogn")
def supported_attribute_type_names(*args, **kwargs):
    return _moved_to_ogn(*args, **kwargs)
