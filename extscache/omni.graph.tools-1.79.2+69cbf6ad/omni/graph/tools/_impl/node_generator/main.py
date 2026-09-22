# noqa: E501,PLW1203
"""Generate code and documentation for an OmniGraph Node description file.

Takes a JSON file containing information describing the configuration of an OmniGraph node and generates
a header file implementing a simplified interface to the graph ABI.

Run this script with the arg "--help" to see available functions in this form, followed by the current list
of supported attribute types:

usage: generate_node.py [-h] [-cd DIR] [-c [DIR]] [-d [DIR]]
                        [-e EXTENSION_NAME] [-i [DIR]]
                        [-in [INTERMEDIATE_DIRECTORY]]
                        [-m [PYTHON_IMPORT_MODULE]] [-n [FILE.ogn]] [-p [DIR]] [-pd]
                        [-s SETTING_NAME] [-t [DIR]] [-td FILE.json]
                        [-tp [DIR]] [-usd [DIR]] [-uw [DIR]] [-v]

Parse a node interface description file and generate code or documentation

optional arguments:
  -h, --help            show this help message and exit
  -cd DIR, --configDirectory DIR
                        the directory containing the code generator configuration files (default is current)
  -c [DIR], --cpp [DIR]
                        generate the C++ interface class into the specified directory (default is current)
  -d [DIR], --docs [DIR]
                        generate the node documentation into the specified directory (default is current)
  -e EXTENSION_NAME, --extension EXTENSION_NAME
                        name of the extension requesting the generation
  -i [DIR], --icons [DIR]
                        Directory into which to install the icon, if one is found
  -in [INTERMEDIATE_DIRECTORY], --intermediate [INTERMEDIATE_DIRECTORY]
                        Directory into which temporary build information is stored
  -m [PYTHON_IMPORT_MODULE], --module [PYTHON_IMPORT_MODULE]
                        Python module where the Python node files live
  -n [FILE.ogn], --nodeFile [FILE.ogn]
                        File containing the node description (use stdin if file name is omitted)
  -p [DIR], --python [DIR]
                        Generate the Python interface class into the specified directory (default is current)
  -pd, --pedantic
                        be more strict in what is accepted as valid syntax and semantics
  -s SETTING_NAME, --settings SETTING_NAME
                Define one or more build-specific settings that can be used to change the generated code at runtime
  -t [DIR], --tests [DIR]
                        Generate a file containing basic operational tests for this node
  -td FILE.json, --typeDefinitions FILE.json
                        File name containing the mapping to use from OGN type names to generated code types
  -tp [DIR], --template [DIR]
                Generate an annotated template for the C++ node class into the specified directory (default is current)
  -usd [DIR], --usdPath [DIR]
                        Generate a file containing a USD template for nodes of this type
  -uw [DIR], --unwritable [DIR]
                        Mark the generated directory as unwritable at runtime
  -v, --verbose         Output the steps the script is performing as it performs them
"""
import argparse
import logging
import os
import re
import sys
from pathlib import Path

from .attributes.management import formatted_supported_attribute_type_names
from .category_definitions import get_category_definitions
from .generate_cpp import generate_cpp
from .generate_documentation import generate_documentation
from .generate_icon import generate_icon
from .generate_python import generate_python
from .generate_template import generate_template
from .generate_tests import generate_tests
from .generate_usd import generate_usd
from .keys import LanguageTypeValues
from .nodes import NodeInterfaceWrapper
from .type_definitions import apply_type_definitions
from .utils import UNWRITABLE_TAG_FILE, GeneratorConfiguration, ParseError, Settings, ensure_writable_directory, logger

__all__ = ["main"]


# ======================================================================
def construct_parser() -> argparse.ArgumentParser:
    """Construct and return the parser for the script arguments"""

    class ReadableDir(argparse.Action):
        """Helper class for the parser to check for a readable directory"""

        def __call__(self, parser, namespace, values, option_string=None):
            """Function called by the arg parser to verify that a directory exists and is readable

            Args:
                parser: argparser required argument, ignored
                namespace: argparser required argument, ignored
                values: The path to the directory being checked for writability
                option_string: argparser required argument, ignored

            Raises:
                argparse.ArgumentTypeError if the requested directory cannot be found or created in readable mode
            """
            prospective_dir = values
            try:
                # If the directory can't be read then listdir will raise an exception
                if os.listdir(prospective_dir):
                    setattr(namespace, self.dest, prospective_dir)
            except Exception as error:
                raise argparse.ArgumentTypeError(str(error))

    class WritableDir(argparse.Action):
        """Helper class for the parser to check for a writable directory"""

        def __call__(self, parser, namespace, values, option_string=None):
            """Function called by the arg parser to verify that a directory exists and is writable

            Args:
                parser: argparser required argument, ignored
                namespace: argparser required argument, ignored
                values: The path to the directory being checked for writability. None is passed unchecked.
                option_string: argparser required argument, ignored

            Raises:
                argparse.ArgumentTypeError if the requested directory cannot be found or created in writable mode
            """
            prospective_dir = values
            try:
                if prospective_dir is not None:
                    ensure_writable_directory(prospective_dir)
                    if not Path(prospective_dir).is_dir():
                        raise IOError(f"Could not create {prospective_dir}")
                setattr(namespace, self.dest, prospective_dir)
            except Exception as error:
                raise argparse.ArgumentTypeError(str(error))

    # If no output directory is specified generated files will end up in the current directory
    default_output_dir = os.path.realpath(os.getcwd())

    # This helps format the usage information in a nicer way
    os.putenv("COLUMNS", "120")

    # Generate a message enumerating the set of attribute types currently supported
    available_attribute_types = formatted_supported_attribute_type_names()
    formatted_types = "\n\t".join(available_attribute_types)
    epilog = "Available attribute types:\n\t" + formatted_types
    available_settings = Settings().all()
    if available_settings:
        epilog += "\nAvailable settings:\n\t" + "\n\t".join(
            [f"{name}: {description}" for name, (_, description) in available_settings.items()]
        )

    # Construct the parsing information. Run the script with "--help" to see the usage.
    parser = argparse.ArgumentParser(
        description="Parse a node interface description file and generate code or documentation",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )
    parser.add_argument(
        "-cd",
        "--configDirectory",
        action=ReadableDir,
        const=default_output_dir,
        metavar="DIR",
        help="the directory containing the code generator configuration files (default is current)",
    )
    parser.add_argument(
        "-c",
        "--cpp",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="generate the C++ interface class into the specified directory (default is current)",
    )
    parser.add_argument(
        "-d",
        "--docs",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="generate the node documentation into the specified directory (default is current)",
    )
    parser.add_argument(
        "-e",
        "--extension",
        action="store",
        metavar="EXTENSION_NAME",
        default=None,
        help="name of the extension requesting the generation",
    )
    # Notice how, unlike other directory names, this one is not a "WritableDir" as the directory should only
    # be created if the node happens to have an icon, which isn't discovered until parse time.
    parser.add_argument(
        "-i",
        "--icons",
        action="store",
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="Directory into which to install the icon, if one is found",
    )
    parser.add_argument(
        "-in",
        "--intermediate",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="INTERMEDIATE_DIRECTORY",
        help="Directory into which temporary build information is stored",
    )
    parser.add_argument(
        "-m",
        "--module",
        nargs="?",
        action="store",
        metavar="PYTHON_IMPORT_MODULE",
        help="Python module where the Python node files live",
    )
    parser.add_argument(
        "-n",
        "--nodeFile",
        nargs="?",
        type=argparse.FileType("r"),
        const=sys.stdin,
        help="File containing the node description (use stdin if file name is omitted)",
        metavar="FILE.ogn",
    )
    parser.add_argument(
        "-p",
        "--python",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="Generate the Python interface class into the specified directory (default is current)",
    )
    parser.add_argument(
        "-pd", "--pedantic", action="store_true", help="Output the steps the script is performing as it performs them"
    )
    parser.add_argument(
        "-s",
        "--settings",
        type=str,
        action="append",
        metavar="SETTING_NAME",
        help="Define one or more build-specific settings that can be used to change the generated code at runtime",
    )
    parser.add_argument(
        "-t",
        "--tests",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="Generate a file containing basic operational tests for this node",
    )
    parser.add_argument(
        "-td",
        "--typeDefinitions",
        action="store",
        default=None,
        help="File name containing the mapping to use from OGN type names to generated code types",
        metavar="FILE.json",
    )
    parser.add_argument(
        "-toc",
        "--tableOfContents",
        action=WritableDir,
        nargs="?",
        const=None,
        metavar="DIR",
        help="(deprecated - does nothing)",
    )
    parser.add_argument(
        "-tp",
        "--template",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="Generate an annotated template for the C++ node class into the specified directory (default is current)",
    )
    parser.add_argument(
        "-usd",
        "--usdPath",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="Generate a file containing a USD template for nodes of this type",
    )
    parser.add_argument(
        "-uw",
        "--unwritable",
        action=WritableDir,
        nargs="?",
        const=default_output_dir,
        metavar="DIR",
        help="Mark the generated directory as unwritable at runtime",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Output the steps the script is performing as it performs them"
    )
    return parser


# ======================================================================
def main(args_to_parse: list[str] = None):
    """Parse the contents of the argument list and perform the requested function. Uses sys.argv if None."""

    parser = construct_parser()
    args = parser.parse_args(args_to_parse)

    # If the script steps are to be echoed enable the logger and dump the script arguments as a first step
    logger.setLevel(logging.DEBUG if args.verbose else logging.WARN)
    logger.info("cpp             = %s", args.cpp)
    logger.info("configDirectory = %s", args.configDirectory)
    logger.info("template        = %s", args.template)
    logger.info("docs            = %s", args.docs)
    logger.info("extension       = %s", args.extension)
    logger.info("icons           = %s", args.icons)
    logger.info("intermediate    = %s", args.intermediate)
    logger.info("module          = %s", args.module)
    logger.info("nodeFile        = %s", args.nodeFile)
    logger.info("python          = %s", args.python)
    logger.info("pedantic        = %s", args.pedantic)
    logger.info("settings        = %s", args.settings)
    logger.info("tests           = %s", args.tests)
    logger.info("toc             = %s", args.tableOfContents)
    logger.info("typeDefinitions = %s", args.typeDefinitions)
    logger.info("unwritable      = %s", args.unwritable)
    logger.info("usdPath         = %s", args.usdPath)
    logger.info("verbose         = %s", args.verbose)

    # Create the settings object from the list of settings specified on the command line.
    # Every setting keyword is assumed to be a boolean, set to true when it is passed in.
    settings = Settings()
    if args.settings is not None:
        for setting in args.settings:
            try:
                setattr(settings, setting, True)
            except AttributeError as error:
                raise ParseError(f"{setting} is not in the known settings list [{settings}]") from error

    # If there is a node to parse then do so
    node_interface_wrapper = None
    if not args.nodeFile:
        if args.docs or args.cpp or args.template or args.python or args.tests:
            logger.error("Cannot generate code unless you specify a nodeFile")
        return

    try:
        # Read in the standard set of category definitions if it can be found
        categories_allowed = {}
        if args.configDirectory is not None:
            config_dir_type_path = Path(args.configDirectory, "CategoryConfiguration.json")
            if config_dir_type_path.is_file():
                categories_allowed = get_category_definitions(config_dir_type_path)

        base_name, node_ext = os.path.splitext(os.path.basename(args.nodeFile.name))
        if node_ext != ".ogn":
            logger.error("Node files must have the .ogn extension")
            return

        if (args.python or args.docs or args.tests) and not args.module:
            logger.error("When generating Python code or documentation you must include the 'module' argument")
            return

        node_interface_wrapper = NodeInterfaceWrapper(
            args.nodeFile,
            extension=args.extension,
            config_directory=args.configDirectory,
            categories_allowed=categories_allowed,
            pedantic=args.pedantic,
        )
        logger.info("Parsed interface for %s", node_interface_wrapper.node_interface.name)

        # Applying the type definitions make them take immediate effect, which means adding/modifying members of
        # the AttributeManager class hierarchy.
        if args.typeDefinitions is not None:
            type_definition_path = Path(args.typeDefinitions)
            if type_definition_path.is_file():
                apply_type_definitions(type_definition_path)
            elif not type_definition_path.is_absolute():
                config_dir_type_path = Path(args.configDirectory, args.typeDefinitions)
                if config_dir_type_path.is_file():
                    apply_type_definitions(config_dir_type_path)
                else:
                    raise ParseError(
                        f"Type definitions '{args.typeDefinitions}' not found in"
                        f" config directory '{args.configDirectory}'"
                    )
            else:
                raise ParseError(f"Absolute type definition path '{args.typeDefinitions}' not found")

        # Sanity check to see if there is a Python file of the same name as the .ogn file but the language was
        # not specified as Python.
        if node_interface_wrapper.node_interface.language != LanguageTypeValues.PYTHON:
            python_file_name = args.nodeFile.name.replace(".ogn", ".py")
            if os.path.isfile(python_file_name):
                raise ParseError(f"Python node file {python_file_name} exists but language was not set to Python")

        # If there is no generation happening then emit a message indicating the success of the parse.
        # (Failure of the parse would have already been indicated by a ParseError exception)
        if not args.docs and not args.cpp and not args.python:
            print(f"Node file {args.nodeFile.name} successfully validated")

        configuration = GeneratorConfiguration(
            args.nodeFile.name,
            node_interface_wrapper.node_interface,
            args.extension,
            args.module,
            base_name,
            None,
            args.verbose,
            settings,
        )

        # The node interface may have an override on the path - get rid of it if the icon isn't being generated
        configuration.destination_directory = args.icons
        icon_path = generate_icon(configuration) if args.icons else None
        if icon_path is not None:
            # Find the icon path relative to the extension directory as that is where the metadata lookup will start
            match = re.match(f".*/{args.extension}/(.*)", icon_path.replace("\\", "/"))
            if not match:
                raise ParseError(f"Icon location '{icon_path}' needs to appear under extension '{args.extension}'")
            node_interface_wrapper.node_interface.icon_path = match.group(1)
        else:
            node_interface_wrapper.node_interface.icon_path = None

        configuration.destination_directory = args.docs
        _ = generate_documentation(configuration) if args.docs else None
        configuration.destination_directory = args.cpp
        _ = generate_cpp(configuration) if args.cpp else None
        configuration.destination_directory = args.template
        _ = generate_template(configuration) if args.template else None
        configuration.destination_directory = args.python
        _ = generate_python(configuration) if args.python else None
        configuration.destination_directory = args.tests
        _ = generate_tests(configuration) if args.tests else None
        configuration.destination_directory = args.usdPath
        _ = generate_usd(configuration) if args.usdPath else None

        # The intermediate directory contains a tag file per-node that can be used to determine if the code generator
        # has been run since the last time the .ogn file was modified. The cost is that deletion of generated files
        # will not trigger their rebuild, but as the information of which files are generated is only known after
        # processing that is an acceptable tradeoff. (The alternative would be a much more verbose system that creates
        # a separate tag per generated file with all of the extra build dependencies required to make that work.)
        if args.intermediate:
            logger.info("Tagging the file as being built")
            intermediate_tag_path = os.path.join(args.intermediate, f"{os.path.basename(args.nodeFile.name)}.built")
            with open(intermediate_tag_path, "w", newline="\n", encoding="utf-8") as tag_fd:
                tag_fd.write("The presence of this file tags the last time its .ogn file was processed")

        if args.unwritable:
            logger.info("Tagging the generated directory as unwritable")
            unwritable_tag_path = os.path.join(args.unwritable, UNWRITABLE_TAG_FILE)
            with open(unwritable_tag_path, "w", newline="\n", encoding="utf-8") as tag_fd:
                tag_fd.write("The presence of this file ensures the directory will not regenerate at runtime")

    except Exception as error:
        raise ParseError(f"{os.path.basename(args.nodeFile.name)} failed") from error


if __name__ == "__main__":
    main(sys.argv)
