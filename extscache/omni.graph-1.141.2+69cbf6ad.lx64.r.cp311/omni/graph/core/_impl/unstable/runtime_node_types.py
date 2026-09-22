"""Support for creating node type definitions at runtime as an alternative to the usual .ogn/.py files.

Exports:
    define_node_type: Decorator for creating node type definitions
    all_runtime_node_types: Returns the list of known runtime node type definitions
    deregister_runtime_node_type: Deregisters a named runtime node type definition
    RUNTIME_MODULE_NAME: Special module name for runtime node type definitions not tied to an extension
    NodeTypeCreationError: Exception specific to this feature
"""

# pylint: disable=no-member
import logging
import os
import sys
from contextlib import suppress
from types import NoneType

import omni.graph.core as og
import omni.graph.tools._internal as ogi
import omni.graph.tools.ogn as ogn

from .attribute_spec import AttributeSpec
from .validate_runtime_methods import MethodValidationError, validate_method

# ==============================================================================================================
RUNTIME_MODULE_NAME = "__orphan__"
"""Unique module name to identify node types that were created at runtime with no extension.
This is most common for those created through the script editor but could also be caused by importing files
from a local directory.
"""

# ==============================================================================================================
# The AutoNode logger will output to stdout in a standard way, defaulting to logging level "WARN" unless the
# environment variable AUTONODE_DEBUG is set, in which case it defaults to level "DEBUG".
_logger = logging.getLogger("OGRuntime")
if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _logger.addHandler(_handler)
else:
    _handler = _logger.handlers[0]
_handler.setFormatter(logging.Formatter("[%(name)s] [%(levelname)s] %(message)s"))
_handler.setLevel(logging.DEBUG)
_logger.setLevel(logging.DEBUG if os.getenv("OG_RUNTIME_DEBUG") else logging.WARN)


# ==============================================================================================================
class NodeTypeCreationError(Exception):
    """Exception specific to node type creation errors"""


# ==============================================================================================================
class NodeTypeDefinition:
    """Wrapper class for a node type that adds a simple API for managing registration and deregistration.

    Normal use case:
        - Runtime node type creates a NodeTypeDefinition via definition=define_node_type()
        - User calls definition.register(), which adds it to ALL_DEFINITIONS
        - User calls definition.deregister(), which removes it from ALL_DEFINITIONS
        - definition goes out of scope, deleting it and skipping definition.deregister() since it is not registered

    Replacement use case, for iterating on node type definitions:
        - Runtime node type creates a NodeTypeDefinition via definition=define_node_type()
        - User calls definition.register(), which adds it to ALL_DEFINITIONS
        - User modifies one or more fields in definition, not including "name", which is not allowed
        - User calls definition.register() again, which deregisters the original definition and registers the new one
        - Note that the fields can only be modified by setting a new copy. If you modify the contents, as in a call
          like 'definition.metadata["categories"] = None' this will not be considered as a change, you must instead
          use definition.metadata = {"categories": None}

    If the user retains their definition but another definition with the same name is created:
        - Runtime node type creates a NodeTypeDefinition via definition=define_node_type()
        - User calls definition.register(), which adds it to ALL_DEFINITIONS
        - Some other runtime node type creates a NodeTypeDefinition via definition2=define_node_type()
        - If the user calls definition2.register() it fails
        - User then calls definition.deregister()
        - Then user calls definition2.register() it registers as above
        - If definition.register() is called again then it will fail since definition2 has the same node type name
        - If definition or definition2 go out of scope nothing happens
        - When ALL_DEFINITIONS goes out of scope or is cleared then definition2 is deregistered

    If the user does not wish to explicitly deregister:
        - Runtime node type creates a NodeTypeDefinition via definition=define_node_type()
        - User calls definition.register(), which adds it to ALL_DEFINITIONS
        - definition goes out of scope for the user, but is retained in ALL_DEFINITIONS
        - When this extension unloads the remaining definitions in ALL_DEFINITIONS are deregistered

    If the user will explicitly deregister from the main API instead of from the definition:
        - Runtime node type creates a NodeTypeDefinition via definition=define_node_type()
        - User calls definition.register(), which adds it to ALL_DEFINITIONS
        - definition goes out of scope for the user, but is retained in ALL_DEFINITIONS
        - User calls og.deregister_node_type() for the defined node type
        - Callback comes in to _on_registry_event to deregister the known type
        - It is noticed that the definition is registered and is then removed from ALL_DEFINITIONS here
    """

    ALL_DEFINITIONS = {}
    DISABLE_SUBSCRIPTION = None

    def __init__(
        self,
        name: str,
        version: int,
        description: str,
        extension: str,
        attributes: list[AttributeSpec] = None,
        ui_name: str = None,
        metadata: dict[str, str] = None,
        method_overrides: dict[str, callable] = None,
    ):
        """See the define_node_type() function for argument details."""
        self.needs_rebuilding = None  # Flags the fact that the name change about to happen is safe
        self.name = name
        self.is_registered = False
        self.version = version
        self.description = description
        self.extension = extension
        self.attribute_dict = {
            og.Attribute.ensure_port_type_in_name(
                attribute_spec.name, attribute_spec.port_type, attribute_spec.type_name == "bundle"
            ): attribute_spec
            for attribute_spec in attributes
        }
        self.ui_name = ogi.python_name_to_ui_name(name.split(".")[-1]) if ui_name is None else ui_name
        self.metadata = metadata
        self.method_overrides = method_overrides
        self.__doc__ = self.__doc__ + define_node_type.__doc__
        self._implementation = None
        self._listen_for_node_type_disable()
        self.needs_rebuilding = True

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def _log_registered_types(cls):
        """Print out the contents of the entire registration list to the log"""
        registered = cls.ALL_DEFINITIONS
        _logger.info("Currently registered runtime node types: %d", len(registered))
        for name, definition in registered.items():
            _logger.info("  %s = %s", name, definition)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def _on_registry_event(cls, event: og.GraphRegistryEvent):
        """Callback for when a node type is registered or deregistered"""
        node_type_name = event.payload["node_type"]
        type_id = event.payload["node_ptr"]
        if event.type == int(og.GraphRegistryEvent.NODE_TYPE_REMOVED):
            _logger.debug("Received registry remove event for %s as %s", node_type_name, type_id)
            with suppress(KeyError):
                cls.ALL_DEFINITIONS[node_type_name].is_registered = False  # In case someone is retaining a copy
                del cls.ALL_DEFINITIONS[node_type_name]
                _logger.debug("-> Successfully removed the runtime definition")

    @classmethod
    def _listen_for_node_type_disable(cls):
        """Ensure there is a subscription to node type disabled events. Only one is needed since it will look
        the node type name up in the global runtime definition dictionary.
        """
        if cls.DISABLE_SUBSCRIPTION is None:
            cls.DISABLE_SUBSCRIPTION = (
                og.GraphRegistry().get_event_stream().create_subscription_to_pop(cls._on_registry_event)
            )

    # --------------------------------------------------------------------------------------------------------------
    def _rebuild_implementation(self):
        """Construct the node type definition class based on the current settings"""

        class NodeTypeSimple:
            @staticmethod
            def compute(_context: og.GraphContext, _node: og.Node):
                """Default compute does nothing"""
                return True

            @staticmethod
            def get_node_type() -> str:
                """Required method to return the node type name"""
                return self.name

            @staticmethod
            def initialize_type(node_type):
                """Set up the node type metadata and add all of the attributes to the node type"""
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, self.extension)
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, self.description)
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                for key, value in self.metadata.items():
                    node_type.set_metadata(str(key), str(value))
                if self.ui_name is not None:
                    node_type.set_metadata(ogn.MetadataKeys.UI_NAME, self.ui_name)
                for attr_name, attribute_spec in self.attribute_dict.items():
                    match attribute_spec.port_type:
                        case og.AttributePortType.INPUT:
                            add_function = node_type.add_input
                        case og.AttributePortType.OUTPUT:
                            add_function = node_type.add_output
                        case og.AttributePortType.STATE:
                            add_function = node_type.add_state
                    attr_name = og.Attribute.ensure_port_type_in_name(
                        attribute_spec.name, attribute_spec.port_type, attribute_spec.type_name == "bundle"
                    )
                    add_function(attr_name, attribute_spec.type_name, True, attribute_spec.default)

            @staticmethod
            def defined_at_runtime() -> bool:
                """Override the function that identifies this node type as being defined at runtime"""
                return True

            @staticmethod
            def _initialize(_context: og.GraphContext, _node: og.Node):
                """The initialize function the user will override so that the default initialization can still happen"""

            @staticmethod
            def initialize(context: og.GraphContext, node: og.Node):
                """Default initialize method sets up the attribute metadata then calls the user initialize method.
                This is due to the fact that the attributes have to exist on a specific node. If the attribute
                specs were part of the node type ABI then the metadata would live there and this would not be necessary
                """
                for attribute in node.get_attributes():
                    attribute_spec = self.attribute_dict.get(attribute.get_name(), None)
                    if attribute_spec is not None:
                        attribute.set_metadata(ogn.MetadataKeys.DESCRIPTION, attribute_spec.description)
                NodeTypeSimple._initialize(context, node)

        self._implementation = NodeTypeSimple
        for method_name, method_override in self.method_overrides.items():
            # The initialize method cannot be replaced as it his critical initialization. Rename it so that the
            # core implementation remains but calls the override as well.
            if method_name == "initialize":
                self._implementation._initialize = method_override  # noqa: protected-access
            else:
                setattr(self._implementation, method_name, method_override)

        self.needs_rebuilding = False

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """Returns string representation of the object, mostly for debugging"""
        return "\n".join(
            [
                f"Node Type Definition for {self.name} version {self.version}",
                f"  Registered = {self.is_registered}",
                f"  UI Name = {self.ui_name}",
                f"  Extension = {self.extension}",
                f"  Description = {self.description}",
                f"  Attributes = {self.attribute_dict}",
                f"  Metadata = {self.metadata}",
                f"  Methods = {self.method_overrides}",
            ]
        )

    # --------------------------------------------------------------------------------------------------------------
    def __del__(self):
        """For confirmation that these remove themselves on exit"""
        _logger.debug("NodeTypeDefinition %s at %x being destroyed", self.name, id(self))
        if self.is_registered:
            _logger.debug("-> was still active")
            self.deregister()

    # --------------------------------------------------------------------------------------------------------------
    def __setattr__(self, name: str, value: any):
        """By checking for changes to the definition reregistration of the same type with a different definition
        can be allowed. The is_registered value is state information and does not indicate a change of definition,
        the _implementation is what will need rebuilding, and the needs_rebuilding is the flag tracking it so none
        of those will change the state.
        """
        if name == "name" and self.needs_rebuilding is not None:
            raise AttributeError(f"Not allowed to change the name of the node type definition for {self.name}")
        if name not in ["is_registered", "_implementation", "needs_rebuilding"]:
            super().__setattr__("needs_rebuilding", True)

        super().__setattr__(name, value)

    # --------------------------------------------------------------------------------------------------------------
    def register(self):
        """Registers the node type with OmniGraph and remembers that it was registered.
        The flag is necessary in order to support external deregistration, i.e. deregistration through an API
        call rather than calling this object's deregister function.
        """
        _logger.debug("NodeTypeDefinition request to register %s at %x", self.name, id(self))
        if self.is_registered:
            if not self.needs_rebuilding:
                raise NodeTypeCreationError(f"Attempted to reregister the same node type {self.name}")
            _logger.debug("-> Definition was changed; deregistering the previous version first")
            self.is_registered = not og.deregister_node_type(self.name)
            _logger.debug("-> Registered state using old definition is now %s", self.is_registered)
        try:
            if self.needs_rebuilding:
                self._rebuild_implementation()
            og.register_node_type(self._implementation, self.version)
            self.is_registered = True
            self.ALL_DEFINITIONS[self.name] = self
            _logger.debug("-> Registered state is now %s", self.is_registered)
        except ValueError as error:
            _logger.debug("-> Registration failed, registration state stays as %s", self.is_registered)
            raise NodeTypeCreationError(f"Attempted to register a duplicate node type {self.name}") from error

    # --------------------------------------------------------------------------------------------------------------
    def deregister(self):
        _logger.debug("NodeTypeDefinition request to deregister %s at %x", self.name, id(self))
        if not self.is_registered:
            _logger.debug("-> Not allowed, it is already deregistered")
            raise NodeTypeCreationError(f"Tried to deregister unregistered node type {self.name}")
        self.is_registered = not og.deregister_node_type(self.name)
        _logger.debug("-> Registered state is now %s", self.is_registered)


# ==============================================================================================================
def all_runtime_node_types() -> dict[str, NodeTypeDefinition]:
    """Returns the dictionary of all currently registered NodeTypeDefinitions by name.
    There may be other objects of this type around but they are the responsibility of their respective owners.
    """
    return NodeTypeDefinition.ALL_DEFINITIONS


# ==============================================================================================================
def deregister_runtime_node_type(node_type_name: str) -> bool:
    """Deregisters a runtime node type by name, for cases when you might not be retaining the NodeTypeDefinition.
    Args:
        node_type_name: Fully qualified name of the node type to deregister
    Returns:
        bool: True iff the node_type_name was previously registered and was successfully deregistered
    """
    _logger.info("Deregistering node type %s by name", node_type_name)
    with suppress(KeyError, NodeTypeCreationError):
        NodeTypeDefinition.ALL_DEFINITIONS[node_type_name].deregister()
        return True
    return False


# ==============================================================================================================
def define_node_type(
    name: str,
    version: int,
    description: str,
    extension: str,
    attributes: list[AttributeSpec] = None,
    ui_name: str = None,
    metadata: dict[str, str] = None,
    method_overrides: dict[str, callable] = None,
    bypass_safety_checks: bool = False,
) -> NodeTypeDefinition:
    """Create a new node type definition with the defined parameters.
    Args:
        name: Unique node type name
        version: Version number of this node type definition
        description: Description of this node type
        extension: Extension to which this node type will belong
        attributes: List of attributes attached to this node type; includes inputs, outputs, and state
        ui_name: Name of the node type as it will appear in the UI
        metadata: Dictionary of metadata values to attach to this node type
        method_overrides: Dictionary of named method overrides for the node type's implementation
        bypass_safety_checks: If True then generation is faster but random exceptions might be raised
    Returns:
        Node type wrapper for controlling the lifetime of the node type definition.
    """
    _logger.info("Creating node type '%s' version '%s' - %s", name, version, description)

    # Many of these checks would be the domain of a static type checker but as we are not currently running one they
    # must be optionally made at runtime.
    if not bypass_safety_checks:
        # Give the errors a consistent formatting
        def _type_error(message: str, bad_value: any):
            return NodeTypeCreationError(f"{message}. Passed in '{bad_value}' of type {type(bad_value)}")

        if not isinstance(name, str):
            raise _type_error("name must be a string.", name)

        if not isinstance(version, int) or version < 0:
            raise _type_error("version must be an integer.", name)

        if not isinstance(description, str):
            raise _type_error("description must be a string.", description)

        if not isinstance(extension, str):
            raise _type_error("extension must be a string.", extension)

        if not isinstance(attributes, (NoneType, list)):
            raise _type_error("attributes must be a list of AttributeSpec.", attributes)
        if attributes is not None:
            _logger.info("  Checking %d attributes", len(attributes))
            for attribute in attributes:
                if not isinstance(attribute, AttributeSpec):
                    raise _type_error("attributes must be AttributeSpecs.", attribute)
                if og.AttributeType.type_from_ogn_type_name(attribute.type_name).base_type == og.BaseDataType.UNKNOWN:
                    raise _type_error("attribute type name is not a legal OGN type.", attribute.type_name)

        if not isinstance(ui_name, (NoneType, str)):
            raise _type_error("ui_name must be a string.", ui_name)

        if not isinstance(metadata, (NoneType, dict)):
            raise _type_error("Metadata must be a dictionary of name(str): value(str).", metadata)
        if metadata is not None:
            _logger.info("  Checking %d metadata values", len(metadata))
            # Nothing to verify here as anything can be turned into a string
            for key, value in metadata.items():
                _logger.debug("    %s = %s", key, value)

        if not isinstance(method_overrides, (NoneType, dict)):
            raise _type_error(
                "Method overrides must be a dictionary mapping the name of the function (str) to the"
                " callable implementation of that named function. You did not pass a dictionary.",
                method_overrides,
            )
        if method_overrides is not None:
            _logger.info("  Checking %d method override values", len(method_overrides))
            for key, value in method_overrides.items():
                _logger.debug("    %s = %s", key, value)
                try:
                    validate_method(key, value)
                except MethodValidationError as error:
                    raise _type_error(str(error), value) from error

    # Give the None values sensible defaults
    if attributes is None:
        attributes = []
    if metadata is None:
        metadata = {}
    if method_overrides is None:
        method_overrides = {}

    # Construct the wrapper for the definition and return it
    return NodeTypeDefinition(
        name,
        version,
        description,
        extension,
        attributes,
        ui_name,
        metadata,
        method_overrides,
    )
