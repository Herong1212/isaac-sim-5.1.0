"""
Contains the support class for managing attributes whose data is 32 bit integers
"""

from typing import Any, List

from ..utils import ParseError
from .AttributeManager import CppConfiguration, CudaConfiguration
from .NumericAttributeManager import NumericAttributeManager, values_in_range
from .parsing import is_type_or_list_of_types


class IntAttributeManager(NumericAttributeManager):
    """Support class for attributes of type 32-bit integer"""

    OGN_TYPE = "int"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "int": CppConfiguration("int", cast_required=False),
        "int[2]": CppConfiguration("pxr::GfVec2i", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "int[3]": CppConfiguration("pxr::GfVec3i", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "int[4]": CppConfiguration("pxr::GfVec4i", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
    }
    CUDA_CONFIGURATION = {
        "int": CudaConfiguration("int", cast_required=False),
        "int[2]": CudaConfiguration("int3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "int[3]": CudaConfiguration("int3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "int[4]": CudaConfiguration("int4", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = [-32, -23]
        if self.tuple_count > 1:
            values = [tuple(value + i for i in range(self.tuple_count)) for value in values]
            if for_usd:
                from pxr import Gf

                gf_type = getattr(Gf, f"Vec{self.tuple_count}i")
                values = [gf_type(*value) for value in values]  # noqa: PLE1133
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_INTEGER

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid integer value"""
        if not is_type_or_list_of_types(value, int, self.tuple_count):
            raise ParseError(f"Value {value} on an int[{self.tuple_count}] attribute is not a matching type")
        if not values_in_range(value, -2147483648, 2147483647):
            raise ParseError(f"Value {value} on a 32-bit integer[{self.tuple_count}] attribute is out of range")
        super().validate_value(value)

    @staticmethod
    def tuples_supported() -> List[int]:
        """USD supports only these tuples natively so restrict support to them for now"""
        return [1, 2, 3, 4]

    def cuda_base_type_name(self) -> str:
        """Returns a string with the CUDA base type of the attribute data"""
        return "int"

    def python_type_name(self):
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("int", "numpy.int32")

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "Int"

    def usd_type_name(self):
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("int")
