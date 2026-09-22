# noqa: PLC0302
"""
Support for the various attribute types used in a node description file.

Provides classes that allow generic calls to check attribute information retrieved from the JSON node description
data. The main interface class AttributeManager is used to decipher, validate, and provide access to all
attribute data in the dictionary passed into it.
"""
import io
import json
import os
import re
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Tuple, Union

from ..deprecate import deprecated_function
from .attributes.AttributeManager import AttributeManager
from .attributes.management import get_attribute_manager
from .attributes.naming import (
    INPUT_GROUP,
    INPUT_NS,
    OUTPUT_GROUP,
    OUTPUT_NS,
    STATE_GROUP,
    STATE_NS,
    attribute_name_in_namespace,
    check_attribute_name,
    is_input_name,
    is_output_name,
    is_state_name,
    make_nice_name,
    split_attribute_name,
)
from .category_definitions import merge_category_definitions
from .keys import (
    CudaPointerValues,
    ExclusionTypeValues,
    ExtraTypeValues,
    GraphSetupKeys,
    LanguageTypeValues,
    MemoryTypeValues,
    NodeTypeKeys,
    TestKeys,
)
from .parse_scheduling import SchedulingHints
from .type_definitions import apply_type_definitions
from .utils import (
    GeneratorConfiguration,
    IndentedOutput,
    MetadataKeys,
    ParseError,
    UnimplementedError,
    check_icon_information,
    check_memory_type,
    check_token_name,
    get_metadata_dictionary,
    is_comment,
    logger,
)
from .validators import validate_description

# ======================================================================
# Deprecated - Use the definitions in keys.NodeTypeKeys interface instead
KEY_NODE_DESCRIPTION = NodeTypeKeys.DESCRIPTION
KEY_NODE_EXCLUDE = NodeTypeKeys.EXCLUDE
KEY_NODE_ICON = NodeTypeKeys.ICON
KEY_NODE_INPUTS = NodeTypeKeys.INPUTS
KEY_NODE_LANGUAGE = NodeTypeKeys.LANGUAGE
KEY_NODE_MEMORY_TYPE = NodeTypeKeys.MEMORY_TYPE
KEY_NODE_METADATA = NodeTypeKeys.METADATA
KEY_NODE_OUTPUTS = NodeTypeKeys.OUTPUTS
KEY_NODE_SCHEDULING = NodeTypeKeys.SCHEDULING
KEY_NODE_SINGLETON_METADATA = NodeTypeKeys.SINGLETON
KEY_NODE_STATE = NodeTypeKeys.STATE
KEY_NODE_TAGS_METADATA = NodeTypeKeys.TAGS
KEY_NODE_TESTS = NodeTypeKeys.TESTS
KEY_NODE_TOKENS = NodeTypeKeys.TOKENS
KEY_NODE_UI_NAME_METADATA = NodeTypeKeys.UI_NAME
KEY_NODE_VERSION = NodeTypeKeys.VERSION

# Deprecated - Use the definitions in keys.TestKeys interface instead
KEY_TEST_DESCRIPTION = TestKeys.DESCRIPTION
KEY_TEST_GPU_ATTRIBUTES = TestKeys.GPU_ATTRIBUTES
KEY_TEST_INPUTS = TestKeys.INPUTS
KEY_TEST_OUTPUTS = TestKeys.OUTPUTS
KEY_TEST_SETUP = TestKeys.SETUP
KEY_TEST_STATE = TestKeys.STATE
KEY_TEST_STATE_GET = TestKeys.STATE_GET
KEY_TEST_STATE_SET = TestKeys.STATE_SET

# Deprecated - use the keys.LanguageTypeValues interface instead
LANGUAGE_CPP = LanguageTypeValues.CPP
LANGUAGE_PYTHON = LanguageTypeValues.PYTHON
ALL_LANGUAGES = LanguageTypeValues.ALL

EXCLUSION_TYPES = [value for key, value in vars(ExclusionTypeValues).items() if not key.startswith("__")]
EXTRA_TYPES = [value for key, value in vars(ExtraTypeValues).items() if not key.startswith("__")]
GRAPH_SETUP_KEYS_ALLOWED = [value for key, value in vars(GraphSetupKeys).items() if not key.startswith("__")]

# Pattern for legal node names
# - starts with a letter or underscore
# - then an arbitrary number of alphanumerics or underscores
# - other special characters cause problems in USD and so are disallowed
RE_NODE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_\.]*$")
RE_NODE_NAME_NORMAL = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
NODE_NAME_REQUIREMENT = (
    "Node name '{}' should be CamelCase with letters, numbers, underscores,"
    " with optional '.' to override the namespace'"
)

# UI names can contain pretty much anything - quotes are problematic though so those are disallowed
RE_NODE_UI_NAME = re.compile("^[^'\"]*$")
NODE_UI_NAME_REQUIREMENT = "User-friendly node name cannot contain quotes"

# Helper for namespace related messages
USE_NAMESPACE = f'must begin with "{INPUT_NS}", "{OUTPUT_NS}", or "{STATE_NS}'


# ======================================================================
def check_node_language(node_language: str):
    """Raises a ParseError if the given language name is not legal, else returns the corresponding language key"""
    try:
        new_language = LanguageTypeValues.key_from_text(node_language)
    except ValueError as error:
        raise ParseError() from error
    return new_language


# ======================================================================
def check_node_name(node_name: str):
    """Raises a ParseError if the given node name has an illegal pattern, else returns the node name"""
    name_info = NODE_NAME_REQUIREMENT.format(node_name)

    if not RE_NODE_NAME.match(node_name):
        raise ParseError(name_info)

    return node_name


# ======================================================================
def check_node_ui_name(node_ui_name: str):
    """Raises a ParseError if the given user-friendly node name has an illegal pattern, else returns the node name"""
    if not RE_NODE_UI_NAME.match(node_ui_name):
        raise ParseError(NODE_UI_NAME_REQUIREMENT)
    return node_ui_name


# ======================================================================
def check_node_version(node_version):
    """Raises a ParseError if the given node version is not an integer"""
    if not isinstance(node_version, int):
        raise ParseError(f'Node version "{node_version}" is not an integer')


# ======================================================================
class NodeGenerationError(Exception):
    """Exception to raise when there is an error in the generation of the node interface, tests, or documentation"""


# ======================================================================
@dataclass
class AllAttributes:
    """Container class holding the inputs, outputs, and state attributes in a common structure"""

    inputs: List[AttributeManager]
    outputs: List[AttributeManager]
    state: List[AttributeManager]


# ======================================================================
class NodeTestData:
    """Class that holds the per-node information required to run a single test.

    Attributes:
        input_values: Dictionary of INPUT_ATTR:INPUT_VALUE to set as part of the test
        state_initial_values: Dictionary of STATE_ATTR:STATE_VALUE to set as part of the test
        state_final_values: Dictionary of STATE_ATTR:STATE_VALUE to check as part of the test
        expected_outputs: Dictionary of OUTPUT_ATTR:EXPECTED_VALUE to check as part of the test
        gpu_outputs: List of output attributes expected to be on the GPU at runtime
    """

    def __init__(self):
        """Initialize an empty single node test configuration, to be populated later"""
        self.input_values = {}
        self.state_initial_values = {}
        self.state_final_values = {}
        self.expected_outputs = {}
        self.gpu_outputs = []

    def add_input(self, new_input: AttributeManager, input_value):
        """Add a new input value for the node's test configuration"""
        self.input_values[new_input] = input_value

    def add_output(self, output: str | AttributeManager, output_value):
        """Add a new expected output value for the node's test configuration"""
        if isinstance(output, str):
            self.expected_outputs[f"outputs:{output}"] = output_value
        else:
            self.expected_outputs[output] = output_value

    def add_set_state(self, state: AttributeManager, state_value):
        """Add a new state initialization value for the node's test configuration"""
        self.state_initial_values[state] = state_value

    def add_get_state(self, state: str | AttributeManager, state_value):
        """Add a new state expected value for the node's test configuration"""
        if isinstance(state, str):
            self.state_final_values[f"state:{state}"] = state_value
        else:
            self.state_final_values[state] = state_value

    def set_gpu_outputs(self, gpu_outputs: List[str]):
        """
        Set the list of the node's output attributes that should be read from the GPU,
        where the decision is made at runtime
        """
        self.gpu_outputs = gpu_outputs


# ======================================================================
class TestData:
    """Class that holds the information required to run a single test.

    Attributes:
        file_path: String that specifies the path of a test scene that should be used,
                   either as an absolute path or relative to the location of the .ogn file
                   that asks to use it. None means that an automatic test scene will instead
                   be generated, which will be a PushGraph containing only the node directly
                   associated with the .ogn file (plus any order setup specified via graph_setup).
                   If file_path is set, graph_setup will be ignored.
        graph_setup: Dictionary in the format of og.Controller.edit to create an initial graph for the test
                     None means use the previous setup, without changing anything. If file_path is specified,
                     graph_setup will be ignored.
        node_test_data: Dictionary of NODE_PATH:NODE_TEST_DATA to check as part of the test.
                        NODE_PATH will be populated according to the .ogn test construct specification,
                        and checks will be performed to ensure that said paths correspond to actual
                        nodes in the test scene at file_path. If file_path is None, then NODE_PATH will
                        remain blank.
    """

    def __init__(self):
        """Initialize an empty test configuration, to be populated later"""
        self.file_path = None
        self.graph_setup = None
        self.node_test_data = {}

    def set_file_path(self, file_path: str):
        """Set the test file path"""
        self.file_path = file_path

    def set_graph_setup(self, setup: Dict):
        """Set the dictionary that will be used to create an initial graph for the test."""
        self.graph_setup = setup


# ======================================================================
class NodeInterface:
    """Class constructed from a node interface description to provide an easier method of extracting information

    Attributes:
        name: Name of the node (mandatory)
        __categories_allowed: List of categories the node can legally accept (loaded from the main parser and the node)
        cuda_pointer_type: Where the pointers to GPU arrays are retrieved to
        description: Description of what the node does (mandatory)
        excluded_generators: List of generators the node type does not want to run
        extra_generators: List of generators not normally run that the node type wants to add
        has_cuda_attributes: True if there is at least one input or output attribute that will be accessed from CUDA
        has_inputs: True if __inputs has size > 0 (cached for performance)
        has_outputs: True if __outputs has size > 0 (cached for performance)
        has_state: True if __state has size > 0 (cached for performance)
        icon_path: Location of the node type's icon (None means no icon)
        __inputs: Dictionary of input attributes as (attribute name, AttributeManager)
        language: Language in which the node will be implemented
        memory_type: Default location for attribute memory
        __outputs: Dictionary of output attributes as (attribute name, AttributeManager)
        pedantic (bool): Should more strict checks be made on the interface?
        __state: Dictionary of state attributes as (attribute name, AttributeManager)
        tests: List of TestData containing information describing the set of tests in the file
        version: Version of the described node, as an integer
        config_directory: Path of directory in which to find any configuration files
        exclude_from_coverage (bool): Set to True if the node type is for internal use and does not require coverage
        information to be collected.
    """

    def __init__(
        self,
        node_name: str,
        node_data: dict,
        config_directory: str,
        categories_allowed: Dict[str, str] = None,
        node_directory: Optional[str] = None,
        pedantic: bool = False,
    ):
        """
        Rearrange the node interface description to optimize access for code and documentation generation.

        Args:
            node_name: Name of the node being accessed
            node_data: Dictionary containing the node interface data, as extracted from the JSON
            config_directory: Path to the directory containing the system configuration files
            categories_allowed: Dictionary of name:description of all categories found in the configuration files
            node_directory: Directory in which the node definition lives, None if it does not live in the file system
            pedantic: Should more strict checks be applied to the node interface description?

        Raises:
            ParseError: If there are any errors parsing the node description - string contains the problem
        """
        self.name = node_name
        self.__categories_allowed = categories_allowed if categories_allowed is not None else {}
        self.__node_directory = node_directory
        self.description = None
        self.version = 1
        self.has_cuda_attributes = False
        self.cuda_pointer_type = None
        self.has_inputs = False
        self.has_outputs = False
        self.has_state = False
        self.icon_path = None
        self.memory_type = MemoryTypeValues.CPU
        self.metadata = {}
        self.__inputs = {}
        self.__outputs = {}
        self.pedantic = pedantic
        self.__state = {}
        self.tests = []
        self.tokens = {}
        self.excluded_generators = []
        self.extra_generators = []
        self.language = LanguageTypeValues.CPP
        self.config_directory = config_directory
        self.scheduling_hints = None
        self.exclude_from_coverage = False
        logger.info("Extracting node interface for %s", node_name)

        if not isinstance(node_data, dict):
            raise ParseError(f"Value of node name key {node_name} must be a dictionary")

        # Parse the mandatory description
        try:
            self.description = node_data[NodeTypeKeys.DESCRIPTION]
            logger.info("Extracted description %s", self.description)
        except KeyError:
            raise ParseError(f'"description" value is mandatory for node "{node_name}"') from None

        # Parse the node version number
        with suppress(KeyError):
            check_node_version(node_data[NodeTypeKeys.VERSION])
            self.version = node_data[NodeTypeKeys.VERSION]
            logger.info("Extracted node version -> %s", self.version)

        # Parse the language specification, if any (C++ is the default)
        if NodeTypeKeys.LANGUAGE in node_data:
            logger.info("Extracting the language information")
            self.language = check_node_language(node_data[NodeTypeKeys.LANGUAGE])
            logger.info(" --> Language set to %s", self.language)

        # Parse the node metadata
        with suppress(KeyError):
            self.metadata = get_metadata_dictionary(node_data[NodeTypeKeys.METADATA])
            logger.info("Extracted node metadata")

        # Parse the node memory type
        with suppress(KeyError):
            self.memory_type = check_memory_type(node_data[NodeTypeKeys.MEMORY_TYPE])
            self.metadata[MetadataKeys.MEMORY_TYPE] = self.memory_type
            logger.info("Extracted node memory type -> %s", self.memory_type)

        # Parse the node override icon path, if any
        with suppress(KeyError):
            (self.icon_path, color, background_color, border_color) = check_icon_information(
                node_data[NodeTypeKeys.ICON]
            )
            if color is not None:
                self.metadata[MetadataKeys.ICON_COLOR] = color
            if background_color is not None:
                self.metadata[MetadataKeys.ICON_BACKGROUND_COLOR] = background_color
            if border_color is not None:
                self.metadata[MetadataKeys.ICON_BORDER_COLOR] = border_color
            logger.info("Extracted override icon path -> %s", self.icon_path)

        # See if the node uses the shortcut for the singleton metadata
        with suppress(KeyError):
            singleton = node_data[NodeTypeKeys.SINGLETON]
            logger.info("Extracted %s flag", NodeTypeKeys.SINGLETON)
            if not isinstance(singleton, bool):
                raise ParseError("Singleton value must be a boolean")
            # Metadata can only be a string so change the boolean to a 0/1 value
            if singleton:
                self.metadata[MetadataKeys.SINGLETON] = "1"

        # See if the node has a definition for cuda pointer locations
        with suppress(KeyError):
            self.cuda_pointer_type = node_data[NodeTypeKeys.CUDA_POINTERS]
            if not hasattr(CudaPointerValues, self.cuda_pointer_type.upper()):
                allowed = [value for value in dir(CudaPointerValues) if not value.startswith("_")]
                raise ParseError(f"{NodeTypeKeys.CUDA_POINTERS} is {self.cuda_pointer_type}, must be one of {allowed}")
            logger.info("Extracted %s flag", NodeTypeKeys.CUDA_POINTERS)
        if (
            self.cuda_pointer_type is None
            and self.language == LanguageTypeValues.PYTHON
            and self.memory_type != MemoryTypeValues.CPU
        ):
            raise ParseError("Default value of `cudaPointers` has changed to 'cpu', add explicit setting to 'cuda'")

        # See if the node uses the shortcut for the tags metadata
        with suppress(KeyError):
            tags = node_data[NodeTypeKeys.TAGS]
            logger.info("Extracted node tags")
            if not isinstance(tags, list) and not isinstance(tags, str):
                raise ParseError("Tags must be a comma-separated string or a list of strings")
            # Metadata can only be a string so flatten a list with commas
            if isinstance(tags, list):
                tags = ",".join(tags)
            self.metadata[MetadataKeys.TAGS] = tags

        # See if the node uses the shortcut for the uiName metadata
        with suppress(KeyError):
            ui_name = node_data[NodeTypeKeys.UI_NAME]
            logger.info("Extracted node uiName")
            if not isinstance(ui_name, str):
                raise ParseError("UI Name must be a single string")
            self.metadata[MetadataKeys.UI_NAME] = ui_name

        # See if any token names are to be hardcoded for the node
        with suppress(KeyError):
            raw_tokens = node_data[NodeTypeKeys.TOKENS]
            logger.info("Extracted tokens")
            if isinstance(raw_tokens, str):
                token_list = raw_tokens.split(",")
                self.tokens = {check_token_name(token_name): token_name for token_name in token_list}
            elif isinstance(raw_tokens, list):
                self.tokens = {check_token_name(token): token for token in raw_tokens}
            elif isinstance(raw_tokens, dict):
                self.tokens = {check_token_name(token): value for token, value in raw_tokens.items()}
            else:
                raise ParseError(f"Unknown type of tokens to handle - '{raw_tokens}'")
            # Store the raw tokens as metadata so that they can be retrieved to regenerate the file
            self.metadata[MetadataKeys.TOKENS] = json.dumps(raw_tokens)

        # See if the node is overriding any of the type definitions.
        with suppress(KeyError):
            type_definitions = node_data[NodeTypeKeys.TYPE_DEFINITIONS]
            logger.info("Extracted type definitions")
            # If the data is just a string then assume it is a file and try to load it, checking the configuration
            # directory if it exists.
            if isinstance(type_definitions, str):
                type_definition_path = Path(type_definitions)
                if type_definition_path.is_file():
                    apply_type_definitions(type_definition_path)
                elif not type_definition_path.is_absolute() and self.config_directory is not None:
                    config_dir_type_path = Path(self.config_directory, type_definition_path)
                    if config_dir_type_path.is_file():
                        apply_type_definitions(config_dir_type_path)
                    else:
                        raise ParseError(
                            f"Type definitions file '{type_definitions}' not found in config directory"
                            f" '{self.config_directory}'"
                        )
                else:
                    raise ParseError(f"Type definitions file '{type_definitions}' not found")
            # If the data is a dictionary assume it contains the type definitions directly (should be rare)
            elif isinstance(type_definitions, dict):
                apply_type_definitions({NodeTypeKeys.TYPE_DEFINITIONS: type_definitions})
            else:
                raise ParseError(f"Type definitions only recognize a string or dictionary type - '{type_definitions}'")

        # See if the node is using any extra category definitions.
        with suppress(KeyError):
            category_definitions = node_data[NodeTypeKeys.CATEGORY_DEFINITIONS]
            logger.info("Extracted category definitions")

            def __add_categories(category_spec):
                # If the data is just a string then assume it is a file and try to load it, checking the configuration
                # directory if it exists.
                if isinstance(category_definitions, str):
                    category_definition_path = Path(category_definitions)
                    # If the absolute path exists, prefer that
                    if category_definition_path.is_file():
                        merge_category_definitions(self.__categories_allowed, category_definition_path)
                        return

                    if not category_definition_path.is_absolute():
                        # Check if the path exists relative to the .ogn file's directory
                        if self.__node_directory is not None:
                            config_dir_type_path = Path(self.__node_directory, category_definition_path)
                            if config_dir_type_path.is_file():
                                merge_category_definitions(self.__categories_allowed, config_dir_type_path)
                                return

                        # Check if the path exists relative to the specified config directory
                        if self.config_directory is not None:
                            config_dir_type_path = Path(self.config_directory, category_definition_path)
                            if config_dir_type_path.is_file():
                                merge_category_definitions(self.__categories_allowed, config_dir_type_path)
                                return

                        node_directory_error = (
                            "" if self.__node_directory is None else f" or node file directory '{node_directory}'"
                        )
                        raise ParseError(
                            f"Category definitions file '{category_definitions}' not found in config directory"
                            f" '{self.config_directory}'{node_directory_error}"
                        )

                    raise ParseError(f"Category definitions file '{category_definitions}' not found")

                if isinstance(category_definitions, dict):
                    merge_category_definitions(self.__categories_allowed, category_definitions)
                    return

                raise ParseError(
                    f"Category definitions only recognize a string or dictionary type - '{category_definitions}'"
                )

            if isinstance(category_definitions, list):
                _ = [__add_categories(category_spec) for category_spec in category_definitions]
            else:
                __add_categories(category_definitions)

        # Categories have to be parsed after category definitions
        with suppress(KeyError):
            categories = node_data[NodeTypeKeys.CATEGORIES]

            def __verify_category(category_to_verify: str):
                """Raise an error if the category is not one of the allowed ones"""
                # Automatically exclude nodes categorized as internal test nodes from coverage requirements.
                # This only excludes the generated database though, you still have to exclude the test node
                # implementation class to completely remove it.
                if category_to_verify == "internal:test":
                    self.exclude_from_coverage = True
                if category_to_verify not in self.__categories_allowed:
                    raise ParseError(
                        f"Category {category_to_verify} not in the allowed list {self.__categories_allowed}"
                    )

            category_metadata = None
            new_categories = {}

            if isinstance(categories, str):
                category_metadata = categories
                for category in categories.split(","):
                    __verify_category(category)
            elif isinstance(categories, list):
                category_list = []
                for category_item in categories:
                    if isinstance(category_item, str):
                        category_list.append(category_item)
                    elif isinstance(category_item, dict):
                        category_list += list(category_item.keys())
                        new_categories.update(category_item)
                        merge_category_definitions(self.__categories_allowed, category_item)
                    else:
                        raise ParseError(
                            f"Category description must be a string, dictionary, or list of them - saw {categories}"
                        )
                category_metadata = ",".join(category_list)
                for category in category_list:
                    __verify_category(category)
            elif isinstance(categories, dict):
                new_categories.update(
                    {
                        name: description
                        for name, description in categories.items()
                        if name not in self.__categories_allowed
                    }
                )
                merge_category_definitions(self.__categories_allowed, categories)
                category_metadata = ",".join(sorted(categories.keys()))

            if category_metadata:
                self.metadata[MetadataKeys.CATEGORIES] = category_metadata
            if new_categories:
                # Use a tab as separator and filter them out of the description
                combined_metadata = []
                for name, info in new_categories.items():
                    if name.find(",") >= 0 or name.find("\t") >= 0:
                        raise ParseError(f"Category name '{name}' cannot contain a comma or tab character")
                    safe_info = info.replace("\t", "    ")
                    combined_metadata.append(f"{name},{safe_info}")
                self.metadata[MetadataKeys.CATEGORY_DESCRIPTIONS] = "\t".join(combined_metadata)

            logger.info("Added node type categories -> %s", category_metadata)

        # Parse the generated type exclusions, if any
        with suppress(KeyError):
            excluded = node_data[NodeTypeKeys.EXCLUDE]
            if isinstance(excluded, str):
                excluded = [excluded]
            self.excluded_generators += excluded
            logger.info("Extracted generator inclusions -> %s", self.excluded_generators)

        # Parse the extra generators, if any
        with suppress(KeyError):
            extras = node_data[NodeTypeKeys.EXTRAS]
            if isinstance(extras, str):
                extras = [extras]
            self.extra_generators += extras
            logger.info("Extracted extra generators -> %s", self.extra_generators)

        # Parse the input attributes, if any
        with suppress(KeyError):
            self.__inputs = self.construct_attributes(node_data[NodeTypeKeys.INPUTS], INPUT_NS)
            self.has_inputs = bool(self.__inputs)
            logger.info("Extracted input attributes")

        # Parse the output attributes, if any
        with suppress(KeyError):
            self.__outputs = self.construct_attributes(node_data[NodeTypeKeys.OUTPUTS], OUTPUT_NS)
            self.has_outputs = bool(self.__outputs)
            logger.info("Extracted output attributes")

        # Parse the state attributes, if any
        try:
            self.__state = self.construct_attributes(node_data[NodeTypeKeys.STATE], STATE_NS)
            # Even if no state attributes were constructed, the existence of the state section flags to the
            # node that state information will be used, so that scheduling can take that into account.
            self.has_state = True
            logger.info("Extracted state attributes")
        except KeyError:
            self.has_state = False

        # Parse the attribute allowedToken metadata to include in hardcoded token names.
        for attrib in self.all_attributes():
            if hasattr(attrib, "get_allowed_tokens"):
                self.tokens.update(attrib.get_allowed_tokens())

        # Parse the node scheduling hints
        with suppress(KeyError):
            self.scheduling_hints = SchedulingHints(node_data[NodeTypeKeys.SCHEDULING])
            logger.info("Extracted scheduler hints")

        # Read in the test configurations. Make sure this happens after all attributes are constructed
        try:
            test_list = node_data[NodeTypeKeys.TESTS]
            self.construct_tests(test_list)
            logger.info("Extracted %s node tests", len(test_list))
        except (KeyError, UnimplementedError):
            self.tests = []  # Remove any partially constructed tests

        # For long strings the description will be a list to be concatenated (due to the
        # limited ways JSON can represent long strings). If that's the case convert back to a single string.
        if self.pedantic:
            errors = validate_description(self.description)
            if errors:
                for error in errors:
                    logger.warning("[PEDANTIC] for node type %s - %s", self.name, str(error))
        if isinstance(self.description, list):
            self.description = " ".join(self.description)
            self.description = self.description.replace("\n ", "\n")
        self.metadata[MetadataKeys.DESCRIPTION] = self.description
        if self.excluded_generators:
            self.metadata[MetadataKeys.EXCLUSIONS] = ",".join(self.excluded_generators)
        if self.language != LanguageTypeValues.CPP:
            self.metadata[MetadataKeys.LANGUAGE] = self.language

        # Empty descriptions are anti-social
        if not self.description:
            warning = "Node description should not be empty"
            if os.getenv("OGN_STRICT_DEBUG"):
                raise ParseError(warning)

            print(f"WARNING: {warning}", flush=True)

    # ----------------------------------------------------------------------
    @property
    def ui_name(self) -> str:
        """Returns the UI name as defined by the metadata if it exists, otherwise just the name used for ID"""
        try:
            return self.metadata[MetadataKeys.UI_NAME]
        except KeyError:
            # Generate a sensible UI name. Do not include the namespace.
            return make_nice_name(self.name.split(".")[-1])

    # ----------------------------------------------------------------------
    def add_test(
        self,
        test_data: TestData,
        node_path: str,
        attribute_name: str,
        attribute_namespace: str,
        attribute_value,
        in_set: bool,
        is_test_file_specified: bool,
    ):
        """Extract Python-compatible information for an attribute based on its JSON name, type, and value.

        Args:
            test_data: Object containing the current test data - updated based on the information passed in
            node_path: Path to the node in the test scene. Can be blank if no test scene has been specified.
            attribute_name: Raw attribute name, may or may not include the namespace
            attribute_namespace: Expected namespace of the attribute
            attribute_value: Value to be read or written to the attribute - must be compatible to the attribute type
            in_set: If True and the namespace is STATE_GROUP then put the value in the set of values to be set on state
                 attributes before the test begins, otherwise put it on the set of values to check after the test ends
            is_test_file_specified: True if the given test has an associated test scene that needs loading.
        """
        if node_path not in test_data.node_test_data:
            test_data.node_test_data[node_path] = NodeTestData()

        # Rely on called methods to properly raise formatting exceptions, if any.
        # Some of these checks we should only perform if a test scene has not been
        # specified in the .ogn test construct. Note that, depending on the presence of a test file,
        # we either pass in the AttributeManager directly (which gives us access to more information
        # regarding said attribute such as where it lives in memory, since this data can be extracted
        # from the single node's .ogn file that is being tested), or just the attribute name (since
        # the attribute information typically provided via the AttributeManager won't be natively
        # available from the single .ogn that the test construct resides in for any OTHER nodes in the
        # test scene).
        if is_test_file_specified:
            value_for_test = attribute_value
            if attribute_namespace == OUTPUT_NS:
                test_data.node_test_data[node_path].add_output(attribute_name, value_for_test)
            else:
                test_data.node_test_data[node_path].add_get_state(attribute_name, value_for_test)
        else:
            name_in_namespace = attribute_name_in_namespace(attribute_name, attribute_namespace)
            (attribute, attribute_group) = self.attribute_by_name(name_in_namespace)
            attribute.validate_value_structure(attribute_value)
            value_for_test = attribute.value_for_test(attribute_value)

            if attribute_group == INPUT_GROUP:
                test_data.node_test_data[node_path].add_input(attribute, value_for_test)
            elif attribute_group == OUTPUT_GROUP:
                test_data.node_test_data[node_path].add_output(attribute, value_for_test)
            elif in_set:
                test_data.node_test_data[node_path].add_set_state(attribute, value_for_test)
            else:
                test_data.node_test_data[node_path].add_get_state(attribute, value_for_test)

    # --------------------------------------------------------------------------------------------------------------
    def __add_value_to_test(
        self,
        test_data: TestData,
        node_path: str,
        raw_attribute_name: str,
        attribute_value: Any,
        attributes: AllAttributes,
        is_test_file_specified: bool,
    ):
        """Add a single value for getting or setting to the test.

        Args:
            test_data: Test to be amended.
            node_path: Path to the node in the test scene. Can be blank if no test scene has been specified.
            raw_attribute_name: Full specification of attribute to be in the test.
            attribute_value: Value to bet set or tested on the attribute.
            attributes: Attribute managers of all types participating in the test.
            is_test_file_specified: Whether or not a test file exists for the current test.
        """
        # Strip the suffix from the state namespace and set the flag to indicate if it is get or set
        is_setting = False
        attribute_name = raw_attribute_name
        if raw_attribute_name.startswith(f"{STATE_NS}_get"):
            attribute_name = raw_attribute_name.replace("_get", "")
        elif raw_attribute_name.startswith(f"{STATE_NS}_set"):
            attribute_name = raw_attribute_name.replace("_set", "")
            is_setting = True

        # Allow specification of the bare attribute name, so long as there are no conflicts with the same name
        # in multiple namespaces. The extra filtering is only done if a test scene is not specified, since we
        # can then compare the existing .ogn node attributes to the test specification directly.
        if not is_test_file_specified:
            if (
                not is_input_name(attribute_name)
                and not is_output_name(attribute_name)
                and not is_state_name(attribute_name)
            ):
                if attribute_name in attributes.inputs and attribute_name in attributes.outputs:
                    raise ParseError(
                        f'Test attribute "{attribute_name}" is both an input and an output {USE_NAMESPACE}'
                    )
                if attribute_name in attributes.inputs and attribute_name in attributes.state:
                    raise ParseError(f'Test attribute "{attribute_name}" is both an input and a state {USE_NAMESPACE}')
                if attribute_name in attributes.outputs and attribute_name in attributes.state:
                    raise ParseError(f'Test attribute "{attribute_name}" is both an output and a state {USE_NAMESPACE}')
                if attribute_name in attributes.inputs:
                    self.add_test(
                        test_data, node_path, attribute_name, INPUT_NS, attribute_value, False, is_test_file_specified
                    )
                elif attribute_name in attributes.outputs:
                    self.add_test(
                        test_data, node_path, attribute_name, OUTPUT_NS, attribute_value, False, is_test_file_specified
                    )
                elif attribute_name in attributes.state:
                    # Using this shortcut assume the state value is to be checked, not set
                    self.add_test(
                        test_data,
                        node_path,
                        attribute_name,
                        STATE_NS,
                        attribute_value,
                        is_setting,
                        is_test_file_specified,
                    )
                else:
                    raise ParseError(f"Test attribute {attribute_name} not recognized")
            else:
                (namespace, base_name) = split_attribute_name(attribute_name)
                # Assume the namespace is correct if specified
                if namespace == INPUT_NS and base_name not in attributes.inputs:
                    raise ParseError(f'Namespaced attribute "{attribute_name}" not an input')
                if namespace == OUTPUT_NS and base_name not in attributes.outputs:
                    raise ParseError(f'Namespaced attribute "{attribute_name}" not an output')
                if namespace.startswith(STATE_NS) and base_name not in attributes.state:
                    raise ParseError(f'Namespaced attribute "{attribute_name}" not a state')
                if namespace not in [INPUT_NS, OUTPUT_NS, STATE_NS]:
                    raise ParseError(f'Test attribute "{attribute_name}" has illegal namespace "{namespace}"')
                self.add_test(
                    test_data, node_path, attribute_name, namespace, attribute_value, is_setting, is_test_file_specified
                )
        else:
            (namespace, base_name) = split_attribute_name(attribute_name)
            self.add_test(
                test_data, node_path, base_name, namespace, attribute_value, is_setting, is_test_file_specified
            )

    # ----------------------------------------------------------------------
    def __check_for_nested_namespace_attributes(self, test_info: Dict):
        """
        Helper method that's used in tests with an external file to check that said test does
        not contain any nested namespaced attributes that have not been commented out/do not follow
        the required formatting convention for .ogn's with specific test scenes (specifically that
        all attributes need to be associated with a specific node path in the test scene).

        Args:
            test_info: Test data in one of the few allowed forms.
        """
        for test_key in TestKeys.ALL:
            if test_key not in test_info:
                continue

            if test_key not in [TestKeys.DESCRIPTION, TestKeys.FILE, TestKeys.GPU_ATTRIBUTES]:
                raise ParseError(
                    "Namespaced attributes without an enclosing node path object are not allowed in tests with a test file."
                )

    # ----------------------------------------------------------------------
    def __process_has_file_case_one(self, test_data: TestData, raw_node_path: str, raw_node_path_value: any):
        """
        Helper method for processing formatting case 1 for .ogn tests
        that ingest an external test file.

        Case 1: The key is the node path, and the value is a dictionary containing the node
        outputs and states that will be checked for equivalence (which in turn can
        also be dictionaries), e.g.:

        {
            "/MyGraph/MyNode": {
                "outputs": {
                    "OutputAttr0": ExpectedValue0,
                    "OutputAttr1": ExpectedValue1
                },
                "state": {
                    "StateAttr": ExpectedState
                }
            }
        }

        Args:
            test_data: Test to be amended.
            raw_node_path: Path to the node in the test scene (plus potentially some attribute information).
            raw_node_path_value: Attribute information associated with the node at the given path.
        """
        if TestKeys.INPUTS in raw_node_path_value:
            raise ParseError(
                f'"{TestKeys.INPUTS}" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
            )

        if TestKeys.OUTPUTS in raw_node_path_value:
            for output_name, output_value in raw_node_path_value[TestKeys.OUTPUTS].items():
                if output_name[0] != "$":
                    self.add_test(test_data, raw_node_path, output_name, OUTPUT_NS, output_value, False, True)

        if TestKeys.SETUP in raw_node_path_value:
            raise ParseError(
                f'"{TestKeys.SETUP}" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
            )

        if TestKeys.STATE in raw_node_path_value:
            for state_name, state_value in raw_node_path_value[TestKeys.STATE].items():
                if state_name[0] != "$":
                    self.add_test(test_data, raw_node_path, state_name, STATE_NS, state_value, False, True)

        if TestKeys.STATE_GET in raw_node_path_value:
            for state_name, state_value in raw_node_path_value[TestKeys.STATE_GET].items():
                if state_name[0] != "$":
                    self.add_test(test_data, raw_node_path, state_name, STATE_NS, state_value, False, True)

        if TestKeys.STATE_SET in raw_node_path_value:
            raise ParseError(
                f'"{TestKeys.STATE_SET}" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
            )

    # ----------------------------------------------------------------------
    def __process_has_file_case_two(
        self, test_data: TestData, raw_node_path: str, raw_node_path_value: any, attributes: AllAttributes
    ):
        """
        Helper method for processing formatting case 2 for .ogn tests
        that ingest an external test file.

        Case 2: The key is the node path, and the value is the compressed version
        of the attribute at hand, e.g.:

        {
            "/MyGraph/MyNode": {
                "outputs.OutputAttr0": ExpectedValue0,
                "outputs.OutputAttr1": ExpectedValue1,
                "state.StateAttr": ExpectedState
            }
        }

        Note that Case 2 attributes will overwrite duplicate Case 1 attributes,
        e.g. if we specified both "/MyGraph/MyNode": { "outputs": { "OutputAttr0": ExpectedValue0 } }
        and "/MyGraph/MyNode": { "outputs.OutputAttr0": ExpectedValue1 }, the latter would override
        the former and we'd be checking for an expected output value of ExpectedValue0.

        Args:
            test_data: Test to be amended.
            raw_node_path: Path to the node in the test scene (plus potentially some attribute information).
            raw_node_path_value: Attribute information associated with the node at the given path.
            attributes: Attribute managers of all types participating in the test.
        """
        for raw_attribute_name, attribute_value in raw_node_path_value.items():
            if raw_attribute_name in TestKeys.ATTRIBUTES:
                continue

            if raw_attribute_name[0] == "$":
                continue

            if raw_attribute_name.startswith("inputs:"):
                raise ParseError(
                    f'"inputs:" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
                )
            if raw_attribute_name.startswith("state_set:"):
                raise ParseError(
                    f'"state_set:" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
                )
            if (
                raw_attribute_name.startswith("state:")
                or raw_attribute_name.startswith("state_get:")
                or raw_attribute_name.startswith("outputs:")
            ):
                self.__add_value_to_test(
                    test_data, raw_node_path, raw_attribute_name, attribute_value, attributes, True
                )
                continue
            raise ParseError(
                f'Unrecognized attribute namespace for entry "{raw_attribute_name}" associated with "{raw_node_path}".'
            )

    # ----------------------------------------------------------------------
    def __process_has_file_case_three(
        self,
        test_data: TestData,
        raw_node_path: str,
        raw_node_path_value: any,
        split_name: str,
        attr_type: str,
        attr_namespace: str,
    ):
        """
        Helper method for processing formatting case 3 for .ogn tests
        that ingest an external test file.

        Case 3: The key is the node path + attribute namespace, and the value is a dictionary
        containing the node's corresponding attributes and values, e.g.:

        {
            "/MyGraph/MyNode.outputs": {
                "OutputAttr0": ExpectedValue0,
                "OutputAttr1": ExpectedValue1
            },
            "/MyGraph/MyNode.state": {
                "StateAttr": ExpectedState
            }
        }

        Args:
            test_data: Test to be amended.
            raw_node_path: Path to the node in the test scene (plus potentially some attribute information).
            raw_node_path_value: Attribute information associated with the node at the given path.
            split_name: A version of raw_node_path that's been split with attribute namespaces.
            attr_type: The attribute type that was used to split the raw_node_path (e.g., ".inputs").
            attr_namespace: The corresponding attribute namespace for the aforementioned attribute
                            type (e.g., ".inputs" is associated with INPUT_NS).
        """
        if attr_type not in raw_node_path:
            return

        if attr_namespace == INPUT_NS:
            raise ParseError(
                f'"{TestKeys.INPUTS}" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
            )

        if attr_namespace == OUTPUT_NS:
            for output_name, output_value in raw_node_path_value.items():
                if output_name[0] != "$":
                    self.add_test(test_data, split_name[0], output_name, OUTPUT_NS, output_value, False, True)
            return

        if attr_namespace == STATE_NS:
            if split_name[1].startswith("_set"):
                raise ParseError(
                    f'"{TestKeys.STATE_SET}" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
                )
            for state_name, state_value in raw_node_path_value.items():
                if state_name[0] != "$":
                    self.add_test(test_data, split_name[0], state_name, STATE_NS, state_value, False, True)
            return

        raise ParseError(
            f'Unrecognized attribute namespace for entry "{attr_namespace}" associated with "{raw_node_path}".'
        )

    # ----------------------------------------------------------------------
    def __process_has_file_case_four(
        self, test_data: TestData, raw_node_path: str, raw_node_path_value: any, split_name: str, attr_namespace: str
    ):
        """
        Helper method for processing formatting case 4 for .ogn tests
        that ingest an external test file.

        Case 4: The key is the fully-compressed node path + attribute, and the value
        is the actual attribute value, e.g.:

        {
            "/MyGraph/MyNode.outputs:OutputAttr0" : ExpectedValue,
            "/MyGraph/MyNode.outputs:OutputAttr1" : ExpectedValue,
            "/MyGraph/MyNode.state:StateAttr" : ExpectedState
        }

        Args:
            test_data: Test to be amended.
            raw_node_path: Path to the node in the test scene (plus potentially some attribute information).
            raw_node_path_value: Attribute information associated with the node at the given path.
            split_name: A version of raw_node_path that's been split with attribute namespaces.
            attr_namespace: The corresponding attribute namespace for the attribute
                            type that was used to split raw_node_path.
        """
        if attr_namespace == INPUT_NS:
            raise ParseError(
                f'"{TestKeys.INPUTS}" namespaced attributes are not allowed in the specification for "{raw_node_path}".'
            )
        if split_name[1][0] != ":":
            raise ParseError(f'Test attribute "{raw_node_path}" is misconfigured; missing a colon.')
        self.add_test(test_data, split_name[0], split_name[1][1:], attr_namespace, raw_node_path_value, False, True)

    # ----------------------------------------------------------------------
    def __process_does_not_have_file_case_one(self, test_info: Dict, test_data: TestData):
        """
        Helper method for processing formatting case 1 for .ogn tests
        that do not have an external test file.

        Case 1: The key is the attribute namespace/keyword (e.g., "inputs", "setup", etc.),
        and the value is a dictionary containing the relevant information - key-value pairs
        of attribute names and their corresponding values, e.g.:

        {
            "description": "Optional, and to be ignored",
            "inputs": {
                "InputAttr": "ValueToSet"
            },
            "outputs": {
                "OutputAttr": "ExpectedValue"
            },
            "state_set": {
                "StateAttr": "InitialState"
            },
            "state_get": {
                "StateAttr": "ExpectedState"
            },
            "setup": {
                "nodes": ["TestNode", "omni.examples.myNode"]
            }
        }

        Args:
            test_info: Test data in one of the few allowed forms.
            test_data: Test to be amended.
        """
        if TestKeys.INPUTS in test_info:
            for input_name, input_value in test_info[TestKeys.INPUTS].items():
                if input_name[0] != "$":
                    self.add_test(test_data, "", input_name, INPUT_NS, input_value, False, False)

        if TestKeys.OUTPUTS in test_info:
            for output_name, output_value in test_info[TestKeys.OUTPUTS].items():
                if output_name[0] != "$":
                    self.add_test(test_data, "", output_name, OUTPUT_NS, output_value, False, False)

        with suppress(KeyError):
            setup = test_info[TestKeys.SETUP]
            for key in setup:
                if key not in GRAPH_SETUP_KEYS_ALLOWED:
                    raise ParseError(f"Graph setup key '{key}' not in the allowed set {GRAPH_SETUP_KEYS_ALLOWED}")
            test_data.set_graph_setup(setup)

        if TestKeys.STATE in test_info:
            for state_name, state_value in test_info[TestKeys.STATE].items():
                if state_name[0] != "$":
                    self.add_test(test_data, "", state_name, STATE_NS, state_value, False, False)

        if TestKeys.STATE_GET in test_info:
            for state_name, state_value in test_info[TestKeys.STATE_GET].items():
                if state_name[0] != "$":
                    self.add_test(test_data, "", state_name, STATE_NS, state_value, False, False)

        if TestKeys.STATE_SET in test_info:
            for state_name, state_value in test_info[TestKeys.STATE_SET].items():
                if state_name[0] != "$":
                    self.add_test(test_data, "", state_name, STATE_NS, state_value, True, False)

    # ----------------------------------------------------------------------
    def __process_does_not_have_file_case_two(self, test_info: Dict, test_data: TestData, attributes: AllAttributes):
        """
        Helper method for processing formatting case 2 for .ogn tests
        that do not have an external test file.

        Case 2: The attribute namespaces, names, and values are compressed
        into a single key-value pair, e.g.:

        {
            "inputs:InputAttr": "ValueToSet"
            "outputs:OutputAttr": "ExpectedValue",
            "state_set:StateAttr": "InitialState",
            "state:StateAttr": "ExpectedState"
        }

        Args:
            test_info: Test data in one of the few allowed forms.
            test_data: Test to be amended.
            attributes: Attribute managers of all types participating in the test.
        """
        for raw_attribute_name, attribute_value in test_info.items():
            # Check to make sure this isn't the attribute grouping rather than an actual name, to parse the simple form
            if raw_attribute_name in TestKeys.ALL:
                continue

            if raw_attribute_name[0] != "$":
                self.__add_value_to_test(test_data, "", raw_attribute_name, attribute_value, attributes, False)

    # ----------------------------------------------------------------------
    def __process_gpu_outputs(self, test_data: TestData, potential_gpu_outputs: List[str], has_file: bool):
        """
        Helper method for parsing "gpu" key-value pairs.

        When an external test scene is utilized, the value needs to take the
        form of a list of node paths concatenated with the "outputs" attribute
        namespace and the attribute name, e.g.:
        "gpu": ["/MyGraph/Node0.outputs:a", "/MyGraph/Node1.outputs:b"]

        When no external scene is used, the value needs to only take the form
        of a list of "outputs" attribute namespaces concatenated with the
        attribute name, since there's no ambiguity in which attribute belongs
        to which node, e.g.:
        "gpu": ["outputs:a", "outputs:b"]

        Note that we can specify gpu_outputs for a node for which we do not
        specify any actual output data. This will still generate a
        node_path : NodeTestData() entry as part of the test, but will not
        actually get utilized in a non-trivial fashion since the NodeTestData()
        object will not have any expected outputs for subsequent runtime data
        comparisons.

        Args:
            test_data: Test to be amended.
            potential_gpu_outputs: The raw list of gpu outputs before processing.
            has_file: Whether or not the test uses an external file.
        """
        node_path = ""

        # GPU attribute must be a list of strings.
        if not all(isinstance(s, str) for s in potential_gpu_outputs):
            raise ParseError('"gpu" attribute must be a list of strings.')

        for potential_attr_path in potential_gpu_outputs:
            if has_file:
                split_name = potential_attr_path.split(".outputs:", 1)
                if len(split_name) != 2 or (len(split_name) == 2 and not "".join(split_name[0].split())):
                    raise ParseError(
                        '"gpu" list can only contain "outputs" node attributes that are appended to a path to a node in the test scene.'
                    )
                node_path = split_name[0]
            else:
                if not potential_attr_path.startswith("outputs:"):
                    raise ParseError('"gpu" list can only contain "outputs" node attributes.')
                node_path = ""

            # Add a new node test data element if it does not exist.
            if node_path not in test_data.node_test_data:
                test_data.node_test_data[node_path] = NodeTestData()
            test_data.node_test_data[node_path].gpu_outputs.append(potential_attr_path)

    # ----------------------------------------------------------------------
    def create_test_from_raw_data(self, test_info: Dict, attributes: AllAttributes):
        """Return a normalized set of test data as parsed from the few allowed formats.

        Test data can appear in roughly four different forms: expanded with a test scene, compressed
        with a test scene, expanded without a test scene, and compressed without a test scene.

        In the "expanded with a test scene" form, we have a path pointing to a specific test
        scene to use for the node, along with dictionaries of node paths (in the test scene)
        that in turn each contain separate dictionaries of their inputs, outputs, and state:
            {
                "description": "Optional, and to be ignored",
                "file": "TestFileForMyNode.usda",
                "/MyGraph/MyNode": {
                    "outputs": {
                        "OutputAttr": "ExpectedValue"
                    },
                    "state_get": {
                        "StateAttr": "ExpectedState"
                    }
                },
                "/MyGraph/AnotherNode": {
                    "outputs": {
                        "AnotherOutputAttr": "AnotherExpectedValue"
                    }
                },
                "gpu": ["/MyGraph/AnotherNode.outputs:AnotherOutputAttr"]
            }

        In the "compressed with a test scene" form, we again have a path pointing to a specific
        test scene to use for the node, but this time collapse the dictionary entries so that
        every node attribute is represented with a single key-value pair like so:
            {
                "description": "Optional, and to be ignored",
                "file": "TestFileForMyNode.usda",
                "/MyGraph/MyNode.outputs:OutputAttr": "ExpectedValue",
                "/MyGraph/MyNode.state:StateAttr": "ExpectedState",
                "/MyGraph/AnotherNode.outputs:AnotherOutputAttr": "AnotherExpectedValue",
                "gpu": ["/MyGraph/AnotherNode.outputs:AnotherOutputAttr"]
            }

        Note that a blend between the two extremes is also allowed, e.g., the following syntax
        would also be valid:
            {
                "description": "Optional, and to be ignored",
                "file": "TestFileForMyNode.usda",
                "/MyGraph/MyNode.outputs": {
                    "OutputAttr": "ExpectedValue"
                },
                "/MyGraph/MyNodes.state_get": {
                    "StateAttr": "ExpectedState"
                },
                "/MyGraph/AnotherNode": {
                    "outputs:AnotherOutputAttr": "AnotherExpectedValue"
                },
                "gpu": ["/MyGraph/AnotherNode.outputs:AnotherOutputAttr"]
            }
        These are listed as two separate cases in our internal helper methods.

        In the "expanded without a test scene" format, the test file name is omitted, and
        the dictionary only contains inputs, outputs, and state in separate dictionaries. These
        attributes should directly correspond to attributes on the node in the .ogn file that
        the test construct lives in:
            {
                "description": "Optional, and to be ignored",
                "inputs": {
                    "InputAttr": "ValueToSet"
                },
                "outputs": {
                    "OutputAttr": "ExpectedValue"
                },
                "state_set": {
                    "StateAttr": "InitialState"
                },
                "state_get": {
                    "StateAttr": "ExpectedState"
                },
                "setup": {
                    "nodes": ["TestNode", "omni.examples.myNode"]
                },
                "gpu": ["outputs:OutputAttr"]
            }

        Finally, in the "compressed without a test scene" form, the file name is again not included
        (meaning that all specified attributes need to be ones that are defined for the node in the .ogn
        file), but the attribute dictionaries are collapsed so that attributes use their full namespace
        in a single dictionary, with state attributes splitting into "state" or "state_get" for expected
        values and "state_set" for initial values:
            {
                "inputs:InputAttr": "ValueToSet"
                "outputs:OutputAttr": "ExpectedValue",
                "state_set:StateAttr": "InitialState",
                "state:StateAttr": "ExpectedState",
                "gpu": ["outputs:OutputAttr"]
            }

        Formats with a test scene are not compatible with formats that do not specify a test scene;
        a mix between the expanded and compressed versions of each (i.e. expanded and compressed formats
        with a test scene, expanded and compressed formats without a test scene), will be accepted, though there is
        no reason to use that approach.

        It is also acceptable if the expanded formats specify attributes names as "inputs:InputAttr", though
        self-defeating for shortening the input data.

        In addition, for tests that do not use a test scene, if the attribute names are unique then the namespace can
        be omitted. i.e. "inputs:x1" and "outputs:x2" can be shortened to "x1" and "x2", but "inputs:a1" and
        "outputs:a1" must be fully qualified. Note that this shortcut cannot be applied to tests utilizing an
        external test scene, since those tests allow for attribute checks against nodes other than the one being
        defined in the current .ogn file, thus making it difficult to determine the namespace in which a given attribute
        should belong in (i.e. if the attribute on the node being checked is an output or a state).

        If a test scene is specified, then the corresponding test structure will not allow the setting
        of node inputs/state directly; it is assumed that the test scene already handles this.

        The "gpu" key can be used to specify any node output attributes whose values should be expected to reside
        on the GPU by the end of the test. Note that the "gpu" key only accepts such output attribute specifications
        with their most complete/verbose name:
        - If no external test scene is being used, then the attributes must be specified as "outputs:myOutputAttr"
          in the list.
        - If an external test scene is being used, then the attributes must be specified as
          "/Path/To/MyNode.outputs:myOutputAttr in the list.

        The optional "description" field is removed and the format is modified if necessary to the simplified form.

        Args:
            test_info: Test data in one of the few allowed forms
            attributes: List of all legal input, output, and state attribute managers for the node in the .ogn file
                        ONLY.

        Note:
            For the purposes of this test only the initial state values of any given node can be checked. If you wish to
            check for state changes you must write a separate test script that evaluates multiple times.

        Returns:
            test_info normalized to remove ignored fields and put into the simplified format.

        Raises:
            ParseError: If the formatting of the test clause was not correct.
        """
        test_data = TestData()
        has_file = False

        # Check if we have a valid, uncommented test file specified. Different parsing
        # logic will need to be implemented depending on whether or not such a file
        # is passed for a given test.
        if TestKeys.FILE in test_info:
            file_path = test_info[TestKeys.FILE]
            if not isinstance(file_path, str):
                raise ParseError(f'Test attribute {TestKeys.FILE}\'s value must be of type "string".')
            # Comments are marked by a leading "$" and can appear anywhere, even among attribute data
            if file_path[0] != "$":
                has_file = True
                test_data.file_path = file_path

        # Process any "gpu" key-value pairs.
        if TestKeys.GPU_ATTRIBUTES in test_info:
            gpu_list = test_info[TestKeys.GPU_ATTRIBUTES]
            if not isinstance(gpu_list, list):
                gpu_list = [gpu_list]
            self.__process_gpu_outputs(test_data, gpu_list, has_file)

        if has_file:
            # Check that the rest of the test does not contain any nested namespaced attributes that have not
            # been commented out/do not follow the required formatting convention for .ogn's with specific test
            # scenes. We assume that all subsequent attributes are paths to various nodes in the scene with attached
            # input/output/state attributes (either directly emplaced within the string key, or as separate
            # dictionaries).
            self.__check_for_nested_namespace_attributes(test_info)

            # Loop through all other (assumed) node path attributes in the test_info dictionary, processing them
            # differently according to the key-value formatting. Note that node input/setup/state attributes cannot
            # be set using this format ("this format" referring to the one that ingests an external test file).
            for raw_node_path, raw_node_path_value in test_info.items():
                # Skip all description keys, file keys, GPU keys, and comments.
                if raw_node_path in [TestKeys.DESCRIPTION, TestKeys.FILE, TestKeys.GPU_ATTRIBUTES]:
                    continue
                if raw_node_path[0] == "$":
                    continue

                # Check if the attribute namespace shows up as part of the raw_node_path.
                attr_type = None
                attr_namespace = None
                if ".inputs" in raw_node_path:
                    attr_type = ".inputs"
                    attr_namespace = INPUT_NS
                elif ".outputs" in raw_node_path:
                    attr_type = ".outputs"
                    attr_namespace = OUTPUT_NS
                elif ".state" in raw_node_path:
                    attr_type = ".state"
                    attr_namespace = STATE_NS

                # Process formatting cases one and two for tests with an external file.
                if not attr_type and not attr_namespace:
                    self.__process_has_file_case_one(test_data, raw_node_path, raw_node_path_value)
                    self.__process_has_file_case_two(test_data, raw_node_path, raw_node_path_value, attributes)
                    continue

                # Process formatting cases three and four for tests with an external file.
                split_name = raw_node_path.split(attr_type, 1)
                if len(split_name) == 1 or (
                    len(split_name) == 2
                    and (
                        not "".join(split_name[1].split())
                        or split_name[1].startswith("_get")
                        or split_name[1].startswith("_set")
                    )
                ):
                    self.__process_has_file_case_three(
                        test_data, raw_node_path, raw_node_path_value, split_name, attr_type, attr_namespace
                    )
                elif len(split_name) == 2 and "".join(split_name[1].split()):
                    self.__process_has_file_case_four(
                        test_data, raw_node_path, raw_node_path_value, split_name, attr_namespace
                    )

        else:
            # Process formatting cases one and two for tests without an external file.
            self.__process_does_not_have_file_case_one(test_info, test_data)
            self.__process_does_not_have_file_case_two(test_info, test_data, attributes)

        return test_data

    # ----------------------------------------------------------------------
    def construct_tests(self, test_list: List[Dict]):
        """Construct the internal list of test configurations from their description"""
        attributes = AllAttributes(
            [split_attribute_name(attribute)[1] for attribute, _ in self.__inputs.items()],
            [split_attribute_name(attribute)[1] for attribute, _ in self.__outputs.items()],
            [split_attribute_name(attribute)[1] for attribute, _ in self.__state.items()],
        )

        # Convert the JSON-based test data to something that can be output as Python
        for test_information in test_list:
            self.tests.append(self.create_test_from_raw_data(test_information, attributes))

    # ----------------------------------------------------------------------
    def construct_attributes(self, attribute_interfaces: dict, namespace: str) -> Dict[str, AttributeManager]:
        """Create attribute interface classes for every attribute in the description dictionary

        Args:
            attribute_interfaces: Dictionary of (attribute name, dictionary) from which to extract interfaces
            namespace: Prefix for attribute names in this interface; will be prepended to the name if missing

        Returns:
            A dictionary of (attribute name, AttributeManager) extracted from the attribute interface list
        """
        extracted_interfaces = {}
        logger.info("Construct attributes from interface %s", attribute_interfaces)
        for raw_attribute_name, attribute_data in attribute_interfaces.items():
            if raw_attribute_name[0] == "$":  # Special IDs are not actual attributes
                logger.info("Ignoring comment tagged %s", raw_attribute_name)
                continue
            # Allow namespace to be already on the name, and ensure it is present either way
            attribute_name = attribute_name_in_namespace(raw_attribute_name, namespace)
            (_, _) = check_attribute_name(attribute_name, self.language)

            if attribute_name in extracted_interfaces:
                raise ParseError(f'Attribute "{raw_attribute_name}" appears more than once in the node definition')
            attribute_manager = get_attribute_manager(attribute_name, attribute_data)
            extracted_interfaces[attribute_name] = attribute_manager
            if attribute_manager.memory_type is None:
                attribute_manager.memory_type = self.memory_type
            if attribute_manager.memory_type != MemoryTypeValues.CPU:
                self.has_cuda_attributes = 1
            attribute_manager.cuda_pointer_type = self.cuda_pointer_type
            # After creation, ensure that the attribute manager has a valid configuration
            try:
                attribute_manager.validate_configuration()
                if attribute_manager.ogn_base_type().startswith("transform"):
                    logger.warning(
                        "'%s' is being deprecated by USD. Use 'framed[4]' or 'matrixd[4]' instead",
                        attribute_manager.ogn_type(),
                    )
            except Exception as error:
                raise ParseError(f"Attribute {attribute_name}") from error

        return extracted_interfaces

    # ----------------------------------------------------------------------
    def attribute_by_name(self, attribute_name: str) -> Tuple[AttributeManager, str]:
        """Look up an attribute on the node by name.

        Args:
            attribute_name: Name of the attribute to find

        Returns:
            (Manager of the named attribute, type of the attribute)

        Raises:
            AttributeError: If the attribute does not exist on the node.
        """
        if attribute_name in self.__inputs:
            return (self.__inputs[attribute_name], INPUT_GROUP)
        if attribute_name in self.__outputs:
            return (self.__outputs[attribute_name], OUTPUT_GROUP)
        if attribute_name in self.__state:
            return (self.__state[attribute_name], STATE_GROUP)

        # Handle the case of short-form names
        match_found = None
        attribute_as_input = attribute_name_in_namespace(attribute_name, INPUT_NS)
        if attribute_as_input in self.__inputs:
            match_found = (self.__inputs[attribute_as_input], INPUT_GROUP)
        attribute_as_output = attribute_name_in_namespace(attribute_name, OUTPUT_NS)
        if attribute_as_output in self.__outputs:
            if match_found is not None:
                raise AttributeError(f'"{attribute_name}" ambiguously matched multiple types')
            match_found = (self.__outputs[attribute_as_output], OUTPUT_GROUP)
        attribute_as_state = attribute_name_in_namespace(attribute_name, STATE_NS)
        if attribute_as_state in self.__state:
            if match_found is not None:
                raise AttributeError(f'"{attribute_name}" ambiguously matched multiple types')
            match_found = (self.__state[attribute_as_state], STATE_GROUP)

        if match_found is not None:
            return match_found

        raise AttributeError(f'"{attribute_name}" was not found in the node"')

    # ----------------------------------------------------------------------
    def all_input_attributes(self) -> List[AttributeManager]:
        """Get the list of all input attributes extracted from the description

        Returns:
            The list of attribute interfaces for inputs on the node
        """
        return NodeInterface.sorted_values(self.__inputs)

    # ----------------------------------------------------------------------
    def all_output_attributes(self) -> List[AttributeManager]:
        """Get the list of all output attributes extracted from the description

        Returns:
            The list of attribute interfaces for outputs on the node
        """
        return NodeInterface.sorted_values(self.__outputs)

    # ----------------------------------------------------------------------
    def all_state_attributes(self) -> List[AttributeManager]:
        """Get the list of all state attributes extracted from the description

        Returns:
            The list of attribute interfaces for state on the node
        """
        return NodeInterface.sorted_values(self.__state)

    # ----------------------------------------------------------------------
    def all_attributes(self) -> List[AttributeManager]:
        """Get the list of all attributes of all types extracted from the description

        Returns:
            The list of attribute interfaces for all attributes defined on the node
        """
        return self.all_input_attributes() + self.all_output_attributes() + self.all_state_attributes()

    # ----------------------------------------------------------------------
    def has_attributes(self) -> bool:
        """Returns true if this node type has any attributes.

        This provides a quick check so that code generators can skip attribute sections when none exist.
        For code sections containing only a single type of attribute use, e.g., if node.all_state_attributes():
        """
        return self.__inputs or self.__outputs or self.__state

    # ----------------------------------------------------------------------
    @staticmethod
    def sorted_values(attributes: dict) -> List[AttributeManager]:
        """Get the list of dictionary values sorted by the dictionary keys

        Args:
            attributes: A dictionary with sortable keys

        Returns:
            The list of dictionary values sorted by the dictionary keys
        """
        return [attributes[key] for key in sorted(attributes.keys())]

    # ----------------------------------------------------------------------
    def all_tests(self) -> List[TestData]:
        """Returns the list of all sets of tests data extracted from the description"""
        return self.tests

    # ----------------------------------------------------------------------
    @deprecated_function("All types are supported, the check_support function should no longer be called")
    def check_support(self):  # pragma: no cover
        """Checks to see if this node contains currently unsupported attributes

        Raises:
            AttributeError: If any attributes on the node are not going to be supported
            UnimplementedError: If any attributes on the node are currently not supported but will be
        """
        for attribute in self.all_input_attributes():
            try:
                attribute.check_support()
            except AttributeError as error:
                raise AttributeError(f"{self.name} input not supported") from error
            except UnimplementedError as error:
                raise UnimplementedError(f"{self.name} input not yet supported") from error
        for attribute in self.all_output_attributes():
            try:
                attribute.check_support()
            except AttributeError as error:
                raise AttributeError(f"{self.name} output not supported") from error
            except UnimplementedError as error:
                raise UnimplementedError(f"{self.name} output not yet supported") from error
        for attribute in self.all_state_attributes():
            try:
                attribute.check_support()
            except AttributeError as error:
                raise AttributeError(f"{self.name} state not supported") from error
            except UnimplementedError as error:
                raise UnimplementedError(f"{self.name} state not yet supported") from error

    # ----------------------------------------------------------------------
    def can_generate(self, generation_type: str) -> bool:
        """Checks to see if a particular type of output should be generated.

        Args:
            generation_type: Name of output generation type. Exact values respected are in main.py

        Return:
            True if the generation_type of data is allowed by the node
        """
        if generation_type in self.excluded_generators:
            return False
        if generation_type == "c++" and self.language in [LanguageTypeValues.PYTHON]:
            return False
        if (
            generation_type == "python"
            and self.language == LanguageTypeValues.CPP
            and ExtraTypeValues.PYTHON not in self.extra_generators
        ):
            return False
        return True

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def quick_generation_check(cls, ogn_file_path: Path) -> List[str]:
        """Does a quick read on the file and returns a list of configuration names for file types that the node
        definition supports generation. (i.e. filtered by language choice and exclusions). You would only call this
        if you do not want to parse the entire .ogn file just for this information, otherwise it is already available
        from the full parsing.
        """
        try:
            with open(ogn_file_path, "r", encoding="utf-8") as ogn_fd:
                raw_ogn = list(json.load(ogn_fd).values())[0]
            all_supported = [
                getattr(ExclusionTypeValues, generation_type)
                for generation_type in dir(ExclusionTypeValues)
                if not generation_type.startswith("_")
            ]
            if NodeTypeKeys.ICON not in raw_ogn:
                # An icon being specified means that it can be generated
                with suppress(ValueError):
                    all_supported.remove(ExclusionTypeValues.ICON)
            if NodeTypeKeys.LANGUAGE in raw_ogn:
                # C++ can generate Python but not the other way around
                language = check_node_language(raw_ogn[NodeTypeKeys.LANGUAGE])
                if language != LanguageTypeValues.CPP:
                    with suppress(ValueError):
                        all_supported.remove(ExclusionTypeValues.CPP)
            else:
                language = LanguageTypeValues.CPP
            if language == LanguageTypeValues.CPP:
                extras = raw_ogn.get(NodeTypeKeys.EXTRAS, [])
                if isinstance(extras, str):
                    extras = [extras]
                if ExtraTypeValues.PYTHON not in extras:
                    all_supported.remove(ExclusionTypeValues.PYTHON)
            if NodeTypeKeys.EXCLUDE in raw_ogn:
                for exclusion in raw_ogn[NodeTypeKeys.EXCLUDE] or []:
                    with suppress(ValueError):
                        all_supported.remove(exclusion)
            return all_supported
        except (json.JSONDecodeError, FileNotFoundError, IndexError) as error:
            raise ParseError(f"Could not parse the .ogn file '{ogn_file_path}'") from error

    # --------------------------------------------------------------------------------------------------------------
    def is_batched_attribute(self, attribute: AttributeManager) -> bool:
        """Returns True if the given attribute description corresponds to one that will have batched database support"""
        return (
            attribute.ogn_base_type() not in ["bundle", "target", "any", "union"]
            and attribute.array_depth == 0
            and attribute.memory_storage() == MemoryTypeValues.CPU
        )

    # --------------------------------------------------------------------------------------------------------------
    def has_batched_attributes(self) -> tuple[bool, bool, bool]:
        """Check the node type definition for attributes that are considered to be batchable.
        That is, attributes with simple data types on the CPU. For now, only inputs and outputs are considered
        batchable but state status is included for consistent reference.

        Returns:
            Tuple indicating if batchable attributes exist in inputs, outputs, and state attributes.
        """
        input_batchable = False
        output_batchable = False
        state_batchable = False

        if self.language != LanguageTypeValues.PYTHON:
            return (input_batchable, output_batchable, state_batchable)

        for attribute in self.all_input_attributes():
            if self.is_batched_attribute(attribute):
                input_batchable = True
                break

        for attribute in self.all_output_attributes():
            if self.is_batched_attribute(attribute):
                output_batchable = True
                break

        return (input_batchable, output_batchable, state_batchable)


# ======================================================================
class NodeInterfaceGenerator:
    """Manage the common functions used by all types of node generators

    Override the interface_file_name() and generate_node_interface() methods for a derived generator.
    You can also override pre_interface_generation() if you have something to emit at the beginning of the
    interface that is not replicated for each node.

    Attributes:
        base_name: Base name of the file containing the node descriptions
        extension: Name of the extension requesting the generation
        generator_version: The version information for this extension when it was run
        interface_directory: Path to the directory where the file should be written (None is as string)
        module: Root import for the files of the node
        node_interface: Node interface whose interface is being generated
        out: File object which is the destination of the test output
        output_path: Location of output destination, None if only going to a string
        target_version: The version information for the omni.graph.core extension the generated code is meant for
        verbose: True if extra debugging output is to be added
    """

    def __init__(self, configuration: GeneratorConfiguration):
        """Set up the generator and output the Python interface code for the node

        Args:
            configuration: Information defining how and where the documentation will be generated

        Raises:
            NodeGenerationError: When for some reason the Python code could not be generated
        """
        self.base_name = configuration.base_name
        self.generator_version = configuration.generator_version
        self.target_version = configuration.target_version
        self.extension = configuration.extension
        self.node_interface = configuration.node_interface
        self.module = configuration.module
        self.node_file_path = configuration.node_file_path
        self.interface_directory = configuration.destination_directory
        self.needs_directory = configuration.needs_directory
        self.verbose = configuration.verbose
        self.output_path = None

        try:
            # Choose the Linux-style newlines to keep output consistent and simple
            if self.interface_directory and self.interface_file_name():
                self.output_path = os.path.abspath(os.path.join(self.interface_directory, self.interface_file_name()))
            # The generated file sizes will never be too large to fit into a string, and generating them to a
            # string first is far more efficient so set up the output to buffer into a string first and then
            # write it to a file when complete, if requested
            self.out = IndentedOutput(io.StringIO())
        except IOError as error:  # pragma: no cover
            raise NodeGenerationError(f"Could not obtain write access to {self.interface_directory}") from error

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        """Return the interface generated as a string, if requested. Otherwise return the interface file path"""
        return str(self.out)

    # ----------------------------------------------------------------------
    def safe_name(self) -> str:
        """Returns the name of the node type, filtered to be safe for Python, USD, or C++ use"""
        return self.node_interface.name.replace(".", "_")

    # ----------------------------------------------------------------------
    def interface_file_name(self) -> Optional[str]:
        """Return the path for the generated file - should be overridden by derived classes"""
        logger.info("Generator has not overridden the interface_file_name")

    # ----------------------------------------------------------------------
    def generate_node_interface(self):
        """Create interface output from the given node interface.

        This does nothing; it should be overridden in a derived class
        """
        logger.info("Generator has not overidden the node interface")

    # ----------------------------------------------------------------------
    def pre_interface_generation(self):
        """Create the information information preceding the node-specific stuff"""
        logger.info("Generator has not overridden the pre-node interface")

    # ----------------------------------------------------------------------
    def post_interface_generation(self):
        """Create the information information following the node-specific stuff"""
        logger.info("Generator has not overridden the post-node interface")

    # ----------------------------------------------------------------------
    def generate_interface(self):
        """Create an interface for the node

        Raises:
            NodeGenerationError: When there is a failure in the generation of the interface
        """
        self.pre_interface_generation()
        self.generate_node_interface()
        self.post_interface_generation()
        # Now that the entire interface has been generated it can be written out to disk.
        if self.output_path is not None:
            self.__check_interface_directory()
            if self.needs_to_write():
                with open(self.output_path, "w", encoding="utf-8") as generated_file:
                    generated_file.write(str(self.out))
            else:
                # We still need to update the mod-time for the sake of timestamp-based build rules
                os.utime(self.output_path)

    # --------------------------------------------------------------------------------------------------------------
    def needs_to_write(self):
        """Check if the file needs to be written

        Returns:
            True if the file does not exist or its contents differ from the generated text
        """
        if os.path.exists(self.output_path):
            with open(self.output_path, encoding="utf-8") as fp:
                data = fp.read()
                if data == str(self.out):
                    return False

        # Leaving this in place as it can be helpful in finding what might have changed in generated code
        #
        # import shutil
        # from pathlib import Path
        # original = Path(self.output_path)
        # before = Path(os.getenv("TMP")) / f"Before_{original.name}"
        # after = Path(os.getenv("TMP")) / f"After_{original.name}"
        # shutil.copyfile(self.output_path, str(before))
        # with open(after, "w") as fd:
        #     fd.write(str(self.out))

        return True

    # --------------------------------------------------------------------------------------------------------------
    def __check_interface_directory(self):
        """Check to see if the interface directory is required, creating it if it is.

        Raises:
            NodeGenerationError if the interface directory was required but did not exist and could not be created
        """
        # No directory needed, that's good
        if not self.needs_directory:
            return

        # No directory specified but one is needed, that's bad
        if not self.interface_directory:
            raise NodeGenerationError(f"Required an interface directory for {self.__class__} but did not specify one")

        # Directory is needed and specified, and exists, that's good
        directory = Path(self.interface_directory)
        if directory.is_dir():
            return

        # Try to create the missing directory
        try:
            directory.mkdir(mode=0o777, parents=True, exist_ok=True)
            logger.info("Created interface destination directory %s", directory)
        except Exception as error:  # pragma: no cover
            raise NodeGenerationError(f"Failed to create interface directory '{directory}'") from error


# ======================================================================
class NodeInterfaceWrapper:
    """Converts a JSON node description file into a set of interfaces to the node contained in it

    Reads and parses a node interface description file in order to present an interface to the data
    that is more specific to the type of data that is in the file.

    Attributes:
        node_interface: The NodeInterface parsed from the JSON data
    """

    def __init__(
        self,
        node_as_json: Union[str, IO, Dict],
        extension: str,
        config_directory: Optional[str] = None,
        categories_allowed: Dict[str, str] = None,
        pedantic: bool = False,
    ):
        """Initialize the class by parsing the node description file or the already-retrieved description

        Args:
            node_as_json: File object, path to file, or raw dictionary containing the node interface description data
            extension: Name of the extension in which the node was defined
            config_directory: Location of directory in which the attribute type configuration files can be found. If
                None then use the directory where this script lives.
            categories_allowed: Dictionary of name:description values for legal categories
            pedantic: Should more strict checks be applied to the node interface description?

        Raises:
            ParseError: If there are any errors parsing the node description - string contains the problem
        """
        self.node_interface = None
        json_description = None
        node_directory = None
        if categories_allowed is None:
            categories_allowed = {}
        if config_directory is None:
            config_directory = os.path.dirname(os.path.realpath(__file__))

        if isinstance(node_as_json, str):
            logger.info("Parsing node interface as string")
            # logger.info(json.dumps(node_as_json, indent=4))
            try:
                json_description = json.loads(node_as_json)
            except json.decoder.JSONDecodeError as error:
                raise ParseError(f"Invalid JSON formatting in string - {error}\n{node_as_json}") from None
        elif isinstance(node_as_json, Dict):
            json_description = node_as_json
        else:
            logger.info("Parsing node interface as a file")
            try:
                json_description = json.load(node_as_json)
                node_directory = os.path.dirname(node_as_json.name)
            except json.decoder.JSONDecodeError as error:
                raise ParseError(f"Invalid JSON formatting in file {node_as_json.name} - {error}") from None

        if not json_description or not json_description.keys():
            raise ParseError("Not a valid JSON file")
        if len([main_key for main_key in json_description.keys() if not is_comment(main_key)]) > 1:
            raise ParseError(f"Only one node definition allowed per file - found {list(json_description.keys())}")

        logger.info("Extracting node information")
        for node_type_name, node_type_description in json_description.items():
            if node_type_name[0] == "$":  # Special IDs are not actual nodes
                logger.info("Ignoring comment tagged %s", node_type_name)
                continue
            logger.info("Extracting node data for %s", node_type_name)
            check_node_name(node_type_name)
            if self.node_interface is not None:
                raise ParseError("Only one node per JSON description is supported")
            if node_type_name.find(".") < 0:
                # If no explicit namespace then prepend the extension name to guarantee uniqueness
                node_type_name = f"{extension}.{node_type_name}"
            self.node_interface = NodeInterface(
                node_type_name, node_type_description, config_directory, categories_allowed, node_directory, pedantic
            )

    # ----------------------------------------------------------------------
    def can_generate(self, generation_type: str) -> bool:
        """Checks to see if a particular type of output should be generated.

        Args:
            generation_type: Name of output generation type. Exact values respected are in main.py

        Return:
            True if the generation_type of data is allowed by the node
        """
        return self.node_interface.can_generate(generation_type) if self.node_interface else False

    # ----------------------------------------------------------------------
    @deprecated_function("All types are now supported, NodeTypeInterfaceWrapper.check_support should no longer be used")
    def check_support(self):  # pragma: no cover
        """Raises AttributeError if any attributes on the node are currently not supported"""
        self.node_interface.check_support()
