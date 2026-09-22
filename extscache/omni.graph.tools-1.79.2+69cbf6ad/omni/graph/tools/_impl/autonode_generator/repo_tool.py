"""This is the repo tool wrapper for the AutoNode node type generator. It runs at build time or on-demand to
process all of the Python files in a directory looking for decorators with node type definitions. It then calls in
to the AutoNode generator to create .ogn and .py files implementing the node types defined by the decorated functions
and classes. It's mostly just a wrapper to the main code that does all of the work since that can also be called
directly at runtime.

For a standard extension setup in a build tree the usage would look like this:

    > repo autonode_generator
      --module-root C:/Exts/omni.my.extension/python
      --toml-file C:/Exts/omni.my.extension/config/extension.toml
      --ogn-folder C:/Build/windows-x86-64/release/exts/omni.my.extension/omni/my/extension/ogn/__autonode/
      --node-type-folder C:/Build/windows-x86-64/release/exts/omni.my.extension/omni/my/extension/ogn/

This command would look for all of the Python AutoNode definitions contained in the scripts in the autonode/
folder of the extension source tree, generating the .ogn/.py files definining the node types into the ogn/__autonode/
folder in the build tree and then running the node type generator to put the final generated node type definitions into
the ogn/ folder of the build tree.

When the configuration information normally found in the .toml file is already known, or has been specially configured,
it can be passed directly to the command instead of through the .toml contents:

    > repo autonode_generator
      --module-root C:/Exts/omni.my.extension/python
      --import-modules omni.my.extension.autonode
      --module-name omni.my.extension
      --ogn-folder C:/Build/windows-x86-64/release/exts/omni.my.extension/omni/my/extension/ogn/__autonode/
      --node-type-folder C:/Build/windows-x86-64/release/exts/omni.my.extension/omni/my/extension/ogn/
"""

import argparse
import logging
from pathlib import Path

from .build import build_autonode_from_paths, build_autonode_from_toml  # noqa: E402
from .parse_help import ReadableDir  # noqa: E402

# --------------------------------------------------------------------------------------------------------------

logger = logging.getLogger("AutoNode")
LOG_LEVELS = "DEBUG|INFO|WARN|ERROR|CRITICAL"


# ==============================================================================================================
def setup_repo_tool(parser: argparse.ArgumentParser, config: dict[str, any]):  # pragma: no cover    Unsupported code
    """Required function that integrates the tool with repo_man"""

    parser.prog = "autonode_generator"
    parser.description = __doc__
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument(
        "-m", "--module-name", type=str, default=None, help="Python module from which the folder was imported"
    )
    parser.add_argument(
        "-i",
        "--import-modules",
        type=str,
        metavar="MODULE",
        nargs="*",
        default=None,
        help="Import modules relative to the module-root where AutoNode definitions can be found",
    )
    parser.add_argument(
        "-r",
        "--module-root",
        action=ReadableDir,
        metavar="PATH",
        required=True,
        help="Root of the directory tree where the Python module can be found",
    )
    parser.add_argument(
        "-t",
        "--toml-file",
        type=argparse.FileType(),
        metavar="PATH",
        default=None,
        help="extension.toml file containing the AutoNode configuration data",
    )
    parser.add_argument(
        "-of",
        "--ogn-folder",
        type=str,
        required=True,
        metavar="DIRECTORY",
        help="Folder into which the node type definitions, .ogn and .py, are to be generated",
    )
    parser.add_argument(
        "-nf",
        "--node-type-folder",
        type=str,
        required=True,
        metavar="DIRECTORY",
        help="Location of the directory where the files generated from the .ogn files should be saved",
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

        if options.toml_file is not None:
            if options.module_name is not None:
                raise ValueError("Cannot use both the toml-file argument and the module-name argument")
            if options.import_modules is not None:
                raise ValueError("Cannot use both the toml-file argument and the import-modules argument")
            build_autonode_from_toml(
                options.module_root,
                options.toml_file,
                Path(options.ogn_folder),
                Path(options.node_type_folder),
            )
        elif options.module_name is not None and options.import_modules is not None:
            # Now that the options are all available, call the generator
            build_autonode_from_paths(
                options.module_root,
                options.module_name,
                options.import_modules,
                Path(options.ogn_folder),
                Path(options.node_type_folder),
            )
        else:
            raise ValueError("Must either specify a toml-file, or both module-name and import-modules")

    return run_repo_tool


# ==============================================================================================================
def autonode_node_type_generator(arg_list: list[str] = None):
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
if __name__ == "__main__":  # pragma: no cover    Unsupported code
    autonode_node_type_generator()
