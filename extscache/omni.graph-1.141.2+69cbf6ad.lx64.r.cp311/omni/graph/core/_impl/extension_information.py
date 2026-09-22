"""Helper to manage information about nodes, node types and their extensions"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple

import omni.ext
import omni.graph.core as og
import omni.graph.tools as ogt
import omni.kit
import omni.usd


class ExtensionInformation:
    """Class that manages information about the relationships between nodes and node types, and extensions

    Public Interface:
        get_node_types_by_extension()
        get_nodes_by_extension()
    """

    # The extension name used when a node type cannot be found in the known extension list
    KEY_UNKNOWN_EXTENSION = "Unknown"

    def __init__(self):
        """Initialize the caches to be empty"""
        self.__known_extensions = None

        # If any extension configurations change the answers change so invalidate the locally cached results
        # when that happens.
        hooks = omni.kit.app.get_app_interface().get_extension_manager().get_hooks()
        self.__extension_enabled_hook = hooks.create_extension_state_change_hook(
            self.__reset_internal_cache, omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE
        )
        assert self.__extension_enabled_hook
        self.__extension_disabled_hook = hooks.create_extension_state_change_hook(
            self.__reset_internal_cache, omni.ext.ExtensionStateChangeType.BEFORE_EXTENSION_DISABLE
        )
        assert self.__extension_disabled_hook

    def __del__(self):
        self.__extension_enabled_hook = None
        self.__extension_disabled_hook = None

    # ----------------------------------------------------------------------
    def __reset_internal_cache(self, ext_id: str, *_):
        """Reset the internal cache so that it can be rebuilt later on demand"""
        self.__known_extensions = None

    # ----------------------------------------------------------------------
    def __get_extensions_matching_node_types(self) -> Dict[str, Dict]:
        """Extract the set of node names per extension from the OGN data stored in the extension.
        The data will be in the file ogn/nodes.json in the root extension directory. It contains
        various information about the nodes in the extension as follows:
            {
                "nodes": [
                    {
                        "name": FULL_NAME_OF_NODE,
                        "version": VERSION_NUMBER_OF_NODE,
                        "description": FULL_DESCRIPTION_OF_NODE
                    }
                ]
            }

        The returned information is a combination of node_type:extension and extension:node_type dictionaries,
        with a special entry in the latter to indicate whether the extension is currently enabled or not.

            {
                "extensions": {
                    "omni.graph.nodes": {
                        "enabled": true,
                        "nodes": ["omni.graph.node.A", "omni.graph.node.B"]
                    }
                },
                "nodes": {
                    "omni.graph.node.A": "omni.graph.nodes",
                    "omni.graph.node.B": "omni.graph.nodes"
                }
            }
        """
        if self.__known_extensions is None:  # noqa: PLR1702
            extension_per_node_type = {}
            self.__known_extensions = defaultdict(dict)
            manager = omni.kit.app.get_app_interface().get_extension_manager()
            for extension in manager.get_extensions():
                node_types_per_extension = []
                # If the generated node information exists, use it
                node_information = os.path.join(extension["path"], "ogn", "nodes.json")
                if os.path.isfile(node_information):
                    with open(node_information, "r", encoding="utf-8") as node_fd:
                        node_data = json.load(node_fd)
                    node_types_per_extension = ogt.get_node_type_names_from_metadata(node_data)
                # If there is no generated information some nodes can still be found by searching the path
                elif os.path.isdir(extension["path"]):
                    for root, dirs, _ in os.walk(extension["path"]):
                        if "ogn" in dirs:
                            ogn_dir = os.path.join(root, "ogn")
                            for ogn_root, _, ogn_files in os.walk(ogn_dir, followlinks=True):
                                for file_name in ogn_files:
                                    _, ext = os.path.splitext(file_name)
                                    if ext == ".ogn":
                                        ogn_file = os.path.join(ogn_root, file_name)
                                        with open(ogn_file, "r", encoding="utf-8") as ogn_fd:
                                            ogn_json = json.load(ogn_fd)
                                        node_type_name = list(ogn_json.keys())[0]
                                        if node_type_name.find(".") < 0:
                                            node_type_name = f"{extension['name']}.{node_type_name}"
                                        node_types_per_extension.append(node_type_name)
                            break
                if node_types_per_extension:
                    self.__known_extensions["extensions"][extension["name"]] = {
                        "enabled": extension["enabled"],
                        "nodes": node_types_per_extension,
                    }
                    extension_per_node_type.update(
                        {node_type: extension["name"] for node_type in node_types_per_extension}
                    )

            self.__known_extensions["nodes"] = extension_per_node_type

            # Prims may have node types attached to them that are not known to OmniGraph. They should not be in any
            # of the known extensions, though that will be checked just in case something wasn't created properly.
            prim_node_types = []
            for _, node_type_name in self.__get_prims_with_node_types().items():
                if node_type_name in extension_per_node_type:
                    continue
                prim_node_types.append(node_type_name)
            if prim_node_types:
                self.__known_extensions["extensions"][self.KEY_UNKNOWN_EXTENSION] = {
                    "enabled": False,
                    "nodes": prim_node_types,
                }

        return dict(self.__known_extensions)

    # ----------------------------------------------------------------------
    def get_node_types_by_extension(self) -> Dict[str, List[str]]:
        """Returns a tuple of two dictionaries. The first is the dictionary of enabled extensions to the list of
        nodes in the scene whose node types they implement, the second is the same thing for disabled extensions."""
        mapping_information = self.__get_extensions_matching_node_types()["extensions"]
        return (
            {extension: value["nodes"] for extension, value in mapping_information.items() if value["enabled"]},
            {extension: value["nodes"] for extension, value in mapping_information.items() if not value["enabled"]},
        )

    # ----------------------------------------------------------------------
    def __get_prims_with_node_types(self) -> Dict[str, str]:
        """Returns a dictionary of non-OmniGraph prims that have the node:type attribute set.
        These occur when the extension that created them is entirely unknown, possibly because
        it has not been installed.
        """
        prims_with_node_types = {}
        for prim in omni.usd.get_context().get_stage().TraverseAll():
            prim_path = str(prim.GetPath())
            node_type_attribute = prim.GetAttribute("node:type")
            if node_type_attribute:
                prims_with_node_types[prim_path] = node_type_attribute.Get()
        return prims_with_node_types

    # ----------------------------------------------------------------------
    def get_nodes_by_extension(self) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """Returns a tuple of three dictionaries.
        - Map of enabled extensions to the list of nodes in the scene whose node types they implement
        - Map of disabled extensions to the list of nodes in the scene whose node types they implement"""
        mapping_information = self.__get_extensions_matching_node_types()
        node_type_extensions = mapping_information["nodes"]
        enabled_extensions = [
            extension for extension, value in mapping_information["extensions"].items() if value["enabled"]
        ]
        node_extensions_enabled = defaultdict(list)
        node_extensions_disabled = defaultdict(list)
        stage = omni.usd.get_context().get_stage()

        # Next walk all of the OmniGraph graphs to find nodes known to it
        nodes_found = {}
        for graph in og.get_all_graphs():
            nodes_in_graph = graph.get_nodes()
            for node in nodes_in_graph:
                # If the node is not valid no information can be obtained from it so skip it
                if not node.is_valid():
                    continue
                if not node.get_node_type().is_valid():
                    # This came from an unloaded extension, but it will still have the node type information in USD
                    prim = stage.GetPrimAtPath(node.get_prim_path())
                    node_type_name = prim.GetAttribute("node:type").Get()
                else:
                    node_type_name = node.get_node_type().get_node_type()
                try:
                    extension = node_type_extensions[node_type_name]
                except KeyError:
                    extension = self.KEY_UNKNOWN_EXTENSION
                if extension in enabled_extensions:
                    node_extensions_enabled[extension].append(str(node.get_prim_path()))
                else:
                    node_extensions_disabled[extension].append(str(node.get_prim_path()))
                nodes_found[str(node.get_prim_path())] = extension

        # If any of the prims haven't been found in the OmniGraph traversal, check them for the telltale
        # "node:type" attribute that is present in all OmniGraph nodes and add them to the unknown extension category
        for prim_path, node_type_name in self.__get_prims_with_node_types().items():
            if prim_path in nodes_found:
                continue
            try:
                extension = mapping_information["nodes"][node_type_name]
            except KeyError:
                extension = self.KEY_UNKNOWN_EXTENSION
            if extension in enabled_extensions:
                node_extensions_enabled[extension].append(prim_path)
            else:
                node_extensions_disabled[extension].append(prim_path)

        return (dict(node_extensions_enabled), dict(node_extensions_disabled))
