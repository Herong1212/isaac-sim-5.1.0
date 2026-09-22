"""Support for nicer access to attribute types"""

from contextlib import suppress

import omni.graph.core as og

from .object_lookup import ObjectLookup
from .type_aliases import AttributeWithValue_t

# Mapping of the port type onto the namespace that the port type will enforce on attributes with that type
PORT_TYPE_NAMESPACES = {
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: "inputs",
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: "outputs",
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: "state",
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_UNKNOWN: "unknown",
}

# Mapping of the port type onto the namespace that the port type will enforce on attributes with that type
PORT_TYPE_NAMESPACES = {
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT: "inputs",
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT: "outputs",
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE: "state",
    og.AttributePortType.ATTRIBUTE_PORT_TYPE_UNKNOWN: "unknown",
}


# ================================================================================
def get_port_type_namespace(port_type: og.AttributePortType) -> str:
    """Returns a string representing the namespace attributes of the named port type reside in"""
    return PORT_TYPE_NAMESPACES[port_type]


# ----------------------------------------------------------------------
def get_attribute_configuration(attr: AttributeWithValue_t):
    """Get the array configuration information from the attribute.

    Attributes can be simple, tuples, or arrays of either. The information on what this is will be
    encoded in the attribute type name. This method decodes that type name to find out what type of
    attribute data the attribute will use.

    The method also gives the right answers for both Attribute and AttributeData with some suitable AttributeError
    catches to special case on unimplemented methods.

    Args:
        attr: Attribute whose configuration is being determined

    Returns:
        Tuple of:
            str: Name of the full/resolved data type used by the attribute (e.g. "float[3][]")
            str: Name of the simple data type used by the attribute (e.g. "float")
            bool: True if the data type is a tuple or array (e.g. "float3" or "float[]")
            bool: True if the data type is a matrix and should be flattened (e.g. "matrixd[3]" or "framed[4][]")

    Raises:
        TypeError: If the attribute type is not yet supported
    """
    # The actual data in extended types is the resolved type name; the attribute type is always token
    ogn_type = attr.get_resolved_type() if isinstance(attr, og.Attribute) else attr.get_type()
    type_name = ogn_type.get_ogn_type_name()

    # The root name is important for lookup
    root_type_name = ogn_type.get_base_type_name()

    if ogn_type.base_type == og.BaseDataType.UNKNOWN and (
        attr.get_extended_type()
        in (og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION)
    ):
        raise TypeError(f"Attribute '{attr.get_name()}' is not resolved, and so has no concrete type")

    is_array_type = (
        ogn_type.array_depth > 0 and ogn_type.role not in [og.AttributeRole.TEXT, og.AttributeRole.PATH]
    ) or ogn_type.role == og.AttributeRole.TARGET
    is_matrix_type = (
        type_name.startswith("matrix") or type_name.startswith("frame") or type_name.startswith("transform")
    )

    # Gather nodes automatically add one level of array to their attributes
    is_gather_node = False
    with suppress(AttributeError):
        is_gather_node = attr.get_node().get_type_name() == "Gather"
        if is_gather_node:
            if is_array_type:
                raise TypeError("Array types on Gather nodes are not yet supported in Python")
            is_array_type = True

    # Arrays of arrays are not yet supported in fabric so they cannot be supported in Python
    if ogn_type.array_depth > 1:
        raise TypeError("Nested array types are not yet supported in Python")

    return (type_name, root_type_name, is_array_type, is_matrix_type)


# ==============================================================================================================
def extract_attribute_type_information(attribute_object: AttributeWithValue_t) -> og.Type:
    """Decompose the type of an attribute into the parts relevant to getting and setting values.

    The naming of the attribute get and set methods in the Python bindings are carefully constructed to correspond
    to the ones returned here, to avoid construction of huge lookup tables. It makes the types instantly recognize
    newly added support, and it makes them easier to expand, at the cost of being less explicit about the
    correspondance between type and method.

    Note:
        If the attribute type is determined at runtime (e.g. Union or Any) then the resolved type is used.
        When the type is not yet resolved the raw types of the attributes are returned (usually "token")

    Args:
        attribute_object: Attribute-like object that has an attribute type that can be decomposed

    Returns:
        og.Type with the type information of the attribute_object

    Raises:
        TypeError: If the attribute type or attribute type object is not supported
    """
    if isinstance(attribute_object, og.Attribute):
        return attribute_object.get_resolved_type()
    if isinstance(attribute_object, og.AttributeData):
        return attribute_object.get_type()
    # The remaing types str, Sdf.Path and Usd.Property of AttributeWithValue_t
    if isinstance(attribute_object, AttributeWithValue_t):
        try:
            attribute = ObjectLookup.attribute(attribute_object)
            return attribute.get_resolved_type()
        except og.OmniGraphError:
            pass

    raise TypeError(f"Attribute object '{attribute_object}' of type '{type(attribute_object)}' is not supported")


# ==============================================================================================================
def get_attr_type(attr_info: AttributeWithValue_t):
    """
    Get the type for the given attribute, taking in to account extended type

    Args:
        attr: Attribute whose type is to be determined

    Returns:
        The type of the attribute
    """
    if isinstance(attr_info, og.AttributeData):
        return attr_info.get_type()

    attribute = ObjectLookup.attribute(attr_info)
    if attribute is None:
        raise og.OmniGraphError(f"Could not identify attribute from {attr_info} to get its type")

    return attribute.get_resolved_type()
