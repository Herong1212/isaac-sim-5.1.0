"""
Contains the support class for managing attributes whose data is single precision numbers
"""

from typing import Any, List

from ..utils import ParseError
from .AttributeManager import CppConfiguration, CudaConfiguration
from .NumericAttributeManager import NumericAttributeManager, is_number_or_list_of_numbers, values_in_range


class FloatAttributeManager(NumericAttributeManager):
    """Support class for attributes of type float"""

    OGN_TYPE = "float"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "float": CppConfiguration("float", cast_required=False),
        "float[2]": CppConfiguration("pxr::GfVec2f", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "float[3]": CppConfiguration("pxr::GfVec3f", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "float[4]": CppConfiguration("pxr::GfVec4f", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
    }
    CUDA_CONFIGURATION = {
        "float": CudaConfiguration("float", cast_required=False),
        "float[2]": CudaConfiguration("float3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "float[3]": CudaConfiguration("float3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "float[4]": CudaConfiguration("float4", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = [4.5, 2.5]
        if self.tuple_count > 1:
            values = [tuple(value + i * 0.125 for i in range(self.tuple_count)) for value in values]
            if for_usd:
                from pxr import Gf

                gf_type = getattr(Gf, f"Vec{self.tuple_count}f")
                values = [gf_type(*value) for value in values]  # noqa: PLE1133
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_FLOAT

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid float value"""
        if not is_number_or_list_of_numbers(value, self.tuple_count):
            raise ParseError(f"Value {value} on a float[{self.tuple_count}] attribute is not a matching type")
        # Values not representable exactly due to precision considerations are still accepted
        if not values_in_range(value, -3402823400e38, 3402823400e38):
            raise ParseError(f"Value {value} on a 32-bit float[{self.tuple_count}] attribute is out of range")
        super().validate_value(value)

    @staticmethod
    def tuples_supported() -> List[int]:
        """USD supports only these tuples natively so restrict support to them for now"""
        return [1, 2, 3, 4]

    def cpp_includes(self) -> List[str]:
        """Tack on the include implementing the USD tuple type"""
        regular_includes = super().cpp_includes()
        if self.tuple_count in [2, 3, 4]:
            regular_includes.append("omni/graph/core/ogn/UsdTypes.h")
        return regular_includes

    def python_type_name(self):
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("float", "numpy.float32")

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "Float"

    def usd_type_name(self):
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("float")
