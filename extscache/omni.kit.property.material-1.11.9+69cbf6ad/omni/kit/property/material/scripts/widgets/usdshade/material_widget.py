# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a widget for displaying and editing USD Shade materials within the NVIDIA Omniverse Kit framework."""

__all__ = ["UsdShadeMaterialWidget"]

import asyncio
from typing import List

import omni.ui as ui
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.usd_property_widget import UiDisplayGroup, UsdPropertiesWidgetBuilder, UsdPropertyUiEntry
from omni.kit.window.preferences import PERSISTENT_SETTINGS_PREFIX
from pxr import Sdf, Usd, UsdShade

from .base_widget import UsdShadeBaseWidget
from .utils import create_nonpersistant_attribute, get_display_group_for_render_context


class UsdShadeMaterialWidget(UsdShadeBaseWidget):
    """A widget for displaying and editing USD Shade materials.

    This widget extends the UsdShadeBaseWidget to provide a user interface for interacting with materials defined in USD (Universal Scene Description) files. It allows users to view and modify material properties, including shader parameters and render contexts. The widget dynamically updates to reflect changes in the underlying USD file and provides a way to visualize different shader effects.

    The widget is designed to work within the NVIDIA Omniverse Kit framework and interacts with various USD and Omniverse Kit APIs to manage material properties. It subscribes to changes in application settings to reflect updates in the UI and supports async operations for handling material attributes.

    Args:
        title (str): The title of the widget, defaulting to 'Material and Shader'."""

    DISPLAY_BASE_SHADER_SETTINGS_PATH = PERSISTENT_SETTINGS_PREFIX + "/app/properties/material/displayBaseShader"
    """str: Path to base shader display settings."""

    RENDER_CONTEXTS_SETTING_PATH = PERSISTENT_SETTINGS_PREFIX + "/app/hydra/material/renderContexts"
    """str: Path to render contexts settings."""

    def __init__(self, title: str = "Material and Shader"):
        """Initializes the UsdShadeMaterialWidget with optional title."""
        super().__init__(UsdShade.Material, title)

        self._display_base_shader_changed_sub = self._settings.subscribe_to_node_change_events(
            self.DISPLAY_BASE_SHADER_SETTINGS_PATH, self._display_base_shader_changed
        )

        self._render_context_changed_sub = self._settings.subscribe_to_node_change_events(
            self.RENDER_CONTEXTS_SETTING_PATH, self._render_context_changed
        )

        self._shader_buttons = []
        self._shader_frames = []

        self._render_context_display_group_order = []
        self._render_context_changed()

        self._display_base_shaders = False
        self._display_base_shader_changed()

    def _get_builder_args(self) -> dict:
        args = super()._get_builder_args()

        args.update({"display_base_shader": self._display_base_shaders})

        return args

    def clean(self) -> None:
        """Clean up function to be called before destroying the object."""

        if self._render_context_changed_sub:
            self._settings.unsubscribe_to_change_events(self._render_context_changed_sub)
            self._render_context_changed_sub = None

        super().clean()

    def _render_context_changed(self, *args, **kwargs) -> None:
        """
        Callback executed when the user selects a render context other than the one that is currently being displayed by the widget.
        """

        order = self._settings.get(self.RENDER_CONTEXTS_SETTING_PATH)
        if order:
            self._render_context_display_group_order = [get_display_group_for_render_context(i) for i in order]
            self.request_rebuild()

    def _display_base_shader_changed(self, *args, **kwargs) -> None:
        """
        Set the title of the widget depending upon if the user wants the terminal shader parameters displayed.
        """

        setting = self._settings.get(self.DISPLAY_BASE_SHADER_SETTINGS_PATH)
        self._display_base_shaders = True if (setting is None) else bool(setting)

        if not self._display_base_shaders:
            self._title = "Material"
        else:
            self._title = "Material and Shader"

        self.request_rebuild()

    def _path_requires_rebuild(self, path: Sdf.Path) -> bool:
        """
        If a property on the underlying shader this prim represents changes then trigger a rebuild.
        """

        if (path.GetPrimPath() in self._shader_prim_paths) and (
            bool(self._payload.get_stage().GetPropertyAtPath(path)) != bool(self._models.get(path))
        ):
            return True

        return super()._path_requires_rebuild(path)

    def _sort_properties_for_ui(self, props: List[UsdPropertyUiEntry]) -> List[UsdPropertyUiEntry]:
        """
        Sort the output ports so that the universal output ports appear first (sorted alphabetically),
        followed by the ports for the other contexts (MDL, Material-X)
        """

        def sort_outputs(props: List[UsdPropertyUiEntry]) -> None:
            if len([prop for prop in props if prop.prop_name.startswith(UsdShade.Tokens.outputs)]) == 0:
                return

            start = next(i for i, prop in enumerate(props) if prop.prop_name.startswith(UsdShade.Tokens.outputs))
            end = next(i for i, prop in enumerate(props[::-1]) if prop.prop_name.startswith(UsdShade.Tokens.outputs))
            end = len(props) if end < start else end
            outputs_slice = props[start : end + 1]

            # sort by number of ":" characters in the property name, this will ensure the universal output ports appear first.
            outputs_slice.sort(
                key=lambda ui_prop: (ui_prop.prop_name.count(Sdf.Path.namespaceDelimiter), ui_prop.prop_name)
            )

            props[start : end + 1] = outputs_slice

        def sort_by_material_ui_order(prop: UsdPropertyUiEntry) -> int:
            display_group = prop.display_group

            if display_group.startswith("Inputs"):
                return 0

            if display_group.startswith("Shader"):
                # sort according to render context order set in Material/Preferences

                parts = display_group.split(Sdf.Path.namespaceDelimiter)
                if len(parts) > 1:
                    context = parts[1]

                    if context in self._render_context_display_group_order:
                        return 1 + (
                            self._render_context_display_group_order.index(context)
                            / len(self._render_context_display_group_order)
                        )

                return 2

            return 3

        customized = super()._sort_properties_for_ui(props)
        sort_outputs(customized)

        customized.sort(key=sort_by_material_ui_order)

        return customized

    def _customize_props_layout(self, props: List[UsdPropertyUiEntry]) -> List[UsdPropertyUiEntry]:
        """
        For those input properties that exist on the base/terminal/root shader prims but are displayed in the Material widget
            set the prim_paths attribute to the path of the underlying UsdShade.Shader prims.
        This way the UI reflects the values and/or connections on those prims.
        """

        customized = props.copy()
        for ui_prop in props:
            if ui_prop.display_group.startswith("Shader"):
                ui_prop.prim_paths = [ui_prop.metadata.get("sourcePrimPath")]

            customized.append(ui_prop)

        return super()._customize_props_layout(props)

    @staticmethod
    async def _create_paused_attribute(material_paths: List[str]) -> None:
        """
        Create the 'paused' attribute which is used by the Material Graph editor.
        If it's value is set to True, the material code in the Hydra render delegate will skip processing this material.
        """

        await create_nonpersistant_attribute(material_paths, "paused", Sdf.ValueTypeNames.Bool, False)

    def _get_shader_prim_paths(self, prim: Usd.Prim) -> None:
        """
        Set the list of terminal shader nodes connected to this material.
        """

        api = UsdShade.ConnectableAPI(prim)

        for output in api.GetOutputs():
            connected_sources = output.GetConnectedSources()
            if not connected_sources:
                continue

            source_info_vector = connected_sources[0]
            if len(source_info_vector) == 0:
                continue

            shader = UsdShade.Shader(source_info_vector[0].source.GetPrim())
            self._shader_prim_paths.append(shader.GetPath())

        self._shader_prim_paths = list(set(self._shader_prim_paths))

    def on_new_payload(self, payload: PrimSelectionPayload) -> bool:
        """Handles a new payload for the widget.

        Args:
            payload (:obj:`PrimSelectionPayload`): The new payload to be handled by the widget.

        Returns:
            bool: True if the prims contained within the payload can be represented by this widget."""

        if not super().on_new_payload(payload):
            return False

        for prim_path in self._payload:
            prim = self._get_prim(prim_path)

            if self._display_base_shaders:
                self._get_shader_prim_paths(prim)

            if not prim.GetAttribute("paused"):
                asyncio.ensure_future(self._create_paused_attribute([prim_path]))

        # Load any modules needed to draw this widget
        self._load_mdl_modules()

        return True

    def _activate_frame(self, frame_id: int) -> None:
        """
        Callback trigged when a render context button is pressed, the corresponing frame containing the shader parameters for that conext will be displayed.
        """

        # width is 20% by default, so this will be the max width, if there are more than 3 buttons we scale down the width.
        width = 20

        if len(self._shader_buttons) > 3:
            width *= 3.0 / len(self._shader_buttons)

        for i, (frame, button) in enumerate(zip(self._shader_frames, self._shader_buttons)):
            button.width = ui.Percent(width)

            if i == frame_id:
                frame.visible = True
                button.set_style({"Button": {"background_color": ui.color(77, 114, 92)}})
            else:
                frame.visible = False
                button.set_style({})

    def _build_shader_frame(self, stage, prim_paths: list, display_group: UiDisplayGroup, level: int, prefix: str):
        """
        Create the "Shader" frame.
        Emulate a traditional tabbed widet by adding buttons to allow the user to select one of the multiple render contexts to be displayed.
        """

        self._shader_buttons.clear()
        self._shader_frames.clear()

        (frame, stack, _) = self._build_framestack(prefix, display_group)

        with frame:
            with stack:
                with ui.HStack(height=0, spacing=5):
                    additional_label_kwargs = {}
                    UsdPropertiesWidgetBuilder.create_label(
                        "  Render Context:", additional_label_kwargs=additional_label_kwargs
                    )
                    for i, key in enumerate(display_group.sub_groups.keys()):
                        self._shader_buttons.append(ui.Button(f"{key}", clicked_fn=lambda i=i: self._activate_frame(i)))

                with ui.ZStack():
                    for _name, sub_group in display_group.sub_groups.items():
                        shader_frame = ui.Frame()
                        self._shader_frames.append(shader_frame)
                        with shader_frame:
                            with ui.VStack():
                                for _nested_name, nested_sub_group in sub_group.sub_groups.items():
                                    self._build_nested_group_frame(
                                        stage, prim_paths, nested_sub_group, level + 1, prefix
                                    )
                                    # break

        self._activate_frame(0)

    def _build_nested_group_frame(
        self, stage, prim_paths: list, display_group: UiDisplayGroup, level: int, prefix: str
    ):
        if display_group.name != "Shader":
            super()._build_nested_group_frame(stage, prim_paths, display_group, level, prefix)

        else:
            self._build_shader_frame(stage, prim_paths, display_group, level, prefix)
