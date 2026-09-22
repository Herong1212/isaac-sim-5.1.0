"""Module managing relationships between the attribute data types in different representations.

The set of representations being managed here includes:
- Names as they appear in a .ogn file
- Type annotation defined in _types.py
- pxr.Sdf.ValueTypeNames name
- Names as they appear in a .usda file

These conversions use the names as extracted from the file DataTypeNameConversions.json that is installed as part
of the omni.graph.tools extension. Using these names as a starting point ensures that the lists stay in sync and
are complete.

This file is very similar to omni.graph.tools._impl.type_name_conversions.py as it processes the same data in a
similar way.
"""

import pprint
from enum import Enum
from functools import lru_cache

import carb
import omni.graph.core as og

# Internal import - should never be done from outside code. Some internal implementation knowledge is used here
# rather than creating APIs that will only ever be used by this code.
from omni.graph.tools._impl.type_name_conversions import DataTypeError, DataTypeNameRepresentation
from omni.graph.tools._impl.type_name_conversions import _conversion_data as _name_conversion_data
from pxr import Sdf

from . import _types as ot


# ==============================================================================================================
class DataTypeRepresentation(Enum):
    """Enumeration of recognized data type representations used for specifying types for conversions."""

    OGN = 0
    """Type name as it appears in the .ogn file"""
    SDF = 1
    """Sdf.ValueTypeNames value corresponding to the data type"""
    PYTHON = 2
    """Type annotation for the data type from the omni.graph.core.types module"""
    TYPE = 3
    """omni.graph.core.Type object representing the OGN data type name"""


# ==============================================================================================================
class _ConversionData:
    """Container for the conversion data type provides different representations, optimized for different uses.
    Attributes:
        conversion_data: List of 5-tuples containing the type definitions corresponding to the descriptions found
        in the enum DataTypeRepresentation. If there is a known representation type missing it will be stored in
        the list as None.
    Raises:
        DataTypeError: If anything could not be converted, other than the known list without representations
    """

    def __init__(self):
        """Set up the raw conversion data by reading the file and storing the JSON results.
        Raises:
          DataTypeError if anything went wrong extracting the conversion data from the file
        """
        # The data returned here is a dictionary of OGN: [USD, SDF, CPP, PYTHON, PYTHON] which will be
        # converted into the data needed for type definitions here.
        raw_data = _name_conversion_data().conversion_data

        sdf_module = Sdf.ValueTypeNames

        self.conversion_data = []
        for ogn_type_name, other_type_names in raw_data.items():
            # No need to keep the informational entry
            if ogn_type_name == "LEGEND":
                continue

            # The SDF value is used as a lookup in the Sdf.ValueTypeNames namespace. The name passed has the
            # Sdf.ValueTypeNames prefix so strip that off to check the module.
            sdf_type_name = other_type_names[DataTypeNameRepresentation.SDF.value - 1]
            sdf_type = None if sdf_type_name is None else getattr(sdf_module, sdf_type_name.split(".")[-1], None)

            # The Python annotation name is used as a lookup in the omni.graph.core.types namespace
            try:
                annotation = other_type_names[DataTypeNameRepresentation.PYTHON_ANNOTATION.value - 1]
                annotation = None if annotation is None else getattr(ot, annotation.split(".")[-1], None)
            except AttributeError:
                carb.log_error(f"No Python type annotation found for '{ogn_type_name}'")
                annotation = None

            # The omni.graph.core.Type is created using the og.AttributeType utility bindings.
            ogn_type = og.AttributeType.type_from_ogn_type_name(ogn_type_name)
            # The conversion won't throw if the type name is invalid but it will return an UNKNOWN type so catch
            # that and replace it with None, the indicator of missing conversions used in this list.
            if ogn_type.base_type == og.BaseDataType.UNKNOWN:
                ogn_type = None

            self.conversion_data.append([ogn_type_name, sdf_type, annotation, ogn_type])

        # Set up a cache for each of the data types
        self.cached_data = {key_type: None for key_type in DataTypeRepresentation.__members__}

    # ==============================================================================================================
    def __str__(self) -> str:
        """Pretty print the contents of the table for debugging"""
        return pprint.pformat(self.conversion_data, indent=2, compact=True)

    # ==============================================================================================================
    def type_centric_data(self, key_type: DataTypeRepresentation) -> dict:
        """Returns a version of the conversion data that has a specified representation as the key type.
        The dictionary is created on demand to avoid the overhead unless it is needed, and cached to avoid the
        overhead of recreating it on every call.
        Args:
            key_type: Data type representation to use as the return dictionary key
        Returns:
            Dictionary of key_type: list_of_equivalent_types. The list will include the key_type as well, indexed as
            per the list of DataTypeRepresentation values for faster lookup.
        Raises:
            DataTypeError if anything is incorrect in the conversion data that prevents the return value from
            being constructed
        """
        # If it's already cached then return it immediately
        if key_type in self.cached_data:
            return self.cached_data[key_type]

        # Build the cached data that is a dictionary with representations of the given type as their keys
        converted_data = {}
        for representations in self.conversion_data:
            key = representations[key_type.value]
            if key is None:
                continue
            if key in converted_data:
                for index, existing_type in enumerate(representations):
                    if converted_data[key][index] is None:
                        converted_data[key][index] = [existing_type]
                    elif isinstance(converted_data[key][index], list):
                        converted_data[key][index].append(existing_type)
                    else:
                        converted_data[key][index] = [converted_data[key][index], existing_type]
            else:
                converted_data[key] = representations.copy()
        self.cached_data[key_type] = converted_data

        return self.cached_data[key_type]


# ==============================================================================================================
@lru_cache(maxsize=1)
def _conversion_data():
    """A simple implementation of the conversion data as a singleton class"""
    return _ConversionData()


# ==============================================================================================================
def convert_type(source: any, source_type: DataTypeRepresentation, return_type: DataTypeRepresentation) -> any:
    """Convert the name of a specific supported data type between two different representations.

    assert Sdf.ValueTypeNames.Bool == convert_type("bool", DataTypeRepresentation.OGN, DataTypeRepresentation.SDF)
    color_type = og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.COLOR)
    assert "color3d[]" == convert_type(color_type, DataTypeRepresentation.TYPE, DataTypeRepresentation.OGN)

    Args:
        source: Representation of the data type using the source representation
        source_type: Representation that source should be in
        return_type: Equivalent representation for type_name to be returned
    Returns:
        type_name in the given return_type representation
    Raises:
        DataTypeError if the type_name was not a legal value in the source representation, or had no equivalent in
        the return representation.
    """
    data = _conversion_data().type_centric_data(source_type)
    if source not in data:
        raise DataTypeError(
            f"Data type name {source} not found in list of {source_type.name} representations {list(data.keys())}"
        )

    try:
        conversion = data[source][return_type.value]
    except IndexError as error:
        raise DataTypeError(f"Conversion data for {source} not found in representation {return_type.name}") from error

    if conversion is None:
        raise DataTypeError(f"No representation of type {return_type.name} available for {source}")

    if isinstance(conversion, list):
        raise DataTypeError(f"Data type {source} has multiple representations as {source_type.name} - {conversion}")

    return conversion
