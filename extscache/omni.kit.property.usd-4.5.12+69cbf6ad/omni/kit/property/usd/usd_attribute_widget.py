# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "UsdAttributeUiEntry",
    "UsdAttributesWidget",
    "SchemaAttributesWidget",
    "MultiSchemaAttributesWidget",
    "UsdAttributeModel",
]

from typing import List

from pxr import Sdf

from .usd_attribute_model import UsdAttributeModel
from .usd_property_widget import (
    MultiSchemaPropertiesWidget,
    SchemaPropertiesWidget,
    UsdPropertiesWidget,
    UsdPropertyUiEntry,
)


class UsdAttributeUiEntry(UsdPropertyUiEntry):  # pragma: no cover
    """
    DEPRECATED! KEEP FOR BACKWARD COMPATIBILITY. Use UsdPropertyUiEntry instead.

    UsdAttributeUiEntry is the UI entry for an attribute.
    """


class UsdAttributesWidget(UsdPropertiesWidget):  # pragma: no cover
    """
    DEPRECATED! KEEP FOR BACKWARD COMPATIBILITY. Use UsdPropertiesWidget instead.

    UsdAttributesWidget provides functionalities to automatically populates UsdAttributes on given prim(s). The UI will
    and models be generated according to UsdAttributes's value type. Multi-prim editing works for shared Attributes
    between all selected prims if instantiated with multi_edit = True.
    """

    def __init__(self, title: str, collapsed: bool, multi_edit: bool = True):
        """
        Constructor.

        Args:
            title: title of the widget.
            collapsed: whether the collapsable frame should be collapsed for this widget.
            multi_edit: whether multi-editing is supported.
                If False, properties will only be collected from the last selected prim.
                If True, shared properties among all selected prims will be collected.
        """
        super().__init__(title, collapsed, multi_edit)

    def build_attribute_item(self, stage, ui_attr: UsdAttributeUiEntry, prim_paths: List[Sdf.Path]):
        """
        Build the attribute item.

        Args:
            stage: The stage.
            ui_attr: The attribute ui entry.
            prim_paths: The prim paths.

        Returns:
            The attribute item.
        """
        return super().build_property_item(stage, ui_attr, prim_paths)

    def _filter_attrs_to_build(self, attrs):
        """
        Filter the attributes to build.

        Args:
            attrs: The attributes.

        Returns:
            The filtered attributes.
        """
        return super()._filter_props_to_build(attrs)

    def _customize_attrs_layout(self, attrs):
        """
        Customize the attributes layout.

        Args:
            attrs: The attributes.

        Returns:
            The customized attributes.
        """
        return super()._customize_props_layout(attrs)

    def _get_shared_attributes_from_selected_prims(self, anchor_prim):
        """
        Get the shared attributes from the selected prims.

        Args:
            anchor_prim: The anchor prim.

        Returns:
            The shared attributes.
        """
        return super()._get_shared_properties_from_selected_prims(anchor_prim)

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        """
        Build the property item.

        Args:
            stage: The stage.
            ui_prop: The property ui entry.
            prim_paths: The prim paths.

        Returns:
            The property item.
        """
        return self.build_attribute_item(stage, ui_prop, prim_paths)

    def _filter_props_to_build(self, props):
        """
        Filter the properties to build.

        Args:
            props: The properties.

        Returns:
            The filtered properties.
        """
        return self._filter_attrs_to_build(props)

    def _customize_props_layout(self, props):
        """
        Customize the properties layout.

        Args:
            props: The properties.

        Returns:
            The customized properties.
        """
        return self._customize_attrs_layout(props)

    def _get_shared_properties_from_selected_prims(self, anchor_prim):
        """
        Get the shared properties from the selected prims.

        Args:
            anchor_prim: The anchor prim.

        Returns:
            The shared properties.
        """
        return self._get_shared_attributes_from_selected_prims(anchor_prim)


class SchemaAttributesWidget(SchemaPropertiesWidget):  # pragma: no cover
    """
    DEPRECATED! KEEP FOR BACKWARD COMPATIBILITY. Use SchemaPropertiesWidget instead.

    SchemaAttributesWidget only filters attributes and only show the onces from a given IsA schema or applied API schema.
    """

    def build_attribute_item(self, stage, ui_attr: UsdAttributeUiEntry, prim_paths: List[Sdf.Path]):
        """
        Build the attribute item.

        Args:
            stage: The stage.
            ui_attr: The attribute ui entry.
            prim_paths: The prim paths.

        Returns:
            The attribute item.
        """
        return super().build_property_item(stage, ui_attr, prim_paths)

    def _filter_attrs_to_build(self, attrs):
        """
        Filter the attributes to build.

        Args:
            attrs: The attributes.

        Returns:
            The filtered attributes.
        """
        return super()._filter_props_to_build(attrs)

    def _customize_attrs_layout(self, attrs):
        """
        Customize the attributes layout.

        Args:
            attrs: The attributes.

        Returns:
            The customized attributes.
        """
        return super()._customize_props_layout(attrs)

    def _get_shared_attributes_from_selected_prims(self, anchor_prim):
        """
        Get the shared attributes from the selected prims.

        Args:
            anchor_prim: The anchor prim.

        Returns:
            The shared attributes.
        """
        return super()._get_shared_properties_from_selected_prims(anchor_prim)

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        """
        Build the property item.

        Args:
            stage: The stage.
            ui_prop: The property ui entry.
            prim_paths: The prim paths.

        Returns:
            The property item.
        """
        return self.build_attribute_item(stage, ui_prop, prim_paths)

    def _filter_props_to_build(self, props):
        """
        Filter the properties to build.

        Args:
            props: The properties.

        Returns:
            The filtered properties.
        """
        return self._filter_attrs_to_build(props)

    def _customize_props_layout(self, props):
        """
        Customize the properties layout.

        Args:
            props: The properties.

        Returns:
            The customized properties.
        """
        return self._customize_attrs_layout(props)

    def _get_shared_properties_from_selected_prims(self, anchor_prim):
        """
        Get the shared properties from the selected prims.

        Args:
            anchor_prim: The anchor prim.

        Returns:
            The shared properties.
        """
        return self._get_shared_attributes_from_selected_prims(anchor_prim)


class MultiSchemaAttributesWidget(MultiSchemaPropertiesWidget):  # pragma: no cover
    """
    DEPRECATED! KEEP FOR BACKWARD COMPATIBILITY. Use MultiSchemaPropertiesWidget instead.

    MultiSchemaAttributesWidget filters attributes and only show the onces from a given IsA schema or schema subclass list.
    """

    def __init__(
        self, title: str, schema, schema_subclasses: list, include_list: list = None, exclude_list: list = None
    ):
        """
        Constructor.

        Args:
            title (str): Title of the widgets on the Collapsable Frame.
            schema: The USD IsA schema or applied API schema to filter attributes.
            schema_subclasses (list): list of subclasses
            include_list (list): list of additional schema named to add
            exclude_list (list): list of additional schema named to remove
        """
        super().__init__(title, schema, schema_subclasses, include_list, exclude_list)

    def build_attribute_item(self, stage, ui_attr: UsdAttributeUiEntry, prim_paths: List[Sdf.Path]):
        """
        Build the attribute item.

        Args:
            stage: The stage.
            ui_attr: The attribute ui entry.
            prim_paths: The prim paths.

        Returns:
            The attribute item.
        """
        return super().build_property_item(stage, ui_attr, prim_paths)

    def _filter_attrs_to_build(self, attrs):
        """
        Filter the attributes to build.

        Args:
            attrs: The attributes.

        Returns:
            The filtered attributes.
        """
        return super()._filter_props_to_build(attrs)

    def _customize_attrs_layout(self, attrs):
        """
        Customize the attributes layout.

        Args:
            attrs: The attributes.
        """
        return super()._customize_props_layout(attrs)

    def _get_shared_attributes_from_selected_prims(self, anchor_prim):
        """
        Get the shared attributes from the selected prims.

        Args:
            anchor_prim: The anchor prim.
        """
        return super()._get_shared_properties_from_selected_prims(anchor_prim)

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        """
        Build the property item.

        Args:
            stage: The stage.
            ui_prop: The property ui entry.
            prim_paths: The prim paths.
        """
        return self.build_attribute_item(stage, ui_prop, prim_paths)

    def _filter_props_to_build(self, props):
        """
        Filter the properties to build.

        Args:
            props: The properties.
        """
        return self._filter_attrs_to_build(props)

    def _customize_props_layout(self, props):
        """
        Customize the properties layout.

        Args:
            props: The properties.
        """
        return self._customize_attrs_layout(props)

    def _get_shared_properties_from_selected_prims(self, anchor_prim):
        """
        Get the shared properties from the selected prims.

        Args:
            anchor_prim: The anchor prim.
        """
        return self._get_shared_attributes_from_selected_prims(anchor_prim)
