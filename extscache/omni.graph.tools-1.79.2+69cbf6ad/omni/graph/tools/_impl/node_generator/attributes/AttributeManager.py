# noqa: PLC0302
"""
Support for handling the parsing and generation for generic attributes.
Specific attribute types will override some of this behaviour in their own subclasses.

Exported Classes:
    AttributeManager

Exported Constants:
    PropertySet
"""
import os
import re
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ...deprecate import deprecated_function
from ..keys import AttributeKeys, CudaPointerValues, MemoryTypeValues
from ..utils import (
    _EXTENDED_TYPE_REGULAR,
    IndentedOutput,
    MetadataKeys,
    ParseError,
    UnimplementedError,
    get_metadata_dictionary,
    logger,
    to_usd_docs,
    to_usd_str,
)
from ..validators import validate_description
from .naming import (
    INPUT_GROUP,
    OUTPUT_GROUP,
    STATE_GROUP,
    assemble_attribute_type_name,
    is_input_name,
    is_output_name,
    is_state_name,
    split_attribute_name,
)
from .parsing import sdf_type_name

# ======================================================================
# Syntactic sugar for type validation of a property set
PropertySet = Tuple[bool, Dict]


# ======================================================================
# C++ type matcher that pulls apart typedefs like "int[2]" into "int" and "[2]".
# The reason is so that they can be put back together into legal types when adding
# references, "int(&)[2]", or pointers, "int(*)[2]". Other types can simply append a "&" or "*" to be legal.
RE_CPP_MATRIX = re.compile(r"(.*)(\[[0-9]+\]\[[0-9]+\])")
RE_CPP_TUPLE = re.compile(r"(.*)(\[[0-9]+\])")


# ======================================================================
@dataclass
class CppConfiguration:
    """Contains the information required to configure the C++ types for an attribute.

    Attributes:
        base_type_name (str): Data type for one of the attribute values (e.g. "double")
        cast_required (bool): If True then a cast is required for construction (e.g. "true" versus "pxr::GfHalf(1.0)")
        include_files (List[str]): List of files to include to define the above types (e.g. ["pxr/gf/vec3d.h"])
        role (str): Name of the AttributeRole enum value that marks this attribute's type (override not allowed)
    """

    base_type_name: str
    include_files: List[str] = field(default_factory=list)
    cast_required: bool = True
    role: str = "eNone"


# ======================================================================
@dataclass
class CudaConfiguration:
    """Contains the information required to configure the CUDA types for an attribute.

    Attributes:
        base_type_name (str): Data type for one of the attribute values (e.g. "double")
        cast_required (bool): If True then a cast is required for construction (e.g. "true" versus "__half(1.0)")
        include_files (List[str]): List of files to include to define the above types (e.g. ["cuda_fp16.h"])
        role (str): Name of the AttributeRole enum value that marks this attribute's type (override not allowed)
    """

    base_type_name: str
    include_files: List[str] = field(default_factory=list)
    cast_required: bool = True
    role: str = "eNone"


# ======================================================================
class AttributeManager:
    """
    Base class that provides support methods common to all types of attributes

    The members of this class implementing the mandatory values must be named the same as AttributeKeys.MANDATORY

    Attributes:
        attribute_type_name: Role interpretation of the attribute type (e.g. colorf for float[3])
        array_depth: How many array levels are on this attribute (optional, range 0-2  - default 0)
        base_name: Name of the attribute with the namespace removed
        cuda_pointer_type: Location of CUDA array pointers
        default: Value for the attribute when none is explicitly specified at runtime (mandatory)
        description: Description of what the attribute does (mandatory)
        do_validation: Is the attribute required to be valid before compute can be called?
        element_count: How many members of an array attribute are specified in the default value?
        attribute_type: Type of attribute this is (INPUT_GROUP, OUTPUT_GROUP, STATE_GROUP)
        is_deprecated: Has the attribute been deprecated? (optional - default False)
        deprecation_msg: Optional message describing what users must to do deal with the deprecated attribute
        imports_og: The list of OmniGraph import statements required by this attribute type
        imports_standard: The list of Python import statements required by this attribute type
        is_required: Is the attribute required for the node to operate? (optional - default True)
        manager: Object created to manage data for this attribute's type
        memory_type: Key indicating where the attribute's memory is stored (optional - default MemoryTypeValues.CPU)
        metadata: Dictionary of Key/Value strings attached to the attribute (optional - default {})
        name: Name of the attribute (mandatory)
        namespace: Namespace of the attribute (split from the full name)
        tuple_count: How many members of the same type are in this attribute as a tuple? (optional - default 1)
                         e.g. float[3] has a tuple count of 3
        type: Type of data contained by this attribute (mandatory)
        unimplemented_error: None if attribute is valid, else a string indicating what is unimplemented

    Abstract Methods To Override:
        These methods do not have usable definitions and must be overridden specifically for each attribute type.
            cpp_base_type_name(self) -> str
            cuda_base_type_name(self) -> str
            python_type_name(self) -> str
            sdf_type_name(self) -> str
            usd_name(self) -> str
            usd_type_name(self) -> str
        Usually you can add element counts and arrays using the associated FOO_add_containers() method, however
        you are free to elevate a type to array and element amounts in any way you like.

    Other Methods To Override:
        These methods add information, and should include the results from the super() call in their result
            add_python_imports(self)
            cpp_includes(self) -> List[str]
            cpp_element_type_name(self) -> str
            cuda_includes(self) -> List[str]
            cuda_element_type_name(self) -> str
            tuples_allowed(self) -> List[int]

        The derived classes must also implement the class variable OGN_TYPE, which defines how the base type of
        the attribute is declared in the .ogn file (e.g. "float" for float, float[3], float[], etc.)
    """

    CPP_CONFIGURATION = {}
    CUDA_CONFIGURATION = {}
    OGN_TYPE = None

    def __init__(self, attribute_name: str, attribute_type_name: str):
        """Set up the empty attribute values for population from the JSON description

        Args:
            attribute_name: Unique name for this attribute
            attribute_type_name: Unique name for this attribute type
        """
        self.cuda_pointer_type = None
        self.default = None
        self.description = None
        self.array_depth = 0
        self.tuple_count = 0
        self.element_count = 0
        self.is_deprecated = False
        self.deprecation_msg = ""
        self.is_required = True
        self.do_validation = True
        self.memory_type = None  # Lets the node set the value if no override is present
        self.metadata = {}
        self.name = attribute_name
        self.namespace, self.base_name = split_attribute_name(attribute_name)
        if is_input_name(attribute_name):
            self.attribute_group = INPUT_GROUP
        elif is_output_name(attribute_name):
            self.attribute_group = OUTPUT_GROUP
        elif is_state_name(attribute_name):
            self.attribute_group = STATE_GROUP
        else:
            raise ParseError(
                f"Attribute '{attribute_name}' has unrecognized port name. "
                "Should be 'inputs:X', 'outputs:X', or 'state:X'"
            )
        self.role = None
        self.attribute_type_name = attribute_type_name
        self.unimplemented_error = None
        self.imports_standard = []
        self.imports_og = []

    # ----------------------------------------------------------------------
    def sample_values(self, for_usd: bool = False) -> Any:
        """A set of sample values of the attribute's type for testing - None if samples are not supported.

        Args:
            for_usd: If True return as the data type used to set the value in USD attributes, else return Python values
                     Values are returned as a list of constructor arguments; e.g. if a call to set a value looks like
                     this: Set(float, float, float) then the parameters returned would be [float, float, float]
        """
        return

    # ----------------------------------------------------------------------
    @classmethod
    def is_matrix_type(cls) -> bool:
        """Returns true iff the attribute is a matrix type, where the tuple_count must be squared"""
        return False

    # ----------------------------------------------------------------------
    def ogn_base_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file"""
        return self.OGN_TYPE

    # ----------------------------------------------------------------------
    def ogn_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file"""
        return assemble_attribute_type_name(self.ogn_base_type(), self.tuple_count, self.array_depth)

    # ----------------------------------------------------------------------
    def ogn_root_type(self) -> str:
        """Returns a string containing the fully expanded name of this attribute type in a .ogn file, without arrays"""
        return assemble_attribute_type_name(self.ogn_base_type(), self.tuple_count, 0)

    # ----------------------------------------------------------------------
    def is_read_only(self) -> bool:
        """Returns True if this attribute should no be written to"""
        return self.attribute_group == INPUT_GROUP

    # ----------------------------------------------------------------------
    def supports_metadata(self) -> bool:
        """Returns True if this type of attribute can handle metadata output"""
        return True

    # ----------------------------------------------------------------------
    def memory_storage(self) -> str:
        """Returns the memory location the attribute's data will be stored - usually the same as its memory type"""
        return self.memory_type if self.memory_type is not None else MemoryTypeValues.CPU

    # ----------------------------------------------------------------------
    def base_data_type_description(self) -> str:
        """Returns a human-readable version of the base data type of the attribute"""
        # TODO: Add in overrides with reasonable descriptions
        return f"{self.OGN_TYPE} value"

    # ----------------------------------------------------------------------
    def data_type_description(self) -> str:
        """Returns a description of the fully qualified data type - common assembly that applies to many types"""
        description = ""
        if self.array_depth > 0:
            description += "Array of "
        if self.tuple_count > 1:
            description += f"{self.tuple_count}-tuples of "
        description += self.base_data_type_description()
        if self.array_depth == 0 and self.tuple_count == 1:
            # Ensure single values have a capitalized description.
            description = description.capitalize()
        else:
            # and multi-values are pluralized
            description = f"{description}s"
        return description

    # ----------------------------------------------------------------------
    def override_cpp_configuration(self, base_type_name: str, include_files: List[str], cast_required: bool):
        """Override the type definitions applicable to the attribute type implemented by this manager.

        Args:
            base_type_name (str): Data type for one of the attribute values (e.g. "double")
            cast_required (bool): Is a cast required for construction? (e.g. "true" versus "pxr::GfHalf(1.0)")
            include_files (List[str]): List of files to include to define the above types (e.g. ["pxr/gf/vec3d.h"])
        """
        old_configuration = self.cpp_configuration()
        old_configuration.base_type_name = base_type_name
        old_configuration.include_files = include_files
        old_configuration.cast_required = cast_required
        self.CPP_CONFIGURATION[self.ogn_root_type()] = old_configuration

    # ----------------------------------------------------------------------
    def cpp_configuration(self) -> CppConfiguration:
        """Returns the C++ configuration data that applies to the attribute type implemented by this manager
        If no implementation is defined then return an empty dictionary.
        """
        try:
            return self.CPP_CONFIGURATION[self.ogn_root_type()]
        except AttributeError:
            return CppConfiguration(self.ogn_root_type())

    # ----------------------------------------------------------------------
    def cpp_includes(self) -> List[str]:
        """Return a list of files to include in the C++ header for proper compilation of this type
        Note that the list entries should include the <> or "" surrounding the file name so that the proper include
        can be generated (e.g. '<carb/Types.h>' versus '"../myIncludes/myFile.h"')
        """
        includes = ["omni/graph/core/Type.h"]
        if self.array_depth > 0:
            includes.append("omni/graph/core/ogn/ArrayAttribute.h")
            includes.append("array")
        else:
            includes.append("omni/graph/core/ogn/SimpleAttribute.h")
        # Any include files in the configuration can be automatically added here, avoiding having each class
        # make a special override function just for that.
        with suppress(AttributeError, KeyError):
            includes += self.cpp_configuration().include_files
        return includes

    # ----------------------------------------------------------------------
    def cpp_declarations(self) -> List[str]:
        """Return a list of declarations to include in the C++ header for proper compilation of this type
        This will be included after the declarations.
        """
        return []

    # ----------------------------------------------------------------------
    def cpp_post_initialization(self, out: IndentedOutput):
        """Outputs any attribute-specific code needing to run at the end of the initializeType method"""
        return

    # ----------------------------------------------------------------------
    def cpp_pre_initialization(self, out: IndentedOutput):
        """Outputs any attribute-specific code needing to run at the top of in the initializeType method"""
        return

    # ----------------------------------------------------------------------
    def cpp_add_arrays(self, base_type: str) -> str:
        """Common method for transforming a base C++ type to add any appropriate arrays.

        Call this method directly when the tuple type is not the standard std::array

        Args:
            base_type: String containing the type name of the single-value, e.g. "float"
        """
        final_type = base_type
        for _level in range(0, self.array_depth):
            final_type = f"{final_type}*"
        return final_type

    # ----------------------------------------------------------------------
    def cpp_base_type_name(self) -> str:
        """Returns a string with the base C++ type of the attribute data"""
        try:
            return self.cpp_configuration().base_type_name
        except (AttributeError, KeyError) as error:
            raise ParseError(f"Attribute {self.name} has an unimplemented C++ base type name") from error

    # ----------------------------------------------------------------------
    def cpp_role_name(self) -> str:
        """Returns a string with the role name for this attribute - none by default"""
        try:
            return f"AttributeRole::{self.cpp_configuration().role}"
        except (AttributeError, KeyError) as error:
            raise ParseError(f"Attribute {self.name} has an unimplemented C++ role name") from error

    # ----------------------------------------------------------------------
    def cpp_element_type_name(self) -> str:
        """Returns a string with the full C++ type of the attribute data"""
        return self.cpp_configuration().base_type_name

    # ----------------------------------------------------------------------
    def _cpp_add_array_accessor(self, raw_type: str) -> str:
        """Returns a string that adds the appropriate array accessor to the given raw type, unchanged if not an array"""
        if self.array_depth > 0:
            if self.is_read_only():
                return f"ogn::const_array<{raw_type}>"
            return f"ogn::array<{raw_type}>"
        return raw_type

    # ----------------------------------------------------------------------
    def _cpp_accessor_type(self, include_arrays: bool) -> str:
        """Returns a string with the full C++ type of the data returned by the attribute's accessor"""
        modifier = "const " if self.is_read_only() else ""
        accessor_type = self.cpp_element_type_name()
        if include_arrays:
            accessor_type = self._cpp_add_array_accessor(accessor_type)
        return f"{modifier}{accessor_type}"

    # ----------------------------------------------------------------------
    def cpp_extended_type(self):
        """Returns the extended type identifier for C++ types"""
        return "kExtendedAttributeType_Regular"

    # ----------------------------------------------------------------------
    def cpp_accessor_on_cpu(self) -> bool:
        """Returns True if the accessor constructed for the attribute's data is always on the CPU, else it will be
        wherever the attribute's memory type dictates.
        """
        return False

    # ----------------------------------------------------------------------
    def cpp_wrapper_class(self) -> Tuple[str, List[str]]:
        """Returns a string with the wrapper class used to access attribute data in the C++ database along
        with the non-default parameters to that class's template"""
        wrapper_class = "ogn::{}{}".format(
            "Array" if self.array_depth > 0 else "Simple",
            {INPUT_GROUP: "Input", OUTPUT_GROUP: "Output", STATE_GROUP: "State"}[self.attribute_group],
        )

        memory_type = MemoryTypeValues.CPU if self.cpp_accessor_on_cpu() else self.memory_type
        template_arguments = [self.fabric_element_type(), MemoryTypeValues.CPP[memory_type]]
        if self.array_depth > 0 and self.cuda_pointer_type is not None:
            template_arguments.append(CudaPointerValues.CPP[self.cuda_pointer_type])
        return (wrapper_class, template_arguments)

    # ----------------------------------------------------------------------
    def cpp_typedef_name(self, use_namespace: bool = True):
        """Returns a string with the typedef for this attribute's raw type as it appears in Fabric.
        Use this typedef name instead of the raw type to avoid C++'s problem with things like "float[3]&"
        """
        safe_base_name = self.base_name.replace(":", "_")
        name = f"{self.namespace}::{safe_base_name}" if use_namespace else safe_base_name
        return f"{name}_t"

    # ----------------------------------------------------------------------
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
        if self.default is not None:
            initializer = self.cpp_default_initializer()
            if initializer is not None:
                initializer_args += f", {initializer}"
        # Array types must always be initialized
        elif self.array_depth > 0:
            initializer_args += ", nullptr, 0"
        return (initializer_name, f"{initializer_type} {initializer_name}({initializer_args});")

    # ----------------------------------------------------------------------
    def is_dynamic(self):
        """Returns False: attributes are not dynamic by default"""
        return False

    # ----------------------------------------------------------------------
    def create_type_name(self) -> str:
        """Returns the type of this attribute as expected by the attribute creation methods"""
        return self.usd_type_name()

    # ----------------------------------------------------------------------
    def has_fixed_type(self) -> bool:
        """Returns True if the attribute's type is fixed at compile time"""
        return True

    # ----------------------------------------------------------------------
    def override_cuda_configuration(self, base_type_name: str, include_files: List[str], cast_required: bool):
        """Override the type definitions applicable to the attribute type implemented by this manager.

        Args:
            base_type_name (str): Data type for one of the attribute values (e.g. "double")
            cast_required (bool): If True then a cast is required for construction (e.g. "true" versus "__half(1.0)")
            include_files (List[str]): List of files to include to define the above types (e.g. ["cuda_fp16.h"])
        """
        old_configuration = self.cuda_configuration()
        old_configuration.base_type_name = base_type_name
        old_configuration.include_files = include_files
        old_configuration.cast_required = cast_required
        self.CUDA_CONFIGURATION[self.ogn_root_type()] = old_configuration

    # ----------------------------------------------------------------------
    def cuda_configuration(self) -> CudaConfiguration:
        """Returns the C++ configuration data that applies to the attribute type implemented by this manager
        If no implementation is defined then return an empty dictionary.
        """
        try:
            return self.CUDA_CONFIGURATION[self.ogn_root_type()]
        except (AttributeError, KeyError):
            return CudaConfiguration(self.ogn_root_type())

    # ----------------------------------------------------------------------
    def cuda_includes(self) -> List[str]:
        """Return a list of include statements to add to the CUDA section of the C++ header
        The strings should be full paths, like "omni/graph/core/iComputeGraph.h"
        """
        includes = []
        # Any include files in the configuration can be automatically added here, avoiding having each class
        # make a special override function just for that.
        with suppress(AttributeError, KeyError):
            includes += self.cuda_configuration().include_files
        return includes

    # ----------------------------------------------------------------------
    def cuda_base_type_name(self) -> str:
        """Returns a string with the base C++ type of the attribute data"""
        try:
            return self.cuda_configuration().base_type_name
        except (AttributeError, KeyError) as error:
            raise ParseError(f"Attribute {self.name} has an unimplemented CUDA base type name") from error

    # ----------------------------------------------------------------------
    def cuda_role_name(self) -> str:
        """Returns a string with the role name for this attribute - none by default"""
        return f"AttributeRole::{self.cuda_configuration().role}"

    # ----------------------------------------------------------------------
    def cuda_element_type_name(self) -> str:
        """Returns a string with the full CUDA type of the attribute element data, not counting arrays"""
        return self.cuda_configuration().base_type_name

    # ----------------------------------------------------------------------
    def cuda_type_name(self) -> str:
        """Returns a string with the full CUDA type of the attribute data.
        The CUDA type adds an extra pointer indirection because the data is passed through from the CPU,
        and can not be dereferenced since the memory is on the GPU.
        """
        cuda_type = self.cuda_element_type_name()
        if cuda_type is None:
            return cuda_type
        # If the memory is coming from the CPU then the data can only be passed by reference, otherwise it must
        # be passed as a pointer to the actual (potentially GPU) data.
        ptr_suffix = "" if self.memory_storage() == MemoryTypeValues.CPU else "*"
        return f"{self.cpp_add_arrays(cuda_type)}{ptr_suffix}"

    # ----------------------------------------------------------------------
    def datamodel_accessor_constructor_args(self) -> List[str]:
        """Returns a list of declarations used by the datamodel accessor constructor"""
        role_name = self.cpp_role_name()
        return ["offset"] if role_name.endswith("eNone") else ["offset", role_name]

    # ----------------------------------------------------------------------
    def datamodel_accessor_declaration(self):
        """Returns a string containing the declaration of the datamodel accessor variable for this attribute"""
        variable_name = self.cpp_variable_name()
        (wrapper_class, template_parameters) = self.cpp_wrapper_class()

        type_declaration = f"{wrapper_class}<{','.join(template_parameters)}>"

        # For now the access methods just return a dereferenced pointer to the data. By encapsulating these in
        # methods now we leave open the option of doing things like delaying value reads if we want to.
        declarations = [f"{type_declaration} {variable_name};"]
        if not self.is_required:
            declarations.append(f"bool has_{variable_name}() const {{ {';'.join(self.fabric_pointer_exists())}; }};")
        return declarations

    # ----------------------------------------------------------------------
    def cpp_typedef_definitions(self) -> List[str]:
        """Return a list of strings containing the definitions of C++ typedefs facilitating the access of this
        attribute's Fabric data. The typedefs returned will vary, based on the memory type of the attribute.
        The base typedef "X_t" will always refer to the type of data you get from the attribute's accessor; i.e.
        the return value from "db.inputs.X()". The typedef will be an appropriate one for the memory type.
        For "ANY" member types there will be two typedefs, "X_cpu_t" and "X_gpu_t" indicating the typedefs to
        use when the data is extracted on the CPU and GPU respectively.
        """
        typedefs = []
        typedef = self.cpp_typedef_name(use_namespace=False)
        # Some typedefs are not conducive to adding pointers or references (e.g. float[3]) so for those there will be
        # an extra layer of type indirection to use as a bridge (using X_t_raw = float[3]; using X_t = X_t_raw&;)
        needs_raw_type = self.cpp_element_type_name().find("[") >= 0
        if needs_raw_type:
            raw_data_type = self._cpp_accessor_type(include_arrays=False)
            typedefs.append(f"using {typedef}_raw = {raw_data_type};")
            cpp_data_type = self._cpp_add_array_accessor(f"{typedef}_raw")
        else:
            cpp_data_type = self._cpp_accessor_type(include_arrays=True)
        # If the attribute can be accessed from CPU or GPU then it will have a different type when
        # passed across the boundary, as the CPU side can only have references to GPU memory pointers.
        if self.memory_storage() == MemoryTypeValues.CPU:
            typedefs.append(f"using {typedef} = {cpp_data_type}&;")
        else:
            typedefs.append(f"using {typedef}_cpu = {cpp_data_type}&;")

            indirection = "**" if self.array_depth > 0 else "*"
            suffix = "_gpu" if self.memory_storage() == MemoryTypeValues.ANY else ""
            cuda_type = self._cpp_accessor_type(include_arrays=False)
            if needs_raw_type:
                typedefs.append(f"using {typedef}_raw = {cuda_type};")
                cuda_type = f"{typedef}_raw"
            typedefs.append(f"using {typedef}{suffix} = {cuda_type}{indirection};")
        return typedefs

    # ----------------------------------------------------------------------
    def _needs_intermediate_typedef(self) -> bool:
        """Returns True if the attribute's data type requires an intermediate typedef in order to form legal pointers
        and references to it. e.g. array of double[3] since "double[3]*" is not a valid type"""
        pointer_type = self.cpp_element_type_name()
        return pointer_type.find("[") >= 0

    # ----------------------------------------------------------------------
    def _intermediate_typedef(self) -> str:
        """Returns the name of the intermediate typedef, only for use when it was required."""
        return f"{self.cpp_typedef_name(use_namespace=True)}_raw"

    # ----------------------------------------------------------------------
    def fabric_default_data_typedef(self) -> str:
        """Returns a string representing the raw data type stored in Fabric for this attribute's default values.
        Uses the predefined raw type for attribute's whose type requires it (e.g. array of double[3] since "double[3]*"
        is not a valid type.)"""
        return self.fabric_raw_type()

    # ----------------------------------------------------------------------
    def fabric_element_type(self) -> str:
        """Return a string corresponding to the type of element data this attribute points to in Fabric. This only
        differs from fabric_raw_type() in that arrays do not get an extra level of indirection.
        """
        prefix = "const " if self.is_read_only() else ""
        return f"{prefix}{self.cpp_element_type_name()}"

    # ----------------------------------------------------------------------
    def fabric_raw_type(self) -> str:
        """Return a string corresponding to the type of data this attribute points to in Fabric. This is used
        for size information, in particular for default values and for adding attributes to Fabric so using the
        C++ type is good enough.
        """
        if self._needs_intermediate_typedef():
            # This type already has any required "const" baked into it
            pointer_type = self._intermediate_typedef()
        else:
            pointer_type = self.fabric_element_type()
        indirection = "*" if self.array_depth > 0 else ""
        return f"{pointer_type}{indirection}"

    # ----------------------------------------------------------------------
    def fabric_pointer_exists(self) -> List[str]:
        """Return a string that checks for the existence of the fabric pointer variable value"""
        return [f"return {self.cpp_variable_name()}.isValid()"]

    # ----------------------------------------------------------------------
    def fabric_needs_counter(self) -> bool:
        """Returns true if the attribute's data type requires a separate element count variable"""
        return self.array_depth > 0

    # ----------------------------------------------------------------------
    def has_can_vectorize(self):
        """Only regular attribute are subject to auto-conversion, which could prevent them from being vectorized
        Array attributes are always vectorizable, thus don't have a canVectorize method
        """
        return self.array_depth == 0

    # ----------------------------------------------------------------------
    def require_precompute_invalidation(self):
        """Only array attributes need a pre compute invalidation call"""
        return self.array_depth != 0

    # ----------------------------------------------------------------------
    def python_extended_type(self):
        """Returns the extended type identifier for Python attribute types"""
        return (_EXTENDED_TYPE_REGULAR, None)

    # ----------------------------------------------------------------------
    def add_python_imports(self):
        """Add the modules required for proper parsing of this type"""
        if self.tuple_count > 1 or self.array_depth > 0:
            self.imports_standard.append("import numpy")

    # ----------------------------------------------------------------------
    def python_role_name(self) -> str:
        """Returns a string with the role name for this attribute usable in Python code - none by default"""
        return ""

    # ----------------------------------------------------------------------
    def python_type_name(self) -> str:
        """Returns a string with the Python "typing" type-checking declaration for the attribute data"""
        raise ParseError(f"Attribute {self.name} has an unimplemented Python type name")

    # ----------------------------------------------------------------------
    def python_type_annotation(self) -> str:
        """Returns a string with the Python annotation name, as defined by the omni.graph.core.types module.
        The type names are derived from the OGN names since they are already similar. The only difference is that
        the names reorder a bit to look more like Sdf names since that's what people will be familiar with.
        """
        base_name = self.sdf_type_name().lower()
        return None if not base_name else f"omni.graph.core.types.{base_name}"

    # ----------------------------------------------------------------------
    def python_add_containers(self, base_type: str, numpy_type: str = None) -> str:
        """Common method for transforming a base Python type to add any appropriate array or component values"""
        if self.tuple_count > 1:
            if self.is_matrix_type():
                if self.array_depth > 0:
                    shape = f"(N,{self.tuple_count},{self.tuple_count})"
                else:
                    shape = f"({self.tuple_count},{self.tuple_count})"
            elif self.array_depth > 0:
                shape = f"(N,{self.tuple_count})"
            else:
                shape = f"({self.tuple_count},)"
        elif self.array_depth > 0:
            shape = "(N,)"
        else:
            return base_type
        return f"numpy.ndarray(shape={shape}, dtype={numpy_type if numpy_type else base_type})"

    # ----------------------------------------------------------------------
    def python_property_name(self) -> str:
        """Return the name of a python property that will correspond to this attribute.

        Input attributes have a parent object "inputs" and output attributes have a parent object "outputs" in order to
        avoid name clashes and be consistent with the appearance of the C++ equivalent code
        """
        return self.base_name.replace(":", "_")

    # ----------------------------------------------------------------------
    def python_attribute_name(self) -> str:
        """Return the name of a python name that will correspond to this attribute.

        The attribute name itself is used as a property to represent the value. This name is for storing the
        actual og.Attribute.
        """
        return f"_attributes.{self.python_property_name()}"

    # ----------------------------------------------------------------------
    def __generate_python_property_get_code(
        self, attribute_name: str, property_name: str, out: IndentedOutput, on_gpu: bool, has_parent: bool = False
    ):
        """Emits the generated code implementing a property read accessor for the attribute.

        Args:
            attribute_name: Name of the attribute being accessed
            property_name: Name of the property to define for the attribute to be accessed
            out: Output location for the generated code
            on_gpu: If True then the accessor should get data pointers from GPU memory
            has_parent: If True then this is a nested accessor and it has to go to the parent for some data
        """
        owner = "self._parent" if has_parent else "self"
        out.write()
        out.write("@property")
        if out.indent(f"def {property_name}(self):"):
            out.write(f"data_view = og.AttributeValueHelper({owner}._attributes.{attribute_name})")

            args = []
            if self.fabric_needs_counter():
                # State attributes pre-calculate the size to be the current attribute value size
                if self.attribute_group == STATE_GROUP:
                    out.write(f"{owner}.{attribute_name}_size = data_view.get_array_size()")
                elif self.attribute_group != INPUT_GROUP:
                    args.append(f"reserved_element_count={owner}.{attribute_name}_size")
            if on_gpu:
                args.append("on_gpu=True")
                if self.cuda_pointer_type == CudaPointerValues.CPU:
                    out.write(f"data_view.gpu_ptr_kind = {CudaPointerValues.PYTHON[self.cuda_pointer_type]}")

            out.write(f"return data_view.get({', '.join(args)})")
            out.exdent()

    # ----------------------------------------------------------------------
    def __generate_python_property_set_code(
        self, attribute_name: str, property_name: str, out: IndentedOutput, on_gpu: bool, has_parent: bool = False
    ):
        """Emits the generated code implementing a property write accessor for the attribute.

        Args:
            attribute_name: Name of the attribute being accessed
            property_name: Name of the property to define for the attribute to be accessed
            out: Output location for the generated code
            on_gpu: If True then the accessor should set data pointers from GPU memory
            has_parent: If True then this is a nested accessor and it has to go to the parent for some data
        """
        owner = "self._parent" if has_parent else "self"
        attribute_member = f"{owner}._attributes.{property_name}"
        out.write()
        out.write(f"@{property_name}.setter")
        if out.indent(f"def {property_name}(self, value):"):
            # Inputs cannot be modified when locked, e.g. during a compute() call
            if self.is_read_only() and out.indent(f"if {owner}._setting_locked:"):
                # Indent this code manually relative to itself; extra indentation will be handled by the caller
                out.write(f"raise og.ReadOnlyError({attribute_member})")
                out.exdent()
            out.write(f"data_view = og.AttributeValueHelper({attribute_member})")
            args = ["value"]
            if self.memory_storage() == MemoryTypeValues.CUDA:
                args.append("on_gpu=True")
                if self.cuda_pointer_type == CudaPointerValues.CPU:
                    out.write(f"data_view.gpu_ptr_kind = {CudaPointerValues.PYTHON[self.cuda_pointer_type]}")
            out.write(f"data_view.set({', '.join(args)})")

            # The set_attr_value call will handle setting the size, keep it sychronized with the local variable
            if self.fabric_needs_counter():
                out.write(f"{owner}.{property_name}_size = data_view.get_array_size()")
            out.exdent()

    # ----------------------------------------------------------------------
    def generate_python_property_code(self, out: IndentedOutput):
        """Emits the generated code implementing a readable property for this attribute.

        The properties will take one of two forms, depending on where the attribute's memory resides.

        For hardcoded CPU or GPU versions the code will be a simple property, e.g. "db.inputs.attributeName":
            @property
            def attributeName(self):
                ...

        When the memory location is determined at runtime then a secondary level is installed to give access to
        both as either "db.inputs.attributeName.cpu" or "db.inputs.attributeName.gpu"
            class __attributeName:
                @property
                def cpu(self):
                    ...
                @property
                def gpu(self):
                    ...
            @property
                def attributeName(self):
                    return __attributeName()
        """
        property_name = self.python_property_name()
        if self.memory_storage() == MemoryTypeValues.ANY:
            out.write()
            if out.indent(f"class __{property_name}:"):
                if out.indent("def __init__(self, parent):"):
                    out.write("self._parent = parent")
                    out.exdent()
                self.__generate_python_property_get_code(property_name, "cpu", out, on_gpu=False, has_parent=True)
                self.__generate_python_property_set_code(property_name, "cpu", out, on_gpu=False, has_parent=True)
                self.__generate_python_property_get_code(property_name, "gpu", out, on_gpu=True, has_parent=True)
                self.__generate_python_property_set_code(property_name, "gpu", out, on_gpu=True, has_parent=True)
                out.exdent()
            out.write()
            out.write("@property")
            if out.indent(f"def {property_name}(self):"):
                out.write(f"return self.__class__.__{property_name}(self)")
                out.exdent()
        elif self.memory_storage() == MemoryTypeValues.CUDA:
            self.__generate_python_property_get_code(property_name, property_name, out, on_gpu=True)
            self.__generate_python_property_set_code(property_name, property_name, out, on_gpu=True)
        else:
            self.__generate_python_property_get_code(property_name, property_name, out, on_gpu=False)
            self.__generate_python_property_set_code(property_name, property_name, out, on_gpu=False)

    # ----------------------------------------------------------------------
    def __generate_python_batched_property_get_code(
        self, attribute_name: str, property_name: str, index: int, out: IndentedOutput
    ):
        """Emits the generated code implementing a property read accessor for the batched attribute.

        Args:
            attribute_name: Name of the attribute being accessed
            property_name: Name of the property to define for the attribute to be accessed
            index: Attribute index within the batch list. Used only for inputs.
            out: Output location for the generated code
        """
        out.write()
        out.write("@property")
        if out.indent(f"def {property_name}(self):"):
            if self.attribute_group == INPUT_GROUP:
                out.write(f"return self._batchedReadValues[{index}]")
            elif self.attribute_group == OUTPUT_GROUP:
                out.write(f"value = self._batchedWriteValues.get(self._attributes.{attribute_name})")
                if out.indent("if value:"):  # if value was already set...return it
                    out.write("return value")
                    out.exdent()
                if out.indent(
                    "else:"
                ):  # otherwise, we fetch it from fabric (issue discovered with OgnIntCounter and OgnCountTo)
                    out.write(f"data_view = og.AttributeValueHelper(self._attributes.{attribute_name})")
                    out.write("return data_view.get()")
                    out.exdent()
            out.exdent()

    # ----------------------------------------------------------------------
    def __generate_python_batched_property_set_code(
        self, attribute_name: str, property_name: str, index: int, out: IndentedOutput
    ):
        """Emits the generated code implementing a property write accessor for the batched attribute.

        Args:
            attribute_name: Name of the attribute being accessed
            property_name: Name of the property to define for the attribute to be accessed
            index: Attribute index within the batch list. Used only for inputs.
            out: Output location for the generated code
        """
        out.write()
        out.write(f"@{property_name}.setter")
        if out.indent(f"def {property_name}(self, value):"):
            if self.attribute_group == INPUT_GROUP:
                out.write(f"self._batchedReadValues[{index}] = value")
            elif self.attribute_group == OUTPUT_GROUP:
                out.write(f"self._batchedWriteValues[self._attributes.{attribute_name}] = value")
            out.exdent()

    # ----------------------------------------------------------------------
    def generate_python_batched_property_code(self, index: int, out: IndentedOutput):
        """Emits the generated code implementing a batched property for this attribute.

        The properties are currently only designed to read/write the data from CPU batch.

        The code will be a simple property, e.g. "db.inputs.attributeName":
            @property
            def attributeName(self):
                ...
        """
        property_name = self.python_property_name()
        self.__generate_python_batched_property_get_code(property_name, property_name, index, out)
        self.__generate_python_batched_property_set_code(property_name, property_name, index, out)

    # ----------------------------------------------------------------------
    def sdf_type_name(self) -> str:
        """Returns a string with the pxr::SdfValueTypeName of the attribute data"""
        return sdf_type_name(self.sdf_base_type(), self.tuple_count, self.array_depth > 0)

    # ----------------------------------------------------------------------
    def sdf_base_type(self) -> Optional[str]:
        """By default no SDF base type exists"""
        return

    # ----------------------------------------------------------------------
    def usd_name(self) -> str:
        """Returns a string with the name of the attribute in a USD file"""
        return self.name

    # ----------------------------------------------------------------------
    def usd_type_name(self) -> str:
        """Returns a string with the data type the attribute would use in a USD file"""
        raise ParseError(f"Attribute {self.name} has an unimplemented USD type name")

    # ----------------------------------------------------------------------
    def usd_add_arrays(self, base_type: str) -> str:
        """Common method for transforming a base USD type to add any appropriate array values"""
        return base_type + "[]" * self.array_depth

    # ----------------------------------------------------------------------
    def usd_add_containers(self, base_type: str) -> str:
        """Common method for transforming a base USD type to add any appropriate array or component values"""
        final_type = base_type
        if self.tuple_count > 1:
            final_type += str(self.tuple_count)
        return self.usd_add_arrays(final_type)

    # ----------------------------------------------------------------------
    @staticmethod
    def tuples_supported() -> List[int]:
        """Returns a list of tuple numbers supported by the attribute type, by default only single values"""
        return [1]

    # ----------------------------------------------------------------------
    @staticmethod
    def array_depths_supported() -> List[int]:
        """Returns a list of array depths supported by the attribute type, by default up to 1 level deep"""
        return [0, 1]

    # ----------------------------------------------------------------------
    @deprecated_function("All types are supported, AttributeManager.check_support should no longer be called")
    def check_support(self):  # pragma: no cover
        """Checks to see if this attribute is currently supported.

        This is different from the attribute being valid as this only raises an exception if the
        attribute is a legal type, it just hasn't had proper code generation added for it yet.

        Raises:
            AttributeError: If any attributes on the node are currently not supported
        """
        # This is the limit of values for the tuple in the C++ implementation of the array type
        if self.tuple_count > 255 or self.tuple_count < 1:
            raise AttributeError(f"Element count {self.tuple_count} is not in the allowed range of 1 - 255")

        # This is the limit of array depth support in the Fabric
        if self.array_depth not in self.array_depths_supported():
            raise UnimplementedError(
                f"Array depth of {self.array_depth} for attribute type"
                f" {self.cpp_base_type_name()} not in supported list {self.array_depths_supported()}"
            )

        # Certain types only support a limited subset of tuple counts (for now), check those here
        if self.tuple_count not in self.tuples_supported():
            raise UnimplementedError(
                f"Tuple count of {self.tuple_count} for attribute type"
                f" {self.cpp_base_type_name()} not in supported list {self.tuples_supported()}"
            )

        if self.unimplemented_error is not None:
            error = self.unimplemented_error
            self.unimplemented_error = None
            raise UnimplementedError(error)

    # ----------------------------------------------------------------------
    def requires_default(self):
        """Returns True if this type of attribute needs a default value"""
        return self.is_required and self.default is None and self.is_read_only()

    # ----------------------------------------------------------------------
    def validate_configuration(self, pedantic: bool = False):
        """Validate that the current state of the object is legal for use

        Args:
            pedantic: If True then be more fussy than usual when checking the configuration

        Raises:
            ParseError if the current configuration is missing mandatory information or has illegal values
        """
        for key in AttributeKeys.MANDATORY:
            if not hasattr(self, key):
                raise ParseError(f"Attribute type is missing mandatory parameter {key}")
        if not hasattr(self, "OGN_TYPE") and not hasattr(self, "roles"):
            raise ParseError("Attribute type must have OGN_TYPE or roles() method")

        # Default values must have compatible type structures
        if self.default is not None:
            try:
                self.validate_value_structure(self.default)
            except UnimplementedError as error:
                # If something is unimplemented there may be further processing to do so note it and move on
                self.unimplemented_error = error
        elif self.requires_default():
            raise ParseError(f'Default value is mandatory for required attribute "{self.name}"')

        if pedantic:
            errors = validate_description(self.description)
            if errors:
                for error in errors:
                    logger.warning("[PEDANTIC] for attribute %s - %s", self.name, str(error))
        # Empty descriptions are anti-social
        elif not self.description:
            warning = f"Attribute '{self.name}' description should not be empty"
            if os.getenv("OGN_STRICT_DEBUG"):
                raise ParseError(warning)
            logger.warning(warning)

        # Memory type must be legal
        if self.memory_type not in MemoryTypeValues.ALL:
            raise ParseError(f"Memory type {self.memory_type} not in legal list {MemoryTypeValues.ALL}")

        # The "allowedTokens" metadata is not allowed on non-token attribute types
        if self.metadata.get(MetadataKeys.ALLOWED_TOKENS, None) and not hasattr(self, "get_allowed_tokens"):
            raise ParseError(
                f"Attribute {self.name} of type {self.ogn_type()} cannot have {MetadataKeys.ALLOWED_TOKENS} metadata"
            )

        # The GPU pointer kind information is intentionally not part of the attribute so add it to metadata.
        if self.cuda_pointer_type == CudaPointerValues.CPU:
            self.metadata[MetadataKeys.CUDA_POINTERS] = CudaPointerValues.CPU

    # ----------------------------------------------------------------------
    def validate_default(self):
        """Check that the default is a legal value, making any implicit changes required to make it so if needed

        Raises:
            ParseError: If the default was not a legal value
        """
        try:
            self.validate_value_structure(self.default)
        except ParseError as error:
            raise ParseError(f"Failed validation of default {self.default} on {self.name}") from error

    # ----------------------------------------------------------------------
    def validate_value(self, value):
        """Raises a ParseError if value is not legal value; never happens in the base class

        This only checks a single value for the attribute type, not things like arrays of values or elements.
        For those checks call validate_value_structure().
        """

    # ----------------------------------------------------------------------
    def validate_value_structure(self, value_to_validate):
        """Validate a value being set on the attribute.

        This checks to make sure there is a match between the structure of the value and that expected by the
        attribute type. (e.g that float[3] contains 3 values, all floats). For a single value check that only
        verifies matching simple data type use validate_value()

        Raises:
            ParseError if the value to validate was not compatible with this attribute type
        """
        legal_level_counts = [0] * self.array_depth
        if isinstance(value_to_validate, list):
            if not legal_level_counts and self.tuple_count < 2:
                raise ParseError(f'Value of simple attribute "{self.name}" cannot be an array')
        elif legal_level_counts or self.tuple_count > 1:
            raise ParseError(
                f"Value {value_to_validate} of type {type(value_to_validate)} on "
                f'multiple-element attribute "{self.name}" must be an array'
            )

        self.validate_value_nested(value_to_validate, legal_level_counts)

    # ----------------------------------------------------------------------
    def validate_value_nested(self, array_data: List, array_levels: List[int]):
        """Validate that the given data matches an array of this attribute's type

        Args:
            array_data: List of data elements to validate.
            array_levels: List of number of members allowed in nested arrays. 0 means any number.
                          Until this is [] the members of array_data must themselves be lists.

        Raises:
            ParseError if the structure of the data does not match the structure and values of the attribute
        """
        if not array_levels:
            self.validate_value(array_data)
        else:
            if array_levels[0] > 0 and len(array_data) != array_levels[0]:
                raise ParseError(f"Attribute {self.name} default expects {array_levels[0]} elements")
            for data in array_data:
                self.validate_value_nested(data, array_levels[1:])

    # ----------------------------------------------------------------------
    def parse_extra_properties(self, property_set: dict) -> PropertySet:
        """Parse any extra properties specific to certain attribute types

        Args:
            property_set: (NAME, VALUE) for properties the attribute type might support
        """
        # Base class does not recognize any extra properties, that's what makes them "extra"
        return property_set

    # ----------------------------------------------------------------------
    def parse_metadata(self, metadata: Dict[str, Any]):
        """Parse the metadata attached to the attribute type.
        Overrides to this method can add additional interpretation of special metadata.
        """
        self.metadata.update(get_metadata_dictionary(metadata))

    # ----------------------------------------------------------------------
    def python_value(self, value):
        """Returns the value of this attribute in a Python-compatible format, None for no default."""
        return value

    # ----------------------------------------------------------------------
    def python_value_as_repr(self, value):
        """Returns the value of this attribute in a format that prints as something that can be assigned."""
        return self.python_value_as_str(value)

    # ----------------------------------------------------------------------
    def python_value_as_str(self, value):
        """Returns the value of this attribute in a Python-compatible format, None for no default."""
        return str(value)

    # ----------------------------------------------------------------------
    def value_for_test(self, value):
        """Returns the value of this attribute in a format suitable for test output, None for no default."""
        return self.python_value(value)

    # ----------------------------------------------------------------------
    def generate_python_validation(self, out: IndentedOutput):
        """Adds any code required to validate the value of an attribute before a Python compute method is called"""
        return

    # ----------------------------------------------------------------------
    def usd_element(self, element, bare: bool = False) -> str:
        """Get the value of a single USD element as a string (e.g. float, int, string, token... no arrays or tuples)"""
        # Strings inside arrays will already be quoted so only add quotes if the element is "bare" (i.e. by itself)
        if isinstance(element, str):
            return to_usd_str(element, bare)

        if isinstance(element, bool):
            return "true" if element else "false"

        if isinstance(element, (int, float)):
            return element

        return element

    # ----------------------------------------------------------------------
    def usd_value(self, value):
        """Returns the current default value of this attribute in a USD-compatible format, None for no default."""
        if value is None:
            return None
        if self.array_depth > 0:
            if not isinstance(value, list):
                raise ParseError(f"Expected list for USD array value on {self.name} - got {value}")
            array_output = []
            if self.tuple_count > 1:
                for element in value:
                    if len(element) != self.tuple_count:
                        raise ParseError(f"USD value expected tuple[{self.tuple_count}] - got {element}")
                    array_output.append(tuple(self.usd_element(child) for child in element))
            else:
                array_output = [self.usd_element(child) for child in value]
            return array_output
        if self.tuple_count > 1:
            return tuple(self.usd_element(child) for child in value)
        return self.usd_element(value, bare=True)

    # ----------------------------------------------------------------------
    def usd_default_value(self):
        """Returns the current default value of this attribute in a USD-compatible format, None for no default."""
        if self.default is None:
            return ""
        return f" = {self.usd_value(self.default)}"

    # ----------------------------------------------------------------------
    def emit_usd_declaration(self, out) -> List[str]:
        """Print a declaration for this attribute in USD

        Args:
            out: Output handler where the USD will be emitted
        """
        try:
            usd_name = self.usd_name()
            usd_type = self.usd_type_name()
        except ParseError:
            # Attributes without USD representations can be skipped
            return

        docs = to_usd_docs(self.description)

        default_value = self.usd_default_value()
        if out.indent(f"custom {usd_type} {usd_name}{default_value} ("):
            out.write(docs)
            out.exdent(")")

    # ----------------------------------------------------------------------
    def tuple_argument(self):
        """Return a string with the declaration of a tuple count argument for constructors"""
        tuple_count_arg = "" if self.tuple_count < 2 else f", {self.tuple_count}"
        return tuple_count_arg

    # ----------------------------------------------------------------------
    def cpp_element_value(self, value) -> str:
        """Return a string with the simple Python 'value' translated to the C++ equivalent as an initializer.
        This method assumes the value is not a list, which should be handled in cpp_constructor_value or
        cpp_tuple_value.

        Args:
            value: Python value to convert - e.g. True -> "true"

        Raises:
            ParseError: The derived classes must override this method to provide a value of the correct format
        """
        if isinstance(value, list):
            raise ParseError(f"Initializer of non-array non-tuple should not be a list : {self.name} = {value}")
        raise ParseError(f"Attribute manager {self} failed to override cpp_element_value()")

    # ----------------------------------------------------------------------
    def cpp_tuple_value(self, value) -> str:
        """Return a string with the simple Python 'value' translated to the C++ equivalent as an initializer.
        This method checks to make sure the list elements match the tuple count, if any.

        Args:
            value: Python value to convert - e.g. True -> "true"

        Raises:
            ParseError: The derived classes must override this method to provide a value of the correct format
        """
        if self.tuple_count > 1:
            if not isinstance(value, list):
                raise ParseError(f"Tuple initialization expected list[{self.tuple_count}], got '{value}'")
            if len(value) != self.tuple_count:
                raise ParseError(f"Tuple count initializer expected list of size {self.tuple_count}, got `{value}`")
            return f"{{{','.join([self.cpp_element_value(element) for element in value])}}}"

        if isinstance(value, list):
            raise ParseError(f"Initializer of non-array non-tuple should not be a list : {self.name} = {value}")

        return self.cpp_element_value(value)

    # ----------------------------------------------------------------------
    def cpp_constructor_value(self, value) -> str:
        """Return a string with the Python 'value' translated to the C++ equivalent as an initializer

        This recurses to handle arrays and tuples. For example an array of float[2] would look like this in Python:
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
        and this in C++
            {{1.0f, 2.0f}, {3.0f, 4.0f}, {5.0f, 6.0f}}

        Args:
            value: Python value to convert - e.g. True -> "true", [] -> {}

        Returns:
            A string representing the given values in C++ form
        """
        if value is None:
            return None

        if self.array_depth > 0:
            # Empty array is treated the same as no default array
            if not value:
                return None
            if not isinstance(value, list):
                raise ParseError(f"Array initialization expected list, got '{value}'")
            return f"{{{','.join([self.cpp_tuple_value(element) for element in value])}}}"

        return self.cpp_tuple_value(value)

    # ----------------------------------------------------------------------
    def cpp_default_initializer(self):
        """Returns the current default value of this attribute in a C++-compatible format, None for no default."""
        try:
            raw_value = self.cpp_constructor_value(self.default)
        except ParseError:
            return None
        array_length = len(self.default) if isinstance(self.default, list) else 0

        if self.array_depth > 0:
            # Empty or missing array defaults must still initialize to an empty array
            if raw_value is None or raw_value == "{}":
                raw_value = "nullptr"
                array_length = 0
            else:
                array_member_type = self.fabric_default_data_typedef().replace("*", "")
                raw_value = f"std::array<{array_member_type}, {array_length}>{{{raw_value}}}.data()"
        if raw_value is None:
            return None

        # Array construction must include the number of elements in the array
        array_count_arg = f", {array_length}" if self.array_depth > 0 else ""
        return f"{raw_value}{array_count_arg}"

    # ----------------------------------------------------------------------
    def is_required_as_string(self):
        """Return the C++ version of true/false that tells if this attribute is required"""
        return "true" if self.is_required else "false"

    # ----------------------------------------------------------------------
    def cpp_variable_name(self, use_namespace: bool = False) -> str:
        """Return the name of the attribute in a form suitable for use as a C++ variable name.

        No attempt is made to remove the cases where an attribute has a keyword name. That is left
        up to the calling code if necessary.

        Args:
            use_namespace: If True then include "inputs:" or "outputs:" as part of the name
        """
        clean_name = self.name if use_namespace else self.base_name
        clean_name = clean_name.replace(":", "_")
        return clean_name

    # ----------------------------------------------------------------------
    def empty_value(self) -> Any:
        """Returns an empty value compatible with the current attribute type"""
        if self.array_depth == 1:
            return []
        base_value = self.empty_base_value()
        return [base_value] * self.tuple_count if self.tuple_count > 1 else base_value

    # ----------------------------------------------------------------------
    def empty_base_value(self) -> Any:
        """Attribute types must define their single empty value"""
        raise UnimplementedError(f"Attribute {self.name} of type {self.attribute_type_name} has no empty value")
