"""
Contains the support class for managing attributes whose data is cartesian frames
"""

from typing import Any, List

from .AttributeManager import CppConfiguration, CudaConfiguration
from .MatrixAttributeManager import MatrixAttributeManager


class FrameAttributeManager(MatrixAttributeManager):
    """Support class for the attribute with role "frame" or "transform"
    These are aliases for "matrixd[4]", with support for different USD naming
    """

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "frame[4]": CppConfiguration(
            "pxr::GfMatrix4d", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eFrame"
        ),
        "transform[4]": CppConfiguration(
            "pxr::GfMatrix4d", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eTransform"
        ),
    }
    CUDA_CONFIGURATION = {
        "frame[4]": CudaConfiguration("Matrix4d", include_files=["omni/graph/core/cuda/Matrix4d.h"], role="eFrame"),
        "transform[4]": CudaConfiguration(
            "Matrix4d", include_files=["omni/graph/core/cuda/Matrix4d.h"], role="eTransform"
        ),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: If True return as the data type used to set the value in USD attributes, else return Python values
        """
        if self.attribute_type_name == "frame":
            a = 1.0
            b = 0.0
            c = 2.0
            d = 3.0
        else:
            a = 1.5
            b = 0.5
            c = 2.5
            d = 3.5
        values = [
            tuple(tuple(a if i == j else b for i in range(self.tuple_count)) for j in range(self.tuple_count)),
            tuple(tuple(c if i == j else d for i in range(self.tuple_count)) for j in range(self.tuple_count)),
        ]
        if for_usd:
            from pxr import Gf

            gf_type = getattr(Gf, f"Matrix{self.tuple_count}d")
            values = [gf_type(*values[0]), gf_type(*values[1])]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    @staticmethod
    def roles():
        """Return a list of valid role names for this type"""
        return ["frame", "transform"]

    @classmethod
    def is_matrix_type(cls) -> bool:
        """Frames and Transforms are matrix types"""
        return True

    def suffix(self):
        """Always uses matrix4d"""
        return "d"

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.FRAME" if self.attribute_type_name == "frame" else "og.AttributeRole.TRANSFORM"

    @staticmethod
    def tuples_supported() -> List[int]:
        """This type of matrix can only be 4d"""
        return [4]

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return f"Frame{self.suffix()}"

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        # transform4d is not a valid USD type, but for our purposes it's the same as frame4d
        return self.usd_add_arrays(f"frame{self.tuple_count}{self.suffix()}")
