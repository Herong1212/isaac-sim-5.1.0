"""Support for generating an annotated C++ template class for OmniGraph Nodes.

Exports:
    generate_template: Create a NODE_template.cpp file containing sample uses of the generated interface
"""

from typing import List, Optional

from .attributes.AttributeManager import AttributeManager
from .attributes.naming import INPUT_GROUP, OUTPUT_GROUP, STATE_GROUP, namespace_of_group
from .keys import LanguageTypeValues
from .nodes import NodeInterfaceGenerator
from .utils import GeneratorConfiguration, UnimplementedError, logger, to_comment, to_cpp_comment

__all__ = ["generate_template"]


class NodeTemplateGenerator(NodeInterfaceGenerator):
    """Manage the functions required to generate an annotated template class for a node"""

    def __init__(self, configuration: GeneratorConfiguration):
        """Set up the generator and output the annotated template class for the node

        Checks the language support.
        """
        self.template_extension = None
        if configuration.node_interface.language == LanguageTypeValues.CPP:
            self.template_extension = "cpp"
        elif configuration.node_interface.language == LanguageTypeValues.PYTHON:
            self.template_extension = "py"
        else:
            language_name = "|".join(LanguageTypeValues.ALL[self.node_interface.language])
            raise UnimplementedError(f"Template generation not supported for '{language_name}' files")

        # This needs the extension set to properly define the interface file name so do it after that
        super().__init__(configuration)

    # ----------------------------------------------------------------------
    def interface_file_name(self) -> str:
        """Return the path to the name of the template file"""
        return self.base_name + "." + self.template_extension

    # ----------------------------------------------------------------------
    def generate_cpp_attribute_info(self, attribute_list: List[AttributeManager], attribute_group: str):
        """Generate the comments explaining how to access the values of attributes in the list

        Args:
            attribute_list: List of attributes for which explanations are to be emitted
            attribute_group: Enum with the attribute's group (input, output, or state)
        """
        namespace = namespace_of_group(attribute_group)
        for attribute in attribute_list:
            self.out.write()
            if attribute_group != INPUT_GROUP:
                if attribute.fabric_needs_counter():
                    self.out.write("// Before setting array outputs you must first set their size to allocate space")
                    self.out.write(f"// db.{namespace}.{attribute.base_name}.size() = newOutputSize;")
                self.out.write(f"// auto& output{attribute.base_name} = db.{namespace}.{attribute.base_name}();")
            else:
                self.out.write(f"// const auto& input_value = db.{namespace}.{attribute.base_name}();")
            role = attribute.cpp_role_name()
            if role:
                self.out.write("// Roles for role-based attributes can be found by name using this member")
                self.out.write(f"// auto roleName = db.{namespace}.{attribute.base_name}.role();")

    # ----------------------------------------------------------------------
    def generate_cpp_template(self):
        """Write out a template for a C++ node describing use of the current OGN configuration.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        # Rely on the formatter to insert the copyright here
        node_description = to_cpp_comment(self.node_interface.description)
        self.out.write(f"{node_description}")
        self.out.write(f"#include <{self.base_name}Database.h>")
        self.out.write(f"class {self.base_name}:")
        self.out.write("{")
        if self.out.indent("public:"):
            self.out.write(f"static bool compute({self.base_name}Database& db)")
            if self.out.indent("{"):

                input_attributes = self.node_interface.all_input_attributes()
                if input_attributes:
                    self.out.write("// ======================================================================")
                    self.out.write("// Use these methods to access the input values")
                    self.out.write("// ======================================================================")
                    self.generate_cpp_attribute_info(self.node_interface.all_input_attributes(), INPUT_GROUP)
                    self.out.write()

                output_attributes = self.node_interface.all_output_attributes()
                if output_attributes:
                    self.out.write("// ======================================================================")
                    self.out.write("// Use these methods to set the output values")
                    self.out.write("// ======================================================================")
                    self.generate_cpp_attribute_info(self.node_interface.all_output_attributes(), OUTPUT_GROUP)
                    self.out.write()

                state_attributes = self.node_interface.all_state_attributes()
                if state_attributes:
                    self.out.write("// ======================================================================")
                    self.out.write("// Use these methods to set the state values")
                    self.out.write("// ======================================================================")
                    self.generate_cpp_attribute_info(state_attributes, STATE_GROUP)
                    self.out.write()

                self.out.write("// ======================================================================")
                self.out.write("// If you have predefined any tokens you can access them by name like this")
                self.out.write("// ======================================================================")
                self.out.write("auto myColorToken = db.tokens.color;")
                self.out.write()

                self.out.write("return true;")
                self.out.exdent("}")
            self.out.exdent("}")

    # ----------------------------------------------------------------------
    def generate_python_attribute_info(self, attribute_list: List[AttributeManager], attribute_group: str):
        """Generate the comments explaining how to access the values of attributes in the list

        Args:
            attribute_list: List of attributes for which explanations are to be emitted
            attribute_group: Enum with the attribute's group (input, output, or state)
        """
        namespace = namespace_of_group(attribute_group)
        for attribute in attribute_list:
            self.out.write()
            if attribute_group != INPUT_GROUP:
                if attribute.fabric_needs_counter():
                    self.out.write("# Before setting array outputs you must first set their size to allocate space")
                    self.out.write(f"# db.{namespace}.{attribute.base_name}_size = new_output_size")
                self.out.write(f"# db.{namespace}.{attribute.base_name} = new_output_value")
            else:
                self.out.write(f"# input_value = db.{namespace}.{attribute.base_name}")
            role = attribute.python_role_name()
            if role:
                self.out.write("# Roles for role-based attributes can be found by name using this member")
                self.out.write(f"# role_name = db.role.{namespace}.{attribute.base_name}")

    # ----------------------------------------------------------------------
    def generate_python_template(self):
        """Write out the code associated with the node.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the C++ interface
        """
        self.out.write('"""')
        self.out.write(f"This is the implementation of the OGN node defined in {self.base_name}.ogn")
        self.out.write('"""')
        self.out.write()
        self.out.write("# Array or tuple values are accessed as numpy arrays so you probably need this import")
        self.out.write("import numpy")
        self.out.write()
        self.out.write()
        if self.out.indent(f"class {self.base_name}:"):
            node_description = to_comment("", self.node_interface.description, 1)
            self.out.write('"""')
            self.out.write(node_description)
            self.out.write('"""')
            self.out.write("@staticmethod")
            if self.out.indent("def compute(db) -> bool:"):
                self.out.write('"""Compute the outputs from the current input"""\n')
                if self.out.indent("try:"):
                    self.out.write("# With the compute in a try block you can fail the compute by raising an exception")
                    input_attributes = self.node_interface.all_input_attributes()
                    if input_attributes:
                        self.out.write("# ======================================================================")
                        self.out.write("# Use these methods to access the input values")
                        self.out.write("# ======================================================================")
                        self.generate_python_attribute_info(self.node_interface.all_input_attributes(), INPUT_GROUP)
                        self.out.write()
                    output_attributes = self.node_interface.all_output_attributes()
                    if output_attributes:
                        self.out.write("# ======================================================================")
                        self.out.write("# Use these methods to set the output values")
                        self.out.write("# ======================================================================")
                        self.generate_python_attribute_info(self.node_interface.all_output_attributes(), OUTPUT_GROUP)
                        self.out.write()
                    state_attributes = self.node_interface.all_state_attributes()
                    if state_attributes:
                        self.out.write("# ======================================================================")
                        self.out.write("# Use these methods to set the state values")
                        self.out.write("# ======================================================================")
                        self.generate_python_attribute_info(state_attributes, STATE_GROUP)
                        self.out.write()
                    self.out.write("pass")
                    self.out.exdent()
                if self.out.indent("except Exception as error:"):
                    self.out.write("# If anything causes your compute to fail report the error and return False")
                    self.out.write("db.log_error(str(error))")
                    self.out.write("return False")
                    self.out.exdent()
                self.out.write()
                self.out.write("# Even if inputs were edge cases like empty arrays, correct outputs mean success")
                self.out.write("return True")
                self.out.exdent()
            self.out.exdent()

    # ----------------------------------------------------------------------
    def generate_node_interface(self):
        """Write out a template implementation of the node in the requested language.

        Raises:
            NodeGenerationError: When there is a failure in the generation of the template
        """
        if self.node_interface.language == LanguageTypeValues.CPP:
            self.generate_cpp_template()
        elif self.node_interface.language == LanguageTypeValues.PYTHON:
            self.generate_python_template()


# ======================================================================
def generate_template(configuration: GeneratorConfiguration) -> Optional[str]:
    """Create support files for the C++ interface to a node

    For now only a header file is generated for the C++ interface, though there will probably be multiple files
    generated in the future. For that reason this single point of contact was created for outside callers.

    Args:
        configuration: Information defining how and where the template will be generated

    Returns:
        String containing the generated template class definition or None if its generation was not enabled

    Raises:
        NodeGenerationError: When there is a failure in the generation of the header
        UnimplementedError: When the language of the node does not support template generation
    """
    if not configuration.node_interface.can_generate("template"):
        return None

    logger.info("Generating Template Node Implementation Class")
    generator = NodeTemplateGenerator(configuration)
    generator.generate_interface()
    return str(generator.out)
