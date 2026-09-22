"""
Support for handling attributes of type "bundle" - i.e. attributes whose job it is to encapsulate arbitrary
collections of other attributes, including other bundle attributes.
"""

from typing import Any

from ..utils import ParseError
from .AttributeManager import AttributeManager, CppConfiguration, CudaConfiguration
from .parsing import is_type_or_list_of_types


# ======================================================================
class BoolAttributeManager(AttributeManager):
    """Support class for attributes of type bool"""

    OGN_TYPE = "bool"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {"bool": CppConfiguration("bool", cast_required=False)}
    CUDA_CONFIGURATION = {"bool": CudaConfiguration("bool", cast_required=False)}

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = [False, True]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid boolean value"""
        if not is_type_or_list_of_types(value, bool, self.tuple_count):
            raise ParseError(f"Value {value} on a boolean[{self.tuple_count}] attribute is not a matching type")
        super().validate_value(value)

    def cpp_element_value(self, value):
        """C++ uses different capitalization for boolean values."""
        return "true" if value else "false"

    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("bool", "numpy.bool")

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "Bool"

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("bool")

    def empty_base_value(self):
        """Return the value a boolean should take when no particular value is specified"""
        return False
