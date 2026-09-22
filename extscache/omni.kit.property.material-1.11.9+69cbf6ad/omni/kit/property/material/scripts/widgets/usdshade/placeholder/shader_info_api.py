# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ShaderInfoAPI"]

import ast
import math
from typing import Any, List, Optional, Type, Union

import carb
from omni.kit.window.preferences import PERSISTENT_SETTINGS_PREFIX
from pxr import Sdf, Sdr, Usd, UsdShade

from ..input_placeholder_attribute import UsdShadeInputPlaceholderAttribute
from ..utils import deep_dict_update, get_sdr_shader_node_for_prim, get_sdr_shader_property_default_value
from .placeholder import UsdShadePropertyPlaceholder


class ShaderInfoAPI:
    """
    An API for querying the properties for a UsdShade prim.

    If the prim is of type UsdShade.Nodegraph, the input/output properties of the prim are returned.

    If the prim is of type UsdShade.Shader
        1. Properties are first gathered from the Sdr registry from the underlying Sdr.ShaderNode
        2. In the case where the property exists on the UsdShade.Shader prim it's metadata is over'd with the metadata returned from the SDR.

    The returned properties are UsdShadePropertyPlaceholder objects.  This allows consumers of this API to iterate over a UsdShade prims properties without having to make a distinction
    between whether the property is one that exists on the stage (UsdAttribute) vs a Sdr.ShaderProperty.

    ToDo: it might make sense to put this into UsdMdl or even AoUsd to provide a means for a user to query all of the parmeters on a shader
      right now someone would need to do this in two parts:
      1. Using the UsdShade API's - this would return only those parameters that have an underlying property on the stage.
      2. Using the SDR API's - this returns information on all of the available parameters.
    """

    MDL_FORCE_RAW_SETTING_PATH = PERSISTENT_SETTINGS_PREFIX + "/app/properties/material/mdlForceRawForUsage"
    RENDER_CONTEXTS_SETTING_PATH = PERSISTENT_SETTINGS_PREFIX + "/app/hydra/material/renderContexts"

    def __init__(self, prim: Usd.Prim, overlay_property_metadata: Optional[bool] = True):
        self._prim = prim
        self._overlay_property_metadata = overlay_property_metadata
        self._prim_path = prim.GetPath()
        self._prim_properties_metadata = {p.GetName(): p.GetAllMetadata() for p in prim.GetProperties()}
        self._sdr_node = None
        self._usdshade_prim = None
        self._prim_type = None

        if self._prim.IsA(UsdShade.Shader):
            self._usdshade_prim = UsdShade.Shader(prim)
            self._sdr_node = get_sdr_shader_node_for_prim(prim, warn_on_substitution=True)
            self._prim_type = UsdShade.Shader

            if not self._sdr_node:  # pragma: no cover
                carb.log_warn(f"Cannot get Sdr.ShaderNode for prim at: '{self._prim_path}'")

        elif self._prim.IsA(UsdShade.NodeGraph):
            self._usdshade_prim = UsdShade.NodeGraph(prim)

            if self._prim.IsA(UsdShade.Material):
                self._prim_type = UsdShade.Material
            else:
                self._prim_type = UsdShade.NodeGraph

        else:  # pragma: no cover
            carb.log_error(f"Expected UsdShade.Shader or UsdShade.NodeGraph prim at: '{self._prim_path}'")

        # This setting provides control over which texture colorspaces are forced to "raw".
        # It's controlled by adding the following annotation to the corresponding texture2d MDL parameter:
        #   anno::usage("roughness")
        # If the usage annotation is set and the value it contains is in the list specified by the mdlForceRawForUsage setting then the colorspace will be set
        # to raw unless specifically overridden.
        self._settings = carb.settings.get_settings()
        self._force_colorspace_raw = self._settings.get(self.MDL_FORCE_RAW_SETTING_PATH).split(",")
        self._force_colorspace_raw = [s.strip() for s in self._force_colorspace_raw]

    def get_node_properties(self) -> List[UsdShadePropertyPlaceholder]:
        """
        Create and return an UsdShadePropertyPlaceholder's for this nodes node level properties.
            e.g. description
        """

        if not self._sdr_node:  # pragma: no cover
            return []

        node_help = self._sdr_node.GetHelp()
        if not node_help:
            return []

        metadata = {Sdf.AttributeSpec.DefaultValueKey: node_help, Sdf.AttributeSpec.DisplayGroupKey: "Description"}

        return [UsdShadePropertyPlaceholder("Description", metadata, True)]

    def get_input_properties(
        self, property_name_filter: Optional[List[str]] = None
    ) -> List[UsdShadePropertyPlaceholder]:
        """
        Create and return UsdShadePropertyPlaceholder's for this nodes input properties
        """

        if self._sdr_node:
            sdr_shader_properties = [self._sdr_node.GetInput(name) for name in self._sdr_node.GetInputNames()]
            return self._get_placeholders(sdr_shader_properties, UsdShade.Tokens.inputs, property_name_filter)

        # If we are here that means we weren't able to retrive an SdrShaderNode from the SDR registry, which might be the case if we are loading a scene file that
        # contains shaders from a render context we don't support, e.g. Arnold or Renderman
        # In this case we will create placeholders from the input attributes on the UsdShade.shader
        input_attributes = [usdshade_input.GetAttr() for usdshade_input in self._usdshade_prim.GetInputs()]
        input_placeholders = self._get_placeholders_for_attrs(input_attributes)

        if self._prim_type == UsdShade.Material:
            for placeholder in input_placeholders:
                placeholder.SetName(f"{placeholder.GetName()}{UsdShadePropertyPlaceholder.MATERIAL_INPUT_SUFFIX}")

        return input_placeholders

    def get_output_properties(
        self, property_name_filter: Optional[List[str]] = None
    ) -> List[UsdShadePropertyPlaceholder]:
        """
        Create and return  UsdShadePropertyPlaceholder's for this nodes output properties
        """
        if self._prim.IsA(UsdShade.Material):
            return self._get_material_output_properties(property_name_filter)

        if self._sdr_node:
            sdr_shader_properties = [self._sdr_node.GetOutput(name) for name in self._sdr_node.GetOutputNames()]
            return self._get_placeholders(sdr_shader_properties, UsdShade.Tokens.outputs, property_name_filter)

        # If we are here that means we weren't able to retrive an SdrShaderNode from the SDR registry, which might be the case if we are loading a scene file that
        # contains shaders from a render context we don't support, e.g. Arnold or Renderman
        # In this case we will create placeholders from the output attributes on the UsdShade.shader
        output_attributes = [
            usdshade_output.GetAttr() for usdshade_output in self._usdshade_prim.GetOutputs()
        ]  # pragma: no cover
        return self._get_placeholders_for_attrs(output_attributes)  # pragma: no cover

    def _get_material_output_properties(
        self, property_name_filter: Optional[List[str]] = None
    ) -> List[UsdShadePropertyPlaceholder]:
        """
        Special handling for UsdShade.Material prim outputs.
        """
        import omni.UsdMdl

        placeholder_properties = []

        render_contexts = self._settings.get(self.RENDER_CONTEXTS_SETTING_PATH)

        for render_context in render_contexts:
            context_name = render_context
            if context_name != UsdShade.Tokens.universalRenderContext:
                context_name += Sdf.Path.namespaceDelimiter

            for suffix in [UsdShade.Tokens.displacement, UsdShade.Tokens.surface, UsdShade.Tokens.volume]:
                full_name = f"{UsdShade.Tokens.outputs}{context_name}{suffix}"
                if property_name_filter and full_name not in property_name_filter:
                    continue

                metadata = {
                    Sdf.PrimSpec.TypeNameKey: Sdf.ValueTypeNames.Token,
                    Sdr.PropertyMetadata.RenderType: omni.UsdMdl.Types.Struct,
                    UsdShade.Tokens.sdrMetadata: {
                        omni.UsdMdl.Metadata.StructType: omni.UsdMdl.StructTypes.Material,
                        omni.UsdMdl.Metadata.Symbol: "::material",
                    },
                }

                placeholder_properties.append(UsdShadePropertyPlaceholder(full_name, metadata, False))

        return placeholder_properties

    def _hints_to_metadata(self, hints: dict, metadata: dict) -> None:
        """
        Hints will contain objects that can be evaled to Python objects, e.g.
            hard_range -> {'max':1,'min':0}
        """

        def materialx_uiminmax(
            min_key: str, max_key: str, hints: dict, py_type: Union[Type[float], Type[int]]
        ) -> Optional[dict]:
            """
            Set range hints for Material-X.
            Note we only set the hint if both values exist, I have noticed cases where only one value is present
            e.g.
            ND_UsdPreviewSurface_surfaceShader ior parameter has the following so only soft_range would be set.
            uimin --> 0.0
            uisoftmax --> 3.0
            uisoftmin --> 1.0
            """
            if (min_key in hints) and (max_key in hints):
                min_val = hints[min_key]
                if isinstance(min_val, str):
                    min_val = tuple(py_type(v) for v in min_val.split(","))
                elif not isinstance(min_val, tuple):
                    min_val = [py_type(min_val)]
                    min_val = tuple(min_val)

                min_val = min_val if len(min_val) > 1 else min_val[0]

                max_val = hints[max_key]
                if isinstance(max_val, str):
                    max_val = tuple(py_type(v) for v in max_val.split(","))
                elif not isinstance(max_val, tuple):
                    max_val = [py_type(max_val)]
                    max_val = tuple(max_val)

                max_val = max_val if len(max_val) > 1 else max_val[0]

                return {"min": min_val, "max": max_val}

            return None

        if hints:
            type_name_key = metadata[Sdf.PrimSpec.TypeNameKey]
            is_int = type_name_key in [
                Sdf.ValueTypeNames.Int,
                Sdf.ValueTypeNames.Int2,
                Sdf.ValueTypeNames.Int3,
                Sdf.ValueTypeNames.Int4,
            ]
            py_type = int if is_int else float

            hard_range = materialx_uiminmax("uimin", "uimax", hints, py_type)
            if hard_range:
                hints["hard_range"] = hard_range

            soft_range = materialx_uiminmax("uisoftmin", "uisoftmax", hints, py_type)
            if soft_range:
                hints["soft_range"] = soft_range

            for k, v in hints.items():
                key = k
                if k == "hard_range":
                    key = "range"

                    # for int values with hard_range of [0, 1] set the widget type to checkbox and skip setting the custom data.
                    if (
                        (type_name_key == Sdf.ValueTypeNames.Int)
                        and isinstance(v, dict)
                        and (v.get("min", None) == 0)
                        and (v.get("max", None) == 1)
                    ):
                        metadata[Sdr.PropertyMetadata.Widget] = "checkBox"
                        continue

                if Sdf.AttributeSpec.CustomDataKey not in metadata:
                    metadata[Sdf.AttributeSpec.CustomDataKey] = {}

                metadata[Sdf.AttributeSpec.CustomDataKey][key] = v

    def _get_placeholders_for_attrs(self, attributes: List[Usd.Attribute]) -> List[UsdShadePropertyPlaceholder]:
        def get_default_value(attribute: Usd.Attribute, property_metadata: dict) -> None:
            type_name = property_metadata.get(Sdf.PrimSpec.TypeNameKey, None)
            if not type_name:
                return

            if isinstance(type_name, str):
                type_name = Sdf.ValueTypeNames.Find(type_name)

            if not isinstance(type_name, Sdf.ValueTypeName):
                return

            default_value = type_name.defaultValue
            property_metadata[Sdf.AttributeSpec.CustomDataKey][Sdf.AttributeSpec.DefaultValueKey] = default_value

        placeholder_properties = []

        for attribute in attributes:
            name = attribute.GetName()
            property_metadata = self._prim_properties_metadata.get(name, {})
            if Sdf.AttributeSpec.CustomDataKey not in property_metadata:
                property_metadata[Sdf.AttributeSpec.CustomDataKey] = {}

            if Sdf.AttributeSpec.DefaultValueKey not in property_metadata[Sdf.AttributeSpec.CustomDataKey]:
                get_default_value(attribute, property_metadata)

            hints = property_metadata.get(UsdShade.Tokens.sdrMetadata, {})
            if hints:
                self._hints_to_metadata(hints, property_metadata)

            if self._prim_type == UsdShade.Shader:
                property_metadata["readonly"] = True

            placeholder = UsdShadePropertyPlaceholder(name, property_metadata, True)

            if not placeholder.GetDisplayName():
                placeholder.SetDisplayName(attribute.GetBaseName())

            display_group = placeholder.GetDisplayGroup()

            if name.startswith(UsdShade.Tokens.outputs):
                if not display_group.startswith("Outputs:"):
                    display_group = f"Outputs:{display_group}"

            elif name.startswith(UsdShade.Tokens.inputs) and not display_group.startswith("Inputs:"):
                display_group = f"Inputs:{display_group}" if display_group else "Inputs"

            placeholder.SetDisplayGroup(display_group)

            placeholder_properties.append(placeholder)

        return placeholder_properties

    def _get_placeholders(
        self,
        sdr_shader_properties: List[Sdr.ShaderProperty],
        property_name_prefix: str,
        property_name_filter: Optional[List[str]] = None,
    ) -> List[UsdShadePropertyPlaceholder]:
        """
        Create and return a list of UsdShadePropertyPlaceholder's from the input list of Sdr.ShaderProperty's
        If the underlying prim has a property of the same name, we optionally overlay it's metadata on top of the metadata we gathered from the SDR, if we have
           conflicting values, the metadata on the prim "wins"/takes precedence
        """

        def get_colorspace_parameter(metadata: dict) -> bool:
            return (
                metadata.get(UsdShade.Tokens.sdrMetadata, {})
                .get("annotation", {})
                .get("annotation_colorspace_parameter", {})
                .get("s", None)
            )

        def update_placeholder_colorspace(
            placeholder_name: str,
            colorspace_placeholder_name: str,
            placeholder_properties: List[UsdShadePropertyPlaceholder],
        ) -> None:
            placeholder_idx = next(
                (i for i, prop in enumerate(placeholder_properties) if prop.GetName() == placeholder_name), -1
            )

            if placeholder_idx == -1:
                carb.log_warn(f"Unable to find placeholder for '{placeholder_name}'.")
                return

            colorspace_idx = next(
                (i for i, prop in enumerate(placeholder_properties) if prop.GetName() == colorspace_placeholder_name),
                -1,
            )
            if placeholder_idx == -1:
                carb.log_warn(f"Unable to find placeholder for '{colorspace_placeholder_name}'.")
                return

            # 1. clear colorspace related metadata from the texture parameter.
            # if this metadata does not exist then texture widget will not display the colorspace dropdown.
            metadata = placeholder_properties[placeholder_idx].GetAllMetadata()
            if "colorSpace" in metadata:
                del metadata["colorSpace"]

            custom_data = metadata.get(Sdf.AttributeSpec.CustomDataKey, None)
            colorspace_default_value = f"colorSpace_{Sdf.AttributeSpec.DefaultValueKey}"
            if custom_data and colorspace_default_value in custom_data:
                del custom_data[colorspace_default_value]

            # 2. setup colorspace parameter, making sure it's visible and that the proper tokens are displayed.
            metadata = placeholder_properties[colorspace_idx].GetAllMetadata()
            if Sdf.AttributeSpec.HiddenKey in metadata:
                del metadata[Sdf.AttributeSpec.HiddenKey]

            metadata["allowedTokens"] = ["auto", "raw", "sRGB"]

        # filter properties
        filtered = [
            prop for prop in sdr_shader_properties if not property_name_filter or prop.GetName() in property_name_filter
        ]

        props_with_colorspace_parameter = []
        placeholder_properties = []
        for sdr_shader_property in filtered:
            metadata = self._get_property_metadata(sdr_shader_property)

            full_name = f"{property_name_prefix}{sdr_shader_property.GetName()}"

            # overlay the metadata from property on the underlying prim if requested
            if self._overlay_property_metadata:
                metadata = deep_dict_update(metadata, self._prim_properties_metadata.get(full_name, {}))

            colorspace_parameter_name = get_colorspace_parameter(metadata)
            if colorspace_parameter_name:
                props_with_colorspace_parameter.append(
                    (full_name, f"{property_name_prefix}{colorspace_parameter_name}")
                )

            placeholder_properties.append(UsdShadePropertyPlaceholder(full_name, metadata, True))

        # process the texture parameters whose colorspace is decoupled from the metadata/is stored as a separate unique parameter.
        for placeholder_name, colorspace_parameter_name in props_with_colorspace_parameter:
            update_placeholder_colorspace(placeholder_name, colorspace_parameter_name, placeholder_properties)

        return placeholder_properties

    def _get_property_metadata(self, sdr_shader_property: Sdr.ShaderProperty) -> dict:
        """
        Convert Sdr.ShaderProperty metadata into property metadata.
        """

        def set_display_group(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            page = sdr_shader_property.GetPage()
            display_group = ""
            if page:
                display_group = page
                del metadata[Sdr.PropertyMetadata.Page]

            if sdr_shader_property.IsOutput():
                if not display_group.startswith("Outputs"):
                    display_group = f"Outputs:{display_group}" if display_group else "Outputs"

            elif not display_group.startswith("Inputs"):
                display_group = f"Inputs:{display_group}" if display_group else "Inputs"

            metadata[Sdf.AttributeSpec.DisplayGroupKey] = display_group

        def set_display_name(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            display_name = sdr_shader_property.GetName()

            label = sdr_shader_property.GetLabel()
            if label:
                display_name = label
                del metadata[Sdr.PropertyMetadata.Label]

            metadata[Sdf.AttributeSpec.DisplayNameKey] = display_name

        def set_type_name(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            ndr_type_indicator = sdr_shader_property.GetTypeAsSdfType()
            type_name = ndr_type_indicator[1]
            if not type_name:
                type_name = str(ndr_type_indicator[0])

            metadata[Sdf.PrimSpec.TypeNameKey] = type_name

        def set_default_value(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            default_value = get_sdr_shader_property_default_value(sdr_shader_property, metadata)
            metadata[Sdf.AttributeSpec.CustomDataKey][Sdf.AttributeSpec.DefaultValueKey] = default_value

        def set_allowed_tokens(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            options = sdr_shader_property.GetOptions()
            if not options:
                return

            metadata["allowedTokens"] = [kv[0] for kv in options]

            if metadata[Sdf.PrimSpec.TypeNameKey] == Sdf.ValueTypeNames.Int:
                metadata[UsdShade.Tokens.sdrMetadata][Sdr.PropertyMetadata.Options] = [
                    (kv[0], int(kv[1])) for kv in options
                ]

        def literal_eval(sdr_shader_property: Sdr.ShaderProperty, expr: str) -> Any:
            """
            Evaulate the input expression if possible returning a Python object.
            Return original expression on failure.
            """
            if not isinstance(expr, str):  # pragma: no cover
                carb.log_warn(
                    f"Unable to evaluate '{expr}' for Sdr.ShaderProperty: '{sdr_shader_property.GetName()}' for prim: '{self._prim_path}'. Excepted string, received: '{type(expr)}'."
                )
                return expr

            if expr.startswith(("[", "{")) or expr.isnumeric():
                try:
                    value = ast.literal_eval(expr)

                except Exception as e:  # pylint: disable=broad-exception-caught  # pragma: no cover
                    carb.log_warn(
                        f"Unable to evaluate '{expr}' for Sdr.ShaderProperty: '{sdr_shader_property.GetName()}' for prim: '{self._prim_path}'. Error: '{e}'"
                    )
                    return expr

            else:
                value = expr

            if isinstance(value, (dict, list, tuple, str, int, float, bool, type(None))):
                return value

            carb.log_warn(
                f"Unable to evaluate '{expr}' for Sdr.ShaderProperty: '{sdr_shader_property.GetName()}' for prim: '{self._prim_path}'. Evaluated data is of unexpected type: '{type(value)}'."
            )  # pragma: no cover
            return value

        def set_sdr_metadata(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            """
            Sdr metadata will contain objects that can be evaled to Python objects, e.g.
                hard_range -> {'max':1,'min':0}
            """
            import omni.UsdMdl

            for token in omni.UsdMdl.GetAllMetadataTokens():
                if token in metadata:
                    metadata[UsdShade.Tokens.sdrMetadata][token] = literal_eval(sdr_shader_property, metadata[token])
                    del metadata[token]

        def promote_hints(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            """
            Hints will contain objects that can be evaled to Python objects, e.g.
                hard_range -> {'max':1,'min':0}
            """

            hints = sdr_shader_property.GetHints()
            if not hints:
                return

            for k, v in hints.items():
                if isinstance(v, str):
                    hints[k] = literal_eval(sdr_shader_property, v)

            self._hints_to_metadata(hints, metadata)

        def set_color_space(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            """
            Convert the MDL tex::gamma_mode value to a color space string.
            """
            import omni.UsdMdl

            add_color_space = Sdr.PropertyMetadata.IsAssetIdentifier in metadata

            render_type = metadata.get(Sdr.PropertyMetadata.RenderType, None)
            if render_type and (render_type != omni.UsdMdl.Types.Texture2d):
                add_color_space = False

            if not add_color_space:
                return

            gamma = metadata[UsdShade.Tokens.sdrMetadata].get(omni.UsdMdl.Metadata.TextureGamma, 0)
            if gamma is None:
                return

            converter = [(0, "auto"), (1, "raw"), (2.2, "sRGB")]
            color_space = next(
                (item[1] for item in converter if math.isclose(item[0], float(gamma), rel_tol=1e-05)), None
            )

            if not color_space:  # pragma: no cover
                color_space = "auto"
                message = (
                    f"The default 'gamma' value for Sdr.ShaderProperty: '{sdr_shader_property.GetName()}' on prim: '{self._prim_path}'"
                    f" contains an unknown value: '{gamma}' and cannot be mapped to a color space name, setting to 'auto'."
                )
                carb.log_warn(message)

            # If the anno::usage hint annotation has been set to one of the following then we force "raw" as the default colorspace.
            hint = metadata.get(Sdr.PropertyMetadata.Hints, None)
            if hint and hint in self._force_colorspace_raw:
                color_space = "raw"

            metadata["colorSpace"] = color_space

            # store the default value as metadata so the MetadataObjectModel is aware of what the default value is.
            metadata[Sdf.AttributeSpec.CustomDataKey][f"colorSpace_{Sdf.AttributeSpec.DefaultValueKey}"] = color_space

        def set_hidden(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            metadata[Sdf.AttributeSpec.HiddenKey] = (
                ("hidden" in metadata)
                or ("unused" in metadata)
                or ("hidden" in metadata[Sdf.AttributeSpec.CustomDataKey])
                or ("unused" in metadata[Sdf.AttributeSpec.CustomDataKey])
            )

        def set_documentation(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            help_text = sdr_shader_property.GetHelp()
            if help_text:
                metadata[Sdf.AttributeSpec.DocumentationKey] = help_text
                del metadata[Sdr.PropertyMetadata.Help]

        def set_placeholder_class(sdr_shader_property: Sdr.ShaderProperty, metadata: dict) -> None:
            """
            By default 'omni.kit.property.usd.UsdBase' constructs placeholder objects of type: 'omni.kit.property.usd.PlaceholderAttribute'.
            However it's possible that for this property no information has been serialzed to the stage.
            This will result in widget errors due to not being able to retrieve property information: value, metadata etc.

            Setting the placeholder_class metadata will cause 'omni.kit.property.usd.UsdBase' to construct placeholder objects
            of type: 'UsdShadeInputPlaceholderAttribute' which is what allows us to display properties in the UI that do not exist on the stage.
            See the 'UsdShadeInputPlaceholderAttribute' class documentation for further information/explanation.

            """
            metadata["placeholder_class"] = UsdShadeInputPlaceholderAttribute

        property_metadata = sdr_shader_property.GetMetadata()
        metadata = property_metadata

        # Is this a custom property
        metadata[Sdf.AttributeSpec.CustomKey] = False

        metadata["variability"] = Sdf.VariabilityVarying

        metadata[UsdShade.Tokens.sdrMetadata] = {}
        metadata[Sdf.AttributeSpec.CustomDataKey] = {}

        set_display_group(sdr_shader_property, metadata)
        set_display_name(sdr_shader_property, metadata)
        set_type_name(sdr_shader_property, metadata)
        set_sdr_metadata(sdr_shader_property, metadata)
        set_documentation(sdr_shader_property, metadata)

        if not sdr_shader_property.IsOutput():
            set_allowed_tokens(sdr_shader_property, metadata)
            promote_hints(sdr_shader_property, metadata)
            set_hidden(sdr_shader_property, metadata)
            set_color_space(sdr_shader_property, metadata)
            set_placeholder_class(sdr_shader_property, metadata)

        # needs to be last as metadata is sometimes used when determining the default value.
        set_default_value(sdr_shader_property, metadata)

        return metadata
