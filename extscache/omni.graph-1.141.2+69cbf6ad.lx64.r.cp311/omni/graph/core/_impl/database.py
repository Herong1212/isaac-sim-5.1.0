# pylint: disable=too-many-lines
"""
Implementation of the support for the generated node database, which provides access tailored to the specific
configuration of a node.
"""
from __future__ import annotations

import inspect
from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple

import omni.graph.core as og
import omni.graph.tools as ogt
import omni.graph.tools.ogn as ogn
from carb import log_error as carb_error
from carb import log_info as carb_info
from carb import log_warn as carb_warn

# Type definition for the generated data that will contain attribute definition data
AttributeDescriptionType = List[Tuple[str, str, str, str, Dict, bool, Any]]


# Mapping from the extended type reported in the interface data and the one used by attributes
EXTENDED_TYPES = {
    ogn.EXTENDED_TYPE_REGULAR: og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR,
    ogn.EXTENDED_TYPE_UNION: og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION,
    ogn.EXTENDED_TYPE_ANY: og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY,
}


# Mapping of a port type to the namespace it uses
PORT_TO_NS = {
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: ogn.INPUT_NS,
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: ogn.OUTPUT_NS,
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: ogn.STATE_NS,
}


# These are all this module is intended to export. Anything else is internal implementation details.
__all__ = [
    "Database",
    "DynamicAttributeAccess",
    "DynamicAttributeInterface",
]


# ================================================================================
def get_caller_info(depth: int = 1) -> Tuple[str, int, str]:
    """Retrieves the information from the caller at the given stack depth

    Args:
        depth: Stack depth, where 1 is the caller of this function

    Returns:
        tuple[str, int, str]:
            - caller file path
            - caller line number
            - caller function name
    """
    try:
        caller_frame = inspect.stack()[depth]
        return caller_frame.filename, caller_frame.lineno, caller_frame.function
    except Exception:  # pylint: disable=broad-except
        return "Unknown", -1, "Unknown"


# =====================================================================
class _PropertyOrDefault:
    """Helper class for attribute properties, returning the default if a property did not exist, its value if it does.
    This facilitates creation of parallel structures for attribute hierarchies so that you can access the information
    like this:

        db.inputs.myAttr
        db.roles.inputs.myAttr
        db.attributes.inputs.myAttr

    """

    def __init__(self, default_value):
        """Set up the default for any properties that do not exist"""
        self.__default = default_value

    def __getattr__(self, name):
        """Override of property accessor, returning the default instead of AttributeError when it does not exist"""
        try:
            return self.__dict__[name]
        except KeyError:
            return self.__default


# ==============================================================================================================
class _DynamicAttributeInfo:
    """Helper class to manage dynamic attribute additions and removals. This assumes the data is managed in the
    standard tree X.inputs.Y, X.outputs.Y, X.state.Y and adds and removes dynamic attribute data from the correct
    location. The method per_attribute_data() should be overridden to provide the data that is stored at the leaf
    level of this tree (i.e. the "Y" value)
    """

    __slots__ = ["inputs", "outputs", "state"]

    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.state = []

    # ----------------------------------------------------------------------
    def __get_port_information(self, port_type: og.AttributePortType) -> _PropertyOrDefault:
        """Return the container for role information on the given port type"""
        if port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
            return self.inputs
        if port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
            return self.outputs
        if port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE:
            return self.state
        return None

    # ----------------------------------------------------------------------
    def __property_name(self, attribute: og.Attribute) -> str:
        """Returns the name of the property on this class to set for the given attribute"""
        return attribute.get_name().replace(f"{PORT_TO_NS[attribute.get_port_type()]}:", "")

    # ----------------------------------------------------------------------
    def add_attribute(self, new_attribute: og.Attribute):
        """Add in the information for a newly created attribute."""
        property_name = self.__property_name(new_attribute)
        port_data = self.__get_port_information(new_attribute.get_port_type())
        if property_name in dir(port_data):
            raise og.OmniGraphError(f"Tried to add the same dynamic attribute '{new_attribute.get_name()}' twice")
        setattr(port_data, property_name, self.per_attribute_data(new_attribute))

    # ----------------------------------------------------------------------
    def remove_attribute(self, old_attribute: og.Attribute):
        """Remove the information for a newly deleted attribute"""
        property_name = self.__property_name(old_attribute)
        port_data = self.__get_port_information(old_attribute.get_port_type())
        if property_name not in dir(port_data):
            raise og.OmniGraphError(f"Tried to remove unknown dynamic attribute '{old_attribute.get_name()}'")
        delattr(port_data, property_name)

    # ----------------------------------------------------------------------
    def per_attribute_data(self, attribute: og.Attribute) -> Any:
        """Override this to store the correct dynamic attribute data on this instance of the object"""
        raise og.OmniGraphError("Tried to store per-attribute data of unknown type")


# =====================================================================
class _Role(_DynamicAttributeInfo):
    """
    Helper class that allows roles to be accessed by using a syntax similar to attribute values.

    The attribute value for input attribute X would be accessed with "db.inputs.X". This class allows the
    role to be accessed with "db.roles.inputs.X", returning None if the attribute has no assigned role.
    All that's required of the derived class is for it to set members who have roles using the normal syntax:

        db.role.inputs.X = og.AttributeRole.COLOR
    """

    def __init__(self):
        """Set up attributes for role discovery"""
        super().__init__()
        self.inputs = _PropertyOrDefault(None)
        self.outputs = _PropertyOrDefault(None)
        self.state = _PropertyOrDefault(None)

    def per_attribute_data(self, attribute: og.Attribute) -> Any:
        """Returns the per-attribute data added for this type by dynamic attributes"""
        return attribute.get_resolved_type().role


# =====================================================================
@dataclass
class _AttributeData:
    """-------- FOR GENERATED CODE USE ONLY --------

    Simple class holding information used to define attributes
    """

    name: str
    data_type: str
    extended_type_index: int
    metadata: Dict
    is_required: bool
    default_value: Any
    is_deprecated: bool
    deprecation_msg: str

    def base_name(self) -> str:
        """Returns the attribute name with the leading namespace removed and colons replaced by underscores"""
        return ogn.attribute_name_as_python_property(self.name)

    def extended_type(self) -> og.ExtendedAttributeType:
        """Returns the extended type of this attribute definition, converted from the int index value"""
        return EXTENDED_TYPES[self.extended_type_index]


# =====================================================================
class _AttributeCache:
    """-------- FOR GENERATED CODE USE ONLY --------

    Handler for OGN attribute definitions that create simple accessors for them.

    This is for use by the generated code, to manage automatic registration of attributes with the node type,
    and to provide a common location for unchanging attribute data as found in _AttributeData.
    Attribute-specific members will be added by the generated code by their names. In the typical configuration,
    this class will be instantiated three times in the database under an umbrella "INTERFACE" static object, as
    "inputs", "outputs", and "state". That way the code can do things like access the definition information for the
    input attribute named "usb" through OgnMyDatabase.INTERFACE.inputs.usb.
    """

    def add_to_node_type(self, node_type_method: Callable, extended_node_type_method: Callable):
        """Adds all attributes that are members of this class to the node type using the passed-in method.
        This will only be called by the generated code when it is setting up the definition of a node type.

        Args:
            node_type_method: Function to call that will add the attributes to a specific INodeType definition
        """
        for property_name in vars(self):
            member = getattr(self, property_name)
            if isinstance(member, _AttributeData):
                if member.extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
                    node_type_method(member.name, member.data_type, member.is_required, member.default_value)
                else:
                    extended_node_type_method(member.name, member.data_type, member.is_required, member.extended_type())


# =====================================================================
class _AllAttributeDefinitions:
    def __init__(self, descriptions: AttributeDescriptionType):
        """Create an attribute definition cache using the information parsed from the descriptions list.

        Args:
            descriptions: List of attribute definition tuples
                            (name, data_type, uiName, description, metadata, is_required, default_value, is_deprecated,
                            deprecation_msg)

        Raises:
            og.OmniGraphError: Raised if there was some problem with the attribute definition
        """
        self.inputs = _AttributeCache()
        self.outputs = _AttributeCache()
        self.state = _AttributeCache()
        for (
            name,
            data_type,
            extended_type,
            ui_name,
            description,
            metadata,
            required,
            default_value,
            *extra,
        ) in descriptions:
            # From omni.graph 1.35 onward, there are two additional parameters in the description.
            if len(extra) == 2:
                (deprecated, deprecation_msg) = extra
            else:
                deprecated = False
                deprecation_msg = ""

            if ui_name is not None:
                metadata[ogn.MetadataKeys.UI_NAME] = ui_name
            if description is not None:
                metadata[ogn.MetadataKeys.DESCRIPTION] = description
            attribute_data = _AttributeData(
                name, data_type, extended_type, metadata, required, default_value, deprecated, deprecation_msg
            )
            # Output Bundles are represented as relationsips without namespace separator `_`
            if (ogn.is_output_name(name) or ogn.is_state_name(name)) and data_type == "bundle":
                attribute_data.name = name.replace(":", "_")
            property_name = attribute_data.base_name()
            if ogn.is_input_name(name):
                setattr(self.inputs, property_name, attribute_data)
            elif ogn.is_output_name(name):
                setattr(self.outputs, property_name, attribute_data)
            elif ogn.is_state_name(name):
                setattr(self.state, property_name, attribute_data)
            else:
                raise og.OmniGraphError(f"Namespace for attribute '{name}' is unknown")

    def add_to_node_type(self, node_type: og.NodeType):
        """Take all of the attribute definitions parsed by this class and add them to the given node type

        Args:
            node_type: Object containing the instantiataion of an INodeType definition
        """
        self.inputs.add_to_node_type(node_type.add_input, node_type.add_extended_input)
        self.outputs.add_to_node_type(node_type.add_output, node_type.add_extended_output)
        self.state.add_to_node_type(node_type.add_state, node_type.add_extended_state)


# =====================================================================
class _AttributeContainer(_DynamicAttributeInfo):
    """-------- FOR GENERATED CODE USE ONLY --------

    Handler for maintaining local copies of the og.Attribute values for a node in a structure that provides more
    natural access to them. For example the attribute "inputs:enterprise" would be accessible through the container
    member inputs.enterprise and would be of type og.Attribute.
    """

    def __parse_cache(self, cache: _AttributeCache):
        """Returns an object that contains the parsed structure in the cache"""
        structure = type("", (), {})
        for property_name in vars(cache):
            member = getattr(cache, property_name)
            if isinstance(member, _AttributeData):
                attribute = self.node.get_attribute(member.name)
                if not attribute.is_valid():
                    raise og.OmniGraphError(
                        f"Could not find node's attribute '{member.name}' in {self.node.get_attributes()}"
                    )
                if member.metadata:
                    for key, value in member.metadata.items():
                        # Metadata is only str:str for now so convert non-strings into strings for later parsing
                        if isinstance(value, list):
                            value = ",".join(value)
                        elif not isinstance(value, str):
                            value = f"'{value}'"
                        attribute.set_metadata(key, value)
                if member.is_deprecated:
                    og._internal.deprecate_attribute(attribute, member.deprecation_msg)  # noqa: PLW0212
                attribute.is_optional_for_compute = not member.is_required
                setattr(structure, member.base_name(), attribute)
        return structure

    def __init__(self, node: og.Node, definitions: _AllAttributeDefinitions):
        """Create the structure containing the attribute objects as class members"""
        super().__init__()
        self.node = node
        self.inputs = self.__parse_cache(definitions.inputs)
        self.outputs = self.__parse_cache(definitions.outputs)
        self.state = self.__parse_cache(definitions.state)

    def per_attribute_data(self, attribute: og.Attribute) -> Any:
        """Returns the per-attribute data added for this type by dynamic attributes"""
        return attribute


# =====================================================================
class PerNodeKeys:
    """Set of key values for per-node data.
    This is data that belongs to a node, but which is only valid for Python node implementations. Any data that
    belongs to all node types should be implemented through the ABI.
    """

    ATTRIBUTES = "attributes"
    """Definitions of the attribute objects on the node"""
    ROLE = "role"
    """Role object built to provide a parallel method of accessing attribute role data"""
    NODE_CALLBACK = "node_callback"
    """Callback subscription for the node event stream"""
    INTERNAL_STATE = "internal_state"
    """Data stored as internal state information by the user"""
    DYNAMIC_ATTRIBUTES = "dynamic_attributes"
    """Accessor for dynamic attributes on the node"""
    ERRORS = "errors"
    """String list containing the unique errors encountered during evaluation"""


# =====================================================================
class DynamicAttributeInterface:
    """Class providing a container for dynamic attribute access interfaces.
    One of these objects is created per-node, per-port, to contain getter and setter properties on dynamic
    attributes for their node and port type. These classes persist in the per-node data and their property
    members are updated based on the addition and removal of dynamic attributes from their node. The base class
    implementation for the attribute accessors, DynamicAttributeAccess, uses this to determine whether an attribute
    access request was made on a static or dynamic attribute.

    The per-node data on the database will contain one of these objects per port-type. When the database is
    created it will be attached to the primary attribute access classes via the base class below,
    DynamicAttributeAccess.

    Attributes:
        _port_type: Type of port managed by this class (only one allowed per instance). Single underscore only so that
                    the base class of the attribute information can access it.
        _element_counts: Dictionary of str:int values which maps the names of dynamic output array attributes to the
                         of pending elements to allocate for their array data (required since Fabric takes the element
                         counter as an argument to the data retrieval so it can't be set ahead of time). It is set when
                         a size is set, reset when a value is set, and read from Fabric when it's value is requested.
                         The key values will be the special attribute name that has "_size" appended to it (until such
                         time as the attribute value can support size access itself).
        _interfaces: Dictionary of str:og.Attribute values which maps the names of a dynamic attribute to the actual
                     attribute on the node.
        _on_gpu: If True then values are requested from the GPU memory, else the CPU memory
        _gpu_ptr_kind: Ignored for CPU memory. For GPU memory specifies whether attribute data will be returned
                       as a GPU pointer to the GPU memory, or a CPU pointer to the GPU memory.
    """

    def __init__(self, port_type: og.AttributePortType):
        """Initialize the namespace used for attributes managed here

        Args:
            port_type: Port type for the dynamic attribute
        """
        self._port_type: og.AttributePortType = port_type
        self._interfaces: dict[str, og.Attribute] = {}
        self._element_counts: dict[str, int] = {}
        self._on_gpu: bool = False
        self._gpu_ptr_kind = og.PtrToPtrKind.NA

    # ----------------------------------------------------------------------
    def __property_name(self, attribute: og.Attribute) -> str:
        """Returns the name of the property on this class to set for the given attribute"""
        return attribute.get_name().replace(f"{PORT_TO_NS[self._port_type]}:", "")

    # ----------------------------------------------------------------------
    def has_attribute(self, property_name: str) -> bool:
        """Returns True if the given property name is a known dynamic attribute on this object

        Args:
            property_name: Name of the property to look for

        Returns:
            bool: True if a dynamic attribute of the given name exists here
        """
        return property_name in self._interfaces

    # ----------------------------------------------------------------------
    def set_default_memory_location(self, on_gpu: bool, gpu_ptr_kind: og.PtrToPtrKind = og.PtrToPtrKind.NA):
        """Set the default memory location from which dynamic attribute values will be retrieved.
        This is what will be used if you access dynamic attribute values in the same way you access regular
        attribute values - e.g. value = db.inputs.dyn_attr.

        The settings of the two flags will determine the type of memory returned for array attributes, such as float[],
        double[3][], and matrixd[4][], and non-array attributes such as int[4], uint, and bool.

        Array attributes

        +----------------------+----------------------------+----------------------------+
        |                      |         on_gpu=True        |        on_gpu=False        |
        +======================+============================+============================+
        | og.PtrToPtrKind.CPU  | CPU Pointers to GPU arrays | CPU Pointers to CPU arrays |
        +----------------------+----------------------------+----------------------------+
        | og.PtrToPtrKind.GPU  | GPU Pointers to GPU arrays | CPU Pointers to CPU arrays |
        +----------------------+----------------------------+----------------------------+
        | og.PtrToPtrKind.NA   | GPU Pointers to GPU arrays | CPU Pointers to CPU arrays |
        +----------------------+----------------------------+----------------------------+

        Non-Array attributes are always returned as CPU values.

        There is currently no supported way of overriding these access methods. If not specified they will default to
        everything being on the CPU.

        Args:
            on_gpu: If true then array attributes will be returned from GPU memory, else from CPU memory
            gpu_ptr_kind: Determines if there is a CPU memory wrapper around the GPU allocated memory, as above.
        """
        self._on_gpu = on_gpu
        self._gpu_ptr_kind = gpu_ptr_kind

    # ----------------------------------------------------------------------
    def get(self, property_name: str) -> Any:
        """Returns the value of the named attribute

        Args:
            property_name: Name of the property within the namespace of this object's port type

        Returns:
            Any: Value of the attribute's data

        Raises:
            og.OmniGraphError: If the attribute is unknown
        """
        try:
            attribute = self._interfaces[property_name]
        except KeyError as error:
            raise og.OmniGraphError(f"Tried to get the value of unknown dynamic attribute '{property_name}'") from error

        # For the special syntax "x = db.inputs.array_size" retrieve the element count for the attribute "inputs:array"
        # Non-arrays will not have an entry in self._element_counts so this will be skipped for them.
        if property_name in self._element_counts:
            if self._element_counts[property_name] is None:
                self._element_counts[property_name] = og.DataView(attribute=attribute).get_array_size()
            return self._element_counts[property_name]

        # Retrieve the attribute value from Fabric
        on_gpu = self._on_gpu and (attribute.get_resolved_type().array_depth == 1)
        pending_element_count = self._element_counts.get(f"{property_name}_size")
        return og.DataView(
            attribute=attribute,
            on_gpu=on_gpu,
            gpu_ptr_kind=self._gpu_ptr_kind,
        ).get(reserved_element_count=pending_element_count)

    # ----------------------------------------------------------------------
    def set(self, property_name: str, locked: bool = False, new_value: Any = None) -> bool:  # noqa: A003
        """Sets the value of the named attribute

        Args:
            property_name: Name of the property within the namespace of this object's port type
            locked: True if setting read-only values is currently locked (i.e. inside a compute)
            new_value: Value to be set on the attribute with the given name

        Raises:
            og.OmniGraphError: If the attribute is unknown
            og.ReadOnlyError: If writing is locked and the attribute is read-only

        Returns:
            bool: True if the value was set
        """
        # For the special syntax "db.outputs.array_size = x" set the element count for the attribute "outputs:array"
        # Non-arrays will not have an entry in self._element_counts so this will be skipped for them. The value of
        # the element count will be used when getting the actual array at a later time.
        if property_name in self._element_counts:
            self._element_counts[property_name] = new_value
            return True

        try:
            attribute = self._interfaces[property_name]
        except KeyError as error:
            raise og.OmniGraphError(f"Tried to set the value of unknown dynamic attribute '{property_name}'") from error
        if (self._port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT) and locked:
            raise og.ReadOnlyError(attribute)
        on_gpu = self._on_gpu and (attribute.get_resolved_type().array_depth == 1)

        # If this was an array attribute being set then reset the array size so that it can be read again from Fabric
        # the next time it is requested. (It could also be set after the og.DataView.set() call but this delays that
        # extra call until it's actually requested.)
        element_count_name = f"{property_name}_size"
        if element_count_name in self._element_counts:
            self._element_counts[element_count_name] = None

        return og.DataView(attribute=attribute, on_gpu=on_gpu, gpu_ptr_kind=self._gpu_ptr_kind).set(new_value)

    # ----------------------------------------------------------------------
    def add_attribute(self, new_attribute: og.Attribute):
        """Add in the interface for a newly created attribute.

        This creates a new attribute on this object named for the new attribute. The value of that attribute is a
        pair of functions that will get and set the value for that attribute.

        Args:
            new_attribute: Attribute that was just added

        Raises:
            og.OmniGraphError: If the attribute has a mismatched port type
        """
        if new_attribute.get_port_type() != self._port_type:
            raise og.OmniGraphError(
                f"Adding attribute {new_attribute.get_name()} onto the wrong port type {self._port_type}"
            )
        property_name = self.__property_name(new_attribute)
        if property_name in self._interfaces:
            raise og.OmniGraphError(f"Tried to add the same dynamic attribute '{new_attribute.get_name()}' twice")
        self._interfaces[property_name] = new_attribute
        if new_attribute.get_resolved_type().array_depth > 0:
            self._element_counts[f"{property_name}_size"] = 0

    # ----------------------------------------------------------------------
    def remove_attribute(self, old_attribute: og.Attribute):
        """Remove the interface for a newly deleted attribute

        Args:
            old_attribute: Attribute that is about to be removed

        Raises:
            og.OmniGraphError: If the attribute has a mismatched port type, or the property didn't exist
        """
        if old_attribute.get_port_type() != self._port_type:
            raise og.OmniGraphError(
                f"Removing attribute {old_attribute.get_name()} from the wrong port type {self._port_type}"
            )
        property_name = self.__property_name(old_attribute)
        with suppress(KeyError):
            del self._element_counts[f"{property_name}_size"]
        try:
            del self._interfaces[property_name]
        except KeyError as error:
            raise og.OmniGraphError(
                f"Tried to remove non-existent dynamic attribute {old_attribute.get_name()}"
            ) from error


# =====================================================================
class DynamicAttributeAccess:
    """Base class for the generated classes that contain the access properties for all attributes.
    Each of the port containers, db.inputs/db.outputs/db.state, houses the attribute data access properties.
    These containers are constructed when the database is created, with hardcoded properties for all statically
    defined attributes. This class intercepts getattr/setattr/delattr calls to check to see if the property
    being requested is a dynamic attribute, and if so then it uses the properties stored in the per-node data
    as the access points.

    So the lookup sequence goes like this
        db  -> og.Database
          .inputs -> ValuesForInput(DynamicAttributeAccess)
                 .myAttribute -> DynamicAttributeAccess.__getattr__
                              -> ValuesForInput.__getattr__ (if the above fails)

    It makes the bold assumption that the attributes are all set up nicely; no duplicate names, invalid types,
    missing configuration, etc.

    Attributes use leading underscores to minimize name collisions with the dynamically added attributes. (Double
    underscores would have been preferable but would have made access from the derived classes problematic.)

    Attributes:
        _context: Graph context used for evaluating this node
        _node: The OmniGraph node to which this data belongs
        _attributes: The set of attributes on this object's port
        _dynamic_attributes: Container holding the per-node specification of dynamic attributes,
            not visible to derived classes
    """

    def __init__(
        self,
        context_id: og.GraphContext,
        node: og.Node,
        attributes,
        dynamic_attributes: DynamicAttributeInterface,
    ):
        """Initialize common data used for all attribute port types

        Args:
            context_id: Context of the evaluation
            node: Node owning the attribute
            attributes: List of attributes belonging to this accessor
            dynamic_attributes: Interface to the dynamic attributes
        """
        if isinstance(context_id, og.GraphContext):
            super().__setattr__("_context", context_id)
        else:
            # V1_5_0 compatibility
            super().__setattr__("_context", context_id.context)
        super().__setattr__("_node", node)
        super().__setattr__("_attributes", attributes)
        super().__setattr__("_dynamic_attributes", dynamic_attributes)
        # Inputs are the only ones with the lock. It's only on during compute so initialize to False here
        if dynamic_attributes._port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
            super().__setattr__("_setting_locked", False)

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        """Debug visualization of the important information in this class"""
        table = []
        members = []
        for member_class in [self.__class__, self._dynamic_attributes.__class__]:
            class_members = inspect.getmembers(member_class)
            members.append(
                [member_class, [a[0] for a in class_members if not (a[0].startswith("__") and a[0].endswith("__"))]]
            )
        for member_class, member_list in members:
            for member in member_list:
                as_property = getattr(member_class, member)
                if isinstance(as_property, property):
                    value = member
                    if as_property.fget is not None:
                        value += " + getter"
                    if as_property.fset is not None:
                        value += " + setter"
                    if as_property.fdel is not None:
                        value += " + deleter"
                    table.append(value)
        return str(table)

    # ----------------------------------------------------------------------
    def get_dynamic_attributes(self) -> DynamicAttributeInterface:
        """Get the interface to the dynamic attributes

        Returns:
            DynamicAttributeInterface: Direct access to the dynamic attributes managed by this class,
                avoiding the __getattr__ override
        """
        return super().__getattribute__("_dynamic_attributes")

    # ----------------------------------------------------------------------
    def __getattr__(self, item: str) -> Any:
        """Intercept requests for attribute information that wasn't pre-generated, to support dynamic attributes"""
        dynamic_attributes = self.get_dynamic_attributes()
        # Look for the name or the name of an array with "_size" appended
        if dynamic_attributes.has_attribute(item) or (
            item.endswith("_size") and dynamic_attributes.has_attribute(item[:-5])
        ):
            return dynamic_attributes.get(item)

        return super().__getattribute__(item)

    # ----------------------------------------------------------------------
    def __setattr__(self, item: str, new_value: Any):
        """Intercept requests for attribute information that wasn't pre-generated, to support dynamic attributes"""
        dynamic_attributes = self.get_dynamic_attributes()
        # Look for the name or the name of an array with "_size" appended
        if dynamic_attributes.has_attribute(item) or (
            item.endswith("_size") and dynamic_attributes.has_attribute(item[:-5])
        ):
            setting_locked = (
                dynamic_attributes._port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            ) and self._setting_locked
            dynamic_attributes.set(item, setting_locked, new_value)
        else:
            super().__setattr__(item, new_value)

    # ----------------------------------------------------------------------
    def __delattr__(self, item: str) -> Any:
        """Intercept requests for removing attribute information that wasn't pre-generated,
        to support dynamic attributes"""
        dynamic_attributes = self.get_dynamic_attributes()
        # Look for the name or the name of an array with "_size" appended
        if dynamic_attributes.has_attribute(item) or (
            item.endswith("_size") and dynamic_attributes.has_attribute(item[:-5])
        ):
            raise og.OmniGraphError(
                f"Deletion of dynamic attribute '{item}' interface can only be done by"
                " removing the attribute from the node"
            )

        return super().__delattr__(item)


# =====================================================================
class Database:
    """Base class for the generated database class for .ogn nodes (Python and C++ implementations)

    Defines some common functionality that is the same for nodes of all types, to help cut down on the amount
    of redundant generated code.

    Like the C++ equivalent, you can access the ABI data types normally passed to the compute as
    *db.abi_node()* and *db.abi_context()*

    Derived classes will have these class member variables instantiated, which are manipulated here in order to
    keep the amount of generated code to a minimum
    """

    INTERFACE = {}
    """Attribute interface definition - things that don't change between nodes of the same type"""
    PER_NODE_DATA = {}
    """Dictionary for data that is different on every node of the same type."""

    # ----------------------------------------------------------------------
    @staticmethod
    def _get_interface(descriptions: AttributeDescriptionType) -> _AllAttributeDefinitions:
        """Returns per-class data containing an attribute cache constructed from the descriptions."""
        return _AllAttributeDefinitions(descriptions)

    # ----------------------------------------------------------------------
    @classmethod
    def _populate_role_data(cls) -> _Role:
        """Returns the role structure corresponding to the node type's attributes.
        While this could be calculated directly it's more efficient to let the generated code do it, as there
        will usually not be many roles to add. Thie method can safely return an empty _Role() object because it
        has been designed to provide correct default values for missing properties.
        """
        return _Role()

    # ----------------------------------------------------------------------
    @classmethod
    def dynamic_attribute_data(cls, node: og.Node, port_type: og.AttributePortType) -> DynamicAttributeInterface:
        """Gets the dynamic attribute data class stored on each node for a given port type

        Args:
            node: Node on which the dynamic attributes should be found
            port_type: Port type for the dynamic attributes to retrieve

        Returns:
            DynamicAttributeInterface: Interface to the dynamic attributes on the given node
        """
        try:
            dynamic_information = cls.per_node_data(node)[PerNodeKeys.DYNAMIC_ATTRIBUTES]
        except KeyError as error:
            raise og.OmniGraphError(f"No per-node dynamic attribute information for {node.get_prim_path}") from error
        try:
            return dynamic_information[port_type]
        except KeyError as error:
            raise og.OmniGraphError(f"No dynamic port information on {node.get_prim_path()} for {port_type}") from error

    # ----------------------------------------------------------------------
    @classmethod
    def __per_node_roles(cls, node: og.Node) -> Optional[_Role]:
        """Returns the dynamic attribute role class stored on each node for a given port type"""
        try:
            role_information = cls.per_node_data(node)[PerNodeKeys.ROLE]
        except KeyError as error:
            raise og.OmniGraphError(f"No per-node role information for {node.get_prim_path}") from error
        return role_information

    # ----------------------------------------------------------------------
    @classmethod
    def __per_node_attributes(cls, node: og.Node) -> Optional[_AttributeContainer]:
        """Returns the dynamic attribute container class stored on each node for a given port type"""
        try:
            attribute_information = cls.per_node_data(node)[PerNodeKeys.ATTRIBUTES]
        except KeyError as error:
            raise og.OmniGraphError(f"No per-node attribute information for {node.get_prim_path}") from error
        return attribute_information

    # ----------------------------------------------------------------------
    @classmethod
    def __on_attribute_created(cls, node: og.Node, attribute: og.Attribute):
        """Callback run when an event was received from the node that it created a new dynamic attribute"""
        cls.dynamic_attribute_data(node, attribute.get_port_type()).add_attribute(attribute)
        cls.__per_node_roles(node).add_attribute(attribute)
        cls.__per_node_attributes(node).add_attribute(attribute)

    # ----------------------------------------------------------------------
    @classmethod
    def __on_attribute_removed(cls, node: og.Node, attribute: og.Attribute):
        """Callback run when an event was received from the node that it removed an existing dynamic attribute"""
        cls.dynamic_attribute_data(node, attribute.get_port_type()).remove_attribute(attribute)
        cls.__per_node_roles(node).remove_attribute(attribute)
        cls.__per_node_attributes(node).remove_attribute(attribute)

    # ----------------------------------------------------------------------
    @classmethod
    def __on_node_event(cls, node: og.Node, event):
        """Callback run when the generated node sends off an event"""
        if event.type == int(og.NodeEvent.CREATE_ATTRIBUTE):
            cls.__on_attribute_created(node, node.get_attribute(event.payload["attribute"]))
        elif event.type == int(og.NodeEvent.REMOVE_ATTRIBUTE):
            cls.__on_attribute_removed(node, node.get_attribute(event.payload["attribute"]))

    # ----------------------------------------------------------------------
    @classmethod
    def _initialize_per_node_data(cls, node: og.Node):
        """Sets up the per-node dictionary of data to cache for faster lookup"""
        per_node_data = {
            PerNodeKeys.ATTRIBUTES: _AttributeContainer(node, cls.INTERFACE),
            PerNodeKeys.DYNAMIC_ATTRIBUTES: {
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: DynamicAttributeInterface(
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
                ),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: DynamicAttributeInterface(
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
                ),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: DynamicAttributeInterface(
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE
                ),
            },
            PerNodeKeys.ROLE: cls._populate_role_data(),
            PerNodeKeys.NODE_CALLBACK: node.get_event_stream().create_subscription_to_pop(
                partial(cls.__on_node_event, node), name=f"{node.get_prim_path()} Event"
            ),
            PerNodeKeys.ERRORS: [],
            PerNodeKeys.INTERNAL_STATE: {},
        }

        cls.PER_NODE_DATA[node.node_id()] = per_node_data

        for attribute in node.get_attributes():
            if not attribute.is_dynamic():
                continue
            cls.__on_attribute_created(node, attribute)

    # ----------------------------------------------------------------------
    @classmethod
    def _release_per_node_data(cls, node: og.Node):
        """Release the dictionary entry for this node's data, if any"""
        with suppress(KeyError):
            cls.PER_NODE_DATA.pop(node.node_id())

    # ----------------------------------------------------------------------
    @classmethod
    def per_node_data(cls, node: og.Node) -> Dict[str, Any]:
        """Returns the per-node data for the given node

        Args:
            node: OmniGraph node for which the data is to be retrieved

        Raises:
            og.OmniGraphError: If the per-node data is missing, most likely because the node is not initialized
        """
        try:
            return cls.PER_NODE_DATA[node.node_id()]
        except AttributeError as error:
            raise og.OmniGraphError(
                f"Database class {cls.__name__} not initialized. No per-node data available"
            ) from error
        except KeyError as error:
            raise og.OmniGraphError(
                f"Database class {cls.__name__} does not contain per-node data for '{node.get_prim_path()}'"
            ) from error

    # ----------------------------------------------------------------------
    # Role definitions, for comparison to find role-based attributes
    ROLE_BUNDLE = ogt.DeprecatedStringConstant("ROLE_BUNDLE", "bundle", "Use AttributeRole.BUNDLE")
    """DEPRECATED - use omni.graph.core.AttributeRole.BUNDLE"""
    ROLE_COLOR = ogt.DeprecatedStringConstant("ROLE_COLOR", "color", "Use AttributeRole.COLOR")
    """DEPRECATED - use omni.graph.core.AttributeRole.COLOR"""
    ROLE_EXECUTION = ogt.DeprecatedStringConstant("ROLE_EXECUTION", "execution", "Use AttributeRole.EXECUTION")
    """DEPRECATED - use omni.graph.core.AttributeRole.EXECUTION"""
    ROLE_FRAME = ogt.DeprecatedStringConstant("ROLE_FRAME", "frame", "Use AttributeRole.FRAME")
    """DEPRECATED - use omni.graph.core.AttributeRole.FRAME"""
    ROLE_MATRIX = ogt.DeprecatedStringConstant("ROLE_MATRIX", "matrix", "Use AttributeRole.MATRIX")
    """DEPRECATED - use omni.graph.core.AttributeRole.MATRIX"""
    ROLE_NORMAL = ogt.DeprecatedStringConstant("ROLE_NORMAL", "normal", "Use AttributeRole.NORMAL")
    """DEPRECATED - use omni.graph.core.AttributeRole.NORMAL"""
    ROLE_OBJECT_ID = ogt.DeprecatedStringConstant("ROLE_OBJECT_ID", "objectId", "Use AttributeRole.OBJECT_ID")
    """DEPRECATED - use omni.graph.core.AttributeRole.OBJECT_ID"""
    ROLE_PATH = ogt.DeprecatedStringConstant("ROLE_PATH", "path", "Use AttributeRole.PATH")
    """DEPRECATED - use omni.graph.core.AttributeRole.PATH"""
    ROLE_POINT = ogt.DeprecatedStringConstant("ROLE_POINT", "point", "Use AttributeRole.POSITION")
    """DEPRECATED - use omni.graph.core.AttributeRole.POSITION"""
    ROLE_QUATERNION = ogt.DeprecatedStringConstant("ROLE_QUATERNION", "quaternion", "Use AttributeRole.QUATERNION")
    """DEPRECATED - use omni.graph.core.AttributeRole.QUATERNION"""
    ROLE_TARGET = ogt.DeprecatedStringConstant("ROLE_TARGET", "target", "Use AttributeRole.TARGET")
    """DEPRECATED - use omni.graph.core.AttributeRole.TARGET"""
    ROLE_TEXCOORD = ogt.DeprecatedStringConstant("ROLE_TEXCOORD", "texcoord", "Use AttributeRole.TEXCOORD")
    """DEPRECATED - use omni.graph.core.AttributeRole.TEXCOORD"""
    ROLE_TIMECODE = ogt.DeprecatedStringConstant("ROLE_TIMECODE", "timecode", "Use AttributeRole.TIMECODE")
    """DEPRECATED - use omni.graph.core.AttributeRole.TIMECODE"""
    ROLE_TRANSFORM = ogt.DeprecatedStringConstant("ROLE_TRANSFORM", "transform", "Use AttributeRole.FRAME")
    """DEPRECATED - use omni.graph.core.AttributeRole.FRAME"""
    ROLE_VECTOR = ogt.DeprecatedStringConstant("ROLE_VECTOR", "vector", "Use AttributeRole.VECTOR")
    """DEPRECATED - use omni.graph.core.AttributeRole.VECTOR"""

    # ----------------------------------------------------------------------
    def __init__(self, node: og.Node):
        """Initialize the helper classes for roles and sizes - attribute values are defined in the derived classes

        Args:
            node: Node to which the database belongs
        """
        self.node = node
        self.context = node.get_graph().get_default_graph_context()
        try:
            per_node_data = self.PER_NODE_DATA[node.node_id()]
        except KeyError:
            self._initialize_per_node_data(node)
            per_node_data = self.PER_NODE_DATA[node.node_id()]

        # Set up properties that let the database access the per-node data as though it belonged to it
        for per_node_data_type, per_node_data_value in per_node_data.items():
            if per_node_data_type != PerNodeKeys.INTERNAL_STATE:
                setattr(self, per_node_data_type, per_node_data_value)

    # ----------------------------------------------------------------------
    def get_metadata(self, metadata_key: str, attribute: Optional[og.Attribute] = None) -> Optional[str]:
        """Get metadata related to this node.

        To get the metadata on the node type call *db.get_metadata(ogn.MetadataKeys.UI_NAME)*
        To get the metadata from a specific attribute call
        *db.get_metadata(ogn.MetadataKeys.UI_NAME, db.attribute.inputs.x)*

        Args:
            metadata_key: Name of the metadata value to return
            attribute: Attribute on which the metadata lives. If None then look at the node type's metadata

        Returns:
            str | None: Metadata value string, or None if the named metadata key did not exist
        """
        if attribute is None:
            return self.node.get_node_type().get_metadata(metadata_key)
        return attribute.get_metadata(metadata_key)

    # ----------------------------------------------------------------------
    @property
    def abi_node(self) -> og.Node:
        """Node: The node to which this database belongs"""
        return self.node

    # ----------------------------------------------------------------------
    @property
    def abi_context(self) -> og.GraphContext:
        """GraphContext: The graph context to which this database belongs"""
        return self.context

    # ----------------------------------------------------------------------
    @ogt.deprecated_function("Move does not exists anymore. This function will perform copy instead")
    def move(self, dst: og.Attribute, src: og.Attribute):  # pragma: no cover
        """Deprecated function. Will perform a copy instead of moving"""
        dst.get_attribute_data().copy_data(src.get_attribute_data())

    # ----------------------------------------------------------------------
    @staticmethod
    def __formatted_message(message: str, severity: str) -> str:
        """Return the commonly formatted error message to report for OmniGraph failures"""
        # Depth of 3 to ignore this one, and the log_XX method that called it to get the real reporter
        (file_path, line_number, function_name) = get_caller_info(3)
        intro = f"OmniGraph {severity}: "
        indent = " " * len(intro)
        return f"{intro}{message}\n{indent}(from {function_name}() at line {line_number} in {file_path})"

    # ----------------------------------------------------------------------
    def log_error(self, message: str, add_context: bool = True):
        """Log an error message from a compute method, for when the compute data is inconsistent or unexpected

        Args:
            message: Text of the message to log
            add_context: If True then add the stack trace from the location of the log report
        """
        if add_context:
            message = self.__formatted_message(message, "Error")
        try:
            self.abi_node.log_compute_message(og.Severity.ERROR, message)
        except AttributeError:
            # Older extensions may not have access to the node message logging ABI.
            error_list = self.per_node_errors(self.abi_node)
            if message not in error_list:
                error_list.append(message)
                carb_error(message)

    # ----------------------------------------------------------------------
    def log_warn(self, message: str):
        """Log a warning message from a compute method, when the compute is consistent but produced no results.
        This method is identical to log_warning; both exist because there are different conventions in other code about
        which name to use, so to avoid wasted developer time fixing unimportant incorrect guesses both are implemented.

        Args:
            message: Text of the message to log
        """
        message = self.__formatted_message(message, "Warning")
        try:
            self.abi_node.log_compute_message(og.Severity.WARNING, message)
        except AttributeError:
            # Older extensions may not have access to the node message logging ABI.
            error_list = self.per_node_errors(self.abi_node)
            if message not in error_list:
                error_list.append(message)
                carb_warn(message)

    # ----------------------------------------------------------------------
    def log_warning(self, message: str):
        """Log a warning message from a compute method, when the compute is consistent but produced no results.
        This method is identical to log_warn; both exist because there are different conventions in other code about
        which name to use, so to avoid wasted developer time fixing unimportant incorrect guesses both are implemented.

        Args:
            message: Text of the message to log
        """
        message = self.__formatted_message(message, "Warning")
        try:
            self.abi_node.log_compute_message(og.Severity.WARNING, message)
        except AttributeError:
            # Older extensions may not have access to the node message logging ABI.
            error_list = self.per_node_errors(self.abi_node)
            if message not in error_list:
                error_list.append(message)
                carb_warn(message)

    # ----------------------------------------------------------------------
    def log_info(self, message: str):
        """Log an information message from a compute method, when status information is required about the compute.
        Usually the compute will be successful, the information is for debugging or analysis.

        Args:
            message: Text of the message to log
        """
        message = self.__formatted_message(message, "Info")
        try:
            self.abi_node.log_compute_message(og.Severity.INFO, message)
        except AttributeError:
            # Older extensions may not have access to the node message logging ABI.
            error_list = self.per_node_errors(self.abi_node)
            if message not in error_list:
                error_list.append(message)
                carb_info(message)

    # ----------------------------------------------------------------------
    @classmethod
    def get_internal_state(cls, node: og.Node, inst_id: str):
        """Returns the internal state information on the node, or None if it does not exist

        Args:
            node: Node for which the internal state is to be retrieved

        Returns:
            Any: Internal state object attached to the given node
        """
        dic = cls.per_node_data(node)[PerNodeKeys.INTERNAL_STATE]
        ret = dic.get(inst_id, None)
        if ret is None:
            # If the node has implemented the internal_state() method then it will be managing per-node state information.
            try:
                get_data_fn = getattr(cls.NODE_TYPE_CLASS, PerNodeKeys.INTERNAL_STATE)
            except AttributeError:
                get_data_fn = None
            # Process this after exception handling in case the instantiation itself raises an exception.
            if get_data_fn:
                ret = get_data_fn()
                dic[inst_id] = ret
        return ret

    # ----------------------------------------------------------------------
    @classmethod
    def per_instance_internal_state(cls, node: og.Node):
        """Returns the internal state information on the node, or None if it does not exist

        Args:
            node: Node for which the internal state is to be retrieved

        Returns:
            Any: Internal state object attached to the given node
        """
        return cls.get_internal_state(node, node.get_graph_instance_id())

    # ----------------------------------------------------------------------
    @classmethod
    def shared_internal_state(cls, node: og.Node):
        """Returns the internal state information on the node, or None if it does not exist

        Args:
            node: Node for which the internal state is to be retrieved

        Returns:
            Any: Internal state object attached to the given node
        """
        return cls.get_internal_state(node, "_shared_state_")

    # ----------------------------------------------------------------------
    @classmethod
    @ogt.deprecated_function(
        "'per_node_internal_state' has been deprecated: use 'per_instance_internal_state' or 'shared_internal_state' "
    )
    def per_node_internal_state(cls, node: og.Node):  # pragma: no cover
        return cls.per_instance_internal_state(node)

    # ----------------------------------------------------------------------
    @property
    @ogt.deprecated_function("'internal_state' has been deprecated: use 'per_instance_state' or 'shared_state'")
    def internal_state(self):  # pragma: no cover
        """Any: The internal state data on the node owning this database"""
        return self.per_instance_internal_state(self.abi_node)

    # ----------------------------------------------------------------------
    @property
    def per_instance_state(self):
        """Any: The internal state data on the node owning this database"""
        return self.per_instance_internal_state(self.abi_node)

    # ----------------------------------------------------------------------
    @property
    def shared_state(self):
        """Any: The internal state data on the node owning this database"""
        return self.shared_internal_state(self.abi_node)

    # ----------------------------------------------------------------------
    @classmethod
    def per_node_errors(cls, node: og.Node):
        """Returns the compute errors on the node, or [] if it does not exist

        Args:
            node: Node for which the errors are to be retrieved

        Returns:
            list[str]: List off errors reported on the node
        """
        try:
            return cls.per_node_data(node)[PerNodeKeys.ERRORS]
        except KeyError:
            cls.per_node_data(node)[PerNodeKeys.ERRORS] = []
            return cls.per_node_data(node)[PerNodeKeys.ERRORS]

    # ----------------------------------------------------------------------
    @classmethod
    def _release_per_node_instance_data(cls, node: og.Node, target: str):
        """Clear the per instance data"""
        with suppress(KeyError):
            dic = cls.PER_NODE_DATA[node.node_id()][PerNodeKeys.INTERNAL_STATE]
            dic.pop(target)

    # ----------------------------------------------------------------------
    def get_variable(self, name: str):
        """Get the value of a variable with a given name. Returns None if the variable does not
        exist on the graph.

        Args:
            name: Name of the variable to retrieve

        Returns:
            Any: Value of the variable, or None if it does not exist on this node's graph
        """
        graph = self.node.get_graph()
        var = graph.find_variable(name)
        if not var:
            return None
        if var.type.array_depth >= 1:
            return var.get_array(self.context)
        return var.get(self.context)

    # ----------------------------------------------------------------------
    def set_variable(self, name: str, value: Any):
        """Set the value of a variable. og.OmniGraphError will be raised if the variable
        does not exist on the graph, or if there is type mismatch

        Args:
            name: Name of the variable to set
            value: New value for the variable

        Raises:
            OmniGraphError: If the variable did not exist or could not be set
        """
        graph = self.node.get_graph()
        var = graph.find_variable(name)
        if not var:
            raise og.OmniGraphError(f"Could not find variable {name}")
        if not var.set(self.context, value):
            raise og.OmniGraphError(
                f"Could not set variable {name} to {value}. Is {value} the proper type ({var.type})?"
            )

    # ----------------------------------------------------------------------
    def set_dynamic_attribute_memory_location(self, on_gpu: bool, gpu_ptr_kind: og.PtrToPtrKind = og.PtrToPtrKind.NA):
        """Set the memory location from which dynamic attribute values will be retrieved

        Args:
            on_gpu: If true the data will be returned from GPU memory, else from CPU memory
            gpu_ptr_kind: Ignored for CPU memory. For GPU memory specifies whether attribute data will be returned
                          as a GPU pointer to the GPU memory, or a CPU pointer to the GPU memory.
        """
        try:
            attribute_accessors = self.per_node_data(self.node)[PerNodeKeys.DYNAMIC_ATTRIBUTES]
        except KeyError as error:
            raise og.OmniGraphError(f"Dynamic attribute accessors not found for {self.node.get_prim_path()}") from error

        for interface in attribute_accessors.values():
            interface.set_default_memory_location(on_gpu, gpu_ptr_kind)
