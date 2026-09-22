"""
Contains the support class for managing attributes whose data is arrays interpreted as surface normals
"""

from typing import Any, List

from .AttributeManager import CppConfiguration, CudaConfiguration
from .RoleAttributeManager import RoleAttributeManager


class NormalAttributeManager(RoleAttributeManager):
    """Support class for all attributes of type normal

    This encompasses all legal USD types of normal(3|4)(d|f|h)
    """

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "normald[3]": CppConfiguration(
            "pxr::GfVec3d", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eNormal"
        ),
        "normalf[3]": CppConfiguration(
            "pxr::GfVec3f", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eNormal"
        ),
        "normalh[3]": CppConfiguration(
            "pxr::GfVec3h", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eNormal"
        ),
    }
    CUDA_CONFIGURATION = {
        "normald[3]": CudaConfiguration(
            "double3", include_files=["cuda_fp16.h", "omni/graph/core/CUDAUtils.h"], role="eNormal"
        ),
        "normalf[3]": CudaConfiguration(
            "float3", include_files=["cuda_fp16.h", "omni/graph/core/CUDAUtils.h"], role="eNormal"
        ),
        "normalh[3]": CudaConfiguration(
            "__half3", include_files=["cuda_fp16.h", "omni/graph/core/CUDAUtils.h"], role="eNormal"
        ),
        "normald[4]": CudaConfiguration(
            "double4", include_files=["cuda_fp16.h", "omni/graph/core/CUDAUtils.h"], role="eNormal"
        ),
        "normalf[4]": CudaConfiguration(
            "float4", include_files=["cuda_fp16.h", "omni/graph/core/CUDAUtils.h"], role="eNormal"
        ),
        "normalh[4]": CudaConfiguration(
            "__half4", include_files=["cuda_fp16.h", "omni/graph/core/CUDAUtils.h"], role="eNormal"
        ),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: If True return as the data type used to set the value in USD attributes, else return Python values
        """
        values = {
            "d": [0.01625, 0.14125],
            "f": [0.125, 0.1625],
            "h": [0.5, 0.25],
        }[self.suffix()]
        values = [tuple((value + 0.125 * i) for i in range(self.tuple_count)) for value in values]
        if for_usd:
            from pxr import Gf

            gf_type = getattr(Gf, f"Vec{self.tuple_count}{self.suffix()}")
            values = [gf_type(*value) for value in values]
        if self.array_depth > 0:
            values = [[value, value[::-1]] for value in values]
        return [[value] for value in values] if for_usd else values

    @staticmethod
    def roles():
        """Return a list of valid role names for this type"""
        return ["normald", "normalf", "normalh"]

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.NORMAL"

    @staticmethod
    def tuples_supported() -> List[int]:
        """This type can only have 3 members, not 1"""
        return [3]

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return f"Normal{self.suffix()}"

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_arrays(f"normal{self.tuple_count}{self.suffix()}")
