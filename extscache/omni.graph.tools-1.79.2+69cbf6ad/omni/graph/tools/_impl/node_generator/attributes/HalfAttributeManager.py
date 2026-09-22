"""
Contains the support class for managing attributes whose data is half precision numbers
"""

from typing import Any, List

from ..utils import ParseError
from .AttributeManager import CppConfiguration, CudaConfiguration
from .NumericAttributeManager import NumericAttributeManager, values_in_range
from .parsing import is_type_or_list_of_types


class HalfAttributeManager(NumericAttributeManager):
    """Support class for attributes of type 16-bit floating point value"""

    OGN_TYPE = "half"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "half": CppConfiguration("pxr::GfHalf", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "half[2]": CppConfiguration("pxr::GfVec2h", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "half[3]": CppConfiguration("pxr::GfVec3h", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "half[4]": CppConfiguration("pxr::GfVec4h", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
    }
    CUDA_CONFIGURATION = {
        "half": CudaConfiguration("__half", cast_required=False),
        "half[2]": CudaConfiguration("__half3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "half[3]": CudaConfiguration("__half3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "half[4]": CudaConfiguration("__half4", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = [2.5, 4.5]
        if self.tuple_count > 1:
            values = [tuple(value + i * 0.125 for i in range(self.tuple_count)) for value in values]
            if for_usd:
                from pxr import Gf

                gf_type = getattr(Gf, f"Vec{self.tuple_count}h")
                values = [gf_type(*value) for value in values]  # noqa: PLE1133
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_FLOAT

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid half-float value"""
        if not is_type_or_list_of_types(value, float, self.tuple_count):
            raise ParseError(f"Value {value} on a half[{self.tuple_count}] attribute is not a matching type")
        # Values not representable exactly due to precision considerations are still accepted
        if not values_in_range(value, -65504, 65504):
            raise ParseError(f"Value {value} on a 16-bit float[{self.tuple_count}] attribute is out of range")
        super().validate_value(value)

    @staticmethod
    def tuples_supported() -> List[int]:
        """USD supports only these tuples natively so restrict support to them for now"""
        return [1, 2, 3, 4]

    def cpp_element_value(self, value) -> str:
        """Ensure floating point elements have decimal values so that they are properly recognized."""
        if isinstance(value, str):
            if value.lower() in ["inf", "+inf"]:
                return "pxr::GfHalf::posInf()"
            if value.lower() == "-inf":
                return "pxr::GfHalf::negInf()"
            if value.lower() == "nan":
                return "pxr::GfHalf::qNan()"
            if value.lower() == "snan":
                return "pxr::GfHalf::sNan()"
        return f"{value * 1.0}f"

    def python_type_name(self):
        """In Python the 16-bit float can only be represented as a regular float"""
        return self.python_add_containers("float", "numpy.float16")

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "Half"

    def usd_type_name(self):
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("half")
