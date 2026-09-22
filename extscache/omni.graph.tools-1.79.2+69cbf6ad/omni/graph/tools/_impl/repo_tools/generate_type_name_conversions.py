"""Repo tool wrapper for the OmniGraph type name conversion generator.

This can be run at build time or at runtime to create a JSON data file containing the mapping between the .ogn
representation of a type name and other known representations.

When run at build time or offline the path to the extension's root is passed in and the directories are scanned
for .ogn files and those definitions are added to the metadata.

    > repo og_create_type_name_conversions
      --output-file C:/Metadata/DataTypeNameConversions.json

Uses the node generator definitions to create the conversion information so that there is always that single
source of truth. Extra information added at runtime will be handled in some other way if necessary.

The file it creates consists of a dictionary where there is a single entry named "LEGEND", which itself is a dictionary
indicating the type of data that will appear as keys and values in the rest of the dictionary. Here is an example of
a single entry:

.. code-block:: json

    {
        "LEGEND": {
            "OGN TYPE": [
                "USD TYPE",
                "SDF TYPE",
                "C++ TYPE",
                "PYTHON TYPE",
                "PYTHON TYPE ANNOTATION"
            ]
        },
        "bool": [
            "bool",
            "Sdf.ValueTypeNames.Bool",
            "ogn::SimpleInput",
            "bool",
            "omni.graph.core.types.Bool"
        ]
    }

This indicates that if you see a type named "bool" in a .ogn file then it will appear as the type "bool" in a .usda
file, which is equivalent to the Python Sdf type named Sdf.ValueTypeNames.Bool, and can be annotated in a Python
function as (bool_type: omni.graph.core.types.Bool). Generated code in C++ nodes will return wrappers of type
ogn::SimpleInput and in Python nodes it will be a simple bool value.
"""

import argparse
import json
import logging
import os
from pathlib import Path

from ..node_generator.attributes.management import ATTRIBUTE_MANAGERS
from ..node_generator.attributes.UnionAttributeManager import UnionAttributeManager
from ..node_generator.keys import MemoryTypeValues
from ..node_generator.utils import ParseError, ensure_writable_directory, rst_table

# --------------------------------------------------------------------------------------------------------------
logger = logging.getLogger("OgCreateTypeNameConversions")
LOG_LEVELS = "DEBUG|INFO|WARN|ERROR|CRITICAL"


# ==============================================================================================================
def setup_repo_tool(parser: argparse.ArgumentParser, config: dict[str, any]):
    """Required function that integrates the tool with repo_man"""

    parser.prog = "omnigraph_type_name_conversions"
    parser.description = __doc__
    parser.formatter_class = argparse.RawTextHelpFormatter

    # This helps format the usage information in a nicer way
    os.putenv("COLUMNS", "120")

    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        help="File to receive the generated JSON description",
        metavar="DATA_CONVERSIONS.json",
    )
    parser.add_argument(
        "-m",
        "--docs-module",
        type=str,
        help="Output file for the generated documentation for the Python omni.graph.core.types module",
        metavar="TYPE_DOCS.rst",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="WARN",
        metavar=LOG_LEVELS,
        help="Flag to enable debug output of the steps being taken during node type generation",
    )

    # --------------------------------------------------------------------------------------------------------------
    def _update_type_conversion_data(output_file: str):
        """Generates the type conversion data and writes it to the file if it has changed.
        Args:
            output_file: Path to the file where the data will live. Not written if it already contained data that
            is the same as what was generated.
        """
        output_path = Path(output_file)
        ensure_writable_directory(output_path.parent)
        try:
            logger.debug("Checking for currently existing attribute type conversion data")
            with open(output_path, "r", encoding="utf-8") as output_fd:
                current_output = json.load(output_fd)
                logger.debug("--> Found existing data as %s", json.dumps(current_output, indent=2))
        except (IOError, json.decoder.JSONDecodeError):
            logger.debug("--> No current data")
            current_output = {}

        new_output = {
            "LEGEND": {"OGN TYPE": ["USD TYPE", "SDF TYPE", "C++ TYPE", "PYTHON TYPE", "PYTHON TYPE ANNOTATION"]}
        }
        for base_type_name, attribute_manager_type in ATTRIBUTE_MANAGERS.items():
            # USD no longer supports the transformX attribute types so filter them out, and OmniGraph is phasing out
            # the path type so filter it out too
            if base_type_name.startswith("transform") or base_type_name == "path":
                continue
            if (
                attribute_manager_type == UnionAttributeManager
                or attribute_manager_type in UnionAttributeManager.__subclasses__()
            ):
                logger.debug("...skipping dataless type %s", type(attribute_manager_type))
                continue
            for tuple_count in attribute_manager_type.tuples_supported():
                for array_depth in attribute_manager_type.array_depths_supported():
                    manager = attribute_manager_type("inputs:Ghost", base_type_name)
                    manager.array_depth = array_depth
                    manager.tuple_count = tuple_count
                    logger.debug("...creating conversion for %s", manager.ogn_type())
                    try:
                        usd_type_name = manager.usd_type_name()
                    except ParseError:
                        usd_type_name = None
                    try:
                        sdf_type_name = manager.sdf_type_name()
                        sdf_type_name = None if sdf_type_name is None else f"Sdf.ValueTypeNames.{sdf_type_name}"
                    except ParseError:  # pragma: no cover (types should be validated already in the build)
                        sdf_type_name = None
                    try:
                        manager.memory_type = MemoryTypeValues.CPU
                        cpp_type_name = manager.cpp_wrapper_class()[0]
                    except ParseError:  # pragma: no cover (types should be validated already in the build)
                        cpp_type_name = None
                    try:
                        python_type_name = manager.python_type_name()
                    except ParseError:  # pragma: no cover (types should be validated already in the build)
                        python_type_name = None
                    try:
                        python_type_annotation = manager.python_type_annotation()
                    except ParseError:  # pragma: no cover (types should be validated already in the build)
                        python_type_annotation = None
                    new_output[manager.ogn_type()] = [
                        usd_type_name,
                        sdf_type_name,
                        cpp_type_name,
                        python_type_name,
                        python_type_annotation,
                    ]

        if current_output != new_output:
            logger.debug("Writing new attribute conversion output as %s", json.dumps(new_output, indent=2))
            with open(output_path, "w", encoding="utf-8") as output_fd:
                json.dump(new_output, output_fd, indent=4)
        else:
            logger.debug("No changes to the conversion data - not writing the file.")

    # --------------------------------------------------------------------------------------------------------------
    def _update_types_documentation(output_file: str):
        """Generates the documentation for type definitions in the omni.graph.core.types module and writes it to the
        file if it has changed.
        Args:
            output_file: Path to the file where the documentation will live. Not written if it already contained data
            that is the same as what was generated.
        """
        output_path = Path(output_file)
        ensure_writable_directory(output_path.parent)
        try:
            logger.debug("Checking for currently existing attribute type module documentation")
            with open(output_path, "r", encoding="utf-8") as output_fd:
                current_output = "".join(output_fd.readlines())
                logger.debug("--> Found existing data as %s", current_output)
        except IOError:
            logger.debug("--> No current data")
            current_output = []

        # Start with the header line - a restructuredText table will be generated using this
        conversion_data = [[".ogn Type Definition", "Type annotation", "Python Data Type"]]
        for base_type_name in sorted(ATTRIBUTE_MANAGERS):
            # USD no longer supports the transformX attribute types so filter them out
            if base_type_name.startswith("transform"):
                logger.debug("...skipping deprecated transform type")
                continue

            if base_type_name == "union":
                logger.debug("...skipping dataless union type")
                continue

            attribute_manager_type = ATTRIBUTE_MANAGERS[base_type_name]
            for tuple_count in attribute_manager_type.tuples_supported():
                for array_depth in attribute_manager_type.array_depths_supported():
                    manager = attribute_manager_type("inputs:Ghost", base_type_name)
                    manager.array_depth = array_depth
                    manager.tuple_count = tuple_count
                    logger.debug("...creating conversion for %s", manager.ogn_type())
                    conversion_data.append(
                        [
                            f"*{manager.ogn_type()}*",
                            manager.python_type_annotation(),
                            manager.python_type_name(),
                        ]
                    )

        new_output = rst_table(conversion_data)

        if current_output != new_output:
            logger.debug("Writing new attribute conversion output as %s", new_output)
            with open(output_path, "w", encoding="utf-8") as output_fd:
                output_fd.writelines(new_output)
        else:
            logger.debug("No changes to the type module documentation - not writing the file.")

    # --------------------------------------------------------------------------------------------------------------
    def run_repo_tool(options: argparse.Namespace, config: dict[str, any]):
        """Function that actually does the work after everything has been collected for it

        Args:
            options: Parsed option values

        Raises:
            ValueError: If any of the options are inconsistent with the others
        """
        numeric_level = getattr(logging, options.log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: '{options.log_level}' not in {LOG_LEVELS}")
        logger.setLevel(numeric_level)
        if numeric_level < logging.INFO:
            for option_name, option_value in vars(options).items():
                if option_name != "merged_tool_config":  # Long-winded and not generally useful, even for debugging
                    logger.debug("%s = %s", option_name, option_value)

        _update_type_conversion_data(options.output_file)
        _update_types_documentation(options.docs_module)

    return run_repo_tool


# ==============================================================================================================
def generate_type_name_conversions(arg_list: list[str] = None):
    """Wrapper around the tool that can be called directly from a script or indirectly from a test
    Args:
        arg_list: sys.argv style command-line arguments to the tool
    """
    _cmd_line_parser = argparse.ArgumentParser()
    _cmd_line_runner = setup_repo_tool(_cmd_line_parser, {})  # noqa: PLE1120
    _cmd_line_options = _cmd_line_parser.parse_args(arg_list)
    _cmd_line_runner(_cmd_line_options, {})  # noqa: PLE1120


# ==============================================================================================================
# Support for calling the tool directly rather than through repo_man
if __name__ == "__main__":  # pragma: no cover
    generate_type_name_conversions()
