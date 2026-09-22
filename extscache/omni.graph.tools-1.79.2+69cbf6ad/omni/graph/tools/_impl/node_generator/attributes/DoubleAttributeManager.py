"""
Contains the support class for managing attributes whose data is double precision numbers
"""

from typing import Any, List

from .AttributeManager import CppConfiguration, CudaConfiguration
from .NumericAttributeManager import NumericAttributeManager


class DoubleAttributeManager(NumericAttributeManager):
    """Support class for attributes of type double.

    As Python does not really have a double type, float values are used for that portion of the code.
    """

    OGN_TYPE = "double"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "double": CppConfiguration("double", cast_required=False),
        "double[2]": CppConfiguration("pxr::GfVec2d", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "double[3]": CppConfiguration("pxr::GfVec3d", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
        "double[4]": CppConfiguration("pxr::GfVec4d", include_files=["omni/graph/core/ogn/UsdTypes.h"]),
    }
    CUDA_CONFIGURATION = {
        "double": CudaConfiguration("double", cast_required=False),
        "double[2]": CudaConfiguration("double3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "double[3]": CudaConfiguration("double3", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
        "double[4]": CudaConfiguration("double4", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"]),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = [4.125, 2.125]
        if self.tuple_count > 1:
            values = [tuple(value + i * 0.125 for i in range(self.tuple_count)) for value in values]
            if for_usd:
                from pxr import Gf

                gf_type = getattr(Gf, f"Vec{self.tuple_count}d")
                values = [gf_type(*value) for value in values]  # noqa: PLE1133
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    def numerical_type(self) -> int:
        """Returns the numerical TYPE_* value for this attribute's data"""
        return NumericAttributeManager.TYPE_DECIMAL

    @staticmethod
    def tuples_supported() -> List[int]:
        """USD supports only these tuples natively so restrict support to them for now"""
        return [1, 2, 3, 4]

    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("float", "numpy.float64")

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "Double"

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("double")
