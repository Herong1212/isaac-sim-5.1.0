"""
Contains the support class for managing attributes whose data is time codes
"""

from typing import Any, List

from .AttributeManager import CppConfiguration, CudaConfiguration
from .DoubleAttributeManager import DoubleAttributeManager


class TimeCodeAttributeManager(DoubleAttributeManager):
    """Support class for all attributes of type timecode

    This is just an alias for double with a time-based interpretation
    """

    OGN_TYPE = "timecode"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "timecode": CppConfiguration("pxr::SdfTimeCode", include_files=["pxr/usd/sdf/timeCode.h"], role="eTimeCode"),
    }
    CUDA_CONFIGURATION = {
        "timecode": CudaConfiguration("double", cast_required=False),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = [5.0, 6.0]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    @staticmethod
    def tuples_supported() -> List[int]:
        """Timecodes do not have tuple representation in USD"""
        return [1]

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.TIMECODE"

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "TimeCode"

    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_arrays("timecode")
