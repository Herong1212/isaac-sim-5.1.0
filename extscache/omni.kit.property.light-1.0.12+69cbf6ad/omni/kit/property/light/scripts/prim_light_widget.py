# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides a widget for editing USD light schema attributes in the Omniverse Kit user interface."""


from typing import Set

import carb
from omni.kit.property.usd.usd_property_widget import (
    MultiSchemaPropertiesWidget,
    UsdPropertyUiEntry,
    create_primspec_bool,
)
from pxr import Usd, UsdLux

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class LightSchemaAttributesWidget(MultiSchemaPropertiesWidget):
    """A widget for editing light schema attributes in a user interface.

    This widget is designed to work with USD's lighting schemas, allowing for the manipulation of various light attributes such as color, intensity, and shadow properties. It supports a range of light types including dome, disk, rect, sphere, and cylinder lights. Custom schema attributes can also be added for more specialized control over USD light properties.

    Args:
        title (str): Title of the widgets on the Collapsable Frame.
        schema: The USD IsA schema or applied API schema to filter attributes.
        schema_subclasses (list): List of subclasses to include.
        include_list (list, optional): List of additional schema names to add.
        exclude_list (list, optional): List of additional schema names to remove.
        locked_types (list): List of prim types that are to be NO_REMOVE."""

    def __init__(
        self,
        title: str,
        schema,
        schema_subclasses: list,
        include_list: list = None,
        exclude_list: list = None,
        locked_types: list = None,
    ):
        """Initializes a new instance of LightSchemaAttributesWidget."""
        from omni.kit.property.usd import RegisteredSchemaCodes, register_schema

        super().__init__(title, schema, schema_subclasses, include_list, exclude_list, group_api_schemas=True)

        self._settings = carb.settings.get_settings()
        self._setting_path = PERSISTENT_SETTINGS_PREFIX + "/app/usd/usdLuxUnprefixedCompat"
        self._subscription = self._settings.subscribe_to_node_change_events(self._setting_path, self._on_change)
        self._usd_lux_unprefixed_compat = ""

        # these APIs cannot be removed from lights, so will appear locked
        register_schema(
            self.__class__.__name__,
            ["LightAPI", "CollectionAPI:lightLink", "CollectionAPI:shadowLink"],
            RegisteredSchemaCodes.NO_REMOVE,
        )

        for prim_type in locked_types if locked_types else []:
            register_schema(
                prim_type,
                ["LightAPI", "CollectionAPI:lightLink", "CollectionAPI:shadowLink"],
                RegisteredSchemaCodes.NO_REMOVE,
            )

        self.lux_attributes: Set[str] = set(
            {
                "inputs:angle",
                "inputs:color",
                "inputs:temperature",
                "inputs:diffuse",
                "inputs:specular",
                "inputs:enableColorTemperature",
                "inputs:exposure",
                "inputs:height",
                "inputs:width",
                "inputs:intensity",
                "inputs:length",
                "inputs:normalize",
                "inputs:radius",
                "inputs:shadow:color",
                "inputs:shadow:distance",
                "inputs:shadow:enable",
                "inputs:shadow:falloff",
                "inputs:shadow:falloffGamma",
                "inputs:shaping:cone:angle",
                "inputs:shaping:cone:softness",
                "inputs:shaping:focus",
                "inputs:shaping:focusTint",
                "inputs:shaping:ies:angleScale",
                "inputs:shaping:ies:file",
                "inputs:shaping:ies:normalize",
                "inputs:texture:format",
            }
        )

        # custom attributes
        def is_prim_light_primary_visible_supported(prim):
            return (
                prim.IsA(UsdLux.DomeLight)
                or prim.IsA(UsdLux.DiskLight)
                or prim.IsA(UsdLux.RectLight)
                or prim.IsA(UsdLux.SphereLight)
                or prim.IsA(UsdLux.CylinderLight)
                or prim.IsA(UsdLux.DistantLight)
            )

        def is_prim_light_disable_fog_interaction_supported(prim):
            return (
                prim.IsA(UsdLux.DomeLight)
                or prim.IsA(UsdLux.DiskLight)
                or prim.IsA(UsdLux.RectLight)
                or prim.IsA(UsdLux.SphereLight)
                or prim.IsA(UsdLux.CylinderLight)
                or prim.IsA(UsdLux.DistantLight)
            )

        def is_prim_light_caustics_supported(prim):
            return prim.IsA(UsdLux.DiskLight) or prim.IsA(UsdLux.RectLight) or prim.IsA(UsdLux.SphereLight)

        def is_prim_light_is_projector_supported(prim):
            return prim.IsA(UsdLux.RectLight)

        def add_vipr(attribute_name, value_dict):
            anchor_prim = self._get_prim(self._payload[-1])
            if anchor_prim and (anchor_prim.IsA(UsdLux.DomeLight) or anchor_prim.IsA(UsdLux.DistantLight)):
                return UsdPropertyUiEntry("visibleInPrimaryRay", "", create_primspec_bool(True), Usd.Attribute)
            return UsdPropertyUiEntry("visibleInPrimaryRay", "", create_primspec_bool(False), Usd.Attribute)

        self.add_custom_schema_attribute(
            "visibleInPrimaryRay", is_prim_light_primary_visible_supported, add_vipr, "", {}
        )
        self.add_custom_schema_attribute(
            "disableFogInteraction",
            is_prim_light_disable_fog_interaction_supported,
            None,
            "",
            create_primspec_bool(False),
        )
        self.add_custom_schema_attribute(
            "light:enableCaustics", is_prim_light_caustics_supported, None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "isProjector", is_prim_light_is_projector_supported, None, "", create_primspec_bool(False)
        )

    def _on_change(self, item, event_type):
        self.request_rebuild()

    def on_new_payload(self, payload):
        """Handles a new payload for the widget.

        Args:
            payload (:obj:'PrimSelectionPayload'): The new payload to be handled by the widget.

        Returns:
            bool: False if the payload is not handled, otherwise a list of used attributes."""
        if not super().on_new_payload(payload):
            return False

        if not self._payload or len(self._payload) == 0:
            return False

        used = []
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
            if self._schema().IsTyped() and not prim.IsA(self._schema):
                return False
            if self._schema().IsAPISchema() and not prim.HasAPI(self._schema):
                return False
            used += [
                attr
                for attr in prim.GetAttributes()
                if attr.GetName() in self._schema_attr_names and not attr.IsHidden()
            ]

            if self.is_custom_schema_attribute_used(prim):
                used.append(None)

        return used

    def has_authored_inputs_attr(self, prim):
        """Checks if given prim has authored input attributes.

        Args:
            prim (:obj:`Usd.Prim`): The USD primitive to check for authored input attributes.

        Returns:
            bool: True if any authored input attributes are found, False otherwise."""
        attrs = set({a.GetName() for a in prim.GetAuthoredAttributes()})
        any_authored = attrs.intersection(self.lux_attributes)
        return any_authored

    def show_schemas(self):
        return True

    def _customize_props_layout(self, attrs):
        from omni.kit.property.usd.custom_layout_helper import (
            CustomLayoutFrame,
            CustomLayoutGroup,
            CustomLayoutProperty,
        )

        self.add_custom_schema_attributes_to_props(attrs)

        frame = CustomLayoutFrame(hide_extra=False)
        anchor_prim = self._get_prim(self._payload[-1])

        # TODO -
        # add shadow values (Shadow Enable, Shadow Include, Shadow Exclude, Shadow Color, Shadow Distance, Shadow Falloff, Shadow Falloff Gamma)
        # add UsdLux.DomeLight portals (see UsdLux.DomeLight GetPortalsRel)
        # add filters (see UsdLux.Light / UsdLux.LightAPI	GetFiltersRel)

        self._usd_lux_unprefixed_compat = self._settings.get(
            PERSISTENT_SETTINGS_PREFIX + "/app/usd/usdLuxUnprefixedCompat"
        )
        has_authored_inputs = self.has_authored_inputs_attr(anchor_prim)

        # remove unsupported attrs
        for item in [attr for attr in attrs if attr.prop_name in self._schema_exclude_list]:
            attrs.remove(item)

        with frame:
            with CustomLayoutGroup("Main"):
                self._create_property("color", "Color", anchor_prim, has_authored_inputs)
                self._create_property(
                    "enableColorTemperature", "Enable Color Temperature", anchor_prim, has_authored_inputs
                )
                self._create_property("colorTemperature", "Color Temperature", anchor_prim, has_authored_inputs)
                self._create_property("intensity", "Intensity", anchor_prim, has_authored_inputs)
                self._create_property("exposure", "Exposure", anchor_prim, has_authored_inputs)
                self._create_property("normalize", "Normalize Power", anchor_prim, has_authored_inputs)

                if anchor_prim and anchor_prim.IsA(UsdLux.DistantLight):
                    self._create_property("angle", "Angle", anchor_prim, has_authored_inputs)

                if anchor_prim and anchor_prim.IsA(UsdLux.DiskLight):
                    self._create_property("radius", "Radius", anchor_prim, has_authored_inputs)

                if anchor_prim and anchor_prim.IsA(UsdLux.RectLight):
                    self._create_property("height", "Height", anchor_prim, has_authored_inputs)
                    self._create_property("width", "Width", anchor_prim, has_authored_inputs)
                    self._create_property("texture:file", "Texture File", anchor_prim, has_authored_inputs)

                if anchor_prim and anchor_prim.IsA(UsdLux.SphereLight):
                    self._create_property("radius", "Radius", anchor_prim, has_authored_inputs)
                    CustomLayoutProperty("treatAsPoint", "Treat As Point")

                if anchor_prim and anchor_prim.IsA(UsdLux.CylinderLight):
                    self._create_property("length", "Length", anchor_prim, has_authored_inputs)
                    self._create_property("radius", "Radius", anchor_prim, has_authored_inputs)
                    CustomLayoutProperty("treatAsLine", "Treat As Line")

                if anchor_prim and anchor_prim.IsA(UsdLux.DomeLight):
                    self._create_property("texture:file", "Texture File", anchor_prim, has_authored_inputs)
                    self._create_property("texture:format", "Texture Format", anchor_prim, has_authored_inputs)

                self._create_property("diffuse", "Diffuse Multiplier", anchor_prim, has_authored_inputs)
                self._create_property("specular", "Specular Multiplier", anchor_prim, has_authored_inputs)
                CustomLayoutProperty("visibleInPrimaryRay", "Visible In Primary Ray")
                CustomLayoutProperty("disableFogInteraction", "Disable Fog Interaction")
                CustomLayoutProperty("light:enableCaustics", "Enable Caustics")
                CustomLayoutProperty("isProjector", "Projector light type")

            with CustomLayoutGroup("Shaping", collapsed=True):
                self._create_property("shaping:focus", "Focus", anchor_prim, has_authored_inputs)
                self._create_property("shaping:focusTint", "Focus Tint", anchor_prim, has_authored_inputs)
                self._create_property("shaping:cone:angle", "Cone Angle", anchor_prim, has_authored_inputs)
                self._create_property("shaping:cone:softness", "Cone Softness", anchor_prim, has_authored_inputs)
                self._create_property("shaping:ies:file", "File", anchor_prim, has_authored_inputs)
                self._create_property("shaping:ies:angleScale", "AngleScale", anchor_prim, has_authored_inputs)
                self._create_property("shaping:ies:normalize", "Normalize", anchor_prim, has_authored_inputs)

            with CustomLayoutGroup("Light Link"):
                CustomLayoutProperty("collection:lightLink:includeRoot", "Light Link Include Root")
                CustomLayoutProperty("collection:lightLink:expansionRule", "Light Link Expansion Rule")
                CustomLayoutProperty("collection:lightLink:includes", "Light Link Includes")
                CustomLayoutProperty("collection:lightLink:excludes", "Light Link Excludes")

            with CustomLayoutGroup("Shadow Link"):
                CustomLayoutProperty("collection:shadowLink:includeRoot", "Shadow Link Include Root")
                CustomLayoutProperty("collection:shadowLink:expansionRule", "Shadow Link Expansion Rule")
                CustomLayoutProperty("collection:shadowLink:includes", "Shadow Link Includes")
                CustomLayoutProperty("collection:shadowLink:excludes", "Shadow Link Excludes")

            with CustomLayoutGroup("Internal"):
                CustomLayoutProperty("light:filters", "Filters")
                CustomLayoutProperty("light:shaderId", "Shader ID")

        return frame.apply(attrs)

    def _create_property(self, name: str, display_name: str, prim, has_authored_inputs):
        from omni.kit.property.usd.custom_layout_helper import CustomLayoutProperty

        if has_authored_inputs or not self._usd_lux_unprefixed_compat or not prim.HasAttribute(name):
            prefixed_name = "inputs:" + name
            return CustomLayoutProperty(prefixed_name, display_name)

        return CustomLayoutProperty(name, display_name)
