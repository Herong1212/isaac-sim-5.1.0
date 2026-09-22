"""Initialization for the OmniGraph UI extension"""

# Required for proper resolution of ONI wrappers
import omni.core

from ._impl.compute_node_widget import ComputeNodeWidget, ComputeNodeWidgetUtils
from ._impl.extension import _PublicExtension
from ._impl.graph_variable_custom_layout import GraphVariableCustomLayout
from ._impl.layer_identifier_widget_builder import LayerIdentifierWidgetBuilder, LayerModel
from ._impl.menu import add_create_menu_type, remove_create_menu_type
from ._impl.omnigraph_attribute_base import OmniGraphBase
from ._impl.omnigraph_attribute_builder import OmniGraphPropertiesWidgetBuilder
from ._impl.omnigraph_attribute_models import OmniGraphAttributeModel, OmniGraphTfTokenAttributeModel
from ._impl.omnigraph_conversion_node_templates import ConversionNodeCustomLayoutBase
from ._impl.omnigraph_prim_node_templates import (
    PrimAttributeCustomLayoutBase,
    PrimPathCustomLayoutBase,
    ReadPrimsCustomLayoutBase,
)
from ._impl.omnigraph_random_node_templates import RandomNodeCustomLayoutBase
from ._impl.omnigraph_settings_editor import SETTING_PAGE_NAME
from ._impl.standalone_attribute_builder import StandaloneAttributeBuilder
from ._impl.utils import build_port_type_convert_menu, find_prop

# Anything added here must also be added to the list of public APIs in test_api.py
__all__ = [
    "add_create_menu_type",
    "build_port_type_convert_menu",
    "ComputeNodeWidget",
    "ComputeNodeWidgetUtils",
    "find_prop",
    "GraphVariableCustomLayout",
    "LayerIdentifierWidgetBuilder",
    "LayerModel",
    "OmniGraphAttributeModel",
    "OmniGraphBase",
    "OmniGraphPropertiesWidgetBuilder",
    "OmniGraphTfTokenAttributeModel",
    "PrimAttributeCustomLayoutBase",
    "PrimPathCustomLayoutBase",
    "RandomNodeCustomLayoutBase",
    "ReadPrimsCustomLayoutBase",
    "ConversionNodeCustomLayoutBase",
    "remove_create_menu_type",
    "SETTING_PAGE_NAME",
    "StandaloneAttributeBuilder",
]
