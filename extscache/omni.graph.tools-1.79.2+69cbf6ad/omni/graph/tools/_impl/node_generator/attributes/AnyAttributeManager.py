"""
Contains the support class for managing attributes whose data is any type of data, determined at runtime
"""

import json
from typing import List

from ..keys import CudaPointerValues, MemoryTypeValues
from ..utils import _EXTENDED_TYPE_ANY, IndentedOutput, ParseError, to_usd_docs, value_as_usd
from .AttributeManager import AttributeManager, CppConfiguration, CudaConfiguration


class AnyAttributeManager(AttributeManager):
    """
    Support class for attributes whose type is only determined at runtime.

    Most of the generated code is removed for this type of attribute since the interface types are not yet known.
    """

    OGN_TYPE = "any"
    CPP_CONFIGURATION = {
        # Type information is overridden but the include file is important to specialize
        "any": CppConfiguration(None, include_files=["omni/graph/core/ogn/UsdTypes.h"])
    }
    CUDA_CONFIGURATION = {"any": CudaConfiguration(None, cast_required=False)}

    # ----------------------------------------------------------------------
    def requires_default(self):
        """Extended types never need default values as their data types are not known in advance"""
        return False

    # ----------------------------------------------------------------------
    def validate_value(self, value):
        """No values are welcome"""
        raise ParseError("'Any' type attributes are not allowed to have a default")

    # ----------------------------------------------------------------------
    def validate_value_structure(self, value_to_validate: any):
        """Any types can accept any value types"""
        # Technically it would be more correct to confirm the type is a legally recognized type but that's a lot of
        # extra work for hardly any extra benefit so just allow anything for now
        return

    # ----------------------------------------------------------------------
    @staticmethod
    def array_depths_supported() -> List[int]:
        """The meaning of an array of mixed union types is unclear and will not be supported at this time"""
        return [0]

    # ----------------------------------------------------------------------
    @staticmethod
    def tuples_supported() -> List[int]:
        """USD supports only these tuples natively so restrict support to them for now"""
        return [1]

    # ----------------------------------------------------------------------
    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type"""
        return "One of the existing Python attribute data types, as resolved at runtime by connection or by value"

    # ----------------------------------------------------------------------
    def cpp_configuration(self) -> CppConfiguration:
        """Returns the C++ configuration data that applies to the attribute type implemented by this manager
        If no implementation is defined then return an empty dictionary.
        """
        try:
            return self.CPP_CONFIGURATION["any"]
        except AttributeError:
            return CppConfiguration("any")

    # ----------------------------------------------------------------------
    def cpp_extended_type(self):
        """Returns the extended type identifier for C++ types"""
        return "kExtendedAttributeType_Any"

    # ----------------------------------------------------------------------
    def is_dynamic(self):
        """Returns True as "any" attributes are dynamic"""
        return True

    # ----------------------------------------------------------------------
    def cpp_base_type_name(self):
        """Returns a string with the C++ type of the attribute data
        This value relies on the fact that the group names correspond to the template parameters for RuntimeAttribute.
        """
        template_args = [self.attribute_group, MemoryTypeValues.CPP[self.memory_storage()]]
        if self.cuda_pointer_type is not None:
            template_args.append(CudaPointerValues.CPP[self.cuda_pointer_type])
        return f"ogn::RuntimeAttribute<{', '.join(template_args)}>"

    # ----------------------------------------------------------------------
    def cpp_element_type_name(self) -> str:
        """The configuration is all manual here so override the default method"""
        return self.cpp_base_type_name()

    # ----------------------------------------------------------------------
    def cpp_includes(self) -> List[str]:
        """Tack on the include implementing the runtime attribute wrappers"""
        regular_includes = super().cpp_includes()
        regular_includes.append("omni/graph/core/ogn/SimpleRuntimeAttribute.h")
        return regular_includes

    # ----------------------------------------------------------------------
    def cpp_accessor_on_cpu(self) -> bool:
        """Extended type wrappers provide a type-casting accessor that will always live on the CPU"""
        return True

    # ----------------------------------------------------------------------
    def has_fixed_type(self) -> bool:
        """Variable typed attributes have runtime type identification"""
        return False

    # ----------------------------------------------------------------------
    def ogn_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file"""
        return "any"

    # ----------------------------------------------------------------------
    def python_extended_type(self):
        """Returns the extended type identifier for Python attribute types"""
        return (_EXTENDED_TYPE_ANY, "any")

    # ----------------------------------------------------------------------
    def add_python_imports(self):
        """Add the modules required for proper parsing of this type"""
        super().add_python_imports()
        self.imports_standard.append("from typing import Any")

    # ----------------------------------------------------------------------
    def python_type_name(self):
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        return self.python_add_containers("any")

    # ----------------------------------------------------------------------
    def python_type_annotation(self) -> str:
        """Returns a string with the Python annotation name, as defined by the omni.graph.core.data_types module.
        The default uses the SDF type name but there isn't one for this type so hardcode the actual type.
        """
        return "omni.graph.core.types.any" + "array" * self.array_depth

    # ----------------------------------------------------------------------
    def python_value_as_repr(self, value):
        """Returns the value of this attribute in a format that prints as something that can be assigned."""
        return json.dumps(value) if isinstance(value, str) else str(value)

    # ----------------------------------------------------------------------
    def python_value_as_str(self, value):
        """Extended types may have string values so run it through json to ensure proper quoting in those cases.
        Arrays could be a different problem but since there are no arrays of strings they can be ignored for now.
        """
        if isinstance(value, str):
            return json.dumps(value)
        return str(value) if value is not None else None

    # ----------------------------------------------------------------------
    def generate_python_property_code(self, out: IndentedOutput):
        """Emits the generated code implementing a readable property for this extended attribute.
        This class overrides the default behaviour because it needs a wrapper class to access the internal
        functionality of the runtime data.
        """
        property_name = self.python_property_name()
        out.write()
        out.write("@property")
        if out.indent(f"def {property_name}(self) -> og.RuntimeAttribute:"):
            out.write(f'"""Get the runtime wrapper class for the attribute {self.namespace}.{property_name}"""')
            out.write(
                f"return og.RuntimeAttribute(self._attributes.{property_name}.get_attribute_data(),"
                f" self._context, {self.is_read_only()})"
            )
            out.exdent()
        # For this type of attribute a setter can forward the assignment to the value of the attribute, where legal
        out.write()
        out.write(f"@{property_name}.setter")
        if out.indent(f"def {property_name}(self, value_to_set: Any):"):
            out.write(f'"""Assign another attribute\'s value to outputs.{property_name}"""')
            if out.indent("if isinstance(value_to_set, og.RuntimeAttribute):"):
                out.write(f"self.{property_name}.value = value_to_set.value")
                out.exdent()
            if out.indent("else:"):
                out.write(f"self.{property_name}.value = value_to_set")
                out.exdent()
            out.exdent()

    # ----------------------------------------------------------------------
    def generate_python_validation(self, out: IndentedOutput):
        """Emit code that checks to make sure the attribute type is resolved before computing"""
        if self.do_validation:
            name = f"{self.namespace}.{self.python_property_name()}"
            if out.indent(f"if db.{name}.type.base_type == og.BaseDataType.UNKNOWN:"):
                out.write(f"db.log_warning('Required extended attribute {self.name} is not resolved, compute skipped')")
                out.write("return False")
                out.exdent()

    # ----------------------------------------------------------------------
    def sdf_type_name(self) -> str:
        """Extended type attributes have no pxr::SdfValueTypeName"""

    # ----------------------------------------------------------------------
    def usd_type_name(self):
        """As the type of the attribute is not known at load time use a token value to describe the accepted types"""
        return "token"

    # ----------------------------------------------------------------------
    def usd_type_accepted_description(self) -> str:
        """Returns a string that will be the default value of the USD token, describing accepted types"""
        return "any"

    # ----------------------------------------------------------------------
    def emit_usd_declaration(self, out):
        """USD declaration for extended types use a placeholder type of token so the code path must be replaced

        Args:
            out: Output handler where the USD will be emitted
        """
        usd_name = self.usd_name()
        usd_type = self.usd_type_name()

        docs = to_usd_docs(self.description)
        if self.array_depth == 0:
            default = value_as_usd(self.usd_type_accepted_description())
        else:
            default = value_as_usd([self.usd_type_accepted_description()] * self.array_depth)

        if out.indent(f"custom {usd_type} {usd_name} = {default} ("):
            out.write(docs)
            out.exdent(")")

    # ----------------------------------------------------------------------
    def fabric_pointer_exists(self) -> List[str]:
        """Return a string that checks for the existence of the fabric pointer variable value"""
        return [f"return {self.cpp_variable_name()}().isValid()"]
