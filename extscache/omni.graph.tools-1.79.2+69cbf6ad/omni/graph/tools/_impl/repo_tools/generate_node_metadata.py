"""Repo tool wrapper for the OmniGraph node metadata generator.

This can be run at build time or at runtime to access all of the node type definitions on a per-extension basis.

When run at build time or offline the path to the extension's root is passed in and the directories are scanned
for .ogn files and those definitions are added to the metadata.

    > repo omnigraph_metadata
      --extension-root /Exts/omni.my.extension
      --destination-file /Build/omni.my.extension/nodes.json

When accessed at runtime through Python the extension path is passed and used to find all of the defined node types
in the extension in order to access the metadata.

    import json
    from omni.graph.tools import build_directory_metadata
    metadata = build_directory_metadata("C:/Exts/omni.my.extension")
    print(json.dumps(metadata, indent=4))

The benefit of using the runtime version is that it will catch any node type definitions that are defined at runtime.

Use build_directory_metadata(DIR) to scan a directory for .ogn files and generate metadata from them.

Returns JSON data that contains the per-node-type metadata in this form:

    {
        "extension": "omni.my.extension",
        "nodes":
        {
            "node.type.1":
            {
                "version": 1,
                "description": "This is my first node type",
                "language": "C++",
                "uiName": "Node Type 1"
            },
            "node.type.2":
            {
                "version": 1,
                "description": "This is my second node type",
                "language": "Python",
                "uiName": "Node Type 2"
            }
        }
    }

The entry "extension" corresponds to the extension id, saved for redundancy, and the entry "nodes" contains the
metadata for the node types defined in that extension.  The list of metadata fields stored will contain the mentioned
set at a minimum, though some more may be added in the future.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# --------------------------------------------------------------------------------------------------------------
_logger = None
_LOG_LEVELS = "DEBUG|INFO|WARN|ERROR|CRITICAL"


def _bootstrap_logger():
    if _logger is not None:
        return _logger
    logger = logging.getLogger("OgMetadata")
    # The metadata logger will output to stdout in a standard way, defaulting to logging level "WARN" unless the
    # environment variables OG_METADATA_DEBUG or REPO_TOOL_DEBUG are set, in which case it defaults to level "DEBUG".
    if not logger.handlers:
        _handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(_handler)
    else:  # pragma: no cover (debugging)
        _handler = logger.handlers[0]
    _handler.setFormatter(logging.Formatter("[%(name)s] [%(levelname)s] %(message)s"))
    logger.setLevel(logging.DEBUG if os.getenv("OG_METADATA_DEBUG") or os.getenv("REPO_TOOL_DEBUG") else logging.WARN)
    return logger


_logger = _bootstrap_logger()


# ==============================================================================================================
class OgnScanError(Exception):
    """Exception to raise when there was a problem scanning .ogn files in a directory."""

    def __init__(self, problem: str, path: Path = None, ogn_files_failed: list[str] = None):
        """Save the information relevant to understanding the scanning error"""
        if path is not None:
            super().__init__(f"Could not scan {path} ({problem})")
        elif ogn_files_failed:
            super().__init__(f"Failed to process some .ogn files ({problem}) - {ogn_files_failed}")
        else:
            super().__init__(f"Failed scanning the extension directory ({problem})")


# ==============================================================================================================
def _write_metadata_if_necessary(ext_id: str, metadata: dict[str, dict], destination: Path) -> dict[str, dict | str]:
    """If the metadata has changed then write it out.
    Args:
        ext_id: Id of the extension whose metadata is being written
        metadata: Metadata to write
        destination: Location of file to be written, and to be checked for current metadata if it exists
    Returns:
        Contents of the metadata file
    Raises:
        IOError: If the file should have been written but could not for some reason
    """
    _logger.info("Checking to see if metadata for %s needs to be written", ext_id)
    full_metadata = {"extension": ext_id, "nodes": metadata}

    if destination is not None:
        metadata_changed = True
        if destination.is_file():
            _logger.info("Comparing generated metadata against existing %s", destination)
            with open(destination, "r", encoding="utf-8") as dest_fd:
                try:
                    # For the purposes of determining if the file should be written the extension ID can be ignored.
                    # It's only important if the node metadata changes.
                    old_full_metadata = json.load(dest_fd)
                    try:
                        old_metadata = old_full_metadata.get("nodes", [])
                        if old_metadata == metadata:
                            metadata_changed = False
                    except AttributeError:
                        metadata_changed = True
                except json.decoder.JSONDecodeError:
                    metadata_changed = True

        if metadata_changed:
            _logger.info("Data has changed. Writing new data")
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
            except OSError as error:  # pragma: no cover
                raise OSError("Failed to create destination directory") from error
            try:
                with open(destination, "w", encoding="utf-8") as dst_fd:
                    json.dump(full_metadata, dst_fd, indent=2)
            except OSError as error:  # pragma: no cover
                raise OSError("Failed to write to destination file") from error

    return full_metadata


# ==============================================================================================================
def get_node_type_names_from_metadata(metadata: dict[str, any]) -> list[str]:
    """Extract the list of fully qualified node type names from the generated metadata
    Args:
        metadata: Dictionary loaded as JSON from the nodes.json file generated earlier
    Returns:
        List of node type names appearing in the metadata, prepending the extension name if needed to make it unique
    """
    node_type_names = []
    # If a new format nodes.json is read the extension will be a separate entry
    extension_name = metadata.get("extension", None)
    for node_type_name, node_type_info in metadata.get("nodes", {}).items():
        if node_type_name.find(".") < 0:
            if extension_name is None:
                extension_name = node_type_info.get("extension", None)
            if extension_name is not None:
                node_type_name = f"{extension_name}.{node_type_name}"
        node_type_names.append(node_type_name)
    return node_type_names


# ==============================================================================================================
def build_directory_metadata(ext_path: str, destination: Path | None) -> dict[str, dict | str]:
    """Find all of the node type metadata that can be found in the given directory.
    Args:
        ext_path: Directory containing the .ogn files belonging to this extension, traversed fully to find them.
        destination: Location of file to write metadata. Do not write anything if None.
    Raises:
        OgnScanError: If the ext_path was not a directory or could not be read, or any of the .ogn files failed parsing.
    """
    _logger.info("Building metadata for extension %s into file %s", ext_path, destination)
    # fmt: off
    # Use os.walk because it is faster than Path.iterate
    ogn_file_paths = tuple(
        os.path.join(ext_path, file_name)
        for (ext_path, _, file_names) in os.walk(ext_path, followlinks=True)
        for file_name in file_names if file_name.endswith(".ogn")
    )
    # fmt: on
    if not ogn_file_paths:
        return {}

    # The extension name is always the name of the root directory
    ext_name = Path(ext_path).parts[-1]

    failed_files = []
    nodes_info = {}
    _logger.info("Extracting information from %d .ogn files", len(ogn_file_paths))
    for file_path in ogn_file_paths:
        _logger.debug("   %s", file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as fd:
                data = json.load(fd)
                node_key = next(iter(data.keys()))
                node_data = data[node_key]

                description = node_data.get("description", "")
                if not description:
                    description = "[No description]"

                ui_name = node_data.get("uiName", "")
                if not ui_name:
                    metadata = node_data.get("metadata")
                    if metadata:
                        ui_name = metadata.get("uiName", "")
                if not ui_name:
                    ui_name = node_key

                nodes_info[node_key] = {
                    "description": description,
                    "version": node_data.get("version", 1),
                    "uiName": ui_name,
                    "language": node_data.get("language", "C++"),
                }
                _logger.debug("   %s", json.dumps(nodes_info[node_key]))
        except FileNotFoundError as error:  # pragma: no cover
            _logger.warning("--> File not found")
            failed_files.append(f"{file_path} - {error}")
        except json.decoder.JSONDecodeError as error:  # pragma: no cover
            _logger.warning("--> JSON decode error")
            failed_files.append(f"{file_path} - {error}")
        except ValueError as error:  # pragma: no cover
            _logger.warning("--> Value error")
            failed_files.append(f"{file_path} - {error}")

    if failed_files:  # pragma: no cover
        raise OgnScanError("Failed to find some metadata", ogn_files_failed=failed_files)

    return _write_metadata_if_necessary(ext_name, nodes_info, destination)


# ==============================================================================================================
class ReadableDir(argparse.Action):
    """Helper class for the parser to check that a value is a readable directory"""

    def __call__(self, parser, namespace, values, option_string=None):
        """Function called by the arg parser to verify that a directory exists and is readable.

        If the function succeeds then the "self.dest" value, which is the argparse option for the argument being
        checked, will be set to a Path pointing to the readable directory.

        Args:
            parser: argparser required argument, ignored.
            namespace: argparser required argument that contains the parsed arguments.
            values: The path to the directory being checked for readability.
            option_string: argparser required argument, ignored.

        Raises:
            argparse.ArgumentTypeError if the requested directory cannot be found or created in readable mode
        """
        try:
            # If this is not a path then a TypeError will be raised
            prospective_dir = Path(values)
        except TypeError as error:
            raise argparse.ArgumentTypeError(f"'{values}' is not a valid directory path") from error

        if prospective_dir.is_dir():
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError(f"{prospective_dir} is not a directory")


# ==============================================================================================================
def setup_repo_tool(parser: argparse.ArgumentParser, config: dict[str, any]):
    """Required function that integrates the tool with repo_man"""

    parser.prog = "omnigraph_metadata"
    parser.description = __doc__
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument(
        "-r",
        "--extension-root",
        action=ReadableDir,
        metavar="PATH",
        required=True,
        help="Root of the directory tree where the extension can be found.",
    )
    parser.add_argument(
        "-d",
        "--destination",
        metavar="PATH",
        default=None,
        help="Path to which the metadata should be written. Write to stdout if no path is specified.",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="WARN",
        metavar=_LOG_LEVELS,
        help="Flag to enable debug output of the steps being taken during node type generation",
    )

    # --------------------------------------------------------------------------------------------------------------
    def run_repo_tool(options: argparse.Namespace, config: dict[str, any]):
        """Function that actually does the work after everything has been collected for it.

        Args:
            options: Parsed option values.

        Raises:
            ValueError: If any of the options are inconsistent with the others.
        """
        destination = None if options.destination is None else Path(options.destination)  # noqa: F821
        metadata = build_directory_metadata(options.extension_root, destination)
        numeric_level = getattr(logging, options.log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: '{options.log_level}' not in {_LOG_LEVELS}")
        _logger.setLevel(numeric_level)

        # If there was no destination file specified then write the metadata to stdout.
        if destination is None:
            print(json.dumps(metadata, indent=4))

    return run_repo_tool


# ==============================================================================================================
def generate_node_metadata(arg_list: list[str] = None):
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
    generate_node_metadata()
