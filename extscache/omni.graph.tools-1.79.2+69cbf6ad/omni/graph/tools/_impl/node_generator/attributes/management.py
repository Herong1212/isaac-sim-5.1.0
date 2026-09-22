"""
Collection of utilities and constants to handle interaction with the set of all attribute managers

.. data:: ATTRIBUTE_MANAGERS

    Dictionary of {BASE_TYPE: AttributeManager} for all supported root attribute types. A root type is
    "int" but not "int[2]". Tuple counts and array depths are parsed by the manager's constructor.
"""

import json
import re
from contextlib import suppress
from typing import Dict, List, Optional, Tuple, Union

from ..keys import AttributeKeys
from ..utils import MetadataKeys, ParseError, UnimplementedError, attrib_description_to_string, check_memory_type
from .AnyAttributeManager import AnyAttributeManager
from .attribute_unions import load_attribute_union_groups
from .AttributeManager import AttributeManager
from .BoolAttributeManager import BoolAttributeManager
from .BundleAttributeManager import BundleAttributeManager
from .ColorAttributeManager import ColorAttributeManager
from .DoubleAttributeManager import DoubleAttributeManager
from .ExecutionAttributeManager import ExecutionAttributeManager
from .FloatAttributeManager import FloatAttributeManager
from .FrameAttributeManager import FrameAttributeManager
from .HalfAttributeManager import HalfAttributeManager
from .Int64AttributeManager import Int64AttributeManager
from .IntAttributeManager import IntAttributeManager
from .MatrixAttributeManager import MatrixAttributeManager
from .NormalAttributeManager import NormalAttributeManager
from .ObjectIdAttributeManager import ObjectIdAttributeManager
from .PathAttributeManager import PathAttributeManager
from .PointAttributeManager import PointAttributeManager
from .QuaternionAttributeManager import QuaternionAttributeManager
from .StringAttributeManager import StringAttributeManager
from .TargetAttributeManager import TargetAttributeManager
from .TexCoordAttributeManager import TexCoordAttributeManager
from .TimeCodeAttributeManager import TimeCodeAttributeManager
from .TokenAttributeManager import TokenAttributeManager
from .UCharAttributeManager import UCharAttributeManager
from .UInt64AttributeManager import UInt64AttributeManager
from .UIntAttributeManager import UIntAttributeManager
from .UnionAttributeManager import UnionAttributeManager
from .VectorAttributeManager import VectorAttributeManager

# ======================================================================
# Collection of all supported attribute type classes
ATTRIBUTE_MANAGERS = {
    support_class.OGN_TYPE: support_class
    for support_class in [
        AnyAttributeManager,
        BoolAttributeManager,
        BundleAttributeManager,
        DoubleAttributeManager,
        FloatAttributeManager,
        HalfAttributeManager,
        IntAttributeManager,
        Int64AttributeManager,
        ObjectIdAttributeManager,
        PathAttributeManager,
        StringAttributeManager,
        TargetAttributeManager,
        TimeCodeAttributeManager,
        TokenAttributeManager,
        UCharAttributeManager,
        UIntAttributeManager,
        UInt64AttributeManager,
        UnionAttributeManager,
    ]
}
# Role-based attributes have more than one possible type name so they have to be iterated
ATTRIBUTE_MANAGERS.update({role: ColorAttributeManager for role in ColorAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: MatrixAttributeManager for role in MatrixAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: FrameAttributeManager for role in FrameAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: NormalAttributeManager for role in NormalAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: PointAttributeManager for role in PointAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: QuaternionAttributeManager for role in QuaternionAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: TexCoordAttributeManager for role in TexCoordAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: VectorAttributeManager for role in VectorAttributeManager.roles()})
ATTRIBUTE_MANAGERS.update({role: ExecutionAttributeManager for role in ExecutionAttributeManager.roles()})
ALL_ATTRIBUTE_TYPES = ATTRIBUTE_MANAGERS  # Backward compatibility


# Attribute types that are OGN shorthand for a list of types, usable within union type definition list
ATTRIBUTE_UNION_GROUPS = load_attribute_union_groups()

# Pattern match for the attribute type names
# group(1) = Base name of the attribute type (e.g. double, float, ...)
# group(2) = Element count (None if no element count specified)
# group(3) = String with matching array brackets - len(group(3))/2 = array depth
RE_ATTRIBUTE_TYPE = re.compile(r"([^\[\]]+)(?:\[([1-9][0-9]{0,2})\])?((?:\[\]){0,2})$")


# ======================================================================
def expand_attribute_union_groups(union_types: List) -> List:
    """Expands any group names in a union type declaration, in-place. The
       list will have duplicate types removed.

    Args:
        union_types: The list of union types
    """
    union_type_set = set()
    for tp in union_types:
        for literal_type in ATTRIBUTE_UNION_GROUPS.get(tp, [tp]):
            union_type_set.add(literal_type)
    return list(union_type_set)


# ======================================================================
def split_attribute_type_name(
    full_type_name: Union[str, List],
) -> Tuple[str, int, int, Optional[Dict[str, AttributeManager]]]:
    """Split a fully qualified attribute type name into its identifying parts

    Args:
        full_type_name: Fully qualified attribute type consisting of type name
        followed by optional element count as "[X]" and optional arrays as "[]"

    Returns:
        (base name, element count, array depth, extra_info) extracted from the full name.
        e.g. "int[5][]" returns ("int", 5, 1) and "float[][]" returns ("float", 1, 2)
        If the type manager requires any construction parameters they will be in the last tuple
        element (None means no construction parameters need be passed)

    Raises:
        ParseError: the name passed in doesn't follow the naming pattern
    """
    extra_info = None
    if isinstance(full_type_name, list):
        attribute_name = "union"
        # Special syntax for annotating "lists of union types" encloses the entire attribute name in [] rather
        # than appending them to the end.   e.g. "type": [["float", "double"]], versus "type": "float[]"
        if full_type_name and isinstance(full_type_name[0], list):
            array_depth = 1
            types_accepted = full_type_name[0]
        else:
            array_depth = 0
            types_accepted = full_type_name
        extra_info = {}

        for attribute_type in expand_attribute_union_groups(types_accepted):
            extra_info[attribute_type] = get_attribute_manager_type(attribute_type)
        tuple_count = 1
    else:
        type_match = RE_ATTRIBUTE_TYPE.match(full_type_name)
        if type_match is None:
            raise ParseError(f"Attribute type name {full_type_name} does not match pattern TYPE{{[X]}}{{[]{{[]}}}}")
        attribute_name = type_match.group(1)

        tuple_count = 1
        if type_match.group(2) is not None:
            tuple_count = int(type_match.group(2))
        array_depth = 0
        if type_match.group(3) is not None:
            array_depth = int(len(type_match.group(3)) / 2)

    return (attribute_name, tuple_count, array_depth, extra_info)


# ======================================================================
def validate_attribute_type_name(type_name: str, tuple_count: int, array_depth: int):
    """Validate a fully qualified attribute name from its constituent parts.

    Use naming.py:assemble_attribute_type_name to give you the full name once it is validated.
    It would be done here except that would create a circular import problem. Normal usage is
        try:
            validate_attribute_type_name(type_name, tuple_count, array_depth)
            full_name = assemble_attribute_type_name(type_name, tuple_count, array_depth)
        except AttributeError:
            pass

    Args:
        type_name: Base name of the attribute type
        tuple_count: Number of tuple elements in the attribute type
        array_depth: Levels of arrays in the attribute type

    Raises:
        AttributeError: the constituent parts cannot be assembled into a legal attribute type
    """
    try:
        manager_type = ATTRIBUTE_MANAGERS[type_name]
    except KeyError as error:
        raise AttributeError(
            f"Type name {type_name} is not on the recognized list {list(ATTRIBUTE_MANAGERS.keys())}"
        ) from error
    tuples_supported = manager_type.tuples_supported()
    array_depths_supported = manager_type.array_depths_supported()

    def __get_legal_type_names() -> List[str]:
        """Returns the list of valid names for a legal type_name"""
        legal_tuple_names = [type_name] if 1 in tuples_supported else []
        legal_tuple_names = [f"{type_name}[{tuple_value}]" for tuple_value in tuples_supported if tuple_value > 1]
        all_legal_names = []
        for legal_depth in array_depths_supported:
            array_tag = "[]" * legal_depth
            for tuple_name in legal_tuple_names:
                all_legal_names.append(f"{type_name}{tuple_name}{array_tag}")
        return all_legal_names

    if tuple_count not in tuples_supported:
        raise AttributeError(
            f"Tuple count {tuple_count} is not supported. Attribute type must be one of {__get_legal_type_names()}"
        )
    if array_depth not in array_depths_supported:
        raise AttributeError(
            f"Array depth {array_depth} is not supported. Attribute type must be one of {__get_legal_type_names()}"
        )


# ======================================================================
def get_attribute_manager_type(attribute_type: str, attribute_name: str = "inputs:default"):
    """Returns an attribute manager that matches the name and type, with no other data.

    The attribute manager returned will be incomplete, and may not be valid. It is meant to use for things
    like verifying legal values for a type, avoiding the chicken-and-egg scenario of needing the manager to
    supply a legal value in order to set the legal value on that manager.

    Args:
        attribute_type: Fully encoded attribute type value, e.g. "int[3][]"

    Returns:
        Populated attribute manager for the given type (all other required values will be set to defaults)

    Raises:
        ParseError if the attribute type is not a recognized legal type
    """
    # Find the manager for this attribute's type
    try:
        base_type_name, tuple_count, array_depth, extra_info = split_attribute_type_name(attribute_type)
    except ParseError as error:
        raise ParseError(
            f'Could not decode attribute type "{attribute_type}" for attribute "{attribute_name}"'
        ) from error

    try:
        validate_attribute_type_name(base_type_name, tuple_count, array_depth)
    except AttributeError as e:
        raise ParseError(f'Unsupported attribute type "{attribute_type}" for attribute "{attribute_name}"') from e
    if extra_info is None:
        attribute_manager = ATTRIBUTE_MANAGERS[base_type_name](attribute_name, base_type_name)
    else:
        attribute_manager = ATTRIBUTE_MANAGERS[base_type_name](attribute_name, base_type_name, extra_info)
    attribute_manager.tuple_count = tuple_count
    attribute_manager.array_depth = array_depth

    return attribute_manager


# ======================================================================
def get_attribute_manager(attribute_name: str, attribute_data: dict) -> AttributeManager:
    """Deciphers, validates, and provides consistent access to attributes described by a dictionary.

    This function deciphers the type of attribute it contains and then runs a sub-parser appropriate to that type of
    attribute which performs semantic validation (e.g. that a default value is within a min/max range).

    Args:
        attribute_name: Fully namespaced name of the attribute being accessed
        attribute_data: Dictionary containing the attribute interface data, as extracted from the JSON

    Raise:
        ParseError: If there are any errors parsing the attribute description - string contains the problem

    Returns:
        Object that provides an interface to the parsed attribute
    """
    if not isinstance(attribute_data, dict):
        raise ParseError(f"Value of node name key {attribute_name} must be a dictionary")

    # Find the manager for this attribute's type
    try:
        attribute_manager = get_attribute_manager_type(
            attribute_data[AttributeKeys.TYPE], attribute_name=attribute_name
        )
    except KeyError:
        raise ParseError(f"The mandatory field 'type' is missing for attribute '{attribute_name}'") from None

    # Set the mandatory attribute values in a generic way
    for attr_key in AttributeKeys.MANDATORY:
        try:
            setattr(attribute_manager, attr_key, attribute_data[attr_key])
        except KeyError:
            raise ParseError(f'"{attr_key}" value is mandatory for attribute "{attribute_name}"') from None

    # Check to see if the attribute is optional
    with suppress(KeyError):
        attribute_manager.is_required = not attribute_data[AttributeKeys.OPTIONAL]

    # Check to see if the attribute has been deprecated
    with suppress(KeyError):
        attribute_manager.deprecation_msg = attribute_data[AttributeKeys.DEPRECATED]
        if isinstance(attribute_manager.deprecation_msg, list):
            attribute_manager.deprecation_msg = " ".join(attribute_manager.deprecation_msg)
        attribute_manager.is_deprecated = True

    # Check to see if the attribute can go into compute without validation
    with suppress(KeyError):
        attribute_manager.do_validation = not attribute_data[AttributeKeys.UNVALIDATED]

    # Store the attribute description in the metadata as there is no direct ABI for it
    attribute_manager.metadata[MetadataKeys.DESCRIPTION] = attrib_description_to_string(attribute_manager.description)

    # Check to see if the attribute is using the shorter definition of uiName metadata
    with suppress(KeyError):
        attribute_manager.metadata[MetadataKeys.UI_NAME] = attribute_data[AttributeKeys.UI_NAME]

    # Check to see if the attribute is using the shorter definition of allowedTokens metadata
    with suppress(KeyError):
        attribute_manager.metadata[MetadataKeys.ALLOWED_TOKENS] = attribute_data[AttributeKeys.ALLOWED_TOKENS]

    # Check to see if the attribute is overriding its memory type
    with suppress(KeyError):
        attribute_manager.memory_type = check_memory_type(attribute_data[AttributeKeys.MEMORY_TYPE])
        attribute_manager.metadata[MetadataKeys.MEMORY_TYPE] = attribute_manager.memory_type

    # Check to see if the attribute has any other metadata. Pass down empty metadata so that the attribute
    # managers have a chance to finalize the metadata they might have processed through the above
    attribute_manager.parse_metadata(attribute_data.get(AttributeKeys.METADATA, {}))

    # Check to see if the attribute has a default value set
    try:
        attribute_manager.default = attribute_data[AttributeKeys.DEFAULT]
        attribute_manager.validate_default()
        # Store the default value as metadata so that it can be retrieved to regenerate the file
        attribute_manager.metadata[MetadataKeys.DEFAULT] = json.dumps(attribute_manager.default)
    except KeyError:
        if attribute_manager.requires_default():
            attribute_manager.default = attribute_manager.empty_value()

    # Process the keys that are not mandatory for the specific discovered attribute type
    extra_properties = {key: value for key, value in attribute_data.items() if key not in AttributeKeys.PROCESSED}
    try:
        unparsed_properties = attribute_manager.parse_extra_properties(extra_properties)
        unparsed_errors = [_prop for _prop in unparsed_properties if _prop[0] != "$"]
        if unparsed_errors:
            raise ParseError(f"Unparsed fields {unparsed_errors}")
    except ParseError as error:
        raise ParseError(f"Failed parsing extra properties on {attribute_name}") from error

    return attribute_manager


# ======================================================================
def supported_attribute_type_names(do_formatting: bool = False) -> List[str]:
    """Returns a list of the OGN type names of all currently supported attribute types (e.g. "int[3]", not "int3")

    Args:
        do_formatting: If True then group together like tuples and arrays

    Returns:
        List of string representing all currently supported attribute types
    """
    supported_type_names = []
    for attribute_type_name, attribute_manager in ATTRIBUTE_MANAGERS.items():
        # USD no longer supports the transformX attribute types so filter them out
        if attribute_type_name.startswith("transform"):
            continue
        try:
            # Create a temporary to check support
            manager = attribute_manager("inputs:temp", attribute_type_name)
            supported_tuples = manager.tuples_supported()
            supported_array_depths = manager.array_depths_supported()
            supported_list = []
            for array_depth in supported_array_depths:
                for tuple_count in supported_tuples:
                    full_name = attribute_type_name
                    full_name = f"{full_name}[{tuple_count}]" if tuple_count > 1 else full_name
                    full_name += "[]" * array_depth
                    supported_list.append(full_name)
            # Add any supported types found in a single list
            if supported_list:
                if do_formatting:
                    supported_type_names.append(", ".join(supported_list))
                else:
                    supported_type_names += supported_list
        except TypeError:
            # This is hit when you try to get a union type, which should be reported differently anyway
            pass
        except (AttributeError, UnimplementedError):  # pragma: no cover   Should otherwise be a clean list
            pass
    supported_type_names.sort()
    return supported_type_names


# ======================================================================
def formatted_supported_attribute_type_names() -> List[str]:
    """Returns a list of the names of all currently supported attribute types, formatted in lines for easy reading"""
    supported_type_names = supported_attribute_type_names(do_formatting=True)
    supported_type_names.append('["A", "B", "C"... = Any one of the listed types]')
    return supported_type_names


# ======================================================================
def split_attribute_list(
    attributes: List[AttributeManager],
) -> Tuple[List[AttributeManager], List[AttributeManager], List[AttributeManager]]:
    """Split a list of attributes into three sets of sublists based on type of data the attribute holds.

    Args:
        attributes: List of attribute managers encapsulating the list of attributes to be split

    Returns:
        Tuple(SingleAttributes, BundleAttributes, RuntimeAttributes)
            SingleAttributes: Attributes containing a single piece of data, including tuples and arrays
            BundleAttributes: Attributes which are a bundle of other attributes, not having any actual data
            RuntimeAttributes: Attributes whose data type is only known at runtime
    """
    single_attributes = []
    bundle_attributes = []
    runtime_attributes = []
    for attribute in attributes:
        if attribute is None:
            continue
        if not attribute.has_fixed_type():
            runtime_attributes.append(attribute)
        elif attribute.create_type_name() == "bundle":
            bundle_attributes.append(attribute)
        else:
            single_attributes.append(attribute)

    return (single_attributes, bundle_attributes, runtime_attributes)


# ======================================================================
def list_without_runtime_attributes(attributes: List[AttributeManager]) -> List[AttributeManager]:
    """Return the attribute list, filtered to remove all attributes whose data type is determined at runtime.

    Args:
        attributes: List of attribute managers encapsulating the list of attributes to be filtered

    Returns:
        List of attributes whose types are known at compile time
    """
    known_attributes = []
    for attribute in attributes:
        if attribute is None:
            continue
        if attribute.has_fixed_type():
            known_attributes.append(attribute)

    return known_attributes
