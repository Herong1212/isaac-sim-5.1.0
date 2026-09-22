"""
Support for handling attributes of type "bundle" - i.e. attributes whose job it is to encapsulate arbitrary
collections of other attributes, including other bundle attributes.
"""

from typing import List

from ..keys import CudaPointerValues, MemoryTypeValues
from ..utils import IndentedOutput, ParseError, to_usd_docs
from .AttributeManager import AttributeManager, CppConfiguration
from .naming import INPUT_GROUP, INPUT_NS


class BundleAttributeManager(AttributeManager):
    """
    Support class for attributes of type attribute bundle.
    This type of attribute is more complex than standard attributes since it has many more features to handle.
    """

    OGN_TYPE = "bundle"

    # Hardcoded type configuration using USD. Dictionary key is the OGN attribute type name (without arrays).
    CPP_CONFIGURATION = {
        # Type information is overridden but the include file is important to specialize
        "bundle": CppConfiguration(None, include_files=["omni/graph/core/ogn/UsdTypes.h"])
    }

    def requires_default(self):
        """Bundles never need default values as nothing other than an empty bundle makes sense"""
        return False

    @staticmethod
    def array_depths_supported() -> List[int]:
        """Bundle arrays are not yet supported in Fabric"""
        return [0]

    def memory_storage(self) -> str:
        """Bundle handles will always be stored on the CPU as that is where Fabric forces them"""
        return MemoryTypeValues.CPU

    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type"""
        return "Wrapper for accessing the nested Bundle values"

    def cpp_base_type_name(self):
        """This type name switches based on read status so this has to override the default method"""
        return "ConstBundleHandle" if self.is_read_only() else "BundleHandle"

    def has_can_vectorize(self):
        """Bundles attributes don't have a "canVectorize" method, as they are always vectorizable"""
        return False

    def require_precompute_invalidation(self):
        """Bundles attributes don't require preCompute invalidation"""
        return False

    def cpp_element_type_name(self) -> str:
        """The configuration is all manual here so override the default method"""
        return self.cpp_base_type_name()

    def cpp_default_initializer(self):
        """The bundle doesn't really have a default possible so initialize it to an invalid handle or empty array."""
        return "nullptr, 0" if self.array_depth > 0 else "BundleHandle::invalidValue()"

    def cpp_includes(self) -> List[str]:
        """Tack on the include implementing the bundle wrappers"""
        includes = super().cpp_includes()
        includes.append("omni/graph/core/ogn/Bundle.h")
        return includes

    def cpp_accessor_on_cpu(self) -> bool:
        """Bundle wrappers provide a type-casting accessor that will always live on the CPU"""
        return True

    def cpp_wrapper_class(self) -> str:
        """Returns the bundle-specific wrapper class name used to access attribute data in the C++ database"""
        template_args = [self.attribute_group, MemoryTypeValues.CPP[self.memory_type]]
        if self.cuda_pointer_type is not None:
            template_args.append(CudaPointerValues.CPP[self.cuda_pointer_type])
        return ("ogn::BundleAttribute", template_args)

    def validate_value(self, value):
        """Raises a ParseError if value is not a valid bundle value"""
        if value is not None:
            raise ParseError(f"Bundle {self.name} does not have values - tried to validate '{value}'")

    def cuda_includes(self) -> List[str]:
        """The bundle data is the same type of data in CUDA as it is in C++"""
        includes = super().cuda_includes()
        includes.append("omni/graph/core/Handle.h")
        return includes

    def cuda_base_type_name(self) -> str:
        """Returns a string with the CUDA base type of the attribute data"""
        return "omni::graph::core::ConstBundleHandle" if self.is_read_only() else "omni::graph::core::BundleHandle"

    def cuda_element_type_name(self) -> str:
        """The configuration is all manual here so override the default method"""
        return self.cuda_base_type_name()

    def fabric_pointer_exists(self) -> List[str]:
        """Return a string that checks for the existence of the Fabric pointer variable value"""
        return [f"return {self.cpp_variable_name()}.isValid()"]

    def python_role_name(self) -> str:
        """Returns a string with the Python role name for this attribute"""
        return "og.AttributeRole.BUNDLE"

    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the bundle data"""
        return "omni.graph.core.BundleContents"

    def python_type_annotation(self) -> str:
        """Returns a string with the Python annotation name, as defined by the omni.graph.core.data_types module.
        The default uses the SDF type name but there isn't one for this type so hardcode the actual type.
        """
        return "omni.graph.core.types.bundle" + "array" * self.array_depth

    def create_type_name(self) -> str:
        """Bundled attributes have a special name when creating so that they can be instantiated differently"""
        return "bundle"

    # ----------------------------------------------------------------------
    def generate_python_property_code(self, out: IndentedOutput):
        """Emits the generated code implementing a property for this bundle attribute.
        This class overrides the default behaviour because it needs a wrapper class to access the internal
        functionality of the bundle.
        """
        property_name = self.python_property_name()
        out.write()
        out.write("@property")
        if out.indent(f"def {property_name}(self) -> og.BundleContents:"):
            out.write(f'"""Get the bundle wrapper class for the attribute {self.namespace}.{property_name}"""')
            out.write(f"return self.__bundles.{property_name}")
            out.exdent()

        # No setters at all for read only bundles
        if self.is_read_only():
            return
        property_name = self.python_property_name()
        out.write()
        out.write(f"@{property_name}.setter")
        if out.indent(f"def {property_name}(self, bundle: og.BundleContents):"):
            out.write(f'"""Overwrite the bundle attribute {self.namespace}.{property_name} with a new bundle"""')
            if out.indent("if not isinstance(bundle, og.BundleContents):"):
                out.write('carb.log_error("Only bundle attributes can be assigned to another bundle attribute")')
                out.exdent()
            out.write(f"self.__bundles.{property_name}.bundle = bundle")
            out.exdent()

    # ----------------------------------------------------------------------
    def add_python_imports(self):
        """Add the modules required for proper parsing of this type"""
        super().add_python_imports()
        self.imports_og.append("import carb")

    # ----------------------------------------------------------------------
    def sdf_type_name(self) -> str:
        """Bundle attributes have no pxr::SdfValueTypeName"""

    # ----------------------------------------------------------------------
    def usd_name(self) -> str:
        """Bundled output and state attributes are represented as
        relationships but because of backwards copatiblity used
        separator must be `_`.
        """
        if self.attribute_group == INPUT_GROUP:
            return self.name
        return self.name.replace(":", "_")

    # ----------------------------------------------------------------------
    def emit_usd_declaration(self, out: IndentedOutput):
        """Print a declaration for this attribute in USD

        Args:
            out: Output handler where the USD will be emitted
        """
        try:
            usd_name = self.usd_name()
        except ParseError:
            # Attributes without USD representations can be skipped
            return

        docs = to_usd_docs(self.description)

        # all bundles are stored as relationships
        if out.indent(f"custom rel {usd_name} ("):
            out.write(docs)
            out.exdent(")")

    # ----------------------------------------------------------------------
    def generate_python_validation(self, out: IndentedOutput):
        if self.is_required and self.do_validation:
            name = f"{self.namespace}.{self.python_property_name()}"
            if out.indent(f"if not db.{name}.valid:"):
                if self.namespace == INPUT_NS:
                    out.write(f"db.log_warning('Required bundle {name} is invalid or not connected, compute skipped')")
                else:
                    out.write(f"db.log_error('Required bundle {name} is invalid, compute skipped')")

                out.write("return False")
                out.exdent()
