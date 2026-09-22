# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from dataclasses import dataclass
from typing import Any, Callable, List, OrderedDict

import omni.ui as ui
import omni.usd
from omni.kit.property.adapter.core import StageAdapter
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_property_widget import (
    MultiSchemaPropertiesWidget,
    UsdPropertyUiEntry,
    create_primspec_bool,
    create_primspec_int,
)
from pxr import Sdf, Usd, UsdGeom


class GeometrySchemaAttributesWidget(MultiSchemaPropertiesWidget):
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
        super().__init__(title, schema, schema_subclasses, include_list, exclude_list, group_api_schemas=True)

        # custom attributes
        self.add_custom_schema_attribute(
            "primvars:enableFastRefractionShadow", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:doNotCastShadows", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:enableShadowTerminatorFix", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(True)
        )
        self.add_custom_schema_attribute(
            "primvars:holdoutObject", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:invisibleToSecondaryRays", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:isMatteObject", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:isVolume", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:multimatte_id", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_int(-1)
        )
        self.add_custom_schema_attribute(
            "primvars:disableRtSssTransmission", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:disableAutoLod", lambda p: p.IsA(UsdGeom.Gprim), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:numSplitsOverride", lambda p: p.IsA(UsdGeom.BasisCurves), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "primvars:numSplits", lambda p: p.IsA(UsdGeom.BasisCurves), None, "", create_primspec_int(2)
        )
        self.add_custom_schema_attribute(
            "primvars:endcaps", lambda p: p.IsA(UsdGeom.BasisCurves), None, "", create_primspec_int(1)
        )
        self.add_custom_schema_attribute(
            "primvars:framesBetweenBvhRebuilds", lambda p: p.IsA(UsdGeom.BasisCurves), None, "", create_primspec_int(-1)
        )
        self.add_custom_schema_attribute(
            "refinementEnableOverride", self._is_prim_refinement_level_supported, None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "refinementLevel", self._is_prim_refinement_level_supported, None, "", create_primspec_int(0)
        )
        self._add_curves = False
        self._add_points = False

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """

        self._add_curves = False
        self._add_points = False

        if not super().on_new_payload(payload):
            return False  # pragma: no cover

        if not self._payload or len(self._payload) == 0:
            return False  # pragma: no cover

        used = []
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            if not prim or not prim.IsA(self._schema):
                return False  # pragma: no cover
            used += [
                attr
                for attr in prim.GetProperties()
                if attr.GetName() in self._schema_attr_names and not attr.IsHidden()
            ]

            if prim.IsA(UsdGeom.BasisCurves):
                self._add_curves = True
            elif prim.IsA(UsdGeom.Points):
                self._add_points = True

            if self.is_custom_schema_attribute_used(prim):
                used.append(None)

        return used

    def show_schemas(self):
        return True

    def _is_prim_refinement_level_supported(self, prim):
        return (
            prim.IsA(UsdGeom.Mesh)
            or prim.IsA(UsdGeom.Cylinder)
            or prim.IsA(UsdGeom.Capsule)
            or prim.IsA(UsdGeom.Cone)
            or prim.IsA(UsdGeom.Sphere)
            or prim.IsA(UsdGeom.Cube)
        )

    def _customize_props_layout(self, attrs):
        self.add_custom_schema_attributes_to_props(attrs)

        frame = CustomLayoutFrame(hide_extra=False)
        with frame:

            def update_bounds(stage, prim_paths):
                valid_stage = omni.usd.get_context().get_stage() if isinstance(stage, StageAdapter) else stage

                timeline = omni.timeline.get_timeline_interface()
                current_time = timeline.get_current_time()
                current_time_code = Usd.TimeCode(
                    omni.usd.get_frame_time_code(current_time, valid_stage.GetTimeCodesPerSecond())
                )

                for path in prim_paths:
                    prim = valid_stage.GetPrimAtPath(path)
                    if prim:
                        attr = prim.GetAttribute("extent")
                        if attr:
                            bounds = UsdGeom.Boundable.ComputeExtentFromPlugins(
                                UsdGeom.Boundable(prim), current_time_code
                            )
                            attr.Set(bounds)

            def build_extent_func(
                stage,
                attr_name,
                metadata,
                property_type,
                prim_paths: List[Sdf.Path],
                additional_label_kwargs=None,
                additional_widget_kwargs=None,
            ):
                from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
                from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
                from omni.kit.property.usd.widgets import ICON_PATH
                from omni.kit.window.property.templates import HORIZONTAL_SPACING

                if not attr_name or not property_type:  # pragma: no cover
                    return None

                def value_changed_func(model, widget):
                    val = model.get_value_as_string()
                    widget.set_tooltip(val)

                with ui.HStack(spacing=HORIZONTAL_SPACING):
                    model = UsdAttributeModel(
                        stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
                    )
                    UsdPropertiesWidgetBuilder.create_label(attr_name, metadata, additional_label_kwargs)
                    kwargs = {
                        "name": "models_readonly",
                        "model": model,
                        "enabled": False,
                        "tooltip": model.get_value_as_string(),
                    }
                    if additional_widget_kwargs:  # pragma: no cover
                        kwargs.update(additional_widget_kwargs)
                    with ui.ZStack():
                        value_widget = ui.StringField(**kwargs)
                        UsdPropertiesWidgetBuilder.create_mixed_text_overlay()

                    ui.Spacer(width=0)
                    with ui.VStack(width=8):
                        ui.Spacer()
                        ui.Image(
                            f"{ICON_PATH}/Default value.svg",
                            width=5.5,
                            height=5.5,
                        )
                        ui.Spacer()

                    model.add_value_changed_fn(lambda m, w=value_widget: value_changed_func(m, w))
                    return model

            def build_size_func(
                stage,
                attr_name,
                metadata,
                property_type,
                prim_paths: List[Sdf.Path],
                additional_label_kwargs=None,
                additional_widget_kwargs=None,
            ):
                from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
                from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
                from omni.kit.window.property.templates import HORIZONTAL_SPACING

                if not attr_name or not property_type:
                    return None

                with ui.HStack(spacing=HORIZONTAL_SPACING):
                    model_kwargs = UsdPropertiesWidgetBuilder.get_attr_value_range_kwargs(metadata)
                    model = UsdAttributeModel(
                        stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
                    )
                    UsdPropertiesWidgetBuilder.create_label(attr_name, metadata, additional_label_kwargs)
                    widget_kwargs = {"model": model}
                    widget_kwargs.update(UsdPropertiesWidgetBuilder.get_attr_value_soft_range_kwargs(metadata))
                    if additional_widget_kwargs:  # pragma: no cover
                        widget_kwargs.update(additional_widget_kwargs)
                    with ui.ZStack():
                        value_widget = UsdPropertiesWidgetBuilder.create_drag_or_slider(
                            ui.FloatDrag, ui.FloatSlider, **widget_kwargs
                        )
                        mixed_overlay = UsdPropertiesWidgetBuilder.create_mixed_text_overlay()
                    UsdPropertiesWidgetBuilder.create_control_state(
                        value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs
                    )
                    model.add_value_changed_fn(lambda m, s=stage, p=prim_paths: update_bounds(s, p))

                    return model

            def build_axis_func(
                stage,
                attr_name,
                metadata,
                property_type,
                prim_paths: List[Sdf.Path],
                additional_label_kwargs=None,
                additional_widget_kwargs=None,
            ):
                from omni.kit.property.usd.usd_attribute_model import TfTokenAttributeModel, UsdAttributeModel
                from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
                from omni.kit.window.property.templates import HORIZONTAL_SPACING

                if not attr_name or not property_type:  # pragma: no cover
                    return None

                with ui.HStack(spacing=HORIZONTAL_SPACING):
                    model = None
                    UsdPropertiesWidgetBuilder.create_label(attr_name, metadata, additional_label_kwargs)
                    tokens = metadata.get("allowedTokens")
                    if tokens is not None and len(tokens) > 0:
                        model = TfTokenAttributeModel(
                            stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
                        )
                        widget_kwargs = {"name": "choices"}
                        if additional_widget_kwargs:  # pragma: no cover
                            widget_kwargs.update(additional_widget_kwargs)
                        with ui.ZStack():
                            value_widget = ui.ComboBox(model, **widget_kwargs)
                            mixed_overlay = UsdPropertiesWidgetBuilder.create_mixed_text_overlay()
                        model.add_item_changed_fn(lambda m, i, s=stage, p=prim_paths: update_bounds(s, p))
                    else:
                        model = UsdAttributeModel(
                            stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
                        )
                        widget_kwargs = {"name": "models"}
                        if additional_widget_kwargs:  # pragma: no cover
                            widget_kwargs.update(additional_widget_kwargs)
                        with ui.ZStack():
                            value_widget = ui.StringField(model, **widget_kwargs)
                            mixed_overlay = UsdPropertiesWidgetBuilder.create_mixed_text_overlay()
                        model.add_value_changed_fn(lambda m, s=stage, p=prim_paths: update_bounds(s, p))

                    UsdPropertiesWidgetBuilder.create_control_state(
                        model=model, value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs
                    )

                    return model

            def build_endcaps_func(
                stage,
                attr_name,
                metadata,
                property_type,
                prim_paths: List[Sdf.Path],
                additional_label_kwargs=None,
                additional_widget_kwargs=None,
            ):
                from omni.kit.property.usd.usd_attribute_model import MdlEnumAttributeModel, OptionItem
                from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
                from omni.kit.window.property.templates import HORIZONTAL_SPACING

                if not attr_name or not property_type:  # pragma: no cover
                    return None

                with ui.HStack(spacing=HORIZONTAL_SPACING):
                    model = None
                    UsdPropertiesWidgetBuilder.create_label(attr_name, metadata, additional_label_kwargs)

                    class EndcapsAttributeModel(MdlEnumAttributeModel):
                        option_names = ["open", "flat", "round"]

                        def __init__(
                            self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict
                        ):
                            super().__init__(stage, attribute_paths, self_refresh, metadata)
                            self._options = []
                            for i, v in enumerate(self.option_names):
                                self._options.append(OptionItem(v, i))

                            self._current_index.set_value(self._value)

                        def _update_option(self):
                            pass

                    model = EndcapsAttributeModel(
                        stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
                    )

                    widget_kwargs = {"name": "choices"}
                    if additional_widget_kwargs:  # pragma: no cover
                        widget_kwargs.update(additional_widget_kwargs)
                    with ui.ZStack():
                        value_widget = ui.ComboBox(model, **widget_kwargs)
                        mixed_overlay = UsdPropertiesWidgetBuilder.create_mixed_text_overlay()
                    UsdPropertiesWidgetBuilder.create_control_state(
                        model=model, value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs
                    )
                    return model

            if self._add_curves:
                with CustomLayoutGroup("Curve"):
                    CustomLayoutProperty("curveVertexCounts", "Per curve points")
                    CustomLayoutProperty("points", "Points")
                    CustomLayoutProperty("normals", "Normals")
                    CustomLayoutProperty("widths", "Widths")
                    CustomLayoutProperty("type", "Type")
                    CustomLayoutProperty("basis", "Basis")
                    CustomLayoutProperty("wrap", "Wrap")
                    CustomLayoutProperty("primvars:numSplitsOverride", "Number of BVH splits Override")
                    CustomLayoutProperty("primvars:numSplits", "Number of BVH splits")
                    CustomLayoutProperty("primvars:endcaps", "Endcaps", build_fn=build_endcaps_func)
                    CustomLayoutProperty("primvars:framesBetweenBvhRebuilds", "Frames Between BVH Rebuilds")

            if self._add_points:
                with CustomLayoutGroup("Points"):
                    CustomLayoutProperty("points", "Points")
                    CustomLayoutProperty("normals", "Normals")
                    CustomLayoutProperty("widths", "Widths")

            common_section_name = "Mesh"
            if self._add_curves or self._add_points:
                common_section_name = "Common"
            with CustomLayoutGroup(common_section_name):
                CustomLayoutProperty("normals", "Normals")
                CustomLayoutProperty("orientation", "Orientation")
                CustomLayoutProperty("points", "Points")
                CustomLayoutProperty("velocities", "Velocities")
                CustomLayoutProperty("accelerations", "Accelerations")
                CustomLayoutProperty("extent", "Extent", build_fn=build_extent_func)
                CustomLayoutProperty("size", "Size", build_fn=build_size_func)
                CustomLayoutProperty("radius", "Radius", build_fn=build_size_func)
                CustomLayoutProperty("axis", "Axis", build_fn=build_axis_func)
                CustomLayoutProperty("height", "Height", build_fn=build_size_func)
                CustomLayoutProperty("polymesh:parameterCheck", "Parameter Check")
                CustomLayoutProperty("primvars:doNotCastShadows", "Cast Shadows", build_fn=self._inverse_bool_builder)
                CustomLayoutProperty("primvars:enableShadowTerminatorFix", "Shadow Terminator Fix")
                CustomLayoutProperty("primvars:enableFastRefractionShadow", "Fast Refraction Shadow")
                CustomLayoutProperty(
                    "primvars:disableRtSssTransmission",
                    "Enable Rt SSS Transmission",
                    build_fn=self._inverse_bool_builder,
                )
                CustomLayoutProperty(
                    "primvars:disableAutoLod",
                    "Enable automatic LOD generation for geometry streaming",
                    build_fn=self._inverse_bool_builder,
                )
                CustomLayoutProperty("primvars:holdoutObject", "Holdout Object")
                CustomLayoutProperty("primvars:invisibleToSecondaryRays", "Invisible To Secondary Rays")
                CustomLayoutProperty("primvars:isMatteObject", "Matte Object")
                CustomLayoutProperty("primvars:isVolme", "Is Volume")
                CustomLayoutProperty("primvars:multimatte_id", "Multimatte ID")

            with CustomLayoutGroup("Face"):
                CustomLayoutProperty("faceVertexIndices", "Indices")
                CustomLayoutProperty("faceVertexCounts", "Counts")
                CustomLayoutProperty("faceVaryingLinearInterpolation", "Linear Interpolation")
                CustomLayoutProperty("holeIndices", "Hole Indices")

            with CustomLayoutGroup("Refinement"):
                CustomLayoutProperty("refinementEnableOverride", "Refinement Override")
                CustomLayoutProperty("refinementLevel", "Refinement Level")
                CustomLayoutProperty("interpolateBoundary", "Interpolate Boundary")
                CustomLayoutProperty("subdivisionScheme", "Subdivision Scheme")
                CustomLayoutProperty("triangleSubdivisionRule", "Triangle SubdivisionRule")

            with CustomLayoutGroup("Corner"):
                CustomLayoutProperty("cornerIndices", "Indices")
                CustomLayoutProperty("cornerSharpnesses", "Sharpnesses")

            with CustomLayoutGroup("Crease"):
                CustomLayoutProperty("creaseIndices", "Indices")
                CustomLayoutProperty("creaseLengths", "Lengths")
                CustomLayoutProperty("creaseSharpnesses", "Sharpnesses")

        return frame.apply(attrs)

    def get_additional_kwargs(self, ui_prop: UsdPropertyUiEntry):
        """
        Override this function if you want to supply additional arguments when building the label or ui widget.
        """
        additional_widget_kwargs = None
        if ui_prop.prop_name == "refinementLevel":
            additional_widget_kwargs = {"min": 0, "max": 5}
        return None, additional_widget_kwargs

    def _inverse_bool_builder(
        self,
        stage,
        attr_name,
        metadata,
        property_type,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        import carb.settings
        from omni.kit.property.usd.usd_attribute_model import UsdAttributeInvertedModel
        from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
        from omni.kit.window.property.templates import HORIZONTAL_SPACING

        if not attr_name or not property_type:  # pragma: no cover
            return None

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            model = UsdAttributeInvertedModel(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
            )
            settings = carb.settings.get_settings()
            left_aligned = settings.get("ext/omni.kit.window.property/checkboxAlignment") == "left"

            if not left_aligned:  # pragma: no cover
                if not additional_label_kwargs:
                    additional_label_kwargs = {}
                additional_label_kwargs["width"] = 0
            UsdPropertiesWidgetBuilder.create_label(attr_name, metadata, additional_label_kwargs)
            if not left_aligned:  # pragma: no cover
                ui.Spacer(width=10)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1))
                ui.Spacer(width=5)
            with ui.VStack(width=10):
                ui.Spacer()
                widget_kwargs = {"width": 10, "height": 0, "name": "greenCheck", "model": model}
                if additional_widget_kwargs:  # pragma: no cover
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    with ui.Placer(offset_x=0, offset_y=-2):
                        value_widget = ui.CheckBox(**widget_kwargs)
                    with ui.Placer(offset_x=1, offset_y=-1):
                        mixed_overlay = ui.Rectangle(
                            height=8, width=8, name="mixed_overlay", alignment=ui.Alignment.CENTER, visible=False
                        )
                ui.Spacer()
            if left_aligned:
                ui.Spacer(width=5)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1))
            UsdPropertiesWidgetBuilder.create_control_state(
                value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs
            )
            return model


@dataclass(frozen=True)
class CustomAttributeInfo:
    schema_name: str
    display_name: str
    type_name: str
    default_value: Any
    predicate: Callable[[Any], bool] = None

    def is_supported(self, prim):
        return self.predicate is None or self.predicate(prim)

    def get_metadata(self):
        return {Sdf.PrimSpec.TypeNameKey: self.type_name, "customData": {"default": self.default_value}}


class ImageableSchemaAttributesWidget(MultiSchemaPropertiesWidget):
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
        self._custom_attributes: OrderedDict[str, CustomAttributeInfo] = OrderedDict()
        self._custom_placeholders: List[str] = []

        # custom attributes
        self.add_custom_schema_attribute(
            "singleSided", self._is_prim_single_sided_supported, None, "", create_primspec_bool(False)
        )

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """
        self._custom_placeholders.clear()
        if not super().on_new_payload(payload):
            return False  # pragma: no cover

        if not self._payload or len(self._payload) == 0:
            return False  # pragma: no cover

        used = []
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            if not prim or not prim.IsA(self._schema):
                return False  # pragma: no cover
            used += [
                attr
                for attr in prim.GetProperties()
                if attr.GetName() in self._schema_attr_names and not attr.IsHidden()
            ]

            for schema_name, attr_info in self._custom_attributes.items():
                if attr_info.is_supported(prim) and not prim.GetAttribute(schema_name):
                    self._custom_placeholders.append(schema_name)
                    used.append(None)

            if self.is_custom_schema_attribute_used(prim):
                used.append(None)

        return used

    def add_custom_attribute(
        self,
        attribute_name,
        display_name,
        type_name="bool",
        default_value=False,
        predicate: Callable[[Any], bool] = None,
    ):
        """
        Add custom attribute with placeholder.
        """
        self._schema_attr_base.add(attribute_name)
        self._custom_attributes.update(
            {attribute_name: CustomAttributeInfo(attribute_name, display_name, type_name, default_value, predicate)}
        )

        self.request_rebuild()

    def remove_custom_attribute(self, attribute_name):
        self._schema_attr_base.remove(attribute_name)
        del self._custom_attributes[attribute_name]
        self.request_rebuild()

    def _is_prim_single_sided_supported(self, prim):
        return (
            prim.IsA(UsdGeom.Mesh)
            or prim.IsA(UsdGeom.Cylinder)
            or prim.IsA(UsdGeom.Capsule)
            or prim.IsA(UsdGeom.Cone)
            or prim.IsA(UsdGeom.Sphere)
            or prim.IsA(UsdGeom.Cube)
        )

    def _customize_props_layout(self, attrs):
        self.add_custom_schema_attributes_to_props(attrs)
        for schema_name, attr_info in self._custom_attributes.items():
            if schema_name in self._custom_placeholders:
                attrs.append(
                    UsdPropertyUiEntry(
                        schema_name,
                        "",
                        attr_info.get_metadata(),
                        Usd.Attribute,
                    )
                )

        frame = CustomLayoutFrame(hide_extra=False)
        with frame:
            for schema_name, attr_info in self._custom_attributes.items():
                CustomLayoutProperty(schema_name, attr_info.display_name)

            CustomLayoutProperty("doubleSided", "Double Sided")
            CustomLayoutProperty("singleSided", "Single Sided")
            CustomLayoutProperty("purpose", "Purpose")
            CustomLayoutProperty("visibility", "Visibility")
            CustomLayoutProperty("primvars:displayColor", "Display Color")
            CustomLayoutProperty("primvars:displayOpacity", "Display Opacity")

        return frame.apply(attrs)
