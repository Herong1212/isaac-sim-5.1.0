"""pybind11 scene::optimizer bindings"""
from __future__ import annotations
import omni.scene.optimizer.core.bindings._omni_scene_optimizer_core
import typing

__all__ = [
    "ExecutionContext",
    "ISceneOptimizer",
    "SOPluginVersion",
    "acquire_interface",
    "release_interface"
]


class ExecutionContext():
    """
    A struct describing the context in which a Scene Optimization should be performed.

    This is accepted by all Scene Optimizer Operation Commands.

    :param int usdStageId: The stage on which to perform the operation
    :param int generateReport: If true, a report will be generated that can be viewed via the Scene Optimizer UI
    :param int verbose: If true, log extended information (may result in slower performance)
    :param int singleThreaded: If true, run operation single threaded
    :param int captureStats: If true, capture and report on the contents of the stage before and after the operations run
    :param str reportPath: File path where the report will be written, if undefined a path will be generated on execute
            
    """
    def __init__(self) -> None: ...
    @property
    def captureStats(self) -> int:
        """
        :type: int
        """
    @captureStats.setter
    def captureStats(self, arg0: int) -> None:
        pass
    @property
    def debug(self) -> int:
        """
        :type: int
        """
    @debug.setter
    def debug(self, arg0: int) -> None:
        pass
    @property
    def generateReport(self) -> int:
        """
        :type: int
        """
    @generateReport.setter
    def generateReport(self, arg0: int) -> None:
        pass
    @property
    def reportPath(self) -> str:
        """
        :type: str
        """
    @reportPath.setter
    def reportPath(self, arg0: str) -> None:
        pass
    @property
    def singleThreaded(self) -> int:
        """
        :type: int
        """
    @singleThreaded.setter
    def singleThreaded(self, arg0: int) -> None:
        pass
    @property
    def usdStageId(self) -> int:
        """
        :type: int
        """
    @usdStageId.setter
    def usdStageId(self, arg0: int) -> None:
        pass
    @property
    def verbose(self) -> int:
        """
        :type: int
        """
    @verbose.setter
    def verbose(self, arg0: int) -> None:
        pass
    pass
class ISceneOptimizer():
    def delete_prims(self, arg0: ExecutionContext, arg1: typing.List[str]) -> None: 
        """
        Delete prims at specified paths
        """
    def deregister_operation(self, arg0: str) -> None: 
        """
        Deregister an operation
        """
    def execute_operation(self, arg0: str, arg1: ExecutionContext, arg2: str) -> tuple: 
        """
        Execute the specified operation. Returns a tuple of success, optional error, and optional arbitrary data.
        """
    def get_operation_arguments(self, arg0: str) -> list: 
        """
        Returns a list of the arguments for the specified operation
        """
    def get_operation_author(self, arg0: str) -> str: 
        """
        Returns the author of the specified operation
        """
    def get_operation_description(self, arg0: str) -> str: 
        """
        Returns the description of the specified operation
        """
    def get_operation_display_name(self, arg0: str) -> str: 
        """
        Returns the display name of the specified operation
        """
    def get_operation_version(self, arg0: str) -> SOPluginVersion: 
        """
        Returns the semantic version of the specified operation
        """
    def get_operation_visible(self, arg0: str) -> bool: 
        """
        Returns whether or not this operation should be displayed in a UI
        """
    def get_operations(self) -> list: 
        """
        Returns a list of the registered operation names
        """
    def json_parser(self, arg0: ExecutionContext, arg1: str) -> bool: 
        """
        Parse a JSON configuration file or string that contains a sequence of operations to run.
        """
    def load_plugins(self) -> None: 
        """
        Load the plugins that ship with scene optimizer and from any paths defined in the SCENE_OPTIMIZER_PLUGIN_PATH environment variable
        """
    def load_plugins_from_path(self, arg0: str) -> None: 
        """
        Loads plugins contained in a directory
        """
    def path_resolver(self, arg0: ExecutionContext, arg1: typing.List[str], arg2: bool) -> list: 
        """
        Parses input paths, regex expressions, and considers hierarchies to find all prims in a scene that conform to the given arguments
        """
    pass
class SOPluginVersion():
    """
    Semantic version for plugins

    :param int major: The major version number
    :param int minor: The minor version number
    :param int rev: The revision number
    """
    def __init__(self) -> None: ...
    @property
    def major(self) -> int:
        """
        :type: int
        """
    @major.setter
    def major(self, arg0: int) -> None:
        pass
    @property
    def minor(self) -> int:
        """
        :type: int
        """
    @minor.setter
    def minor(self, arg0: int) -> None:
        pass
    @property
    def rev(self) -> int:
        """
        :type: int
        """
    @rev.setter
    def rev(self, arg0: int) -> None:
        pass
    pass
def acquire_interface(plugin_name: str = None, library_path: str = None) -> ISceneOptimizer:
    pass
def release_interface(arg0: ISceneOptimizer) -> None:
    pass
