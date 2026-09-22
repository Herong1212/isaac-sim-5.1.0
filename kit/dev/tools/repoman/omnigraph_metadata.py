"""Wrapper to access the omnigraph_metadata repo_man tool, which lives in the Kit source tree"""
import argparse
import importlib
from pathlib import Path
import sys

from tools.repoman.omnigraph_utils import find_tools_locations, logger, report_module_not_found, tool_enabled

# Note: At some point the omni.graph.tools extension may move upstream of Kit, in which case this wrapper will have
#       to be updated and moved with it.


def setup_repo_tool(parser: argparse.ArgumentParser, config: dict[str, any]):
    """This tool entry point is a link to the actual omnigraph_metadata that is in Kit.
    The reason we need it is that `entry_point` is not optional and will fail repo_man if doesn't exist, however the
    entry point is different depending on whether this is running in Kit or merely in a Kit-kernel based repo.
    This wrapper ensures that the tool is found in any of these three situations:
    - Running within Kit before a build happens
    - Running in Kit after a build happens
    - Running in an app with the Kit SDK installed
    """
    if not tool_enabled(config, "repo_omnigraph_metadata"):
        return None

    import_path = "omni.graph.tools/omni/graph/tools/_impl/repo_tools"
    module_name = "generate_node_metadata"

    for module_path in find_tools_locations(config, import_path):
        # This little trick lets the relative imports in the module work
        logger.info("Importing Metadata generator from %s", module_path)
        sys.path.append(str(module_path))
        imported_module = importlib.import_module(module_name)
        logger.info("Metadata generator module is %s", imported_module)
        sys.path.remove(str(module_path))

        setup_function = getattr(imported_module, "setup_repo_tool", None)
        if setup_function is not None:
            logger.info("Found the setup function %s.%s", setup_function.__module__, setup_function.__name__)
            return setup_function(parser, config)

    return report_module_not_found(parser, Path(__file__).stem)
