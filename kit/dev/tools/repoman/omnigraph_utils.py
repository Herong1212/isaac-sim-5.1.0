"""Common utilities shared by the repo tools used for OmniGraph"""
import argparse
import logging
import os
from pathlib import Path
import sys

import omni.repo.man


# ==============================================================================================================
# Keep all of the repo tools logging together
logger = None


def _bootstrap_logger():
    if logger is not None:
        return logger
    new_logger = logging.getLogger("RepoTool")
    if not new_logger.handlers:
        _handler = logging.StreamHandler(sys.stdout)
        new_logger.addHandler(_handler)
    else:
        _handler = new_logger.handlers[0]
    _handler.setFormatter(logging.Formatter("[%(name)s] [%(levelname)s] %(message)s"))
    _handler.setLevel(logging.DEBUG)
    new_logger.setLevel(logging.DEBUG if os.getenv("REPO_TOOL_DEBUG") else logging.WARN)
    return new_logger


logger = _bootstrap_logger()


# ==============================================================================================================
def tool_enabled(config: dict[str, any], tool_name: str) -> bool:
    """Returns True if the named tool does not have a configuration entry of enabled=False"""
    tool_config = config.get(tool_name, {})
    enabled = tool_config.get("enabled", False)
    if not enabled:
        logger.info("Tool '%s' not enabled", tool_name)
    return enabled


# ==============================================================================================================
def find_tools_locations(config: dict[str, any], import_path: str):
    """Returns a list of paths where the tools might be imported from.
    Args:
        config: Dictionary of configuration information from the repo tool call
        import_path: Module in which the tool you are looking for can be found
    """
    repo_folders = config.get("repo", {}).get("folders", {})
    root = repo_folders["root"]
    platform_host = omni.repo.man.get_host_platform()
    source_path = f"source/extensions/{import_path}"

    # build based repos (advanced)
    possible_module_paths = []
    for build_config in ["release", "debug"]:
        built_path = Path(f"{root}/_build/{platform_host}/{build_config}")
        if built_path.is_dir():
            # Inside of Kit
            possible_module_paths.append(built_path / "exts" / import_path)
            # In a Kit-SDK based repo
            possible_module_paths.append(built_path / "kit" / "exts" / import_path)
            # In a Kit-Kernel based repo
            possible_module_paths.append(built_path / "extsbuild" / import_path)
        # In a DriveSim style repo
        target_path = Path(f"{root}/_build/target-deps/kit_sdk_{build_config}/exts")
        if target_path.is_dir():
            possible_module_paths.append(target_path / import_path)

    # simple repo
    possible_module_paths.append(Path(f"{root}/{source_path}"))
    possible_module_paths.append(Path(f"{root}/../kit/{source_path}"))

    return [possible_path for possible_path in possible_module_paths if possible_path.is_dir()]


# ==============================================================================================================
def report_module_not_found(parser: argparse.ArgumentParser, tool_name: str) -> callable:
    """Report back to the user that the module could not be found and therefore the tool could not be run"""
    # If nothing was found then this is probably running the test suite from a package, where the script will not be
    # needed as part of the build so it can be safely ignored.
    parser.prog = tool_name
    parser.description = f"{parser.prog} cannot be run. omni.graph.tools is not in a visible build or source tree."
    parser.formatter_class = argparse.RawTextHelpFormatter

    def _run_no_repo_tool(options: argparse.Namespace, config: dict[str, any]):
        raise ValueError(parser.description)

    return _run_no_repo_tool
