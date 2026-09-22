"""Support for generating USD template files for OmniGraph Nodes.

Exports:
    generate_usd: Create a NODETemplate.usda file containing a template for instantiation of the described node type
"""

from typing import List, Optional

from .attributes.AttributeManager import AttributeManager
from .nodes import NodeInterfaceGenerator
from .utils import GeneratorConfiguration, logger, to_usd_docs


def pluralize(count: int):
    """Return a string with the pluralization suffix for the given count ("s" for non-1, "" for 1)"""
    return "" if count == 1 else "s"


class NodeUsdGenerator(NodeInterfaceGenerator):
    """Manage the functions required to generate a USD template file representing a node type"""

    def __init__(self, configuration: GeneratorConfiguration):  # noqa: PLW0246
        """Set up the generator and output the USD template for the node

        Just passes the initialization on to the parent class. See the argument and exception descriptions there.
        """
        super().__init__(configuration)

    # ----------------------------------------------------------------------
    def interface_file_name(self):
        """Return the path to the name of the USD file"""
        return self.base_name + "Template.usda"

    # ----------------------------------------------------------------------
    def __prim_name(self) -> str:
        """Returns a string comprising the name of the prim representing this node in the USD file"""
        return f"Template_{self.safe_name()}"

    # ----------------------------------------------------------------------
    def generate_attributes_usd(self, attributes: List[AttributeManager]):
        """Write out USD code corresponding to the node

        Args:
            attributes: List of attributes whose USD is to be generated

        Raises:
            NodeGenerationError: When there is a failure in the generation of the USD file
        """
        for attribute in attributes:
            attribute.emit_usd_declaration(self.out)

    # ----------------------------------------------------------------------
    def generate_node_interface(self):
        """Generate the USD code corresponding to the node_interface

        Raises:
            NodeGenerationError: When there is a failure in the generation of the USD file
        """
        node_name = self.node_interface.name
        node_version = self.node_interface.version
        self.out.write("")
        if self.out.indent(f'def OmniGraphNode "{self.__prim_name()}" ('):
            self.out.write(to_usd_docs(self.node_interface.description))
            self.out.exdent(")")
        self.out.write("{")
        self.out.indent()
        self.out.write(f'token node:type = "{node_name}"')
        self.out.write(f"int node:typeVersion = {node_version}")
        for attributes in [
            self.node_interface.all_input_attributes(),
            self.node_interface.all_output_attributes(),
            self.node_interface.all_state_attributes(),
        ]:
            if attributes:
                attribute_count = len(attributes)
                self.out.write("")
                self.out.write(f"# {attribute_count} attribute{pluralize(attribute_count)}")
                self.generate_attributes_usd(attributes)

        self.out.exdent("}")

    # ----------------------------------------------------------------------
    def pre_interface_generation(self):
        """Create the USD header information and the graph enclosing the node"""
        self.out.write("#usda 1.0")
        self.out.write("(")
        self.out.write(f'    doc ="""Generated from node description file {self.base_name}.ogn')
        self.out.write('Contains templates for node types found in that file."""')
        self.out.write(")")
        self.out.write("")
        self.out.write('def OmniGraph "TestGraph"')
        if self.out.indent("{"):
            self.out.write('token evaluator:type = "push"')
            self.out.write("int2 fileFormatVersion = (1, 3)")
            self.out.write('token flatCacheBacking = "Shared"')
            self.out.write('token pipelineStage = "pipelineStageSimulation"')

    # ----------------------------------------------------------------------
    def post_interface_generation(self):
        """Close the graph definition"""
        self.out.exdent()
        self.out.write("}")


# ======================================================================
def generate_usd(configuration: GeneratorConfiguration) -> Optional[str]:
    """Create support files for the USD template definition for a node

    Args:
        configuration: Information defining how and where the template will be generated

    Returns:
        String containing the generated USD or None if its generation was not enabled

    Raises:
        NodeGenerationError: When there is a failure in the generation of the USD file
    """
    if not configuration.node_interface.can_generate("usd"):
        return None

    logger.info("Generating USD Template File")
    generator = NodeUsdGenerator(configuration)
    generator.generate_interface()
    return str(generator.out)
