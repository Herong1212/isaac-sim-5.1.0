"""
Contains the support class for managing attributes whose data is strings
"""

import json
from typing import Any, List

from ..keys import CudaPointerValues, MemoryTypeValues
from ..utils import ParseError
from .AttributeManager import AttributeManager, CppConfiguration, CudaConfiguration
from .parsing import is_type_or_list_of_types


class StringAttributeManager(AttributeManager):
    """Support class for attributes of type string"""

    OGN_TYPE = "string"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "string": CppConfiguration("char*", cast_required=False, role="eText"),
    }
    CUDA_CONFIGURATION = {
        "string": CudaConfiguration("char*", cast_required=False, role="eText"),
    }

    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: Ignored - values are set as-is in Python
        """
        values = ["Anakin", "Skywalker"]
        if self.tuple_count > 1:
            values = [tuple(value + "x" * i for i in range(self.tuple_count)) for value in values]
        if self.array_depth > 0:
            values = [values, [values[1], values[0]]]
        return [[value] for value in values] if for_usd else values

    @staticmethod
    def tuples_supported() -> List[int]:
        """Strings don't have tuples"""
        return [1]

    @staticmethod
    def array_depths_supported() -> List[int]:
        """String arrays are not yet supported by fabric"""
        return [0]

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid string value"""
        if not is_type_or_list_of_types(value, str, self.tuple_count):
            raise ParseError(f"Value {value} on a string[{self.tuple_count}] attribute is not a matching type")
        super().validate_value(value)

    def cpp_includes(self) -> List[str]:
        """Tack on the include implementing the string wrapper types"""
        regular_includes = super().cpp_includes()
        regular_includes.append("omni/graph/core/ogn/ArrayAttribute.h")
        return regular_includes

    def cpp_element_value(self, value):
        """String defaults must be quoted - use the json library to do it right"""
        return f"{json.dumps(value)}" if value is not None else None

    def cpp_default_initializer(self):
        """The string initializer recognizes that a simple string is actual stored as an array."""
        # Arrays of strings have the same form as regular arrays
        if self.array_depth > 0:
            return super().cpp_default_initializer()

        # Regular strings look like arrays in that they have a defined length, yet not, because they can be represented
        # as an actual string rather than a std::array
        raw_value = self.cpp_element_value(self.default)
        if not raw_value:
            return "nullptr, 0"
        return f"{raw_value}, {len(self.default)}"

    def cpp_wrapper_class(self) -> str:
        """Returns a string with the wrapper class used to access attribute data in the C++ database along
        with the non-default parameters to that class's template"""
        wrapper_class = ""
        if self.is_read_only():
            modifier = "const "
            wrapper_class = "ogn::ArrayInput"
        else:
            modifier = ""
            wrapper_class = "ogn::ArrayOutput"

        template_arguments = [f"{modifier}char", MemoryTypeValues.CPP[self.memory_type]]
        if self.cuda_pointer_type is not None:
            template_arguments.append(CudaPointerValues.CPP[self.cuda_pointer_type])
        return (wrapper_class, template_arguments)

    def has_can_vectorize(self):
        """String attributes don't have a "canVectorize" method, as they are always vectorizable"""
        return False

    def require_precompute_invalidation(self):
        """String attributes always require a preCompute invalidation, as those are arrays"""
        return True

    def fabric_needs_counter(self) -> bool:
        """Even simple strings require counter variables since they are implemented as arrays"""
        return True

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.TEXT"

    def python_value(self, value):
        """String values must be quoted - use the json library to do it right"""
        return json.dumps(value) if value is not None else None

    def python_value_as_repr(self, value):
        """Returns the value of this attribute in a format that prints as something that can be assigned."""
        return json.dumps(value) if isinstance(value, str) else str(value)

    def python_value_as_str(self, value):
        """Returns the value of this attribute in a Python-compatible format, None for no default."""
        return str(value)

    def python_type_name(self):
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("str", "numpy.str")

    def sdf_base_type(self) -> str:
        """Returns a string with the base type of the pxr.Sdf.ValueTypeName of the attribute data"""
        return "String"

    def usd_type_name(self):
        """Returns a string with the data type the attribute would use in a USD file"""
        return self.usd_add_containers("string")

    def empty_base_value(self) -> str:
        """Return the default for a string, which must include quotes"""
        return ""
