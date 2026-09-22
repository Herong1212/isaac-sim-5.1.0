"""Support for generating .ogn content from existing nodes"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import omni.graph.core as og
import omni.graph.tools as ogt
import omni.graph.tools.ogn as ogn


# ==============================================================================================================
def __get_scheduling_hints(scheduling_hints: og.ISchedulingHints) -> Dict[str, Any]:
    """Returns the subsections of the node definition that define scheduling hints. Only non-defaults are included"""
    scheduling = []
    if og.eThreadSafety.E_SAFE == scheduling_hints.thread_safety:
        scheduling.append(ogn.SchedulingHints.THREADSAFE)

    global_access = scheduling_hints.get_data_access(og.eAccessLocation.E_GLOBAL)
    if global_access == og.eAccessType.E_READ:
        scheduling.append(ogn.SchedulingHints.GLOBAL_DATA_READ)
    elif global_access == og.eAccessType.E_WRITE:
        scheduling.append(ogn.SchedulingHints.GLOBAL_DATA_WRITE)
    elif global_access == og.eAccessType.E_READ_WRITE:
        scheduling.append(ogn.SchedulingHints.GLOBAL_DATA)

    static_access = scheduling_hints.get_data_access(og.eAccessLocation.E_STATIC)
    if static_access == og.eAccessType.E_READ:
        scheduling.append(ogn.SchedulingHints.STATIC_DATA_READ)
    elif static_access == og.eAccessType.E_WRITE:
        scheduling.append(ogn.SchedulingHints.STATIC_DATA_WRITE)
    elif static_access == og.eAccessType.E_READ_WRITE:
        scheduling.append(ogn.SchedulingHints.STATIC_DATA)

    topology_access = scheduling_hints.get_data_access(og.eAccessLocation.E_TOPOLOGY)
    if topology_access == og.eAccessType.E_READ:
        scheduling.append(ogn.SchedulingHints.TOPOLOGY_READ)
    elif topology_access == og.eAccessType.E_WRITE:
        scheduling.append(ogn.SchedulingHints.TOPOLOGY_WRITE)
    elif topology_access == og.eAccessType.E_READ_WRITE:
        scheduling.append(ogn.SchedulingHints.TOPOLOGY)

    usd_access = scheduling_hints.get_data_access(og.eAccessLocation.E_USD)
    if usd_access == og.eAccessType.E_READ:
        scheduling.append(ogn.SchedulingHints.USD_READ)
    elif usd_access == og.eAccessType.E_WRITE:
        scheduling.append(ogn.SchedulingHints.USD_WRITE)
    elif usd_access == og.eAccessType.E_READ_WRITE:
        scheduling.append(ogn.SchedulingHints.USD)

    compute_rule = scheduling_hints.compute_rule
    if compute_rule == og.eComputeRule.E_ON_REQUEST:
        scheduling.append(ogn.SchedulingHints.COMPUTERULE_ON_REQUEST)

    # purity_status is in IScheduleHints2 objects
    if hasattr(scheduling_hints, "purity_status"):
        purity_status = scheduling_hints.purity_status
        if purity_status == og.ePurityStatus.E_PURE:
            scheduling.append(ogn.SchedulingHints.PURE)

    return {ogn.NodeTypeKeys.SCHEDULING: scheduling} if scheduling else {}


# ==============================================================================================================
def __get_node_type_metadata(node_type: og.NodeType) -> Dict[str, Any]:
    """Returns the subsections of the node definition that come from its metadata"""
    full_data = {}
    metadata = {}
    icon_data = {}
    for key, value in node_type.get_all_metadata().items():
        # Description, tags, and UI Name are promoted to top level keys
        if key == ogn.MetadataKeys.DESCRIPTION:
            full_data[ogn.NodeTypeKeys.DESCRIPTION] = ogt.shorten_string_lines_to(value, 100)
        elif key == ogn.MetadataKeys.TAGS:
            full_data[ogn.NodeTypeKeys.TAGS] = value
        elif key == ogn.MetadataKeys.UI_NAME:
            full_data[ogn.NodeTypeKeys.UI_NAME] = value
        # Extension is part of the generated metadata and should not be in the file
        elif key == ogn.MetadataKeys.EXTENSION:
            pass
        # Language is only output if it is not the default C++
        elif key == ogn.MetadataKeys.LANGUAGE:
            if value != ogn.LanguageTypeValues.CPP:
                full_data[ogn.NodeTypeKeys.LANGUAGE] = value
        # Icon metadata is added hierarchically
        elif key == ogn.MetadataKeys.ICON_BACKGROUND_COLOR:
            icon_data[ogn.IconKeys.BACKGROUND_COLOR] = value
        elif key == ogn.MetadataKeys.ICON_BORDER_COLOR:
            icon_data[ogn.IconKeys.BORDER_COLOR] = value
        elif key == ogn.MetadataKeys.ICON_COLOR:
            icon_data[ogn.IconKeys.COLOR] = value
        elif key == ogn.MetadataKeys.ICON_PATH:
            # Prune the path by assuming that it is in the same directory as the .ogn file
            icon_path = Path(value)
            icon_data[ogn.IconKeys.PATH] = f"{icon_path.stem.split('.')[-1]}{icon_path.suffix}"
        elif key == ogn.MetadataKeys.TOKENS:
            full_data[ogn.NodeTypeKeys.TOKENS] = json.loads(value)
        elif key == ogn.MetadataKeys.EXCLUSIONS:
            full_data[ogn.NodeTypeKeys.EXCLUDE] = value.split(",")
        elif key == ogn.MetadataKeys.MEMORY_TYPE:
            full_data[ogn.NodeTypeKeys.MEMORY_TYPE] = value
        # Anything else is plain old generic metadata
        # Ignore internal metadata as it comes from other keywords
        elif not key.startswith("__"):
            metadata[key] = value
    # Insert the hierarchical metadata assembled from the list
    if metadata:
        full_data[ogn.NodeTypeKeys.METADATA] = metadata
    if icon_data:
        full_data[ogn.NodeTypeKeys.ICON] = icon_data
    return full_data


# ==============================================================================================================
def __get_attribute_metadata(attribute: og.Attribute) -> Dict[str, Any]:  # pragma no cover  - requires ogn to test
    """Returns the subsections of the attribute definition that come from its metadata"""
    full_data = {}
    metadata = {}
    for key, value in attribute.get_all_metadata().items():
        # Description, tags, and UI Name are promoted to top level keys
        if key == ogn.MetadataKeys.DESCRIPTION:
            full_data[ogn.AttributeKeys.DESCRIPTION] = ogt.shorten_string_lines_to(value, 100)
        elif key == ogn.MetadataKeys.ALLOWED_TOKENS:
            # This is handled using the raw token data, to account for lists and dictionaries
            pass
        elif key == ogn.MetadataKeys.ALLOWED_TOKENS_RAW:
            metadata[ogn.AttributeKeys.ALLOWED_TOKENS] = json.loads(value)
        elif key == ogn.MetadataKeys.UI_NAME:
            full_data[ogn.AttributeKeys.UI_NAME] = value
        elif key == ogn.MetadataKeys.MEMORY_TYPE:
            full_data[ogn.AttributeKeys.MEMORY_TYPE] = value
        elif key == ogn.MetadataKeys.DEFAULT:
            full_data[ogn.AttributeKeys.DEFAULT] = json.loads(value)

        # Anything else is plain old generic metadata
        elif not key.startswith("__"):
            metadata[key] = value
    # Insert the hierarchical metadata assembled from the list
    if metadata:
        full_data[ogn.AttributeKeys.METADATA] = metadata
    return full_data


# ==============================================================================================================
def __get_attribute_type_information(attribute: og.Attribute) -> Union[str, List[str]]:
    """Returns the description of the attribute's type information required by OGN"""
    if attribute.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY:
        return "any"

    if attribute.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION:
        return attribute.get_union_types()

    return attribute.get_resolved_type().get_ogn_type_name()


# ==============================================================================================================
def __get_attribute_configuration(node: og.Node) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Returns the three subsections describing the attributes in the list"""
    inputs = {}
    outputs = {}
    state = {}
    for attribute in node.get_attributes():
        attribute_name = ogn.attribute_name_without_port(attribute.get_name())
        # Ignore the schema attributes
        if attribute_name in ["node:type", "node:typeVersion"]:
            continue
        # Skip the automatically generated output bundle
        if attribute_name == node.get_prim_path().split("/")[-1]:
            continue
        port = attribute.get_port_type()
        if port == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
            attributes = inputs
        elif port == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
            attributes = outputs
        elif port == og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE:
            attributes = state
        else:
            # Non-standard attributes are not part of OGN
            continue
        attribute_detail = {ogn.AttributeKeys.TYPE: __get_attribute_type_information(attribute)}

        attribute_detail.update(__get_attribute_metadata(attribute))

        if attribute.is_optional_for_compute:
            attribute_detail[ogn.AttributeKeys.OPTIONAL] = True

        attributes.update({attribute_name: attribute_detail})

    return (inputs, outputs, state)


# ==============================================================================================================
def generate_ogn_from_node(node: og.Node) -> Dict[str, Any]:
    """Return a .ogn dictionary that implements the node type information contained in the given node"""
    ogn_data = {}

    # OM-41093 prevents using node_type.get_node_type() to extract the name from the ABI. Fortunately the
    # type is preserved in the node attributes.
    node_type = node.get_node_type()
    if node_type is None:
        raise ValueError(f"Node {node.get_prim_path()} did not have a recognized node type")
    try:
        node_type_name = node.get_attribute("node:type").get()
    except TypeError:
        node_type_name = node_type.get_node_type()

    ogn_data[ogn.NodeTypeKeys.VERSION] = og.GraphRegistry().get_node_type_version(node_type_name)

    ogn_data.update(__get_node_type_metadata(node_type))

    ogn_data.update(__get_scheduling_hints(node_type.get_scheduling_hints()))

    (inputs, outputs, state) = __get_attribute_configuration(node)
    if inputs:
        ogn_data.update({ogn.NodeTypeKeys.INPUTS: inputs})
    if outputs:
        ogn_data.update({ogn.NodeTypeKeys.OUTPUTS: outputs})
    if state or node_type.has_state():
        ogn_data.update({ogn.NodeTypeKeys.STATE: state})

    return {node_type_name: ogn_data}
