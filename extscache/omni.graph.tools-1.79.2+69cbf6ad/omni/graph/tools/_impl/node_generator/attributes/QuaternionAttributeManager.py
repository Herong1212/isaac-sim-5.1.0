"""
Contains the support class for managing attributes whose data is arrays interpreted as quaternions
"""

from typing import Any, List, Union

from ..utils import ParseError
from .AttributeManager import CppConfiguration, CudaConfiguration
from .RoleAttributeManager import RoleAttributeManager

QUAT_OR_QUAT_LIST = Union[List[float], List[List[float]]]


class QuaternionAttributeManager(RoleAttributeManager):
    """Support class for all attributes of type quaternion

    This encompasses all legal USD types of quat(d|f|h).

    Note that for all quaternion values showing up in OGN the order of values will be (i, j, k, real), even though
    internally the Gf.Quat constructor uses (real, i, j, k). This means you have to be careful when extracting the
    quaternion values, using a cast rather element-wise construction to maintain the proper ordering.
    """

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "quatd[4]": CppConfiguration(
            "pxr::GfQuatd", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eQuaternion"
        ),
        "quatf[4]": CppConfiguration(
            "pxr::GfQuatf", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eQuaternion"
        ),
        "quath[4]": CppConfiguration(
            "pxr::GfQuath", include_files=["omni/graph/core/ogn/UsdTypes.h"], role="eQuaternion"
        ),
    }
    CUDA_CONFIGURATION = {
        "quatd[3]": CudaConfiguration(
            "double4", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"], role="eQuaternion"
        ),
        "quatf[4]": CudaConfiguration(
            "float4", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"], role="eQuaternion"
        ),
        "quath[4]": CudaConfiguration(
            "__half4", include_files=["cuda_fp16.h", "omni/graph/core/cuda/CUDAUtils.h"], role="eQuaternion"
        ),
    }

    def __constructor_ordering(self, value: QUAT_OR_QUAT_LIST) -> QUAT_OR_QUAT_LIST:
        """Converts the ordering of a quaternion value so that the vector appears in constructor parameter ordering.

        Args:
            value: Quaternion or list of quaternions to convert, assumed to be in [i, j, k, r] order
                   Values are lists, not tuples, because that's all the .ogn passes in.

        Returns:
            Quaternion or list of quaternions in constructor ordering

        Raises:
            ParseError if the value was not a legal quaternion value specification
        """
        if value is None:
            return None

        if not isinstance(value, list):
            raise ParseError(f"Value passed was not a legal quaternion construction value - '{value}'")

        # An empty list needs no conversion
        if not value:
            if self.array_depth == 0:
                raise ParseError("An empty list cannot be passed to a simple quaternion constructor")
            return []

        # Handle lists of lists
        if isinstance(value[0], list):
            real_value = []
            for item in value:
                if not isinstance(item, list) or len(item) != 4:
                    raise ParseError(f"Quaternion array member needs 4 members, got '{item}'")
                real_value.append([item[3], item[0], item[1], item[2]])
        elif len(value) == 4:
            real_value = [value[3], value[0], value[1], value[2]]
        else:
            raise ParseError(f"Quaternion value must have four elements, got '{value}'")

        return real_value

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: If True return as the data type used to set the value in USD attributes, else return Python values
        """
        values = {
            "d": [(0.01625, 0.14125, 0.26625, 0.78), (0.14125, 0.26625, 0.39125, 0.51625)],
            "f": [(0.125, 0.25, 0.375, 0.5), (0.25, 0.375, 0.5, 0.625)],
            "h": [(0.0, 0.25, 0.5, 0.75), (0.125, 0.375, 0.625, 0.875)],
        }[self.suffix()]
        if for_usd:
            from pxr import Gf

            gf_quat_type = getattr(Gf, f"Quat{self.suffix()}")
            # The reordering ensures consistency in the order of parameters exposed to the interface to match the
            # order stored in memory rather than the order in the constructor.
            values = [gf_quat_type(real, i, j, k) for (i, j, k, real) in values]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    @staticmethod
    def roles():
        """Return a list of valid role names for this type"""
        return ["quatd", "quatf", "quath"]

    def cpp_constructor_value(self, value: QUAT_OR_QUAT_LIST) -> str:
        """The Gf.Quat classes construct in a different order (r, i, j, k) than the user-facing order (i, j, k, r) so
        generate the initializer in the rearranged order

        Args:
            value: Python value to convert

        Returns:
            A string representing the given values in C++ form
        """
        if not self.cpp_configuration().base_type_name.startswith("pxr"):
            return super().cpp_constructor_value(value)

        return super().cpp_constructor_value(self.__constructor_ordering(value))

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.QUATERNION"

    @staticmethod
    def tuples_supported() -> List[int]:
        """This type can only have 4 members"""
        return [4]

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return f"Quat{self.suffix()}"

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_arrays(f"quat{self.suffix()}")

    def usd_value(self, value):
        """Reorder the value to be in Gf.Quat construction order."""
        return super().usd_value(self.__constructor_ordering(value))
