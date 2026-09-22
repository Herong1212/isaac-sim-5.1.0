# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a builder class for constructing custom USD shading property models and UI elements, as well as a function to get the appropriate builder based on property metadata."""

__all__ = ["UsdShadeCustomModelsBuilder"]

from typing import List, Union

import omni.ui as ui
from omni.kit.property.usd.usd_property_widget import UsdPropertyUiEntry
from omni.kit.property.usd.usd_property_widget_builder import (
    UsdPropertiesWidgetBuilder,
    get_model_cls,
    get_model_kwargs,
)
from omni.kit.window.property.templates import HORIZONTAL_SPACING
from pxr import Sdf, Sdr, UsdShade

from .expression import CallExpressionModel
from .matrix import MdlMatrixAttributeModel
from .output import UsdShadeOutputModel


class UsdShadeCustomModelsBuilder:
    """A class responsible for constructing custom models for USD shading properties.

    This class includes methods that build custom UI components based on the shading attributes and metadata provided. These methods are used to generate UI elements like call expressions, matrices, outputs, and checkboxes that correspond to various USD shading property types. Each method is a class method, ensuring that direct instantiation of the class is not required to utilize the functionality.
    """

    @classmethod
    def call_expression_builder(
        cls,
        stage,
        attr_name,
        metadata,
        type_name,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """Builds and returns a CallExpressionModel for the given attribute.

        Args:
            stage: The stage to which the model belongs.
            attr_name (str): The name of the attribute for which the model is created.
            metadata (dict): Metadata associated with the attribute.
            type_name (str): The type name of the attribute.
            prim_paths (List[:obj:`Sdf.Path`]): List of paths to the primitives containing the attribute.
            additional_label_kwargs (Optional[dict]): Additional kwargs for the label creation.
            additional_widget_kwargs (Optional[dict]): Additional kwargs for the widget creation.

        Returns:
            :obj:`CallExpressionModel`: The created CallExpressionModel instance."""
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = UsdPropertiesWidgetBuilder.create_label(attr_name, metadata, additional_label_kwargs)

            model_kwargs = get_model_kwargs(additional_widget_kwargs)
            model_cls = get_model_cls(CallExpressionModel, additional_widget_kwargs)
            model = model_cls(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
            )

            widget_kwargs = {"model": model, "name": "models_readonly"}
            widget_kwargs.update(model_kwargs)

            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            with ui.ZStack():
                value_widget = ui.StringField(**widget_kwargs)
                value_widget.read_only = True
                value_widget.identifier = f"string_{attr_name}"
                mixed_overlay = UsdPropertiesWidgetBuilder.create_mixed_text_overlay(widget_model=model, model=model)

            UsdPropertiesWidgetBuilder.create_control_state(
                value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )

            return model

    @classmethod
    def matrix_builder(
        cls,
        stage,
        attr_name,
        metadata,
        type_name,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """Builds and returns a model for matrix attributes.

        Args:
            stage: The stage to which the model belongs.
            attr_name (str): The name of the attribute for which the model is created.
            metadata (dict): Metadata associated with the attribute.
            type_name (str): The type name of the attribute.
            prim_paths (List[:obj:`Sdf.Path`]): List of paths to the primitives containing the attribute.
            additional_label_kwargs (Optional[dict]): Additional kwargs for label creation.
            additional_widget_kwargs (Optional[dict]): Additional kwargs for widget creation.

        Returns:
            The created matrix attribute model."""

        import omni.UsdMdl as UsdMdl

        render_type = metadata[Sdr.PropertyMetadata.RenderType]
        dimensions = render_type.replace(UsdMdl.Types.Double, "").replace(UsdMdl.Types.Float, "").split("x")
        dimensions = [int(x) for x in dimensions]

        default_value = metadata[Sdf.AttributeSpec.CustomDataKey][Sdf.AttributeSpec.DefaultValueKey]
        if not default_value:
            default_value = [0.0] * dimensions[0] * dimensions[1]
            metadata[Sdf.AttributeSpec.CustomDataKey][Sdf.AttributeSpec.DefaultValueKey] = default_value

        model_cls = get_model_cls(MdlMatrixAttributeModel, additional_widget_kwargs)
        model = model_cls(stage, [path.AppendProperty(attr_name) for path in prim_paths], dimensions, False, metadata)

        return UsdPropertiesWidgetBuilder.matrix_builder(
            model,
            dimensions[0],
            stage,
            attr_name,
            metadata,
            prim_paths,
            additional_label_kwargs,
            additional_widget_kwargs,
        )

    @classmethod
    def outputs_builder(
        cls,
        stage,
        attr_name,
        metadata,
        type_name,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """For outputs create a string field with no value that is locked for editing.

        Args:
            stage: The stage to which the model belongs.
            attr_name (str): The name of the attribute for which the model is created.
            metadata (dict): Metadata associated with the attribute.
            type_name (str): The type name of the attribute.
            prim_paths (List[:obj:`Sdf.Path`]): List of paths to the primitives containing the attribute.
            additional_label_kwargs (Optional[dict]): Additional kwargs for label creation.
            additional_widget_kwargs (Optional[dict]): Additional kwargs for widget creation.

        Returns:
            :obj:`UsdShadeOutputModel`: The created UsdShadeOutputModel instance."""
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = UsdPropertiesWidgetBuilder.create_label(attr_name, metadata, additional_label_kwargs)

            model_kwargs = get_model_kwargs(additional_widget_kwargs)
            model_cls = get_model_cls(UsdShadeOutputModel, additional_widget_kwargs)
            model = model_cls(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
            )

            widget_kwargs = {"model": model, "name": "models_readonly"}
            widget_kwargs.update(model_kwargs)

            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            with ui.ZStack():
                value_widget = ui.StringField(**widget_kwargs)
                value_widget.identifier = f"string_{attr_name}"
                value_widget.read_only = True

            UsdPropertiesWidgetBuilder.create_control_state(label=label, **widget_kwargs)

            return model

    @classmethod
    def checkbox_builder(
        cls,
        stage,
        attr_name,
        metadata,
        type_name,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """Builds and returns a boolean property widget.

        Args:
            stage: The stage to which the model belongs.
            attr_name (str): The name of the attribute for which the model is created.
            metadata (dict): Metadata associated with the attribute.
            type_name (str): The type name of the attribute.
            prim_paths (List[:obj:`Sdf.Path`]): List of paths to the primitives containing the attribute.
            additional_label_kwargs (Optional[dict]): Additional kwargs for label creation.
            additional_widget_kwargs (Optional[dict]): Additional kwargs for widget creation."""
        return UsdPropertiesWidgetBuilder.bool_builder(
            stage, attr_name, type_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
        )


def get_custom_ui_prop_build_fn(ui_prop: UsdPropertyUiEntry) -> None:
    """Returns a function that builds custom UI property models based on the specified ui_prop.

    Args:
        ui_prop (:obj:`UsdPropertyUiEntry`): The UI property entry that contains metadata to determine the appropriate custom model builder function.

    Returns:
        Optional[Callable]: A function that is used to build a custom UI property model if a matching builder is found; otherwise, None.
    """

    import omni.UsdMdl as UsdMdl

    def get_widget_type(ui_prop: UsdPropertyUiEntry) -> Union[str | None]:
        """
        Find and return widget type from metadata if it exists.
        """

        widget = ui_prop.metadata.get("widget", None)
        if widget and widget != "default":
            return widget

        sdr_metadata = ui_prop.metadata.get(UsdShade.Tokens.sdrMetadata, {})
        annotation = sdr_metadata.get("annotation", {})
        annotation_widget_type = annotation.get("annotation_widget_type", {})
        return annotation_widget_type.get("s", None)

    # For outputs create a simple string widget that displays the outputs type.
    if ui_prop.prop_name.startswith(UsdShade.Tokens.outputs):
        return UsdShadeCustomModelsBuilder.outputs_builder

    if ui_prop.prop_name.startswith(UsdShade.Tokens.inputs):
        if UsdShade.Tokens.sdrMetadata in ui_prop.metadata:
            sdr_metadata = ui_prop.metadata[UsdShade.Tokens.sdrMetadata]
            expression_kind = sdr_metadata.get(UsdMdl.Metadata.ExpressionKind, None)

            if expression_kind == UsdMdl.ExpressionKinds.Call:
                return UsdShadeCustomModelsBuilder.call_expression_builder

        type_name = ui_prop.metadata.get(Sdf.PrimSpec.TypeNameKey, None)

        if type_name == Sdf.ValueTypeNames.Int:
            widget_type = get_widget_type(ui_prop)
            if widget_type == "checkBox":
                return UsdShadeCustomModelsBuilder.checkbox_builder

        render_type = ui_prop.metadata.get(Sdr.PropertyMetadata.RenderType, None)

        # non-uniform and float matrices.
        if render_type in [
            UsdMdl.Types.Double2x3,
            UsdMdl.Types.Double2x4,
            UsdMdl.Types.Double3x2,
            UsdMdl.Types.Double3x4,
            UsdMdl.Types.Double4x2,
            UsdMdl.Types.Double4x3,
            UsdMdl.Types.Float2x2,
            UsdMdl.Types.Float2x3,
            UsdMdl.Types.Float2x4,
            UsdMdl.Types.Float3x2,
            UsdMdl.Types.Float3x3,
            UsdMdl.Types.Float3x4,
            UsdMdl.Types.Float4x2,
            UsdMdl.Types.Float4x3,
            UsdMdl.Types.Float4x4,
        ]:

            return UsdShadeCustomModelsBuilder.matrix_builder

    return None
