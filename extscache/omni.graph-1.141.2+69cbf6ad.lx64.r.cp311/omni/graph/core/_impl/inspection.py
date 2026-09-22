"""Helpers for running inspection on OmniGraph objects"""

import json
from contextlib import suppress
from typing import Dict, List, Optional, Union

import carb
import omni.graph.core as og

from .errors import OmniGraphError

# The types the inspector understands
_OmniGraphObjectTypes = Union[og.Graph, og.GraphContext, og.GraphRegistry, og.NodeType]


class OmniGraphInspector:
    """Provides simple interfaces for inspection of OmniGraph objects"""

    def __init__(self):
        """Import the inspection interface, logging a warning if it doesn't exist.
        This allows the functions to silently fail, while still providing an alert to the user as to why their
        inspection operations might not work as expected.
        """
        try:
            import omni.inspect as oi
        except ImportError as error:
            carb.log_warn(f"Load the omni.inspect extension to use OmniGraphInspector ({error})")
            oi = None
        self.__oi = oi

    # ----------------------------------------------------------------------
    def available(self) -> bool:
        """Returns true if the inspection capabilities are available"""
        return self.__oi is not None

    # ----------------------------------------------------------------------
    def memory_use(self, omnigraph_object: _OmniGraphObjectTypes) -> int:
        """Returns the number of bytes of memory used by the object, if it supports it

        Args:
            omnigraph_object: Object whose memory use is to be inspected

        Returns:
            int: Number of bytes found to be used by the object passed in

        Raises:
            OmniGraphError: If the object type doesn't support memory inspection
        """
        if not self.__oi:
            return 0
        if type(omnigraph_object) not in [og.GraphContext, og.NodeType]:
            raise OmniGraphError("Memory use can only be inspected on graph contexts and node types")

        memory_inspector = self.__oi.IInspectMemoryUse()
        omnigraph_object.inspect(memory_inspector)
        return memory_inspector.total_used()

    # ----------------------------------------------------------------------
    def as_text(self, omnigraph_object: _OmniGraphObjectTypes, file_path: Optional[str] = None) -> str:
        """Returns the serialized data belonging to the context (for debugging)

        Args:
            omnigraph_object: Object whose contents are to be inspected
            file_path: If a string then dump the output to a file at that path, otherwise return a string with the dump

        Returns:
            str: If no file_path was specified then return the inspected data.
                If a file_path was specified then return the path where the data was written (should be the same)

        Raises:
            OmniGraphError: If the object type doesn't support text inspection
        """
        if not self.__oi:
            return ""
        if not isinstance(omnigraph_object, og.GraphContext):
            raise OmniGraphError("Serialization only works on graph contexts")

        serializer = self.__oi.IInspectSerializer()
        if file_path is None:
            serializer.set_output_to_string()
        else:
            serializer.output_to_file_path = file_path
        omnigraph_object.inspect(serializer)

        return serializer.as_string() if file_path is None else serializer.get_output_location()

    # ----------------------------------------------------------------------
    def as_json(
        self,
        omnigraph_object: _OmniGraphObjectTypes,
        file_path: Optional[str] = None,
        flags: Optional[List[str]] = None,
    ) -> str:
        """Outputs the JSON format data belonging to the context (for debugging)

        Args:
            omnigraph_object: Object whose contents are to be inspected
            file_path: If a string then dump the output to a file at that path, otherwise return a string with the dump
            flags: Set of enabled flags on the inspection object. Valid values are:
                maps: Show all of the attribute type maps (lots of redundancy here, and independent of data present)
                noDataDetails: Hide the minutiae of where each attribute's data is stored in Fabric

        Returns:
            str: If no file_path was specified then return the inspected data.
                If a file_path was specified then return the path where the data was written (should be the same)

        Raises:
            OmniGraphError: If the object type doesn't support json inspection
        """
        if not self.__oi:
            return "{}"
        if not hasattr(omnigraph_object, "inspect") or not callable(omnigraph_object.inspect):
            raise OmniGraphError("JSON serialization only works on objects that have an 'inspect()' method")

        if flags is None:
            flags = []
        serializer = self.__oi.IInspectJsonSerializer()
        for flag in flags:
            serializer.set_flag(flag, True)
        if file_path is None:
            serializer.set_output_to_string()
        else:
            serializer.output_to_file_path = file_path
        omnigraph_object.inspect(serializer)

        if "help" in flags:
            return serializer.help_information()

        return serializer.as_string() if file_path is None else serializer.get_output_location()

    # ----------------------------------------------------------------------
    def attribute_locations(self, context: og.GraphContext) -> Dict[str, Dict[str, int]]:
        """Find all of the attribute data locations within Fabric for the given context.

        Args:
            context: Graph context whose Fabric data is to be inspected

        Returns:
            dict[str, dict[str,int]]: { attribute name : (attribute path, attribute location) }
        """
        if not self.__oi:
            return {}

        serializer = self.__oi.IInspectJsonSerializer()
        serializer.set_output_to_string()
        context.inspect(serializer)
        ignored_suffixes = ["_gpuElemCount", "_elemCount", "_cpuElemCount"]

        try:
            json_data = json.loads(serializer.as_string())["GraphContext"]["Fabric"]["Bucket Contents"]
            locations = {}
            for bucket_id, bucket_info in json_data.items():
                with suppress(KeyError):
                    paths = bucket_info["Path List"]
                    path_locations = [{} for _ in paths] if paths else [{}]
                    for storage_name, storage_info in bucket_info["Mirrored Arrays"].items():
                        abort = False
                        for suffix in ignored_suffixes:
                            if storage_name.endswith(suffix):
                                abort = True
                        if abort:
                            continue
                        # If the storage has no CPU location ignore it for now
                        with suppress(KeyError):
                            location = storage_info["CPU Data Location"]
                            data_size = storage_info["CPU Data Size"]
                            data_size = data_size / len(paths) if paths else data_size
                            if paths:
                                for i, _path in enumerate(paths):
                                    path_locations[i][storage_name] = hex(int(location))
                                    location += data_size
                            else:
                                path_locations[0][storage_name] = hex(int(location))
                    if paths:
                        for i, path in enumerate(paths):
                            locations[path] = path_locations[i]
                    else:
                        locations[f"NULL{bucket_id}"] = path_locations[0]
            return locations

        except Exception as error:
            raise OmniGraphError("Could not get the Fabric contents to analyze") from error
