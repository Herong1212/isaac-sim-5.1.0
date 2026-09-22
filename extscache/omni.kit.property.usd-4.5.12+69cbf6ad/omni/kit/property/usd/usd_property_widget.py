# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "UsdPropertyUiEntry",
    "UiDisplayGroup",
    "UsdPropertiesWidget",
    "SchemaPropertiesWidget",
    "MultiSchemaPropertiesWidget",
    "RawUsdPropertiesWidget",
]

import asyncio
import contextlib
import inspect
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Optional, Sequence, Set, Type, Union

import carb
import carb.profiler
import carb.settings
import omni.kit.app
import omni.kit.property.adapter.core as ac
import omni.kit.widget.context_menu
import omni.kit.window.property.managed_frame
import omni.ui as ui
import omni.usd
from carb.eventdispatcher import Event, get_eventdispatcher
from omni.kit.async_engine import run_coroutine
from omni.kit.window.property.templates import ButtonItem, SimplePropertyWidget
from pxr import Sdf, Tf, Trace, Usd, UsdUtils

from .message_bus_events import ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT
from .usd_model_base import UsdBase
from .usd_property_widget_builder import UsdPropertiesWidgetBuilder, get_ui_style

ENABLE_ADAPTER_SETTINGS = "/ext/omni.kit.property.usd/enableAdapter"

# Clipboard to store copied group properties
__properties_to_copy: Dict[Sdf.Path, Any] = {}


def get_group_properties_clipboard():
    """
    Get the group properties clipboard.
    """
    return __properties_to_copy


def set_group_properties_clipboard(properties_to_copy: Dict[Sdf.Path, Any]):
    """
    Set the group properties clipboard.
    """
    global __properties_to_copy
    __properties_to_copy = properties_to_copy


def create_primspec_token(tokens, default_token):
    """
    Create a primspec token.
    """
    return {Sdf.PrimSpec.TypeNameKey: "token", "allowedTokens": tokens, "customData": {"default": default_token}}


def create_primspec_float(default_float=0.0):
    """
    Create a primspec float.
    """
    return {Sdf.PrimSpec.TypeNameKey: "float", "customData": {"default": default_float}}


def create_primspec_int(default_int=0):
    """
    Create a primspec int.
    """
    return {Sdf.PrimSpec.TypeNameKey: "int", "customData": {"default": default_int}}


def create_primspec_bool(default_bool=False):
    """
    Create a primspec bool.
    """
    return {Sdf.PrimSpec.TypeNameKey: "bool", "customData": {"default": default_bool}}


def create_primspec_string(default_str=""):
    """
    Create a primspec string.
    """
    return {Sdf.PrimSpec.TypeNameKey: "string", "customData": {"default": default_str}}


def create_primspec_asset(default_asset_path=""):
    """
    Create a primspec asset.
    """
    return {Sdf.PrimSpec.TypeNameKey: "asset", "customData": {"default": Sdf.AssetPath(default_asset_path)}}


class UsdPropertyUiEntry:
    """
    A class to represent a USD property UI entry.
    """

    def __init__(
        self,
        prop_name: str,
        display_group: str,
        metadata,
        property_type,
        build_fn=None,
        display_group_collapsed: bool = False,
        prim_paths: List[Sdf.Path] = None,
    ):
        """
        Constructor.

        Args:
            prop_name: name of the Usd Property. This is not the display name.
            display_group: group of the Usd Property when displayed on UI.
            metadata: metadata associated with the Usd Property.
            property_type: type of the property. Either Usd.Property or Usd.Relationship.
            build_fn: a custom build function to build the UI. If not None the default builder will not be used.
            display_group_collapsed: if the display group should be collapsed. Group only collapses when ALL its contents request such.
            prim_paths: to override what prim paths this property will be built upon. Leave it to None to use default (currently selected paths, or last selected path if multi-edit is off).
        """
        self.prop_name = prop_name
        self.display_group = display_group
        self.display_group_collapsed = display_group_collapsed
        self.metadata = metadata
        self.property_type = property_type
        self.prim_paths = prim_paths
        self.build_fn = build_fn

        # keep lint happy
        get_ui_style()

    def __repr__(self):
        return f"<{self.__class__} prop_name:{self.prop_name} display_group:{self.display_group}>"

    def add_custom_metadata(self, key: str, value):
        """
        If value is not None, add it to the custom data of the metadata using the specified key.  Otherwise, remove that
        key from the custom data.

        Args:
            key: the key that should contain the custom metadata value
            value: the value that should be added to the custom metadata if not None
        """
        custom_data = self.metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        if value is not None:
            custom_data[key] = value
        elif key in custom_data:
            del custom_data[key]
        self.metadata[Sdf.PrimSpec.CustomDataKey] = custom_data

    def override_display_group(self, display_group: str, collapsed: bool = False):
        """
        Overrides the display group of the property. It only affects UI and DOES NOT write back DisplayGroup metadata to USD.

        Args:
            display_group: new display group to override to.
            collapsed: if the display group should be collapsed. Group only collapses when ALL its contents request such.
        """
        self.display_group = display_group
        self.display_group_collapsed = collapsed

    def override_display_name(self, display_name: str):
        """
        Overrides the display name of the property. It only affects UI and DOES NOT write back DisplayName metadata to USD.

        Args:
            display_group: new display group to override to.
        """
        self.metadata[Sdf.PropertySpec.DisplayNameKey] = display_name

    def override_doc_string(self, doc_string: str):
        """
        Overrides the doc string of the property, which is used for tooltips. It only affects UI and DOES NOT write
        back Documentation metadata to USD.

        Args:
            doc_string: new doc string
        """
        self.metadata[Sdf.PropertySpec.DocumentationKey] = doc_string

    # for backward compatibility
    def __getitem__(self, key):
        lookup = {0: self.prop_name, 1: self.display_group, 2: self.metadata}
        if key in lookup:
            return lookup[key]
        return None

    @property
    def attr_name(self):
        """
        Get the attribute name of the property.
        """
        return self.prop_name

    @attr_name.setter
    def attr_name(self, value):
        """
        Set the attribute name of the property.

        Args:
            value: the new attribute name
        """
        self.prop_name = value

    def get_nested_display_groups(self):
        """
        Get the nested display groups of the property.

        Returns:
            list: the nested display groups
        """
        if len(self.display_group) == 0:
            return []
        # Per USD documentation nested display groups are separated by colon
        return self.display_group.split(":")

    def __eq__(self, other):
        """
        Check if the property is equal to another property.

        Args:
            other: the other property

        Returns:
            bool: True if the properties are equal, False otherwise
        """
        return (
            type(self) == type(other)  # pylint: disable=unidiomatic-typecheck
            and self.prop_name == other.prop_name
            and self.display_group == other.display_group
            and self._compare_metadata(self.metadata, other.metadata)
            and self.property_type == other.property_type
            and self.prim_paths == other.prim_paths
        )

    def _compare_metadata(self, meta1, meta2) -> bool:
        """
        Compare two metadata dictionaries.

        Args:
            meta1: the first metadata dictionary
            meta2: the second metadata dictionary

        Returns:
            bool: True if the metadata is equal, False otherwise
        """
        ignored_metadata = {"default", "colorSpace"}
        for key, value in meta1.items():  # noqa: SIM111
            if key not in ignored_metadata and (key not in meta2 or meta2[key] != value):  # noqa: SIM111
                return False

        for key, value in meta2.items():  # noqa: SIM111
            if key not in ignored_metadata and (key not in meta1 or meta1[key] != value):  # noqa: SIM111
                return False

        return True


class UiDisplayGroup:
    """
    A class to represent a USD display group.
    """

    def __init__(
        self, name: str, ordered: bool, props: Optional[List[UsdPropertyUiEntry]] = None, ignore_groups: bool = False
    ):
        self.name = name
        self.sub_groups = DefaultDict()
        self.props = []
        self._ordered = ordered
        self._ordered_items = []
        self._ignore_groups = ignore_groups

        if props:
            for prop in props:
                self.add_prop(prop, prop.get_nested_display_groups() if not self._ignore_groups else [])

    def add_prop(self, prop: UsdPropertyUiEntry, nested_groups: List[str]) -> None:
        """
        Add a property to the display group.
        """
        if len(nested_groups) == 0:
            self.props.append(prop)
            if self._ordered:
                self._ordered_items.append(prop)

        else:
            sub_group_name = nested_groups[0]
            sub_group = self.sub_groups.setdefault(sub_group_name, UiDisplayGroup(sub_group_name, self._ordered))
            sub_group.add_prop(prop, nested_groups[1:])

            if self._ordered and sub_group_name not in self._ordered_items:
                self._ordered_items.append(sub_group_name)

    def get_children(self) -> List[Union[Type["UiDisplayGroup"] | UsdPropertyUiEntry]]:
        """
        Get the children of the display group.
        """
        children = []

        if not self._ordered:
            children = list(self.sub_groups.values())
            children.extend(prop for prop in self.props if prop.display_group and not self._ignore_groups)

        else:
            for item in self._ordered_items:
                if isinstance(item, UsdPropertyUiEntry):
                    if item.display_group and not self._ignore_groups:
                        children.append(item)
                else:
                    children.append(self.sub_groups[item])

        return children

    def get_sub_props(self) -> List[UsdPropertyUiEntry]:
        """
        Get the sub properties of the display group.
        """
        sub_props = []

        for display_group in self.sub_groups.values():
            sub_props.extend(display_group.get_sub_props())

        sub_props.extend(self.props)

        return sub_props

    def __repr__(self):
        return f"<{self.__class__} name:{self.name} sub_groups:{self.sub_groups}>"


class UsdPropertiesWidget(SimplePropertyWidget):
    """
    UsdPropertiesWidget provides functionalities to automatically populates UsdProperties on given prim(s). The UI will
    and models be generated according to UsdProperties's value type. Multi-prim editing works for shared Properties
    between all selected prims if instantiated with multi_edit = True.
    """

    def __init__(
        self,
        title: str,
        collapsed: bool,
        multi_edit: bool = True,
        enable_adapter: bool = False,
        maintain_property_order: bool = False,
    ):
        """
        Constructor.

        Args:
            title (str): title of the widget.
            collapsed (bool): whether the collapsable frame should be collapsed for this widget.
            multi_edit (bool): whether multi-editing is supported.
            enable_adapter (bool): use stage_adapters
            maintain_property_order (bool): _customize_props_layout returns a list of properties to display on the widget.
        """
        # doc compiler cannot handle full info
        # title (str): title of the widget.
        # collapsed (bool): whether the collapsable frame should be collapsed for this widget.
        # multi_edit (bool): whether multi-editing is supported.
        #     If False, properties will only be collected from the last selected prim.
        #     If True, shared properties among all selected prims will be collected.
        # enable_adapter (bool): use stage_adapters
        # maintain_property_order (bool): _customize_props_layout returns a list of properties to display on the widget.
        #     If False - nested properties/pages/frames are displayed first, followed by the non nested properties
        #     e.g. page, page, property, property
        #     If True - the order in which the properties appear will be the order of this list.
        #     This allows for something like: property, page, page, property
        super().__init__(title=title, collapsed=collapsed)
        self._multi_edit = multi_edit
        self._models = defaultdict(list)
        self._bus_sub = None
        self._listener = None
        self._listener_adapters = []
        self._pending_dirty_task_or_future = None
        self._pending_dirty_paths = set()
        self._group_menu_entries = []
        self._stage_adapters = []
        self.__custom_attribute = {}
        self.__custom_attribute_values = {}
        self._enable_adapter = carb.settings.get_settings().get_as_bool(ENABLE_ADAPTER_SETTINGS) and enable_adapter
        self._any_item_visible = False
        self._fabric_listener = None
        self._maintain_property_order = maintain_property_order

    def clean(self):
        """
        See PropertyWidget.clean
        """
        self.reset_models()
        super().clean()

    def reset(self):
        """
        See PropertyWidget.reset
        """
        self.reset_models()
        super().reset()

    def reset_models(self):
        """
        Reset model states. Release allocations etc.
        """
        # models can be shared among multiple prims. Only clean once!
        unique_models = set()
        if self._models is not None:
            for models in self._models.values():
                for model in models:
                    unique_models.add(model)
        for model in unique_models:
            model.clean()
        self._models = defaultdict(list)
        if self._listener:
            self._listener.Revoke()
        self._listener = None
        for listener in self._listener_adapters:
            listener.destroy()
        self._listener_adapters = []
        self._fabric_listener = None
        self._bus_sub = None
        if self._pending_dirty_task_or_future is not None:  # pragma: no cover
            self._pending_dirty_task_or_future.cancel()
            self._pending_dirty_task_or_future = None
        self._pending_dirty_paths.clear()
        for entry in self._group_menu_entries:
            entry.release()
        self._group_menu_entries.clear()

    def get_additional_kwargs(self, ui_prop: UsdPropertyUiEntry):
        """
        Override this function if you want to supply additional arguments when building the label or ui widget.
        """
        additional_label_kwargs = None
        additional_widget_kwargs = None
        if hasattr(ui_prop, "model_kwargs"):
            additional_widget_kwargs = ui_prop.model_kwargs

        return additional_label_kwargs, additional_widget_kwargs

    def get_valid_stage_adapter(self, prim_path, attr_name):
        """
        Gets stage adapter for prim.

        Args:
            prim_path (str): prim path.
            attr_name (str): attribute/property name.
        Returns:
            StageAdapter: Stage adapter for prim/attribute.
        """
        if len(attr_name) > 0:
            for stage in self._stage_adapters:
                with contextlib.suppress(Exception):
                    if stage.GetAttributeAtPath(prim_path.AppendProperty(attr_name)):
                        return stage

        return None

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        """
        Override this function to customize property building.
        """

        # override prim paths to build if UsdPropertyUiEntry specifies one
        if ui_prop.prim_paths:
            prim_paths = ui_prop.prim_paths

        build_fn = ui_prop.build_fn if ui_prop.build_fn else UsdPropertiesWidgetBuilder.build  # noqa: F405
        additional_label_kwargs, additional_widget_kwargs = self.get_additional_kwargs(ui_prop)

        # highlight filter text
        if self._filter.name:
            if additional_label_kwargs is None:
                additional_label_kwargs = {}
            additional_label_kwargs["highlight"] = self._filter.name

        model_stage = self.get_valid_stage_adapter(prim_paths[0], ui_prop.prop_name) or stage
        models = build_fn(
            model_stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            prim_paths,
            additional_label_kwargs,
            additional_widget_kwargs,
        )
        if models:
            if not isinstance(models, list):
                models = [models]
            for model in models:
                for prim_path in prim_paths:
                    self._models[prim_path.AppendProperty(ui_prop.prop_name)].append(model)

        return models

    def _build_nested_group_props(self, stage, prim_paths, props):
        collapse_frame = len(props) > 0
        # we need to build those property in 2 different possible locations
        for prop in props:
            self.build_property_item(stage, prop, prim_paths)
            collapse_frame &= prop.display_group_collapsed

        return collapse_frame

    def _build_framestack(self, prefix, display_group):
        wid = prefix + ":" + display_group.name
        frame = ui.CollapsableFrame(
            title=display_group.name,
            build_header_fn=lambda collapsed, text, id=id: self._build_frame_header(collapsed, text, wid),
            name="subFrame",
        )
        omni.kit.window.property.managed_frame.prep(frame, group_name=prefix)
        with frame:
            self._build_header_context_menu(group_name=display_group.name, group_id=wid, props=None)
            stack = ui.VStack(height=0, spacing=5, name="frame_v_stack")
        return (frame, stack, wid)

    def _build_extra_properties(
        self, stage, prim_paths: list, display_group: UiDisplayGroup, prefix: str, sub_props: List[UsdPropertyUiEntry]
    ):
        extra_group_name = "Extra Properties"
        extra_group_id = prefix + ":" + extra_group_name
        cframe = ui.CollapsableFrame(
            title=extra_group_name,
            build_header_fn=lambda collapsed, text, id=extra_group_id: self._build_frame_header(collapsed, text, id),
            name="subFrame",
        )
        with cframe:
            with ui.VStack(height=0, spacing=5, name="frame_v_stack"):
                self._build_nested_group_props(stage, prim_paths, display_group.props)

            self._build_header_context_menu(group_name=extra_group_name, group_id=extra_group_id, props=sub_props)
        omni.kit.window.property.managed_frame.prep(cframe, group_name=prefix)

    def _build_nested_group_frame(
        self,
        stage,
        prim_paths: list,
        display_group: UiDisplayGroup,
        level: int,
        prefix: str,
        ignore_collapsed: bool = False,
    ):
        # Only create a collapsable frame if the group is not "" (for root level group)
        if display_group and len(display_group.name) > 0:
            (frame, stack, wid) = self._build_framestack(prefix, display_group)
        else:
            wid = prefix
            frame = ui.Frame(name="subFrame")
            with frame:
                stack = ui.VStack(height=0, spacing=5, name="frame_v_stack")

        sub_props = display_group.get_sub_props()

        with frame:
            with stack:
                collapse = len(display_group.props) > 0

                for child in display_group.get_children():
                    if isinstance(child, UiDisplayGroup):
                        params = [
                            param.name
                            for param in inspect.signature(self._build_nested_group_frame).parameters.values()
                        ]
                        if "ignore_collapsed" in params:
                            self._build_nested_group_frame(stage, prim_paths, child, level + 1, wid, ignore_collapsed)
                        else:
                            self._build_nested_group_frame(stage, prim_paths, child, level + 1, wid)
                    else:
                        self.build_property_item(stage, child, prim_paths)
                        collapse &= child.display_group_collapsed

                if level == 0:
                    # Only do "Extra Properties" for root level group
                    if len(display_group.sub_groups) > 0 and len(display_group.props) > 0:
                        self._build_extra_properties(stage, prim_paths, display_group, prefix, sub_props)

                    else:
                        collapse = self._build_nested_group_props(stage, prim_paths, display_group.props)

                if (
                    collapse
                    and not ignore_collapsed
                    and isinstance(frame, ui.CollapsableFrame)
                    and not self._filter.name
                    and omni.kit.window.property.managed_frame.get_collapsed_state(f"{prefix}/{frame.title}") is None
                ):

                    frame.collapsed = collapse

            # if level is 0, this is the root level group, and we use the self._title for its name
            self._build_header_context_menu(
                group_name=display_group.name if level > 0 else self._title, group_id=wid, props=sub_props
            )

    async def _build_schema_group_frames(self, oframe, stage, display_group: UiDisplayGroup, prim):
        """
        Build schema API widget with "Remove" button or "padlock" icon.
        """
        from omni.kit.property.usd import RegisteredSchemaCodes, is_registered_schema

        def build_display_group(prim, api_prop_names):
            def display_name(ui_prop):
                return UsdPropertiesWidgetBuilder.get_display_name(ui_prop.prop_name, ui_prop.metadata)  # noqa: F405

            def is_schema(ui_prop, api_prop_names):
                return ui_prop.prop_name in api_prop_names

            shared_props = self._get_shared_properties_from_selected_prims_with_prop_names(prim, api_prop_names)
            if not shared_props:  # pragma: no cover
                return UiDisplayGroup("", False, [], ignore_groups=True)

            shared_props = self._customize_props_layout(shared_props)

            # _customize_props_layout may override display names, so we apply the user filter here rather than
            # earlier in _filter_props_to_build
            if not self._filter.name:
                filtered_props = [ui_prop for ui_prop in shared_props if is_schema(ui_prop, api_prop_names)]
            else:
                filtered_props = [
                    ui_prop
                    for ui_prop in shared_props
                    if self._filter.matches(display_name(ui_prop)) and is_schema(ui_prop, api_prop_names)
                ]
                if not filtered_props:
                    return UiDisplayGroup("", False, [], ignore_groups=True)

            # build display bug ignore groups
            return UiDisplayGroup("", False, filtered_props, ignore_groups=True)

        if stage:
            from .widgets import ICON_PATH

            def delete_api(api_schema_full):
                (api_schema, api_instance) = schema_reg.GetTypeNameAndInstance(api_schema_full)
                omni.kit.commands.execute(
                    "RemoveAPIFromPrims",
                    paths=self._payload.get_paths(),
                    api_schema=api_schema,
                    api_instance=api_instance,
                )

            schema_reg = Usd.SchemaRegistry()
            icon_path = f"{ICON_PATH}/Locked Value.svg"
            schema_list = []
            for api_schema_full in prim.GetAppliedSchemas():
                (api_schema, api_instance) = schema_reg.GetTypeNameAndInstance(api_schema_full)
                api_prim_def = schema_reg.FindAppliedAPIPrimDefinition(api_schema)
                if api_prim_def:
                    api_prop_names = api_prim_def.GetPropertyNames()
                    if api_instance:
                        api_prop_names = [
                            prop_name.replace("__INSTANCE_NAME__", api_instance) for prop_name in api_prop_names
                        ]

                schema_list.append((api_schema_full, api_prop_names))

            # some schemas can have properties from the other schemas (LightAPI), so remove them
            updated = True
            while updated:
                updated = False
                for index, (api_schema_full, api_prop_names) in enumerate(schema_list):
                    for _, api_prop_names2 in schema_list:
                        if api_prop_names != api_prop_names2:
                            api_prop_names_new = list(set(api_prop_names) - set(api_prop_names2))
                            if len(api_prop_names) != len(api_prop_names_new):
                                updated = True
                                schema_list[index] = (api_schema_full, api_prop_names_new)
                                break
                    if updated:
                        break

            cls_name = self.__class__.__name__
            if schema_list:
                oframe.visible = True
                with oframe:
                    with ui.VStack(height=0, spacing=5, name="frame_v_stack"):
                        for api_schema_full, api_prop_names in schema_list:
                            # ignore private APIs
                            schema_types = [cls_name, prim.GetTypeName()]
                            widget_name, schema_codes = is_registered_schema(schema_types, api_schema_full)
                            if schema_codes & RegisteredSchemaCodes.PRIVATE:
                                continue

                            if (
                                schema_codes & RegisteredSchemaCodes.NO_REMOVE and widget_name in schema_types
                            ) or not carb.settings.get_settings().get("ext/omni.kit.property.usd/removeSchemaAPI"):
                                button_item = ButtonItem(icon=icon_path, width=16, height=16, enabled=False)
                            else:
                                button_item = ButtonItem(
                                    "Remove",
                                    width=16,
                                    height=16,
                                    callback_fn=lambda s=api_schema_full: delete_api(s),
                                    identifier=f"{api_schema_full}.remove_api_schema_button",
                                )

                            prim_paths = self._payload[-1:]
                            new_display_group = build_display_group(prim, api_prop_names)
                            schema_group_id = f"Schema:{api_schema_full}"

                            sframe = ui.CollapsableFrame(
                                title=api_schema_full,
                                build_header_fn=lambda collapsed, text, id=schema_group_id, bi=[
                                    button_item
                                ]: self._build_frame_header_with_buttons(collapsed, text, id, bi),
                                name="schemaFrame",
                                collapsed=True,
                            )
                            with sframe:
                                with ui.VStack(height=0, spacing=5, name="frame_v_stack"):
                                    params = [
                                        param.name
                                        for param in inspect.signature(
                                            self._build_nested_group_frame
                                        ).parameters.values()
                                    ]
                                    if "ignore_collapsed" in params:
                                        self._build_nested_group_frame(
                                            stage,
                                            prim_paths,
                                            new_display_group,
                                            0,
                                            api_schema_full,
                                            ignore_collapsed=True,
                                        )
                                    else:
                                        self._build_nested_group_frame(
                                            stage, prim_paths, new_display_group, 0, api_schema_full
                                        )

                                self._build_header_context_menu(
                                    group_name=api_schema_full,
                                    group_id=schema_group_id,
                                    props=new_display_group.get_sub_props(),
                                )
                            omni.kit.window.property.managed_frame.prep(sframe, group_name="Schema")

    def build_nested_group_frames(self, stage, display_group: UiDisplayGroup):
        """
        Override this function to build group frames differently.
        """
        if self._multi_edit:
            prim_paths = self._payload.get_paths()
        else:
            prim_paths = self._payload[-1:]

        self._build_nested_group_frame(stage, prim_paths, display_group, 0, self._title)

        # if we have subFrame we need the main frame to assume the groupFrame styling
        if len(display_group.sub_groups) > 0:
            # here we reach into the Parent class frame
            self._collapsable_frame.name = "groupFrame"

    def build_items(self):
        """
        See SimplePropertyWidget.build_items
        """
        self.reset()

        if not self._payload or len(self._payload) == 0:
            return

        last_prim = self._get_prim(self._payload[-1])
        stage = last_prim.GetStage() if last_prim else None

        if not stage:  # pragma: no cover
            return

        self._listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)

        shared_props = self._get_shared_properties_from_selected_prims(last_prim)
        if not shared_props:  # pragma: no cover
            return

        shared_props = self._customize_props_layout(shared_props)

        # _customize_props_layout may override display names, so we apply the user filter here rather than
        # earlier in _filter_props_to_build
        if not self._filter.name:
            filtered_props = shared_props
        else:

            def display_name(ui_prop):
                return UsdPropertiesWidgetBuilder.get_display_name(ui_prop.prop_name, ui_prop.metadata)  # noqa: F405

            filtered_props = [ui_prop for ui_prop in shared_props if self._filter.matches(display_name(ui_prop))]
            if not filtered_props:
                return
        self._any_item_visible = True

        attr_names = [prop.prop_name for prop in filtered_props]
        self.add_listener_adapters(attr_names)

        self._bus_sub = get_eventdispatcher().observe_event(
            event_name=ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT, on_event=self._on_bus_event
        )

        grouped_props = UiDisplayGroup("", self._maintain_property_order, filtered_props)
        self.build_nested_group_frames(stage, grouped_props)
        if (
            hasattr(self, "show_schemas")
            and self.show_schemas()
            and carb.settings.get_settings().get("ext/omni.kit.property.usd/showSchemaAPI")
        ):
            frame = ui.Frame(visible=False)
            asyncio.ensure_future(self._build_schema_group_frames(frame, stage, grouped_props, last_prim))

    def _build_header_context_menu(self, group_name: str, group_id: str, props: List[UsdPropertyUiEntry] = None):
        """
        Override this function to build the context menu when right click on a Collapsable group header

        Args:
            group_name: Display name of the group. If it's not a subgroup, it's the title of the widget.
            group_id: A unique identifier for group context menu.
            props: Properties under this group. It contains all properties in its subgroups as well.
        """
        self._build_group_builtin_header_context_menu(group_name, group_id, props)
        self._build_group_additional_header_context_menu(group_name, group_id, props)

    def _build_group_builtin_header_context_menu(
        self, group_name: str, group_id: str, props: List[UsdPropertyUiEntry] = None
    ):
        from .usd_attribute_model import GfVecAttributeSingleChannelModel

        prop_names: Set[str] = set()
        if props:
            for prop in props:
                prop_names.add(prop.prop_name)

        def can_copy(objects: Any):
            # Only support single selection copy oer OM-20206
            return len(self._payload) == 1

        def on_copy(objects: Any):
            visited_models = set()

            properties_to_copy: Dict[Sdf.Path, Any] = {}
            for models in self._models.values():
                for model in models:
                    if model in visited_models:
                        continue

                    visited_models.add(model)

                    # Skip "Mixed"
                    if model.is_ambiguous():  # pragma: no cover
                        continue

                    paths = model.get_property_paths()
                    if paths:
                        # Copy from the last path
                        # In theory if the value is not mixed all paths should have same value, so which one to pick doesn't matter
                        last_path = paths[-1]

                        # Only copy from the properties from this group
                        if props is not None and last_path.name not in prop_names:
                            continue

                        if issubclass(type(model), UsdBase):
                            # No need to copy single channel model. Each vector attribute also has a GfVecAttributeModel
                            if isinstance(model, GfVecAttributeSingleChannelModel):
                                continue

                            properties_to_copy[paths[-1]] = model.get_value()

            if properties_to_copy:
                set_group_properties_clipboard(properties_to_copy)

        menu = {
            "name": f'Copy All Property Values in "{group_name}"',
            "show_fn": lambda objects: True,
            "enabled_fn": can_copy,
            "onclick_fn": on_copy,
        }

        self._group_menu_entries.append(self._register_header_context_menu_entry(menu, group_id))

        def on_paste(objects: Any):
            properties_to_copy = get_group_properties_clipboard()
            if not properties_to_copy:  # pragma: no cover
                return

            unique_model_prim_paths: Set[Sdf.Path] = set()
            for prop_path in self._models:
                unique_model_prim_paths.add(prop_path.GetPrimPath())

            with omni.kit.undo.group():
                try:
                    for path, value in properties_to_copy.items():
                        for prim_path in unique_model_prim_paths:

                            # Only paste to the properties in this group
                            if props is not None and path.name not in prop_names:
                                continue

                            paste_to_model_path = prim_path.AppendProperty(path.name)
                            models = self._models.get(paste_to_model_path, [])
                            for model in models:
                                if isinstance(model, GfVecAttributeSingleChannelModel):
                                    continue
                                model.set_value(value)
                except Exception:  # pylint: disable=broad-exception-caught  # pragma: no cover
                    import traceback

                    carb.log_error(f"on_paste error:{traceback.format_exc()}")

        menu = {
            "name": f'Paste All Property Values to "{group_name}"',
            "show_fn": lambda objects: True,
            "enabled_fn": lambda objects: get_group_properties_clipboard(),
            "onclick_fn": on_paste,
        }
        self._group_menu_entries.append(self._register_header_context_menu_entry(menu, group_id))

        def can_reset(objects: Any):
            visited_models = set()

            for models in self._models.values():
                for model in models:
                    if model in visited_models:
                        continue

                    visited_models.add(model)

                    paths = model.get_property_paths()
                    if paths:

                        last_path = paths[-1]

                        # Only reset from the properties from this group
                        if props is not None and last_path.name not in prop_names:
                            continue

                        if issubclass(type(model), UsdBase) and model.is_different_from_default():
                            return True
            return False

        def on_reset(objects: Any):
            visited_models = set()

            for models in self._models.values():
                for model in models:
                    if model in visited_models:
                        continue

                    visited_models.add(model)

                    paths = model.get_property_paths()
                    if paths:

                        last_path = paths[-1]

                        # Only reset from the properties from this group
                        if props is not None and last_path.name not in prop_names:
                            continue

                        if issubclass(type(model), UsdBase):
                            model.set_default()

        menu = {
            "name": f'Reset All Property Values in "{group_name}"',
            "show_fn": lambda objects: True,
            "enabled_fn": can_reset,
            "onclick_fn": on_reset,
        }

        self._group_menu_entries.append(self._register_header_context_menu_entry(menu, group_id))

    def _build_group_additional_header_context_menu(
        self, group_name: str, group_id: str, props: List[UsdPropertyUiEntry] = None
    ):
        """
        Override this function to build the additional context menu to Kit's built-in ones when right click on a Collapsable group header

        Args:
            group_name: Display name of the group. If it's not a subgroup, it's the title of the widget.
            group_id: A unique identifier for group context menu.
            props: Properties under this group. It contains all properties in its subgroups as well.
        """

    def _register_header_context_menu_entry(self, menu: Dict, group_id: str):
        """
        Registers a menu entry to Collapsable group header

        Args:
            menu: The menu entry to be registered.
            group_id: A unique identifier for group context menu.

        Return:
            The subscription object of the menu entry to be kept alive during menu's life span.
        """
        return omni.kit.widget.context_menu.add_menu(menu, "group_context_menu." + group_id, "omni.kit.window.property")

    def _filter_props_to_build(self, props):
        """
        When deriving from UsdPropertiesWidget, override this function to filter properties to build.
        Args:
            props: List of Usd.Property on a selected prim.
        """
        return [prop for prop in props if not prop.IsHidden()]

    def _filter_props_to_build_with_prop_names(self, props, prop_names):
        """
        When deriving from UsdPropertiesWidget, override this function to filter properties to build.
        Args:
            props: List of Usd.Property on a selected prim.
            prop_names: List of property names to filter.
        """
        return [prop for prop in props if prop.GetName() in prop_names and not prop.IsHidden()]

    def _customize_props_layout(self, props):
        """
        When deriving from UsdPropertiesWidget, override this function to reorder/regroup properties to build.
        To reorder the properties display order, reorder entries in props list.
        To override display group or name, call prop.override_display_group or prop.override_display_name respectively.
        If you want to hide/add certain property, remove/add them to the list.

        NOTE: All above changes won't go back to USD, they're pure UI overrides.

        Args:
            props: List of Tuple(property_name, property_group, metadata)

        Example:

            for prop in props:
                # Change display group:
                prop.override_display_group("New Display Group")

                # Change display name (you can change other metadata, it won't be write back to USD, only affect UI):
                prop.override_display_name("New Display Name")

            # add additional "property" that doesn't exist.
            props.append(UsdPropertyUiEntry("PlaceHolder", "Group", { Sdf.PrimSpec.TypeNameKey: "bool"}, Usd.Property))
        """

        self.add_custom_schema_attributes_to_props(props)
        return props

    @Trace.TraceFunction
    def _on_usd_changed(self, notice, stage):
        carb.profiler.begin(1, "UsdPropertyWidget._on_usd_changed")
        try:
            if stage != self._payload.get_stage() and isinstance(stage, Usd.Stage):  # pragma: no cover
                return

            if not self._collapsable_frame:  # pragma: no cover
                return

            if len(self._payload) == 0:  # pragma: no cover
                return

            # Widget is pending rebuild, no need to check for dirty
            if self._pending_rebuild_task is not None:
                return

            resynced_paths = []
            changed_info_paths = []
            if not isinstance(stage, Usd.Stage):
                for valid_stage in self._stage_adapters:
                    ret, resynced_paths, changed_info_paths = valid_stage.get_notice_paths(stage, notice)
                    if ret:
                        break
            else:
                if stage != self._payload.get_stage():
                    return
                resynced_paths = notice.GetResyncedPaths()
                changed_info_paths = notice.GetChangedInfoOnlyPaths()

            dirty_paths = set()

            for path in resynced_paths:
                if path in self._payload:
                    self.request_rebuild()
                    return

                # layer was deleted
                if path == Sdf.Path.absoluteRootPath:
                    payload = self._payload.cleanup_payload()
                    # where prims removed from payload as they were part of the layer that was deleted?
                    if payload != self._payload:
                        import omni.kit.window.property as p

                        p.get_window().notify("prim", payload)
                    else:
                        self.request_rebuild()
                    return

            for path in resynced_paths:
                if path.GetPrimPath() in self._payload:
                    prop = stage.GetPropertyAtPath(path)
                    # If prop is added or removed, rebuild frame
                    # TODO only check against the properties this widget cares about
                    if (not prop.IsValid()) != (self._models.get(path) is None):
                        self.request_rebuild()
                        return
                    # else trigger existing model to reload the value
                    dirty_paths.add(path)

            for path in changed_info_paths:
                dirty_paths.add(path)

            self._pending_dirty_paths.update(dirty_paths)

            if self._pending_dirty_task_or_future is None:
                self._pending_dirty_task_or_future = run_coroutine(self._delayed_dirty_handler())
        finally:
            carb.profiler.end(1)

    def _on_bus_event(self, event: Event):
        if not self._collapsable_frame:  # pragma: no cover
            return

        if len(self._payload) == 0:  # pragma: no cover
            return

        # Widget is pending rebuild, no need to check for dirty
        if self._pending_rebuild_task is not None:  # pragma: no cover
            return

        stage = event["stage"] if "stage" in event else None
        if not stage:
            # If the event is passed from C++, it can not pass down a stage pointer, but stage id instead.
            stage_id = event["stage_id"] if "stage_id" in event else None
            if stage_id is not None:
                cache = UsdUtils.StageCache.Get()
                stage = cache.Find(Usd.StageCache.Id.FromLongInt(stage_id))

        if stage is not None and stage != self._payload.get_stage():
            return

        path = event["path"]
        self._pending_dirty_paths.add(Sdf.Path(path))
        if self._pending_dirty_task_or_future is None:
            self._pending_dirty_task_or_future = run_coroutine(self._delayed_dirty_handler())

    def _get_prim(self, prim_path):
        if prim_path:
            stage = self._payload.get_stage()
            if stage:
                return stage.GetPrimAtPath(prim_path)
        return None

    def _get_prim_properties(self, prim: Usd.Prim):
        """UsdPrim.GetProperties() returns a vector of UsdProperty's.
        This method can be overridden in a derived class if an alternate class is holding the data.
        If this is the case such a derived class would need to implement several of the methods in UsdProperty
        such as GetName(), GetAllMetadata(), etc in order to property integrate it with this widget.
        """

        return prim.GetProperties()

    def _create_property_entry(self, name: str, display_group: str, metadata: dict, prop_type) -> UsdPropertyUiEntry:
        """Override in a derived class if UsdPropertyUiEntry needs to be constructed differently or if
        a class derived from UsdPropertyUiEntry is required, which would be the case if one of the UsdPropertyUiEntry methods
        needs to be overridden.
        """
        return UsdPropertyUiEntry(name, display_group, metadata, prop_type)

    def _get_shared_properties_from_selected_prims(self, anchor_prim):
        shared_props_dict = None

        if self._multi_edit:
            prim_paths = self._payload.get_paths()
        else:
            prim_paths = self._payload[-1:]

        usd_stage = self._payload.get_stage()
        if not usd_stage:  # pragma: no cover
            return None

        valid_stages = self._stage_adapters if self._stage_adapters else [usd_stage]
        for prim_path in prim_paths:
            if not prim_path:  # pragma: no cover
                continue
            prop_dict = {}

            for stage in valid_stages:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:  # pragma: no cover
                    continue

                props = self._get_prim_properties(prim)
                props = self._filter_props_to_build(props)

                for prop in props:
                    if prop.IsHidden():  # pragma: no cover
                        continue

                    prop_name: str = prop.GetName()
                    if prop_name not in prop_dict:
                        prop_type = prop.GetPropertyType() if hasattr(prop, "GetPropertyType") else type(prop)
                        prop_dict[prop_name] = self._create_property_entry(
                            prop_name, prop.GetDisplayGroup(), prop.GetAllMetadata(), prop_type
                        )

            if shared_props_dict is None:
                shared_props_dict = prop_dict
            else:
                # Find intersection of the dicts
                intersect_shared_props = {}
                for prop_name, prop_info in shared_props_dict.items():
                    if prop_dict.get(prop_name) == prop_info:
                        intersect_shared_props[prop_name] = prop_info

                if len(intersect_shared_props) == 0:  # pragma: no cover
                    # No intersection, nothing to build
                    # early return
                    return None

                shared_props_dict = intersect_shared_props

        shared_props = list(shared_props_dict.values())
        # Sort properties to PropertyOrder using the last selected object
        order = anchor_prim.GetPropertyOrder()
        shared_prop_order = []
        shared_prop_unordered = []
        for prop in shared_props:
            if prop[0] in order:
                shared_prop_order.append(prop[0])
            else:
                shared_prop_unordered.append(prop[0])

        shared_prop_order.extend(shared_prop_unordered)
        return sorted(shared_props, key=lambda x: shared_prop_order.index(x[0]))

    def _get_shared_properties_from_selected_prims_with_prop_names(self, anchor_prim, prop_names):
        shared_props_dict = None

        if self._multi_edit:
            prim_paths = self._payload.get_paths()
        else:
            prim_paths = self._payload[-1:]

        usd_stage = self._payload.get_stage()
        if not usd_stage:  # pragma: no cover
            return None

        valid_stages = self._stage_adapters if self._stage_adapters else [usd_stage]
        for prim_path in prim_paths:
            if not prim_path:  # pragma: no cover
                continue
            prop_dict = {}

            for stage in valid_stages:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:  # pragma: no cover
                    continue

                props = self._get_prim_properties(prim)
                props = self._filter_props_to_build_with_prop_names(props, prop_names)

                for prop in props:
                    if prop.IsHidden():  # pragma: no cover
                        continue

                    prop_name: str = prop.GetName()
                    if prop_name not in prop_dict:
                        prop_type = prop.GetPropertyType() if hasattr(prop, "GetPropertyType") else type(prop)
                        prop_dict[prop_name] = self._create_property_entry(
                            prop_name, prop.GetDisplayGroup(), prop.GetAllMetadata(), prop_type
                        )

            if shared_props_dict is None:
                shared_props_dict = prop_dict
            else:
                # Find intersection of the dicts
                intersect_shared_props = {}
                for prop_name, prop_info in shared_props_dict.items():
                    if prop_dict.get(prop_name) == prop_info:
                        intersect_shared_props[prop_name] = prop_info

                if len(intersect_shared_props) == 0:  # pragma: no cover
                    # No intersection, nothing to build
                    # early return
                    return None

                shared_props_dict = intersect_shared_props

        shared_props = list(shared_props_dict.values())
        # Sort properties to PropertyOrder using the last selected object
        order = anchor_prim.GetPropertyOrder()
        shared_prop_order = []
        shared_prop_unordered = []
        for prop in shared_props:
            if prop[0] in order:
                shared_prop_order.append(prop[0])
            else:
                shared_prop_unordered.append(prop[0])

        shared_prop_order.extend(shared_prop_unordered)
        return sorted(shared_props, key=lambda x: shared_prop_order.index(x[0]))

    def request_rebuild(self):
        # If widget is going to be rebuilt, _pending_dirty_task_or_future does not need to run.
        if self._pending_dirty_task_or_future is not None:
            self._pending_dirty_task_or_future.cancel()
        self._pending_dirty_task_or_future = None
        self._pending_dirty_paths.clear()
        super().request_rebuild()

    async def _delayed_dirty_handler(self):
        # pylint: disable=protected-access

        loops = 100
        while loops > 0:
            # Do not refresh UI until visible/uncollapsed
            if not self._collapsed:  # pragma: no cover
                break

            await omni.kit.app.get_app().next_update_async()
            loops -= 1

        # clear the pending dirty tasks BEFORE dirting model.
        # dirtied model may trigger additional USD notice that needs to be scheduled.
        self._pending_dirty_task_or_future = None

        if self._pending_dirty_paths:
            # Make a copy of the paths. It may change if USD edits are made during iteration
            pending_dirty_paths = self._pending_dirty_paths.copy()
            self._pending_dirty_paths.clear()

            carb.profiler.begin(1, "UsdPropertyWidget._delayed_dirty_handler")
            # multiple path can share the same model. Only dirty once!
            dirtied_models = set()
            for path in pending_dirty_paths:
                models = self._models.get(path)
                if models:
                    for model in models:
                        if model not in dirtied_models:
                            model._set_dirty()
                            dirtied_models.add(model)

            carb.profiler.end(1)

    def on_new_payload(self, payload):  # pylint: disable=arguments-differ
        self.__custom_attribute_values = {}

        stage = payload.get_stage()

        if stage and self._enable_adapter:
            stage_adapters = ac.get_adapter_registry().instantiate_all_stage_adapters(stage)
            self._stage_adapters = list(stage_adapters.values())
            self._stage_adapters.sort(key=lambda x: x.priority_write)
        else:
            self._stage_adapters = []

        return super().on_new_payload(payload)

    def add_custom_schema_attribute(self, attribute_name, classify_fn, create_fn, display_group, value_dict):
        """
        Adds a custom schema attribute.

        Args:
            attribute_name (str): The name of the attribute.
            classify_fn (function): The function to classify the attribute.
        """
        self.__custom_attribute[attribute_name] = (classify_fn, create_fn, display_group, value_dict)

    def is_custom_schema_attribute_used(self, prim) -> list:
        """
        Checks if the custom schema attribute is used.

        Args:
            prim (Usd.Prim): The prim to check.
        """
        attribute_used = False
        for attribute_name, item in self.__custom_attribute.items():
            (classify_fn, _, _, _) = item
            if not prim.GetAttribute("disableFogInteraction") and classify_fn(prim):
                attribute_used = True
                self.__custom_attribute_values[attribute_name] = True

        return attribute_used

    def add_custom_schema_attributes_to_props(self, props) -> None:
        """
        Adds custom attributes (See is_custom_schema_attribute_used).

        Args:
            props (list): list of props.
        """
        for attribute_name, item in self.__custom_attribute_values.items():
            if item:
                (_, create_fn, display_group, value_dict) = self.__custom_attribute[attribute_name]
                if create_fn:
                    props.append(create_fn(attribute_name, value_dict))
                else:
                    props.append(UsdPropertyUiEntry(attribute_name, display_group, value_dict, Usd.Attribute))

    def add_listener_adapters(self, attr_names):
        """
        Adds change tracker to attribute name.

        Args:
            attr_names (list): list of attributes.
        """
        if len(attr_names) > 0:
            for adapter in self._stage_adapters:
                self._listener_adapters.append(
                    adapter.CreateChangeTracker(attr_names, self._payload.get_paths(), self._on_usd_changed)
                )


class SchemaPropertiesWidget(UsdPropertiesWidget):
    """
    SchemaPropertiesWidget only filters properties and only show the onces from a given IsA schema or applied API schema.
    """

    def __init__(self, title: str, schema, include_inherited: bool):
        """
        Constructor.

        Args:
            title (str): Title of the widgets on the Collapsible Frame.
            schema: The USD IsA schema or applied API schema to filter properties.
            include_inherited (bool): Whether the filter should include inherited properties.
        """
        super().__init__(title, collapsed=False, enable_adapter=True)
        self._title = title
        self._schema = schema
        self._include_inherited = include_inherited

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """
        if not super().on_new_payload(payload):  # pragma: no cover
            return False

        if not self._payload or len(self._payload) == 0:  # pragma: no cover
            return False

        for prim_path in self._payload:
            prim = self._get_prim(prim_path)

            if not prim:  # pragma: no cover
                return False

            is_api_schema = Usd.SchemaRegistry().IsAppliedAPISchema(self._schema)
            if not (is_api_schema and prim.HasAPI(self._schema) or not is_api_schema and prim.IsA(self._schema)):
                return False

        return True

    def _filter_props_to_build(self, props):
        """
        See UsdPropertiesWidget._filter_props_to_build
        """
        if len(props) == 0:
            return props

        if Usd.SchemaRegistry().IsMultipleApplyAPISchema(self._schema):
            prim = props[0].GetPrim()
            schema_instances = set()
            schema_type_name = Usd.SchemaRegistry().GetSchemaTypeName(self._schema)
            for schema in prim.GetAppliedSchemas():
                if schema.startswith(schema_type_name):
                    schema_instances.add(schema[len(schema_type_name) + 1 :])
            filtered_props = []
            api_path_func_name = f"Is{schema_type_name}Path"
            api_path_func = getattr(self._schema, api_path_func_name)

            # self._schema.GetSchemaAttributeNames caches the query result in a static variable and any new instance
            # token passed into it won't change the cached property names. This can potentially cause problems as other
            # code calling same function with different instance name will get wrong result.
            #
            # There's any other function IsSchemaPropertyBaseName but it's not implemented on all applied schemas. (not
            # implemented in a few PhysicsSchema, for example.
            #
            # if include_inherited is True, it returns SchemaTypeName:BaseName for properties, otherwise it only returns
            # BaseName.
            schema_attr_names = self._schema.GetSchemaAttributeNames(self._include_inherited, "")

            for prop in props:
                if prop.IsHidden():
                    continue
                prop_path = prop.GetPath().pathString
                for instance_name in schema_instances:
                    instance_seg = prop_path.find(":" + instance_name + ":")
                    if instance_seg != -1:
                        api_path = prop_path[0 : instance_seg + 1 + len(instance_name)]
                        if api_path_func(api_path):
                            base_name = prop_path[instance_seg + 1 + len(instance_name) + 1 :]
                            if base_name in schema_attr_names:
                                filtered_props.append(prop)
                                break
            return filtered_props
        schema_attr_names = self._schema.GetSchemaAttributeNames(self._include_inherited)
        return [prop for prop in props if prop.GetName() in schema_attr_names]


class MultiSchemaPropertiesWidget(UsdPropertiesWidget):
    """
    MultiSchemaPropertiesWidget filters properties and only show the onces from a given IsA schema or schema subclass list.
    """

    __known_api_schemas = set()

    def __init__(
        self,
        title: str,
        schema,
        schema_subclasses: list,
        include_list: list = None,
        exclude_list: list = None,
        api_schemas: Sequence[str] = None,
        group_api_schemas: bool = False,
    ):
        """
        Constructor.

        Args:
            title (str): Title of the widgets on the Collapsable Frame.
            schema: The USD IsA schema or applied API schema to filter properties.
            schema_subclasses (list): list of subclasses
            include_list (list): list of additional schema named to add
            exclude_list (list): list of additional schema named to remove
            api_schemas (sequence): a sequence of AppliedAPI schema names that this widget handles
            group_api_schemas (bool): whether to create default groupings for any AppliedSchemas on the Usd.Prim
        """
        super().__init__(title=title, collapsed=False, enable_adapter=True)
        self._title = title
        self._schema = schema

        # create schema_attr_names
        self._schema_attr_base = schema.GetSchemaAttributeNames(False)
        for subclass in schema_subclasses:
            self._schema_attr_base += subclass.GetSchemaAttributeNames(False)
        self._schema_attr_base += include_list if include_list else []
        self._schema_attr_base = set(self._schema_attr_base) - set(exclude_list if exclude_list else [])
        self._schema_exclude_list = exclude_list
        # Setup the defaults for handling applied API schemas
        self._applied_schemas = {}
        self._schema_attr_names = None
        self._group_api_schemas = group_api_schemas
        # Save any custom Applied Schemas and mark them to be ignored when building default widget
        self._custom_api_schemas = api_schemas
        if self._custom_api_schemas:
            MultiSchemaPropertiesWidget.__known_api_schemas.update(self._custom_api_schemas)

    def __del__(self):
        # Mark any custom Applied Schemas to start being handled by the defaut widget
        if self._custom_api_schemas:
            MultiSchemaPropertiesWidget.__known_api_schemas.difference_update(self._custom_api_schemas)

    def clean(self):
        """
        See PropertyWidget.clean
        """
        self._applied_schemas = {}
        self._schema_attr_names = None
        super().clean()

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """
        if not super().on_new_payload(payload):  # pragma: no cover
            return False

        if not self._payload or len(self._payload) == 0:  # pragma: no cover
            return False

        used = []
        schema_reg = Usd.SchemaRegistry()
        self._applied_schemas = {}
        # Build out our _schema_attr_names variable to include properties from the base schema and any applied schemas
        self._schema_attr_names = self._schema_attr_base

        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
            if self._schema().IsTyped() and not prim.IsA(self._schema):
                return False
            if self._schema().IsAPISchema() and not prim.HasAPI(self._schema):
                return False
            # If the base-schema has requested auto-grouping of all Applied Schemas, handle that grouping now
            if self._group_api_schemas:
                # TODO: Should this be delayed until _customize_props_layout ?
                for api_schema in prim.GetAppliedSchemas():
                    # Ignore any API schemas that are already registered as custom widgets
                    if api_schema in MultiSchemaPropertiesWidget.__known_api_schemas:
                        continue
                    # Skip over any API schemas that USD doesn't actually know about
                    prim_def = schema_reg.FindAppliedAPIPrimDefinition(api_schema)
                    if not prim_def:  # pragma: no cover
                        continue
                    api_prop_names = prim_def.GetPropertyNames()
                    self._schema_attr_names = self._schema_attr_names.union(api_prop_names)
                    for api_prop in api_prop_names:
                        display_group = prim_def.GetPropertyMetadata(api_prop, "displayGroup")
                        prop_grouping = self._applied_schemas.setdefault(api_schema, {}).setdefault(display_group, [])
                        prop_grouping.append((api_prop, prim_def.GetPropertyMetadata(api_prop, "displayName")))

            props = self._get_prim_properties(prim)
            used += self._filter_props_to_build(props)

        return used

    def show_schemas(self):
        """Support add/remove of Schema API's.

        Returns:
            bool: Return True for widget to allow add/remove of Schema API's."""
        return False

    def _filter_props_to_build(self, props):
        """
        See UsdPropertiesWidget._filter_props_to_build
        """
        return [prop for prop in props if prop.GetName() in self._schema_attr_names and not prop.IsHidden()]

    def _filter_props_to_build_with_prop_names(self, props, prop_names):
        """
        See UsdPropertiesWidget._filter_props_to_build_with_prop_names
        """
        return [
            prop
            for prop in props
            if prop.GetName() in self._schema_attr_names.union(set(prop_names)) and not prop.IsHidden()
        ]

    def _customize_props_layout(self, props):
        # If no applied schemas, just use the base class' layout.
        if not self._applied_schemas:
            return super()._customize_props_layout(props)

        from omni.kit.property.usd.custom_layout_helper import (
            CustomLayoutFrame,
            CustomLayoutGroup,
            CustomLayoutProperty,
        )

        self.add_custom_schema_attributes_to_props(props)

        # We can't really escape the parent group, so all default/base and applied-schemas will be common to a group
        frame = CustomLayoutFrame(hide_extra=False)
        with frame:
            # Add all base properties at the top
            base_attrs = [attr for attr in props if attr.prop_name in self._schema_attr_base]
            if base_attrs:
                with CustomLayoutGroup(self._title):
                    for attr in base_attrs:
                        CustomLayoutProperty(attr.prop_name, attr.display_group)
                        attr.override_display_group(self._title)

        # Now create a master-group for each applied schema, and possibly sub-groups for it's properties
        # Here's where we may want to actually escape the parent and create a totally new group
        with frame:
            for api_schema, api_schema_groups in self._applied_schemas.items():
                with CustomLayoutGroup(api_schema):
                    for prop_group, prop_items in api_schema_groups.items():
                        with CustomLayoutGroup(prop_group):
                            for prop in prop_items:
                                CustomLayoutProperty(*prop)

        return frame.apply(props)


class RawUsdPropertiesWidget(UsdPropertiesWidget):
    """
    A class to represent a USD raw properties widget.
    """

    MULTI_SELECTION_LIMIT_SETTING_PATH = "/persistent/exts/omni.kit.property.usd/raw_widget_multi_selection_limit"
    MULTI_SELECTION_LIMIT_DO_NOT_ASK_SETTING_PATH = (
        "/exts/omni.kit.property.usd/multi_selection_limit_do_not_ask"  # session only, not persistent!
    )

    def __init__(self, title: str, collapsed: bool, multi_edit: bool = True, enable_adapter: bool = False):
        super().__init__(title=title, collapsed=collapsed, multi_edit=multi_edit, enable_adapter=enable_adapter)
        self._settings = carb.settings.get_settings()
        self._settings.set_default(RawUsdPropertiesWidget.MULTI_SELECTION_LIMIT_DO_NOT_ASK_SETTING_PATH, False)

        self._skip_multi_selection_protection = False

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):  # pragma: no cover
            return False

        for prim_path in self._payload:  # pragma: no cover
            if not prim_path.IsPrimPath():
                return False

        self._skip_multi_selection_protection = False

        return bool(self._payload and len(self._payload) > 0)

    def build_impl(self):
        # rebuild frame when frame is opened
        super().build_impl()
        self._collapsable_frame.set_collapsed_changed_fn(self._on_collapsed_changed)

    def build_items(self):
        # only show raw items if frame is open
        if self._collapsable_frame and not self._collapsable_frame.collapsed and not self._multi_selection_protected():
            super().build_items()

    def _on_collapsed_changed(self, collapsed):
        if not collapsed:
            self.request_rebuild()

    def _multi_selection_protected(self):
        if self._no_multi_selection_protection_this_session():
            return False

        def show_all(do_not_ask: bool):
            self._settings.set(RawUsdPropertiesWidget.MULTI_SELECTION_LIMIT_DO_NOT_ASK_SETTING_PATH, do_not_ask)
            self._skip_multi_selection_protection = True
            self.request_rebuild()

        multi_select_limit = self._settings.get(RawUsdPropertiesWidget.MULTI_SELECTION_LIMIT_SETTING_PATH)

        if multi_select_limit and len(self._payload) > multi_select_limit and not self._skip_multi_selection_protection:
            ui.Separator()
            ui.Label(
                f"You have selected {len(self._payload)} Prims, to preserve fast performance the Raw Usd Properties Widget is not showing above the current limit of {multi_select_limit} Prims. Press the button below to show it anyway but expect potential performance penalty.",
                width=omni.ui.Percent(100),
                alignment=ui.Alignment.CENTER,
                name="label",
                word_wrap=True,
            )
            button = ui.Button("Skip Multi Selection Protection")
            with ui.HStack(width=0):
                checkbox = ui.CheckBox()
                ui.Spacer(width=5)
                ui.Label("Do not ask again for current session.", name="label")
            button.set_clicked_fn(lambda: show_all(checkbox.model.get_value_as_bool()))
            return True

        return False

    def _no_multi_selection_protection_this_session(self):
        return self._settings.get(RawUsdPropertiesWidget.MULTI_SELECTION_LIMIT_DO_NOT_ASK_SETTING_PATH)
