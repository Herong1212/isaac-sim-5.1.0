# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides USD property widgets and related utilities for use in the Omniverse Kit."""


__all__ = [
    "AllowedTokenItem",
    "ControlStateManager",
    "FloatModel",
    "GfMatrixAttributeModel",
    "GfQuatAttributeModel",
    "GfQuatEulerAttributeModel",
    "GfVecAttributeModel",
    "GfVecAttributeSingleChannelModel",
    "IntModel",
    "MdlEnumAttributeModel",
    "OptionItem",
    "PlaceholderAttribute",
    "PrimPathWidget",
    "PrimSelectionPayload",
    "SdfAssetPathArrayAttributeItemModel",
    "SdfAssetPathArrayAttributeSingleEntryModel",
    "SdfAssetPathAttributeModel",
    "SdfAssetPathItem",
    "SdfTimeCodeModel",
    "SelectionNotifier",
    "TfTokenAttributeModel",
    "UsdAttributeInvertedModel",
    "UsdAttributeModel",
    "UsdBase",
    "UsdFloatItem",
    "UsdMatrixItem",
    "UsdPropertyWidgets",
    "UsdQuatItem",
    "UsdVectorItem",
    "UsdPropertiesWidget",
    "UsdPropertiesWidgetBuilder",
    "UsdPropertyUiEntry",
    "SchemaPropertiesWidget",
    "get_large_selection_count",
    "RelationshipTargetPicker",
    "SelectionWatch",
    "MetadataObjectModel",
    "PayloadReferenceWidget",
    "CustomLayoutFrame",
    "CustomLayoutGroup",
    "CustomLayoutProperty",
    "RegisteredSchemaCodes",
    "register_schema",
    "get_registered_schemas",
    "is_registered_schema",
    "ADDITIONAL_CHANGED_PATH_EVENT_TYPE",
    "ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT",
]


from enum import IntEnum

from .control_state_manager import ControlStateManager
from .custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from .message_bus_events import ADDITIONAL_CHANGED_PATH_EVENT_TYPE, ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT
from .placeholder_attribute import PlaceholderAttribute
from .prim_selection_payload import *
from .references_widget import PayloadReferenceWidget
from .relationship import RelationshipTargetPicker, SelectionWatch
from .usd_attribute_model import *
from .usd_model_base import *
from .usd_model_items import *
from .usd_object_model import MetadataObjectModel
from .usd_property_widget import (
    SchemaPropertiesWidget,
    UsdPropertiesWidget,
    UsdPropertiesWidgetBuilder,
    UsdPropertyUiEntry,
)
from .widgets import Examples, PrimPathWidget, SelectionNotifier, UsdPropertyWidgets


def get_large_selection_count():
    """Fetches the count of large selections from the settings.

    Returns:
        int: The number of large selections as per the settings."""
    import carb.settings

    return carb.settings.get_settings().get("/persistent/exts/omni.kit.property.usd/large_selection")


class RegisteredSchemaCodes(IntEnum):
    """returned by is_registered_schema"""

    NOT_FOUND = 1
    """returned by **is_registered_schema()** when named widget isn't found"""
    FOUND = 2
    """returned by **is_registered_schema()** when named widget is found"""
    PRIVATE = 4
    """additional state flag. if its not owned by this widget and shouldn't be processed."""
    PUBLIC = 8
    """additional state flag. it can be processed and owner isn't important."""
    NO_CREATE = 16
    """additional state flag. Don't add to "Add Schema API" window list."""
    NO_REMOVE = 32
    """additional state flag. Schema API is locked can cannot be removed."""


property_widget_schemas = {}


def register_schema(widget_name: str, schemas: list, options: RegisteredSchemaCodes = RegisteredSchemaCodes.PRIVATE):
    """
    Register schemas to widget, to add ownership.

    Args:
        widget_name (str): Name of widget that owns this schema.
        schemas (list): List of schemas.
        options (RegisteredSchemaCodes): Ownership flags of schemas.
    """
    from pxr import Tf, Usd

    new_schema_names = {}
    widget_schemas = property_widget_schemas.get(widget_name, {})
    schema_reg = Usd.SchemaRegistry()
    for s in schemas:
        if isinstance(s, Tf.Type):
            if schema_reg.IsAppliedAPISchema(s) and schema_reg.GetAPISchemaTypeName(s) not in widget_schemas:
                new_schema_names[schema_reg.GetAPISchemaTypeName(s)] = options
        elif isinstance(s, str) and s not in widget_schemas:
            new_schema_names[s] = options

    if new_schema_names:
        if widget_name in property_widget_schemas:
            property_widget_schemas[widget_name] |= new_schema_names
        else:
            property_widget_schemas[widget_name] = new_schema_names


def get_registered_schemas():
    """Get dictionary of all registered schema."""
    return property_widget_schemas


def is_registered_schema(widget_names: list[str], schema_name: str) -> tuple[str, RegisteredSchemaCodes]:
    """
    Check is schema is registered for widget.

    Args:
        widget_names (list[str]): List of name of widget that owns this schema.
        schema_name (str): Name of schema to get ownership flags.

    Returns:
        (str, RegisteredSchemaCodes): Name of owner and ownership flags. See RegisteredSchemaCodes for more info.
    """
    for widget_name in widget_names:
        if widget_name in property_widget_schemas and schema_name in property_widget_schemas[widget_name]:
            return widget_name, property_widget_schemas[widget_name][schema_name]

    for key, schemas in property_widget_schemas.items():
        if schema_name in schemas:
            return key, schemas[schema_name]

    return "", RegisteredSchemaCodes.NOT_FOUND
