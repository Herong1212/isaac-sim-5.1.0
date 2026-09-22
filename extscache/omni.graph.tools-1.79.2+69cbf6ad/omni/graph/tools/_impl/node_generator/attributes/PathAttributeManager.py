"""
Contains the support class for managing attributes whose data is strings represented as tokens
"""

from typing import Any

from .AttributeManager import CppConfiguration, CudaConfiguration
from .StringAttributeManager import StringAttributeManager


class PathAttributeManager(StringAttributeManager):
    """Support class for attributes of type path.
    There is no USD support for Sdf.Path values so these paths have to be stored as strings. This is acceptable as
    it is trivial to cast a string to an Sdf.Path if you wish to use that API to manipulate the string value.
    """

    OGN_TYPE = "path"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "path": CppConfiguration("char*", cast_required=False, role="ePath"),
    }
    CUDA_CONFIGURATION = {
        "path": CudaConfiguration("char*", cast_required=False, role="ePath"),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = ["/This/Is", "/The/Way"]
        if self.tuple_count > 1:
            values = [tuple(value + "x" * i for i in range(self.tuple_count)) for value in values]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type"""
        return "Path that points to an object on the USD stage"

    def create_type_name(self) -> str:
        """Path attributes have a special name when creating so that they can be instantiated differently"""
        return "path"

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.PATH"

    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the path data"""
        return "list[usdrt::SdfPath]"

    def python_type_annotation(self) -> str:
        """Returns a string with the Python annotation name, as defined by the omni.graph.core.data_types module.
        The default uses the SDF type name but there isn't one for this type so hardcode the actual type.
        """
        return "omni.graph.core.types.path" + "array" * self.array_depth

    def sdf_type_name(self) -> str:
        """Path attributes have no pxr::SdfValueTypeName"""
