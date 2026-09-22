# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines a base widget for interacting with USD Shade elements within the omni.kit.property.material extension."""

__all__ = ["UsdShadeBaseWidget"]

import asyncio
import copy
from typing import Any, Dict, List, Optional, Tuple, Union

import carb
import omni.client.utils
from omni.kit.async_engine import run_coroutine
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry, create_primspec_bool
from omni.kit.window.preferences import PERSISTENT_SETTINGS_PREFIX
from pxr import Sdf, Sdr, Tf, Usd, UsdShade

from .models import get_custom_ui_prop_build_fn
from .placeholder import GetPlaceholderPropertiesForPrim, UsdShadePropertyPlaceholder
from .usdshade_property_ui_entry import UsdShadePropertyUiEntry
from .utils import get_shader_info, remove_properties_and_connections


class UsdShadeBaseWidget(UsdPropertiesWidget):
    """A base class for creating widgets for USD Shade elements.

    This class provides a foundation for deriving custom widgets that interact with USD Shading prims, such as shaders and materials. It handles common functionalities like managing USD schema objects, setting up white mode exceptions, and responding to MDL module loads. It also facilitates the customization of the widget's UI, including property ordering and group collapsing.

    Args:
        schema (:obj:`Usd.SchemaBase`): The USD schema this widget targets.
        title (str): The top level group name in the UI.
        schema_ignore (Optional[List[:obj:`Usd.SchemaBase`]]): Optional list of USD schema types ignored by this widget.
    """

    # for testing/debugging purposes
    PRINT_LAYOUT = False
    """bool: Flag for testing/debugging the UI layout."""
    PRINT_LAYOUT_METADATA = False
    """bool: Flag to print metadata for debugging."""

    # The order that the UI groups should be displayed in the UI.
    UI_ORDER = ["Description", "inputs", "outputs", "info", "Material Flags", "ui"]
    """List[str]: Order to display UI groups."""

    MATERIAL_ADAPTER_SETTING_PATH = "/ext/omni.kit.property.material/enableAdapter"
    """str: Path to material adapter setting."""

    MATERIAL_WHITE_MODE_EXCEPTION_LIST_SETTING_PATH = PERSISTENT_SETTINGS_PREFIX + "/app/rendering/whiteModeExceptions"
    """str: Path to white mode exceptions setting."""
    MATERIAL_WHITE_MODE_EXCEPTION_INPUT = f"{UsdShade.Tokens.inputs}excludeFromWhiteMode"
    """str: Identifier for white mode exception input."""

    def __init__(self, schema: Usd.SchemaBase, title: str, schema_ignore: Optional[List[Usd.SchemaBase]] = None):
        """Initializes the UsdShadeBaseWidget.

        This method initializes the widget with a USD schema and various settings."""
        import omni.UsdMdl as UsdMdl

        self._settings = carb.settings.get_settings()
        enable_adapter = self._settings.get_as_bool(self.MATERIAL_ADAPTER_SETTING_PATH) or False

        super().__init__(title=title, collapsed=False, enable_adapter=enable_adapter, maintain_property_order=True)

        self._schema = schema
        self._schema_ignore = schema_ignore

        # The order in which properties will be displayed on the widget.
        self._property_order = []

        # list of UsdShade.Shader prim paths the widget cares about
        self._shader_prim_paths = []

        # mdl modules that we are waiting for to load before triggering a rebuild of the widget.
        self._mdl_modules_pending_load = set()

        # listeners to handle MDL module loading and reloading
        self._mdl_module_load_sub = Tf.Notice.Register(UsdMdl.Notice.ModuleLoaded, self._on_mdl_module_load, None)
        self._mdl_module_reload_sub = Tf.Notice.Register(UsdMdl.Notice.ModuleReloaded, self._on_mdl_module_reload, None)

        # ToDo: clean this up - we should only need to specify white mode at the material level similar to what we do with paused.
        # white mode properties
        self._white_mode_exceptions = set()
        self._white_mode_sub = None

        self._cancel_and_rebuild_task = None

        if self._schema in [UsdShade.Shader, UsdShade.Material]:
            self._setup_white_mode()

    def _get_shader_source_asset(self, shader_prim_path: Sdf.Path) -> Optional[Sdf.AssetPath]:
        """
        Return the source asset from the UsdShade.Shader at 'shader_prim_path' if it's source type is MDL
        """
        import omni.UsdMdl as UsdMdl

        usdshade_shader = UsdShade.Shader.Get(self._payload.get_stage(), shader_prim_path)
        if usdshade_shader and (usdshade_shader.GetImplementationSource() == UsdShade.Tokens.sourceAsset):
            return usdshade_shader.GetSourceAsset(UsdMdl.Tokens.Mdl)

        return None

    async def cancel_and_rebuild(self) -> None:
        # We sometimes end up in a state where the
        # widget is never updated due to the self._pending_rebuild_task not being completed, the following fixes this issue,
        # however its not clear to me if this is the right way to address this.

        # flake8: noqa: E0203

        if self._pending_dirty_task_or_future is not None:
            self._pending_dirty_task_or_future.cancel()
        self._pending_dirty_task_or_future = None
        self._pending_dirty_paths.clear()

        if self._pending_rebuild_task is not None:
            self._pending_rebuild_task.cancel()

        self._pending_rebuild_task = self._delayed_rebuild()
        await self._pending_rebuild_task

    # NOTE: This is called during test_reload_material due doesn't register in code coverage
    def _on_mdl_module_reload(self, notice, sender) -> None:  # pragma: no cover
        """
        Callback triggered when an MDL module has been reloaded.
        If the module is one used by the current set of shader prims request a rebuild.
        """
        if not (self._payload and self._shader_prim_paths):
            return

        resolved_path = notice.GetResolvedPath()
        if not resolved_path:
            return

        # path will be similar to the following:
        #     file:/C:/shaders/material_properties_test_data/mdl/int.mdl?watch=00000288087701f0
        resolved_url = omni.client.make_url(resolved_path.split("?")[0])

        stage = self._payload.get_stage()

        for shader_prim_path in self._shader_prim_paths:
            source_asset = self._get_shader_source_asset(shader_prim_path)
            if not source_asset:
                continue

            source_asset_url = omni.client.make_url(source_asset.resolvedPath)
            if omni.client.utils.equal_urls(resolved_url, source_asset_url):
                remove_properties_and_connections(stage.GetPrimAtPath(shader_prim_path))
                self._cancel_and_rebuild_task = run_coroutine(self.cancel_and_rebuild())
                return

    def _on_mdl_module_load(self, notice, sender) -> None:
        """
        Callback triggered when an MDL module has been loaded.
        When the list of MDL modules we are waiting on to load reaches 0 we trigger a rebuild
        """
        # The load callback is triggered any time we load a module into database.
        # If we are not waiting for anything we can early exit
        if not self._mdl_modules_pending_load:
            return

        resolved_path = notice.GetResolvedPath()
        if not resolved_path:
            return

        # path will be similar to the following:
        #     file:/C:/shaders/material_properties_test_data/mdl/int.mdl?watch=00000288087701f0
        resolved_url = omni.client.make_url(resolved_path.split("?")[0])

        for source_asset in self._mdl_modules_pending_load.copy():
            source_asset_url = omni.client.make_url(source_asset.resolvedPath)

            if omni.client.utils.equal_urls(resolved_url, source_asset_url):
                self._mdl_modules_pending_load.remove(source_asset)

        # Everything we need to draw the widget is loaded, rebuild
        if not self._mdl_modules_pending_load:
            self._cancel_and_rebuild_task = run_coroutine(self.cancel_and_rebuild())

    def clean(self) -> None:  # pragma: no cover
        """Cleans up resources and unsubscribes from events before the widget is destroyed."""

        if self._white_mode_sub:
            self._settings.unsubscribe_to_change_events(self._white_mode_sub)
            self._white_mode_sub = None

        self._mdl_module_load_sub.Revoke()
        self._mdl_module_load_sub = None

        self._mdl_module_reload_sub.Revoke()
        self._mdl_module_reload_sub = None

        if self._cancel_and_rebuild_task is not None:
            self._cancel_and_rebuild_task.cancel()
        self._cancel_and_rebuild_task = None

        super().clean()

    def _setup_white_mode(self) -> None:
        self._white_mode_sub = self._settings.subscribe_to_node_change_events(
            self.MATERIAL_WHITE_MODE_EXCEPTION_LIST_SETTING_PATH, self._on_white_mode_list_changed
        )

        self._on_white_mode_list_changed()

        self.add_custom_schema_attribute(
            self.MATERIAL_WHITE_MODE_EXCEPTION_INPUT,
            lambda p: p.IsA(UsdShade.Shader) or p.IsA(UsdShade.Material),
            self._on_create_white_mode_exception_bool,
            "",
            create_primspec_bool(False),
        )

    def _on_white_mode_list_changed(self, *args, **kwargs) -> None:
        try:
            mat_list = self._settings.get(self.MATERIAL_WHITE_MODE_EXCEPTION_LIST_SETTING_PATH)
            if mat_list:
                mat_names = mat_list.split(",")
                self._white_mode_exceptions = {mat_name.strip() for mat_name in mat_names}
            else:
                self._white_mode_exceptions.clear()

        except Exception:  # pylint: disable=broad-exception-caught  # pragma: no cover
            carb.log_error(f"Invalid white mode exception list: '{mat_list}'.")
            self._white_mode_exceptions.clear()

    def _on_create_white_mode_exception_bool(self, attribute_name: str, value_dict: Dict) -> UsdPropertyUiEntry:
        import omni.UsdMdl as UsdMdl

        if value_dict and self._shader_prim_paths:
            value_dict = copy.deepcopy(value_dict)  # make a deep copy so that we don't modify the reference
            custom_data = value_dict.get(Sdf.AttributeSpec.CustomDataKey, {})
            if custom_data:
                default_value = False
                # Since placeholder attribute cannot have "mixed" value, just use the last prim's value for now
                stage = self._payload.get_stage()
                last_shader_prim_path = self._shader_prim_paths[-1]
                shader = UsdShade.Shader.Get(stage, last_shader_prim_path)
                if shader:
                    subidentifier = shader.GetSourceAssetSubIdentifier(UsdMdl.Tokens.Mdl)
                    default_value = subidentifier in self._white_mode_exceptions

                custom_data[Sdf.AttributeSpec.DefaultValueKey] = default_value

        return UsdPropertyUiEntry(attribute_name, "Material Flags", value_dict, Usd.Attribute)

    def get_additional_kwargs(self, ui_prop: UsdPropertyUiEntry) -> Tuple[Union[dict | None], Union[dict | None]]:
        """Generates additional keyword arguments for the UI properties.

        Args:
            ui_prop (:obj:`UsdPropertyUiEntry`): The UI property for which to generate the kwargs."""

        def set_model_kwargs(widget_args: Union[dict | None], key: str, value: Any) -> dict:
            if not isinstance(widget_args, dict):
                widget_args = {}

            if "model_kwargs" not in widget_args:
                widget_args["model_kwargs"] = {}

            widget_args["model_kwargs"][key] = value
            return widget_args

        (additional_label_kwargs, additional_widget_kwargs) = super().get_additional_kwargs(ui_prop)

        if ui_prop.prop_name.startswith((UsdShade.Tokens.inputs, UsdShade.Tokens.outputs)):
            type_name = ui_prop.metadata.get(Sdf.PrimSpec.TypeNameKey, None)
            if type_name:
                if not isinstance(additional_label_kwargs, dict):
                    additional_label_kwargs = {}

                tooltip = f"{ui_prop.prop_name}({type_name})"

                render_type = ui_prop.metadata.get(Sdr.PropertyMetadata.RenderType, None)
                if render_type:
                    tooltip += f"\n\trender type: {render_type}"

                documentation = ui_prop.metadata.get(Sdf.AttributeSpec.DocumentationKey, None)
                if documentation:
                    tooltip += f"\n\n\t{documentation}"

                additional_label_kwargs["tooltip"] = tooltip

            if ui_prop.metadata.get("readonly", False):
                additional_widget_kwargs = set_model_kwargs(additional_widget_kwargs, "readonly", True)

            # ToDo:
            # Disable for now as it causes ports to be removed in the old Material Graph editor.
            # Re-enable when Matrial Graph 2.0 is ready.
            # However for backwards compatibility we might need to check which version of the Material Graph editor we are using.

            # This will cause the property to be removed from the stage if it is set to it's default value.
            # if ui_prop.prop_name.startswith(UsdShade.Tokens.inputs):
            #    additional_widget_kwargs = set_model_kwargs(additional_widget_kwargs, "remove_if_default", True)

        elif (ui_prop.prop_name == UsdShade.Tokens.infoId) or (
            ui_prop.prop_name.endswith(UsdShade.Tokens.subIdentifier)
        ):
            additional_widget_kwargs = set_model_kwargs(
                additional_widget_kwargs, "change_property_commands", ["SetUsdShadeInfoAttribute"]
            )

        return additional_label_kwargs, additional_widget_kwargs

    def _create_property_entry(self, name: str, display_group: str, metadata: dict, prop_type) -> UsdPropertyUiEntry:
        return UsdShadePropertyUiEntry(name, display_group, metadata, prop_type)

    def _get_builder_args(self) -> dict:
        """
        Return a dictionary of args that can be passed to the UsdShadePropertyPlaceholder builders.
        """
        return {}

    def _get_prim_properties(self, prim: Usd.Prim) -> List[UsdShadePropertyPlaceholder]:
        """
        Return the list of properties to be displayed in the UI for prim.
        Note: rather than return Usd.Property's we create UsdShadePropertyPlaceholder's.
            see UsdShadePropertyPlaceholder comments for more information as to why these are used.
        """

        # If we are waiting on MDL modules to be loaded into the registry, return an empty list.
        # When all of the modules we need have been loaded a callback will be triggered to rebuild the widget.
        if self._mdl_modules_pending_load:
            return []

        builder_args = self._get_builder_args()
        return GetPlaceholderPropertiesForPrim(prim, builder_args)

    def _path_requires_rebuild(self, path: Sdf.Path) -> bool:
        """
        Called from _on_usd_changed, a return value of True indicates that changes to the attribute at this path require a rebuild of the widget.
        The path will be from one of the following:
            1. Usd.Notice.ObjectsChanged.GetChangedInfoOnlyPaths()
            2. Usd.Notice.ObjectsChanged.GetResyncedPaths()
        """
        return False

    def _load_mdl_modules(self) -> None:
        """
        Gather a list of the MDL modules needed by this widget that need to be loaded into the registry.
        Modules will be loaded async, when they all have been loaded a callback wll be triggered to rebuild the widget.
        """
        import omni.UsdMdl as UsdMdl

        async def load_module(source_asset: Sdf.AssetPath) -> None:
            UsdMdl.RegistryUtils.AddModuleToRegistry(source_asset)

        for shader_prim_path in self._shader_prim_paths:
            source_asset = self._get_shader_source_asset(shader_prim_path)
            if source_asset and not UsdMdl.RegistryUtils.IsModuleLoaded(source_asset):
                self._mdl_modules_pending_load.add(source_asset)

        for source_asset in self._mdl_modules_pending_load:
            asyncio.ensure_future(load_module(source_asset))

    def on_new_payload(self, payload: PrimSelectionPayload) -> bool:
        """Handles a new payload for the widget.

        Args:
            payload (:obj:`PrimSelectionPayload`): The new payload to be handled by the widget.

        Returns:
            bool: Whether the payload can be represented by this widget."""

        self._shader_prim_paths.clear()
        self._mdl_modules_pending_load.clear()

        if not (payload and super().on_new_payload(payload)):
            return False

        for prim_path in payload:
            prim = self._get_prim(prim_path)

            if not prim:
                return False

            if not prim.IsA(self._schema):
                return False

            if self._schema_ignore and any(prim.IsA(schema) for schema in self._schema_ignore):
                return False

        return True

    def _identical_selection(self) -> bool:
        """
        If multiple prims are selected in the UI, this function will return True/False based on whether or not we determine the prims to be identical,
            which in turn drives which properties will be displayed in the UI.
        """
        prims = [self._get_prim(shader_prim_path) for shader_prim_path in self._shader_prim_paths]
        usdshade_shaders = [UsdShade.Shader(prim) for prim in prims]
        info = [get_shader_info(usdshade_shader) for usdshade_shader in usdshade_shaders]

        # Identical iff the info:* attributes for each shader has the same values.
        return all(x == info[0] for x in info)

    def _filter_props_to_build(self, props: List[UsdShadePropertyPlaceholder]) -> List[UsdShadePropertyPlaceholder]:
        """
        If multiple prims are selected and they are not identical then we will only show the [inputs, ui] properties.
        """
        if (len(self._payload) > 1) and (not self._identical_selection()):
            filtered = [prop for prop in props if prop.GetName().startswith((UsdShade.Tokens.inputs, "ui:"))]
            return super()._filter_props_to_build(filtered)

        return super()._filter_props_to_build(props)

    def _sort_properties_for_ui(self, props: List[UsdPropertyUiEntry]) -> List[UsdPropertyUiEntry]:
        """
        Sort by the following:
            1. annotation UI order - for inputs and outputs only
            2. the UI_ORDER declared above.
        """

        def sort_by_anno_ui_order(prefix: str, properties: List[UsdPropertyUiEntry]) -> None:
            """
            If the properties contain annotation metadata describing their ordering sort according to these values.
            """

            def get_anno_ui_order(prop: UsdPropertyUiEntry, default_value: int) -> int:
                custom_data = prop.metadata.get(Sdf.AttributeSpec.CustomDataKey, {})
                ui_order = custom_data.get("ui_order", {})
                return int(ui_order.get("order", custom_data.get("uiorder", default_value)))

            if len([prop for prop in properties if prop.prop_name.startswith(prefix)]) > 1:
                start = next(i for i, prop in enumerate(properties) if prop.prop_name.startswith(prefix))
                end = len(properties) - next(
                    i for i, prop in enumerate(properties[::-1]) if prop.prop_name.startswith(prefix)
                )
                properties_slice = properties[start:end]
                properties_slice.sort(key=lambda prop: get_anno_ui_order(prop, len(properties_slice)))
                properties[start:end] = properties_slice

        def sort_by_ui_order(prop: UsdPropertyUiEntry) -> float:
            """
            Sort properties according to UI_ORDER defined above.
            """

            prop_name_prefix = prop.prop_name.split(Sdf.Path.namespaceDelimiter)[0]

            key = len(self.UI_ORDER)
            if prop_name_prefix in self.UI_ORDER:
                key = self.UI_ORDER.index(prop_name_prefix)

                if prop_name_prefix == "info":
                    key += (prop.prop_name != UsdShade.Tokens.infoImplementationSource) * 0.1

            return key

        customized = super()._customize_props_layout(props)

        sort_by_anno_ui_order(UsdShade.Tokens.inputs, customized)
        sort_by_anno_ui_order(UsdShade.Tokens.outputs, customized)

        customized.sort(key=sort_by_ui_order)

        return customized

    def _customize_props_layout(self, props: List[UsdPropertyUiEntry]) -> List[UsdPropertyUiEntry]:
        """
        This function does the following:
            1. Sort the properties based on how we want them to appear in the UI.
            2. Adds build functions for any custom widgets.
            3. Set the collapsed state of UI groups.
        """

        customized = super()._customize_props_layout(props)
        for prop in props:
            if prop.prop_name.endswith(UsdShadePropertyPlaceholder.MATERIAL_INPUT_SUFFIX):
                prop.prop_name = prop.prop_name.replace(UsdShadePropertyPlaceholder.MATERIAL_INPUT_SUFFIX, "")

        customized = self._sort_properties_for_ui(customized)

        # Get any custom widget builders
        for ui_prop in customized:
            # Get any custom widget builders
            ui_prop.build_fn = get_custom_ui_prop_build_fn(ui_prop)

            # Collapse all groups that are not Inputs.
            ui_prop.display_group_collapsed = ui_prop.display_group not in ["Inputs"]

        # The following is for testing/debugging purposes and will be removed once this has undergone some user testing.
        if self.PRINT_LAYOUT:  # pragma: no cover
            print("\n\ncustomized:")
            for prop in customized:
                # if not prop.prop_name.startswith("inputs:"):
                #     continue
                print(f"\t{prop.prop_name}\t{prop.display_group}")
                if self.PRINT_LAYOUT_METADATA:
                    for k, v in prop.metadata.items():
                        if k == "documentation":
                            continue
                        print(f"\t\t{k} --> {v}")

        self._property_order = [
            prop.prop_name for prop in customized if prop.prop_name.startswith(UsdShade.Tokens.inputs)
        ]

        return customized

    def _on_usd_changed(self, notice: Usd.Notice.ObjectsChanged, stage: Usd.Stage) -> bool:
        """
        The USD properties have changed - most likely due to a user or script changing a property value.
        Check to see if the changed property affects this widget and if so trigger a complete rebuild of the widget if the change demands it.
        """
        if not self._payload:  # pragma: no cover
            return

        if stage != self._payload.get_stage():  # pragma: no cover
            return

        if not self._collapsable_frame:  # pragma: no cover
            return

        # Widget is pending rebuild, no need to check for dirty
        if self._pending_rebuild_task is not None:
            return

        # Changes to certain paths demand the widget be completely rebuilt.
        for path in notice.GetChangedInfoOnlyPaths():
            if self._path_requires_rebuild(path):
                self.request_rebuild()
                return

        for path in notice.GetResyncedPaths():
            if self._path_requires_rebuild(path):
                self.request_rebuild()
                return

        super()._on_usd_changed(notice=notice, stage=stage)
