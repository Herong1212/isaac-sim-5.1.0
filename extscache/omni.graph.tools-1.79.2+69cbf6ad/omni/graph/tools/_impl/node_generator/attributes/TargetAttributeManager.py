"""
Support for handling "target" attributes that pass path data through the graph
"""

import json
from typing import List, Tuple

from ..keys import CudaPointerValues, MemoryTypeValues
from ..utils import IndentedOutput, ParseError, to_usd_docs
from .AttributeManager import AttributeManager, CppConfiguration, CudaConfiguration
from .naming import INPUT_GROUP, OUTPUT_GROUP, STATE_GROUP


class TargetAttributeManager(AttributeManager):
    """Support class for attributes of type target (ie paths)."""

    OGN_TYPE = "target"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        "target": CppConfiguration("TargetPath", cast_required=False, role="eTarget"),
    }
    CUDA_CONFIGURATION = {
        "target": CudaConfiguration("TargetPath*", cast_required=False, role="eTarget"),
    }

    @staticmethod
    def tuples_supported() -> List[int]:
        """Target attributes do not support tuples"""
        return [1]

    @staticmethod
    def array_depths_supported() -> List[int]:
        """Target attributes are arrays but have an arrayDepth of 0"""
        return [0]

    def requires_default(self):
        """Target attributes do not support defaults"""
        return False

    def cpp_includes(self) -> List[str]:
        """Target attributes include all array headers"""
        includes = super().cuda_includes()
        includes.append("omni/graph/core/ogn/ArrayAttribute.h")
        includes.append("array")
        return includes

    def _cpp_add_array_accessor(self, raw_type: str) -> str:
        """Returns a string that adds the appropriate array accessor to the given raw type
        Target attributes force the type to be an array"""
        if self.is_read_only():
            return f"ogn::const_array<{raw_type}>"
        return f"ogn::array<{raw_type}>"

    def cpp_wrapper_class(self) -> str:
        """Returns a string with the wrapper class used to access attribute data in the C++ database along
        with the non-default parameters to that class's template"""
        wrapper_class = "ogn::Array{}".format(
            {INPUT_GROUP: "Input", OUTPUT_GROUP: "Output", STATE_GROUP: "State"}[self.attribute_group]
        )
        template_arguments = [self.fabric_element_type(), MemoryTypeValues.CPP[self.memory_type]]
        if self.cuda_pointer_type is not None:
            template_arguments.append(CudaPointerValues.CPP[self.cuda_pointer_type])
        return (wrapper_class, template_arguments)

    def cpp_initializer(self) -> Tuple[str, str]:
        """Generate the code for the static attribute initializer.

        The initializer contains any compile-time values for the attribute, like name and type name.

        Returns:
            (NAME, DECLARATION)
                NAME: Name of the initializer object, which should be file-static
                DECLRATION: Full declaration of the initializer object
        """
        # Uses the logic in generate_attribute_static_data to get the right name for the initializer
        initializer_type = f"ogn::AttributeInitializer<{self.fabric_default_data_typedef()}, {self.attribute_group}>"
        initializer_name = self.cpp_variable_name()
        initializer_args = f'"{self.usd_name()}"'
        initializer_args += f', "{self.create_type_name()}"'
        initializer_args += f", {self.cpp_extended_type()}"
        initializer_args += ", nullptr, 0"
        return (initializer_name, f"{initializer_type} {initializer_name}({initializer_args});")

    def create_type_name(self) -> str:
        """Returns the type of this attribute as expected by the attribute creation methods"""
        return "target"

    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type"""
        return "Reference to a list of objects, usually prims, on the USD stage"

    def cuda_includes(self) -> List[str]:
        """Cuda cannot include iComputeGraph so it directly includes the handle definition file for path access"""
        includes = super().cuda_includes()
        includes.append("omni/graph/core/Handle.h")
        return includes

    def fabric_raw_type(self) -> str:
        """Return a string corresponding to the type of data this attribute points to in Fabric. This is used
        for size information, in particular for default values and for adding attributes to Fabric so using the
        C++ type is good enough.
        """
        pointer_type = self.fabric_element_type()
        return f"{pointer_type}*"

    def fabric_needs_counter(self) -> bool:
        """Returns true if the attribute's data type requires a separate element count variable"""
        return True

    def has_can_vectorize(self):
        """Only regular attribute are subject to auto-conversion, which could prevent them from being vectorized
        Array attributes are always vectorizable, thus don't have a canVectorize method"""
        return False

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid path value"""
        if isinstance(value, list) and not all(isinstance(single_value, str) for single_value in value):
            raise ParseError(f"Value {value} on a target attribute contains non-strings")
        if not isinstance(value, str):
            raise ParseError(f"Value {value} on a target attribute is not a string")
        super().validate_value(value)

    def validate_value_structure(self, value_to_validate):
        """Validate a value being set on the attribute. Targets can be lists or strings."""
        if isinstance(value_to_validate, list):
            legal_level_counts = [0]
        else:
            legal_level_counts = []

        self.validate_value_nested(value_to_validate, legal_level_counts)

    def require_precompute_invalidation(self):
        """Only array attributes need a pre compute invalidation call"""
        return True

    def add_python_imports(self):
        """Add the modules required for proper parsing of this type"""
        super().add_python_imports()
        self.imports_standard.append("import usdrt")

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.TARGET"

    def python_value(self, value):
        """Returns the value of this attribute in a Python-compatible format, None for no default."""
        return json.dumps(value) if value is not None else None

    def python_value_as_repr(self, value):
        """Returns the value of this attribute in a format that prints as something that can be assigned."""
        return json.dumps(value) if isinstance(value, str) else str(value)

    def python_value_as_str(self, value):
        """Returns the value of this attribute in a Python-compatible format, None for no default."""
        return str(value)

    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the target data"""
        return "list[usdrt::SdfPath]"

    def python_type_annotation(self) -> str:
        """Returns a string with the Python annotation name, as defined by the omni.graph.core.data_types module.
        The default uses the SDF type name but there isn't one for this type so hardcode the actual type.
        """
        return "omni.graph.core.types.target" + "array" * self.array_depth

    def empty_base_value(self):
        """Attribute types must define their single empty value"""
        return []

    def emit_usd_declaration(self, out: IndentedOutput):
        """Print a declaration for this attribute in USD.
        Target attributes are emmitted as relationships.

        Args:
            out: Output handler where the USD will be emitted
        """
        try:
            usd_name = self.usd_name()
        except ParseError:
            return

        docs = to_usd_docs(self.description)

        # Target attributes are stored as virtual prims, not actual USD attributes, so they require a
        # different type of declaration. Inputs are relationships, outputs are defined as nested prims.
        if out.indent(f"custom rel {usd_name} ("):
            out.write(docs)
            out.exdent(")")
