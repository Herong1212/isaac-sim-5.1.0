"""pybind11 omni.graph.core bindings"""
from __future__ import annotations
import omni.graph.core._omni_graph_core
import typing
import carb.events._events
import numpy
import omni.core._core
import omni.graph.core._omni_graph_core._internal
import omni.graph.core._omni_graph_core._og_unstable
import omni.inspect._omni_inspect
_Shape = typing.Tuple[int, ...]

__all__ = [
    "ACCORDING_TO_CONTEXT_GRAPH_INDEX",
    "APPLIED_SCHEMA",
    "ASSET",
    "AUTHORING_GRAPH_INDEX",
    "Attribute",
    "AttributeData",
    "AttributePortType",
    "AttributeRole",
    "AttributeType",
    "BOOL",
    "BUNDLE",
    "BaseDataType",
    "BucketId",
    "BundleChangeType",
    "COLOR",
    "CONNECTION",
    "ComputeGraph",
    "ConnectionInfo",
    "ConnectionType",
    "DOUBLE",
    "ERROR",
    "EXECUTION",
    "ExecutionAttributeState",
    "ExtendedAttributeType",
    "FLOAT",
    "FRAME",
    "FileFormatVersion",
    "FunctionResult",
    "Graph",
    "GraphBackingType",
    "GraphContext",
    "GraphEvaluationMode",
    "GraphEvent",
    "GraphPipelineStage",
    "GraphRegistry",
    "GraphRegistryEvent",
    "HALF",
    "IBundle2",
    "IBundleChanges",
    "IBundleFactory",
    "IBundleFactory2",
    "IConstBundle2",
    "INFO",
    "INSTANCING_GRAPH_TARGET_PATH",
    "INT",
    "INT64",
    "INodeCategories",
    "INodeTypeForwarding",
    "INodeTypeForwarding2",
    "IPrimView",
    "ISchedulingHints",
    "ISchedulingHints2",
    "IVariable",
    "MATRIX",
    "MemoryType",
    "NONE",
    "NORMAL",
    "Node",
    "NodeEvent",
    "NodeType",
    "OBJECT_ID",
    "OmniGraphBindingError",
    "PATH",
    "POSITION",
    "PRIM",
    "PRIM_TYPE_NAME",
    "PtrToPtrKind",
    "QUATERNION",
    "RELATIONSHIP",
    "Severity",
    "TAG",
    "TARGET",
    "TEXCOORD",
    "TEXT",
    "TIMECODE",
    "TOKEN",
    "TRANSFORM",
    "Type",
    "UCHAR",
    "UINT",
    "UINT64",
    "UNKNOWN",
    "VECTOR",
    "WARNING",
    "acquire_interface",
    "attach",
    "create_prim_view_from_prims",
    "create_prim_view_from_query",
    "deregister_node_type",
    "deregister_post_load_file_format_upgrade_callback",
    "deregister_pre_load_file_format_upgrade_callback",
    "detach",
    "eAccessLocation",
    "eAccessType",
    "eComputeRule",
    "ePurityStatus",
    "eThreadSafety",
    "eVariableScope",
    "get_all_graphs",
    "get_all_graphs_and_subgraphs",
    "get_bundle_tree_factory_interface",
    "get_compute_cuda_device",
    "get_compute_graph_contexts",
    "get_global_orchestration_graphs",
    "get_global_orchestration_graphs_in_pipeline_stage",
    "get_graph_by_path",
    "get_graphs_in_pipeline_stage",
    "get_node_by_path",
    "get_node_categories_interface",
    "get_node_type",
    "get_node_type_forwarding_interface",
    "get_node_type_forwarding_interface2",
    "get_registered_nodes",
    "is_global_graph_prim",
    "on_shutdown",
    "register_node_type",
    "register_post_load_file_format_upgrade_callback",
    "register_pre_load_file_format_upgrade_callback",
    "register_python_node",
    "release_interface",
    "set_test_failure",
    "shutdown_compute_graph",
    "test_failure_count",
    "update"
]


class Attribute():
    """
    An attribute, defining a data type and value that belongs to a node
    """
    def __bool__(self) -> bool: ...
    def __eq__(self, arg0: Attribute) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def connect(self, path: Attribute, modify_usd: bool) -> bool: 
        """
        Connects this attribute with another attribute.  Assumes regular connection type.

        Args:
            path (omni.graph.core.Attribute): The destination attr
            modify_usd (bool): Whether to create USD.

        Returns:
            bool: True for success, False for fail
        """
    @staticmethod
    def connectEx(*args, **kwargs) -> typing.Any: 
        """
        Connects this attribute with another attribute.  Allows for different connection types.

        Args:
            info (omni.graph.core.ConnectionInfo): The ConnectionInfo object that contains both the attribute and the connection type
            modify_usd (bool): Whether to modify the underlying USD with this connection

        Returns:
            bool: True for success, False for fail
        """
    def connectPrim(self, path: str, modify_usd: bool, write: bool) -> bool: 
        """
        Connects this attribute to a prim that can represent a bundle connection or just a plain prim relationship

        Args:
            path (str): The path to the prim
            modify_usd (bool): Whether to modify USD.
            write (bool): Whether this connection represents a bundle
        Returns:
            bool: True for success, False for fail
        """
    def deprecation_message(self) -> str: 
        """
        Gets the deprecation message on an attribute, if it is deprecated.
        Typically this message gives guidance as to what the user should do instead of using the deprecated attribute.

        Returns:
            str: The message associated with a deprecated attribute
        """
    def disconnect(self, attribute: Attribute, modify_usd: bool) -> bool: 
        """
        Disconnects this attribute from another attribute.

        Args:
            attribute (omni.graph.core.Attribute): The destination attribute of the connection to remove
            modify_usd (bool): Whether to modify USD
        Returns:
            bool: True for success, False for fail
        """
    def disconnectPrim(self, path: str, modify_usd: bool, write: bool) -> bool: 
        """
        Disconnects this attribute to a prim that can represent a bundle connection or just a plain prim relationship

        Args:
            path (str): The path to the prim
            modify_usd (bool): Whether to modify USD.
            write (bool): Whether this connection represents a bundle
        Returns:
            bool: True for success, False for fail
        """
    @staticmethod
    def ensure_port_type_in_name(name: str, port_type: AttributePortType, is_bundle: bool) -> str: 
        """
        Return the attribute name with the port type namespace prepended if it isn't already present.

        Args:
            name (str): The attribute name, with or without the port prefix
            port_type (omni.graph.core.AttributePortType): The port type of the attribute
            is_bundle (bool): true if the attribute name is to be used in a bundle. Note that colon is an illegal character
            in bundled attributes so an underscore is used instead.

        Returns:
            str: The name with the proper prefix for the given port type
        """
    def get(self, on_gpu: bool = False, instance: int = 18446744073709551614) -> object: 
        """
        Get the value of the attribute

        Args:
            on_gpu (bool): Is the data to be retrieved from the GPU?
            instance (int): an instance index when getting value on an instantiated graph

        Returns:
            Any: Value of the attribute's data
        """
    def get_all_metadata(self) -> dict: 
        """
        Gets the attribute's metadata

        Returns:
            dict[str,str]: A dictionary of name:value metadata on the attribute
        """
    @staticmethod
    def get_array(*args, **kwargs) -> typing.Any: 
        """
        Gets the value of an array attribute

        Args:
            on_gpu (bool): Is the data to be retrieved from the GPU?
            get_for_write (bool): Should the data be retrieved for writing?
            reserved_element_count (int): If the data is to be retrieved for writing, preallocate this many elements
            instance (int): an instance index when getting value on an instantiated graph

        Returns:
            list[Any]: Value of the array attribute's data
        """
    @staticmethod
    def get_attribute_data(*args, **kwargs) -> typing.Any: 
        """
        Get the AttributeData object that can access the attribute's data

        Args:
            instance (int): an instance index when getting value on an instantiated graph

        Returns:
            omni.graph.core.AttributeData: The underlying attribute data accessor object for this attribute
        """
    def get_disable_dynamic_downstream_work(self) -> bool: 
        """
        Where we have dynamic scheduling, downstream nodes can have their execution disabled by turning on the flag
        in the upstream attribute.  Note you also have to call setDynamicDownstreamControl on the node to enable
        this feature.  See setDynamicDownstreamControl on INode for further information.

        Returns:
            bool: True if downstream nodes are disabled in dynamic scheduling, False otherwise
        """
    def get_downstream_connection_count(self) -> int: 
        """
        Gets the number of downstream connections to this attribute

        Returns:
            int: the number of downstream connections on this attribute.
        """
    def get_downstream_connections(self) -> typing.List[Attribute]: 
        """
        Gets the list of downstream connections to this attribute

        Returns:
            list[omni.graph.core.Attribute]: The list of downstream connections for this attribute.
        """
    @staticmethod
    def get_downstream_connections_info(*args, **kwargs) -> typing.Any: 
        """
        Returns the list of downstream connections for this attribute, with detailed connection information
        such as the connection type.

        Returns:
            list[omni.graph.core.ConnectionInfo]: A list of the downstream ConnectionInfo objects
        """
    def get_extended_type(self) -> ExtendedAttributeType: 
        """
        Get the extended type of the attribute

        Returns:
            omni.graph.core.ExtendedAttributeType: Extended type of the attribute data object
        """
    def get_handle(self) -> int: 
        """
        Get a handle to the attribute

        Returns:
            int: An opaque handle to the attribute
        """
    def get_metadata(self, key: str) -> str: 
        """
        Returns the metadata value for the given key.

        Args:
            key: (str) The metadata keyword

        Returns:
            str: Metadata value for the given keyword, or None if it is not defined
        """
    def get_metadata_count(self) -> int: 
        """
        Gets the number of metadata values on the attribute

        Returns:
            int: the number of metadata values currently defined on the attribute.
        """
    def get_name(self) -> str: 
        """
        Get the attribute's name

        Returns:
            str: The name of the current attribute.
        """
    @staticmethod
    def get_node(*args, **kwargs) -> typing.Any: 
        """
        Gets the node to which this attribute belongs

        Returns:
            omni.graph.core.Node: The node associated with the attribute
        """
    def get_path(self) -> str: 
        """
        Get the path to the attribute

        Returns:
            str: The full path to the attribute, including the node path.
        """
    def get_port_type(self) -> AttributePortType: 
        """
        Gets the attribute's port type (input, output, or state)

        Returns:
            omni.graph.core.AttributePortType: The port type of the attribute.
        """
    @staticmethod
    def get_port_type_from_name(name: str) -> AttributePortType: 
        """
        Parse the port type from the given attribute name if present. The port type is indicated by a prefix seperated by
        a colon or underscore in the case of bundled attributes.

        Args:
            name The attribute name

        Returns:
            omni.graph.core.AttributePortType: The port type indicated by the attribute prefix if present.
                AttributePortType.UNKNOWN if there is no recognized prefix.
        """
    @staticmethod
    def get_resolved_type(*args, **kwargs) -> typing.Any: 
        """
        Get the resolved type of the attribute

        Returns:
            omni.graph.core.Type: Resolved type of the attribute data object, or the hardcoded type for regular attributes
        """
    def get_type_name(self) -> str: 
        """
        Get the name of the attribute's type

        Returns:
            str: The type name of the current attribute.
        """
    def get_union_types(self) -> object: 
        """
        Get the list of types accepted by a union attribute

        Returns:
            list[str]: The list of accepted types for the attribute if it is an extended union type, else None
        """
    def get_upstream_connection_count(self) -> int: 
        """
        Gets the number of upstream connections to this attribute

        Returns:
            int: the number of upstream connections on this attribute.
        """
    def get_upstream_connections(self) -> typing.List[Attribute]: 
        """
        Gets the list of upstream connections to this attribute

        Returns:
            list[omni.graph.core.Attribute]: The list of upstream connections for this attribute.
        """
    @staticmethod
    def get_upstream_connections_info(*args, **kwargs) -> typing.Any: 
        """
        Returns the list of upstream connections for this attribute, with detailed connection information
        such as the connection type.

        Returns:
            list[omni.graph.core.ConnectionInfo]: A list of the upstream ConnectionInfo objects
        """
    def is_array(self) -> bool: 
        """
        Checks if the attribute is an array type.

        Returns:
            bool: True if the attribute data type is an array
        """
    def is_compatible(self, attribute: Attribute) -> bool: 
        """
        Checks to see if this attribute is compatible with another one, in particular the data types they use

        Args:
            attribute (omni.graph.core.Attribute): Attribute for which compatibility is to be checked

        Returns:
            bool: True if this attribute is compatible with "attribute"
        """
    def is_connected(self, attribute: Attribute) -> bool: 
        """
        Checks to see if this attribute has a connection to another attribute

        Args:
            attribute (Attribute): Attribute for which the connection is to be checked

        Returns:
            bool: True if this attribute is connected to another, either as source or destination
        """
    def is_deprecated(self) -> bool: 
        """
        Checks whether an attribute is deprecated. Deprecated attributes should not be used as
        they will be removed in a future version.

        Returns:
            bool: True if the attribute is deprecated
        """
    def is_dynamic(self) -> bool: 
        """
        Checks to see if an attribute is dynamic

        Returns:
            bool: True if the current attribute is a dynamic attribute (not in the node type definition).
        """
    def is_runtime_constant(self) -> bool: 
        """
        Checks is this attribute is a runtime constant.

        Runtime constants will keep the same value every frame, for every instance.
        This property can be taken advantage of in vectorized compute.

        Returns:
            bool: True if the attribute is a runtime constant
        """
    def is_valid(self) -> bool: 
        """
        Checks if the current attribute is valid.

        Returns:
            bool: True if the attribute reference points to a valid attribute object
        """
    @staticmethod
    def map_to_target(*args, **kwargs) -> typing.Any: 
        """
        Maps the attribute to another one on the graph target.

        Args:
            target_attrib_name (str): the attribute name on the graph target prim to map this attribute to
            fabric_id (integer): (optional) The fabric id cache in which the attribute lives.
                                  Uses the default fabric cache associated to the graph if not specified
        Returns:
            FunctionResult: Whether the call was immediately applied, failed or deferred. Deferral can
                            happen when the graph does not yet have any explicit instances or a prim view applied
        """
    def register_value_changed_callback(self, func: object) -> None: 
        """
        Registers a function that will be invoked when the value of the given attribute changes.

        Note that an attribute can have one and only one callback. Subsequent calls will replace
        previously set callbacks. Passing None for the function argument will clear the existing
        callback.

        Args:
            func (callable): A function with one argument representing the attribute that changed.
        """
    @staticmethod
    def remove_port_type_from_name(name: str, is_bundle: bool) -> str: 
        """
        Find the attribute name with the port type removed if it is present. For example "inputs:attr" becomes "attr"

        Args:
            name (str): The attribute name, with or without the port prefix
            is_bundle (bool): True if the attribute name is to be used in a bundle. Note that colon is an illegal character
                              in bundled attributes so an underscore is used instead.

        Returns:
            str: The name with the port type prefix removed
        """
    def set(self, value: object, on_gpu: bool = False, instance: int = 18446744073709551614) -> bool: 
        """
        Sets the value of the attribute's data

        Args:
            value (Any): New value of the attribute's data
            on_gpu (bool): Is the data to be set on the GPU?
            instance (int): an instance index when setting value on an instantiated graph

        Returns:
            bool: True if the value was successfully set
        """
    def set_default(self, value: object, on_gpu: bool = False) -> bool: 
        """
        Sets the default value of the attribute's data (value when not connected)

        Args:
            value (Any): New value of the default attribute's data
            on_gpu (bool): Is the data to be set on the GPU?

        Returns:
            bool: True if the value was successfully set
        """
    def set_disable_dynamic_downstream_work(self, disable: bool) -> None: 
        """
        Where we have dynamic scheduling, downstream nodes can have their execution disabled by turning on the flag
        in the upstream attribute.  Note you also have to call setDynamicDownstreamControl on the node to enable
        this feature.  This function allows you to set the flag on the attribute that will disable the downstream
        node. See setDynamicDownstreamControl on INode for further information.

        Args:
            disable (bool): Whether to disable downstream connected nodes in dynamic scheduling.
        """
    def set_metadata(self, key: str, value: str) -> bool: 
        """
        Sets the metadata value for the given key

        Args:
            key (str): The metadata keyword
            value (str): The value of the metadata
        """
    @staticmethod
    def set_resolved_type(*args, **kwargs) -> typing.Any: 
        """
        Sets the resolved type for the extended attribute.

        Only valid for attributes with union/any extended types, who's
        type has not yet been resolved.  Should only be called from on_connection_type_resolve() callback.  This operation
        is async and may fail if the type cannot be resolved as requested.

        Args:
            resolved_type (omni.graph.core.Type): The type to resolve the attribute to
        """
    def update_attribute_value(self, update_immediately: bool) -> bool: 
        """
        Requests the value of an attribute.  In the cases of lazy evaluation systems, this
        generates the "pull" that causes the attribute to update its value.

        Args:
            update_immediately (bool): Whether to update the attribute value immediately.  If True, the function
                                       will block until the attribute is update and then return. If False, the
                                       attribute will be updated in the next update loop.

        Returns:
            Any: The value of the attribute
        """
    @staticmethod
    def write_complete(attributes: typing.Sequence) -> None: 
        """
        Warn the framework that writing to the provided attributes is done, so it can trigger callbacks attached to them

        Args:
            attributes (list[omni.graph.core.Attribute]): List of attributes that are done writing
            
        """
    @property
    def gpu_ptr_kind(self) -> typing.Any:
        """
        Defines the memory space that GPU array data pointers live in.

        :type: typing.Any
        """
    @gpu_ptr_kind.setter
    def gpu_ptr_kind(*args, **kwargs) -> None:
        """
        Defines the memory space that GPU array data pointers live in.
        """
    @property
    def is_optional_for_compute(self) -> bool:
        """
        Flag that is set when an attribute need not be valid for compute() to happen. bool: 

        :type: bool
        """
    @is_optional_for_compute.setter
    def is_optional_for_compute(self, arg1: bool) -> None:
        """
        Flag that is set when an attribute need not be valid for compute() to happen. bool: 
        """
    @property
    def target_mapping(self) -> object:
        """
            Returns the attribute name on the graph target the attribute is mapped to

            Returns:
                string: The name of the target, or None if there isn't one mapped
            

        :type: object
        """
    resolved_prefix = ''
    pass
class AttributeData():
    """
    Reference to data defining an attribute's value
    """
    def __bool__(self) -> bool: ...
    def __eq__(self, arg0: AttributeData) -> bool: ...
    def __hash__(self) -> int: ...
    def as_read_only(self) -> AttributeData: 
        """
        Returns read-only variant of the attribute data.

        Returns:
            AttributeData: Read-only variant of the attribute data.
        """
    def copy_data(self, rhs: AttributeData) -> bool: 
        """
        Copies the AttributeData data into this object's data.

        Args:
            rhs (omni.graph.core.AttributeData): Attribute data to be copied - must be the same type as the current object to work

        Returns:
            bool: True if the data was successfully copied, else False.
        """
    def cpu_valid(self) -> bool: 
        """
        Returns whether this attribute data object is currently valid on the cpu.

        Returns:
            bool: True if the data represented by this object currently has a valid value in CPU memory
        """
    def get(self, on_gpu: bool = False) -> object: 
        """
        Gets the current value of the attribute data

        Args:
            on_gpu (bool): Is the data to be retrieved from the GPU?

        Returns:
            Any: Value of the attribute data
        """
    @staticmethod
    def get_array(*args, **kwargs) -> typing.Any: 
        """
        Gets the current value of the attribute data.

        Args:
            on_gpu (bool): Is the data to be retrieved from the GPU?
            get_for_write (bool): Should the data be retrieved for writing?
            reserved_element_count (int): If the data is to be retrieved for writing, preallocate this many elements

        Returns:
            Any: Value of the array attribute data
        """
    def get_extended_type(self) -> ExtendedAttributeType: 
        """
        Returns the extended type of the current attribute data.

        Returns:
            omni.graph.core.ExtendedAttributeType: Extended type of the attribute data object
        """
    def get_name(self) -> str: 
        """
        Returns the name of the current attribute data.

        Returns:
            str: Name of the attribute data object
        """
    def get_resolved_type(self) -> Type: 
        """
        Returns the resolved type of the extended attribute data. Only valid for attributes with union/any extended types.

        Returns:
            omni.graph.core.Type: Resolved type of the attribute data object
        """
    def get_type(self) -> Type: 
        """
        Returns the type of the current attribute data.

        Returns:
            omni.graph.core.Type: Type of the attribute data object
        """
    def gpu_valid(self) -> bool: 
        """
        Returns whether this attribute data object is currently valid on the gpu.

        Returns:
            bool: True if the data represented by this object currently has a valid value in GPU memory
        """
    def is_read_only(self) -> bool: 
        """
        Returns whether this attribute data object is read-only or not.

        Returns:
            bool: True if the data represented by this object is read-only
        """
    def is_valid(self) -> bool: 
        """
        Returns whether this attribute data object is valid or not.

        Returns:
            bool: True if the data represented by this object is valid
        """
    def resize(self, element_count: int) -> bool: 
        """
        Sets the number of elements in the array represented by this object.

        Args:
            element_count (int): Number of elements to reserve in the array

        Returns:
            bool: True if the array was resized, False if not (e.g. if the attribute data was not an array type)
        """
    def set(self, value: object, on_gpu: bool = False) -> bool: 
        """
        Sets the value of the attribute data

        Args:
            value (Any): New value of the attribute data
            on_gpu (bool): Is the data to be set on the GPU?

        Returns:
            bool: True if the value was successfully set
        """
    def size(self) -> int: 
        """
        Returns the size of the data represented by this object (1 if it's not an array).

        Returns:
            int: Number of elements in the data
        """
    @property
    def gpu_ptr_kind(self) -> PtrToPtrKind:
        """
        Defines the memory space that GPU array data pointers live in

        :type: PtrToPtrKind
        """
    @gpu_ptr_kind.setter
    def gpu_ptr_kind(self, arg1: PtrToPtrKind) -> None:
        """
        Defines the memory space that GPU array data pointers live in
        """
    pass
class AttributePortType():
    """
    Port side of the attribute on its node

    Members:

      ATTRIBUTE_PORT_TYPE_INPUT : Deprecated: use og.AttributePortType.INPUT

      ATTRIBUTE_PORT_TYPE_OUTPUT : Deprecated: use og.AttributePortType.OUTPUT

      ATTRIBUTE_PORT_TYPE_STATE : Deprecated: use og.AttributePortType.STATE

      ATTRIBUTE_PORT_TYPE_UNKNOWN : Deprecated: use og.AttributePortType.UNKNOWN

      INPUT : Attribute is an input

      OUTPUT : Attribute is an output

      STATE : Attribute is state

      UNKNOWN : Attribute port type is unknown
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ATTRIBUTE_PORT_TYPE_INPUT: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: 0>
    ATTRIBUTE_PORT_TYPE_OUTPUT: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: 1>
    ATTRIBUTE_PORT_TYPE_STATE: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: 2>
    ATTRIBUTE_PORT_TYPE_UNKNOWN: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_UNKNOWN: 3>
    INPUT: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: 0>
    OUTPUT: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: 1>
    STATE: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: 2>
    UNKNOWN: omni.graph.core._omni_graph_core.AttributePortType # value = <AttributePortType.ATTRIBUTE_PORT_TYPE_UNKNOWN: 3>
    __members__: dict # value = {'ATTRIBUTE_PORT_TYPE_INPUT': <AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: 0>, 'ATTRIBUTE_PORT_TYPE_OUTPUT': <AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: 1>, 'ATTRIBUTE_PORT_TYPE_STATE': <AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: 2>, 'ATTRIBUTE_PORT_TYPE_UNKNOWN': <AttributePortType.ATTRIBUTE_PORT_TYPE_UNKNOWN: 3>, 'INPUT': <AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: 0>, 'OUTPUT': <AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: 1>, 'STATE': <AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: 2>, 'UNKNOWN': <AttributePortType.ATTRIBUTE_PORT_TYPE_UNKNOWN: 3>}
    pass
class AttributeRole():
    """
    Interpretation applied to the attribute data

    Members:

      APPLIED_SCHEMA : Data is to be interpreted as an applied schema

      BUNDLE : Data is to be interpreted as an OmniGraph Bundle

      COLOR : Data is to be interpreted as RGB or RGBA color

      EXECUTION : Data is to be interpreted as an Action Graph execution pin

      FRAME : Data is to be interpreted as a 4x4 matrix representing a reference frame

      MATRIX : Data is to be interpreted as a square matrix of values

      NONE : Data has no special role

      NORMAL : Data is to be interpreted as a normal vector

      OBJECT_ID : Data is to be interpreted as a unique object identifier

      PATH : Data is to be interpreted as a path to a USD element

      POSITION : Data is to be interpreted as a position or point vector

      PRIM_TYPE_NAME : Data is to be interpreted as the name of a prim type

      QUATERNION : Data is to be interpreted as a rotational quaternion

      TARGET : Data is to be interpreted as a relationship target path

      TEXCOORD : Data is to be interpreted as texture coordinates

      TEXT : Data is to be interpreted as a text string

      TIMECODE : Data is to be interpreted as a time code

      TRANSFORM : Deprecated

      VECTOR : Data is to be interpreted as a simple vector

      UNKNOWN : Data role is currently unknown
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    APPLIED_SCHEMA: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.APPLIED_SCHEMA: 11>
    BUNDLE: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.BUNDLE: 16>
    COLOR: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.COLOR: 4>
    EXECUTION: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.EXECUTION: 13>
    FRAME: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.FRAME: 8>
    MATRIX: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.MATRIX: 14>
    NONE: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.NONE: 0>
    NORMAL: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.NORMAL: 2>
    OBJECT_ID: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.OBJECT_ID: 15>
    PATH: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.PATH: 17>
    POSITION: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.POSITION: 3>
    PRIM_TYPE_NAME: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.PRIM_TYPE_NAME: 12>
    QUATERNION: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.QUATERNION: 6>
    TARGET: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TARGET: 20>
    TEXCOORD: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TEXCOORD: 5>
    TEXT: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TEXT: 10>
    TIMECODE: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TIMECODE: 9>
    TRANSFORM: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TRANSFORM: 7>
    UNKNOWN: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.UNKNOWN: 21>
    VECTOR: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.VECTOR: 1>
    __members__: dict # value = {'APPLIED_SCHEMA': <AttributeRole.APPLIED_SCHEMA: 11>, 'BUNDLE': <AttributeRole.BUNDLE: 16>, 'COLOR': <AttributeRole.COLOR: 4>, 'EXECUTION': <AttributeRole.EXECUTION: 13>, 'FRAME': <AttributeRole.FRAME: 8>, 'MATRIX': <AttributeRole.MATRIX: 14>, 'NONE': <AttributeRole.NONE: 0>, 'NORMAL': <AttributeRole.NORMAL: 2>, 'OBJECT_ID': <AttributeRole.OBJECT_ID: 15>, 'PATH': <AttributeRole.PATH: 17>, 'POSITION': <AttributeRole.POSITION: 3>, 'PRIM_TYPE_NAME': <AttributeRole.PRIM_TYPE_NAME: 12>, 'QUATERNION': <AttributeRole.QUATERNION: 6>, 'TARGET': <AttributeRole.TARGET: 20>, 'TEXCOORD': <AttributeRole.TEXCOORD: 5>, 'TEXT': <AttributeRole.TEXT: 10>, 'TIMECODE': <AttributeRole.TIMECODE: 9>, 'TRANSFORM': <AttributeRole.TRANSFORM: 7>, 'VECTOR': <AttributeRole.VECTOR: 1>, 'UNKNOWN': <AttributeRole.UNKNOWN: 21>}
    pass
class AttributeType():
    """
    Utilities for operating with the attribute data type class omni.graph.core.Type and related types
    """
    @staticmethod
    def base_data_size(type: Type) -> int: 
        """
        Figure out how much space a base data type occupies in memory inside Fabric.
        This will not necessarily be the same as the space occupied by the Python data, which is only transient.
        Multiply by the tuple count and the array element count to get the full size of any given piece of data.

        Args:
            type (omni.graph.core.Type): The type object whose base data type size is to be found

        Returns:
            int: Number of bytes one instance of the base data type occupies in Fabric
        """
    @staticmethod
    def get_unions() -> dict: 
        """
        Returns a dictionary containing the names and contents of the ogn attribute union types.

        Returns:
            dict[str, list[str]]: Dictionary that maps the attribute union names to list of associated ogn types
        """
    @staticmethod
    def is_legal_ogn_type(type: Type) -> bool: 
        """
        Check to see if the type combination has a legal representation in OGN.

        Args:
            type (omni.graph.core.Type): The type object to be checked

        Returns:
            bool: True if the type represents a legal OGN type, otherwise False
        """
    @staticmethod
    def sdf_type_name_from_type(type: Type) -> object: 
        """
        Given an attribute type find the corresponding SDF type name for it, None if there is none, e.g. a 'bundle'

        Args:
            type (omni.graph.core.Type): The type to be converted

        Returns:
            str: The SDF type name of the type, or None if there is no corresponding SDF type
        """
    @staticmethod
    def type_from_ogn_type_name(ogn_type_name: str) -> Type: 
        """
        Parse an OGN attribute type name into the corresponding omni.graph.core.Type description.

        Args:
            ogn_type_name (str): The OGN-style attribute type name to be converted

        Returns:
            omni.graph.core.Type: Type corresponding to the attribute type name in OGN format.
            Type object will be the unknown type if the type name could be be parsed.
        """
    @staticmethod
    def type_from_sdf_type_name(sdf_type_name: str) -> Type: 
        """
        Parse an SDF attribute type name into the corresponding omni.graph.core.Type description.
        Note that SDF types are not capable of representing some of the valid types - use typeFromOgnTypeName()
        for a more comprehensive type name description.

        Args:
            sdf_type_name (str): The SDF-style attribute type name to be converted

        Returns:
            omni.graph.core.Type: Type corresponding to the attribute type name in SDF format.
            Type object will be the unknown type if the type name could be be parsed.
        """
    pass
class BaseDataType():
    """
    Basic data type for attribute data

    Members:

      ASSET : Data represents an Asset

      BOOL : Data is a boolean

      CONNECTION : Data is a special value representing a connection

      DOUBLE : Data is a double precision floating point value

      FLOAT : Data is a single precision floating point value

      HALF : Data is a half precision floating point value

      INT : Data is a 32-bit integer

      INT64 : Data is a 64-bit integer

      PRIM : Data is deprecated

      RELATIONSHIP : Data is a relationship to a USD prim

      TAG : Data is a special Fabric tag

      TOKEN : Data is a reference to a unique shared string

      UCHAR : Data is an 8-bit unsigned character

      UINT : Data is a 32-bit unsigned integer

      UINT64 : Data is a 64-bit unsigned integer

      UNKNOWN : Data type is currently unknown
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ASSET: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.ASSET: 12>
    BOOL: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.BOOL: 1>
    CONNECTION: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.CONNECTION: 14>
    DOUBLE: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.DOUBLE: 9>
    FLOAT: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.FLOAT: 8>
    HALF: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.HALF: 7>
    INT: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.INT: 3>
    INT64: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.INT64: 5>
    PRIM: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.PRIM: 13>
    RELATIONSHIP: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.RELATIONSHIP: 11>
    TAG: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.TAG: 15>
    TOKEN: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.TOKEN: 10>
    UCHAR: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.UCHAR: 2>
    UINT: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.UINT: 4>
    UINT64: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.UINT64: 6>
    UNKNOWN: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.UNKNOWN: 0>
    __members__: dict # value = {'ASSET': <BaseDataType.ASSET: 12>, 'BOOL': <BaseDataType.BOOL: 1>, 'CONNECTION': <BaseDataType.CONNECTION: 14>, 'DOUBLE': <BaseDataType.DOUBLE: 9>, 'FLOAT': <BaseDataType.FLOAT: 8>, 'HALF': <BaseDataType.HALF: 7>, 'INT': <BaseDataType.INT: 3>, 'INT64': <BaseDataType.INT64: 5>, 'PRIM': <BaseDataType.PRIM: 13>, 'RELATIONSHIP': <BaseDataType.RELATIONSHIP: 11>, 'TAG': <BaseDataType.TAG: 15>, 'TOKEN': <BaseDataType.TOKEN: 10>, 'UCHAR': <BaseDataType.UCHAR: 2>, 'UINT': <BaseDataType.UINT: 4>, 'UINT64': <BaseDataType.UINT64: 6>, 'UNKNOWN': <BaseDataType.UNKNOWN: 0>}
    pass
class BucketId():
    """
    internal Use only, and obsolete: This type was only useful for writing back to USD, which cannot be achieved anymore through this type.
                            However, writing back to USD can still be achieved by using the USD API directly.
    """
    def __init__(self, id: int) -> None: 
        """
        [OBSOLETE] Set up the initial value of the bucket id

                    Args:
                        id (int): [OBSOLETE] Unique identifier of a bucket of Fabric data
        """
    @property
    def id(self) -> int:
        """
        Internal Use - [OBSOLETE] Unique identifier of a bucket of Fabric data

        :type: int
        """
    @id.setter
    def id(self, arg0: int) -> None:
        """
        Internal Use - [OBSOLETE] Unique identifier of a bucket of Fabric data
        """
    pass
class BundleChangeType():
    """
    Enumeration representing the type of change that occurred in a bundle.

    This enumeration is used to identify the kind of modification that has taken place in a bundle or attribute.
    It's used as the return type for functions that check bundles and attributes, signaling whether those have been
    modified or not.

    Members:

      NONE : Indicates that no change has occurred in the bundle.

      MODIFIED : Indicates that the bundle has been modified.
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    MODIFIED: omni.graph.core._omni_graph_core.BundleChangeType # value = <BundleChangeType.MODIFIED: 1>
    NONE: omni.graph.core._omni_graph_core.BundleChangeType # value = <BundleChangeType.NONE: 0>
    __members__: dict # value = {'NONE': <BundleChangeType.NONE: 0>, 'MODIFIED': <BundleChangeType.MODIFIED: 1>}
    pass
class ComputeGraph():
    """
    Main OmniGraph interface registered with the extension system
    """
    pass
class ConnectionInfo():
    """
    Attribute and connection type in a given graph connection
    """
    def __init__(self, attr: Attribute, connection_type: ConnectionType) -> None: 
        """
        Set up the connection info data

        Args:
            attr (omni.graph.core.Attribute): Attribute in the connection
            connection_type (omni.graph.core.ConnectionType): Type of connection
        """
    @property
    def attr(self) -> Attribute:
        """
        Attribute being connected

        :type: Attribute
        """
    @attr.setter
    def attr(self, arg0: Attribute) -> None:
        """
        Attribute being connected
        """
    @property
    def connection_type(self) -> ConnectionType:
        """
        Type of connection

        :type: ConnectionType
        """
    @connection_type.setter
    def connection_type(self, arg0: ConnectionType) -> None:
        """
        Type of connection
        """
    pass
class ConnectionType():
    """
    Type of connection)

    Members:

      CONNECTION_TYPE_REGULAR : Normal connection

      CONNECTION_TYPE_DATA_ONLY : Connection only represents data access, not execution flow

      CONNECTION_TYPE_EXECUTION : Connection only represents execution flow, not data access
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CONNECTION_TYPE_DATA_ONLY: omni.graph.core._omni_graph_core.ConnectionType # value = <ConnectionType.CONNECTION_TYPE_DATA_ONLY: 1>
    CONNECTION_TYPE_EXECUTION: omni.graph.core._omni_graph_core.ConnectionType # value = <ConnectionType.CONNECTION_TYPE_EXECUTION: 2>
    CONNECTION_TYPE_REGULAR: omni.graph.core._omni_graph_core.ConnectionType # value = <ConnectionType.CONNECTION_TYPE_REGULAR: 0>
    __members__: dict # value = {'CONNECTION_TYPE_REGULAR': <ConnectionType.CONNECTION_TYPE_REGULAR: 0>, 'CONNECTION_TYPE_DATA_ONLY': <ConnectionType.CONNECTION_TYPE_DATA_ONLY: 1>, 'CONNECTION_TYPE_EXECUTION': <ConnectionType.CONNECTION_TYPE_EXECUTION: 2>}
    pass
class ExecutionAttributeState():
    """
    Current execution state of an attribute [DEPRECATED: See omni.graph.action.IActionGraph]

    Members:

      DISABLED : Execution is disabled

      ENABLED : Execution is enabled

      ENABLED_AND_PUSH : Output attribute connection is enabled and the node is pushed to the evaluation stack

      LATENT_PUSH : Push this node as a latent event for the current entry point

      LATENT_FINISH : Output attribute connection is enabled and the latent state is finished for this node
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    DISABLED: omni.graph.core._omni_graph_core.ExecutionAttributeState # value = <ExecutionAttributeState.DISABLED: 0>
    ENABLED: omni.graph.core._omni_graph_core.ExecutionAttributeState # value = <ExecutionAttributeState.ENABLED: 1>
    ENABLED_AND_PUSH: omni.graph.core._omni_graph_core.ExecutionAttributeState # value = <ExecutionAttributeState.ENABLED_AND_PUSH: 2>
    LATENT_FINISH: omni.graph.core._omni_graph_core.ExecutionAttributeState # value = <ExecutionAttributeState.LATENT_FINISH: 4>
    LATENT_PUSH: omni.graph.core._omni_graph_core.ExecutionAttributeState # value = <ExecutionAttributeState.LATENT_PUSH: 3>
    __members__: dict # value = {'DISABLED': <ExecutionAttributeState.DISABLED: 0>, 'ENABLED': <ExecutionAttributeState.ENABLED: 1>, 'ENABLED_AND_PUSH': <ExecutionAttributeState.ENABLED_AND_PUSH: 2>, 'LATENT_PUSH': <ExecutionAttributeState.LATENT_PUSH: 3>, 'LATENT_FINISH': <ExecutionAttributeState.LATENT_FINISH: 4>}
    pass
class ExtendedAttributeType():
    """
    Extended attribute type, if any

    Members:

      EXTENDED_ATTR_TYPE_REGULAR : Deprecated: use og.ExtendedAttributeType.REGULAR

      EXTENDED_ATTR_TYPE_UNION : Deprecated: use og.ExtendedAttributeType.UNION

      EXTENDED_ATTR_TYPE_ANY : Deprecated: use og.ExtendedAttributeType.ANY

      REGULAR : Attribute has a fixed data type

      UNION : Attribute has a list of allowable types of data

      ANY : Attribute can take any type of data
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ANY: omni.graph.core._omni_graph_core.ExtendedAttributeType # value = <ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY: 2>
    EXTENDED_ATTR_TYPE_ANY: omni.graph.core._omni_graph_core.ExtendedAttributeType # value = <ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY: 2>
    EXTENDED_ATTR_TYPE_REGULAR: omni.graph.core._omni_graph_core.ExtendedAttributeType # value = <ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR: 0>
    EXTENDED_ATTR_TYPE_UNION: omni.graph.core._omni_graph_core.ExtendedAttributeType # value = <ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION: 1>
    REGULAR: omni.graph.core._omni_graph_core.ExtendedAttributeType # value = <ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR: 0>
    UNION: omni.graph.core._omni_graph_core.ExtendedAttributeType # value = <ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION: 1>
    __members__: dict # value = {'EXTENDED_ATTR_TYPE_REGULAR': <ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR: 0>, 'EXTENDED_ATTR_TYPE_UNION': <ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION: 1>, 'EXTENDED_ATTR_TYPE_ANY': <ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY: 2>, 'REGULAR': <ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR: 0>, 'UNION': <ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION: 1>, 'ANY': <ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY: 2>}
    pass
class FileFormatVersion():
    """
    Version number for the OmniGraph file format
    """
    def __eq__(self, arg0: FileFormatVersion) -> bool: ...
    def __ge__(self, arg0: FileFormatVersion) -> bool: ...
    def __gt__(self, arg0: FileFormatVersion) -> bool: ...
    def __init__(self, major_version: int, minor_version: int) -> None: 
        """
        Set up the values defining the file format version

        Args:
            major_version (int): Major version, introduces incompatibilities
            minor_version (int): Minor version, introduces compatible changes only
        """
    def __le__(self, arg0: FileFormatVersion) -> bool: ...
    def __lt__(self, arg0: FileFormatVersion) -> bool: ...
    def __neq__(self, arg0: FileFormatVersion) -> bool: ...
    def __str__(self) -> str: ...
    @property
    def majorVersion(self) -> int:
        """
        Major version, introduces incompatibilities

        :type: int
        """
    @majorVersion.setter
    def majorVersion(self, arg0: int) -> None:
        """
        Major version, introduces incompatibilities
        """
    @property
    def minorVersion(self) -> int:
        """
        Minor version, introduces compatible changes only

        :type: int
        """
    @minorVersion.setter
    def minorVersion(self, arg0: int) -> None:
        """
        Minor version, introduces compatible changes only
        """
    __hash__ = None
    pass
class FunctionResult():
    """
    Value indicating whether a function call succeeded

    Members:

      FAILURE : The function call failed

      SUCCESS : The function call succeeded

      DEFERRED : The action invoked by the function call has been deferred
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    DEFERRED: omni.graph.core._omni_graph_core.FunctionResult # value = <FunctionResult.DEFERRED: 2>
    FAILURE: omni.graph.core._omni_graph_core.FunctionResult # value = <FunctionResult.FAILURE: 0>
    SUCCESS: omni.graph.core._omni_graph_core.FunctionResult # value = <FunctionResult.SUCCESS: 1>
    __members__: dict # value = {'FAILURE': <FunctionResult.FAILURE: 0>, 'SUCCESS': <FunctionResult.SUCCESS: 1>, 'DEFERRED': <FunctionResult.DEFERRED: 2>}
    pass
class Graph():
    """
    Object containing everything necessary to execute a connected set of nodes.
    """
    def __bool__(self) -> bool: ...
    def __eq__(self, arg0: Graph) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def change_pipeline_stage(self, newPipelineStage: GraphPipelineStage) -> None: 
        """
        Change the pipeline stage that this graph is in (simulation, pre-render, post-render, on-demand)

        Args:
            newPipelineStage (omni.graph.core.GraphPipelineStage): The new pipeline stage of the graph
        """
    def create_graph_as_node(self, name: str, path: str, evaluator: str, is_global_graph: bool, is_backed_by_usd: bool, backing_type: GraphBackingType, pipeline_stage: GraphPipelineStage, evaluation_mode: GraphEvaluationMode = GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC) -> Node: 
        """
        Creates a graph that is wrapped by a node in the current graph.

        Args:
            name (str): The name of the node
            path (str): The path to the graph
            evaluator (str): The name of the evaluator to use for the graph
            is_global_graph (bool): Whether this is a global graph
            is_backed_by_usd (bool): Whether the constructs are to be backed by USD
            backing_type (omni.graph.core.GraphBackingType): The kind of cache backing this graph
            pipeline_stage (omni.graph.core.GraphPipelineStage): What stage in the pipeline the global graph is at
                                                      (simulation, pre-render, post-render)
            evaluation_mode (omni.graph.core.GraphEvaluationMode): What mode to use when evaluating the graph
        Returns:
            omni.graph.core.Node: Node wrapping the graph that was created
        """
    def create_node(self, path: str, node_type: str, use_usd: bool) -> Node: 
        """
        Given the path to the node and the type of the node, creates a node of that type at that path.

        Args:
            path (str): The path to the node
            node_type (str): The type of the node
            use_usd (bool): Whether or not to create the USD backing for the node

        Returns:
            omni.graph.core.Node: The newly created node
        """
    @staticmethod
    def create_runtime_variable(*args, **kwargs) -> typing.Any: 
        """
        Creates a variable on the graph without USD backing.

        Args:
            name (str): The name of the variable
            type (omni.graph.core.Type): The type of the variable to create.
            value (Any): The initial value to set on the variable, default is None.

        Returns:
            omni.graph.core.IVariable: A reference to the newly created variable, or None if the variable could not be created.
        """
    def create_subgraph(self, subgraphPath: str, evaluator: str = '', createUsd: bool = True) -> Graph: 
        """
        Given the path to the subgraph, create the subgraph at that path.

        Args:
            subgraphPath (str): The path to the subgraph
            evaluator (str): The evaluator type
            createUsd (bool): Whether or not to create the USD backing for the node

        Returns:
            omni.graph.core.Graph: Subgraph object created for the given path.
        """
    @staticmethod
    def create_variable(*args, **kwargs) -> typing.Any: 
        """
        Creates a variable on the graph.

        Args:
            name (str): The name of the variable
            type (omni.graph.core.Type): The type of the variable to create.

        Returns:
            omni.graph.core.IVariable: A reference to the newly created variable, or None if the variable could not be created.
        """
    def deregister_error_status_change_callback(self, status_change_handle: int) -> None: 
        """
        De-registers the error status change callback to be invoked when the error status of nodes change during evaluation.

        Args:
            status_change_handle (int): The handle that was returned during the register_error_status_change_callback call
        """
    def destroy_node(self, node_path: str, update_usd: bool) -> bool: 
        """
        Given the path to the node, destroys the node at that path.

        Args:
            node_path (str): The path to the node
            update_usd (bool): Whether or not to destroy the USD backing for the node

        Returns:
            bool: True if the node was successfully destroyed
        """
    def evaluate(self) -> None: 
        """
        Tick the graph by causing it to evaluate.
        """
    def find_variable(self, name: str) -> IVariable: 
        """
        Find the variable with the given name in the graph.

        Args:
            name (str): The name of the variable to find.

        Returns:
            omni.graph.core.IVariable | None: The variable with the given name, or None if not found.
        """
    @staticmethod
    def get_context(*args, **kwargs) -> typing.Any: 
        """
        Gets the context associated to the graph

        Returns:
            omni.graph.core.GraphContext: The context associated to the graph
        """
    @staticmethod
    def get_default_graph_context(*args, **kwargs) -> typing.Any: 
        """
        Gets the default context associated with this graph

        Returns:
            omni.graph.core.GraphContext: The default graph context associated with this graph.
        """
    def get_evaluator_name(self) -> str: 
        """
        Gets the name of the evaluator being used on this graph

        Returns:
            str: The name of the graph evaluator (dirty_push, push, execution)
        """
    def get_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Get the event stream the graph uses for notification of changes.

        Returns:
            carb.events.IEventStream: Event stream to monitor for graph changes
        """
    def get_graph_backing_type(self) -> GraphBackingType: 
        """
        Gets the data type backing this graph

        Returns:
            omni.graph.core.GraphBackingType:  Returns the type of data structure backing this graph
        """
    def get_handle(self) -> int: 
        """
        Gets a unique handle identifier for this graph

        Returns:
            int: Unique handle identifier for this graph
        """
    def get_instance_count(self) -> int: 
        """
        Gets the number of instances this graph has

        Returns:
            int: The number of instances the graph has (0 if the graph is standalone).
        """
    def get_node(self, path: str) -> Node: 
        """
        Given a path to the node, returns the object for the node.

        Args:
            path (str): The path to the node

        Returns:
            omni.graph.core.Node: Node object for the given path, None if it does not exist
        """
    def get_nodes(self) -> typing.List[Node]: 
        """
        Gets the list of nodes currently in this graph

        Returns:
            list[omni.graph.core.Node]: The nodes in this graph.
        """
    def get_owning_compound_node(self) -> Node: 
        """
        Returns the compound node for which this graph is the compound subgraph of.

        Returns:
            (og.Node) If this graph is a compound graph, the owning compound node. Otherwise, this an invalid node is returned.
        """
    def get_parent_graph(self) -> object: 
        """
        Gets the immediate parent graph of this graph

        Returns:
            omni.graph.core.Graph | None: The immediate parent graph of this graph (may be None)
        """
    def get_path_to_graph(self) -> str: 
        """
        Gets the path to this graph

        Returns:
            str: The path to this graph (may be empty).
        """
    def get_pipeline_stage(self) -> GraphPipelineStage: 
        """
        Gets the pipeline stage to which this graph belongs

        Returns:
            omni.graph.core.PipelineStage: The type of pipeline stage of this graph (simulation, pre-render, post-render)
        """
    def get_subgraph(self, path: str) -> Graph: 
        """
        Gets the subgraph living at the given path below this graph

        Args:
            path (str): Path to the subgraph to find

        Returns:
            omni.graph.core.Graph | None: Subgraph at the path, or None if not found
        """
    def get_subgraphs(self) -> typing.List[Graph]: 
        """
        Gets the list of subgraphs under this graph

        Returns:
            list[omni.graph.core.Graph]: List of graphs that are subgraphs of this graph
        """
    def get_variables(self) -> typing.List[IVariable]: 
        """
        Returns the list of variables defined on the graph.

        Returns:
            list[omni.graph.core.IVariable]: The current list of variables on the graph.
            
        """
    def inspect(self, inspector: omni.inspect._omni_inspect.IInspector) -> bool: 
        """
        Runs the inspector on the graph

        Args:
            inspector (omni.inspect.Inspector): The inspector to run

        Returns:
            bool: True if the inspector was successfully run on the graph, False if it is not supported
        """
    def is_auto_instanced(self) -> bool: 
        """
        Returns whether this graph is an auto instance or not. An auto instance is a graph that got merged as an instance with all other similar graphs in the stage.

        Returns:
            bool: True if this graph is an auto instance
        """
    def is_compound_graph(self) -> bool: 
        """
        Returns whether this graph is a compound graph. A compound graph is subgraph that controlled by a compound node.

        Returns:
            bool: True if this graph is a compound graph
        """
    def is_disabled(self) -> bool: 
        """
        Checks to see if the graph is disabled

        Returns:
            bool: True if this graph object is disabled.
        """
    def is_valid(self) -> bool: 
        """
        Checks to see if the graph object is valid

        Returns:
            bool: True if this graph object is valid.
        """
    def register_error_status_change_callback(self, callback: object) -> int: 
        """
        Registers a callback to be invoked after graph evaluation for all the nodes whose error status changed
        during the evaluation. The callback receives a list of the nodes whose error status changed.

        Args:
            callback (callable): The callback function

        Returns:
            int: A handle that can be used for deregistration. Note the calling module is responsible for deregistration
            of the callback in all circumstances, including where the extension is hot-reloaded.
        """
    def reload_from_stage(self) -> None: 
        """
        Force the graph to reload by deleting it and re-parsing from the stage.

        This is potentially destructive if you have internal state information in any nodes.
        """
    def reload_settings(self) -> None: 
        """
        Reload the graph settings.
        """
    def remove_variable(self, variable: IVariable) -> bool: 
        """
        Removes the given variable from the graph.

        Args:
            variable (omni.graph.core.IVariable): The variable to remove.

        Returns:
            bool: True if the variable was successfully removed, False otherwise.
        """
    def rename_node(self, path: str, new_path: str) -> bool: 
        """
        Given the path to the node, renames the node at that path.

        Args:
            path (str): The path to the node
            new_path (str): The new path

        Returns:
            bool: True if the node was successfully renamed
        """
    def rename_subgraph(self, path: str, new_path: str) -> bool: 
        """
        Renames the path of a subgraph

        Args:
            path (str): Path to the subgraph being renamed
            new_path (str): New path for the subgraph
        """
    def set_auto_instancing_allowed(self, arg0: bool) -> bool: 
        """
        Allows (or not) this graph to be an auto-instance, ie. to be executed vectorized as an instance amongst all other identical graph

        Args:
            allowed (bool): Whether this graph is allowed to be an auto instance.

        Returns:
            bool: Whether this graph was allowed to be an auto instance before this call.
        """
    def set_disabled(self, disable: bool) -> None: 
        """
        Sets whether this graph object is to be disabled or not.

        Args:
            disable (bool): True if the graph is to be disabled
        """
    def set_prim_view(self, view: IPrimView) -> bool: 
        """
        Apply a view to a graph: a view is a way to dynamically maintain a list of instances for a graph.

        Args:
            view (IPrimViewPtr): The view to apply to that graph

        Returns:
            bool: whether or not the view has been successfully applied to the graph.
            
        """
    def set_usd_notice_handling_enabled(self, enable: bool) -> None: 
        """
        Sets whether this graph object has USD notice handling enabled.

        Args:
            enable (bool): True to enable USD notice handling, False to disable.
        """
    def usd_notice_handling_enabled(self) -> bool: 
        """
        Checks whether this graph has USD notice handling enabled.

        Returns:
            bool: True if USD notice handling is enabled on this graph.
        """
    @property
    def evaluation_mode(self) -> GraphEvaluationMode:
        """
            omni.graph.core.GraphEvaluationMode: The evaluation mode sets how the graph will be evaluated.

            GRAPH_EVALUATION_MODE_AUTOMATIC - Evaluate the graph in Standalone mode when there are no relationships to it,
            otherwise it will be evaluated in Instanced mode.

            GRAPH_EVALUATION_MODE_STANDALONE - Evaluates the graph with the graph Prim as the graph target, and ignore Prims with relationships
            to the graph Prim. Use this mode when constructing self-contained graphs that evaluate independently.

            GRAPH_EVALUATION_MODE_INSTANCED - Evaluates only when the graph there are relationships from OmniGraphAPI interfaces. Each Prim with
            a relationship to the graph Prim will cause an evaluation, with the Graph Target set to path of Prim with the OmniGraphAPI interface.
            Use this mode when the graph represents as an asset or template that can be applied to multiple Prims.
            

        :type: GraphEvaluationMode
        """
    @evaluation_mode.setter
    def evaluation_mode(self, arg1: GraphEvaluationMode) -> None:
        """
        omni.graph.core.GraphEvaluationMode: The evaluation mode sets how the graph will be evaluated.

        GRAPH_EVALUATION_MODE_AUTOMATIC - Evaluate the graph in Standalone mode when there are no relationships to it,
        otherwise it will be evaluated in Instanced mode.

        GRAPH_EVALUATION_MODE_STANDALONE - Evaluates the graph with the graph Prim as the graph target, and ignore Prims with relationships
        to the graph Prim. Use this mode when constructing self-contained graphs that evaluate independently.

        GRAPH_EVALUATION_MODE_INSTANCED - Evaluates only when the graph there are relationships from OmniGraphAPI interfaces. Each Prim with
        a relationship to the graph Prim will cause an evaluation, with the Graph Target set to path of Prim with the OmniGraphAPI interface.
        Use this mode when the graph represents as an asset or template that can be applied to multiple Prims.
        """
    CURRENT_FILE_FORMAT_VERSION: omni.graph.core._omni_graph_core.FileFormatVersion
    pass
class GraphBackingType():
    """
    Location of the data backing the graph

    Members:

      GRAPH_BACKING_TYPE_FLATCACHE_SHARED : Deprecated: Use GRAPH_BACKING_TYPE_FABRIC_SHARED

      GRAPH_BACKING_TYPE_FLATCACHE_WITH_HISTORY : Deprecated: Use GRAPH_BACKING_TYPE_FABRIC_WITH_HISTORY

      GRAPH_BACKING_TYPE_FLATCACHE_WITHOUT_HISTORY : Deprecated: Use GRAPH_BACKING_TYPE_FABRIC_WITHOUT_HISTORY

      GRAPH_BACKING_TYPE_FABRIC_SHARED : Data is a regular Fabric instance

      GRAPH_BACKING_TYPE_FABRIC_WITH_HISTORY : Data is a Fabric instance without any history

      GRAPH_BACKING_TYPE_FABRIC_WITHOUT_HISTORY : Data is a Fabric instance with a ring buffer of history

      GRAPH_BACKING_TYPE_NONE : No data is stored for the graph

      GRAPH_BACKING_TYPE_UNKNOWN : The data backing is not currently known
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    GRAPH_BACKING_TYPE_FABRIC_SHARED: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_SHARED: 0>
    GRAPH_BACKING_TYPE_FABRIC_WITHOUT_HISTORY: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITHOUT_HISTORY: 2>
    GRAPH_BACKING_TYPE_FABRIC_WITH_HISTORY: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITH_HISTORY: 1>
    GRAPH_BACKING_TYPE_FLATCACHE_SHARED: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_SHARED: 0>
    GRAPH_BACKING_TYPE_FLATCACHE_WITHOUT_HISTORY: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITHOUT_HISTORY: 2>
    GRAPH_BACKING_TYPE_FLATCACHE_WITH_HISTORY: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITH_HISTORY: 1>
    GRAPH_BACKING_TYPE_NONE: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_NONE: 4>
    GRAPH_BACKING_TYPE_UNKNOWN: omni.graph.core._omni_graph_core.GraphBackingType # value = <GraphBackingType.GRAPH_BACKING_TYPE_UNKNOWN: 3>
    __members__: dict # value = {'GRAPH_BACKING_TYPE_FLATCACHE_SHARED': <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_SHARED: 0>, 'GRAPH_BACKING_TYPE_FLATCACHE_WITH_HISTORY': <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITH_HISTORY: 1>, 'GRAPH_BACKING_TYPE_FLATCACHE_WITHOUT_HISTORY': <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITHOUT_HISTORY: 2>, 'GRAPH_BACKING_TYPE_FABRIC_SHARED': <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_SHARED: 0>, 'GRAPH_BACKING_TYPE_FABRIC_WITH_HISTORY': <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITH_HISTORY: 1>, 'GRAPH_BACKING_TYPE_FABRIC_WITHOUT_HISTORY': <GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_WITHOUT_HISTORY: 2>, 'GRAPH_BACKING_TYPE_NONE': <GraphBackingType.GRAPH_BACKING_TYPE_NONE: 4>, 'GRAPH_BACKING_TYPE_UNKNOWN': <GraphBackingType.GRAPH_BACKING_TYPE_UNKNOWN: 3>}
    pass
class GraphContext():
    """
    Execution context for a graph
    """
    def __bool__(self) -> bool: ...
    def __eq__(self, arg0: GraphContext) -> bool: ...
    def __hash__(self) -> int: ...
    def get_attribute_as_bool(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> bool: 
        """
        get_attribute_as_bool is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_boolarray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[bool]: 
        """
        get_attribute_as_boolarray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_double(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> float: 
        """
        get_attribute_as_double is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_doublearray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.float64]: 
        """
        get_attribute_as_doublearray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_float(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> float: 
        """
        get_attribute_as_float is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_floatarray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.float32]: 
        """
        get_attribute_as_floatarray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_half(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> float: 
        """
        get_attribute_as_half is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_halfarray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.float32]: 
        """
        get_attribute_as_halfarray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_int(self, arg0: Attribute, arg1: bool, arg2: bool, arg3: int) -> int: 
        """
        get_attribute_as_int is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_int64(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> int: 
        """
        get_attribute_as_int64 is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_int64array(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.int64]: 
        """
        get_attribute_as_int64array is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_intarray(self, arg0: Attribute, arg1: bool, arg2: bool, arg3: int) -> numpy.ndarray[numpy.int32]: 
        """
        get_attribute_as_intarray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_nested_doublearray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.float64]: 
        """
        get_attribute_as_nested_doublearray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_nested_floatarray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.float32]: 
        """
        get_attribute_as_nested_floatarray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_nested_halfarray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.float32]: 
        """
        get_attribute_as_nested_halfarray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_nested_intarray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.int32]: 
        """
        get_attribute_as_nested_intarray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_string(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> str: 
        """
        get_attribute_as_string is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_uchar(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> int: 
        """
        get_attribute_as_uchar is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_uchararray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.uint8]: 
        """
        get_attribute_as_uchararray is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_uint(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> int: 
        """
        get_attribute_as_uint is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_uint64(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> int: 
        """
        get_attribute_as_uint64 is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_uint64array(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.uint64]: 
        """
        get_attribute_as_uint64array is deprecated. Use og.Controller.get() instead.
        """
    def get_attribute_as_uintarray(self, attribute: Attribute, getDefault: bool = False, write: bool = False, writeElemCount: int = 0) -> numpy.ndarray[numpy.uint32]: 
        """
        get_attribute_as_uintarray is deprecated. Use og.Controller.get() instead.
        """
    def get_bundle(self, path: str) -> IBundle2: 
        """
        Get the bundle object as read-write.

        Args:
            path (str): the path to the bundle

        Returns:
            omni.graph.core.IBundle2: The bundle object at the path, None if there isn't one
        """
    def get_elapsed_time(self) -> float: 
        """
        Returns the time between last evaluation of the graph and "now"

        Returns:
            float: the elapsed time
        """
    @staticmethod
    @typing.overload
    def get_elem_count(*args, **kwargs) -> typing.Any: 
        """
        get_elem_count is deprecated. Use og.Controller.get_array_size() instead.

        get_elem_count is deprecated. Use og.Controller.get_array_size() instead.
        """
    @typing.overload
    def get_elem_count(self, arg0: Attribute) -> int: ...
    def get_frame(self) -> float: 
        """
        Returns the global playback time in frames

        Returns:
            float: the global playback time in frames
        """
    def get_graph(self) -> Graph: 
        """
        Gets the graph associated with this graph context

        Returns:
            omni.graph.core.Graph: The graph associated with this graph context.
        """
    def get_graph_target(self, index: int = 18446744073709551614) -> str: 
        """
        Get the Prim path of the graph target.

        The graph target is defined as the parent Prim of the compute graph, except during
        instancing - where OmniGraph executes a graph once for each Prim. In the case
        of instancing, the graph target will change at each execution to be the path of the instance.
        If this is called outside of graph execution, the path of the graph Prim is returned, or an empty
        token if the graph does not have a Prim associated with it.

        Args:
            index (int): The index of instance to fetch. By default, the graph context index is used.

        Returns:
            str: The prim path of the current graph target.
        """
    @typing.overload
    def get_input_bundle(self, path: str) -> IConstBundle2: 
        """
        Get the bundle object as read only.

        Args:
            path (str): the path to the bundle

        Returns:
            omni.graph.core.IBundle2: The bundle object at the path, None if there isn't one



        Get a bundle object that is an input attribute.

        Args:
            node (omni.graph.core.Node): the node on which the bundle can be found
            attribute_name (str): the name of the input attribute
            instance (int): an instance index when getting value on an instantiated graph

        Returns:
            omni.graph.core.IConstBundle2: The bundle object at the path, None if there isn't one
        """
    @typing.overload
    def get_input_bundle(self, node: Node, attribute_name: str, instance: int = 18446744073709551614) -> IConstBundle2: ...
    def get_input_target_bundles(self, node: Node, attribute_name: str, instance: int = 18446744073709551614) -> typing.List[IConstBundle2]: 
        """
        Get all input targets in the relationship with the given name on the specified compute node.

        The targets are returned as bundle objects.

        Args:
            node (omni.graph.core.Node): the node on which the input targets can be found
            attribute_name (str): the name of the relationship attribute
            instance (int): an instance index when getting value on an instantiated graph

        Returns:
            list[omni.graph.core.IConstBundle2]: The list of input targets, as bundle objects.
        """
    def get_is_playing(self) -> bool: 
        """
        Returns the state of global playback

        Returns:
            bool: True if playback has started, False is playback is stopped
        """
    @typing.overload
    def get_output_bundle(self, path: str) -> IBundle2: 
        """
        Get a bundle object that is an output attribute.

        Args:
            path (str): the path to the bundle

        Returns:
            omni.graph.core.IBundle2: The bundle object at the path, None if there isn't one



        Get a bundle object that is an output attribute.

        Args:
            node (omni.graph.core.Node): the node on which the bundle can be found
            attribute_name (str): the name of the output attribute
            instance (int): an instance index when getting value on an instantiated graph

        Returns:
            omni.graph.core.IBundle2: The bundle object at the path, None if there isn't one
        """
    @typing.overload
    def get_output_bundle(self, node: Node, attribute_name: str, instance: int = 18446744073709551614) -> IBundle2: ...
    def get_time(self) -> float: 
        """
        Returns the global playback time

        Returns:
            float: the global playback time in seconds
        """
    def get_time_since_start(self) -> float: 
        """
        Returns the elapsed time since the app started

        Returns:
            float: the number of seconds since the app started in seconds
        """
    def inspect(self, inspector: omni.inspect._omni_inspect.IInspector) -> bool: 
        """
        Runs the inspector on the graph context

        Args:
            inspector (omni.inspect.Inspector): The inspector to run

        Returns:
            bool: True if the inspector was successfully run on the context, False if it is not supported
        """
    def is_valid(self) -> bool: 
        """
        Checks to see if this graph context object is valid

        Returns:
            bool: True if this object is valid
        """
    def set_bool_attribute(self, arg0: bool, arg1: Attribute) -> None: 
        """
        set_bool_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_boolarray_attribute(self, arg0: typing.List[bool], arg1: Attribute) -> None: 
        """
        set_boolarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_double_attribute(self, arg0: float, arg1: Attribute) -> None: 
        """
        set_double_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_double_matrix_attribute(self, arg0: typing.List[float], arg1: Attribute) -> None: 
        """
        set_double_matrix_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_doublearray_attribute(self, arg0: typing.List[float], arg1: Attribute) -> None: 
        """
        set_doublearray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_float_attribute(self, arg0: float, arg1: Attribute) -> None: 
        """
        set_float_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_floatarray_attribute(self, arg0: typing.List[float], arg1: Attribute) -> None: 
        """
        set_floatarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_half_attribute(self, arg0: float, arg1: Attribute) -> None: 
        """
        set_half_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_halfarray_attribute(self, arg0: typing.List[float], arg1: Attribute) -> None: 
        """
        set_halfarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_int64_attribute(self, arg0: int, arg1: Attribute) -> None: 
        """
        set_int64_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_int64array_attribute(self, arg0: typing.List[int], arg1: Attribute) -> None: 
        """
        set_int64array_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_int_attribute(self, arg0: int, arg1: Attribute) -> None: 
        """
        set_int_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_intarray_attribute(self, arg0: typing.List[int], arg1: Attribute) -> None: 
        """
        set_intarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_nested_doublearray_attribute(self, arg0: typing.List[typing.List[float]], arg1: Attribute) -> None: 
        """
        set_nested_doublearray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_nested_floatarray_attribute(self, arg0: typing.List[typing.List[float]], arg1: Attribute) -> None: 
        """
        set_nested_floatarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_nested_halfarray_attribute(self, arg0: typing.List[typing.List[float]], arg1: Attribute) -> None: 
        """
        set_nested_halfarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_nested_intarray_attribute(self, arg0: typing.List[typing.List[int]], arg1: Attribute) -> None: 
        """
        set_nested_intarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_string_attribute(self, arg0: str, arg1: Attribute) -> None: 
        """
        set_string_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_uchar_attribute(self, arg0: int, arg1: Attribute) -> None: 
        """
        set_uchar_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_uchararray_attribute(self, arg0: typing.List[int], arg1: Attribute) -> None: 
        """
        set_uchararray_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_uint64_attribute(self, arg0: int, arg1: Attribute) -> None: 
        """
        set_uint64_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_uint64array_attribute(self, arg0: typing.List[int], arg1: Attribute) -> None: 
        """
        set_uint64array_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_uint_attribute(self, arg0: int, arg1: Attribute) -> None: 
        """
        set_uint_attribute is deprecated. Use og.Controller.set() instead.
        """
    def set_uintarray_attribute(self, arg0: typing.List[int], arg1: Attribute) -> None: 
        """
        set_uintarray_attribute is deprecated. Use og.Controller.set() instead.
        """
    @staticmethod
    def write_bucket_to_backing(*args, **kwargs) -> typing.Any: 
        """
        This method was internal, and is now obsolete: it does not function anymore. In order to write back to USD, you can directly use the USD API.
        """
    pass
class GraphEvaluationMode():
    """
    How the graph evaluation is scheduled

    Members:

      GRAPH_EVALUATION_MODE_AUTOMATIC : Evaluation is scheduled based on graph type

      GRAPH_EVALUATION_MODE_STANDALONE : Evaluation is scheduled as a single graph

      GRAPH_EVALUATION_MODE_INSTANCED : Evaluation is scheduled by instances
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    GRAPH_EVALUATION_MODE_AUTOMATIC: omni.graph.core._omni_graph_core.GraphEvaluationMode # value = <GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC: 0>
    GRAPH_EVALUATION_MODE_INSTANCED: omni.graph.core._omni_graph_core.GraphEvaluationMode # value = <GraphEvaluationMode.GRAPH_EVALUATION_MODE_INSTANCED: 2>
    GRAPH_EVALUATION_MODE_STANDALONE: omni.graph.core._omni_graph_core.GraphEvaluationMode # value = <GraphEvaluationMode.GRAPH_EVALUATION_MODE_STANDALONE: 1>
    __members__: dict # value = {'GRAPH_EVALUATION_MODE_AUTOMATIC': <GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC: 0>, 'GRAPH_EVALUATION_MODE_STANDALONE': <GraphEvaluationMode.GRAPH_EVALUATION_MODE_STANDALONE: 1>, 'GRAPH_EVALUATION_MODE_INSTANCED': <GraphEvaluationMode.GRAPH_EVALUATION_MODE_INSTANCED: 2>}
    pass
class GraphEvent():
    """
            Graph modification event.
            

    Members:

      CREATE_VARIABLE : Variable was created

      REMOVE_VARIABLE : Variable was removed

      VARIABLE_TYPE_CHANGE : Variable type was changed
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CREATE_VARIABLE: omni.graph.core._omni_graph_core.GraphEvent # value = <GraphEvent.CREATE_VARIABLE: 0>
    REMOVE_VARIABLE: omni.graph.core._omni_graph_core.GraphEvent # value = <GraphEvent.REMOVE_VARIABLE: 1>
    VARIABLE_TYPE_CHANGE: omni.graph.core._omni_graph_core.GraphEvent # value = <GraphEvent.VARIABLE_TYPE_CHANGE: 5>
    __members__: dict # value = {'CREATE_VARIABLE': <GraphEvent.CREATE_VARIABLE: 0>, 'REMOVE_VARIABLE': <GraphEvent.REMOVE_VARIABLE: 1>, 'VARIABLE_TYPE_CHANGE': <GraphEvent.VARIABLE_TYPE_CHANGE: 5>}
    pass
class GraphPipelineStage():
    """
    Pipeline stage in which the graph lives

    Members:

      GRAPH_PIPELINE_STAGE_SIMULATION : The regular evaluation stage

      GRAPH_PIPELINE_STAGE_PRERENDER : The stage that evaluates just before rendering

      GRAPH_PIPELINE_STAGE_POSTRENDER : The stage that evaluates just after rendering

      GRAPH_PIPELINE_STAGE_ONDEMAND : The stage evaluating only when requested

      GRAPH_PIPELINE_STAGE_UNKNOWN : The stage is not currently known
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    GRAPH_PIPELINE_STAGE_ONDEMAND: omni.graph.core._omni_graph_core.GraphPipelineStage # value = <GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND: 200>
    GRAPH_PIPELINE_STAGE_POSTRENDER: omni.graph.core._omni_graph_core.GraphPipelineStage # value = <GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER: 30>
    GRAPH_PIPELINE_STAGE_PRERENDER: omni.graph.core._omni_graph_core.GraphPipelineStage # value = <GraphPipelineStage.GRAPH_PIPELINE_STAGE_PRERENDER: 20>
    GRAPH_PIPELINE_STAGE_SIMULATION: omni.graph.core._omni_graph_core.GraphPipelineStage # value = <GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION: 10>
    GRAPH_PIPELINE_STAGE_UNKNOWN: omni.graph.core._omni_graph_core.GraphPipelineStage # value = <GraphPipelineStage.GRAPH_PIPELINE_STAGE_UNKNOWN: 100>
    __members__: dict # value = {'GRAPH_PIPELINE_STAGE_SIMULATION': <GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION: 10>, 'GRAPH_PIPELINE_STAGE_PRERENDER': <GraphPipelineStage.GRAPH_PIPELINE_STAGE_PRERENDER: 20>, 'GRAPH_PIPELINE_STAGE_POSTRENDER': <GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER: 30>, 'GRAPH_PIPELINE_STAGE_ONDEMAND': <GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND: 200>, 'GRAPH_PIPELINE_STAGE_UNKNOWN': <GraphPipelineStage.GRAPH_PIPELINE_STAGE_UNKNOWN: 100>}
    pass
class GraphRegistry():
    """
    Manager of the node types registered to OmniGraph.
    """
    def __init__(self) -> None: ...
    def get_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Get the event stream for the graph registry change notification.

        The events that are raised are specified by GraphRegistryEvent. The payload for the
        added and removed events is the name of the node type being added or removed, and uses
        the key "node_type".

        Returns:
            carb.events.IEventStream: Event stream to monitor for graph registry changes
        """
    def get_node_type_version(self, node_type_name: str) -> int: 
        """
        Finds the version number of the given node type.

        Args:
            node_type_name (str): Name of the node type to check

        Returns:
            int: Version number registered for the node type, None if it is not registered
        """
    def inspect(self, inspector: omni.inspect._omni_inspect.IInspector) -> bool: 
        """
        Runs the inspector on the graph registry

        Args:
            inspector (omni.inspect.Inspector): The inspector to run

        Returns:
            bool: True if the inspector was successfully run on the graph registry, False if it is not supported
        """
    pass
class GraphRegistryEvent():
    """
            Graph Registry modification event.
            

    Members:

      NODE_TYPE_ADDED : Node type was registered

      NODE_TYPE_REMOVED : Node type was deregistered

      NODE_TYPE_NAMESPACE_CHANGED : Namespace of a node type changed

      NODE_TYPE_CATEGORY_CHANGED : Category of a node type changed

      STAGE_PRE_ATTACH : A stage is being attached
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    NODE_TYPE_ADDED: omni.graph.core._omni_graph_core.GraphRegistryEvent # value = <GraphRegistryEvent.NODE_TYPE_ADDED: 0>
    NODE_TYPE_CATEGORY_CHANGED: omni.graph.core._omni_graph_core.GraphRegistryEvent # value = <GraphRegistryEvent.NODE_TYPE_CATEGORY_CHANGED: 3>
    NODE_TYPE_NAMESPACE_CHANGED: omni.graph.core._omni_graph_core.GraphRegistryEvent # value = <GraphRegistryEvent.NODE_TYPE_NAMESPACE_CHANGED: 2>
    NODE_TYPE_REMOVED: omni.graph.core._omni_graph_core.GraphRegistryEvent # value = <GraphRegistryEvent.NODE_TYPE_REMOVED: 1>
    STAGE_PRE_ATTACH: omni.graph.core._omni_graph_core.GraphRegistryEvent # value = <GraphRegistryEvent.STAGE_PRE_ATTACH: 4>
    __members__: dict # value = {'NODE_TYPE_ADDED': <GraphRegistryEvent.NODE_TYPE_ADDED: 0>, 'NODE_TYPE_REMOVED': <GraphRegistryEvent.NODE_TYPE_REMOVED: 1>, 'NODE_TYPE_NAMESPACE_CHANGED': <GraphRegistryEvent.NODE_TYPE_NAMESPACE_CHANGED: 2>, 'NODE_TYPE_CATEGORY_CHANGED': <GraphRegistryEvent.NODE_TYPE_CATEGORY_CHANGED: 3>, 'STAGE_PRE_ATTACH': <GraphRegistryEvent.STAGE_PRE_ATTACH: 4>}
    pass
class IBundle2(_IBundle2, IConstBundle2, _IConstBundle2, omni.core._core.IObject):
    """
    Provide read write access to recursive bundles.
    """
    def __bool__(self) -> bool: ...
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    def add_attribute(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use create_attribute() instead.
        """
    @staticmethod
    def add_attributes(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use create_attributes() instead.
        """
    def clear(self) -> None: 
        """
        DEPRECATED - use clear_contents() instead
        """
    def clear_contents(self, bundle_metadata: bool = True, attributes: bool = True, child_bundles: bool = True) -> int: 
        """
        Removes all attributes and child bundles from this bundle, but keeps the bundle itself.

        Args:
            bundle_metadata (bool): Clears bundle metadata in this bundle.
            attributes (bool): Clears attributes in this bundle.
            child_bundles (bool): Clears child bundles in this bundle.

        Returns:
            omni.core.Result: Success if successfully cleared.
        """
    @staticmethod
    def copy_attribute(*args, **kwargs) -> typing.Any: 
        """
        Create new attribute by copying existing one, including its data.

        Created attribute is owned by this bundle.

        Args:
            attribute (omni.graph.core.AttributeData): Attribute whose data type is to be copied.
            overwrite (bool): Overwrite existing attribute in this bundle.

        Returns:
            omni.graph.core.AttributeData: Copied attribute.



        Create new attribute by copying existing one, including its data.

        Created attribute is owned by this bundle.

        Args:
            name (str): The new name for copied attribute.
            attribute (omni.graph.core.AttributeData): Attribute whose data type is to be copied.
            overwrite (bool): Overwrite existing attribute in this bundle.

        Returns:
            omni.graph.core.AttributeData: Copied attribute.
        """
    @staticmethod
    def copy_attributes(*args, **kwargs) -> typing.Any: 
        """
        Create new attributes by copying existing ones, including their data.

        Names of new attributes are taken from source attributes.
        Created attributes are owned by this bundle.

        Args:
            attributes (list[omni.graph.core.AttributeData]): Attributes whose data type is to be copied.
            overwrite (bool): Overwrite existing attributes in this bundle.

        Returns:
            list[omni.graph.core.AttributeData]: A list of copied attributes.\\



        Create new attributes by copying existing ones, including their data, with possibility of giving them new names.

        Created attributes are owned by this bundle.

        Args:
            names (list[str]): Names for the new attributes.
            attributes (list[omni.graph.core.AttributeData]): Attributes whose data type is to be copied.
            overwrite (bool): Overwrite existing attributes in this bundle.

        Returns:
            list[omni.graph.core.AttributeData]: A list of copied attributes.
        """
    def copy_bundle(self, source_bundle: IConstBundle2, overwrite: bool = True) -> None: 
        """
        Copy bundle data and metadata from the source bundle to this bundle.

        Args:
            source_bundle (omni.graph.core.IConstBundle2): Bundle whose data is to be copied.
            overwrite (bool): Overwrite existing content of the bundle.
        """
    @typing.overload
    def copy_child_bundle(self, bundle: IConstBundle2, name: typing.Optional[str] = None) -> IBundle2: 
        """
        Create new child bundle by copying existing one, with possibility of giving child a new name.

        Created bundle is owned by this bundle.

        Args:
            bundle (omni.graph.core.IConstBundle2): Bundle whose data is to be copied.
            name (str): Name of new child.

        Returns:
            omni.graph.core.IBundle2: Newly copied bundle.



        Create new child bundle by copying existing one, with possibility of giving child a new name.

        Created bundle is owned by this bundle.

        Args:
            name (str): Name of new child.
            bundle (omni.graph.core.IConstBundle2): Bundle whose data is to be copied.

        Returns:
            omni.graph.core.IBundle2: Newly copied bundle.
        """
    @typing.overload
    def copy_child_bundle(self, name: str, bundle: IConstBundle2) -> IBundle2: ...
    @typing.overload
    def copy_child_bundles(self, bundles: typing.List[IConstBundle2], names: typing.Optional[typing.List[str]] = None) -> typing.List[IBundle2]: 
        """
        Create new child bundles by copying existing ones, with possibility of giving children new names.

        Created bundles are owned by this bundle.

        Args:
            bundles (list[omni.graph.core.IConstBundle2]): Bundles whose data is to be copied.
            names (list[str]): Names of new children.

        Returns:
            list[omni.graph.core.IBundle2]: Newly copied bundles.



        Create new child bundles by copying existing ones, with possibility of giving children new names.

        Created bundles are owned by this bundle.

        Args:
            names (list[str]): Names of new children.
            bundles (list[omni.graph.core.IConstBundle2]): Bundles whose data is to be copied.

        Returns:
            list[omni.graph.core.IBundle2]: Newly copied bundles.
        """
    @typing.overload
    def copy_child_bundles(self, names: typing.List[str], bundles: typing.List[IConstBundle2]) -> typing.List[IBundle2]: ...
    @staticmethod
    def create_attribute(*args, **kwargs) -> typing.Any: 
        """
        Creates attribute based on provided name and type.

        Created attribute is owned by this bundle.

        Args:
            name (str): Name of the attribute.
            type (omni.graph.core.Type): Type of the attribute.
            element_count (int): Number of elements in the array.

        Returns:
            omni.graph.core.AttributeData: Newly created attribute.
        """
    @staticmethod
    def create_attribute_like(*args, **kwargs) -> typing.Any: 
        """
        Use input attribute as pattern to create attribute in this bundle.

        The name and type are taken from pattern attribute, data is not copied.
        Created attribute is owned by this bundle.

        Args:
            pattern_attribute (omni.graph.core.AttributeData): Attribute whose name and type is to be used to create new attribute.

        Returns:
            omni.graph.core.AttributeData: Newly created attribute.
        """
    @staticmethod
    def create_attribute_metadata(*args, **kwargs) -> typing.Any: 
        """
        Create attribute metadata fields.

        Args:
            attribute (str): Name of the attribute.
            field_names (list[str]): Names of new metadata field.
            field_types (list[omni.graph.core.Type]): Types of new metadata field.
            element_count (int): Number of elements in the arrray.

        Returns:
            list[omni.graph.core.AttributeData]: Newly created metadata fields.



        Create attribute metadata field.

        Args:
            attribute (str): Name of the attribute.
            field_name (str): Name of new metadata field.
            field_type (omni.graph.core.Type): Type of new metadata field.

        Returns:
            omni.graph.core.AttributeData: Newly created metadata field.
        """
    @staticmethod
    def create_attributes(*args, **kwargs) -> typing.Any: 
        """
        Creates attributes based on provided names and types.

        Created attributes are owned by this bundle.

        Args:
            names (list[str]): Names of the attributes.
            types (list[omni.graph.core.Type]): Types of the attributes.

        Returns:
            list[omni.graph.core.AttributeData]: A list of created attributes.
        """
    @staticmethod
    def create_attributes_like(*args, **kwargs) -> typing.Any: 
        """
        Use input attributes as pattern to create attributes in this bundle.

        Names and types for new attributes are taken from pattern attributes, data is not copied.
        Created attributes are owned by this bundle.

        Args:
            pattern_attributes (list[omni.graph.core.AttributeData]): Attributes whose name and type is to be used to create new attributes.

        Returns:
            list[omni.graph.core.AttributeData]: A list of newly created attributes.
        """
    @staticmethod
    def create_bundle_metadata(*args, **kwargs) -> typing.Any: 
        """
        Creates bundle metadata fields based on provided names and types.

        Created fields are owned by this bundle.

        Args:
            field_names (list[str]): Names of the fields.
            field_types (list[omni.graph.core.Type]): Types of the fields.
            element_count (int): Number of elements in the arrray.

        Returns:
            list[omni.graph.core.AttributeData]: A list of created fields.



        Creates bundle metadata field based on provided name and type.

        Created field are owned by this bundle.

        Args:
            field_name (str): Name of the field.
            field_type (omni.graph.core.Type): Type of the field.

        Returns:
            omni.graph.core.AttributeData: Created field.
        """
    def create_child_bundle(self, path: str) -> IBundle2: 
        """
        Creates immediate child bundle under specified path in this bundle.

        Created bundle is owned by this bundle.
        This method does not work recursively. Only immediate child can be created.

        Args:
            path (str): New child path in this bundle.

        Returns:
            omni.graph.core.IBundle2: Created child bundle.
        """
    def create_child_bundles(self, paths: typing.List[str]) -> typing.List[IBundle2]: 
        """
        Creates immediate child bundles under specified paths in this bundle.

        Created bundles are owned by this bundle.
        This method does not work recursively. Only immediate children can be created.

        Args:
            paths (list[str]): New children paths in this bundle.

        Returns:
            list[omni.graph.core.IBundle2]: A list of created child bundles.
        """
    @staticmethod
    def get_attribute_by_name(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use get_attribute_by_name(name) instead


                    Searches for attribute in this bundle by using attribute name.

                    Args:
                        name (str): Attribute name to search for.

                    Returns:
                        omni.graph.core.AttributeData: An attribute. If attribute is not found then invalid attribute is returned.
                    
        """
    def get_attribute_data(self, write: bool = False) -> list: 
        """
        DEPRECATED - use get_attributes() instead
        """
    def get_attribute_data_count(self) -> int: 
        """
        DEPRECATED - use get_attribute_count() instead
        """
    @staticmethod
    def get_attribute_metadata_by_name(*args, **kwargs) -> typing.Any: 
        """
        Search for metadata fields for the attribute by using field names.

        Args:
            attribute (str): Name of the attribute.
            field_names (list[str]): Attribute metadata fields to be searched for.

        Returns:
            list[omni.graph.core.AttributeData]: Array of metadata fields in the attribute.



        Search for metadata field for the attribute by using field name.

        Args:
            attribute (str): Name of the attribute.
            field_name (str): Attribute metadata field to be searched for.

        Returns:
            omni.graph.core.AttributeData: Metadata fields in the attribute.
        """
    def get_attribute_names_and_types(self) -> tuple: 
        """
        DEPRECATED - use get_attribute_names() or get_attribute_types() instead
        """
    @staticmethod
    def get_attributes(*args, **kwargs) -> typing.Any: 
        """
        Searches for attributes in this bundle by using attribute names.

        Args:
            names (list[str]): Attribute names to search for.

        Returns:
            list[omni.graph.core.AttributeData]: A list of found attributes.
        """
    @staticmethod
    def get_attributes_by_name(*args, **kwargs) -> typing.Any: 
        """
        Searches for attributes in this bundle by using attribute names.

        Args:
            names (list[str]): Attribute names to search for.

        Returns:
            list[omni.graph.core.AttributeData]: A list of found attributes.
        """
    @staticmethod
    def get_bundle_metadata_by_name(*args, **kwargs) -> typing.Any: 
        """
        Search for field handles in this bundle by using field names.

        Args:
            field_names (list[str]): Bundle metadata fields to be searched for.

        Returns:
            list[omni.graph.core.AttributeData]: Metadata fields in this bundle.



        Search for field handle in this bundle by using field name.

        Args:
            field_name (str): Bundle metadata fields to be searched for.

        Returns:
            omni.graph.core.AttributeData: Metadata field in this bundle.
        """
    def get_child_bundle(self, index: int) -> IBundle2: 
        """
        Get the child bundle by index.

        Args:
            index (int): Child bundle index in range [0, child_bundle_count).

        Returns:
            omni.graph.core.IBundle2: Child bundle under the index. If bundle index is out of range, then invalid bundle is returned.
        """
    def get_child_bundle_by_name(self, name: str) -> IBundle2: 
        """
        Lookup for child under specified name.

        Args:
            path (str): Name to child bundle in this bundle.

        Returns:
            omni.graph.core.IBundle2: Child bundle in this bundle. If child does not exist under the path, then invalid bundle is returned.
        """
    def get_child_bundles(self) -> typing.List[IBundle2]: 
        """
        Get all child bundle handles in this bundle.

        Returns:
            list[omni.graph.core.IBundle2]: A list of all child bundles in this bundle.
        """
    def get_child_bundles_by_name(self, names: typing.List[str]) -> typing.List[IBundle2]: 
        """
        Lookup for children under specified names.

        Args:
            names (list[str]): Names of child bundles in this bundle.

        Returns:
            list[omni.graph.core.IBundle2]: A list of found child bundles in this bundle.
        """
    def get_metadata_storage(self) -> IBundle2: 
        """
        DEPRECATED - DO NOT USE
        """
    def get_parent_bundle(self) -> IBundle2: 
        """
        Get the parent of this bundle

        Returns:
            omni.graph.core.IBundle2: The parent of this bundle, or invalid bundle if there is no parent.
        """
    def get_prim_path(self) -> str: 
        """
        DEPRECATED - use get_path() instead
        """
    @staticmethod
    def insert_attribute(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use copy_attribute() instead
        """
    def insert_bundle(self, bundle_to_copy: IConstBundle2) -> None: 
        """
        DEPRECATED - use copy_bundle() instead.
        """
    def is_read_only(self) -> bool: 
        """
        Returns if this interface is read-only.
        """
    def is_valid(self) -> bool: 
        """
        DEPRECATED - use bool cast instead
        """
    @staticmethod
    def link_attribute(*args, **kwargs) -> typing.Any: 
        """
        Adds an attribute to this bundle as link with names taken from target attribute.

        Added attribute is a link to other attribute that is part of another bundle.
        The link is owned by this bundle, but target of the link is not.
        Removing link from this bundle does not destroy the data link points to.

        Args:
            target_attribute (omni.graph.core.AttributeData): Attribute whose data is to be added.

        Returns:
            omni.graph.core.AttributeData: Attribute that is a link.



        Adds an attribute to this bundle as link with custom name.

        Added attribute is a link to other attribute that is part of another bundle.
        The link is owned by this bundle, but target of the link is not.
        Removing link from this bundle does not destroy the data link points to.

        Args:
            link_name (str): Name for new link.
            target_attribute (omni.graph.core.AttributeData): Attribute whose data is to be added.

        Returns:
            omni.graph.core.AttributeData: Attribute that is a link.
        """
    @staticmethod
    def link_attributes(*args, **kwargs) -> typing.Any: 
        """
        Adds a set of attributes to this bundle as links with names taken from target attributes.

        Added attributes are links to other attributes that are part of another bundle.
        The links are owned by this bundle, but targets of the links are not.
        Removing links from this bundle does not destroy the data links point to.

        Args:
            target_attributes (list[omni.graph.core.AttributeData]): Attributes whose data is to be added.

        Returns:
            list[omni.graph.core.AttributeData]: A list of attributes that are links.



        Adds a set of attributes to this bundle as links with custom names.

        Added attributes are links to other attributes that are part of another bundle.
        The links are owned by this bundle, but targets of the links are not.
        Removing links from this bundle does not destroy the data links point to.

        Args:
            link_names (list[str]):
            target_attributes (list[omni.graph.core.AttributeData]): Attributes whose data is to be added.

        Returns:
            list[omni.graph.core.AttributeData]: A list of attributes that are links.
        """
    @typing.overload
    def link_child_bundle(self, name: str, bundle: IConstBundle2) -> IBundle2: 
        """
        Link a bundle as child in current bundle, under given name.

        Args:
            name (str): The name under which the child bundle should be linked
            bundle (omni.graph.core.IConstBundle2): The bundle to link

        Returns:
            omni.graph.core.IBundle2: The linked bundle.



        Link a bundle as child in current bundle.

        Args:
            bundle (omni.graph.core.IConstBundle2): The bundle to link

        Returns:
            omni.graph.core.IBundle2: The linked bundle.
        """
    @typing.overload
    def link_child_bundle(self, bundle: IConstBundle2) -> IBundle2: ...
    @typing.overload
    def link_child_bundles(self, names: typing.List[str], bundles: typing.List[IConstBundle2]) -> typing.List[IBundle2]: 
        """
        Link a set of bundles as child in current bundle, under given names.

        Args:
            names (list[str]): The names under which the child bundles should be linked
            bundles (list[omni.graph.core.IConstBundle2]): The bundles to link

        Returns:
            list[omni.graph.core.IBundle2]: The list of created bundles.



        Link a set of bundles as child in current bundle.

        Args:
            bundles (list[omni.graph.core.IConstBundle2]): The bundles to link

        Returns:
            list[omni.graph.core.IBundle2]: The list of created bundles.
        """
    @typing.overload
    def link_child_bundles(self, bundles: typing.List[IConstBundle2]) -> typing.List[IBundle2]: ...
    def remove_all_attributes(self) -> int: 
        """
        Remove all attributes from this bundle.

        Returns:
            int: Number of attributes successfully removed.
        """
    def remove_all_child_bundles(self) -> int: 
        """
        Remove all child bundles from this bundle.

        Only empty bundles can be removed.

        Returns:
            int: Number of child bundles successfully removed.
        """
    @typing.overload
    def remove_attribute(self, name: str) -> None: 
        """
        DEPRECATED - use remove_attribute_by_name() instead.


                    Looks up the attribute and if it is part of this bundle then remove it.

                    Attribute handle that is not part of this bundle is ignored.

                    Args:
                        attribute (omni.graph.core.AttributeData): Attribute whose data is to be removed.

                    Returns:
                        omni.core.Result: Success if successfully removed.
                    
        """
    @staticmethod
    @typing.overload
    def remove_attribute(*args, **kwargs) -> typing.Any: ...
    @typing.overload
    def remove_attribute_metadata(self, attribute: str, field_names: typing.List[str]) -> int: 
        """
        Remove attribute metadata fields.

        Args:
            attribute (str): Name of the attribute.
            field_names (list[str]): Names of the fields to be removed.
        Returns:
            int: Number of fields successfully removed.



        Remove attribute metadata field.

        Args:
            attribute (str): Name of the attribute.
            field_name (str): Name of the field to be removed.

        Returns:
            omni.core.Result: Success if successfully removed.
        """
    @typing.overload
    def remove_attribute_metadata(self, attribute: str, field_name: str) -> int: ...
    @typing.overload
    def remove_attributes(self, names: typing.List[str]) -> None: 
        """
        DEPRECATED - use remove_attributes_by_name() instead.


                    Looks up the attributes and if they are part of this bundle then remove them.

                    Attribute handles that are not part of this bundle are ignored.

                    Args:
                        attributes (list[omni.graph.core.AttributeData]): Attributes whose data is to be removed.

                    Returns:
                        int: number of removed attributes
                    
        """
    @staticmethod
    @typing.overload
    def remove_attributes(*args, **kwargs) -> typing.Any: ...
    def remove_attributes_by_name(self, names: typing.List[str]) -> int: 
        """
        Looks up the attributes by names and remove their data and metadata.

        Args:
            names (list[str]): Names of the attributes whose data is to be removed.

        Returns:
            omni.core.Result: Success if successfully removed.
        """
    @typing.overload
    def remove_bundle_metadata(self, field_names: typing.List[str]) -> int: 
        """
        Looks up bundle metadata fields and if they are part of this bundle metadata then remove them.

        Fields that are not part of this bundle are ignored.

        Args:
            field_names (list[str]): Names of the fields whose data is to be removed.

        Returns:
            int: Number of fields successfully removed.



        Looks up bundle metadata field and if it is part of this bundle metadata then remove it.

        Field that is not part of this bundle is ignored.

        Args:
            field_name (str): Name of the field whose data is to be removed.

        Returns:
            omni.core.Result: Success if successfully removed.
        """
    @typing.overload
    def remove_bundle_metadata(self, field_name: str) -> int: ...
    def remove_child_bundle(self, bundle: IConstBundle2) -> int: 
        """
        Looks up the bundle and if it is child of the bundle then remove it.

        Bundle handle that is not child of this bundle is ignored.
        Only empty bundle can be removed.

        Args:
            bundle (omni.graph.core.IConstBundle2): bundle to be removed.

        Returns:
            omni.core.Result: Success if successfully removed.
        """
    def remove_child_bundles(self, bundles: typing.List[IConstBundle2]) -> int: 
        """
        Looks up the bundles and if they are children of the bundle then remove them.

        Bundle handles that are not children of this bundle are ignored.
        Only empty bundles can be removed.

        Args:
            bundles (list[omni.graph.core.IConstBundle2]): Bundles to be removed.

        Returns:
            int: Number of child bundles successfully removed.
        """
    def remove_child_bundles_by_name(self, names: typing.List[str]) -> int: 
        """
        Looks up child bundles by name and remove their data and metadata.

        Args:
            names (list[str]): Names of the child bundles to be removed.

        Returns:
            omni.core.Result: Success if successfully removed.
        """
    pass
class IBundleChanges(_IBundleChanges, omni.core._core.IObject):
    """
    Interface for monitoring and handling changes in bundles and attributes.

    The IBundleChanges_abi is an interface that provides methods for checking whether bundles and attributes
    have been modified, and cleaning them if they have been modified. This is particularly useful in scenarios
    where it's crucial to track changes and maintain the state of bundles and attributes.

    This interface provides several methods for checking and cleaning modifications, each catering to different
    use cases such as handling single bundles, multiple bundles, attributes, or specific attributes of a single bundle.

    The methods of this interface return a BundleChangeType enumeration that indicates whether the checked entity
    (bundle or attribute) has been modified.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    @typing.overload
    def activate_change_tracking(*args, **kwargs) -> typing.Any: 
        """
        @brief Activate tracking for specific bundle on its attributes and children.
        @param handle to the specific bundles to enable change tracking.
        @return An omni::core::Result indicating the success of the operation.


                Activates the change tracking system for a bundle.

                This method controls the change tracking system of a bundle. It's only applicable
                for read-write bundles.

                Args:
                    bundle: A bundle to activate change tracking system for.
                
        """
    @typing.overload
    def activate_change_tracking(self, bundle: IBundle2) -> None: ...
    def clear_changes(self) -> int: 
        """
        Clears all recorded changes.

        This method is used to clear or reset all the recorded changes of the bundles and attributes.
        It can be used when the changes have been processed and need to be discarded.

        An omni::core::Result indicating the success of the operation.
        """
    @staticmethod
    def create(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    @typing.overload
    def deactivate_change_tracking(*args, **kwargs) -> typing.Any: 
        """
        @brief Deactivate tracking for specific bundle on its attributes and children.
        @param handle to the specific bundles to enable change tracking.
        @return An omni::core::Result indicating the success of the operation.


                Deactivates the change tracking system for a bundle.

                This method controls the change tracking system of a bundle. It's only applicable
                for read-write bundles.

                Args:
                    bundle: A bundle to deactivate change tracking system for.
                
        """
    @typing.overload
    def deactivate_change_tracking(self, bundle: IBundle2) -> None: ...
    @typing.overload
    def get_change(self, bundle: IConstBundle2) -> BundleChangeType: 
        """
        Retrieves the change status of a list of bundles.

        This method is used to check if any of the provided bundles or their contents have been modified.

        Args:
            bundles: A list of the bundles to check for modifications.

        Returns:
            list[omni.graph.core.BundleChangeType]: A list filled with BundleChangeType values for each bundle.



        Retrieves the change status of a specific attribute.

        This method is used to check if a specific attribute has been modified.

        Args:
            attribute: The specific attribute to check for modifications.

        Returns:
            omni.graph.core.BundleChangeType: A BundleChangeType value indicating the type of change (if any) that has occurred to the attribute.
        """
    @staticmethod
    @typing.overload
    def get_change(*args, **kwargs) -> typing.Any: ...
    @typing.overload
    def get_changes(self, bundles: typing.List[IConstBundle2]) -> typing.List[BundleChangeType]: 
        """
        Retrieves the change status of a list of bundles.

        This method is used to check if any of the bundles in the provided list or their contents have been modified.

        Args:
            bundles: A list of the bundles to check for modifications.

        Returns:
            list[omni.graph.core.BundleChangeType]: A list filled with BundleChangeType values for each bundle.



        Retrieves the change status of a list of attributes.

        This method is used to check if any of the attributes in the provided list have been modified.

        Args:
            attributes: A list of attributes to check for modifications.

        Returns:
            list[omni.graph.core.BundleChangeType]: A list filled with BundleChangeType values for each attribute.



        Retrieves the change status for a list of bundles and attributes.

        This method is used to check if any of the bundles or attributes in the provided list have been modified.
        If an entry in the list is neither a bundle nor an attribute, its change status will be marked as None.

        Args:
            entries: A list of bundles and attributes to check for modifications.

        Returns:
            list[omni.graph.core.BundleChangeType]: A list filled with BundleChangeType values for each entry in the provided list.
        """
    @staticmethod
    @typing.overload
    def get_changes(*args, **kwargs) -> typing.Any: ...
    @typing.overload
    def get_changes(self, entries: typing.Sequence) -> typing.List[BundleChangeType]: ...
    pass
class IBundleFactory2(_IBundleFactory2, IBundleFactory, _IBundleFactory, omni.core._core.IObject):
    """
    IBundleFactory version 2.

    The version 2 allows to retrieve instances of IBundle instances from paths.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    def get_bundle_from_path(*args, **kwargs) -> typing.Any: 
        """
        Get read write IBundle interface from path.

        Args:
            context (omni.graph.core.GraphContext): The context where bundles belong to.
            path (str):  Location of the bundle.

        Returns:
            omni.graph.core.IBundle2: Bundle instance.
        """
    @staticmethod
    def get_const_bundle_from_path(*args, **kwargs) -> typing.Any: 
        """
        Get read only IBundle interface from path.

         Args:
             context (omni.graph.core.GraphContext): The context where bundles belong to.
             path (str): Location of the bundle.

         Returns:
             omni.graph.core.IConstBundle2: Bundle instance.
         
        """
    pass
class IBundleFactory(_IBundleFactory, omni.core._core.IObject):
    """
    Interface to create new bundles
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    def create(*args, **kwargs) -> typing.Any: 
        """
        Creates an interface object for bundle factories

        Returns:
            omni.graph.core.IBundleFactory2: Created instance of bundle factory.
        """
    @staticmethod
    def create_bundle(*args, **kwargs) -> typing.Any: 
        """
        Create bundle at given path.

        Args:
            context (omni.graph.core.GraphContext): The context where bundles are created.
            path (str): Location for new bundle.

        Returns:
            omni.graph.core.IBundle2: Bundle instance.
        """
    @staticmethod
    def create_bundles(*args, **kwargs) -> typing.Any: 
        """
        Create bundles at given paths.

        Args:
            context (omni.graph.core.GraphContext): The context where bundles are created.
            paths (list[str]): Locations for new bundles.

        Returns:
            list[omni.graph.core.IBundle2]: A list of bundle instances.
        """
    @staticmethod
    def get_bundle(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - no conversion is required

        DEPRECATED - no conversion is required
        """
    @staticmethod
    def get_bundles(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - no conversion is required

        DEPRECATED - no conversion is required
        """
    pass
class IConstBundle2(_IConstBundle2, omni.core._core.IObject):
    """
    Provide read only access to recursive bundles.
    """
    @typing.overload
    def __bool__(self) -> bool: 
        """
        Returns:
            bool: True if this bundle is valid, False otherwise.
        """
    @typing.overload
    def __bool__(self) -> bool: ...
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    def add_attribute(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use create_attribute() instead.
        """
    @staticmethod
    def add_attributes(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use create_attributes() instead.
        """
    def clear(self) -> None: 
        """
        DEPRECATED - use clear_contents() instead
        """
    @staticmethod
    def get_attribute_by_name(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use get_attribute_by_name(name) instead


                    Searches for attribute in this bundle by using attribute name.

                    Args:
                        name (str): Attribute name to search for.

                    Returns:
                        omni.graph.core.AttributeData: An attribute. If attribute is not found then invalid attribute is returned.
                    
        """
    def get_attribute_count(self) -> int: 
        """
        Get the number of attributes in this bundle

        Returns:
            int: Number of attributes in this bundle.
        """
    def get_attribute_data(self, write: bool = False) -> list: 
        """
        DEPRECATED - use get_attributes() instead
        """
    def get_attribute_data_count(self) -> int: 
        """
        DEPRECATED - use get_attribute_count() instead
        """
    @staticmethod
    def get_attribute_metadata_by_name(*args, **kwargs) -> typing.Any: 
        """
        Search for metadata fields for the attribute by using field names.

        Args:
            attribute (str): Name of the attribute.
            field_names (list[str]): Attribute metadata fields to be searched for.

        Returns:
            list[omni.graph.core.AttributeData]: Array of metadata fields in the attribute.



        Search for metadata field for the attribute by using field name.

        Args:
            attribute (str): Name of the attribute.
            field_name (str): Attribute metadata field to be searched for.

        Returns:
            omni.graph.core.AttributeData: Metadata fields in the attribute.
        """
    def get_attribute_metadata_count(self, attribute: str) -> int: 
        """
        Gets the number of metadata fields in an attribute within the bundle

        Args:
            attribute (str): Name of the attribute to count metadata for.

        Returns:
            int: Number of metadata fields in the attribute.
        """
    def get_attribute_metadata_names(self, attribute: str) -> typing.List[str]: 
        """
        Get names of all metadata fields in the attribute.

        Args:
            attribute (str): Name of the attribute.

        Returns:
            list[str]: Array of names in the attribute.
        """
    @staticmethod
    def get_attribute_metadata_types(*args, **kwargs) -> typing.Any: 
        """
        Get types of all metadata fields in the attribute.

        Args:
            attribute (string): Name of the attribute.

        Returns:
            list[omni.graph.core.Type]: Array of types in the attribute.
        """
    def get_attribute_names(self) -> typing.List[str]: 
        """
        Get the names of all attributes in this bundle.

        Returns:
            list[str]: A list of the names.
        """
    def get_attribute_names_and_types(self) -> tuple: 
        """
        DEPRECATED - use get_attribute_names() or get_attribute_types() instead
        """
    @staticmethod
    def get_attribute_types(*args, **kwargs) -> typing.Any: 
        """
        Get the types of all attributes in this bundle.

        Returns:
            list[omni.graph.core.Type]: A list of the types.
        """
    @staticmethod
    def get_attributes(*args, **kwargs) -> typing.Any: 
        """
        Get all attributes in this bundle.

        Returns:
            list[omni.graph.core.AttributeData]: A list of all attributes in this bundle.
        """
    @staticmethod
    def get_attributes_by_name(*args, **kwargs) -> typing.Any: 
        """
        Searches for attributes in this bundle by using attribute names.

        Args:
            names (list[str]): Attribute names to search for.

        Returns:
            list[omni.graph.core.AttributeData]: A list of found attributes.
        """
    @staticmethod
    def get_bundle_metadata_by_name(*args, **kwargs) -> typing.Any: 
        """
        Search for field handles in this bundle by using field names.

        Args:
            field_names (list[str]): Bundle metadata fields to be searched for.

        Returns:
            list[omni.graph.core.AttributeData]: Metadata fields in this bundle.



        Search for field handle in this bundle by using field name.

        Args:
            field_name (str): Bundle metadata fields to be searched for.

        Returns:
            omni.graph.core.AttributeData: Metadata field in this bundle.
        """
    def get_bundle_metadata_count(self) -> int: 
        """
        Get the number of metadata entries

        Returns:
            int: Number of metadata fields in this bundle.
        """
    def get_bundle_metadata_names(self) -> typing.List[str]: 
        """
        Get the names of all metadata fields in this bundle.

        Returns:
            list[str]: Array of names in this bundle.
        """
    @staticmethod
    def get_bundle_metadata_types(*args, **kwargs) -> typing.Any: 
        """
        Get the types of all metadata fields in this bundle.

        Returns:
            list[omni.graph.core.Type]: Array of types in this bundle.
        """
    def get_child_bundle(self, index: int) -> IConstBundle2: 
        """
        Get the child bundle by index.

        Args:
            index (int): Child bundle index in range [0, child_bundle_count).

        Returns:
            omni.graph.core.IConstBundle2: Child bundle under the index. If bundle index is out of range, then invalid bundle is returned.
        """
    def get_child_bundle_by_name(self, path: str) -> IConstBundle2: 
        """
        Lookup for child under specified path.

        Args:
            path (str): Path to child bundle in this bundle.

        Returns:
            omni.graph.core.IConstBundle2: Child bundle in this bundle. If child does not exist under the path, then invalid bundle is returned.
        """
    def get_child_bundle_count(self) -> int: 
        """
        Get the number of child bundles

        Returns:
            int: Number of child bundles in this bundle.
        """
    def get_child_bundles(self) -> typing.List[IConstBundle2]: 
        """
        Get all child bundle handles in this bundle.

        Returns:
            list[omni.graph.core.IConstBundle2]: A list of all child bundles in this bundle.
        """
    def get_child_bundles_by_name(self, names: typing.List[str]) -> typing.List[IConstBundle2]: 
        """
        Lookup for children under specified names.

        Args:
            names (list[str]): Names to child bundles in this bundle.

        Returns:
            list[omni.graph.core.IConstBundle2]: A list of found child bundles in this bundle.
        """
    @staticmethod
    def get_context(*args, **kwargs) -> typing.Any: 
        """
        Get the context used by this bundle

        Returns:
            omni.graph.core.GraphContext: The context of this bundle.
        """
    def get_metadata_storage(self) -> IConstBundle2: 
        """
        Get access to metadata storage that contains all metadata information

        Returns:
            list[omni.graph.core.IBundle2]: List of bundles with the metadata information
        """
    def get_name(self) -> str: 
        """
        Get the name of the bundle

        Returns:
            str: The name of this bundle.
        """
    def get_parent_bundle(self) -> IConstBundle2: 
        """
        Get the parent bundle

        Returns:
            omni.graph.core.IConstBundle2: The parent of this bundle, or invalid bundle if there is no parent.
        """
    def get_path(self) -> str: 
        """
        Get the path to this bundle

        Returns:
            str: The path to this bundle.
        """
    def get_prim_path(self) -> str: 
        """
        DEPRECATED - use get_path() instead
        """
    @staticmethod
    def insert_attribute(*args, **kwargs) -> typing.Any: 
        """
        DEPRECATED - use copy_attribute() instead
        """
    def insert_bundle(self, bundle_to_copy: IConstBundle2) -> None: 
        """
        DEPRECATED - use copy_bundle() instead.
        """
    def is_read_only(self) -> bool: 
        """
        Returns if this interface is read-only.
        """
    def is_valid(self) -> bool: 
        """
        DEPRECATED - use bool cast instead
        """
    def remove_attribute(self, name: str) -> None: 
        """
        DEPRECATED - use remove_attribute_by_name() instead.
        """
    def remove_attributes(self, names: typing.List[str]) -> None: 
        """
        DEPRECATED - use remove_attributes_by_name() instead.
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    pass
class INodeCategories(_INodeCategories, omni.core._core.IObject):
    """
    Interface to the list of categories that a node type can belong to 
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def define_category(self, category_name: str, category_description: str) -> bool: 
        """
        Define a new category

        @param[in] categoryName Name of the new category
        @param[in] categoryDescription Description of the category

        @return false if there was already a category with the given name
        """
    @staticmethod
    def get_all_categories() -> object: 
        """
        Get the list of available categories and their descriptions.

        Returns:
            dict[str,str]: Dictionary with categories as a name:description dictionary if it succeeded, else None
        """
    @staticmethod
    def get_node_categories(node_id: object) -> object: 
        """
        Return the list of categories that have been applied to the node.

        Args:
            node_id (str | Node): The node, or path to the node, whose categories are to be found
        Returns:
            list[str]: A list of category names applied to the node if it succeeded, else None
        """
    @staticmethod
    def get_node_type_categories(node_type_id: object) -> object: 
        """
        Return the list of categories that have been applied to the node type.

        Args:
            node_type_id (str | NodeType): The node type, or name of the node type, whose categories are to be found
        Returns:
            list[str]: A list of category names applied to the node type if it succeeded, else None
        """
    def remove_category(self, category_name: str) -> bool: 
        """
        Remove an existing category, mainly to manage the ones created by a node type for itself

        @param[in] categoryName Name of the category to remove

        @return false if there was no category with the given name
        """
    @property
    def category_count(self) -> int:
        """
        :type: int
        """
    pass
class INodeTypeForwarding2(_INodeTypeForwarding2, INodeTypeForwarding, _INodeTypeForwarding, omni.core._core.IObject):
    """
    @brief Interface that creates a forward on a request for a node type to a different node type

    There are a couple of different common use cases for needing a forward:
    - Node type gets renamed
    - Node type moves from one extension to another

    The node type forward specifies the unique node type name so if extension omni.my.extension has a node whose type
    is specified as "MyNode" then the forward must be from "omni.my.extension.MyNode".

    The forwarding is version-based as well, where the version is a minimum number required for forwarding, the usual
    node version update mechanism not withstanding. For example, if you set up a forward from "omni.nodes.MyNode" version
    2 to "omni.my_nodes.MyNode" version 3 then any larger version number is forwarded to the same location:
    - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
    - omni.nodes.MyNode(3) -> omni.my_nodes.MyNode(3)
    - omni.nodes.MyNode(4) -> omni.my_nodes.MyNode(3)

    The forwards can also have multiple versions forwarding to different locations, so if on top of the above forward
    you also add a forward from "omni.nodes.MyNode" version 3 to "omni.new_nodes.MyNode" version 4 then these become
    the example forward locations:
    - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
    - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
    - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)

    Version numbers lower than the first forward are left as-is
    - omni.nodes.MyNode(1) -> omni.nodes.MyNode(1)

    @note The usual mechanism of calling updateVersionNumber on a node is only applied after a forward so in the above
          cases requesting omni.nodes.MyNode(2) does not call updateVersionNumber(1,2) on your omni.nodes.MyNode
          implementation.

    Node type forwards are associative, so if A forwards to B and B forwards to C then when you request A you get C.
    Adding a new forward from omni.my_nodes.MyNode(3) to omni.new_nodes.MyNode(2) above yields this forwarding:
    - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3) -> omni.new_nodes.MyNode(2)
    - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
    - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def inspect(self, inspector: omni.inspect._omni_inspect.IInspector) -> bool: 
        """
        Runs the inspector on the scheduling hints.

        @param[in] inspector The inspector class
        @return true if the inspection ran successfully, false if the inspection type is not supported
        """
    pass
class INodeTypeForwarding(_INodeTypeForwarding, omni.core._core.IObject):
    """
    @brief Interface that creates a forward on a request for a node type to a different node type

    There are a couple of different common use cases for needing a forward:
    - Node type gets renamed
    - Node type moves from one extension to another

    The node type forward specifies the unique node type name so if extension omni.my.extension has a node whose type
    is specified as "MyNode" then the forward must be from "omni.my.extension.MyNode".

    The forwarding is version-based as well, where the version is a minimum number required for forwarding, the usual
    node version update mechanism not withstanding. For example, if you set up a forward from "omni.nodes.MyNode" version
    2 to "omni.my_nodes.MyNode" version 3 then any larger version number is forwarded to the same location:
    - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
    - omni.nodes.MyNode(3) -> omni.my_nodes.MyNode(3)
    - omni.nodes.MyNode(4) -> omni.my_nodes.MyNode(3)

    The forwards can also have multiple versions forwarding to different locations, so if on top of the above forward
    you also add a forward from "omni.nodes.MyNode" version 3 to "omni.new_nodes.MyNode" version 4 then these become
    the example forward locations:
    - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
    - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
    - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)

    Version numbers lower than the first forward are left as-is
    - omni.nodes.MyNode(1) -> omni.nodes.MyNode(1)

    @note The usual mechanism of calling updateVersionNumber on a node is only applied after a forward so in the above
          cases requesting omni.nodes.MyNode(2) does not call updateVersionNumber(1,2) on your omni.nodes.MyNode
          implementation.

    Node type forwards are associative, so if A forwards to B and B forwards to C then when you request A you get C.
    Adding a new forward from omni.my_nodes.MyNode(3) to omni.new_nodes.MyNode(2) above yields this forwarding:
    - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3) -> omni.new_nodes.MyNode(2)
    - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
    - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def define_forward(self, forward_name: str, forward_version: int, replacement_name: str, replacement_version: int, replacement_extension_id: str) -> bool: 
        """
        @brief Define a new node type forward.
        It is allowed to have the same forwardName to be defined more than once, however the "forwardVersion" must be
        different from any existing ones. Later "forwardVersion" numbers will supersede earlier ones in this case.
        For example if you have these two forwards set up:
        - OldNode,1 -> BetterNode,1,omni.better.extension
        - OldNode,2 -> MuchBetterNode,1,omni.much_better.extension

        then when version 1 of "OldNode" is requested it will treat it as if you requested "BetterNode", but when
        versions 2 or later are requested it will instead treat it as if you requested "MuchBetterNode". These can be
        chained together:
        - OldNode,1 -> BetterNode,1,omni.better.extension
        - BetterNode,1 -> MuchBetterNode,1,omni.much_better.extension

        @param[in] forwardName Name to be replaced
        @param[in] forwardVersion The first version of the forward name to be replaced
        @param[in] replacementName Node type name that replaces the forwarded name
        @param[in] replacementVersion Version of the node type that replaces the forwarded name
        @param[in] extensionId Extension ID in which the replacement node type can be found
        @return false if there was already an forward with the given name and initial version number
        """
    @staticmethod
    def find_forward(forward_name: str, forward_version: int) -> tuple: 
        """
        Find a node type name replacement corresponding to the given node type forward name and version.

        Args:
             forward_name: Name of the node type forward to look up
             forward_version: Version number of the node type forward being looked up

        Returns:
            tuple[str,int,str] | None: Matching forward as (new_name, new_version, new_extension) if one was found, else None.
                e.g. find_forward("OldNode", 2) -> ("NewNode", 1, "omni.my.extension")

        Raises:
            ValueError: if there was no forward for the given name/version combination
        """
    @staticmethod
    def get_forwarding() -> object: 
        """
        Get the list of available node type forwarding.

        Returns:
            dict[tuple[str,str], tuple[str,int,str]] | None: Dictionary of all defined forwarding as
                (forwarded_name, forwarded_version): (new_name, new_version, new_extension) if it succeeded, else None.
                e.g. {("OldNode", 2): ("NewNode", 1, "omni.my.extension")}
        Raises:
            ValueError: if retrieval of the forwarding failed
        """
    def remove_forward(self, forward_name: str, forward_version: int) -> bool: 
        """
        @brief Remove an existing node type forward.
        Since an forwardName + forwardVersion combination is unique there is no need to pass in the replacement information.
        Only the forward with the matching version is removed. Any others with the same name remain untouched.

        @param[in] forwardName Forward to be removed
        @param[in] forwardVersion The version at which the forward is to be removed
        @return false if there was already an forward with the given name and initial version number
        """
    def remove_forwarded_type(self, referenced_name: str, referenced_version: int) -> int: 
        """
        @brief Remove forwards referencing a given node type name.

        @param[in] referencedName Forward to be removed
        @param[in] referencedVersion The version at which the forward is to be removed
        @return number of forwards to the given type that were removed
        """
    @property
    def forward_count(self) -> int:
        """
        :type: int
        """
    pass
class IPrimView(_IPrimView, omni.core._core.IObject):
    """
    PrimView is an interface that provides a view to a set of prims for use with OmniGraph instancing.

    The prim view provides both a list of prims, and a layout of which prims can be treated as consecutive data in fabric
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @property
    def paths(self) -> list:
        """
            Returns the list of prim paths as a flat list.

            

        :type: list
        """
    @property
    def prim_count(self) -> int:
        """
        :type: int
        """
    @property
    def segments(self) -> list:
        """
            Returns the property paths as a list of lists of segments.

            If the prim view supports ordering prims by bucket, then each sublist represents
            the prims in a single bucket, in the order they appear in the bucket.

            The order of the buckets is arbitrary, but stable between calls where the buckets have not been updated
            

        :type: list
        """
    pass
class ISchedulingHints2(_ISchedulingHints2, ISchedulingHints, _ISchedulingHints, omni.core._core.IObject):
    """
    Interface extension for ISchedulingHints that adds a new "pure" hint
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ISchedulingHints) -> None: ...
    @property
    def purity_status(self) -> ePurityStatus:
        """
        :type: ePurityStatus
        """
    @purity_status.setter
    def purity_status(self, arg1: ePurityStatus) -> None:
        pass
    pass
class ISchedulingHints(_ISchedulingHints, omni.core._core.IObject):
    """
    Interface to the list of scheduling hints that can be applied to a node type
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def get_data_access(self, data_type: eAccessLocation) -> eAccessType: 
        """
        Get the type of access the node has for a given data type

        @param[in] dataType Type of data for which access type is being modified
        @returns Value of the access type flag
        """
    def inspect(self, inspector: omni.inspect._omni_inspect.IInspector) -> bool: 
        """
        Runs the inspector on the scheduling hints.

        @param[in] inspector The inspector class
        @return true if the inspection ran successfully, false if the inspection type is not supported
        """
    def set_data_access(self, data_type: eAccessLocation, new_access_type: eAccessType) -> None: 
        """
        Set the flag describing how a node accesses particular data in its compute _abi (defaults to no access).
        Setting any of these flags will, in most cases, automatically mark the node as "not threadsafe".
        One current exception to this is allowing a node to be both threadsafe and a writer to USD, since
        such behavior can be achieved if delayed writebacks (e.g. "registerForUSDWriteBack") are utilized
        in the node's compute method.

        @param[in] dataType Type of data for which access type is being modified
        @param[in] newAccessType New value of the access type flag
        """
    @property
    def compute_rule(self) -> eComputeRule:
        """
        :type: eComputeRule
        """
    @compute_rule.setter
    def compute_rule(self, arg1: eComputeRule) -> None:
        pass
    @property
    def thread_safety(self) -> eThreadSafety:
        """
        :type: eThreadSafety
        """
    @thread_safety.setter
    def thread_safety(self, arg1: eThreadSafety) -> None:
        pass
    pass
class IVariable(_IVariable, omni.core._core.IObject):
    """
    Object that contains a value that is local to a graph, available from anywhere in the graph
    """
    def __bool__(self) -> bool: ...
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    def get(*args, **kwargs) -> typing.Any: 
        """
        Get the value of a variable

        Args:
            graph_context (omni.graph.core.GraphContext): The GraphContext object to get the variable value from.
            instance_path (str): Optional path to the prim instance to fetch the variable value for. By default this will
                fetch the variable value from the graph prim.

        Returns:
            Any: Value of the variable
        """
    @staticmethod
    def get_array(*args, **kwargs) -> typing.Any: 
        """
        Get the value of an array variable

        Args:
            graph_context (omni.graph.core.GraphContext): The GraphContext object to get the variable value from.
            get_for_write (bool): Should the data be retrieved for writing?
            reserved_element_count (int): If the data is to be retrieved for writing, preallocate this many elements
            instance_path (str): Optional path to the prim instance to fetch the variable value for. By default this will
                fetch the variable value from the graph prim.

        Returns:
            Any: Value of the array variable
        """
    @staticmethod
    def set(*args, **kwargs) -> typing.Any: 
        """
        Sets the value of a variable

        Args:
            graph_context (omni.graph.core.GraphContext): The GraphContext object to store the variable value.
            value (any): The value assigned to the variable.
            instance_path (str): Optional path to the prim instance to set the variable value on. By default this will
                set the variable value on the graph prim.

        Returns:
            bool: True if the value was successfully set
        """
    @staticmethod
    def set_type(*args, **kwargs) -> typing.Any: 
        """
        Changes the type of a variable. Changing the type of a variable may remove the variable's default value.

        Args:
            variable_type (omni.graph.core.Type): The type to switch the variable to.

        Returns:
            bool: True if the type was successfully changed.
        """
    @property
    def category(self) -> str:
        """
        :type: str
        """
    @category.setter
    def category(self, arg1: str) -> None:
        pass
    @property
    def display_name(self) -> str:
        """
        :type: str
        """
    @display_name.setter
    def display_name(self, arg1: str) -> None:
        pass
    @property
    def is_backed_by_usd(self) -> bool:
        """
            Specifies if the variable is backed by a Usd attribute.

            Returns:
                bool: True if the variable is backed by Usd, otherwise False.
            

        :type: bool
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def scope(self) -> eVariableScope:
        """
        :type: eVariableScope
        """
    @scope.setter
    def scope(self, arg1: eVariableScope) -> None:
        pass
    @property
    def source_path(self) -> str:
        """
        :type: str
        """
    @property
    def tooltip(self) -> str:
        """
        :type: str
        """
    @tooltip.setter
    def tooltip(self, arg1: str) -> None:
        pass
    @property
    def type(self) -> typing.Any:
        """
            Gets the data type of the variable.

            Returns:
                omni.graph.core.Type: The data type of the variable.
            

        :type: typing.Any
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    pass
class MemoryType():
    """
    Default memory location for an attribute or node's data

    Members:

      CPU : The memory is on the CPU by default

      CUDA : The memory is on the GPU by default

      ANY : The memory does not have any default device
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ANY: omni.graph.core._omni_graph_core.MemoryType # value = <MemoryType.ANY: 2>
    CPU: omni.graph.core._omni_graph_core.MemoryType # value = <MemoryType.CPU: 0>
    CUDA: omni.graph.core._omni_graph_core.MemoryType # value = <MemoryType.CUDA: 1>
    __members__: dict # value = {'CPU': <MemoryType.CPU: 0>, 'CUDA': <MemoryType.CUDA: 1>, 'ANY': <MemoryType.ANY: 2>}
    pass
class Node():
    """
    An element of execution within a graph, containing attributes and connected to other nodes
    """
    def __bool__(self) -> bool: ...
    def __eq__(self, arg0: Node) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def _do_not_use(self) -> bool: 
        """
        Temporary internal function - do not use
        """
    def clear_old_compute_messages(self) -> int: 
        """
        Clears all compute messages logged for the node prior to its most recent evaluation.
        Messages logged during the most recent evaluation remain untouched.

        Normally this will be called during graph evaluation so it is of little use unless
        you're writing your own evaluation manager.

        Returns:
            int: The number of messages that were deleted.
        """
    @staticmethod
    def create_attribute(*args, **kwargs) -> typing.Any: 
        """
        Creates an attribute with the specified name, type, and port type and returns success state.

        Args:
            attributeName (str): Name of the attribute.
            attributeType (omni.graph.core.Type): Type of the attribute.
            portType (omni.graph.core.AttributePortType): The port type of the attribute, defaults to
                omni.graph.core.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            value (Any): The initial value to set on the attribute, default is None
            extendedType (omni.graph.core.ExtendedAttributeType): The extended type of the attribute, defaults to
                omni.graph.core.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR
            unionTypes (str): Comma-separated list of union types if the extended type is
                omni.graph.core.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION,
                defaults to empty string for non-union types.

        Returns:
            bool: True if the creation was successful, else False
        """
    def deregister_on_connected_callback(self, callback: int) -> None: 
        """
        De-registers the on_connected callback to be invoked when attributes connect.

        Args:
            callback (callable): The handle that was returned during the register_on_connected_callback call
        """
    def deregister_on_disconnected_callback(self, callback: int) -> None: 
        """
        De-registers the on_disconnected callback to be invoked when attributes disconnect.

        Args:
            callback (callable): The handle that was returned during the register_on_disconnected_callback call
        """
    def deregister_on_path_changed_callback(self, callback: int) -> None: 
        """
        Deregisters the on_path_changed callback to be invoked when anything changes in the stage. [DEPRECATED]

        Args:
            callback (callable): The handle that was returned during the register_on_path_changed_callback call
        """
    def get_attribute(self, name: str) -> Attribute: 
        """
        Given the name of an attribute returns an attribute object to it.

        Args:
            name (str): The name of the attribute

        Returns:
            omni.graph.core.Attribute: Attribute with the given name, or None if it does not exist on the node
        """
    def get_attribute_exists(self, name: str) -> bool: 
        """
        Given an attribute name, returns whether this attribute exists or not.

        Args:
            name (str): The name of the attribute

        Returns:
            bool: True if the attribute exists on this node, else False
        """
    def get_attributes(self) -> typing.List[Attribute]: 
        """
        Returns the list of attributes on this node.
        """
    @staticmethod
    def get_backing_bucket_id(*args, **kwargs) -> typing.Any: 
        """
        This method was internal, and is now obsolete: it does not function anymore. In order to write back to USD, you can directly use the USD API.
        """
    @staticmethod
    def get_compound_graph_instance(*args, **kwargs) -> typing.Any: 
        """
        Returns a handle to the associated sub-graph, if the given node is a compound node.

        Returns:
            omni.graph.core.Graph: The subgraph
        """
    def get_compute_count(self) -> int: 
        """
        Returns the number of instances on which this node's computation has been invoked. The counter has a limited range and will
        eventually roll over to 0, so a higher count cannot be assumed to represent a more recent compute than an
        older one.

        Returns:
            int: Number of instances this node's computation has been invoked since the counter last rolled over to 0.
        """
    @staticmethod
    def get_compute_messages(*args, **kwargs) -> typing.Any: 
        """
        Returns a list of the compute messages currently logged for the node at a specific severity.

        Args:
            severity (omni.graph.core.Severity): Severity level of the message.

        Returns:
            list[str]: The list of messages, may be empty.
        """
    def get_compute_vectorized_count(self) -> int: 
        """
        Returns the number of vectorized segments on which this node's computation has been invoked. The counter has a limited range and will
        eventually roll over to 0, so a higher count cannot be assumed to represent a more recent compute than an
        older one.

        Returns:
            int: Number of vectorized segments on which this node's computation has been invoked since the counter last rolled over to 0.
        """
    def get_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Get the event stream the node uses for notification of changes.

        Returns:
            carb.events.IEventStream: Event stream to monitor for node changes
        """
    @staticmethod
    def get_graph(*args, **kwargs) -> typing.Any: 
        """
        Get the graph to which this node belongs

        Returns:
            omni.graph.core.Graph: Graph associated with the current node. The returned graph will be invalid if the
            node is not valid.
        """
    def get_graph_instance_id(self, instance: int = 18446744073709551614) -> str: 
        """
        Args:
            instance (int): an index that identify the graph instance for which a unique ID is requested
            Be aware that even if not instantiated, the authoring graph (kAuthoringGraphIndex) is different from any runtime instance.
        Returns:
             A unique name that identifies the graph for the requested index.
        """
    def get_handle(self) -> int: 
        """
        Get an opaque handle to the node

        Returns:
            int: a unique handle to the node
        """
    @staticmethod
    def get_node_type(*args, **kwargs) -> typing.Any: 
        """
        Gets the node type of this node

        Returns:
            omni.graph.core.NodeType: The node type from which this node was created.
        """
    def get_prim_path(self) -> str: 
        """
        Returns the path to the prim currently backing the node.
        """
    def get_type_name(self) -> str: 
        """
        Get the node type name

        Returns:
            str: The type name of the node.
        """
    @staticmethod
    def get_wrapped_graph(*args, **kwargs) -> typing.Any: 
        """
        Get the graph wrapped by this node

        Returns:
            omni.graph.core.Graph: The graph wrapped by the current node, if any.  The returned graph will be invalid
            if the node does not wrap a graph or is invalid.
        """
    def increment_compute_count(self) -> int: 
        """
        Increments the node's compute counter. This method is provided primarily for debugging and experimental uses
        and should not normally be used by end-users.

        Returns:
            int: The new compute counter. This may be zero if the counter has just rolled over.
        """
    def is_backed_by_usd(self) -> bool: 
        """
        Check if the node is back by USD or not

        Returns:
            bool: True if the current node is by an USD prim on the stage.
        """
    def is_compound_node(self) -> bool: 
        """
        Returns whether this node is a compound node. A compound node is a node that has a node type that
        is defined by an OmniGraph.

        Returns:
            bool: True if this node is a compound node, False otherwise.
        """
    def is_disabled(self) -> bool: 
        """
        Check if the node is currently disabled

        Returns:
            bool: True if the node is disabled.
        """
    def is_valid(self) -> bool: 
        """
        Check the validity of the node

        Returns:
            bool: True if the node is valid.
        """
    @staticmethod
    def log_compute_message(*args, **kwargs) -> typing.Any: 
        """
        Logs a compute message of a given severity for the node.

        This method is intended to be used from within the compute() method of a
        node to alert the user to any problems or issues with the node's most recent
        evaluation. They are accumulated until the next successful evaluation
        at which point they are cleared.

        If duplicate messages are logged, with the same severity level, only one is
        stored.

        Args:
            severity (omni.graph.core.Severity): Severity level of the message.
            message (str): The message.

        Returns:
            bool: True if the message has already been logged, else False
        """
    def node_id(self) -> int: 
        """
        Returns a unique identifier value for this node.

        Returns:
            int: Unique identifier value for the node - not persistent through file save and load
        """
    def register_on_connected_callback(self, callback: object) -> int: 
        """
        Registers a callback to be invoked when the node has attributes connected.  The callback takes 2 parameters:
        the attributes from and attribute to of the connection.

        Args:
            callback (callable): The callback function

        Returns:
            int: A handle that could be used for deregistration.
        """
    def register_on_disconnected_callback(self, callback: object) -> int: 
        """
        Registers a callback to be invoked when the node has attributes disconnected.  The callback takes 2 parameters:
        the attributes from and attribute to of the disconnection.

        Args:
            callback (callable): The callback function

        Returns:
            A handle identifying the callback that can be used for deregistration.
        """
    def register_on_path_changed_callback(self, callback: object) -> int: 
        """
        Registers a callback to be invoked when a path changes in the stage.  The callback takes 1 parameter:
        a list of the paths that were changed. [DEPRECATED]

        Args:
            callback (callable): The callback function

        Returns:
            A handle identifying the callback that can be used for deregistration.
        """
    def remove_attribute(self, attributeName: str) -> bool: 
        """
        Removes an attribute with the specified name and type and returns success state.

        Args:
            attributeName (str): Name of the attribute.

        Returns:
            bool: True if the removal was successful, False if the attribute was not found
        """
    def request_compute(self) -> bool: 
        """
        Requests a compute of this node

        Returns:
            bool: True if the request was successful, False if there was an error
        """
    def resolve_coupled_attributes(self, attributesArray: typing.List[Attribute]) -> bool: 
        """
        Resolves attribute types given a set of attributes which are fully type coupled.
        For example if node 'Increment' has one input attribute 'a' and one output attribute 'b'
        and the types of 'a' and 'b' should always match. If the input is resolved then this function will
        resolve the output to the same type.
        It will also take into consideration available conversions on the input size.
        The type of the first (resolved) provided attribute will be used to resolve others or select appropriate conversions

        Note that input attribute types are never inferred from output attribute types.

        This function should only be called from the INodeType function 'on_connection_type_resolve'

        Args:
            attributesArray (list[omni.graph.core.Attribute]): Array of attributes to be resolved as a coupled group

        Returns:
            bool: True if successful, False otherwise, usually due to mismatched or missing resolved types
        """
    @staticmethod
    def resolve_partially_coupled_attributes(*args, **kwargs) -> typing.Any: 
        """
        Resolves attribute types given a set of attributes, that can have differing tuple counts and/or array depth,
        and differing but convertible base data type.
        The three input buffers are tied together, holding the attribute, the tuple
        count, and the array depth of the types to be coupled.
        This function will solve base type conversion by targeting the first provided type in the list,
        for all other ones that require it.

        For example if node 'makeTuple2' has two input attributes 'a' and 'b' and one output 'c' and we want to resolve
        any float connection to the types 'a':float, 'b':float, 'c':float[2] (convertible base types and different tuple counts)
        then the input buffers would contain:
        attrsBuf = [a, b, c]
        tuplesBuf = [1, 1, 2]
        arrayDepthsBuf = [0, 0, 0]
        rolesBuf = [AttributeRole::eNone, AttributeRole::eNone, AttributeRole::eNone]

        This is worth noting that 'b' could be of any type convertible to float. But since the first provided
        attribute is 'a', the type of 'a' will be used to propagate the type resolution.

        Note that input attribute types are never inferred from output attribute types.

        This function should only be called from the INodeType function 'on_connection_type_resolve'

        Args:
            attributesArray (list[omni.graph.core.Attribute]): Array of attributes to be resolved as a coupled group
            tuplesArray (list[int]): Array of tuple count desired for each corresponding attribute. Any value
                of None indicates the found tuple count is to be used when resolving.
            arraySizesArray (list[int]): Array of array depth desired for each corresponding attribute. Any value
                of None indicates the found array depth is to be used when resolving.
            rolesArray (list[omni.graph.core.AttributeRole]): Array of role desired for each corresponding attribute. A
                value of AttributeRole::eUnknown indicates the found role is to be used when resolving.

        Returns:
            bool: True if successful, False otherwise, usually due to mismatched or missing resolved types
        """
    def set_compute_incomplete(self) -> None: 
        """
        Informs the system that compute is incomplete for this frame.   In lazy evaluation systems, this node will be
        scheduled on the next frame since it still has more work to do.
        """
    def set_disabled(self, disabled: bool) -> None: 
        """
        Sets whether the node is disabled or not.

        Args:
            disabled (bool): True for disabled, False for not.
        """
    pass
class NodeEvent():
    """
            Node modification event.
            

    Members:

      CREATE_ATTRIBUTE : Attribute was created

      REMOVE_ATTRIBUTE : Attribute was removed

      ATTRIBUTE_TYPE_RESOLVE : Extended attribute type was resolved
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ATTRIBUTE_TYPE_RESOLVE: omni.graph.core._omni_graph_core.NodeEvent # value = <NodeEvent.ATTRIBUTE_TYPE_RESOLVE: 2>
    CREATE_ATTRIBUTE: omni.graph.core._omni_graph_core.NodeEvent # value = <NodeEvent.CREATE_ATTRIBUTE: 0>
    REMOVE_ATTRIBUTE: omni.graph.core._omni_graph_core.NodeEvent # value = <NodeEvent.REMOVE_ATTRIBUTE: 1>
    __members__: dict # value = {'CREATE_ATTRIBUTE': <NodeEvent.CREATE_ATTRIBUTE: 0>, 'REMOVE_ATTRIBUTE': <NodeEvent.REMOVE_ATTRIBUTE: 1>, 'ATTRIBUTE_TYPE_RESOLVE': <NodeEvent.ATTRIBUTE_TYPE_RESOLVE: 2>}
    pass
class NodeType():
    """
    Definition of a node's interface and structure
    """
    def __bool__(self) -> bool: 
        """
        Returns whether the current node type is valid.
        """
    def __eq__(self, arg0: NodeType) -> bool: 
        """
        Returns whether two node type objects refer to the same underlying node type implementation.
        """
    def add_extended_input(self, name: str, type: str, is_required: bool, extended_type: ExtendedAttributeType) -> None: 
        """
        Adds an extended input type to this node type.  Every node of this node type would then have this input.

        Args:
            name (str): The name of the input
            type (str): Extra information for the type - for union types, this is a list of types of this union, comma separated
                For example, "double,float"
            is_required (bool): Whether the input is required or not
            extended_type (omni.graph.core.ExtendedAttributeType): The kind of extended attribute this is
                e.g. omni.graph.core.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION
        """
    def add_extended_output(self, name: str, type: str, is_required: bool, extended_type: ExtendedAttributeType) -> None: 
        """
        Adds an extended output type to this node type.  Every node of this node type would then have this output.

        Args:
            name (str): The name of the output
            type (str): Extra information for the type - for union types, this is a list of types of this union, comma separated
                For example, "double,float"
            is_required (bool): Whether the output is required or not
            extended_type (omni.graph.core.ExtendedAttributeType): The kind of extended attribute this is
                e.g. omni.graph.core.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION
        """
    def add_extended_state(self, name: str, type: str, is_required: bool, extended_type: ExtendedAttributeType) -> None: 
        """
        Adds an extended state type to this node type.  Every node of this node type would then have this state.

        Args:
            name (str): The name of the state attribute
            type (str): Extra information for the type - for union types, this is a list of types of this union, comma separated
                For example, "double,float"
            is_required (bool): Whether the state attribute is required or not
            extended_type (omni.graph.core.ExtendedAttributeType): The kind of extended attribute this is
                e.g. omni.graph.core.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION
        """
    def add_input(self, name: str, type: str, is_required: bool, default_value: object = None) -> None: 
        """
        Adds an input to this node type.  Every node of this node type would then have this input.

        Args:
            name (str): The name of the input
            type (str): The type name of the input
            is_required (bool): Whether the input is required or not
            default_value (any): Default value for the attribute if it is not explicitly set (None means no default)
        """
    def add_output(self, name: str, type: str, is_required: bool, default_value: object = None) -> None: 
        """
        Adds an output to this node type.  Every node of this node type would then have this output.

        Args:
            name (str): The name of the output
            type (str): The type name of the output
            is_required (bool): Whether the output is required or not
            default_value (any): Default value for the attribute if it is not explicitly set (None means no default)
        """
    def add_state(self, name: str, type: str, is_required: bool, default_value: object = None) -> None: 
        """
        Adds an state to this node type.  Every node of this node type would then have this state.

        Args:
            name (str): The name of the state
            type (str): The type name of the state
            is_required (bool): Whether the state is required or not
            default_value (any): Default value for the attribute if it is not explicitly set (None means no default)
        """
    def defined_at_runtime(self) -> bool: 
        """
        Checks to see if this node type was defined at runtime or at build time

        Returns:
            bool: True if this node type was defined at runtime.
        """
    def get_all_categories(self) -> list: 
        """
        Gets the node type's categories

        Returns:
            list[str]: A list of all categories associated with this node type
        """
    def get_all_metadata(self) -> dict: 
        """
        Gets the node type's metadata

        Returns:
            dict[str,str]: A dictionary of name:value metadata on the node type
        """
    def get_all_subnode_types(self) -> dict: 
        """
        Finds all subnode types of the current node type.

        Returns:
            dict[str, omni.graph.core.NodeType]: Dictionary of type_name:type_object for all subnode types of this one
        """
    def get_metadata(self, key: str) -> str: 
        """
        Returns the metadata value for the given key.

        Args:
            key (str): The metadata keyword

        Returns:
            str | None: Metadata value for the given keyword, or None if it is not defined
        """
    def get_metadata_count(self) -> int: 
        """
        Gets the number of metadata values set on the node type

        Returns:
            int: The number of metadata values currently defined on the node type.
        """
    def get_node_type(self) -> str: 
        """
        Get this node type's name

        Returns:
            str: The name of this node type.
        """
    def get_path(self) -> str: 
        """
        Gets the path to the node type definition

        Returns:
            str: The path to the node type prim. For compound node definitions, this is path on the stage to the
            OmniGraphSchema.CompoundNodeType_1 object that defines the compound.
            For other node types, the path returned is unique, but does not represent a valid Prim on the stage.
        """
    def get_scheduling_hints(self) -> ISchedulingHints: 
        """
        Gets the set of scheduling hints currently set on the node type.

        Returns:
            omni.graph.core.ISchedulingHints: The scheduling hints for this node type
        """
    def has_state(self) -> bool: 
        """
        Checks to see if instantiations of the node type has internal state

        Returns:
            bool: True if nodes of this type will have internal state data, False if not.
        """
    def inspect(self, inspector: omni.inspect._omni_inspect.IInspector) -> bool: 
        """
        Runs the inspector on the node type

        Args:
            inspector (omni.inspect.Inspector): The inspector to run

        Returns:
            bool: True if the inspector was successfully run on the node type, False if it is not supported
        """
    def is_compound_node_type(self) -> bool: 
        """
        Checks to see if this node type defines a compound node type

        Returns:
            bool: True if this node type is a compound node type, meaning its implementation is defined by an OmniGraph
        """
    def is_valid(self) -> bool: 
        """
        Checks to see if this object is valid

        Returns:
            bool: True if this node type object is valid.
        """
    def set_has_state(self, has_state: bool) -> None: 
        """
        Sets the boolean indicating a node has state.

        Args:
            has_state (bool): Whether the node has state or not
        """
    def set_metadata(self, key: str, value: str) -> bool: 
        """
        Sets the metadata value for the given key.

        Args:
            key (str): The metadata keyword
            value (str): The value of the metadata
        """
    def set_scheduling_hints(self, scheduling_hints: ISchedulingHints) -> None: 
        """
        Modify the scheduling hints defined on the node type.

        Args:
            scheduling_hints (omni.graph.core.ISchedulingHints): New set of scheduling hints for the node type
        """
    __hash__ = None
    pass
class OmniGraphBindingError(Exception, BaseException):
    pass
class PtrToPtrKind():
    """
    Memory type for the pointer to a GPU data array

    Members:

      NA : Memory is CPU or type is not an array

      CPU : Pointers to GPU arrays live on the CPU

      GPU : Pointers to GPU arrays live on the GPU
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CPU: omni.graph.core._omni_graph_core.PtrToPtrKind # value = <PtrToPtrKind.CPU: 1>
    GPU: omni.graph.core._omni_graph_core.PtrToPtrKind # value = <PtrToPtrKind.NA: 0>
    NA: omni.graph.core._omni_graph_core.PtrToPtrKind # value = <PtrToPtrKind.NA: 0>
    __members__: dict # value = {'NA': <PtrToPtrKind.NA: 0>, 'CPU': <PtrToPtrKind.CPU: 1>, 'GPU': <PtrToPtrKind.NA: 0>}
    pass
class Severity():
    """
    Severity level of the log message

    Members:

      INFO : Message is informational only

      WARNING : Message is regarding a recoverable unexpected situation

      ERROR : Message is regarding an unrecoverable unexpected situation
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ERROR: omni.graph.core._omni_graph_core.Severity # value = <Severity.ERROR: 2>
    INFO: omni.graph.core._omni_graph_core.Severity # value = <Severity.INFO: 0>
    WARNING: omni.graph.core._omni_graph_core.Severity # value = <Severity.WARNING: 1>
    __members__: dict # value = {'INFO': <Severity.INFO: 0>, 'WARNING': <Severity.WARNING: 1>, 'ERROR': <Severity.ERROR: 2>}
    pass
class Type():
    """
    Full definition of the data type owned by an attribute
    """
    def __eq__(self, arg0: Type) -> bool: ...
    def __getstate__(self) -> tuple: ...
    def __hash__(self) -> int: ...
    def __init__(self, base_type: BaseDataType, tuple_count: int = 1, array_depth: int = 0, role: AttributeRole = AttributeRole.NONE) -> None: ...
    def __ne__(self, arg0: Type) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    def get_base_type_name(self) -> str: 
        """
        Gets the name of this type's base data type

        Returns:
            str: Name of just the base data type of this type, e.g. "float"
        """
    def get_ogn_type_name(self) -> str: 
        """
        Gets the OGN-style name of this type

        Returns:
            str: Name of this type in OGN format, which differs slightly from the USD format, e.g. "float[3]"
        """
    def get_role_name(self) -> str: 
        """
        Gets the name of the role of this type

        Returns:
            str: Name of just the role of this type, e.g. "color"
        """
    def get_type_name(self) -> str: 
        """
        Gets the name of this data type

        Returns:
            str: Name of this type, e.g. "float3"
        """
    def is_compatible_raw_data(self, type_to_compare: Type) -> bool: 
        """
        Does a role-insensitive comparison with the given Type.

        For example double[3] != pointd[3], but they are compatible and so this function would return True.

        Args:
            type_to_compare (omni.graph.core.Type): Type to compare for compatibility

        Returns:
            bool: True if the given type is compatible with this type
        """
    def is_matrix_type(self) -> bool: 
        """
        Checks if the type one of the matrix types, whose tuples are interpreted as a square array

        Returns:
            bool: True if this type is one of the matrix types
        """
    @property
    def array_depth(self) -> int:
        """
                    (int) Zero for a single value, one for an array.

        :type: int
        """
    @array_depth.setter
    def array_depth(self, arg1: int) -> None:
        """
        (int) Zero for a single value, one for an array.
        """
    @property
    def base_type(self) -> BaseDataType:
        """
                    (omni.graph.core.BaseDataType) Base type of the attribute.

        :type: BaseDataType
        """
    @base_type.setter
    def base_type(self, arg1: BaseDataType) -> None:
        """
        (omni.graph.core.BaseDataType) Base type of the attribute.
        """
    @property
    def role(self) -> AttributeRole:
        """
                    (omni.graph.core.AttributeRole) The semantic role of the type.
                

        :type: AttributeRole
        """
    @role.setter
    def role(self, arg1: AttributeRole) -> None:
        """
        (omni.graph.core.AttributeRole) The semantic role of the type.
        """
    @property
    def tuple_count(self) -> int:
        """
                    (int) Number of components in each tuple. 1 for a single value (scalar), 3 for a point3d, etc.

        :type: int
        """
    @tuple_count.setter
    def tuple_count(self, arg1: int) -> None:
        """
        (int) Number of components in each tuple. 1 for a single value (scalar), 3 for a point3d, etc.
        """
    pass
class _IBundle2(IConstBundle2, _IConstBundle2, omni.core._core.IObject):
    pass
class _IBundleChanges(omni.core._core.IObject):
    pass
class _IBundleFactory2(IBundleFactory, _IBundleFactory, omni.core._core.IObject):
    pass
class _IBundleFactory(omni.core._core.IObject):
    pass
class _IConstBundle2(omni.core._core.IObject):
    pass
class _INodeCategories(omni.core._core.IObject):
    pass
class _INodeTypeForwarding2(INodeTypeForwarding, _INodeTypeForwarding, omni.core._core.IObject):
    pass
class _INodeTypeForwarding(omni.core._core.IObject):
    pass
class _IPrimView(omni.core._core.IObject):
    pass
class _ISchedulingHints2(ISchedulingHints, _ISchedulingHints, omni.core._core.IObject):
    pass
class _ISchedulingHints(omni.core._core.IObject):
    pass
class _IVariable(omni.core._core.IObject):
    pass
class eAccessLocation():
    """
    What type of non-attribute data does this node access

    Members:

      E_USD : Accesses the USD stage data

      E_GLOBAL : Accesses data that is not part of the node or node type

      E_STATIC : Accesses data that is shared by every instance of a particular node type

      E_TOPOLOGY : Accesses information on the topology of the graph to which the node belongs
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    E_GLOBAL: omni.graph.core._omni_graph_core.eAccessLocation # value = <eAccessLocation.E_GLOBAL: 1>
    E_STATIC: omni.graph.core._omni_graph_core.eAccessLocation # value = <eAccessLocation.E_STATIC: 2>
    E_TOPOLOGY: omni.graph.core._omni_graph_core.eAccessLocation # value = <eAccessLocation.E_TOPOLOGY: 3>
    E_USD: omni.graph.core._omni_graph_core.eAccessLocation # value = <eAccessLocation.E_USD: 0>
    __members__: dict # value = {'E_USD': <eAccessLocation.E_USD: 0>, 'E_GLOBAL': <eAccessLocation.E_GLOBAL: 1>, 'E_STATIC': <eAccessLocation.E_STATIC: 2>, 'E_TOPOLOGY': <eAccessLocation.E_TOPOLOGY: 3>}
    pass
class eAccessType():
    """
    How does the node access the data described by the enum eAccessLocation

    Members:

      E_NONE : There is no access to data of the associated type

      E_READ : There is only read access to data of the associated type

      E_WRITE : There is only write access to data of the associated type

      E_READ_WRITE : There is both read and write access to data of the associated type
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    E_NONE: omni.graph.core._omni_graph_core.eAccessType # value = <eAccessType.E_NONE: 0>
    E_READ: omni.graph.core._omni_graph_core.eAccessType # value = <eAccessType.E_READ: 1>
    E_READ_WRITE: omni.graph.core._omni_graph_core.eAccessType # value = <eAccessType.E_READ_WRITE: 3>
    E_WRITE: omni.graph.core._omni_graph_core.eAccessType # value = <eAccessType.E_WRITE: 2>
    __members__: dict # value = {'E_NONE': <eAccessType.E_NONE: 0>, 'E_READ': <eAccessType.E_READ: 1>, 'E_WRITE': <eAccessType.E_WRITE: 2>, 'E_READ_WRITE': <eAccessType.E_READ_WRITE: 3>}
    pass
class eComputeRule():
    """
    How the node is allowed to be computed

    Members:

      E_DEFAULT : Nodes are computed according to the default evaluator rules

      E_ON_REQUEST : The evaluator may skip computing this node until explicitly requested with INode::requestCompute
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    E_DEFAULT: omni.graph.core._omni_graph_core.eComputeRule # value = <eComputeRule.E_DEFAULT: 0>
    E_ON_REQUEST: omni.graph.core._omni_graph_core.eComputeRule # value = <eComputeRule.E_ON_REQUEST: 1>
    __members__: dict # value = {'E_DEFAULT': <eComputeRule.E_DEFAULT: 0>, 'E_ON_REQUEST': <eComputeRule.E_ON_REQUEST: 1>}
    pass
class ePurityStatus():
    """
    The purity of the node implementation. For some context, a "pure" node is
    one whose initialize, compute, and release methods are entirely deterministic,
    i.e. they will always produce the same output attribute values for a given set
    of input attribute values, and do not access, rely on, or otherwise mutate data
    external to the node's scope

    Members:

      E_IMPURE : Node is assumed to not be pure

      E_PURE : Node can be considered pure if explicitly specified by the node author
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    E_IMPURE: omni.graph.core._omni_graph_core.ePurityStatus # value = <ePurityStatus.E_IMPURE: 0>
    E_PURE: omni.graph.core._omni_graph_core.ePurityStatus # value = <ePurityStatus.E_PURE: 1>
    __members__: dict # value = {'E_IMPURE': <ePurityStatus.E_IMPURE: 0>, 'E_PURE': <ePurityStatus.E_PURE: 1>}
    pass
class eThreadSafety():
    """
    How thread safe is the node during evaluation

    Members:

      E_SAFE : Nodes can be evaluated in multiple threads safely

      E_UNSAFE : Nodes cannot be evaluated in multiple threads safely

      E_UNKNOWN : The thread safety status of the node type is unknown
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    E_SAFE: omni.graph.core._omni_graph_core.eThreadSafety # value = <eThreadSafety.E_SAFE: 0>
    E_UNKNOWN: omni.graph.core._omni_graph_core.eThreadSafety # value = <eThreadSafety.E_UNKNOWN: 2>
    E_UNSAFE: omni.graph.core._omni_graph_core.eThreadSafety # value = <eThreadSafety.E_UNSAFE: 1>
    __members__: dict # value = {'E_SAFE': <eThreadSafety.E_SAFE: 0>, 'E_UNSAFE': <eThreadSafety.E_UNSAFE: 1>, 'E_UNKNOWN': <eThreadSafety.E_UNKNOWN: 2>}
    pass
class eVariableScope():
    """
    Scope in which the variable has been made available

    Members:

      E_PRIVATE : Variable is accessible only to its graph 

      E_READ_ONLY : Variable can be read by other graphs 

      E_PUBLIC : Variable can be read/written by other graphs 
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    E_PRIVATE: omni.graph.core._omni_graph_core.eVariableScope # value = <eVariableScope.E_PRIVATE: 0>
    E_PUBLIC: omni.graph.core._omni_graph_core.eVariableScope # value = <eVariableScope.E_PUBLIC: 2>
    E_READ_ONLY: omni.graph.core._omni_graph_core.eVariableScope # value = <eVariableScope.E_READ_ONLY: 1>
    __members__: dict # value = {'E_PRIVATE': <eVariableScope.E_PRIVATE: 0>, 'E_READ_ONLY': <eVariableScope.E_READ_ONLY: 1>, 'E_PUBLIC': <eVariableScope.E_PUBLIC: 2>}
    pass
def _commit_output_attributes_data(python_commit_db: dict) -> None:
    """
    For internal use only. Batch commit of attribute values

    Args:
        python_commit_db : Dictionary of attributes as keys and data as values
    """
def _prefetch_input_attributes_data(python_prefetch_db: list) -> list:
    """
    For internal use only.

    Args:
        python_prefetch_db : List of attributes

    Returns:
        list[Any]: Prefetched attribute values
    """
def acquire_interface(plugin_name: str = None, library_path: str = None) -> ComputeGraph:
    pass
def attach(stage_id: int, mps: float) -> None:
    """
    Attach the graph to a particular stage.

    Args:
        stage_id (int): The stage id of the stage to attach to
        mps (float): the meters per second setting for the stage
    """
def create_prim_view_from_prims(prims: list) -> IPrimView:
    """
    Create a prim vie from a list of prims

    Args:
        prims: List of strings or Sdf.Paths of the prim location
    """
def create_prim_view_from_query(include: list, exclude: list = []) -> IPrimView:
    """
    Create a prim view from lists of tuples of (name, type) pairs, used to create a query that returns a subset of Prims
    in fabric.

    Note that the prim view returned may not return any Prims until it has been applied to a graph.

    Args:
        include: Attributes that must exist on the Prim to be returned by the query.
        exclude: Attributes that must not exist on the Prim to be returned by the query.
    """
def deregister_node_type(name: str) -> bool:
    """
    Deregisters a python subnode type with OmniGraph.

    Args:
        name (str): Name of the Python node type being deregistered

    Returns:
        bool: True if the deregistration was successful, else False
    """
def deregister_post_load_file_format_upgrade_callback(postload_handle: int) -> None:
    """
    De-registers the postload callback to be invoked when the file format version changes.

    Args:
        postload_handle (int): The handle that was returned during the register_post_load_file_format_upgrade_callback call
    """
def deregister_pre_load_file_format_upgrade_callback(preload_handle: int) -> None:
    """
    De-registers the preload callback to be invoked when the file format version changes.

    Args:
        preload_handle (int): The handle that was returned during the register_pre_load_file_format_upgrade_callback call
    """
def detach() -> None:
    """
    Detaches the graph from the currently attached stage.
    """
def get_all_graphs() -> typing.List[Graph]:
    """
    Get all of the top-level non-orchestration graphs

    Returns:
        list[omni.graph.core.Graph]: A list of the top level graphs (non-orchestration) in OmniGraph.
    """
def get_all_graphs_and_subgraphs() -> typing.List[Graph]:
    """
    Get all of the non-orchestration graphs

    Returns:
        list[omni.graph.core.Graph]: A list of the (non-orchestration) in OmniGraph.
    """
def get_bundle_tree_factory_interface() -> IBundleFactory:
    """
    Gets an object that can interface with an IBundleFactory

    Returns:
        omni.graph.core.IBundleFactory: Object that can interface with the bundle tree
    """
def get_compute_cuda_device() -> int:
    """
    Gets the CUDA device ID used by OmniGraph.

    Returns:
        int: The CUDA device used by OmniGraph.
    """
def get_compute_graph_contexts() -> typing.List[GraphContext]:
    """
    Gets all of the current graph contexts

    Returns:
        list[omni.graph.core.GraphContext]: A list of all graph contexts in OmniGraph.
    """
def get_global_orchestration_graphs() -> typing.List[Graph]:
    """
    Gets the global orchestration graphs

    Returns:
        list[omni.graph.core.Graph]: A list of the global orchestration graphs that house all other graphs.
    """
def get_global_orchestration_graphs_in_pipeline_stage(pipeline_stage: GraphPipelineStage) -> typing.List[Graph]:
    """
    Returns a list of the global orchestration graphs that house all other graphs for a given pipeline stage.

    Args:
        pipeline_stage (omni.graph.core.GraphPipelineStage): The pipeline stage in question

    Returns:
        list[omni.graph.core.Graph]: A list of the global orchestration graphs in the given pipeline stage
    """
def get_graph_by_path(path: str) -> object:
    """
    Finds the graph with the given path.

    Args:
        path (str): The path of the graph. For example "/World/PushGraph"

    Returns:
        omni.graph.core.Graph: The matching graph, or None if it was not found.
    """
def get_graphs_in_pipeline_stage(pipeline_stage: GraphPipelineStage) -> typing.List[Graph]:
    """
    Returns a list of the non-orchestration graphs for a given pipeline stage (simulation, pre-render, post-render)

    Args:
        pipeline_stage (omni.graph.core.GraphPipelineStage): The pipeline stage in question

    Returns:
        list[omni.graph.core.Graph]: The list of graphs belonging to the pipeline stage
    """
def get_node_by_path(path: str) -> object:
    """
    Get a node that lives at a given path

    Args:
        path (str): Path at which to find the node

    Returns:
        omni.graph.core.Node: The node corresponding to a node path in OmniGraph, None if no node was found at that path.
    """
def get_node_categories_interface() -> INodeCategories:
    """
    Gets an object for accessing the node categories

    Returns:
        omni.graph.core.INodeCategories: Object that can interface with the category data
    """
def get_node_type(node_type_name: str) -> NodeType:
    """
    Returns the registered node type object with the given name.

    Args:
        node_type_name (str): Name of the registered NodeType to find and return

    Returns:
        omni.graph.core.NodeType: NodeType object registered with the given name, None if it is not registered
    """
def get_node_type_forwarding_interface(*args, **kwargs) -> typing.Any:
    """
    Deprecated:
        Use get_node_type_forwarding_interface2() instead
    """
def get_node_type_forwarding_interface2(*args, **kwargs) -> typing.Any:
    """
    Gets an object for accessing the node type forwarding

    Returns:
        omni.graph.core.INodeTypeForwarding2: Object that can interface with the node type forward data
    """
def get_registered_nodes() -> typing.List[str]:
    """
    Get the currently registered node type names

    Returns:
        list[str]: The list of names of node types currently registered
    """
def is_global_graph_prim(prim_path: str) -> bool:
    """
    Determines if the prim path passed in represents a prim that is backing a global graph

    Args:
        prim_path (str): The path to the prim in question

    Returns:
        bool: True if the prim path represents a prim that is backing a global graph, False otherwise
    """
def on_shutdown() -> None:
    """
    For internal use only. Called to allow the Python API to clean up prior to the extension being unloaded.
    """
def register_node_type(name: object, version: int) -> None:
    """
    Registers a new python subnode type with OmniGraph.

    Args:
        name (str): Name of the Python node type being registered
        version (int): Version number of the Python node type being registered
    Raises:
        ValueError: If a subnode type of the same name was already registered
    """
def register_post_load_file_format_upgrade_callback(callback: object) -> int:
    """
    Registers a callback to be invoked when the file format version changes.  Happens after the
    file has already been parsed and stage attached to.  The callback takes 3 parameters: the old file format version,
    the new file format version, and the affected graph object.

    Args:
        callback (callable): The callback function

    Returns:
        int: A handle that could be used for deregistration. Note the calling module is responsible for deregistration
        of the callback in all circumstances, including where the extension is hot-reloaded.
    """
def register_pre_load_file_format_upgrade_callback(callback: object) -> int:
    """
    Registers a callback to be invoked when the file format version changes.  Happens before the
    file has already been parsed and stage attached to. The callback takes 3 parameters: the old file format version,
    the new file format version, and a graph object (always invalid since the graph has not been created yet).

    Args:
        callback (callable): The callback function

    Returns:
        int: A handle that could be used for deregistration. Note the calling module is responsible for deregistration
        of the callback in all circumstances, including where the extension is hot-reloaded.
    """
def register_python_node() -> None:
    """
    Registers the unique Python node type with OmniGraph. This houses all of the Python node implementations as subtypes.
    """
def release_interface(arg0: ComputeGraph) -> None:
    pass
def set_test_failure(has_failure: bool) -> None:
    """
    Sets or clears a generic test failure.

    Args:
        has_failure (bool): If True then increment the test failure count, else clear it.
    """
def shutdown_compute_graph() -> None:
    """
    Deprecated: do not use.
    """
def test_failure_count() -> int:
    """
    Gets the number of active test failures

    Returns:
        int: The number of currently active test failures.
    """
def update(current_time: float, elapsed_time: float) -> None:
    """
    Deprecated: do not use.
    """
ACCORDING_TO_CONTEXT_GRAPH_INDEX = 18446744073709551614
APPLIED_SCHEMA: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.APPLIED_SCHEMA: 11>
ASSET: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.ASSET: 12>
AUTHORING_GRAPH_INDEX = 18446744073709551615
BOOL: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.BOOL: 1>
BUNDLE: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.BUNDLE: 16>
COLOR: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.COLOR: 4>
CONNECTION: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.CONNECTION: 14>
DOUBLE: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.DOUBLE: 9>
ERROR: omni.graph.core._omni_graph_core.Severity # value = <Severity.ERROR: 2>
EXECUTION: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.EXECUTION: 13>
FLOAT: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.FLOAT: 8>
FRAME: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.FRAME: 8>
HALF: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.HALF: 7>
INFO: omni.graph.core._omni_graph_core.Severity # value = <Severity.INFO: 0>
INSTANCING_GRAPH_TARGET_PATH = '_OMNI_GRAPH_TARGET'
INT: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.INT: 3>
INT64: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.INT64: 5>
MATRIX: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.MATRIX: 14>
NONE: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.NONE: 0>
NORMAL: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.NORMAL: 2>
OBJECT_ID: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.OBJECT_ID: 15>
PATH: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.PATH: 17>
POSITION: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.POSITION: 3>
PRIM: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.PRIM: 13>
PRIM_TYPE_NAME: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.PRIM_TYPE_NAME: 12>
QUATERNION: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.QUATERNION: 6>
RELATIONSHIP: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.RELATIONSHIP: 11>
TAG: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.TAG: 15>
TARGET: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TARGET: 20>
TEXCOORD: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TEXCOORD: 5>
TEXT: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TEXT: 10>
TIMECODE: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TIMECODE: 9>
TOKEN: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.TOKEN: 10>
TRANSFORM: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.TRANSFORM: 7>
UCHAR: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.UCHAR: 2>
UINT: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.UINT: 4>
UINT64: omni.graph.core._omni_graph_core.BaseDataType # value = <BaseDataType.UINT64: 6>
UNKNOWN: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.UNKNOWN: 21>
VECTOR: omni.graph.core._omni_graph_core.AttributeRole # value = <AttributeRole.VECTOR: 1>
WARNING: omni.graph.core._omni_graph_core.Severity # value = <Severity.WARNING: 1>
_internal = omni.graph.core._omni_graph_core._internal
_og_unstable = omni.graph.core._omni_graph_core._og_unstable
