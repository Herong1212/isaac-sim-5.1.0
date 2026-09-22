# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pxr import Sdf, Usd, UsdShade

from .material_context import MaterialContext
from .nodegraph_builder import NodeGraphPropertiesBuilder
from .placeholder import UsdShadePropertyPlaceholder
from .shader_builder import ShaderPropertiesBuilder


class MaterialPropertiesBuilder(NodeGraphPropertiesBuilder):
    def __init__(self, prim: Usd.Prim, args: dict):
        NodeGraphPropertiesBuilder.__init__(self, prim, args, UsdShade.Material)

        if not self._valid:  # pragma: no cover
            return

        self._material_contexts = {}

        self._display_base_shader = self._args.get("display_base_shader", True)

        if self._display_base_shader:
            self._get_active_contexts()

    def _get_active_contexts(self) -> None:
        """
        Process terminal connections to material prim to determine which contexts are connected.
        """

        self._material_contexts.clear()
        api = UsdShade.ConnectableAPI(self._prim)

        for output in api.GetOutputs():
            connected_sources = output.GetConnectedSources()
            if not connected_sources:
                continue

            source_info_vector = connected_sources[0]
            if len(source_info_vector) == 0:
                continue

            prim = source_info_vector[0].source.GetPrim()

            shader = UsdShade.Shader(prim)
            if not shader:  # pragma: no cover
                self._valid = False
                self._material_contexts.clear()
                return

            parts = output.GetFullName().replace(UsdShade.Tokens.outputs, "").split(Sdf.Path.namespaceDelimiter)

            # mdl, mtlx, ri, etc..
            context_name = UsdShade.Tokens.universalRenderContext if len(parts) == 1 else parts[0]

            if context_name not in self._material_contexts:
                self._material_contexts[context_name] = MaterialContext(context_name)

            # surface, displacement, volume
            shader_type = parts[-1]
            self._material_contexts[context_name].add_output(shader_type, prim)

    def _gather_properties(self) -> None:
        """
        If self._shader_prim exists then, query the Sdr.ShaderNode that is associated with this prim to obtain:
            1. input properties
            2. node level properties, e.g. description.
        Otherwise gather the properties using NodeGraphPropertiesBuilder
        """

        if len(self._material_contexts) == 0:  # pragma: no cover
            super()._gather_properties()
            return

        display_group_prefix = "Shader"

        for material_context in self._material_contexts.values():
            context_prefix = (
                f"{display_group_prefix}{Sdf.Path.namespaceDelimiter}{material_context.display_group_prefix}"
            )

            for material_output in material_context.outputs:
                shader_placeholder_properties = ShaderPropertiesBuilder(material_output.prim, self._args).build()

                shader_placeholder_properties = [
                    prop
                    for prop in shader_placeholder_properties
                    if prop.GetName().startswith((UsdShade.Tokens.inputs, "Description")) and prop.GetDisplayGroup()
                ]

                shader_prefix = f"{context_prefix}{Sdf.Path.namespaceDelimiter}{material_output.display_group_prefix}"

                for placeholder in shader_placeholder_properties:
                    if placeholder.GetName().startswith("Description"):
                        placeholder.SetName(
                            f"Description{Sdf.Path.namespaceDelimiter}{material_output.display_group_prefix}"
                        )
                        placeholder.SetDisplayName("Description")

                    display_group = f"{shader_prefix}{Sdf.Path.namespaceDelimiter}{placeholder.GetDisplayGroup()}"
                    display_group = display_group.replace("Inputs", "").replace("Inputs:", "").removesuffix(":")
                    placeholder.SetDisplayGroup(display_group)
                    placeholder.SetMetadata("sourcePrimPath", material_output.prim.GetPath())

                self._placeholder_properties.extend(shader_placeholder_properties)

        super()._gather_properties()

    def _set_placeholder_metadata(self, placeholder: UsdShadePropertyPlaceholder) -> None:
        """
        If the property name starts with "info:", set the displayName and displayGroup metadata.
        Otherwise pass this up to parent class for handling.
        """

        property_name = placeholder.GetName()

        if property_name.startswith(UsdShade.Tokens.outputs):
            display_name = property_name
            parts = property_name.replace(UsdShade.Tokens.outputs, "").split(Sdf.Path.namespaceDelimiter)
            num_parts = len(parts)
            if num_parts == 1:
                display_name = parts[0].capitalize()

            elif num_parts == 2:
                display_name = f"{parts[0].upper()} {parts[1].capitalize()}"

            placeholder.SetDisplayGroup("Outputs")
            placeholder.SetDisplayName(display_name)

        else:
            super()._set_placeholder_metadata(placeholder)

    def _append_prim_properties(self) -> None:
        """
        Create UsdShadePropertyPlaceholder's for those properties on the prim for which we haven't already done so.
        Override to add Material "outputs:*" properties
        """
        placeholder_property_names = [p.GetName() for p in self._placeholder_properties]

        for prop in self._prim.GetProperties():
            prop_name = prop.GetName()

            if not prop_name.startswith(UsdShade.Tokens.inputs) and prop_name not in placeholder_property_names:
                self._placeholder_properties.append(self._create_placeholder(prop))
