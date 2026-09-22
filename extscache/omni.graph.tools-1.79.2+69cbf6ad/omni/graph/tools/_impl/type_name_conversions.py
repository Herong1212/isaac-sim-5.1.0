"""This module provides converters for the data types used in the .ogn files.

Exports:
    convert_type_name: Function that provides the conversion of type name between different representations
    DataTypeError: Exception type when an error is found doing the conversions
    DataTypeNameRepresentation: Enum of the various known data type name representations
"""

import json
from enum import Enum
from functools import lru_cache
from pathlib import Path

import carb

__all__ = ["convert_type_name", "DataTypeError", "DataTypeNameRepresentation"]


# ==============================================================================================================
class DataTypeError(Exception):
    """Exception type to raise when there is a problem with the data type conversions"""


# ==============================================================================================================
class DataTypeNameRepresentation(Enum):
    """Enumeration of recognized data type name representations. The order of the enums corresponds to the order of
    data type conversion names as specified in the DataTypeNameConversions.json file. OGN is the keyword in the
    dictionary and the rest are the value's list contents.
    """

    OGN = 0
    """Type name as it appears in the .ogn file"""
    USD = 1
    """Type name as it appears in the .usda file"""
    SDF = 2
    """Type name variable from the Python Sdf.ValueTypeNames namespace"""
    CPP = 3
    """Returned type when requesting the type value from a generated .cpp node"""
    PYTHON = 4
    """Returned type when requesting the type value from a generated .py node"""
    PYTHON_ANNOTATION = 5
    """Namespaced definition that can be used as a type annotation for Python variables representing attribute data"""


# ==============================================================================================================
class _ConversionData:
    """Container for the conversion data type provides different representations, optimized for different uses"""

    def __init__(self):
        """Set up the raw conversion data by reading the file and storing the JSON results.
        Raises:
          DataTypeError if anything went wrong extracting the conversion data from the file
        """
        # It's not ideal that the location of this file is duplicated between the build system and here but there's no
        # easy way to share a path between the .lua file and this .py file.
        ext_path = Path(carb.tokens.get_tokens_interface().resolve("${omni.graph.tools}"))
        conversion_file = ext_path / "ogn" / "DataTypeNameConversions.json"

        if not conversion_file.is_file():  # pragma: no cover
            raise DataTypeError(f"Conversion file '{conversion_file}' not found")

        try:
            # Performance Note: If this ever takes too long due to I/O speed it could always be switched to use the
            # same logic as the repo_tool "omnigraph_type_name_conversions" to generate it without going through a file
            with open(conversion_file, "r", encoding="utf-8") as conv_fd:
                self.conversion_data = json.load(conv_fd)
        except (IOError, json.decoder.JSONDecodeError) as error:  # pragma: no cover
            raise DataTypeError(f"Failed to parse conversion file '{conversion_file}'") from error

        # Set up a cache for each of the data types
        self.cached_data = {key_type: None for key_type in DataTypeNameRepresentation.__members__}

    # ==============================================================================================================
    def _type_centric_data(self, key_type: DataTypeNameRepresentation) -> dict:
        """Returns a version of the conversion data that has a specified representation as the key type.
        The dictionary is created on demand to avoid the overhead unless it is needed, and cached to avoid the
        overhead of recreating it on every call.
        Args:
            key_type: Data type representation to use as the return dictionary key
        Returns:
            Dictionary of key_type: list_of_equivalent_types. The list will include the key_type as well, indexed as
            per the list of DataTypeNameRepresentation values for faster lookup.
        Raises:
            DataTypeError if anything is incorrect in the conversion data that prevents the return value from
            being constructed
        """
        if key_type not in self.cached_data:
            converted_data = {}
            for ogn_type, other_types in self.conversion_data.items():
                # No need to keep the informational entry
                if ogn_type == "LEGEND":
                    continue

                key = ogn_type if key_type == DataTypeNameRepresentation.OGN else other_types[key_type.value - 1]
                values = [ogn_type] + other_types
                if key in converted_data:
                    for index, existing_type in enumerate(values):
                        if converted_data[key][index] is None:
                            converted_data[key][index] = [existing_type]
                        elif isinstance(converted_data[key][index], list):
                            converted_data[key][index].append(existing_type)
                        else:
                            converted_data[key][index] = [converted_data[key][index], existing_type]
                else:
                    converted_data[key] = [ogn_type] + other_types
            self.cached_data[key_type] = converted_data

        return self.cached_data[key_type]


# ==============================================================================================================
@lru_cache(maxsize=1)
def _conversion_data():
    """A simple implementation of the conversion data as a singleton class"""
    return _ConversionData()


# ==============================================================================================================
def convert_type_name(
    type_name: str, source_type: DataTypeNameRepresentation, return_type: DataTypeNameRepresentation
) -> str:
    """Convert the name of a specific supported data type between two different representations.

    assert "bool[]" == convert_type_name("bool[]", DataTypeNameRepresentation.OGN, DataTypeNameRepresentation.USD)
    assert "color3d[]" == convert_type_name("colord[3]", DataTypeNameRepresentation.OGN, DataTypeNameRepresentation.USD)

    Args:
        type_name: Name of the data type using the source representation
        source_type: Representation that type_name should be in
        return_type: Equivalent representation for type_name to be returned
    Returns:
        type_name in the given return_type representation
    Raises:
        DataTypeError if the type_name was not a legal value in the source representation, or had no equivalent in
        the return representation. This includes the case where there is more than one unique answer to the return
        type name, as you might find in the case of asking for the equivalent for the C++ data type "ogn::SimpleInput".
    """
    data = _conversion_data()._type_centric_data(source_type)  # pylint: disable=protected-access
    if type_name not in data:
        raise DataTypeError(
            f"Data type name {type_name} not found in list of {source_type.name} representations {list(data.keys())}"
        )

    try:
        conversion = data[type_name][return_type.value]
    except IndexError as error:
        raise DataTypeError(
            f"Conversion data for {type_name} not found in representation {return_type.name}"
        ) from error

    if conversion is None:
        raise DataTypeError(f"No representation of type {return_type.name} available for {type_name}")

    if isinstance(conversion, list):
        raise DataTypeError(
            f"Data type name {type_name} has multiple representations as {source_type.name} - {conversion}"
        )

    return conversion
