# noqa: PLC0302
"""Support for generating C++ interface code for OmniGraph Nodes."""
import json
from contextlib import suppress
from itertools import zip_longest
from pathlib import Path
from typing import List, Optional

from ..deprecate import DeprecateMessage
from .attributes.AttributeManager import AttributeManager
from .attributes.management import list_without_runtime_attributes, split_attribute_list
from .attributes.naming import INPUT_GROUP, INPUT_NS, OUTPUT_GROUP, OUTPUT_NS, STATE_GROUP, STATE_NS, namespace_of_group
from .keys import MemoryTypeValues
from .nodes import NodeInterfaceGenerator
from .utils import (
    OMNI_GRAPH_CORE_EXTENSION,
    GeneratorConfiguration,
    MetadataKeyOutput,
    MetadataKeys,
    NameManager,
    ParseError,
    logger,
    to_cpp_comment,
    to_cpp_str,
)

__all__ = ["generate_cpp"]


# ======================================================================
def grouper(iterable, max_size: int):
    """Returns the iterable decomposed into iterables of size "max_size", filling any excess with None"""
    args = [iter(iterable)] * max_size
    return zip_longest(*args, fillvalue=None)


# ======================================================================
class NodeCppGenerator(NodeInterfaceGenerator):
    """Manage the functions required to generate a C++ interface for a node

    Attributes:
        declarations: List of declarations that need to appear after include files but before code
        __name_manager: Manager for unique name shortening for unimportant internal generated names
        include_files: List of includes that need to appear at the top of the header file
    """

    def __init__(self, configuration: GeneratorConfiguration):
        """Set up the generator and output the C++ interface code for the node

        Args:
            configuration: Information used to configure the output
        """
        super().__init__(configuration)
        self.declarations = []
        self.preamble_code = []
        self.__name_manager = NameManager()
        self.__needs_initialize = None
        self.__has_deprecated_attributes = None

    # ----------------------------------------------------------------------
    def __calculate_per_attribute_flags(self):
        """Calculate the flags used to determine whether any attributes meet a certain criteria.
        Only call this after all parsing has completed.
        """
        if self.__needs_initialize is None:
            all_attributes = self.node_interface.all_input_attributes()
            all_attributes += self.node_interface.all_output_attributes()
            all_attributes += self.node_interface.all_state_attributes()
            self.__needs_initialize = False
            self.__has_deprecated_attributes = False
            for attribute in all_attributes:
                if attribute.is_deprecated:
                    self.__has_deprecated_attributes = True
                if attribute.metadata or not attribute.is_required or attribute.is_deprecated:
                    self.__needs_initialize = True

    @property
    def needs_initialize(self) -> bool:
        self.__calculate_per_attribute_flags()
        return self.__needs_initialize

    @property
    def has_deprecated_attributes(self) -> bool:
        self.__calculate_per_attribute_flags()
        return self.__has_deprecated_attributes

    # ----------------------------------------------------------------------
    def nm(self, variable_name: str) -> str:
        """Returns unique, possibly shortened version of the unique variableName"""
        return self.__name_manager.name(variable_name)

    # ----------------------------------------------------------------------
    def database_class_name(self):
        """Returns the name of the generated database class"""
        return f"{self.base_name}Database"

    # ----------------------------------------------------------------------
    def state_manager_name(self):
        """Returns the name of the static object that will be the state manager for this node type"""
        return f"sm_stateManager{self.base_name}"

    # ----------------------------------------------------------------------
    def generator_version_name(self):
        """Returns the name of the static object that will hold the code generator version used for this node type"""
        return f"sm_generatorVersion{self.base_name}"

    # ----------------------------------------------------------------------
    def target_version_name(self):
        """Returns the name of the static object that will hold the code target version used for this node type.
        The code target version is the version of omni.graph.core for which the code was generated.
        """
        return f"sm_targetVersion{self.base_name}"

    # ----------------------------------------------------------------------
    def interface_file_name(self) -> str:
        """Return the path to the name of the header file"""
        return f"{self.database_class_name()}.h"

    # ----------------------------------------------------------------------
    def pre_interface_generation(self):
        """Create the header information independent of the node itself"""
        self.preamble_code.append("#include <carb/InterfaceUtils.h>")
        self.preamble_code.append("#include <omni/graph/core/NodeTypeRegistrar.h>")
        self.preamble_code.append("#include <omni/graph/core/iComputeGraph.h>")
        self.preamble_code.append("#include <omni/graph/core/CppWrappers.h>")
        self.preamble_code.append("#include <omni/fabric/Enums.h>")
        self.preamble_code.append("using omni::fabric::PtrToPtrKind;")
        if self.extension == OMNI_GRAPH_CORE_EXTENSION:
            self.preamble_code.append('#include "Token.h"')
        self.preamble_code.append("#include <map>")
        self.preamble_code.append("#include <vector>")
        self.preamble_code.append("#include <tuple>")
        self.preamble_code.append("#include <omni/graph/core/OgnHelpers.h>")
        if self.node_interface.icon_path:
            self.preamble_code.append("#include <carb/tokens/TokensUtils.h>")
        self.add_attribute_type_setup()

    # ----------------------------------------------------------------------
    def get_file_inclusions(self) -> str:
        """Return code with the discovered include files in an order that makes sense"""
        pxr_includes = []
        regular_includes = []

        if self.node_interface.scheduling_hints is not None:
            regular_includes += self.node_interface.scheduling_hints.cpp_includes_required()

        if self.has_deprecated_attributes:
            regular_includes.append("#include <omni/graph/core/IInternal.h>")

        # Partition the files into those included from USD and those not. By doing this the
        # warnings that including USD files can be harmlessly silenced.
        for include_file in self.preamble_code:
            if include_file.find("/ogn/UsdTypes.h") < 0:
                regular_includes.append(include_file)
            else:
                pxr_includes.append(include_file)

        # Poor include practices make it necessary to include the pxr information used by Graph.h just
        # to include the definition of the direct IToken interface, needed since accessing it indirectly
        # causes complaints from carb::Framework::tryAcquireInterface().
        if self.extension == OMNI_GRAPH_CORE_EXTENSION:
            pxr_includes.append("#include <omni/graph/core/PreUsdInclude.h>")
            pxr_includes.append("#include <pxr/usd/sdf/path.h>")
            pxr_includes.append("#include <pxr/usd/usd/stage.h>")
            pxr_includes.append("#include <pxr/usd/usd/prim.h>")
            pxr_includes.append("#include <omni/graph/core/PostUsdInclude.h>")

        if pxr_includes:
            # The namespace makes USD access easier, and it's used everywhere already
            pxr_includes.append("using namespace pxr;\n")

        return "\n".join(pxr_includes + regular_includes)

    # ----------------------------------------------------------------------
    def post_interface_generation(self):
        """Insert the file header information, now that it is known"""
        header = "#pragma once\n\n"
        # Protect the CPU and CUDA code so that the include file only gets one set of definitions.
        # Doing it this way rather than generating two files keeps the include rules simple.
        if self.node_interface.has_cuda_attributes:
            header += "#ifndef __CUDACC__\n"
        header += self.get_file_inclusions()
        header += "\n"
        header += "\n".join(self.declarations)

        with suppress(KeyError):
            categories = json.dumps(self.node_interface.metadata[MetadataKeys.CATEGORIES]).lower()
            if "graph:prerender" in categories:
                header += "#include <omni/graph/core/GpuInteropEntryUserData.h>\n"
                header += "#include <carb/cudainterop/CudaInterop.h>\n"
            if "graph:postrender" in categories:
                header += "#include <omni/graph/image/unstable/ComputeParamsBuilder.h>\n"

        header += "\n"

        self.out.prepend(header)
        if self.node_interface.has_cuda_attributes:
            self.out.write("#else")
            self.generate_cuda_code()
            self.out.write("#endif")

    # ----------------------------------------------------------------------
    def generate_registration_macro(self):
        """Generate the macro that will be called after the node definition to create the registration manager.
        This has to be done in two steps like this since the macro will reference code that performs a template-based
        introspection on the node class, which can only happen after it has been defined.

        This relies on instantiation of the OgnHelpers.h macros "DECLARE_OGN_NODES()" and "INITIALIZE_OGN_NODES()"
        in the proper spots.
        """
        template_args = ", ".join([self.base_name, self.database_class_name()])
        constructor_args = ", ".join(
            [f'"{self.node_interface.name}"', f"{self.node_interface.version}", f'"{self.extension}"']
        )

        self.out.write("#define REGISTER_OGN_NODE() \\")
        if self.out.indent("namespace { \\"):
            self.out.write(f"ogn::NodeTypeBootstrapImpl<{template_args}> s_registration({constructor_args}); \\")
            self.out.exdent()
        self.out.write("}")

    # ----------------------------------------------------------------------
    def add_attribute_type_setup(self):
        """Write out the code to generate the include files used by all attributes.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        # Required include files and declarations have to be first
        includes = []
        declarations = []
        for input_attribute in self.node_interface.all_input_attributes():
            includes += input_attribute.cpp_includes()
            declarations += input_attribute.cpp_declarations()
        for output_attribute in self.node_interface.all_output_attributes():
            includes += output_attribute.cpp_includes()
            declarations += output_attribute.cpp_declarations()
        for state_attribute in self.node_interface.all_state_attributes():
            includes += state_attribute.cpp_includes()
            declarations += state_attribute.cpp_declarations()
        self.preamble_code += [f"#include <{include_file}>" for include_file in sorted(set(includes))]
        if declarations:
            self.preamble_code += sorted(set(declarations))

    # ----------------------------------------------------------------------
    def generate_registration(self):
        """Write out the code to register the node.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        self.out.write(
            f'REGISTER_NODE_TYPE({self.base_name}, "{self.node_interface.name}", {self.node_interface.version})'
        )

    # ----------------------------------------------------------------------
    def generate_attribute_static_data(self):
        """Generate the code required to create the static data structures for unchanging parts of the attributes."""
        # Namespace it to create file-local objects with easy access
        self.out.write(f"namespace {self.base_name}Attributes")
        self.out.write("{")

        def generate_static_attributes(attribute_list: List[AttributeManager], attribute_group: str):
            """Helper function that generates the static attribute support classes for all attributes in the list

            Args:
                attribute_list: List of attributes to generate
                attribute_group: Enum with the attribute's group (input, output, or state)
            """
            namespace = namespace_of_group(attribute_group)
            self.out.write(f"namespace {namespace}")
            self.out.write("{")
            for attribute in attribute_list:
                self.out.write(attribute.cpp_typedef_definitions())
                (_initializer_name, initializer_declaration) = attribute.cpp_initializer()
                self.out.write(initializer_declaration)
            self.out.write("}")

        generate_static_attributes(self.node_interface.all_input_attributes(), attribute_group=INPUT_GROUP)
        generate_static_attributes(self.node_interface.all_output_attributes(), attribute_group=OUTPUT_GROUP)
        generate_static_attributes(self.node_interface.all_state_attributes(), attribute_group=STATE_GROUP)

        self.out.write("}")
        self.out.write(f"using namespace {self.base_name}Attributes;")

    # ----------------------------------------------------------------------
    def generate_attribute_accessors(self, attribute_list: List[AttributeManager], attribute_group: str):
        """Write out the code to create the declarations of the attribute accessor pointers.

        Args:
            attribute_list: List of attributes on the node of that type
            attribute_group: Enum with the attribute's group (input, output, or state)

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        # If no attributes of this type then the type will not be referenced and does not need generating
        if not attribute_list:
            return

        namespace = namespace_of_group(attribute_group)

        self.out.write()

        typename = namespace + "T"

        if self.out.indent("struct " + typename + " {"):
            self.out.write(typename + "(size_t const& offset)")
            first = True
            for attribute in attribute_list:
                if first:
                    ctor = ": "
                    first = False
                else:
                    ctor = ", "
                ctor += attribute.cpp_variable_name()
                ctor += "{"
                ctor += ",".join(attribute.datamodel_accessor_constructor_args())
                ctor += "}"
                self.out.write(ctor)

            self.out.write("{}")

            # The accessible structures are the wrappers through which the data will be accessed. They will
            # all have an operator() to access the data type directly, and may have other convenience methods
            # for managing things like iterating, resizing, copying, etc.
            for attribute in attribute_list:
                self.out.write(attribute.datamodel_accessor_declaration())

            self.out.exdent(f"}} {namespace};")

    # ----------------------------------------------------------------------
    def generate_attribute_constructors(self, attribute_list: List[AttributeManager], attribute_group: str):
        """Write out the code to create the constructors of the attribute accessor pointers.

        Args:
            attribute_list: List of attributes
            attribute_group: Enum with the attribute's group (input, output, or state)

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        # If no attributes of this type then the type will not be referenced and does not need generating
        if not attribute_list:
            return

        namespace = namespace_of_group(attribute_group)

        ctor = ", " + namespace + "{m_offset.index}"
        self.out.write(ctor)

    # ----------------------------------------------------------------------
    def write_n_per_line(self, list_to_write: List[str], stride: int):
        """Write out a comma-separated list with "stride" elements per line

        There is no filling of extra entries, or quoting of the provided strings, so writing out a list of the
        string names for [1, 10] by fours would be:
            one, two, three, four,
            five, six, seven, eight,
            nine, ten

        Args:
            list_to_write: List of strings to split out into smaller sublists per line
            stride: Number of elements per line
        """
        list_size = len(list_to_write)
        suffix = ","
        for i in range(0, list_size, stride):
            if i + stride >= list_size:  # Avoid the trailing comma on the last line
                suffix = ""
            self.out.write(f"{', '.join(list_to_write[i:i + stride])}{suffix}")

    # ----------------------------------------------------------------------
    def get_attributes_by_memory_type(self, attribute_group: str):
        """Return a trio of attribute lists, partitioned by the type of memory their data occupies.

        Args:
            attribute_group: Enum with the attribute's group (input, output, or state)

        Returns:
            (cpu_attributes,  : List of attributes exclusively living on the CPU
             cuda_attributes, : List of attributes exclusively living on the GPU in CUDA format
             any_attributes)  : List of attributes that may live in either location
        """
        if attribute_group == INPUT_GROUP:
            attributes = self.node_interface.all_input_attributes()
        elif attribute_group == OUTPUT_GROUP:
            attributes = self.node_interface.all_output_attributes()
        else:
            attributes = self.node_interface.all_state_attributes()
        cpu_attributes = [attribute for attribute in attributes if attribute.memory_storage() == MemoryTypeValues.CPU]
        cuda_attributes = [attribute for attribute in attributes if attribute.memory_storage() == MemoryTypeValues.CUDA]
        any_attributes = [attribute for attribute in attributes if attribute.memory_storage() == MemoryTypeValues.ANY]
        return (cpu_attributes, cuda_attributes, any_attributes)

    # ----------------------------------------------------------------------
    # Enum for the types of handles for which to generate extraction code
    HANDLE_INPUT = 0
    HANDLE_INPUT_BUNDLE = 1
    HANDLE_OUTPUT = 2
    HANDLE_OUTPUT_BUNDLE = 3
    HANDLE_STATE = 4
    HANDLE_STATE_BUNDLE = 5
    # List of (get_method, handle_type, handle_object, namespace) for each type of method.
    HANDLE_TABLE = {
        HANDLE_INPUT: ("getAttributesR", "ConstAttributeDataHandle", "inputDataHandles", INPUT_NS),
        HANDLE_INPUT_BUNDLE: ("getAttributesR", "ConstAttributeDataHandle", "inputDataBundleHandles", INPUT_NS),
        HANDLE_OUTPUT: ("getAttributesW", "AttributeDataHandle", "outputDataHandles", OUTPUT_NS),
        HANDLE_OUTPUT_BUNDLE: ("getAttributesW", "AttributeDataHandle", "outputBundleDataHandles", OUTPUT_NS),
        HANDLE_STATE: ("getAttributesW", "AttributeDataHandle", "stateDataHandles", STATE_NS),
        HANDLE_STATE_BUNDLE: ("getAttributesW", "AttributeDataHandle", "stateBundleDataHandles", STATE_NS),
    }
    # Runtime attribute type correspondences
    # (accessor_method, handle_type, wrapper_type, namespace, access type, is_const_cast required to reset)
    RUNTIME_TABLE = {
        HANDLE_INPUT: ("getConstAttributeDataHandle", "ConstAttributeDataHandle", INPUT_NS, True),
        HANDLE_OUTPUT: ("getAttributeDataHandle", "AttributeDataHandle", OUTPUT_NS, False),
        HANDLE_STATE: ("getAttributeDataHandle", "AttributeDataHandle", STATE_NS, False),
    }

    # ----------------------------------------------------------------------
    def write_attrib_metadata(self, attribute: AttributeManager):
        """Write attribute metadata"""
        for key_raw, value_raw in attribute.metadata.items():
            cpp_key = MetadataKeyOutput.cpp_name_from_key(key_raw)
            if cpp_key is None:
                # Run it through json to handle escaping the quotes
                cpp_key = json.dumps(key_raw)
            # Handle lists of strings or just strings
            if isinstance(value_raw, list):
                value = '"' + ",".join([x.replace('"', '\\"') for x in value_raw]) + '"'
            else:
                value = json.dumps(value_raw)
            self.out.write(f"attr.iAttribute->setMetadata(attr, {cpp_key}, {value});")

    # ----------------------------------------------------------------------
    def __generate_data_handles(
        self, attributes: list, group_index, handle_type: int, check_if_handle_required: bool = False
    ):
        """Shared code to initialize data handles for all types of attributes

        Args:
            attributes: List of attributes for which to generate the handles
            group_index: Index of this handle group among all others with the same types
            handle_type: Enumerated value used to switch the methods and data members generated
            check_if_handle_required: If True do a more expensive check to see if the handle needs to be generated
        """
        if not attributes:
            return

        handle_data = self.HANDLE_TABLE[handle_type]

        # The grouping operation might have left Nones in the list - prune them out to make later code more clear
        actual_attributes = [attribute for attribute in attributes if attribute is not None]
        if not actual_attributes:
            return

        # Example of line generated here for two input attributes:
        #   auto inputDataHandles = getAttributesR<
        #       ConstAttributeDataHandle, ConstAttributeDataHandle
        #       >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
        #           inputs::attribute1.m_token, inputs::attribute2.m_token
        #       )
        #   );

        self.out.indent(f"auto {handle_data[2]}{group_index} = {handle_data[0]}<")
        # The template arguments require one handle type per attribute in the tuple (written 4 per line for clarity)
        self.write_n_per_line([handle_data[1]] * len(actual_attributes), 4)
        self.out.indent(">(contextObj, nodeObj.nodeContextHandle, std::make_tuple(")
        # The token arguments are the names of the attribute token declared earlier
        tokens = [f"{handle_data[3]}::{attribute.cpp_variable_name()}.m_token" for attribute in actual_attributes]
        self.write_n_per_line(tokens, 4)
        self.out.exdent(")")
        # The "kAccordingToContextIndex" is for the relative instance index. OGN DB are always created for the current active instance
        self.out.exdent(", kAccordingToContextIndex);")

    # ----------------------------------------------------------------------
    def generate_input_array_extraction(self, input_attributes: list, group_index, handle_type: int):
        """Generate the code to extract the information of the input array attributes' data in Fabric.

        This presumes all handles were stored locally in the tuple named in the handle table entry.

        Args:
            input_attributes: List of input attributes
            group_index: Which of the subgroupings of attributes is this?
            handle_type: HANDLE_* index indicating which type of attribute is being generated
        """
        if not input_attributes:
            return

        actual_attributes = list_without_runtime_attributes(input_attributes)
        if not actual_attributes:
            return

        (_, _, handle_name, namespace) = self.HANDLE_TABLE[handle_type]

        # All of the attributes that are array types need to manage a counter pointer since that's how Fabric
        # knows how big the data is.
        for index, attribute in enumerate(actual_attributes):
            accessor_name = f"{namespace}.{attribute.cpp_variable_name()}"
            extract_handle = f"std::get<{index}>({handle_name}{group_index})"
            self.out.write(f"{accessor_name}.setContext(contextObj);")
            self.out.write(f"{accessor_name}.setHandle({extract_handle});")

    # ----------------------------------------------------------------------
    def generate_writable_array_extraction(self, attributes: list, group_index: int, handle_type: int):
        """Generate the code to extract the information of the writable array attributes in Fabric.

        Args:
            attributes: List of writable attributes for which to extract pointers
            group_index: Which of the subgroupings of attributes is this?
            handle_type: HANDLE_* index indicating which type of attribute is being generated
        """
        if not attributes:
            return

        # Writable attributes need a definite type to be extracted here. Others will be extracted on demand.
        actual_attributes = list_without_runtime_attributes(attributes)
        if not actual_attributes:
            return

        (_, _, handle_name, namespace) = self.HANDLE_TABLE[handle_type]

        # All of the attributes that are array types need to manage a counter pointer since that's how Fabric
        # knows how big the data is. They also have to keep track of the context and handle to allow for resizing,
        # which would modify the Fabric memory locations.
        for index, attribute in enumerate(actual_attributes):
            accessor_name = f"{namespace}.{attribute.cpp_variable_name()}"
            extract_handle = f"std::get<{index}>({handle_name}{group_index})"
            self.out.write(f"{accessor_name}.setContext(contextObj);")
            self.out.write(f"{accessor_name}.setHandle({extract_handle});")

    # ----------------------------------------------------------------------
    def generate_writable_bundle_extraction(self, attributes: list, group_index: int, handle_type: int):
        """Generate the code to extract information of bundle-type writable attributes'

        Args:
            attributes: List of output attributes for which to setup output bundles
            handle_type: HANDLE_* index indicating which type of attribute is being generated
        """
        if not attributes:
            return

        # The grouping operation might have left Nones in the list - prune them out to make later code more clear
        actual_attributes = [attribute for attribute in attributes if attribute is not None]
        if not actual_attributes:
            return

        (_, _, handle_name, namespace) = self.HANDLE_TABLE[handle_type]

        for index, attribute in enumerate(actual_attributes):
            accessor_name = f"{namespace}.{attribute.cpp_variable_name()}"
            extract_handle = f"std::get<{index}>({handle_name}{group_index})"
            self.out.write(f"{accessor_name}.setContext(contextObj);")
            self.out.write(f"{accessor_name}.setHandle({extract_handle});")

    # ----------------------------------------------------------------------
    def generate_runtime_attribute_initialization(self, attributes: list, handle_type: int):
        """Generate the code to generate the initialization of runtime attributes' data from Fabric.

        Args:
            attributes: List of output attributes for which to extract pointers
            group_index: Which of the subgroupings of attributes is this?
            handle_type: HANDLE_* index indicating which type of attribute is being generated
        """
        (handle_accessor, handle_type, namespace, requires_const_cast) = self.RUNTIME_TABLE[handle_type]

        # Example lines generated here for two attributes, sharing temporary attributes per attribute type in order
        # to avoid naming conflicts and support the different methods and classes different attribute types require.
        # {
        #     AttributeObj __a;
        #     ConstAttributeDataHandle __h;
        #     __a = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::floatOrToken.m_token);
        #     __h = __a.iAttribute->getConstAttributeDataHandle(__a, kAccordingToContextIndex);
        #     const_cast<ogn::RuntimeAttribute<ogn::kInput, ogn::kCpu>&>(inputs.m_floatOrToken).reset(contextObj, __h);
        #
        #     __a = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::boolOrFloat.m_token);
        #     __h = __a.iAttribute->getConstAttributeDataHandle(__a, kAccordingToContextIndex);
        #     const_cast<ogn::RuntimeAttribute<ogn::kInput, ogn::kCpu>&>(inputs.m_boolOrFloat).reset(contextObj, __h);
        # }
        declaration = [
            f"{handle_type} __h;",
            "AttributeObj __a;",
        ]
        for attribute in attributes:
            if attribute is not None:
                # Only write the declaration if there is at least one attribute to process
                if declaration is not None:
                    self.out.indent("{")
                    self.out.write(declaration)
                    declaration = None
                member = f"{namespace}::{attribute.cpp_variable_name()}"
                self.out.write(f"__a = nodeObj.iNode->getAttributeByToken(nodeObj, {member}.m_token);")
                self.out.write(f"__h = __a.iAttribute->{handle_accessor}(__a, kAccordingToContextIndex);")
                attr_object = f"{namespace}.{attribute.cpp_variable_name()}()"
                if attribute.array_depth == 0:
                    if requires_const_cast:
                        accessor_type = (
                            f"ogn::RuntimeAttribute<{attribute.attribute_group},"
                            f" {MemoryTypeValues.CPP[attribute.memory_type]}>"
                        )
                        attr_object = f"const_cast<typename std::remove_const_t<{accessor_type}&>>({attr_object})"
                    self.out.write(f"{attr_object}.reset(contextObj, __h, __a);")
                else:
                    raise ParseError("Arrays not yet supported on runtime attributes")
                self.out.write()
        if declaration is None:
            self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_dynamic_attribute_initialization(self):
        # Generates the method calls to initialize the dynamic inputs, outputs, and states:
        #
        # tryGetDynamicAttributes<AttributePortType::kAttributePortType_Input>(staticAttributeCount, m_dynamicInputs);
        # tryGetDynamicAttributes<AttributePortType::kAttributePortType_Output>(staticAttributeCount, m_dynamicOutputs);
        # tryGetDynamicAttributes<AttributePortType::kAttributePortType_State>(staticAttributeCount, m_dynamicStates);
        #
        self.out.write(
            "tryGetDynamicAttributes<AttributePortType::kAttributePortType_Input>(staticAttributeCount, m_dynamicInputs);"
        )
        self.out.write(
            "tryGetDynamicAttributes<AttributePortType::kAttributePortType_Output>(staticAttributeCount, m_dynamicOutputs);"
        )
        self.out.write(
            "tryGetDynamicAttributes<AttributePortType::kAttributePortType_State>(staticAttributeCount, m_dynamicStates);"
        )

    # ----------------------------------------------------------------------
    def generate_token_declarations(self):
        """Emit the code required to declare the tokens subclass in the database."""
        if not self.node_interface.tokens:
            return
        self.out.write("struct TokenManager")
        if self.out.indent("{"):
            for token_name, _ in self.node_interface.tokens.items():
                self.out.write(f"NameToken {token_name};")
            self.out.exdent("};")
        self.out.write("static TokenManager tokens;")

    # ----------------------------------------------------------------------
    def generate_token_intialization(self):
        """Emit the code required to initialize the tokens subclass in the database."""
        if not self.node_interface.tokens:
            return
        for token_name, token_value in self.node_interface.tokens.items():
            value = json.dumps(token_value)
            self.out.write(f"{self.database_class_name()}::tokens.{token_name} = iToken.getHandle({value});")

    # ----------------------------------------------------------------------
    def generate_database_constructors(self):
        """Write out the code that defines the database class constructors"""

        # Declare the constructor for temporary stack object
        self.out.write("")
        self.out.write("//Only use this constructor for temporary stack-allocated object:")
        self.out.write(f"{self.database_class_name()}(NodeObj const& nodeObjParam)")
        self.out.write(": OmniGraphDatabase()")

        # append attribute ctors
        self.generate_attribute_constructors(self.node_interface.all_input_attributes(), INPUT_GROUP)
        self.generate_attribute_constructors(self.node_interface.all_output_attributes(), OUTPUT_GROUP)
        self.generate_attribute_constructors(self.node_interface.all_state_attributes(), STATE_GROUP)

        if self.out.indent("{"):
            self.out.write("GraphContextObj const* contexts = nullptr;")
            self.out.write("NodeObj const* nodes = nullptr;")
            self.out.write("size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);")
            self.out.write("_ctor(contexts, nodes, handleCount);")
            self.out.write("_init();")
            self.out.exdent("}")

        # Declare the legacy constructor for temporary stack object
        # Marked as deprecated starting kit 105.2
        self.out.write("")
        self.out.write(
            'CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")'
        )
        self.out.write(f"{self.database_class_name()}(GraphContextObj const&, NodeObj const& nodeObjParam)")
        self.out.write(f": {self.database_class_name()}(nodeObjParam)")
        self.out.write("{}")

        # Declare the constructor, taking pointers to objects and contexts in order to be auto-instancing compatible
        self.out.write("")
        self.out.write("//Main constructor")
        self.out.write(
            f"{self.database_class_name()}(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)"
        )
        self.out.write(": OmniGraphDatabase()")

        # append attribute ctors
        self.generate_attribute_constructors(self.node_interface.all_input_attributes(), INPUT_GROUP)
        self.generate_attribute_constructors(self.node_interface.all_output_attributes(), OUTPUT_GROUP)
        self.generate_attribute_constructors(self.node_interface.all_state_attributes(), STATE_GROUP)

        if self.out.indent("{"):
            self.out.write("_ctor(contextObjParam, nodeObjParam, handleCount);")
            self.out.write("_init();")
            self.out.exdent("}")

        self.out.exdent("")
        self.out.indent("private:")

        self.out.indent("void _init() {")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")

        # TODO: This could use some cleanup - it's a bit redundant and confused at the moment

        # Split the input and output attributes into groups by memory type - CPU, CUDA, and ANY.
        # These are grouped together to minimize the calls across the ABI. More consolidation could happen
        # by getting all of the handles in one shot but that would complicate the management so unless it
        # becomes a performance problem it won't be done
        cpu_inputs, cuda_inputs, any_inputs = self.get_attributes_by_memory_type(INPUT_GROUP)
        cpu_outputs, cuda_outputs, any_outputs = self.get_attributes_by_memory_type(OUTPUT_GROUP)
        cpu_state, cuda_state, any_state = self.get_attributes_by_memory_type(STATE_GROUP)

        declared_locals = False

        for input_attributes, output_attributes, state_attributes in [
            [cpu_inputs, cpu_outputs, cpu_state],
            [cuda_inputs, cuda_outputs, cuda_state],
            [any_inputs, any_outputs, any_state],
        ]:
            if not input_attributes and not output_attributes and not state_attributes:
                continue

            # Avoid the necessity to provide unique names within this block
            (input_attrs, input_bundles, input_runtime) = split_attribute_list(input_attributes)
            (output_attrs, output_bundles, output_runtime) = split_attribute_list(output_attributes)
            (state_attrs, state_bundles, state_runtime) = split_attribute_list(state_attributes)
            needs_nesting = (
                input_attrs or input_bundles or output_attrs or output_bundles or state_attrs or state_bundles
            )

            # Extract some common parts of the ABI that will be used later
            if not declared_locals and (needs_nesting or input_runtime or output_runtime or state_runtime):
                self.out.write("GraphContextObj const& contextObj = abi_context();")
                self.out.write("NodeObj const& nodeObj = abi_node();")
                declared_locals = True

            if needs_nesting and self.out.indent("{"):
                # Arbitrarily split up the list of attributes into groups of 60, in the unlikely event there are more
                # than that. Limiting the size of the processed groups avoids potential template recursion depth limits.
                # Making it a larger number minimizes the calls across the ABI into the DataModel.
                # They are cast to lists so that they can be used more than once (generators cannot be reused)
                # groups of 60 seems to be safe for both VC compiler and gcc.
                input_single_groups = list(grouper(input_attrs, 60))
                input_bundle_groups = list(grouper(input_bundles, 60))
                output_bundle_groups = list(grouper(output_bundles, 60))
                output_single_groups = list(grouper(output_attrs, 60))
                state_bundle_groups = list(grouper(state_bundles, 60))
                state_single_groups = list(grouper(state_attrs, 60))

                # Keep the generation of the attribute handles from the tokens independent from the rest as in future
                # this could be cached on the node and reused since it never changes from one evaluation to the next.
                for i, attribute_sublist in enumerate(input_single_groups):
                    self.__generate_data_handles(attribute_sublist, i, self.HANDLE_INPUT)
                for i, attribute_sublist in enumerate(input_bundle_groups):
                    self.__generate_data_handles(attribute_sublist, i, self.HANDLE_INPUT_BUNDLE)
                for i, attribute_sublist in enumerate(output_single_groups):
                    self.__generate_data_handles(attribute_sublist, i, self.HANDLE_OUTPUT)
                for i, attribute_sublist in enumerate(output_bundle_groups):
                    self.__generate_data_handles(attribute_sublist, i, self.HANDLE_OUTPUT_BUNDLE)
                for i, attribute_sublist in enumerate(state_single_groups):
                    self.__generate_data_handles(attribute_sublist, i, self.HANDLE_STATE)
                for i, attribute_sublist in enumerate(state_bundle_groups):
                    self.__generate_data_handles(attribute_sublist, i, self.HANDLE_STATE_BUNDLE)

                # Generate the code that extracts the Fabric pointers for each attribute.
                for i, attribute_sublist in enumerate(input_single_groups):
                    self.generate_input_array_extraction(attribute_sublist, i, self.HANDLE_INPUT)
                for i, attribute_sublist in enumerate(input_bundle_groups):
                    self.generate_input_array_extraction(attribute_sublist, i, self.HANDLE_INPUT_BUNDLE)
                for i, attribute_sublist in enumerate(output_single_groups):
                    self.generate_writable_array_extraction(attribute_sublist, i, self.HANDLE_OUTPUT)
                for i, attribute_sublist in enumerate(output_bundle_groups):
                    self.generate_writable_bundle_extraction(attribute_sublist, i, self.HANDLE_OUTPUT_BUNDLE)
                for i, attribute_sublist in enumerate(state_single_groups):
                    self.generate_writable_array_extraction(attribute_sublist, i, self.HANDLE_STATE)
                for i, attribute_sublist in enumerate(state_bundle_groups):
                    self.generate_writable_bundle_extraction(attribute_sublist, i, self.HANDLE_STATE_BUNDLE)

                self.out.exdent("}")

            # Runtime attributes are set up in one step since their handles are only required once, to set up
            # their data wrappers, which will access the data at runtime.
            self.generate_runtime_attribute_initialization(input_runtime, self.HANDLE_INPUT)
            self.generate_runtime_attribute_initialization(output_runtime, self.HANDLE_OUTPUT)
            self.generate_runtime_attribute_initialization(state_runtime, self.HANDLE_STATE)

            # Generate the dynamic attribute initialization call
            self.generate_dynamic_attribute_initialization()

            # Generate the mapped attribute initialization call
            self.out.write("")
            self.out.write("collectMappedAttributes(m_mappedAttributes);")

            # Whether or not the database is allowed to cache pointers from one frame to another or not
            self.out.write("")
            self.out.write("m_canCachePointers = contextObj.iContext->canCacheAttributePointers ?")
            self.out.write(
                "                         contextObj.iContext->canCacheAttributePointers(contextObj) : true;"
            )

        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_STOP")

        self.out.exdent("}")

        self.out.exdent("")
        self.out.indent("public:")

    # ----------------------------------------------------------------------
    def generate_dynamic_attribute_accessors(self):
        excl = "  // LCOV_EXCL_LINE" if self.node_interface.exclude_from_coverage else ""
        self.out.write("std::vector<ogn::DynamicInput> const& getDynamicInputs() const")
        if self.out.indent("{"):
            self.out.write(f"return m_dynamicInputs;{excl}")
            self.out.exdent("}")
        self.out.write("gsl::span<ogn::DynamicOutput> getDynamicOutputs()")
        if self.out.indent("{"):
            self.out.write(f"return m_dynamicOutputs;{excl}")
            self.out.exdent("}")
        self.out.write("gsl::span<ogn::DynamicState> getDynamicStates()")
        if self.out.indent("{"):
            self.out.write(f"return m_dynamicStates;{excl}")
            self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_release(self):
        """Write out the code that defines the database internal state accessor, if any.

        Since the existence of the internal state can only be determined at compile time, not code generation time,
        the method is always emitted, relying on the state manager to efficiently handle nodes with and without state.
        """
        self.out.write("static void release(const NodeObj& nodeObj, GraphInstanceID instanceID)")
        if self.out.indent("{"):
            self.out.write(f"{self.state_manager_name()}.removeState(nodeObj.nodeHandle, instanceID);")
            self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_initialize(self):
        """Write out the code for the function that initializes a node of this type after creation.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        all_attributes = self.node_interface.all_input_attributes()
        all_attributes += self.node_interface.all_output_attributes()
        all_attributes += self.node_interface.all_state_attributes()
        if not all_attributes:
            return

        self.out.write("static void initialize(const GraphContextObj&, const NodeObj& nodeObj)")
        if self.out.indent("{"):
            if self.node_interface.exclude_from_coverage:
                self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")
            self.out.write("const INode* iNode = nodeObj.iNode;")
            if self.has_deprecated_attributes:
                self.out.write("const IInternal* iInternal = carb::getCachedInterface<omni::graph::core::IInternal>();")
                if self.out.indent("if( ! iInternal ) {"):
                    self.out.write(
                        f'CARB_LOG_ERROR("IInternal not found when initializing {self.node_interface.name}");'
                    )
                    self.out.write("return;")
                    self.out.exdent("}")
            self.out.write("AttributeObj attr;")
            for attribute in all_attributes:
                if not attribute.metadata and attribute.is_required and not attribute.is_deprecated:
                    continue

                member = f"{attribute.namespace}::{attribute.cpp_variable_name()}"
                self.out.write(f"attr = iNode->getAttributeByToken(nodeObj, {member}.token());")
                self.write_attrib_metadata(attribute)

                # Set the optional flag if it isn't the default
                if not attribute.is_required:
                    self.out.write("attr.iAttribute->setIsOptionalForCompute(attr, true);")

                # Deprecate the attribute, if necessary
                if attribute.is_deprecated:
                    self.out.write(f"iInternal->deprecateAttribute(attr, {to_cpp_str(attribute.deprecation_msg)});")

            if self.node_interface.exclude_from_coverage:
                self.out.write("// LCOV_EXCL_STOP")

            self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_initialize_type(self):
        """Write out the code for the function that initializes the node type.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        input_attributes = self.node_interface.all_input_attributes()
        output_attributes = self.node_interface.all_output_attributes()
        state_attributes = self.node_interface.all_state_attributes()

        self.out.write("static void initializeType(const NodeTypeObj& nodeTypeObj)")
        self.out.indent("{")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")

        # Metadata always needs this, and attributes will as well if there are any
        self.out.write("const INodeType* iNodeType = nodeTypeObj.iNodeType;")

        # Avoid generation of an unused variable
        if input_attributes or output_attributes or state_attributes or self.node_interface.tokens:
            # Cannot use the token interface stored in the database class since it doesn't exist here.
            self.out.write("auto iTokenPtr = carb::getCachedInterface<omni::fabric::IToken>();")
            if self.out.indent("if( ! iTokenPtr ) {"):
                self.out.write(f'CARB_LOG_ERROR("IToken not found when initializing {self.node_interface.name}");')
                self.out.write("return;")
                self.out.exdent("}")
            # The extra step of making a reference is taken so that future accesses to the interface are the
            # same no matter which extension you are in.
            self.out.write("auto& iToken{ *iTokenPtr };")
            self.generate_token_intialization()

        # Generate the initialization of attributes, including setting defaults and adding them to the node type
        def generate_attribute_initialize(attribute_list: List[AttributeManager], namespace: str):
            """Helper to initialize attributes of a given type. Prevents triplication of the loop"""
            self.out.write()
            for attribute in attribute_list:
                attribute.cpp_pre_initialization(self.out)
            for attribute in attribute_list:
                self.out.write(
                    f"{namespace}::{attribute.cpp_variable_name()}.initialize(iToken, *iNodeType, nodeTypeObj);"
                )
            for attribute in attribute_list:
                attribute.cpp_post_initialization(self.out)

        generate_attribute_initialize(input_attributes, INPUT_NS)
        generate_attribute_initialize(output_attributes, OUTPUT_NS)
        generate_attribute_initialize(state_attributes, STATE_NS)

        # Generate the initialization of the node metadata, including the hardcoded one holding the extension name
        self.out.write(
            f"iNodeType->setMetadata(nodeTypeObj, {MetadataKeyOutput.EXTENSION}, {json.dumps(self.extension)});"
        )
        for key, value in self.node_interface.metadata.items():
            cpp_key = MetadataKeyOutput.cpp_name_from_key(key)
            if cpp_key is None:
                # Run it through json to handle escaping the quotes
                cpp_key = json.dumps(key)
            self.out.write(f"iNodeType->setMetadata(nodeTypeObj, {cpp_key}, {json.dumps(value)});")

        # If any of the scheduling hints flags have been defined then set them here
        if self.node_interface.scheduling_hints is not None:
            self.node_interface.scheduling_hints.emit_cpp(self.out)

        # The icon path is relative to the extension path, which is only known at runtime, so build it up then.
        # To the user it will appear as an absolute path, which they can modify if they wish to.
        if self.node_interface.icon_path is not None:
            actual_path = Path(self.node_interface.icon_path)
            icon_path = json.dumps(self.node_interface.icon_path)
            # If the path is absolute then it does not need to be resolved at runtime
            if actual_path.is_absolute():
                self.out.write(f"iNodeType->setMetadata(nodeTypeObj, {MetadataKeyOutput.ICON_PATH}, {icon_path});")
            else:
                self.out.write("auto iTokens = carb::getCachedInterface<carb::tokens::ITokens>();")
                if self.out.indent("if( ! iTokens ) {"):
                    self.out.write(
                        'CARB_LOG_ERROR("Extension path not available - ITokens not found when initializing'
                        f' {self.node_interface.name}");'
                    )
                    self.out.exdent("}")
                self.out.write("else")
                if self.out.indent("{"):
                    self.out.write(
                        f'std::string iconPath = carb::tokens::resolveString(iTokens, "${{{self.extension}}}");'
                    )
                    self.out.write('iconPath.append("/");')
                    self.out.write(f"iconPath.append({icon_path});")
                    self.out.write(
                        f"iNodeType->setMetadata(nodeTypeObj, {MetadataKeyOutput.ICON_PATH}, iconPath.c_str());"
                    )
                    self.out.exdent("}")

        # Set up the state variable, directly if there are state attributes
        if self.node_interface.has_state:
            self.out.write("iNodeType->setHasState(nodeTypeObj, true);")

        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_STOP")
        # Close off the method definition
        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_validate(self):
        """Write out the code for the function that validates the attributes before compute.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        self.out.indent("bool validate() const {")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")
        attributes_to_walk = [
            [INPUT_NS, self.node_interface.all_input_attributes()],
            [OUTPUT_NS, self.node_interface.all_output_attributes()],
            [STATE_NS, self.node_interface.all_state_attributes()],
        ]
        conditions = ["validateNode()"]
        for attribute_prefix, attribute_list in attributes_to_walk:
            for attribute in attribute_list:
                if attribute.is_required:
                    if attribute.has_fixed_type():
                        conditions.append(f"{attribute_prefix}.{attribute.cpp_variable_name()}.isValid()")
                    elif attribute.do_validation:
                        conditions.append(f"{attribute_prefix}.{attribute.cpp_variable_name()}().resolved()")

        self.out.indent(f"return {conditions[0]}")
        for condition in conditions[1:]:
            self.out.write(f"&& {condition}")
        self.out.exdent(";")

        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_STOP")
        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_pre_compute(self):
        """Write out the code for the function that warn some attribute that a compute is about to happen.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """

        # call precompute on attributes that implements it
        self.out.indent("void preCompute() {")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")
        attributes_to_walk = [
            [INPUT_NS, self.node_interface.all_input_attributes()],
            [OUTPUT_NS, self.node_interface.all_output_attributes()],
            [STATE_NS, self.node_interface.all_state_attributes()],
        ]

        # if DB cannot cache any pointers, invalidate everything and returns
        if self.out.indent("if(m_canCachePointers == false) {"):
            for attribute_prefix, attribute_list in attributes_to_walk:
                for attribute in attribute_list:
                    self.out.write(f"{attribute_prefix}.{attribute.cpp_variable_name()}.invalidateCachedPointer();")
            self.out.write("return;")
            self.out.exdent("}")

        # else, we need to invalidate selectively attributes that cannot be cached
        for attribute_prefix, attribute_list in attributes_to_walk:
            for attribute in attribute_list:
                if attribute.require_precompute_invalidation():
                    self.out.write(f"{attribute_prefix}.{attribute.cpp_variable_name()}.invalidateCachedPointer();")

        # .... as well as all the mapped attributes
        if self.out.indent("for(NameToken const& attrib : m_mappedAttributes) {"):
            attributes_to_walk = [
                [INPUT_NS, self.node_interface.all_input_attributes()],
                [OUTPUT_NS, self.node_interface.all_output_attributes()],
            ]
            for attribute_prefix, attribute_list in attributes_to_walk:
                for attribute in attribute_list:
                    if attribute.create_type_name() != "bundle":
                        self.out.indent(
                            f"if(attrib == {attribute_prefix}::{attribute.cpp_variable_name()}.m_token) " + "{"
                        )
                        self.out.write(f"{attribute_prefix}.{attribute.cpp_variable_name()}.invalidateCachedPointer();")
                        self.out.write("continue;")
                        self.out.exdent("}")
            self.out.write("bool found = false;")
            if self.out.indent("for (auto& __a : m_dynamicInputs) {"):
                if self.out.indent("if (__a().name() == attrib) {"):
                    self.out.write("__a.invalidateCachedPointer();")
                    self.out.write("found = true;")
                    self.out.write("break;")
                    self.out.exdent("}")
                self.out.exdent("}")
                self.out.write("if(found) continue;")
            if self.out.indent("for (auto& __a : m_dynamicOutputs) {"):
                if self.out.indent("if (__a().name() == attrib) {"):
                    self.out.write("__a.invalidateCachedPointer();")
                    self.out.write("found = true;")
                    self.out.write("break;")
                    self.out.exdent("}")
                self.out.exdent("}")
                self.out.write("if(found) continue;")
            if self.out.indent("for (auto& __a : m_dynamicStates) {"):
                if self.out.indent("if (__a().name() == attrib) {"):
                    self.out.write("__a.invalidateCachedPointer();")
                    self.out.write("found = true;")
                    self.out.write("break;")
                    self.out.exdent("}")
                self.out.exdent("}")
                self.out.write("if(found) continue;")
            self.out.exdent("}")
            if self.node_interface.exclude_from_coverage:
                self.out.write("// LCOV_EXCL_STOP")
        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_can_vectorize(self):
        """Write out the code for the function that validates whether or not a full batch of vectorized attributes can be computed at once.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        self.out.indent("bool canVectorize() const {")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")
        attributes_to_walk = [
            [INPUT_NS, self.node_interface.all_input_attributes()],
            [OUTPUT_NS, self.node_interface.all_output_attributes()],
            [STATE_NS, self.node_interface.all_state_attributes()],
        ]
        conditions = []
        for attribute_prefix, attribute_list in attributes_to_walk:
            for attribute in attribute_list:
                if attribute.has_can_vectorize():
                    conditions.append(f"{attribute_prefix}.{attribute.cpp_variable_name()}.canVectorize()")
        if conditions:
            self.out.indent(f"if( !{conditions[0]}")
            for condition in conditions[1:]:
                self.out.write(f"|| !{condition}")
            self.out.exdent(") return false;")
        if self.out.indent("for (auto const& __a : m_dynamicInputs) {"):
            self.out.write("if(!__a.canVectorize()) return false;")
            self.out.exdent("}")
        if self.out.indent("for (auto const& __a : m_dynamicOutputs) {"):
            self.out.write("if(!__a.canVectorize()) return false;")
            self.out.exdent("}")
        if self.out.indent("for (auto const& __a : m_dynamicStates) {"):
            self.out.write("if(!__a.canVectorize()) return false;")
            self.out.exdent("}")
        self.out.write("return true;")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_STOP")
        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_on_type_resolution_changed(self):
        """Write out the code for the function that notifies that a type resolution event has occured on an attribute

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        attributes_to_walk = [
            [INPUT_NS, self.node_interface.all_input_attributes()],
            [OUTPUT_NS, self.node_interface.all_output_attributes()],
            [STATE_NS, self.node_interface.all_state_attributes()],
        ]
        dynamic_attributes = []
        for attribute_prefix, attribute_list in attributes_to_walk:
            for attribute in attribute_list:
                if attribute.is_dynamic():
                    dynamic_attributes.append((attribute_prefix, attribute))
        self.out.indent("void onTypeResolutionChanged(AttributeObj const& attr) {")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")
        self.out.write("if (! attr.isValid()) return;")
        self.out.write("NameToken token = attr.iAttribute->getNameToken(attr);")
        if dynamic_attributes:
            for attribute_prefix, attribute in dynamic_attributes:
                self.out.indent(f"if({attribute_prefix}::{attribute.cpp_variable_name()}.m_token == token)" + " {")
                self.out.write(f"{attribute_prefix}.{attribute.cpp_variable_name()}.fetchDetails(attr);")
                self.out.write("return;")
                self.out.exdent("}")
        if self.out.indent("for (auto& __a : m_dynamicInputs) {"):
            if self.out.indent("if (__a().name() == token) {"):
                self.out.write("__a.fetchDetails(attr);")
                self.out.write("return;")
                self.out.exdent("}")
            self.out.exdent("}")
        if self.out.indent("for (auto& __a : m_dynamicOutputs) {"):
            if self.out.indent("if (__a().name() == token) {"):
                self.out.write("__a.fetchDetails(attr);")
                self.out.write("return;")
                self.out.exdent("}")
            self.out.exdent("}")
        if self.out.indent("for (auto& __a : m_dynamicStates) {"):
            if self.out.indent("if (__a().name() == token) {"):
                self.out.write("__a.fetchDetails(attr);")
                self.out.write("return;")
                self.out.exdent("}")
            self.out.exdent("}")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_STOP")
        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_on_dynamic_attributes_changed(self):
        """
        Generates the code that updates the dynamic attribute caches
        when dynamic attributes are added or removed
        """
        # void onDynamicAttributesChanged(AttributeObj const& attribute, bool isAttributeCreated) {
        #     onDynamicAttributeCreatedOrRemoved(m_dynamicInputs, m_dynamicOutputs, m_dynamicStates, attribute, isAttributeCreated);
        # }
        self.out.indent("void onDynamicAttributesChanged(AttributeObj const& attribute, bool isAttributeCreated) {")
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")
        self.out.write(
            "onDynamicAttributeCreatedOrRemoved(m_dynamicInputs, m_dynamicOutputs, m_dynamicStates, attribute, isAttributeCreated);"
        )
        if self.node_interface.exclude_from_coverage:
            self.out.write("// LCOV_EXCL_STOP")
        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_on_data_location_changed(self):
        if self.out.indent("void onDataLocationChanged(AttributeObj const& attr) {"):
            if self.node_interface.exclude_from_coverage:
                self.out.write("// LCOV_EXCL_START : internal:test nodes are excluded from coverage")
            self.out.write("if (! attr.isValid()) return;")
            self.out.write("updateMappedAttributes(m_mappedAttributes, attr);")
            self.out.write("NameToken token = attr.iAttribute->getNameToken(attr);")
            attributes_to_walk = [
                [self.HANDLE_INPUT, INPUT_NS, self.node_interface.all_input_attributes()],
                [self.HANDLE_OUTPUT, OUTPUT_NS, self.node_interface.all_output_attributes()],
            ]
            for rt_table_idx, attribute_prefix, attribute_list in attributes_to_walk:
                for attribute in attribute_list:
                    if self.out.indent(
                        f"if(token == {attribute_prefix}::{attribute.cpp_variable_name()}.m_token) " + "{"
                    ):
                        if attribute.is_dynamic():
                            self.out.write(f"{attribute_prefix}.{attribute.cpp_variable_name()}.fetchDetails(attr);")
                        else:
                            (func, datahandle_type, _, _) = self.RUNTIME_TABLE[rt_table_idx]
                            self.out.write(f"{datahandle_type} hdl = attr.iAttribute->{func}(attr, m_offset);")
                            self.out.write(f"{attribute_prefix}.{attribute.cpp_variable_name()}.setHandle(hdl);")
                        self.out.write("return;")
                        self.out.exdent("}")
            if self.out.indent("for (auto& __a : m_dynamicInputs) {"):
                if self.out.indent("if (__a().name() == token) {"):
                    self.out.write("__a.fetchDetails(attr);")
                    self.out.write("return;")
                    self.out.exdent("}")
                self.out.exdent("}")
            if self.out.indent("for (auto& __a : m_dynamicOutputs) {"):
                if self.out.indent("if (__a().name() == token) {"):
                    self.out.write("__a.fetchDetails(attr);")
                    self.out.write("return;")
                    self.out.exdent("}")
                self.out.exdent("}")
            if self.out.indent("for (auto& __a : m_dynamicStates) {"):
                if self.out.indent("if (__a().name() == token) {"):
                    self.out.write("__a.fetchDetails(attr);")
                    self.out.write("return;")
                    self.out.exdent("}")
                self.out.exdent("}")
            if self.node_interface.exclude_from_coverage:
                self.out.write("// LCOV_EXCL_STOP")
            self.out.exdent("}")

    def generate_cuda_interop_scaffolding(self):
        """Generates the helper methods for allocating RenderVars in post render graph nodes."""
        # The ComputeParamsBuilder<std::string> wraps the RenderProduct and GPU interfaces.
        # It provides a controlled API for allocating new RenderVars from post render graph nodes.
        if self.out.indent(
            "omni::graph::image::unstable::ComputeParamsBuilder<std::string> getCudaParamsBuilder(InstanceIndex relativeIdx = { 0 }) {"
        ):
            self.out.write(
                f'auto variable = const_cast<{self.database_class_name()}*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);'
            )
            if self.out.indent("if (CARB_UNLIKELY(!variable.isValid() || 0 == *variable.get<uint64_t>())) {"):
                self.out.write("auto nodeObj = abi_node(relativeIdx);")
                self.out.write("auto graphObj = nodeObj.iNode->getGraph(nodeObj);")
                self.out.write("auto pipeline = graphObj.iGraph->getPipelineStage(graphObj);")
                if self.out.indent("if (pipeline != kGraphPipelineStage_PostRender) {"):
                    self.out.write(
                        'CARB_LOG_ERROR("%s: The node %s is trying to get a ComputeParamsBuilder outside of a post render graph. Nodes using this API are only supported in post render graphs.", __func__, nodeObj.iNode->getPrimPath(nodeObj));'
                    )
                self.out.exdent("}")
                self.out.write(
                    "// LCOV_EXCL_START : this error condition is a manifestation of an error in the execution framework and not expected to happen in user code"
                )
                if self.out.indent("else {"):
                    self.out.write(
                        'CARB_LOG_ERROR("%s: Invalid GPU data for node %s", __func__, nodeObj.iNode->getPrimPath(nodeObj));'
                    )
                self.out.exdent("}")
                self.out.write("// LCOV_EXCL_STOP")
                self.out.write(
                    "return omni::graph::image::unstable::ComputeParamsBuilder<std::string>{ nullptr, nullptr, *this };"
                )
            self.out.exdent("}")
            self.out.write(
                "auto internalData = reinterpret_cast<GpuInteropRpEntryUserData*>(*variable.get<uint64_t>());"
            )
            self.out.write(
                "return omni::graph::image::unstable::ComputeParamsBuilder<std::string>{ internalData->gpu, internalData->rp, *this };"
            )
        self.out.exdent("}")

        # The ComputeParams<std::string> class obtained from the ComputeParamsBuilder is stored in a graph variable.
        # This ensures that graph instancing is supported by default in post render graph nodes.
        if self.out.indent(
            "void setCudaParams(omni::graph::image::unstable::ComputeParams<std::string>&& params, InstanceIndex relativeIdx = { 0 }) {"
        ):
            self.out.write(
                f'auto variable = const_cast<{self.database_class_name()}*>(this)->getVariable("__computeParams", m_offset + relativeIdx);'
            )
            if self.out.indent("if (CARB_UNLIKELY(!(variable.isValid() && *variable.get<uint64_t>()))) {"):
                self.out.write("auto nodeObj = abi_node(relativeIdx);")
                self.out.write("auto graphObj = nodeObj.iNode->getGraph(nodeObj);")
                self.out.write("auto pipeline = graphObj.iGraph->getPipelineStage(graphObj);")
                if self.out.indent("if (pipeline != kGraphPipelineStage_PostRender) {"):
                    self.out.write(
                        'CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s. Nodes using this API are only supported in post render graphs.", __func__, nodeObj.iNode->getPrimPath(nodeObj));'
                    )
                self.out.exdent("}")
                self.out.write(
                    "// LCOV_EXCL_START : this error condition is a manifestation of an error in the execution framework and not expected to happen in user code"
                )
                if self.out.indent("else {"):
                    self.out.write(
                        'CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s.", __func__, nodeObj.iNode->getPrimPath(nodeObj));'
                    )
                self.out.exdent("}")
                self.out.write("// LCOV_EXCL_STOP")
                self.out.write("return;")
            self.out.exdent("}")

            self.out.write(
                "auto paramsPtr = reinterpret_cast<omni::graph::image::unstable::ComputeParams<std::string>*>(*variable.get<uint64_t>());"
            )
            self.out.write(
                "*paramsPtr = std::forward<omni::graph::image::unstable::ComputeParams<std::string>>(params);"
            )
        self.out.exdent("}")

        # The ComputeParams<std::string> object can be retrieved in computeCuda() such that the node can operate on
        # the newly allocated RenderVar.
        if self.out.indent(
            "omni::graph::image::unstable::ComputeParams<std::string> const& getCudaParams(InstanceIndex relativeIdx = { 0 }) const {"
        ):
            self.out.write("static omni::graph::image::unstable::ComputeParams<std::string> defaultParams{};")
            self.out.write(
                f'auto variable = const_cast<{self.database_class_name()}*>(this)->getVariable("__computeParams", m_offset + relativeIdx);'
            )
            if self.out.indent("if (CARB_UNLIKELY(!(variable.isValid() && *variable.get<uint64_t>()))) {"):
                self.out.write("auto nodeObj = abi_node(relativeIdx);")
                self.out.write("auto graphObj = nodeObj.iNode->getGraph(nodeObj);")
                self.out.write("auto pipeline = graphObj.iGraph->getPipelineStage(graphObj);")
                if self.out.indent("if (pipeline != kGraphPipelineStage_PostRender) {"):
                    self.out.write(
                        'CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s. Nodes using this API are only supported in post render graphs.", __func__, nodeObj.iNode->getPrimPath(nodeObj));'
                    )
                self.out.exdent("}")
                self.out.write(
                    "// LCOV_EXCL_START : this error condition is a manifestation of an error in the execution framework and not expected to happen in user code"
                )
                if self.out.indent("else {"):
                    self.out.write(
                        'CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s.", __func__, nodeObj.iNode->getPrimPath(nodeObj));'
                    )
                self.out.exdent("}")
                self.out.write("// LCOV_EXCL_STOP")
                self.out.write("return defaultParams;")
            self.out.exdent("}")
            self.out.write(
                "return *reinterpret_cast<omni::graph::image::unstable::ComputeParams<std::string>*>(*variable.get<uint64_t>());"
            )
        self.out.exdent("}")

    def generate_get_cuda_stream(self):
        """Generates the getCudaStream() database method."""
        if self.out.indent("cudaStream_t getCudaStream(InstanceIndex relativeIdx = { 0 }) const {"):
            self.out.write(
                f'auto variable = const_cast<{self.database_class_name()}*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);'
            )
            self.out.write(
                "return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};"
            )
        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_database(self):
        """Write out the code to initialize the required attributes.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        self.generate_attribute_static_data()

        # The namespace encapsulates the attribute access to make it easier to isolate it
        self.out.write(f"namespace I{self.base_name}")
        self.out.write("{")

        # Optional description information. Can be omitted if the generated code is never examined.
        node_description = to_cpp_comment(self.node_interface.description)
        self.out.write(f"{node_description}")

        # Generate the class wrapping all of the access to the DataModel, including the core ABI objects
        self.out.write(f"class {self.database_class_name()} : public omni::graph::core::ogn::OmniGraphDatabase")
        self.out.write("{")
        if self.out.indent("public:"):
            self.generate_token_declarations()
            # marked as deprecated starting with kit 105.2
            self.out.write("template <typename StateInformation>")
            self.out.write(
                'CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")'
            )
            if self.out.indent(
                "static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {"
            ):
                self.out.write(
                    f"return {self.state_manager_name()}.getState<StateInformation>(nodeObj.nodeHandle, index);"
                )
                self.out.exdent("}")
            self.out.write("template <typename StateInformation>")
            if self.out.indent("static StateInformation& sSharedState(const NodeObj& nodeObj) {"):
                self.out.write(
                    f"return {self.state_manager_name()}.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);"
                )
                self.out.exdent("}")
            self.out.write("template <typename StateInformation>")
            if self.out.indent(
                "static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {"
            ):
                self.out.write(
                    f"return {self.state_manager_name()}.getState<StateInformation>(nodeObj.nodeHandle, index);"
                )
                self.out.exdent("}")

            self.out.write("template <typename StateInformation>")
            if self.out.indent(
                "static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {"
            ):
                self.out.write(
                    f"return {self.state_manager_name()}.getState<StateInformation>(nodeObj.nodeHandle, instanceId);"
                )
                self.out.exdent("}")
            # marked as deprecated starting with kit 105.2
            self.out.write("template <typename StateInformation>")
            self.out.write(
                'CARB_DEPRECATED("internalState is deprecated. Use sharedState or perInstanceState instead")'
            )
            if self.out.indent("StateInformation& internalState(size_t relativeIdx = 0) {"):
                self.out.write("return sInternalState<StateInformation>(abi_node(), m_offset + relativeIdx);")
                self.out.exdent("}")
            self.out.write("template <typename StateInformation>")
            if self.out.indent("StateInformation& sharedState() {"):
                self.out.write("return sSharedState<StateInformation>(abi_node());")
                self.out.exdent("}")
            self.out.write("template <typename StateInformation>")
            if self.out.indent("StateInformation& perInstanceState(size_t relativeIdx = 0) {"):
                self.out.write("return sPerInstanceState<StateInformation>(abi_node(), m_offset + relativeIdx);")
                self.out.exdent("}")
            self.out.write("template <typename StateInformation>")
            if self.out.indent("StateInformation& perInstanceState(GraphInstanceID instanceId) {"):
                self.out.write("return sPerInstanceState<StateInformation>(abi_node(), instanceId);")
                self.out.exdent("}")
            self.out.write(f"static ogn::StateManager {self.state_manager_name()};")
            self.out.write(f"static std::tuple<int, int, int>{self.generator_version_name()};")
            self.out.write(f"static std::tuple<int, int, int>{self.target_version_name()};")

            # Add support for dynamic attributes.
            # The final count includes the node version and type attributes,
            # which are always returned by a call to getAttributes in C++
            self.out.write(
                f"static constexpr size_t staticAttributeCount = {2 + len(self.node_interface.all_attributes())};"
            )

            # The dynamic inputs, outputs and state lists are code generated to allow for future support for non-cpu attributes
            self.out.write("std::vector<ogn::DynamicInput> m_dynamicInputs;")
            self.out.write("std::vector<ogn::DynamicOutput> m_dynamicOutputs;")
            self.out.write("std::vector<ogn::DynamicState> m_dynamicStates;")

            # The mapped attribute are stored in the database for fast reset in precompute
            self.out.write("std::vector<NameToken> m_mappedAttributes;")

            # A flag to know if the database is allowed to cache pointers
            self.out.write("bool m_canCachePointers{true};")

            self.generate_attribute_accessors(self.node_interface.all_input_attributes(), INPUT_GROUP)
            self.generate_attribute_accessors(self.node_interface.all_output_attributes(), OUTPUT_GROUP)
            self.generate_attribute_accessors(self.node_interface.all_state_attributes(), STATE_GROUP)

            self.generate_database_constructors()

            # The ABI initializeType method is implemented as a member of this class to simplify registration
            self.generate_initialize_type()

            # The ABI initialize method is implemented as a member of this class to facilitate attribute
            # metadata and internal state data.
            if self.needs_initialize:
                self.generate_initialize()

            self.generate_dynamic_attribute_accessors()

            # The ABI initialize method is implemented as a member of this class to facilitate internal state data.
            self.generate_release()

            # Compute will require validation that all required attributes exist before running
            self.generate_validate()

            # Compute needs preparation before running
            self.generate_pre_compute()

            # This will used by the framework to know if a batch of vectorized attributes can be computed at once
            self.generate_can_vectorize()

            # This will used by the framework to notify that a type resolution event has occured on an attribute
            self.generate_on_type_resolution_changed()

            # Used by the framework to notify the DB when dynamic attributes are added or removed
            self.generate_on_dynamic_attributes_changed()

            # Used by the framework to notify the DB when an attribute data location has changed (as a result of a target (un)mapping)
            self.generate_on_data_location_changed()

            # Support the CUDA interop post render graph nodes
            with suppress(KeyError):
                categories = json.dumps(self.node_interface.metadata[MetadataKeys.CATEGORIES]).lower()
                if "graph:postrender" in categories:
                    self.generate_cuda_interop_scaffolding()

                if "graph:prerender" in categories or "graph:postrender" in categories:
                    self.generate_get_cuda_stream()

            # Terminate the class definition
            self.out.exdent("};")

            # Initialize the static objects here, to avoid potential namespace clashes later
            class_name = self.database_class_name()
            self.out.write(f"ogn::StateManager {class_name}::{self.state_manager_name()};")

            # Remember the generator and code target version, in case it is needed later for backwards compatibility
            generator_version = ",".join([str(version) for version in self.generator_version])
            self.out.write(
                f"std::tuple<int, int, int> {class_name}::{self.generator_version_name()}"
                f"{{std::make_tuple({generator_version})}};"
            )
            target_version = ",".join([str(version) for version in self.target_version])
            self.out.write(
                f"std::tuple<int, int, int> {class_name}::{self.target_version_name()}"
                f"{{std::make_tuple({target_version})}};"
            )

            # If there are tokens declare the class member that implements them
            if self.node_interface.tokens:
                self.out.write(f"{class_name}::TokenManager {class_name}::tokens;")

        # Hide the namespace enclosure from the node code
        self.out.write("}")
        self.out.write(f"using namespace I{self.base_name};")

    # ----------------------------------------------------------------------
    def generate_cuda_code(self):
        """Write out the code that will be used by the CUDA code.
        Here is some sample output for a node multiplying a vector by a constant

            namespace OgnFooCudaTypes
            {
            namespace inputs
            {
            using multiplier_t = const float&;
            using input_t = const float3&;
            }
            namespace outputs
            {
            using result_t = float;
            }
            }
            using namespace OgnFooCudaTypes;

        With this set of definitions and the ones in the CPU types you can easily define functions that cross the
        CPU/GPU boundary. This would be the signature in the .cpp file:
            extern "C" void scaleVector(inputs::input_t, inputs::multiplier_t, outputs::result_t);
        with this definition in the .cu file:
            extern "C" void scaleVector(inputs::input_t, inputs::multiplier_t, outputs::result_t);

        The pointer is necessary as the CPU cannot directly access GPU data so it has to pass through
        the extracted Fabric data as (undereferencable) pointers. It is made explicit rather than burying
        it in the type definition in order to make it obvious to the user that they are dealing with a pointer.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the CUDA interface
        """

        def generate_cuda_includes(attribute_list: List[AttributeManager]) -> List[str]:
            """Helper function that returns a list of all include statements needed by CUDA definitions"""
            includes = []
            for attribute in attribute_list:
                includes += attribute.cuda_includes()
            return includes

        def generate_cuda_typedefs(attribute_list: List[AttributeManager], attribute_group: str):
            """Helper function that generates the CUDA typedefs all attributes in the list
            The types here are similar but not identical to those generated in the static attribute
            information definition class created in generate_attribute_static_data().

            Args:
                attribute_list: List of attributes to generate
                attribute_group: Enum with the attribute's group (input, output, or state)
            """
            namespace = namespace_of_group(attribute_group)
            self.out.write(f"namespace {namespace}")
            self.out.write("{")
            for attribute in attribute_list:
                attribute_data_type = attribute.cuda_type_name()
                # No type means the attribute type cannot be passed to CUDA code
                if attribute_data_type is not None:
                    modifier = "const " if attribute.is_read_only() else ""
                    initializer_name = attribute.cpp_variable_name()
                    self.out.write(f"using {initializer_name}_t = {modifier}{attribute_data_type};")
            self.out.write("}")

        input_includes = generate_cuda_includes(self.node_interface.all_input_attributes())
        output_includes = generate_cuda_includes(self.node_interface.all_output_attributes())
        state_includes = generate_cuda_includes(self.node_interface.all_state_attributes())
        for include_file in sorted(set(input_includes + output_includes + state_includes)):
            self.out.write(f"#include <{include_file}>")

        # Namespace it to create file-local objects with easy access
        self.out.write(f"namespace {self.base_name}CudaTypes")
        self.out.write("{")

        generate_cuda_typedefs(self.node_interface.all_input_attributes(), INPUT_GROUP)
        generate_cuda_typedefs(self.node_interface.all_output_attributes(), OUTPUT_GROUP)
        generate_cuda_typedefs(self.node_interface.all_state_attributes(), STATE_GROUP)

        self.out.write("}")
        self.out.write(f"using namespace {self.base_name}CudaTypes;")

    # ----------------------------------------------------------------------
    def generate_node_interface(self):
        """Write out the code associated with the node.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        self.generate_database()
        self.generate_registration_macro()


# ======================================================================
def generate_cpp(configuration: GeneratorConfiguration, all_supported: bool = None) -> Optional[str]:
    """Create support files for the C++ interface to a node

    For now only a header file is generated for the C++ interface, though there will probably be multiple files
    generated in the future. For that reason this single point of contact was created for outside callers.

    Args:
        configuration: Information defining how and where the header will be generated
        all_supported: Deprecated: Do not use.

    Returns:
        String containing the generated header code or None if its generation was not enabled

    Raises:
        NodeGenerationError: When there is a failure in the generation of the header
    """
    if all_supported is not None:
        DeprecateMessage.deprecated("generate_cpp no longer recognizes the all_supported flag - remove it")

    if not configuration.node_interface.can_generate("c++"):
        return None
    logger.info("Generating C++ Database Definition")
    generator = NodeCppGenerator(configuration)
    generator.generate_interface()
    return str(generator.out)
