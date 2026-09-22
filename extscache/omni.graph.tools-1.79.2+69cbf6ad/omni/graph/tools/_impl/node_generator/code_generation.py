"""Interactive access to the .ogn code generator"""

import json
from typing import Dict, Union

from ..internal.versions import ExtensionVersion_t
from .generate_cpp import generate_cpp
from .generate_documentation import generate_documentation
from .generate_icon import generate_icon
from .generate_python import generate_python
from .generate_template import generate_template
from .generate_tests import generate_tests
from .generate_usd import generate_usd
from .nodes import NodeInterfaceWrapper
from .utils import OGN_PARSE_DEBUG, GeneratorConfiguration, ParseError, Settings


# ==============================================================================================================
def code_generation(
    ogn: Union[str, Dict[str, Dict]],
    class_name: str,
    extension: str,
    module: str,
    settings: Settings = None,
    generator_version_override: ExtensionVersion_t = None,
    target_version_override: ExtensionVersion_t = None,
) -> Dict[str, str]:
    """Run the code generator on the ogn input, which is in the same JSON format as the .ogn file

    Args:
        ogn: Raw OGN data, either in string version or in JSON parsed form
        class_name: Base name for the OGN generated classes. e.g. OgnMyNode
        extension: Extension to which the generated node type will belong
        module: Python module from which the generated node type will be imported
        settings: Optional code generator settings that will modify the type of code generated
        generator_version_override: Generator version to use instead of the one extracted from omni.graph.tools
        target_version_override: Target version to use instead of the one extracted from omni.graph.core

    Returns:
        Dictionary of the generated code. The key value is the type of code, the value is the actual code.
        If no code is generated for a particular key value then it will contain None.

        cpp        = C++ header defining the database for a node implemented in C++
        template   = C++ or Python template implementation
        docs       = .rst format containing the node documentation
        icon       = path to the icon specified in the node description or None
        python     = Python database definition, for both C++ and Python nodes
        tests      = Python code implementing some simple tests on the node
        usd        = Sample USD that defines the node type as a prim template
        node       = Node wrapper object

    Raises:
        ParseError if the ogn dictionary is not parseable as legal OGN data.
    """
    if isinstance(ogn, str):
        try:
            ogn = json.loads(ogn)
        except json.decoder.JSONDecodeError as error:
            raise ParseError("Failed to parse dictionary") from error

    generated_code = {}
    try:
        node_interface_wrapper = NodeInterfaceWrapper(ogn, extension)
        configuration = GeneratorConfiguration(
            None,
            node_interface_wrapper.node_interface,
            extension,
            module,
            class_name,
            None,
            OGN_PARSE_DEBUG,
            settings or Settings(),
            generator_version_override=generator_version_override,
            target_version_override=target_version_override,
        )

        generated_code["icon"] = generate_icon(configuration)
        generated_code["cpp"] = generate_cpp(configuration)
        generated_code["docs"] = generate_documentation(configuration)
        generated_code["python"] = generate_python(configuration)
        generated_code["template"] = generate_template(configuration)
        generated_code["tests"] = generate_tests(configuration)
        generated_code["usd"] = generate_usd(configuration)
        generated_code["node"] = node_interface_wrapper.node_interface

    except ParseError as error:
        raise ParseError("Failed to parse dictionary") from error

    return generated_code
