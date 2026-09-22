"""Helpers for configuring and running local tests, not meant for general use"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import omni.ext
import omni.graph.tools._internal as ogi
import omni.graph.tools.ogn as ogn
import omni.kit
from omni.graph.tools.tests.internal_utils import CreateHelper


# ==============================================================================================================
class _TestExtensionManager:
    """Object that lets you create and control a dynamically generated extension
    Attributes:
        __root: Path to the directory in which the extension will be created
        __ext_path: Path to the created extension directory
        __ext_name: Name of the created extension
        __ogn_files: Dictionary of class name to .ogn file implementing the class
        __module_path: Path to the Python module directory inside the extension
        __exclusions: List of file types to exclude from any generated code
        __creator: Helper that creates files of various types
    """

    # Dictionary of Path:count that tracks how many test extensions are using a given path, tracked so that the
    # extension manager's path information can be properly managed.
    PATHS_ADDED = defaultdict(lambda: 0)

    def __init__(
        self,
        root: Path,
        ext_name: str,
        versions: ogi.GenerationVersions,
        import_ogn: bool,
        import_ogn_tests: bool,
    ):
        """Initialize the temporary extension object, creating the required files.
        The files will not be deleted by this class, their lifespan must be managed by the caller, e.g. through using
        a TempDirectory for their location.

        Args:
            root: Directory that contains all extensions
            ext_name: Name of the extension to create (e.g. 'omni.my.extension')
            versions: Versions to use in any generated code
            import_ogn: Add a python module spec for the .ogn submodule in the extension.toml
            import_ogn_tests: Add a python module spec for the .ogn.tests submodule in the extension.toml
        Raises:
            AttributeError if there was a problem creating the extension configuration
        """
        ogi.LOG.info("Creating extension %s at %s", ext_name, root)
        self.__root: Path = root
        self.__ext_path: Path = root / ext_name
        self.__ext_name: str = ext_name
        self.__ogn_files: dict[str, Path] = {}  # Class name to .ogn file implementing it
        self.__module_path: Path = self.__ext_path / ext_name.replace(".", "/")
        self.__module_path.mkdir(parents=True, exist_ok=True)
        self.__exclusions: list[ogi.FileType] = []
        self.__creator: CreateHelper = CreateHelper(ext_name, self.__root, versions)

        self.__creator.add_extension_module(self.__root, ext_name, self.__module_path, import_ogn, import_ogn_tests)

    # --------------------------------------------------------------------------------------------------------------
    def add_standalone_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ):
        """Add a node definition for a node with no generated code. See CreateHelper.add_standalone_node for details"""
        created_files = self.__creator.add_standalone_node(node_type_name, exclusions)
        self.__exclusions = exclusions
        for created_file in created_files:
            if created_file.suffix == ".ogn":
                self.__ogn_files[node_type_name] = created_file
                return
        raise ValueError(f"No .ogn file found in standalone created files {created_files}")

    # --------------------------------------------------------------------------------------------------------------
    def add_v1_18_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ):
        """Add a node definition using the V1.18 and earlier pattern. See CreateHelper.add_v1_18_node for details"""
        created_files = self.__creator.add_v1_18_node(node_type_name, exclusions)
        self.__exclusions = exclusions
        for created_file in created_files:
            if created_file.suffix == ".ogn":
                self.__ogn_files[node_type_name] = created_file
                return
        raise ValueError(f"No .ogn file found in V1.18 created files {created_files}")

    # --------------------------------------------------------------------------------------------------------------
    def add_v1_19_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ):
        """Add a node definition using the V1.19 pattern. See CreateHelper.add_v1_19_node for details"""
        created_files = self.__creator.add_v1_19_node(node_type_name, exclusions)
        self.__exclusions = exclusions
        for created_file in created_files:
            if created_file.suffix == ".ogn":
                self.__ogn_files[node_type_name] = created_file
                return
        raise ValueError(f"No .ogn file found in V1.19 created files {created_files}")

    # --------------------------------------------------------------------------------------------------------------
    def add_cache_for_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ):
        """Add a node definition to the cache. See CreateHelper.add_cache_for_node for details"""
        self.__creator.add_cache_for_node(node_type_name, exclusions)
        self.__exclusions = exclusions

    # --------------------------------------------------------------------------------------------------------------
    async def add_hot_attribute_to_ogn(self):
        """Rewrite the .ogn file with a new input attribute "hot_attribute" for hot reload testing"""
        ogi.LOG.info("!!! Adding hot reload attribute to %s", str(self.__ogn_files))
        # Remember the .ogn definitions for use in the generation of sample code
        ogn_definitions = {
            class_name: {
                ogn.NodeTypeKeys.DESCRIPTION: "None",
                ogn.NodeTypeKeys.VERSION: 1,
                ogn.NodeTypeKeys.EXCLUDE: self.__exclusions or [],
                ogn.NodeTypeKeys.LANGUAGE: ogn.LanguageTypeValues.PYTHON,
                ogn.NodeTypeKeys.INPUTS: {
                    "hot": {"type": "bool", "description": "Additional attribute added for hot reload"}
                },
            }
            for class_name in self.__ogn_files
        }

        ogi.LOG.info("Updated ogn definition(s) in %s", self.__ogn_files)
        for class_name, ogn_path in self.__ogn_files.items():
            ogn_path = CreateHelper.safe_create(
                self.__module_path / "ogn" / "nodes",
                class_name,
                ogi.FileType.OGN,
                json.dumps({class_name: ogn_definitions[class_name]}),
            )
            self.__ogn_files[class_name] = ogn_path

        ogi.LOG.info("!!! Attribute added from hot reload")

    # --------------------------------------------------------------------------------------------------------------
    def add_extra_import(self, directory_name: str, file_name: str, object_to_define: str) -> Path:
        """Add a new file under the ogn/ directory that acts as a proxy for an import that results from the links
        that the LUA function add_ogn_subdirectory() adds. Returns the path to the newly created file.
        """
        return CreateHelper.safe_create(
            # self.__module_path / "ogn" / directory_name / file_name,
            self.__module_path / "ogn" / file_name,
            None,
            None,
            f"{object_to_define} = True\n",
        )

    # --------------------------------------------------------------------------------------------------------------
    async def enable(self):
        """Make the constructed extension visible to the extension manager, if it hasn't yet been, and enable it"""
        ogi.LOG.info("Enabling extension %s at %s", self.__ext_name, self.__ext_path)
        manager = omni.kit.app.get_app().get_extension_manager()
        # Remove and add back to ensure that the path is scanned for the new content
        manager.remove_path(str(self.__root))
        manager.add_path(str(self.__root), omni.ext.ExtensionPathType.COLLECTION_USER)

        # This sync is to get the manager to refresh its paths
        await omni.kit.app.get_app().next_update_async()

        manager.set_extension_enabled_immediate(self.__ext_name, True)
        self.PATHS_ADDED[self.__root] += 1

        # This sync is to allow time for executing the extension enabled hooks
        await omni.kit.app.get_app().next_update_async()

    # --------------------------------------------------------------------------------------------------------------
    async def disable(self):
        """Disable the constructed extension, if enabled and decrement the accesses to its path"""
        ogi.LOG.info("Disabling extension %s", self.__ext_name)
        manager = omni.kit.app.get_app().get_extension_manager()
        # If this was the last extension to need the path then remove it from the manager's path. Either way the
        # path is removed first to force the path to be scanned for the remaining content.
        manager.set_extension_enabled_immediate(self.__ext_name, False)

        # This sync is to ensure the extension is disabled before removing its path
        await omni.kit.app.get_app().next_update_async()

        manager.remove_path(str(self.__root))
        self.PATHS_ADDED[self.__root] -= 1
        # If some other creator exists in the same path then bring the path back for continued use
        if self.PATHS_ADDED[self.__root] > 0:
            manager.add_path(str(self.__root), omni.ext.ExtensionPathType.COLLECTION_USER)

        # This sync is to get the manager to executing the extension disabled hooks and refresh the paths
        await omni.kit.app.get_app().next_update_async()
