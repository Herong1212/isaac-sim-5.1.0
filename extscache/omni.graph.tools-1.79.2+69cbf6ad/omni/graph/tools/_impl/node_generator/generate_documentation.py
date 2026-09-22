"""
Support for generating documentation files for OmniGraph Nodes.

The documentation is written in the reStructuredText format, consistent with API documentation.
Note that the script ../make_docs_toc.py relies on parsing the files so if the format changes it must be updated.

Exported Methods:
    generate_documention
    node_link

Exported Constants
    RE_OGN_CATEGORIES
    RE_OGN_NAME_INFO
    RE_OGN_DESCRIPTION_BEGIN
    RE_OGN_DESCRIPTION_END
    RE_OGN_BODY_MARKER
"""

import re
from contextlib import suppress
from pathlib import Path
from typing import List, Optional

from ..deprecate import deprecated_constant_object
from .attributes.AttributeManager import AttributeManager
from .attributes.naming import make_nice_name
from .nodes import NodeInterfaceGenerator
from .utils import GeneratorConfiguration, MetadataKeys, UnimplementedError, logger, rst_csv_table, rst_title

__all__ = [
    "generate_documentation",
    "node_link",
    "RE_OGN_CATEGORIES",
    "RE_OGN_DESCRIPTION_BEGIN",
    "RE_OGN_DESCRIPTION_END",
    "RE_OGN_NAME_INFO",
    "RE_OGN_BODY_MARKER",
]

# Pattern to recognize the name of the node in the file (must coordinate with the output of generate_documentation.py)
_TITLE_OUTPUT = "    :title: {}"
RE_OGN_NAME_INFO = re.compile(f"^{_TITLE_OUTPUT}$".format("(.+)"))

# Patterns for title lines in the file
RE_OGN_DESCRIPTION_TITLE = deprecated_constant_object(
    re.compile("Description$"), "Use RE_OGN_DESCRIPTION_BEGIN instead"
)
RE_OGN_INPUTS_TITLE = deprecated_constant_object(re.compile("Description$"), "Use RE_OGN_DESCRIPTION_END instead")

# Pattern to find the metadata containing the node type categories
RE_OGN_CATEGORIES = re.compile(r'\s*"Categories", "([^"]+)"')

# Pattern marking the body of the description, for easy parsing
_DESCRIPTION_BEGIN = ".. <description>"
RE_OGN_DESCRIPTION_BEGIN = re.compile(f"^{_DESCRIPTION_BEGIN}")
_DESCRIPTION_END = ".. </description>"
RE_OGN_DESCRIPTION_END = re.compile(f"^{_DESCRIPTION_END}")

# Pattern marking the start of the node body
_NODE_LINK_PATTERN = ".. _{}:"
RE_OGN_BODY_MARKER = re.compile(f"^{_NODE_LINK_PATTERN}".format("(.*)"))

# Substitutions for special characters that need escaping in .rst
RST_LITERAL_TRANSLATE = str.maketrans({"*": r"\*"})


# ==============================================================================================================
def node_link(node_id: str, version: int | None = None) -> str:
    """Returns the string representing the link to the node's generated documentation"""
    if version is not None:
        return node_id.replace(".", "_") + f"_{version}"
    return node_id.replace(".", "_")


# ==============================================================================================================
class NodeDocumentationGenerator(NodeInterfaceGenerator):
    """Manage the functions required to generate a C++ interface for a node"""

    def __init__(self, configuration: GeneratorConfiguration):
        """Set up the generator and output the documentation for the node

        Just passes the initialization on to the parent class. See the argument and exception descriptions there.
        """
        logger.info("Creating NodeDocumentationGenerator")
        super().__init__(configuration)
        self._prequel = []
        self._sequel = []
        if configuration.node_file_path:
            prequel_file = Path(configuration.node_file_path).with_suffix(".pre.rst")
            with suppress(IOError):
                with open(prequel_file, "r", encoding="utf-8") as pre_fd:
                    self._prequel = pre_fd.readlines()
            sequel_file = Path(configuration.node_file_path).with_suffix(".post.rst")
            with suppress(IOError):
                with open(sequel_file, "r", encoding="utf-8") as seq_fd:
                    self._sequel = seq_fd.readlines()

    # --------------------------------------------------------------------------------------------------------------
    def interface_file_name(self) -> str:
        """Return the path to the name of the documentation file"""
        return self.base_name + ".rst"

    # --------------------------------------------------------------------------------------------------------------
    def generate_attributes_documentation(self, attributes: List[AttributeManager]):
        """Write out documentation code corresponding to the node

        Args:
            attributes: List of attributes whose documentation is to be generated

        Raises:
            NodeGenerationError: When there is a failure in the generation of the documentation file
        """
        logger.info("Generating documentation for %s attributes", len(attributes))
        # RST tables are very particular about sizing so first find out how big the columns need to be
        attribute_table = [["Name", "Type", "Descripton", "Default"]]
        for attribute in attributes:
            try:
                ui_name = attribute.metadata[MetadataKeys.UI_NAME]
            except KeyError:
                ui_name = make_nice_name(attribute.name)
            name = f"{ui_name} (*{attribute.name}*)"
            try:
                type_name = attribute.ogn_type()
            except AttributeError:
                type_name = "[Unsupported]"
            try:
                default_value = attribute.default
            except UnimplementedError:
                default_value = "[Unsupported]"
            description = attribute.description
            if isinstance(description, list):
                description = " ".join(description)
            description = description.replace("\n", " ")
            attribute_table.append([name, f"``{type_name}``", description, default_value])
            # If there is any metadata add it in name/value pairs below the attribute definition
            for key, value in attribute.metadata.items():
                if key not in [
                    MetadataKeys.DESCRIPTION,
                    MetadataKeys.DEFAULT,
                    MetadataKeys.UI_NAME,
                ] and not key.startswith("__"):
                    attribute_table.append(["", "Metadata", f"*{key}* = {value.translate(RST_LITERAL_TRANSLATE)}", ""])

        self.out.write(rst_csv_table(attribute_table, extra_directives=[":widths: 20, 20, 50, 10"]))

    # --------------------------------------------------------------------------------------------------------------
    def generate_code(self, title: str, code_file_path: str, code_type: str, code_id: str):
        """Generate a code block with the given title containing the contents of the given file

        If the file does not exist then a message to that effect is emitted and no code block is generated
        """
        logger.info("Generating code titled '%s' of type '%s'", title, code_type)
        self.out.write(rst_title(title, 0))
        self.out.write()

        try:
            self.out.write(f".. _{code_id}:\n")
            self.out.write(f".. code:: {code_type}")
            self.out.write()
            self.out.indent()
            with open(code_file_path, "r", encoding="utf-8") as code_fd:
                for code_line in code_fd:
                    self.out.write(code_line.rstrip())
            self.out.exdent()
            self.out.write()
        except FileNotFoundError:
            self.out.write(f"File not found: {code_file_path}")
            return

    # --------------------------------------------------------------------------------------------------------------
    def pre_interface_generation(self):
        """Generate the documentation setup, which is just the link to the top of the generated documentation.
        Two versions of the link are dumped - one is version-specific in case a direct link to a particular version
        is needed. The other has no version so it can be safely linked without the links breaking when the version
        number is changed.
        """
        self.out.write(_NODE_LINK_PATTERN.format(node_link(self.node_interface.name, self.node_interface.version)))
        self.out.write()
        self.out.write(_NODE_LINK_PATTERN.format(node_link(self.node_interface.name)))
        self.out.write()

    # --------------------------------------------------------------------------------------------------------------
    def _generate_header(self):
        """Generate the header section with RST metadata and link label"""
        self.out.write(".. " + "=" * 80)
        self.out.write(".. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.")
        self.out.write(".. " + "=" * 80)
        self.out.write()

        # TODO: When this is picked up automatically by the extension in which it lives the orphan will not be needed
        self.out.write(":orphan:")
        self.out.write()

        keywords = ["lang-en", "omnigraph", "node"]
        categories = self.node_interface.metadata.get(MetadataKeys.CATEGORIES, None) or []
        keywords += categories if isinstance(categories, list) else [categories]
        keywords += self.node_interface.scheduling_hints.flags_set() if self.node_interface.scheduling_hints else []
        node_name_components = self.node_interface.name.split(".")
        if len(node_name_components) > 1:
            keywords.append(node_name_components[-2].lower())
        # Magic conversion of CamelCase to snake-hyphenated-case
        keywords.append(re.sub(r"(?<!^)(?=[A-Z])", "-", node_name_components[-1]).lower())

        self.out.write(".. meta::")
        # Note: If you change this then change RE_OGN_NAME_INFO to match the pattern
        self.out.write(_TITLE_OUTPUT.format(self.node_interface.ui_name))
        self.out.write(f"    :keywords: {' '.join(keywords)}")
        self.out.write()

    # --------------------------------------------------------------------------------------------------------------
    def _generate_title(self):
        """Generate the title section with the node UI name, version number, and description"""
        self.out.write(rst_title(f"{self.node_interface.ui_name}", 0))
        self.out.write()
        self.out.write(_DESCRIPTION_BEGIN)
        self.out.write()  # Need a blank to terminate the comment
        self.out.write(self.node_interface.description)
        self.out.write()
        self.out.write(_DESCRIPTION_END)
        self.out.write()

        if self._prequel:
            self.out.write([line.rstrip() for line in self._prequel])
            self.out.write()

        self.out.write(rst_title("Installation", 1))
        self.out.write()
        extension_link = f"ext_{self.extension}".replace(".", "_")
        ext_link = f":ref:`{self.extension}<{extension_link}>`"
        self.out.write(f"To use this node enable {ext_link} in the Extension Manager.")
        self.out.write()

    # --------------------------------------------------------------------------------------------------------------
    def _generate_metadata(self):
        """Generate the node metadata with various details of the node not directly related to evaluation"""
        # Gather the node metadata for reporting
        node_metadata_table = [["Name", "Value"]]
        node_metadata_table.append(["Unique ID", self.node_interface.name])
        node_metadata_table.append(["Version", self.node_interface.version])
        node_metadata_table.append(["Extension", self.extension])
        if self.node_interface.icon_path is not None:
            node_metadata_table.append(["Icon", self.node_interface.icon_path])
        node_metadata_table.append(["Has State?", self.node_interface.has_state])
        node_metadata_table.append(["Implementation Language", self.node_interface.language])
        node_metadata_table.append(["Default Memory Type", self.node_interface.memory_type])
        excluded = self.node_interface.excluded_generators
        exclusions = ", ".join(excluded) if excluded else "None"
        node_metadata_table.append(["Generated Code Exclusions", exclusions])
        renamed_metadata = {
            MetadataKeys.CATEGORIES: "Categories",
        }
        for key, value in self.node_interface.metadata.items():
            # Some metadata appears in other locations already so skip it here
            if key not in [
                MetadataKeys.EXTENSION,
                MetadataKeys.DESCRIPTION,
                MetadataKeys.EXCLUSIONS,
                MetadataKeys.LANGUAGE,
            ]:
                node_metadata_table.append([renamed_metadata.get(key, key), value])
        node_metadata_table.append(["Generated Class Name", f"{self.base_name}Database"])
        node_metadata_table.append(["Python Module", f"{self.module}"])

        self.out.write(rst_title("Metadata", 1))
        self.out.write(rst_csv_table(node_metadata_table, extra_directives=[":widths: 30,70"]))

    # --------------------------------------------------------------------------------------------------------------
    def generate_node_interface(self):
        """Generate the documentation for the node"""
        logger.info("Generating documentation for node %s", self.node_interface.name)

        self._generate_header()
        self._generate_title()

        attributes = self.node_interface.all_input_attributes()
        if attributes:
            self.out.write(rst_title("Inputs", 1))
            self.generate_attributes_documentation(attributes)
        attributes = self.node_interface.all_output_attributes()
        if attributes:
            self.out.write(rst_title("Outputs", 1))
            self.generate_attributes_documentation(attributes)
        attributes = self.node_interface.all_state_attributes()
        if attributes:
            self.out.write(rst_title("State", 1))
            self.generate_attributes_documentation(attributes)

        self._generate_metadata()

        if self._sequel:
            self.out.write([line.rstrip() for line in self._sequel])
            self.out.write()


# ==============================================================================================================
def generate_documentation(configuration: GeneratorConfiguration) -> Optional[str]:
    """Create support files for the documentation of a node

    Args:
        configuration: Information defining how and where the documentation will be generated

    Returns:
        String containing the generated documentation or None if its generation was not enabled

    Raises:
        NodeGenerationError: When there is a failure in the generation of the documentation file
    """
    if not configuration.node_interface.can_generate("docs"):
        return None
    logger.info("Generating documentation")
    generator = NodeDocumentationGenerator(configuration)
    generator.generate_interface()
    return str(generator.out)
