"""
Contains the support class for managing attributes whose data is unsigned characters
"""

from typing import Any, List

from ..utils import ParseError
from .AttributeManager import CppConfiguration, CudaConfiguration
from .NumericAttributeManager import NumericAttributeManager, values_in_range
from .parsing import is_type_or_list_of_types


class UCharAttributeManager(NumericAttributeManager):
    """Support class for attributes of type unsigned 8-bit integer"""

    OGN_TYPE = "uchar"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "uchar": CppConfiguration("uint8_t", cast_required=False),
    }
    CUDA_CONFIGURATION = {
        "uchar": CudaConfiguration("uint8_t", cast_required=False),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = [12, 8]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_UNSIGNED_INTEGER

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid integer value"""
        if not is_type_or_list_of_types(value, int, self.tuple_count):
            raise ParseError(f"Value {value} on a uchar[{self.tuple_count}] attribute is not a matching type")
        if not values_in_range(value, 0, 255):
            raise ParseError(f"Value {value} on a uchar[{self.tuple_count}] attribute is out of range")
        super().validate_value(value)

    @staticmethod
    def tuples_supported() -> List[int]:
        """USD only supports a single unsigned value, no tuples"""
        return [1]

    def python_type_name(self):
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("int", "numpy.uint8")

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "UChar"

    def usd_type_name(self):
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("uchar")
