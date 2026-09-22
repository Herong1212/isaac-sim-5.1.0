# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["get_ui_style", "get_model_cls", "SdfAssetPathDelegate", "UsdPropertiesWidgetBuilder"]

import asyncio
import fnmatch
import weakref
from functools import lru_cache, partial
from typing import Any, Callable, List, Type, Union

import carb
import carb.settings
import omni.client
import omni.ui as ui
import omni.usd
from omni.kit.property.adapter.core import PropertyType, StageAdapter
from omni.kit.widget.highlight_label import HighlightLabel
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_HEIGHT, LABEL_WIDTH, LABEL_WIDTH_LIGHT
from pxr import Sdf, Sdr, Usd

from . import widgets
from .asset_filepicker import replace_query, show_asset_file_picker
from .attribute_context_menu import AttributeContextMenu, AttributeContextMenuEvent
from .control_state_manager import ControlStateManager
from .relationship import RelationshipArrayModel, SdfRelationshipArrayItemModel
from .usd_attribute_model import (
    BoolArrayAttributeSingleChannelModel,
    GfMatrixAttributeModel,
    GfVecAttributeModel,
    GfVecAttributeSingleChannelModel,
    MatrixBaseAttributeModel,
    MdlEnumAttributeModel,
    SdfAssetPathArrayAttributeItemModel,
    SdfAssetPathAttributeModel,
    SdfTimeCodeModel,
    TfTokenAttributeModel,
    UsdAttributeModel,
)
from .usd_object_model import MetadataObjectModel


@lru_cache()
def _get_plus_glyph():
    return ui.get_custom_glyph_code("${glyphs}/menu_context.svg")


def get_ui_style():
    """
    Retrieves the UI style from the settings.

    Returns:
        str: The UI style.
    """
    return carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"


def get_model_cls(cls, args, key="model_cls"):
    """
    Retrieves the model class from the arguments.

    Args:
        cls: The default model class.
        args: The arguments.
        key: The key to retrieve the model class from the arguments.

    Returns:
        The model class.
    """
    if args:
        return args.get(key, cls)
    return cls


def get_model_kwargs(args, key="model_kwargs"):
    """
    Retrieves the model kwargs from the arguments.

    Args:
        args: The arguments.
        key: The key to retrieve the model kwargs from the arguments.

    Returns:
        The model kwargs.
    """
    if args:
        return args.get(key, {})
    return {}


def is_relative_path(path: str) -> bool:
    """
    Checks if the path is a relative path.

    Args:
        path: The path to check.

    Returns:
        bool: True if the path is a relative path, False otherwise.
    """
    # Adapted from usd-resolver repo

    # Absolute paths either have a colon before a slash (indicating urls or drive letters in windows)
    # or they start with a '/' (indicating absolute paths in linux or UNC prefix on windows
    # Relative paths are !Absolute paths
    if not path:
        return False

    if path[0] == "/":
        return False

    colon_idx = path.find(":")
    slash_idx = path.find("/")
    if colon_idx != -1 and slash_idx != -1 and colon_idx < slash_idx:
        return False

    return True


class SdfAssetPathDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer. TreeView calls the methods
    of the delegate to create custom widgets for each item.
    """

    def __init__(self, stage, attr_name, widget_kwargs):
        super().__init__()

        self._stage = stage
        self._attr_name = attr_name
        self._widget_kwargs = widget_kwargs

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per column per item"""
        with ui.VStack():
            ui.Spacer(height=2)
            with ui.ZStack():
                ui.Rectangle(name="backdrop")
                frame = ui.Frame(
                    height=0,
                    spacing=5,
                    style={
                        "Frame": {"margin_width": 2, "margin_height": 2},
                        "Button": {"background_color": 0x0},
                    },
                )
                with frame:
                    (item_value_model, value_model) = model.get_item_value_model(item, column_id)

                    extra_widgets = []
                    with ui.HStack(spacing=HORIZONTAL_SPACING, width=ui.Percent(100)):
                        with ui.VStack(spacing=0, height=ui.Percent(100), width=0):
                            ui.Spacer()
                            # Create ||| grab area
                            grab = ui.HStack(
                                identifier=f"sdf_asset_array_{self._attr_name}[{item_value_model.index}].reorder_grab",
                                height=LABEL_HEIGHT,
                            )
                            with grab:
                                for _i in range(3):
                                    ui.Line(
                                        width=3,
                                        alignment=ui.Alignment.H_CENTER,
                                        name="grab",
                                    )
                            ui.Spacer()

                        # do a content_clipping for the rest of the widget so only dragging on the grab triggers
                        # reorder
                        with ui.HStack(content_clipping=1):
                            self._build_asset_entry(
                                self._widget_kwargs, item_value_model, value_model, frame, extra_widgets
                            )

            ui.Spacer(height=2)

    def _build_asset_entry(self, widget_kwargs, item_value_model, value_model, frame, extra_widgets):
        self.build_path_field(widget_kwargs.copy(), item_value_model, frame, extra_widgets)
        self._build_additional(widget_kwargs.copy(), item_value_model, value_model)
        self._build_remove_button(widget_kwargs.copy(), item_value_model, value_model)

    def build_path_field(self, widget_kwargs, item_value_model, frame, extra_widgets):
        """
        Builds the path field for the asset entry.

        This method builds the path field for the asset entry and adds it to the extra widgets.

        Args:
            widget_kwargs: The widget kwargs.
            item_value_model: The item value model.
            frame: The frame.
            extra_widgets: The extra widgets.
        """
        widget_kwargs["model"] = item_value_model
        UsdPropertiesWidgetBuilder.build_path_field(
            item_value_model, self._stage, self._attr_name, widget_kwargs, frame, extra_widgets
        )

    def _build_additional(self, widget_kwargs, item_value_model, value_model):
        """
        Builds the additional widgets for the asset entry.

        This method builds the additional widgets for the asset entry.
        """

    def _build_remove_button(self, widget_kwargs, item_value_model, value_model):
        """
        Builds the remove button for the asset entry.

        This method builds the remove button for the asset entry.
        """

        def remove_entry(index: int, value_model: UsdAttributeModel):
            value = list(value_model.get_value())
            new_value = value[:index] + value[index + 1 :]
            value_model.set_value(new_value)

        remove_style = {
            "image_url": str(widgets.ICON_PATH.joinpath("remove.svg")),
            "margin": 0,
            "padding": 0,
        }
        ui.Spacer(width=HORIZONTAL_SPACING)
        ui.Button(
            "",
            width=12,
            height=ui.Percent(100),
            fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
            clicked_fn=lambda index=item_value_model.index, value_model=value_model: remove_entry(index, value_model),
            name="remove",
            style=remove_style,
            tooltip="Remove Asset",
            identifier=f"sdf_asset_array_{self._attr_name}[{item_value_model.index}].remove",
        )


class UsdPropertiesWidgetBuilder:
    """
    Builds the properties widget for the asset entry.

    This class builds the properties widget for the asset entry.
    """

    # We don't use Tf.Type.FindByName(name) directly because the name depends
    # on the compiler. For example the line `Sdf.ValueTypeNames.Int64.type`
    # resolves to `Tf.Type.FindByName('long')` on Linux and on Windows it's
    # `Tf.Type.FindByName('__int64')`.
    tf_half = Sdf.ValueTypeNames.Half.type
    tf_float = Sdf.ValueTypeNames.Float.type
    tf_double = Sdf.ValueTypeNames.Double.type
    tf_uchar = Sdf.ValueTypeNames.UChar.type
    tf_uint = Sdf.ValueTypeNames.UInt.type
    tf_int = Sdf.ValueTypeNames.Int.type
    tf_int64 = Sdf.ValueTypeNames.Int64.type
    tf_uint64 = Sdf.ValueTypeNames.UInt64.type
    tf_bool = Sdf.ValueTypeNames.Bool.type
    tf_bool_array = Sdf.ValueTypeNames.BoolArray.type
    tf_string = Sdf.ValueTypeNames.String.type
    tf_gf_mtx2d = Sdf.ValueTypeNames.Matrix2d.type
    tf_gf_mtx3d = Sdf.ValueTypeNames.Matrix3d.type
    tf_gf_mtx4d = Sdf.ValueTypeNames.Matrix4d.type
    tf_gf_vec2i = Sdf.ValueTypeNames.Int2.type
    tf_gf_vec2h = Sdf.ValueTypeNames.Half2.type
    tf_gf_vec2f = Sdf.ValueTypeNames.Float2.type
    tf_gf_vec2d = Sdf.ValueTypeNames.Double2.type
    tf_gf_vec3i = Sdf.ValueTypeNames.Int3.type
    tf_gf_vec3h = Sdf.ValueTypeNames.Half3.type
    tf_gf_vec3f = Sdf.ValueTypeNames.Float3.type
    tf_gf_vec3d = Sdf.ValueTypeNames.Double3.type
    tf_gf_vec4i = Sdf.ValueTypeNames.Int4.type
    tf_gf_vec4h = Sdf.ValueTypeNames.Half4.type
    tf_gf_vec4f = Sdf.ValueTypeNames.Float4.type
    tf_gf_vec4d = Sdf.ValueTypeNames.Double4.type
    tf_tf_token = Sdf.ValueTypeNames.Token.type
    tf_sdf_asset_path = Sdf.ValueTypeNames.Asset.type
    tf_sdf_time_code = Sdf.ValueTypeNames.TimeCode.type

    # array type builders
    tf_sdf_asset_array_path = Sdf.ValueTypeNames.AssetArray.type

    @classmethod
    def init_builder_table(cls):
        """
        Initializes the builder table.

        This method initializes the builder table.
        """
        cls.widget_builder_table = {
            cls.tf_half: cls.floating_point_builder,
            cls.tf_float: cls.floating_point_builder,
            cls.tf_double: cls.floating_point_builder,
            cls.tf_uchar: cls.integer_builder,
            cls.tf_uint: cls.integer_builder,
            cls.tf_int: cls.integer_builder,
            cls.tf_int64: cls.integer_builder,
            cls.tf_uint64: cls.integer_builder,
            cls.tf_bool: cls.bool_builder,
            cls.tf_bool_array: cls.bool_array_builder,
            cls.tf_string: cls.string_builder,
            cls.tf_gf_mtx2d: cls.gf_matrix_builder,
            cls.tf_gf_mtx3d: cls.gf_matrix_builder,
            cls.tf_gf_mtx4d: cls.gf_matrix_builder,
            cls.tf_gf_vec2i: cls.vec2_per_channel_builder,
            cls.tf_gf_vec2h: cls.vec2_per_channel_builder,
            cls.tf_gf_vec2f: cls.vec2_per_channel_builder,
            cls.tf_gf_vec2d: cls.vec2_per_channel_builder,
            cls.tf_gf_vec3i: cls.vec3_per_channel_builder,
            cls.tf_gf_vec3h: cls.vec3_per_channel_builder,
            cls.tf_gf_vec3f: cls.vec3_per_channel_builder,
            cls.tf_gf_vec3d: cls.vec3_per_channel_builder,
            cls.tf_gf_vec4i: cls.vec4_per_channel_builder,
            cls.tf_gf_vec4h: cls.vec4_per_channel_builder,
            cls.tf_gf_vec4f: cls.vec4_per_channel_builder,
            cls.tf_gf_vec4d: cls.vec4_per_channel_builder,
            cls.tf_tf_token: cls.tftoken_builder,
            cls.tf_sdf_asset_path: cls.sdf_asset_path_builder,
            cls.tf_sdf_time_code: cls.time_code_builder,
            # array type builders
            cls.tf_sdf_asset_array_path: cls.sdf_asset_path_array_builder,
        }
        cls.reset_builder_coverage_table()

    @classmethod
    def reset_builder_coverage_table(cls):
        """
        Resets the builder coverage table.

        This method resets the builder coverage table.
        """
        cls.widget_builder_coverage_table = {
            cls.tf_half: False,
            cls.tf_float: False,
            cls.tf_double: False,
            cls.tf_uchar: False,
            cls.tf_uint: False,
            cls.tf_int: False,
            cls.tf_int64: False,
            cls.tf_uint64: False,
            cls.tf_bool: False,
            cls.tf_bool_array: False,
            cls.tf_string: False,
            cls.tf_gf_mtx2d: False,
            cls.tf_gf_mtx3d: False,
            cls.tf_gf_mtx4d: False,
            cls.tf_gf_vec2i: False,
            cls.tf_gf_vec2h: False,
            cls.tf_gf_vec2f: False,
            cls.tf_gf_vec2d: False,
            cls.tf_gf_vec3i: False,
            cls.tf_gf_vec3h: False,
            cls.tf_gf_vec3f: False,
            cls.tf_gf_vec3d: False,
            cls.tf_gf_vec4i: False,
            cls.tf_gf_vec4h: False,
            cls.tf_gf_vec4f: False,
            cls.tf_gf_vec4d: False,
            cls.tf_tf_token: False,
            cls.tf_sdf_asset_path: False,
            cls.tf_sdf_time_code: False,
            cls.tf_sdf_asset_array_path: False,
        }

    @classmethod
    def startup(cls):
        """
        Starts up the builder.

        This method starts up the builder.
        """

        cls.init_builder_table()
        cls.default_range_steps = {}

    @classmethod
    def shutdown(cls):
        """
        Shuts down the builder.

        This method shuts down the builder.
        """

    @classmethod
    def build(
        cls,
        stage,
        attr_name,
        metadata,
        property_type,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the properties widget for the asset entry.

        This method builds the properties widget for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            metadata: The metadata.
            property_type: The property type.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The properties widget model.
        """

        if property_type in (Usd.Attribute, PropertyType.ATTRIBUTE):
            type_name = cls.get_type_name(metadata)
            tf_type = type_name.type
            build_func = cls.widget_builder_table.get(tf_type, cls.fallback_builder)
            cls.widget_builder_coverage_table[tf_type] = True
            return build_func(
                stage, attr_name, type_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
            )
        if property_type in (Usd.Relationship, PropertyType.RELATIONSHIP):
            # OM-118904: workaround for usdrt._Usd.Relationship
            usd_stage = stage.usd_stage if isinstance(stage, StageAdapter) else stage
            return cls.relationship_builder(
                usd_stage, attr_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
            )
        return None

    ###### builder funcs ######
    @staticmethod
    def can_accept_prim_path_drop(payload: str, model_weak, stage, allow_multi_files=False) -> bool:
        """
        Checks if the payload can be accepted as a prim path drop.

        This method checks if the payload can be accepted as a prim path drop.

        Args:
            payload: The payload.
            model_weak: The model weak.
            stage: The stage.
            allow_multi_files: Whether to allow multi files.

        Returns:
            bool: True if the payload can be accepted as a prim path drop, False otherwise.
        """
        model_weak = model_weak()
        if not model_weak:
            return False

        urls = payload.split("\n")

        if not urls:
            return False

        if not allow_multi_files and len(urls) > 1:
            carb.log_warn("sdf_relationship_path_builder multi-file drag/drop not supported")
            return False

        accepted = False
        for url in urls:
            if url.isdigit():  # reorder drops are just numbers, we are checking paths
                continue
            prim = stage.GetPrimAtPath(url)
            if prim:
                if model_weak.filter_type_list is not None and len(model_weak.filter_type_list) != 0:
                    for ftype in model_weak.filter_type_list:
                        if prim.IsA(ftype):
                            accepted = True
                            break
                if model_weak.filter_lambda is not None:
                    accepted = model_weak.filter_lambda(prim)
                if len(model_weak.filter_type_list) == 0 and model_weak.filter_lambda is None:
                    accepted = True
        return accepted

    @classmethod
    def build_prim_path_field(cls, model, list_item_model, stage, attr_name, widget_kwargs, frame, extra_widgets):
        """
        Builds the prim path field for the asset entry.

        This method builds the prim path field for the asset entry and adds it to the extra widgets.

        Args:
            model: The model.
            list_item_model: The list item model.
            stage: The stage.
            attr_name: The attribute name.
            widget_kwargs: The widget kwargs.
            frame: The frame.
            extra_widgets: The extra widgets.
        """
        with ui.HStack():

            def assign_value_fn(model_weak, payload):
                model_weak = model_weak()
                if not model_weak:
                    return
                urls = payload.split("\n")

                if not urls:
                    return

                if len(urls) != 1:
                    carb.log_warn("sdf_relationship_path_builder multi-file drag/drop not supported")
                    return
                model_weak.set_value(urls[0])

            with ui.ZStack():
                value_widget = ui.StringField(**widget_kwargs)

                value_widget.set_accept_drop_fn(
                    lambda url, model_weak=weakref.ref(list_item_model): cls.can_accept_prim_path_drop(
                        url, model_weak, stage
                    )
                )
                value_widget.set_drop_fn(
                    lambda event, model_weak=weakref.ref(model): assign_value_fn(model_weak, event.mime_data)
                )
                value_widget.identifier = f"sdf_relationship_{attr_name}" + (
                    f"[{model.index}]" if hasattr(model, "index") else ""
                )
                mixed_overlay = cls.create_mixed_text_overlay()
            ui.Spacer(width=3)

            style = {"image_url": str(widgets.ICON_PATH.joinpath("small_folder.png"))}

            enabled = False
            try:
                from omni.kit.window.file_importer import get_file_importer

                enabled = get_file_importer() is not None
            except ModuleNotFoundError:
                pass

            def change_relationship_entry(model_weak, paths):
                """
                Changes the relationship entry.

                This method changes the relationship entry.

                Args:
                    model_weak: The model weak.
                    paths: The paths.
                """
                model_weak = model_weak()
                if model_weak and len(paths) > 0:
                    model_weak.set_value(Sdf.Path(paths[0]))

            def on_browse(model_weak, list_model_weak):
                """
                On browse.

                This method is called when the browse button is clicked.

                Args:
                    model_weak: The model weak.
                    list_model_weak: The list model weak.
                """
                list_model_weak = list_model_weak()
                if not list_model_weak:
                    return

                list_model_weak.picker.show(
                    1, lambda paths, model_weak=model_weak: change_relationship_entry(model_weak, paths)
                )

            browse_button = ui.Button(
                style=style,
                width=20,
                tooltip="Browse..." if enabled else "Prim browser not available",
                clicked_fn=lambda model_weak=weakref.ref(model), list_model_weak=weakref.ref(
                    list_item_model
                ): on_browse(model_weak, list_model_weak),
                enabled=enabled,
                identifier=f"sdf_browse_relationship_{attr_name}"
                + (f"[{model.index}]" if hasattr(model, "index") else ""),
            )
            extra_widgets.append(browse_button)

            return value_widget, mixed_overlay

    @classmethod
    def relationship_builder(
        cls,
        stage,
        attr_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the relationship builder for the asset entry.

        This method builds the relationship builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The relationship builder model.
        """
        widget_kwargs = {"name": "models", "target_name": "Target", "target_plural_name": "Targets"}
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)

        class SdfRelationshipPathDelegate(ui.AbstractItemDelegate):
            """
            Delegate is the representation layer. TreeView calls the methods
            of the delegate to create custom widgets for each item.
            """

            def build_branch(self, model, item, column_id, level, expanded):
                """Create a branch widget that opens or closes subtree"""

            def build_widget(self, model, item, column_id, level, expanded):
                """Create a widget per column per item"""
                with ui.VStack():
                    ui.Spacer(height=5)
                    with ui.ZStack():
                        ui.Rectangle(name="backdrop")
                        frame = ui.Frame(
                            height=0,
                            spacing=5,
                            style={
                                "Frame": {"margin_width": 2, "margin_height": 2},
                                "Button": {"background_color": 0x0},
                            },
                        )
                        with frame:
                            (item_value_model, value_model) = model.get_item_value_model(item, column_id)

                            extra_widgets = []
                            with ui.HStack(spacing=HORIZONTAL_SPACING, width=ui.Percent(100)):
                                with ui.VStack(spacing=0, height=ui.Percent(100), width=0):
                                    ui.Spacer()
                                    # Create ||| grab area
                                    grab = ui.HStack(
                                        identifier=f"sdf_relationship_{attr_name}[{item_value_model.index}].reorder_grab",
                                        height=LABEL_HEIGHT,
                                    )
                                    with grab:
                                        for _ in range(3):
                                            ui.Line(
                                                width=3,
                                                alignment=ui.Alignment.H_CENTER,
                                                name="grab",
                                            )
                                    ui.Spacer()

                                # do a content_clipping for the rest of the widget so only dragging on the grab triggers
                                # reorder
                                with ui.HStack(content_clipping=1):
                                    widget_kwargs["model"] = item_value_model
                                    cls.build_prim_path_field(
                                        item_value_model, model, stage, attr_name, widget_kwargs, frame, extra_widgets
                                    )

                                    def remove_entry(index: int, value_model: RelationshipArrayModel):
                                        value = list(value_model.get_value())
                                        new_value = value[:index] + value[index + 1 :]
                                        value_model.set_value(new_value)

                                    remove_style = {
                                        "image_url": str(widgets.ICON_PATH.joinpath("remove.svg")),
                                        "margin": 0,
                                        "padding": 0,
                                    }
                                    ui.Spacer(width=HORIZONTAL_SPACING)
                                    ui.Button(
                                        "",
                                        width=12,
                                        height=ui.Percent(100),
                                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                                        clicked_fn=lambda index=item_value_model.index, value_model=value_model: remove_entry(
                                            index, value_model
                                        ),
                                        name="remove",
                                        style=remove_style,
                                        tooltip="Remove Relationship",
                                        identifier=f"sdf_relationship_{attr_name}[{item_value_model.index}].remove",
                                    )

                    ui.Spacer(height=5)

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            cls.create_label(attr_name, metadata, additional_label_kwargs)

            with ui.VStack():
                delegate_cls = get_model_cls(SdfRelationshipPathDelegate, widget_kwargs, key="delegate_cls")
                delegate = delegate_cls()
                model_cls = get_model_cls(SdfRelationshipArrayItemModel, widget_kwargs)
                item_model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], metadata, delegate, widget_kwargs
                )

                with ui.ZStack():
                    relationship_mixed = ui.HStack(spacing=HORIZONTAL_SPACING, content_clipping=1)
                    with relationship_mixed:
                        tooltip = ""
                        for index, path in enumerate(prim_paths):
                            tooltip += f"{path}\n"
                            if index > 9:
                                tooltip += "...."
                                break

                        selected_info_name = "Mixed"
                        style = {"Field": {"color": 0xFFCC9E61}, "Tooltip": {"color": 0xFF333333}}
                        widget = ui.StringField(
                            name="prims_path",
                            height=LABEL_HEIGHT,
                            enabled=False,
                            tooltip=tooltip,
                            tooltip_offset_y=22,
                            style=style,
                        )
                        widget.model.set_value(selected_info_name)
                    # content_clipping so drag n drop in tree view doesn't scroll the outer frame
                    tree_frame_stack = ui.HStack(spacing=HORIZONTAL_SPACING, content_clipping=1)
                    with tree_frame_stack:
                        with ui.Frame(height=0):
                            tree_view = ui.TreeView(
                                item_model,
                                delegate=delegate,
                                root_visible=False,
                                header_visible=False,
                                drop_between_items=True,
                                style={
                                    "TreeView:selected": {"background_color": 0x00},
                                    "TreeView": {"background_color": 0xFFA07D4F},  # reorder indicator
                                },
                            )
                            tree_view.identifier = f"sdf_relationship_array_{attr_name}"

                        ui.Spacer(width=12)
                with ui.HStack(spacing=HORIZONTAL_SPACING, height=LABEL_HEIGHT):
                    extra_widgets = []
                    with ui.ZStack():

                        def on_add_relationships(model_weak, paths):
                            model_weak = model_weak()
                            if not model_weak:
                                return

                            existing = model_weak.get_value()
                            for path in paths:
                                if path not in existing:
                                    existing.append(Sdf.Path(path))
                            model_weak.set_value(existing)

                        def add_relationship(weak_model: SdfRelationshipArrayItemModel):
                            model = weak_model()
                            if model:
                                model.picker.show(
                                    model.targets_limit - len(model.value_model.get_targets()),
                                    lambda paths, weak_model=weak_model: on_add_relationships(weak_model, paths),
                                )

                        target_name = widget_kwargs.get("target_name")
                        button = ui.Button(
                            f"{_get_plus_glyph()} Add {target_name}...",
                            clicked_fn=lambda model_weak=weakref.ref(item_model): add_relationship(model_weak),
                        )
                        button.identifier = f"sdf_relationship_array_{attr_name}.add_relationships"
                        button.set_accept_drop_fn(
                            lambda url, model_weak=weakref.ref(item_model.value_model): cls.can_accept_file_drop(
                                url, model_weak, True
                            )
                        )
                        target_limit = widget_kwargs.get("targets_limit", 0)
                        if (
                            target_limit > 0
                            and item_model.get_value() is not None
                            and len(item_model.get_value()) >= target_limit
                        ):
                            button.enabled = False

                        def on_list_len_changed(model, button_weak, limit):
                            button_weak = button_weak()
                            if button_weak and limit > 0 and model.get_value() is not None:
                                button_weak.enabled = len(model.get_value()) < limit

                        item_model.value_model.add_value_changed_fn(
                            lambda model, button_weak=weakref.ref(button), limit=target_limit: on_list_len_changed(
                                model, button_weak, limit
                            )
                        )

                        def on_drop_fn(event, model_weak):
                            model_weak = model_weak()
                            if not model_weak:
                                return

                            paths = event.mime_data.split("\n")
                            on_add_relationships(weakref.ref(model_weak), paths)

                        button.set_drop_fn(
                            lambda event, model_weak=weakref.ref(item_model.value_model): on_drop_fn(event, model_weak)
                        )
                        extra_widgets.append(button)
                        cls.create_mixed_text_overlay(content_clipping=1)
                    ui.Spacer(width=12)

                    def on_model_value_changed(model):
                        value = model.get_value()
                        # hide treeview if mixed-editing or no node
                        tree_frame_stack.visible = not model.is_ambiguous() and bool(value)
                        button.visible = not model.is_ambiguous()
                        relationship_mixed.visible = model.is_ambiguous()

                    item_model.value_model.add_value_changed_fn(on_model_value_changed)
                    on_model_value_changed(item_model.value_model)

            return item_model

    @classmethod
    def fallback_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the fallback builder for the asset entry.

        This method builds the fallback builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The fallback builder model.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            model_kwargs = get_model_kwargs(additional_widget_kwargs)
            model_cls = get_model_cls(UsdAttributeModel, additional_widget_kwargs)
            model = model_cls(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
            )
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            kwargs = {
                "name": "models_readonly",
                "model": model,
                "enabled": False,
                "tooltip": model.get_value_as_string(),
            }
            if additional_widget_kwargs:
                kwargs.update(additional_widget_kwargs)
            with ui.ZStack():
                value_widget = ui.StringField(**kwargs)
                value_widget.identifier = f"fallback_{attr_name}"
                mixed_overlay = cls.create_mixed_text_overlay()
            cls.create_control_state(value_widget=value_widget, mixed_overlay=mixed_overlay, **kwargs, label=label)
            return model

    @classmethod
    def floating_point_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the floating point builder for the asset entry.

        This method builds the floating point builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The floating point builder model.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            model_kwargs = cls.get_attr_value_range_kwargs(metadata)
            model_kwargs.update(get_model_kwargs(additional_widget_kwargs))
            model_cls = get_model_cls(UsdAttributeModel, additional_widget_kwargs)
            model = model_cls(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
            )
            # insert hard-range min/max before soft-range
            widget_kwargs = {"model": model}
            widget_kwargs.update(model_kwargs)
            soft_range_min, soft_range_max = cls.get_attr_value_soft_range(metadata, model)
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            widget_kwargs.update(cls.get_attr_value_soft_range_kwargs(metadata, model))
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            with ui.ZStack():
                if soft_range_min < soft_range_max:
                    value_widget = cls.create_drag_or_slider(ui.FloatDrag, ui.FloatDrag, **widget_kwargs)
                    cls._setup_soft_float_dynamic_range(attr_name, metadata, value_widget.step, model, value_widget)
                else:
                    value_widget = cls.create_drag_or_slider(ui.FloatDrag, ui.FloatSlider, **widget_kwargs)
                value_widget.identifier = f"float_slider_{attr_name}"
                mixed_overlay = cls.create_mixed_text_overlay(widget_model=model, model=model)
            cls.create_control_state(
                value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model

    @classmethod
    def integer_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the integer builder for the asset entry.

        This method builds the integer builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The integer model.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            is_mdl_enum = False
            sdr_metadata = metadata.get("sdrMetadata", None)
            if sdr_metadata and sdr_metadata.get("options", None):
                is_mdl_enum = True
            if is_mdl_enum:
                model_kwargs = get_model_kwargs(additional_widget_kwargs)
                model_cls = get_model_cls(MdlEnumAttributeModel, additional_widget_kwargs)
                model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
                )
                widget_kwargs = {"name": "choices", "model": model}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    value_widget = ui.ComboBox(model, **widget_kwargs)
                    mixed_overlay = cls.create_mixed_text_overlay(widget_model=model, model=model)
            else:
                model_kwargs = cls.get_attr_value_range_kwargs(metadata)
                if type_name.type == cls.tf_uint:
                    model_kwargs["min"] = 0
                model_kwargs.update(get_model_kwargs(additional_widget_kwargs))
                model_cls = get_model_cls(UsdAttributeModel, additional_widget_kwargs)
                model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
                )
                # insert hard-range min/max before soft-range
                widget_kwargs = {"model": model}
                widget_kwargs.update(model_kwargs)
                widget_kwargs.update(cls.get_attr_value_soft_range_kwargs(metadata, model))
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    value_widget = cls.create_drag_or_slider(ui.IntDrag, ui.IntSlider, **widget_kwargs)
                    mixed_overlay = cls.create_mixed_text_overlay(widget_model=model, model=model)

            value_widget.identifier = f"integer_slider_{attr_name}"
            cls.create_control_state(
                value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model

    @classmethod
    def bool_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the bool builder for the asset entry.

        This method builds the bool builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The bool model.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            model_kwargs = get_model_kwargs(additional_widget_kwargs)
            model_cls = get_model_cls(UsdAttributeModel, additional_widget_kwargs)
            model = model_cls(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
            )
            settings = carb.settings.get_settings()
            left_aligned = settings.get("ext/omni.kit.window.property/checkboxAlignment") == "left"

            if not left_aligned:
                if not additional_label_kwargs:
                    additional_label_kwargs = {}
                additional_label_kwargs["width"] = 0
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            if not left_aligned:
                ui.Spacer(width=10)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1))
                ui.Spacer(width=5)
            with ui.VStack(width=10):
                ui.Spacer()
                widget_kwargs = {"width": 10, "height": 0, "name": "greenCheck", "model": model}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    with ui.Placer(offset_x=0, offset_y=-2):
                        value_widget = ui.CheckBox(**widget_kwargs)
                        value_widget.identifier = f"bool_{attr_name}"
                    with ui.Placer(offset_x=1, offset_y=-1):
                        mixed_overlay = ui.Rectangle(
                            height=8, width=8, name="mixed_overlay", alignment=ui.Alignment.CENTER, visible=False
                        )
                ui.Spacer()
            if left_aligned:
                ui.Spacer(width=5)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1))
            cls.create_control_state(
                value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model

    @classmethod
    def bool_array_builder(
        cls: Type["UsdPropertiesWidgetBuilder"],
        stage: Usd.Stage,
        attr_name: str,
        type_name: Sdf.ValueTypeName,
        metadata: dict,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs: Union[dict | None] = None,
        additional_widget_kwargs: Union[dict | None] = None,
    ):
        """
        The array is split into components and each one has their own checkBox

        This method builds the bool array builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The bool array builder model.
        """

        bool_vector_types = ["bool2", "bool3", "bool4"]

        render_type = metadata.get(Sdr.PropertyMetadata.RenderType, None)
        if render_type not in bool_vector_types:
            return cls.fallback_builder(
                stage, attr_name, type_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
            )

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            return cls.create_bool_per_channel(
                stage,
                attr_name,
                prim_paths,
                bool_vector_types.index(render_type) + 2,
                type_name,
                type_name.type,
                metadata,
                label,
                additional_widget_kwargs,
            )

    @classmethod
    def string_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the string builder for the asset entry.

        This method builds the string builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The string builder model.
        """
        model = cls._create_filepath_for_ui_type(
            stage, attr_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
        )
        if model:
            return model

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            tokens = metadata.get("allowedTokens")
            if tokens is not None and len(tokens) > 0:
                model_kwargs = get_model_kwargs(additional_widget_kwargs)
                model_cls = get_model_cls(TfTokenAttributeModel, additional_widget_kwargs)
                model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
                )
                widget_kwargs = {"name": "choices"}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    value_widget = ui.ComboBox(model, **widget_kwargs)
                    mixed_overlay = cls.create_mixed_text_overlay()
            else:
                model_kwargs = get_model_kwargs(additional_widget_kwargs)
                model_cls = get_model_cls(UsdAttributeModel, additional_widget_kwargs)
                model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
                )
                widget_kwargs = {"name": "string"}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    value_widget = ui.StringField(model, **widget_kwargs)
                    value_widget.identifier = f"string_{attr_name}"
                    mixed_overlay = cls.create_mixed_text_overlay(widget_model=model, model=model)
            cls.create_control_state(
                model=model, value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model

    @classmethod
    def matrix_builder(
        cls: Type["UsdPropertiesWidgetBuilder"],
        matrix_model: MatrixBaseAttributeModel,
        column_count: int,
        stage: Usd.Stage,
        attr_name: str,
        metadata: dict,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs: Union[dict | None] = None,
        additional_widget_kwargs: Union[dict | None] = None,
    ) -> MatrixBaseAttributeModel:
        """
        Builds the matrix builder for the asset entry.

        This method builds the matrix builder for the asset entry.

        Args:
            matrix_model: The matrix model.
            column_count: The column count.
            stage: The stage.
            attr_name: The attribute name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The matrix builder model.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)

            widget_kwargs = get_model_kwargs(additional_widget_kwargs)

            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            value_widget = ui.MultiFloatDragField(
                matrix_model, **widget_kwargs, column_count=column_count, width=ui.Percent(50), h_spacing=5, v_spacing=2
            )

            value_widget.identifier = f"matrix_{attr_name}"

            mixed_overlay = cls.create_mixed_text_overlay(widget_model=matrix_model, model=matrix_model)

            cls.create_control_state(
                model=matrix_model, value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )

            return matrix_model

    @classmethod
    def gf_matrix_builder(
        cls: Type["UsdPropertiesWidgetBuilder"],
        stage: Usd.Stage,
        attr_name: str,
        type_name: Sdf.ValueTypeName,
        metadata: dict,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs: Union[dict | None] = None,
        additional_widget_kwargs: Union[dict | None] = None,
    ) -> Union[GfMatrixAttributeModel | None]:
        """
        Builds the gf matrix builder for the asset entry.

        This method builds the gf matrix builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The gf matrix builder model.
        """
        matrix_types = {
            Sdf.ValueTypeNames.Matrix2d: 2,
            Sdf.ValueTypeNames.Matrix3d: 3,
            Sdf.ValueTypeNames.Matrix4d: 4,
            Sdf.ValueTypeNames.Frame4d: 4,
        }
        column_count = matrix_types.get(type_name, None)
        if not column_count:
            carb.log_warn(f"gf_matrix_builder cannot determine column count for typename: '{type_name.type}'.")
            return None

        model_cls = get_model_cls(GfMatrixAttributeModel, additional_widget_kwargs)
        model = model_cls(
            stage,
            [path.AppendProperty(attr_name) for path in prim_paths],
            column_count,
            type_name.type,
            False,
            metadata,
        )

        return cls.matrix_builder(
            model,
            column_count,
            stage,
            attr_name,
            metadata,
            prim_paths,
            additional_label_kwargs,
            additional_widget_kwargs,
        )

    @classmethod
    def vec2_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):  # pragma: no cover
        """
        The entire vector is built as one multi-drag field

        This method builds the vec2 builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The vec2 builder model.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            model_kwargs = cls.get_attr_value_range_kwargs(metadata)
            model_kwargs.update(get_model_kwargs(additional_widget_kwargs))
            model_cls = get_model_cls(GfVecAttributeModel, additional_widget_kwargs)
            model = model_cls(
                stage,
                [path.AppendProperty(attr_name) for path in prim_paths],
                2,
                type_name.type,
                False,
                metadata,
                **model_kwargs,
            )
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            widget_kwargs = {"model": model}
            widget_kwargs.update(cls.get_attr_value_soft_range_kwargs(metadata, model))
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            create_drag_fn = (
                cls.create_multi_int_drag_with_labels
                if type_name.type.typeName.endswith("i")
                else cls.create_multi_float_drag_with_labels
            )
            value_widget, mixed_overlay = create_drag_fn(
                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371)], comp_count=2, **widget_kwargs
            )
            value_widget.identifier = f"vec2_{attr_name}"
            cls.create_control_state(
                value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model

    @classmethod
    def vec2_per_channel_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        The vector is split into components and each one has their own drag field and status control
        """
        custom_data = metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            # Note: bool_array_builder() is used to create the widgets for the MDL vector Boolean shader parameters: bool2, bool3 and bool4.
            # however the following is required to maintain backwards compatibility w/ older scenes that stored these values as USD int2, int3 and int4 values.
            if (
                custom_data
                and "mdl" in custom_data
                and "type" in custom_data["mdl"]
                and custom_data["mdl"]["type"] == "bool2"
            ):
                return cls.create_bool_per_channel(
                    stage,
                    attr_name,
                    prim_paths,
                    2,
                    type_name,
                    type_name.type,
                    metadata,
                    label,
                    additional_widget_kwargs,
                )
            return cls.create_color_or_drag_per_channel(
                stage,
                attr_name,
                prim_paths,
                2,
                type_name,
                type_name.type,
                metadata,
                label,
                additional_widget_kwargs,
            )

    @classmethod
    def vec3_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):  # pragma: no cover
        """
        The entire vector is built as one multi-drag field
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            return cls.create_color_or_multidrag(
                stage, attr_name, prim_paths, 3, type_name, type_name.type, metadata, label, additional_widget_kwargs
            )

    @classmethod
    def vec3_per_channel_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        The vector is split into components and each one has their own drag field and status control
        """
        custom_data = metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            # Note: bool_array_builder() is used to create the widgets for the MDL vector Boolean shader parameters: bool2, bool3 and bool4.
            # however the following is required to maintain backwards compatibility w/ older scenes that stored these values as USD int2, int3 and int4 values.
            if (
                custom_data
                and "mdl" in custom_data
                and "type" in custom_data["mdl"]
                and custom_data["mdl"]["type"] == "bool3"
            ):
                return cls.create_bool_per_channel(
                    stage,
                    attr_name,
                    prim_paths,
                    3,
                    type_name,
                    type_name.type,
                    metadata,
                    label,
                    additional_widget_kwargs,
                )
            return cls.create_color_or_drag_per_channel(
                stage,
                attr_name,
                prim_paths,
                3,
                type_name,
                type_name.type,
                metadata,
                label,
                additional_widget_kwargs,
            )

    @classmethod
    def vec4_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):  # pragma: no cover
        """
        The entire vector is built as one multi-drag field
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            return cls.create_color_or_multidrag(
                stage, attr_name, prim_paths, 4, type_name, type_name.type, metadata, label, additional_widget_kwargs
            )

    @classmethod
    def vec4_per_channel_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        The vector is split into components and each one has their own drag field and status control
        """
        custom_data = metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            # Note: bool_array_builder() is used to create the widgets for the MDL vector Boolean shader parameters: bool2, bool3 and bool4.
            # however the following is required to maintain backwards compatibility w/ older scenes that stored these values as USD int2, int3 and int4 values.
            if (
                custom_data
                and "mdl" in custom_data
                and "type" in custom_data["mdl"]
                and custom_data["mdl"]["type"] == "bool4"
            ):
                return cls.create_bool_per_channel(
                    stage,
                    attr_name,
                    prim_paths,
                    4,
                    type_name,
                    type_name.type,
                    metadata,
                    label,
                    additional_widget_kwargs,
                )
            return cls.create_color_or_drag_per_channel(
                stage,
                attr_name,
                prim_paths,
                4,
                type_name,
                type_name.type,
                metadata,
                label,
                additional_widget_kwargs,
            )

    @classmethod
    def tftoken_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the tftoken builder for the asset entry.

        This method builds the tftoken builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The tftoken builder model.
        """

        def on_model_item_changed(model, item, widget):
            from omni.kit.property.usd.usd_style import Styles

            value = model.get_value()

            if value and not model.is_allowed_token(value):
                widget.set_style({"color": Styles.REFERENCE_ERROR})
            else:
                widget.set_style({})

        model = cls._create_filepath_for_ui_type(
            stage, attr_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
        )
        if model:
            return model

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            model = None
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            tokens = metadata.get("allowedTokens")
            if tokens is not None and len(tokens) > 0:
                model_kwargs = get_model_kwargs(additional_widget_kwargs)
                model_cls = get_model_cls(TfTokenAttributeModel, additional_widget_kwargs)
                model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
                )
                widget_kwargs = {"name": "choices"}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    value_widget = ui.ComboBox(model, **widget_kwargs)
                    value_widget.model.add_item_changed_fn(partial(on_model_item_changed, widget=value_widget))
                    mixed_overlay = cls.create_mixed_text_overlay()
                    on_model_item_changed(value_widget.model, None, value_widget)
            else:
                model_kwargs = get_model_kwargs(additional_widget_kwargs)
                model_cls = get_model_cls(
                    UsdAttributeModel, additional_widget_kwargs, key="no_allowed_tokens_model_cls"
                )
                model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
                )
                widget_kwargs = {"name": "models"}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                with ui.ZStack():
                    value_widget = ui.StringField(model, **widget_kwargs)
                    mixed_overlay = cls.create_mixed_text_overlay(widget_model=model, model=model)
            value_widget.identifier = f"token_{attr_name}"

            cls.create_control_state(
                model=model, value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model

    @classmethod
    def _build_asset_checkpoint_ui(cls, model, frame):
        """
        Builds the asset checkpoint ui for the asset entry.

        This method builds the asset checkpoint ui for the asset entry.

        Args:
            model: The model.
            frame: The frame.
        """
        try:
            from .versioning_helper import VersioningHelper

            absolute_asset_path = model.get_resolved_path()
            if VersioningHelper.is_versioning_enabled() and absolute_asset_path:
                # Use checkpoint widget in the drop down menu for more detailed information
                from omni.kit.widget.versioning.checkpoint_combobox import CheckpointCombobox

                spacer = ui.Spacer(height=5)
                stack = ui.HStack()
                with stack:
                    UsdPropertiesWidgetBuilder.create_label("Checkpoint", additional_label_kwargs={"width": 80})

                    def on_selection_changed(model_or_item, model):
                        url = model.get_resolved_path()
                        try:
                            from omni.kit.widget.versioning.checkpoints_model import CheckpointItem

                            checkpoint = ""
                            if isinstance(model_or_item, CheckpointItem):
                                checkpoint = model_or_item.get_relative_path()
                            elif model_or_item is None:
                                checkpoint = ""
                        except ModuleNotFoundError:
                            pass

                        client_url = omni.client.break_url(url)
                        new_path = omni.client.make_url(
                            scheme=client_url.scheme,
                            user=client_url.user,
                            host=client_url.host,
                            port=client_url.port,
                            path=client_url.path,
                            query=checkpoint,
                            fragment=client_url.fragment,
                        )
                        if url != new_path:
                            model.set_value(new_path)
                            frame.rebuild()

                    CheckpointCombobox(absolute_asset_path, lambda si, m=model: on_selection_changed(si, m))

                    # reset button
                    def reset_func(model):
                        on_selection_changed(None, model)
                        frame.rebuild()

                    checkpoint = ""
                    client_url = omni.client.break_url(model.get_resolved_path())
                    if client_url.query:
                        _, checkpoint = omni.client.get_branch_and_checkpoint_from_query(client_url.query)
                    ui.Spacer(width=4)
                    ui.Image(
                        (
                            f"{widgets.ICON_PATH}/Default value.svg"
                            if checkpoint == ""
                            else f"{widgets.ICON_PATH}/Changed value.svg"
                        ),
                        mouse_pressed_fn=lambda x, y, b, a, m=model: reset_func(m),
                        width=12,
                        height=18,
                        tooltip="Reset Checkpoint" if checkpoint else "",
                    )

                    def on_have_server_info(server: str, support_checkpoint: bool, ui_items: list):
                        if not support_checkpoint:
                            for item in ui_items:
                                item.visible = False

                    VersioningHelper.check_server_checkpoint_support(
                        VersioningHelper.extract_server_from_url(absolute_asset_path),
                        lambda s, c, i=[spacer, stack]: on_have_server_info(s, c, i),
                    )

                    return
        except ImportError as e:
            # If the widget is not available, create a simple combo box instead
            carb.log_warn(f"Checkpoint widget in Asset is not available due to: {e}")

    @classmethod
    def sdf_asset_path_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the sdf asset path builder for the asset entry.

        This method builds the sdf asset path builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The sdf asset path builder model.
        """
        model_kwargs = get_model_kwargs(additional_widget_kwargs)
        model_cls = get_model_cls(SdfAssetPathAttributeModel, additional_widget_kwargs)
        model = model_cls(
            stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
        )

        # List of models. It's possible that the path is texture related path, which
        # will return colorSpace model also.
        return cls._create_path_widget(
            model, stage, attr_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
        )

    @classmethod
    def sdf_asset_path_array_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Builds the sdf asset path array builder for the asset entry.

        This method builds the sdf asset path array builder for the asset entry.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The sdf asset path array builder model.
        """
        widget_kwargs = {"name": "models"}
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)

        models = []

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)

            with ui.VStack():
                delegate_cls = get_model_cls(SdfAssetPathDelegate, additional_widget_kwargs, key="delegate_cls")
                delegate = delegate_cls(stage, attr_name, widget_kwargs)
                model_cls = get_model_cls(SdfAssetPathArrayAttributeItemModel, additional_widget_kwargs)
                item_model = model_cls(
                    stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, delegate
                )

                # content_clipping so drag n drop in tree view doesn't scroll the outer frame
                tree_frame_stack = ui.HStack(spacing=HORIZONTAL_SPACING, content_clipping=1)
                with tree_frame_stack:
                    with ui.Frame(height=0):
                        tree_view = ui.TreeView(
                            item_model,
                            delegate=delegate,
                            root_visible=False,
                            header_visible=False,
                            drop_between_items=True,
                            style={
                                "TreeView:selected": {"background_color": 0x00},
                                "TreeView": {"background_color": 0xFFFFFFFF},  # reorder indicator
                            },
                        )
                        tree_view.identifier = f"sdf_asset_array_{attr_name}"

                    ui.Spacer(width=12)
                with ui.HStack(spacing=HORIZONTAL_SPACING, height=LABEL_HEIGHT):
                    extra_widgets = []
                    with ui.ZStack():

                        def assign_value_fn(model, path):
                            value = model.get_value()
                            if not isinstance(value, Sdf.AssetPathArray):
                                list_value = []
                                for item in value:
                                    list_value.append(Sdf.AssetPath(item.path, item.resolvedPath))
                            else:
                                list_value = list(value)

                            list_value.append(Sdf.AssetPath(path))
                            model.set_value(Sdf.AssetPathArray(list_value))

                        button = ui.Button(
                            f"{_get_plus_glyph()} Add Asset...",
                            clicked_fn=lambda model_weak=weakref.ref(item_model.value_model), stage_weak=weakref.ref(
                                stage
                            ): show_asset_file_picker(
                                "Select Asset...",
                                assign_value_fn,
                                model_weak,
                                stage_weak,
                                multi_selection=True,
                                on_selected_fn=cls._assign_asset_path_value,
                            ),
                        )
                        button.identifier = f"sdf_asset_array_{attr_name}.add_asset"
                        button.set_accept_drop_fn(
                            lambda url, model_weak=weakref.ref(item_model.value_model): cls.can_accept_file_drop(
                                url, model_weak, True
                            )
                        )

                        def on_drop_fn(event, model_weak):
                            model_weak = model_weak()
                            if not model_weak:
                                return

                            paths = event.mime_data.split("\n")
                            with omni.kit.undo.group():
                                for path in paths:
                                    path = cls.convert_asset_path(path)
                                    assign_value_fn(model_weak, path)

                        button.set_drop_fn(
                            lambda event, model_weak=weakref.ref(item_model.value_model): on_drop_fn(event, model_weak)
                        )
                        extra_widgets.append(button)
                        mixed_overlay = cls.create_mixed_text_overlay(content_clipping=1)

                    def on_model_value_changed(model: UsdAttributeModel):
                        value = model.get_value()
                        # hide treeview if mixed-editing or no node
                        tree_frame_stack.visible = not model.is_ambiguous() and bool(value)
                        button.visible = not model.is_ambiguous()

                    item_model.value_model.add_value_changed_fn(on_model_value_changed)
                    on_model_value_changed(item_model.value_model)

                    cls.create_control_state(
                        item_model.value_model,
                        value_widget=tree_view,
                        mixed_overlay=mixed_overlay,
                        extra_widgets=extra_widgets,
                        **widget_kwargs,
                        label=label,
                    )

            models.append(item_model)
            return models

    @classmethod
    def _get_alignment(cls):
        """
        Gets the alignment for the label.

        This method gets the alignment for the label.

        Returns:
            The alignment.
        """
        settings = carb.settings.get_settings()
        return (
            ui.Alignment.RIGHT
            if settings.get("/ext/omni.kit.window.property/labelAlignment") == "right"
            else ui.Alignment.LEFT
        )

    @classmethod
    def create_label(cls, attr_name, metadata=None, additional_label_kwargs=None):
        """
        Creates a label for the attribute.

        This method creates a label for the attribute.

        Args:
            attr_name: The attribute name.
            metadata: The metadata.
            additional_label_kwargs: The additional label kwargs.

        Returns:
            The label widget.
        """
        alignment = cls._get_alignment()
        label_kwargs = {
            "name": "label",
            "word_wrap": not (
                additional_label_kwargs
                and "elided_text" in additional_label_kwargs
                and additional_label_kwargs["elided_text"]
            ),
            "width": LABEL_WIDTH,
            "height": LABEL_HEIGHT,
            "label_width": (
                ui.Percent(100) if additional_label_kwargs and "elided_text" in additional_label_kwargs else 0
            ),
            "alignment": alignment,
        }
        if get_ui_style() == "NvidiaLight":
            label_kwargs["width"] = LABEL_WIDTH_LIGHT
        if additional_label_kwargs:
            label_kwargs.update(additional_label_kwargs)
        if metadata and "tooltip" not in label_kwargs:
            label_kwargs["tooltip"] = cls.generate_tooltip_string(attr_name, metadata)
        label = HighlightLabel(cls.get_display_name(attr_name, metadata), **label_kwargs)
        ui.Spacer(width=5)
        return label

    @classmethod
    def create_text_label(cls, attr_name, metadata=None, additional_label_kwargs=None):
        """
        Creates a text label for the attribute.

        This method creates a text label for the attribute.

        Args:
            attr_name: The attribute name.
            metadata: The metadata.
            additional_label_kwargs: The additional label kwargs.

        Returns:
            The text label widget.
        """
        alignment = cls._get_alignment()
        label_kwargs = {
            "name": "label",
            "word_wrap": not (
                additional_label_kwargs
                and "elided_text" in additional_label_kwargs
                and additional_label_kwargs["elided_text"]
            ),
            "width": LABEL_WIDTH,
            "height": LABEL_HEIGHT,
            "label_width": (
                ui.Percent(100) if additional_label_kwargs and "elided_text" in additional_label_kwargs else 0
            ),
            "alignment": alignment,
        }

        def open_url(url):
            import webbrowser

            webbrowser.open(url)

        if get_ui_style() == "NvidiaLight":
            label_kwargs["width"] = LABEL_WIDTH_LIGHT
        if additional_label_kwargs:
            label_kwargs.update(additional_label_kwargs)
        if metadata and "tooltip" not in label_kwargs:
            label_kwargs["tooltip"] = cls.generate_tooltip_string(attr_name, metadata)
        display_name = cls.get_display_name(attr_name, metadata)

        # TODO: not sure why only support http url here, need David to confirm
        if display_name.startswith("http"):
            label_kwargs["name"] = "url"
            label = ui.StringField(**label_kwargs)
            label.model.set_value(display_name)
            label.set_mouse_pressed_fn(lambda x, y, b, m, url=display_name: open_url(url))
        else:
            label = ui.StringField(**label_kwargs)
            label.model.set_value(display_name)

        ui.Spacer(width=5)
        return label

    @classmethod
    def generate_tooltip_string(cls, attr_name, metadata):
        """
        Generates a tooltip string for the attribute.

        This method generates a tooltip string for the attribute.

        Args:
            attr_name: The attribute name.
            metadata: The metadata.

        Returns:
            The tooltip string.
        """
        doc_string = metadata.get(Sdf.PropertySpec.DocumentationKey)
        type_name = cls.get_type_name(metadata)
        tooltip = f"{attr_name} ({type_name})" if not doc_string else f"{attr_name} ({type_name})\n\t\t{doc_string}"
        return tooltip

    @classmethod
    def create_attribute_context_menu(cls, widget, model, comp_index=-1):
        """
        Creates an attribute context menu for the attribute.

        This method creates an attribute context menu for the attribute.

        Args:
            widget: The widget.
            model: The model.
            comp_index: The component index.

        Returns:
            The attribute context menu.
        """

        def show_attribute_context_menu(b, widget_ref, model_ref):
            if b != 1:
                return

            if not model_ref:
                return

            if not widget_ref:
                return

            event = AttributeContextMenuEvent(
                widget_ref,
                model.get_attribute_paths(),
                model_ref.get_stage(),
                model_ref.get_current_time_code(),
                model_ref,
                comp_index,
            )
            AttributeContextMenu.get_instance().on_mouse_event(event)

        widget.set_mouse_pressed_fn(
            lambda x, y, b, _: show_attribute_context_menu(b, weakref.proxy(widget), weakref.proxy(model))
        )

    ###### helper funcs ######

    @staticmethod
    def get_attr_value_range(metadata):
        """
        Gets the attribute value range.

        This method gets the attribute value range.

        Args:
            metadata: The metadata.

        Returns:
            The attribute value range.
        """
        custom_data = metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        range_mm = custom_data.get("range", {})
        range_min = range_mm.get("min", 0)
        range_max = range_mm.get("max", 0)

        # TODO: IMGUI DragScalarN only support scalar range for all vector component.
        # Need to change it to support per component range.
        if hasattr(range_min, "__getitem__"):
            range_min = range_min[0]
        if hasattr(range_max, "__getitem__"):
            range_max = range_max[0]

        return range_min, range_max

    @staticmethod
    def _get_attr_value_ui_type(metadata):
        """
        Gets the attribute value UI type.

        This method gets the attribute value UI type.

        Args:
            metadata: The metadata.

        Returns:
            The attribute value UI type.
        """
        custom_data = metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        return custom_data.get("uiType")

    @classmethod
    def _setup_soft_float_dynamic_range(cls, attr_name, metadata, default_step, model, widget):
        """
        Sets up the soft float dynamic range.

        This method sets up the soft float dynamic range.

        Args:
            attr_name: The attribute name.
            metadata: The metadata.
            default_step: The default step.
            model: The model.
            widget: The widget.
        """
        # pylint: disable=protected-access

        soft_range_min, soft_range_max = cls.get_attr_value_soft_range(metadata, model)
        if soft_range_min < soft_range_max:

            def on_end_edit(model, widget, attr_name, metadata, soft_range_min, soft_range_max):
                default_range = True

                value = model.get_value()
                # TODO: IMGUI DragScalarN only support scalar range for all vector component.
                # Need to change it to support per component range.
                if hasattr(value, "__getitem__"):
                    value = value[0]

                if model._soft_range_min is not None and model._soft_range_min < soft_range_min:
                    soft_range_min = model._soft_range_min
                    default_range = False
                if model._soft_range_max is not None and model._soft_range_max > soft_range_max:
                    soft_range_max = model._soft_range_max
                    default_range = False

                if value < soft_range_min:
                    soft_range_min = value
                    model.set_soft_range_userdata(soft_range_min, soft_range_max)
                    default_range = False

                if value > soft_range_max:
                    soft_range_max = value
                    model.set_soft_range_userdata(soft_range_min, soft_range_max)
                    default_range = False

                widget.min = soft_range_min
                widget.max = soft_range_max
                if not default_range:
                    if attr_name not in cls.default_range_steps:
                        cls.default_range_steps[attr_name] = widget.step
                    widget.step = max(0.1, (soft_range_max - soft_range_min) / 1000.0)

            def on_set_default(model, widget, attr_name, metadata):
                soft_range_min, soft_range_max = cls.get_attr_value_soft_range(metadata, model, False)
                widget.min = soft_range_min
                widget.max = soft_range_max
                if attr_name in cls.default_range_steps:
                    widget.step = cls.default_range_steps[attr_name]

            model.add_end_edit_fn(
                lambda m, w=widget, n=attr_name, md=metadata, min=soft_range_min, max=soft_range_max: on_end_edit(
                    m, w, n, md, min, max
                )
            )
            model.set_on_set_default_fn(lambda m=model, w=widget, n=attr_name, md=metadata: on_set_default(m, w, n, md))

    @classmethod
    def get_attr_value_range_kwargs(cls, metadata):
        """
        Gets the attribute value range kwargs.

        This method gets the attribute value range kwargs.

        Args:
            metadata: The metadata.

        Returns:
            The attribute value range kwargs.
        """
        kwargs = {}
        range_min, range_max = cls.get_attr_value_range(metadata)

        # only set range if soft_range is valid (min < max)
        if range_min < range_max:
            kwargs["min"] = range_min
            kwargs["max"] = range_max

        return kwargs

    @staticmethod
    def get_attr_value_soft_range(metadata, model=None, use_override=True):
        """
        Gets the attribute value soft range.

        This method gets the attribute value soft range.

        Args:
            metadata: The metadata.
            model: The model.
            use_override: Whether to use the override.

        Returns:
            The attribute value soft range.
        """
        # pylint: disable=protected-access

        custom_data = metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        soft_range = custom_data.get("soft_range", {})
        soft_range_min = soft_range.get("min", 0)
        soft_range_max = soft_range.get("max", 0)

        # TODO: IMGUI DragScalarN only support scalar range for all vector component.
        # Need to change it to support per component range.
        if hasattr(soft_range_min, "__getitem__"):
            soft_range_min = soft_range_min[0]
        if hasattr(soft_range_max, "__getitem__"):
            soft_range_max = soft_range_max[0]

        if model and use_override:
            value = model.get_value()
            if hasattr(value, "__getitem__"):
                value = value[0]

            if model._soft_range_min is not None and model._soft_range_min < soft_range_min:
                soft_range_min = model._soft_range_min
            if model._soft_range_max is not None and model._soft_range_max > soft_range_max:
                soft_range_max = model._soft_range_max

            if soft_range_min < soft_range_max:
                if value < soft_range_min:
                    soft_range_min = value
                    model.set_soft_range_userdata(soft_range_min, soft_range_max)
                if value > soft_range_max:
                    soft_range_max = value
                    model.set_soft_range_userdata(soft_range_min, soft_range_max)

        return soft_range_min, soft_range_max

    @classmethod
    def get_attr_value_soft_range_kwargs(cls, metadata, model=None):
        """
        Gets the attribute value soft range kwargs.

        This method gets the attribute value soft range kwargs.

        Args:
            metadata: The metadata.
            model: The model.

        Returns:
            The attribute value soft range kwargs.
        """
        kwargs = {}
        range_min, range_max = cls.get_attr_value_soft_range(metadata, model)

        # only set soft_range if soft_range is valid (min < max)
        if range_min < range_max:
            kwargs["min"] = range_min
            kwargs["max"] = range_max
            model.update_control_state()

        return kwargs

    @staticmethod
    def create_drag_or_slider(drag_widget, slider_widget, **kwargs):
        """
        Creates a drag or slider widget.

        This method creates a drag or slider widget.

        Args:
            drag_widget: The drag widget.
            slider_widget: The slider widget.
            kwargs: The keyword arguments.

        Returns:
            The drag or slider widget.
        """
        if "min" in kwargs and "max" in kwargs:
            range_min = kwargs["min"]
            range_max = kwargs["max"]
            if range_max - range_min < 100:
                return slider_widget(name="value", **kwargs)

            if "step" not in kwargs:
                kwargs["step"] = max(0.1, (range_max - range_min) / 1000.0)
        else:
            if "step" not in kwargs:
                kwargs["step"] = 0.1

        # If range is too big or no range, don't use a slider
        return drag_widget(name="value", **kwargs)

    @classmethod
    def create_multi_float_drag_with_labels(cls, model, labels, comp_count, **kwargs):  # pragma: no cover
        """
        Creates a multi float drag with labels.

        This method creates a multi float drag with labels.

        Args:
            model: The model.
            labels: The labels.
            comp_count: The component count.
            kwargs: The keyword arguments.

        Returns:
            The multi float drag with widget and overlay widget.
        """
        return cls.create_multi_drag_with_labels(ui.MultiFloatDragField, model, labels, comp_count, **kwargs)

    @classmethod
    def create_multi_int_drag_with_labels(cls, model, labels, comp_count, **kwargs):  # pragma: no cover
        """
        Creates a multi int drag with labels.

        This method creates a multi int drag with labels.

        Args:
            model: The model.
            labels: The labels.
            comp_count: The component count.
            kwargs: The keyword arguments.

        Returns:
            The multi int drag with widget and overlay widget.
        """
        return cls.create_multi_drag_with_labels(ui.MultiIntDragField, model, labels, comp_count, **kwargs)

    @classmethod
    def create_multi_drag_with_labels(cls, drag_field_widget, model, labels, comp_count, **kwargs):  # pragma: no cover
        """
        Creates a multi drag with labels.

        This method creates a multi drag with labels.

        Args:
            drag_field_widget: The drag field widget.
            model: The model.
            labels: The labels.
            comp_count: The component count.
            kwargs: The keyword arguments.

        Returns:
            The multi drag with widget and overlay widget.
        """
        RECT_WIDTH = 13  # noqa: N806
        SPACING = 4  # noqa: N806

        with ui.ZStack():
            with ui.HStack():
                ui.Spacer(width=RECT_WIDTH)
                widget_kwargs = {"name": "multivalue", "h_spacing": RECT_WIDTH + SPACING}
                widget_kwargs.update(kwargs)
                value_widget = drag_field_widget(model, **widget_kwargs)
            with ui.HStack():
                for i in range(comp_count):
                    if i != 0:
                        ui.Spacer(width=SPACING)
                    label = labels[i]
                    with ui.ZStack(width=RECT_WIDTH + 1):
                        ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                        ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                    ui.Spacer()
            mixed_overlay = []
            with ui.HStack():
                for i in range(comp_count):
                    ui.Spacer(width=RECT_WIDTH + SPACING)
                    item_model = model.get_item_value_model(model.get_item_children(None)[i], 0)
                    mixed_overlay.append(cls.create_mixed_text_overlay(item_model, model, i))

        return value_widget, mixed_overlay

    @classmethod
    def create_float_drag_per_channel_with_labels_and_control(cls, models, metadata, labels, **kwargs):
        """
        Creates a float drag per channel with labels and control.

        This method creates a float drag per channel with labels and control.

        Args:
            models: The models.
            metadata: The metadata.
            labels: The labels.
            kwargs: The keyword arguments.

        Returns:
            HStack widget.
        """
        return cls.create_drag_per_channel_with_labels_and_control(
            ui.FloatDrag, ui.FloatSlider, models, metadata, labels, **kwargs
        )

    @classmethod
    def create_int_drag_per_channel_with_labels_and_control(cls, models, metadata, labels, **kwargs):
        """
        Creates a int drag per channel with labels and control.

        This method creates a int drag per channel with labels and control.

        Args:
            models: The models.
            metadata: The metadata.
            labels: The labels.
            kwargs: The keyword arguments.

        Returns:
            HStack widget.
        """
        return cls.create_drag_per_channel_with_labels_and_control(
            ui.IntDrag, ui.IntSlider, models, metadata, labels, **kwargs
        )

    @classmethod
    def create_drag_per_channel_with_labels_and_control(
        cls, drag_field_widget, slider_field_widget, models, metadata, labels, **kwargs
    ):
        """
        Creates a drag per channel with labels and control.

        This method creates a drag per channel with labels and control.

        Args:
            drag_field_widget: The drag field widget.
            slider_field_widget: The slider field widget.
            models: The models.
            metadata: The metadata.
            labels: The labels.
            kwargs: The keyword arguments.

        Returns:
            HStack widget.
        """
        RECT_WIDTH = 13  # noqa: N806
        SPACING = 4  # noqa: N806

        hstack = ui.HStack()
        with hstack:
            for i, model in enumerate(models):
                with ui.HStack():
                    if i != 0:
                        ui.Spacer(width=SPACING)
                    label = labels[i]
                    with ui.ZStack(width=RECT_WIDTH + 1):
                        ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                        ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                    widget_kwargs = {"model": model}
                    widget_kwargs.update(cls.get_attr_value_soft_range_kwargs(metadata, model))
                    widget_kwargs.update(**kwargs)
                    soft_range_min, soft_range_max = cls.get_attr_value_soft_range(metadata, model)
                    with ui.ZStack():
                        if soft_range_min < soft_range_max:
                            value_widget = cls.create_drag_or_slider(
                                drag_field_widget, drag_field_widget, **widget_kwargs
                            )
                            cls._setup_soft_float_dynamic_range(
                                model.get_attribute_paths()[-1], metadata, value_widget.step, model, value_widget
                            )
                        else:
                            value_widget = cls.create_drag_or_slider(
                                drag_field_widget, slider_field_widget, **widget_kwargs
                            )
                        mixed_overlay = cls.create_mixed_text_overlay(model, model)

                    ui.Spacer(width=SPACING)
                    widget_kwargs["widget_comp_index"] = i
                    cls.create_control_state(value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs)
        return hstack

    @classmethod
    def create_color_or_multidrag(
        cls,
        stage,
        attr_name,
        prim_paths,
        comp_count,
        type_name,
        tf_type,
        metadata,
        label,
        additional_widget_kwargs=None,
    ):  # pragma: no cover
        """
        Creates a color or multidrag.

        This method creates a color or multidrag.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            prim_paths: The prim paths.
            comp_count: The component count.
            type_name: The type name.
            tf_type: The tf type.
            metadata: The metadata.
            label: The label.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The color or multidrag widget.
        """
        model_kwargs = cls.get_attr_value_range_kwargs(metadata)
        model_kwargs.update(get_model_kwargs(additional_widget_kwargs))
        extra_widgets = []
        model_cls = get_model_cls(GfVecAttributeModel, additional_widget_kwargs)
        model = model_cls(
            stage,
            [path.AppendProperty(attr_name) for path in prim_paths],
            comp_count,
            tf_type,
            False,
            metadata,
            **model_kwargs,
        )
        ui_type = ""
        if comp_count in (3, 4):
            ui_type = cls._get_attr_value_ui_type(metadata)

        if (
            type_name == Sdf.ValueTypeNames.Color3h
            or type_name == Sdf.ValueTypeNames.Color3f
            or type_name == Sdf.ValueTypeNames.Color3d
            or type_name == Sdf.ValueTypeNames.Color4h
            or type_name == Sdf.ValueTypeNames.Color4f
            or type_name == Sdf.ValueTypeNames.Color4d
            or ui_type == "color"
        ):
            widget_kwargs = {"min": 0.0, "max": 2.0, "model": model}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            with ui.HStack(spacing=4):
                value_widget, mixed_overlay = cls.create_multi_float_drag_with_labels(
                    labels=[("R", 0xFF5555AA), ("G", 0xFF76A371), ("B", 0xFFA07D4F), ("A", 0xFFFFFFFF)],
                    comp_count=comp_count,
                    **widget_kwargs,
                )
                extra_widgets.append(ui.ColorWidget(model, width=65, height=0))
        else:
            widget_kwargs = {"model": model}
            widget_kwargs.update(cls.get_attr_value_soft_range_kwargs(metadata, model))
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            create_drag_fn = (
                cls.create_multi_int_drag_with_labels
                if type_name.type.typeName.endswith("i")
                else cls.create_multi_float_drag_with_labels
            )
            value_widget, mixed_overlay = create_drag_fn(
                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F), ("W", 0xFFFFFFFF)],
                comp_count=comp_count,
                **widget_kwargs,
            )
            value_widget.identifier = f"color_{attr_name}"
        cls.create_control_state(
            value_widget=value_widget,
            mixed_overlay=mixed_overlay,
            extra_widgets=extra_widgets,
            **widget_kwargs,
            label=label,
        )
        return model

    @classmethod
    def create_bool_per_channel(
        cls,
        stage,
        attr_name,
        prim_paths,
        comp_count,
        type_name,
        tf_type,
        metadata,
        label,
        additional_widget_kwargs=None,
    ):
        """
        Creates a bool per channel.

        This method creates a bool per channel.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            prim_paths: The prim paths.
            comp_count: The component count.
            type_name: The type name.
            tf_type: The tf type.
            metadata: The metadata.
            label: The label.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The bool per channel widget.
        """
        # pylint: disable=protected-access

        model_kwargs = cls.get_attr_value_range_kwargs(metadata)
        model_kwargs.update(get_model_kwargs(additional_widget_kwargs))
        models = []

        # We need a UsdAttributeModel here for context menu and default button:
        model_cls = get_model_cls(UsdAttributeModel, additional_widget_kwargs)
        model = model_cls(
            stage,
            [path.AppendProperty(attr_name) for path in prim_paths],
            False,
            metadata,
            change_on_edit_end=True,
            **model_kwargs,
        )

        def on_model_value_changed(model: UsdAttributeModel):
            model._update_value()

        model.add_value_changed_fn(on_model_value_changed)

        single_channel_model_cls = get_model_cls(
            BoolArrayAttributeSingleChannelModel, additional_widget_kwargs, "single_channel_model_cls"
        )

        for i in range(comp_count):
            models.append(
                single_channel_model_cls(
                    stage,
                    [path.AppendProperty(attr_name) for path in prim_paths],
                    i,
                    False,
                    metadata,
                    change_on_edit_end=True,
                    **model_kwargs,
                )
            )

            widget_kwargs = {}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

        mixed_overlay = []
        with ui.ZStack():
            with ui.HStack(spacing=4, width=32):
                with ui.HStack(spacing=HORIZONTAL_SPACING, identifier=f"boolean_per_channel_{attr_name}"):
                    for channel_model in models:
                        with ui.VStack(width=10):
                            ui.Spacer()
                            with ui.ZStack():
                                with ui.Placer(offset_x=0, offset_y=-2):
                                    with ui.ZStack():
                                        ui.CheckBox(width=10, height=0, name="greenCheck", model=channel_model)
                                        mixed_overlay.append(
                                            ui.Rectangle(
                                                width=12,
                                                height=12,
                                                name="mixed_overlay",
                                                alignment=ui.Alignment.CENTER,
                                                visible=False,
                                            )
                                        )
                            ui.Spacer()

        ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1))
        ui.Spacer(width=5)
        models.append(model)
        cls.create_control_state(model=model, mixed_overlay=mixed_overlay, label=label)
        model._update_value()  # trigger an initial refresh. Only needed if the model is not assigned to a widget
        return models

    @classmethod
    def create_color_or_drag_per_channel(
        cls,
        stage,
        attr_name,
        prim_paths,
        comp_count,
        type_name,
        tf_type,
        metadata,
        label,
        additional_widget_kwargs=None,
    ):
        """
        Creates a color or drag per channel.

        This method creates a color or drag per channel.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            prim_paths: The prim paths.
            comp_count: The component count.
            type_name: The type name.
            tf_type: The tf type.
            metadata: The metadata.
            label: The label.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The color or drag per channel widget.
        """
        model_kwargs = cls.get_attr_value_range_kwargs(metadata)
        model_kwargs.update(get_model_kwargs(additional_widget_kwargs))
        extra_widgets = []
        models = []

        # We need a GfVecAttributeModel here for:
        # If attribute is a color, the color picker widget needs this model type
        # When copying value from attribute label, this model is used to fetch value.
        model_cls = get_model_cls(GfVecAttributeModel, additional_widget_kwargs)
        model = model_cls(
            stage,
            [path.AppendProperty(attr_name) for path in prim_paths],
            comp_count,
            tf_type,
            False,
            metadata,
            **model_kwargs,
        )

        single_channel_model_cls = get_model_cls(
            GfVecAttributeSingleChannelModel, additional_widget_kwargs, "single_channel_model_cls"
        )
        for i in range(comp_count):
            models.append(
                single_channel_model_cls(
                    stage,
                    [path.AppendProperty(attr_name) for path in prim_paths],
                    i,
                    False,
                    metadata,
                    **model_kwargs,
                )
            )

        ui_type = ""
        if comp_count in (3, 4):
            ui_type = cls._get_attr_value_ui_type(metadata)

        if (
            type_name == Sdf.ValueTypeNames.Color3h
            or type_name == Sdf.ValueTypeNames.Color3f
            or type_name == Sdf.ValueTypeNames.Color3d
            or type_name == Sdf.ValueTypeNames.Color4h
            or type_name == Sdf.ValueTypeNames.Color4f
            or type_name == Sdf.ValueTypeNames.Color4d
            or ui_type == "color"
        ):
            widget_kwargs = {"min": 0.0, "max": 2.0}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            with ui.HStack(spacing=4):
                labels = [("R", 0xFF5555AA), ("G", 0xFF76A371), ("B", 0xFFA07D4F), ("A", 0xFFFFFFFF)]
                value_widget = cls.create_float_drag_per_channel_with_labels_and_control(
                    models, metadata, labels, **widget_kwargs
                )
                color_picker = ui.ColorWidget(model, width=LABEL_HEIGHT, height=0)
                extra_widgets.append(color_picker)

                # append model AFTER create_float_drag_per_channel_with_labels_and_control call
                widget_kwargs["model"] = model
                models.append(model)
                cls.create_control_state(
                    value_widget=color_picker,
                    mixed_overlay=None,
                    extra_widgets=extra_widgets,
                    **widget_kwargs,
                    label=label,
                )

        else:
            widget_kwargs = {}
            widget_kwargs.update(cls.get_attr_value_soft_range_kwargs(metadata, model))
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            labels = [("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F), ("W", 0xFFFFFFFF)]

            if type_name.type.typeName.endswith("i"):
                value_widget = cls.create_int_drag_per_channel_with_labels_and_control(
                    models, metadata, labels, **widget_kwargs
                )
            else:
                value_widget = cls.create_float_drag_per_channel_with_labels_and_control(
                    models, metadata, labels, **widget_kwargs
                )

            # append model AFTER create_float_drag_per_channel_with_labels_and_control call
            models.append(model)
            cls.create_attribute_context_menu(label, model)

        value_widget.identifier = f"drag_per_channel_{attr_name}"
        return models

    @staticmethod
    def get_display_name(attr_name, metadata):
        """
        Gets the display name.

        This method gets the display name.

        Args:
            attr_name: The attribute name.
            metadata: The metadata.

        Returns:
            The display name.
        """
        if not metadata:
            return attr_name
        return metadata.get(Sdf.PropertySpec.DisplayNameKey, attr_name)

    @staticmethod
    def get_type_name(metadata):
        """
        Gets the type name.

        This method gets the type name.

        Args:
            metadata: The metadata.

        Returns:
            The type name.
        """
        type_name = metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")
        return Sdf.ValueTypeNames.Find(type_name)

    @staticmethod
    def create_mixed_text_overlay(widget_model=None, model=None, comp=-1, content_clipping: bool = False):
        """
        Creates a mixed text overlay.

        This method creates a mixed text overlay.

        Args:
            widget_model: The widget model.
            model: The model.
            comp: The component.
            content_clipping: The content clipping.

        Returns:
            The mixed text overlay widget.
        """
        with ui.ZStack(alignment=ui.Alignment.CENTER):
            stack = ui.ZStack(alignment=ui.Alignment.CENTER, visible=False, content_clipping=content_clipping)
            with stack:
                ui.Rectangle(alignment=ui.Alignment.CENTER, name="mixed_overlay_text")
                ui.Label("Mixed", name="mixed_overlay", alignment=ui.Alignment.CENTER)

        if widget_model and model is not None:
            hidden_on_edit = False

            def begin_edit(_):
                nonlocal hidden_on_edit
                if stack.visible:
                    stack.visible = False
                    hidden_on_edit = True

            def end_edit(_):
                nonlocal hidden_on_edit
                if hidden_on_edit:
                    if model.is_comp_ambiguous(comp):
                        stack.visible = True
                    hidden_on_edit = False

            widget_model.add_begin_edit_fn(begin_edit)
            widget_model.add_end_edit_fn(end_edit)
        return stack

    @staticmethod
    def is_model_readonly(model):
        """
        Checks if the model is readonly.

        This method checks if the model is readonly.

        Args:
            model: The model.

        Returns:
            True if the model is readonly, False otherwise.
        """
        return model.is_readonly() if hasattr(model, "is_readonly") else False

    @classmethod
    def create_control_state(cls, model, value_widget=None, mixed_overlay=None, extra_widgets=None, **kwargs):
        """
        Creates a control state.

        This method creates a control state.

        Args:
            model: The model.
            value_widget: The value widget.
            mixed_overlay: The mixed overlay.
            extra_widgets: The extra widgets.
            kwargs: The keyword arguments.
        """
        # Allow widgets to be displayed without the control state
        if kwargs.get("no_control_state"):
            return

        control_state_mgr = ControlStateManager.get_instance()

        no_default = kwargs.get("no_default", False)
        widget_comp_index = kwargs.get("widget_comp_index", -1)
        original_widget_name = value_widget.name if value_widget else ""

        original_widget_state = {}
        if value_widget:
            if UsdPropertiesWidgetBuilder.is_model_readonly(model):
                value_widget.enabled = False
            original_widget_state["value_widget"] = value_widget.enabled
        else:
            original_widget_state["value_widget"] = not UsdPropertiesWidgetBuilder.is_model_readonly(model)

        if extra_widgets:
            for index, widget in enumerate(extra_widgets):
                if UsdPropertiesWidgetBuilder.is_model_readonly(model):
                    widget.enabled = False
                original_widget_state[f"extra_widgets_{index}"] = widget.enabled

        def build_fn():
            state = model.control_state

            # no_default is actually no state
            if no_default:
                state = 0

            action, icon_path, tooltip = control_state_mgr.build_control_state(
                control_state=state,
                model=model,
                value_widget=value_widget,
                extra_widgets=extra_widgets if extra_widgets else [],
                mixed_overlay=mixed_overlay,
                original_widget_name=original_widget_name,
                **kwargs,
            )

            with ui.VStack():
                ui.Spacer()
                button = ui.ImageWithProvider(
                    icon_path,
                    mouse_pressed_fn=action,
                    width=12,
                    height=5 if state == 0 else 12,  # TODO let state decide
                    tooltip=tooltip,
                )
                ui.Spacer()

                attr_paths = model.get_attribute_paths()
                if attr_paths and len(attr_paths) > 0:
                    button.identifier = f"control_state_{attr_paths[0].elementString[1:]}"

        frame = ui.Frame(build_fn=build_fn, width=0)
        model.set_on_control_state_changed_fn(frame.rebuild)

        if value_widget:
            cls.create_attribute_context_menu(value_widget, model, widget_comp_index)

        label_widget = kwargs.get("label", None)
        if label_widget:
            # When right click on label, always copy entire value
            cls.create_attribute_context_menu(label_widget, model)

    @classmethod
    def time_code_builder(
        cls,
        stage,
        attr_name,
        type_name,
        metadata,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs=None,
        additional_widget_kwargs=None,
    ):
        """
        Creates a time code builder.

        This method creates a time code builder.

        Args:
            stage: The stage.
            attr_name: The attribute name.
            type_name: The type name.
            metadata: The metadata.
            prim_paths: The prim paths.
            additional_label_kwargs: The additional label kwargs.
            additional_widget_kwargs: The additional widget kwargs.

        Returns:
            The time code builder model.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            model_kwargs = get_model_kwargs(additional_widget_kwargs)
            model_cls = get_model_cls(SdfTimeCodeModel, additional_widget_kwargs)
            model = model_cls(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
            )
            label = cls.create_label(attr_name, metadata, additional_label_kwargs)
            _, _ = cls.get_attr_value_range(metadata)
            widget_kwargs = {"model": model}
            widget_kwargs.update(cls.get_attr_value_soft_range_kwargs(metadata, model))
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            with ui.ZStack():
                value_widget = cls.create_drag_or_slider(ui.FloatDrag, ui.FloatSlider, **widget_kwargs)
                value_widget.identifier = f"timecode_{attr_name}"
                mixed_overlay = cls.create_mixed_text_overlay()
            cls.create_control_state(
                value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model

    @staticmethod
    def can_accept_file_drop(payload: str, model_weak, allow_multi_files=False) -> bool:
        """
        Checks if the file drop is allowed.

        This method checks if the file drop is allowed.

        Args:
            payload: The payload.
            model_weak: The model weak.
            allow_multi_files: Whether to allow multiple files.

        Returns:
            True if the file drop is allowed, False otherwise.
        """
        model_weak = model_weak()
        if not model_weak:
            return False

        urls = payload.split("\n")

        if not urls:
            return False

        if not allow_multi_files and len(urls) > 1:
            carb.log_warn("sdf_asset_path_builder multi-file drag/drop not supported")
            return False

        custom_data = model_weak.metadata.get(Sdf.PrimSpec.CustomDataKey, {})
        file_exts_dict = custom_data.get("fileExts", {})

        for url in urls:
            accepted = False
            if file_exts_dict:
                for ext in file_exts_dict:
                    if fnmatch.fnmatch(url, ext):
                        accepted = True
                        break
                if not accepted:
                    carb.log_warn(f"Dropped file {url} does not match allowed extensions {list(file_exts_dict.keys())}")
            else:
                # TODO support filtering by file extension
                if "." in url:
                    # TODO dragging from stage view also result in a drop, which is a prim path not an asset path
                    # For now just check if dot presents in the url (indicating file extension).
                    accepted = True
            if not accepted:
                return False
        return True

    @staticmethod
    def convert_asset_path(path: str) -> str:
        """
        Converts an asset path.

        This method converts an asset path.

        Args:
            path: The path.

        Returns:
            The converted asset path.
        """
        # OM-79996: Remove the prefix for HDR dragged from environment window
        env_hdr_prefix = "env::hdr::"
        if path.startswith(env_hdr_prefix):
            path = path[len(env_hdr_prefix) :]

        # make_path_relative_to_current_edit_target returns path unchanged if "/persistent/app/material/dragDropMaterialPath" is set to absolute
        return omni.usd.make_path_relative_to_current_edit_target(path)

    @classmethod
    def build_path_field(cls, model, stage, attr_name, widget_kwargs, frame, extra_widgets):
        """
        Builds a path field.

        This method builds a path field.

        Args:
            model: The model.
            stage: The stage.
            attr_name: The attribute name.
            widget_kwargs: The widget kwargs.
            frame: The frame.
            extra_widgets: The extra widgets.

        Returns:
            The path field widget and overlay widget.
        """
        # pylint: disable=protected-access

        with ui.HStack():

            async def clear_name(widget: ui.StringField):
                widget.model.set_value("")

            async def name_changed(model, widget: ui.Button):
                widget.visible = model.get_value() not in ("", "@@")

            async def locate_name_changed(model, widget: ui.Button):
                # NOTE: changing style makes image disappear
                if model.is_editing():
                    return

                enabled = True
                if hasattr(model, "is_valid_path"):
                    enabled = model.is_valid_path()

                # do not enable locate button if model value is pointing to multiple different paths.
                enabled &= not model.is_ambiguous()

                # update widget
                missing_url = ""
                if isinstance(model.get_value(), Sdf.Path):
                    missing_url = (
                        f"Cannot locate file \"{model.get_value().path.replace('@', '')}\"" if model.get_value() else ""
                    )
                widget.enabled = enabled
                widget.tooltip = "Locate File" if enabled else missing_url

            async def edit_name_changed(model, widget: ui.Button):
                if model.is_editing():
                    return

                # update widget
                widget.enabled = bool(model.get_resolved_path())
                widget.tooltip = "Edit File" if enabled else ""

            def assign_value_fn(model, path: str, resolved_path: str = ""):
                if isinstance(model, SdfAssetPathAttributeModel):
                    model.set_value(path, resolved_path)
                else:
                    model.set_value(path)

            remove_style = {
                "Button.Image::remove": {"image_url": str(widgets.ICON_PATH.joinpath("remove-text.svg"))},
                "Button.Image::remove:hovered": {
                    "image_url": str(widgets.ICON_PATH.joinpath("remove-text-hovered.svg"))
                },
            }

            with ui.ZStack():
                with ui.ZStack(style=remove_style):
                    value_widget = ui.StringField(**widget_kwargs)
                    with ui.HStack():
                        ui.Spacer()
                        clear_widget_stack = ui.VStack(width=0, content_clipping=True)  # vertically center the button
                        with clear_widget_stack:
                            ui.Spacer()
                            clear_widget = ui.Button(
                                "",
                                width=20,
                                height=20,
                                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                                clicked_fn=lambda f=value_widget: asyncio.ensure_future(clear_name(f)),
                                name="remove",
                            )
                            ui.Spacer()

                    # turn path red if file not found
                    def on_complete(result, url, widget):
                        from omni.kit.property.usd.usd_style import Styles

                        if result == omni.client.Result.ERROR_NOT_FOUND or result is None:
                            widget.set_style({"color": Styles.REFERENCE_ERROR})
                        else:
                            widget.set_style({})

                    async def url_changed(model, stage, widget: ui.Widget):
                        if model and stage:
                            # Validate URL against the layer that authored the strongest value opinion.
                            layers = cls._get_layers_with_strongest_value_opinions_on_model(model, stage)
                            for layer in layers:
                                await cls.validate_url(model, layer, lambda r, u, w=widget: on_complete(r, u, w))

                    value_widget.model.add_value_changed_fn(
                        lambda m, w=clear_widget_stack: asyncio.ensure_future(name_changed(m, w))
                    )
                    value_widget.model.add_value_changed_fn(
                        lambda m, s=stage, w=value_widget: asyncio.ensure_future(url_changed(m, s, w))
                    )
                    value_widget.model._value_changed()

                value_widget.set_accept_drop_fn(
                    lambda url, model_weak=weakref.ref(model): cls.can_accept_file_drop(url, model_weak)
                )
                value_widget.set_drop_fn(
                    lambda event, model_weak=weakref.ref(model), stage_weak=weakref.ref(
                        stage
                    ): cls._assign_asset_path_value(stage_weak, model_weak, event.mime_data, assign_value_fn, frame)
                )
                value_widget.identifier = f"sdf_asset_{attr_name}" + (
                    f"[{model.index}]" if hasattr(model, "index") else ""
                )
                clear_widget.identifier = f"sdf_clear_asset_{attr_name}" + (
                    f"[{model.index}]" if hasattr(model, "index") else ""
                )
                mixed_overlay = cls.create_mixed_text_overlay()
            ui.Spacer(width=3)

            style = {"image_url": str(widgets.ICON_PATH.joinpath("small_folder.png"))}

            enabled = False
            try:
                from omni.kit.window.file_importer import get_file_importer

                enabled = get_file_importer() is not None
            except ModuleNotFoundError:
                pass

            browse_button = ui.Button(
                style=style,
                width=20,
                tooltip="Browse..." if enabled else "File importer not available",
                clicked_fn=lambda model_weak=weakref.ref(model), stage_weak=weakref.ref(stage): show_asset_file_picker(
                    "Select Asset...",
                    assign_value_fn,
                    model_weak,
                    stage_weak,
                    on_selected_fn=cls._assign_asset_resolved_value,
                ),
                enabled=enabled,
                identifier=f"sdf_browse_asset_{attr_name}" + (f"[{model.index}]" if hasattr(model, "index") else ""),
            )
            extra_widgets.append(clear_widget)
            extra_widgets.append(browse_button)
            extra_widgets.append(ui.Spacer(width=3))

            # Button to jump to the file in Content Window
            def locate_file(model, stage):
                async def locate_file_async(model, stage):
                    # omni.kit.window.content_browser is optional dependency
                    try:
                        import os

                        import omni.client
                        import omni.kit.app

                        await omni.kit.app.get_app().next_update_async()

                        url = ""
                        if hasattr(model, "get_resolved_path"):
                            url = model.get_resolved_path()
                            if url:
                                url = f"{omni.usd.correct_filename_case(os.path.dirname(url))}/{os.path.basename(url)}"
                        elif isinstance(model, ui.AbstractValueModel):
                            url = model.get_value_as_string()
                            url = url.replace("\\", "/")

                            if url and is_relative_path(url):
                                # relative path value should be resolved against the layer with strongest value opinion
                                layers = cls._get_layers_with_strongest_value_opinions_on_model(model, stage)
                                resolved_urls = []

                                for layer in layers:
                                    resolved_urls.append(
                                        omni.client.make_absolute_url_if_possible(layer.identifier, url)
                                    )

                                if resolved_urls and all(
                                    resolved_url == resolved_urls[0] for resolved_url in resolved_urls
                                ):
                                    url = resolved_urls[0]
                                else:
                                    # on multi-selection, if multiple attributes have same value but are from different
                                    # layers and resolve to different urls, it's seen as ambiguous and cannot jump
                                    url = ""

                        if not url:
                            return

                        client_url = omni.client.break_url(url)
                        if client_url:
                            url = omni.client.make_url(
                                scheme=client_url.scheme,
                                user=client_url.user,
                                host=client_url.host,
                                port=client_url.port,
                                path=client_url.path,
                            )

                        import omni.kit.window.content_browser

                        w = omni.ui.Workspace.get_window("Content")
                        if w and w.visible:
                            w.focus()
                        else:
                            omni.ui.Workspace.show_window("Content")
                        await omni.kit.app.get_app().next_update_async()

                        instance = omni.kit.window.content_browser.get_instance()
                        instance.navigate_to(url)
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        carb.log_warn(f"Failed to locate file: {e}")

                asyncio.ensure_future(locate_file_async(model, stage))

            style = {
                "image_url": str(widgets.ICON_PATH.joinpath("find.png")),
                "Button.Image:disabled": {"color": 0x88888888},
            }
            enabled = True
            if hasattr(model, "is_valid_path"):
                enabled = model.is_valid_path()

            # do not enable locate button if model value is pointing to multiple different paths.
            enabled &= not model.is_ambiguous()

            missing_url = ""
            if isinstance(model.get_value(), Sdf.Path):
                missing_url = (
                    f"Cannot locate file \"{model.get_value().path.replace('@', '')}\"" if model.get_value() else ""
                )

            locate_widget = ui.Button(
                style=style,
                width=20,
                enabled=enabled,
                tooltip="Locate File" if enabled else missing_url,
                clicked_fn=lambda model=model: locate_file(model, stage),
                identifier=f"sdf_locate_asset_{attr_name}" + (f"[{model.index}]" if hasattr(model, "index") else ""),
            )
            value_widget.model.add_value_changed_fn(
                lambda m, w=locate_widget: asyncio.ensure_future(locate_name_changed(m, w))
            )
            extra_widgets.append(locate_widget)

            if "on_edit_fn" in widget_kwargs:
                edit_style = {
                    "image_url": "resources/glyphs/pencil.svg",
                    "margin": 0,
                    "padding": 0,
                    "Button.Image:disabled": {"color": 0x88888888},
                }
                ui.Spacer(width=HORIZONTAL_SPACING)
                enabled = bool(model.get_resolved_path())
                edit_widget = ui.Button(
                    style=edit_style,
                    width=12,
                    enabled=enabled,
                    tooltip="Edit Asset" if enabled else "",
                    clicked_fn=lambda value_model=model: widget_kwargs["on_edit_fn"](value_model.get_value()),
                    identifier=f"sdf_edit_asset_{attr_name}" + (f"[{model.index}]" if hasattr(model, "index") else ""),
                )
                edit_widget.enabled = bool(model.get_resolved_path())
                value_widget.model.add_value_changed_fn(
                    lambda m, w=edit_widget: asyncio.ensure_future(edit_name_changed(m, w))
                )

            return value_widget, mixed_overlay

    @classmethod
    async def validate_url(cls, model, layer, on_complete) -> None:
        """Validates model string as URL and calls on_complete with either None for no URL, omni.client.Result.OK or omni.client.Result.ERROR.

        Args:
            model (ui.SimpleStringModel): model to read string from
            layer (Sdf.Layer): Layer handle.
            on_complete (callable): Function to call when completed.
        """
        url = model.get_value_as_string()
        url_path = None
        if url and layer:
            url_path = layer.ComputeAbsolutePath(url)

        if hasattr(model, "get_attributes") and model.get_attributes():
            attr = model.get_attributes()[-1]
            asset = attr.Get() if attr else None
            if isinstance(asset, Sdf.AssetPath):
                url_path = asset.resolvedPath

        if url_path:
            result, _ = await omni.client.stat_async(replace_query(url_path, None))
            return on_complete(result, url_path)
        if url == "":
            return on_complete(omni.client.Result.OK, None)

        return on_complete(None, None)

    @classmethod
    def _assign_asset_path_value(
        cls, stage_weak, model_weak, payload: str, assign_value_fn: Callable[[Any, str], None], frame=None
    ):
        stage_weak = stage_weak()
        if not stage_weak:
            return

        model_weak = model_weak()
        if not model_weak:
            return

        urls = payload.split("\n")
        with omni.kit.undo.group():
            for path in urls:
                path = cls.convert_asset_path(path)
                assign_value_fn(model_weak, path.replace("\\", "/"))

        if frame:
            frame.rebuild()

    @classmethod
    def _assign_asset_resolved_value(
        cls, stage_weak, model_weak, payload: str, assign_value_fn: Callable[[Any, str], None], frame=None
    ):
        model = model_weak()
        if not model:
            return

        urls = payload.split("\n")
        with omni.kit.undo.group():
            for path in urls:
                assign_value_fn(model, cls.convert_asset_path(path).replace("\\", "/"), path)

        if frame:
            frame.rebuild()

    @classmethod
    def _create_path_widget(
        cls, model, stage, attr_name, metadata, prim_paths, additional_label_kwargs, additional_widget_kwargs
    ):
        if "colorSpace" in metadata:
            options = ["auto", "raw", "sRGB"]
            key = "colorSpace"
            custom_data = metadata.get(Sdf.AttributeSpec.CustomDataKey, {})
            default = custom_data.get(f"{key}_{Sdf.AttributeSpec.DefaultValueKey}", options[0])

            colorspace_model = MetadataObjectModel(
                stage,
                [path.AppendProperty(attr_name) for path in prim_paths],
                False,
                metadata,
                key=key,
                default=default,
                options=options,
            )
        else:
            colorspace_model = None

        def build_frame(
            cls,
            model,
            colorspace_model,
            frame,
            stage,
            attr_name,
            metadata,
            prim_paths,
            additional_label_kwargs,
            additional_widget_kwargs,
        ):
            extra_widgets = []

            with ui.VStack():
                with ui.HStack(spacing=HORIZONTAL_SPACING):
                    label = cls.create_label(attr_name, metadata, additional_label_kwargs)

                    widget_kwargs = {"model": model, "name": "models"}

                    if additional_widget_kwargs:
                        widget_kwargs.update(additional_widget_kwargs)

                    value_widget, mixed_overlay = cls.build_path_field(
                        model, stage, attr_name, widget_kwargs, frame, extra_widgets
                    )

                    cls.create_control_state(
                        value_widget=value_widget,
                        mixed_overlay=mixed_overlay,
                        extra_widgets=extra_widgets,
                        **widget_kwargs,
                        label=label,
                    )

                    if colorspace_model:
                        with ui.HStack(width=ui.Percent(12)):
                            cs_widget_kwargs = {"name": "choices", "identifier": f"colorspace_{attr_name}", "width": 50}

                            with ui.ZStack():
                                value_widget = ui.ComboBox(colorspace_model, **cs_widget_kwargs)
                                mixed_overlay = cls.create_mixed_text_overlay(
                                    widget_model=colorspace_model, model=colorspace_model
                                )

                            cls.create_control_state(colorspace_model, value_widget, mixed_overlay)

                if isinstance(model, SdfAssetPathAttributeModel):
                    cls._build_asset_checkpoint_ui(model, frame)

        frame = ui.Frame(width=omni.ui.Percent(100))
        frame.set_build_fn(
            lambda: build_frame(
                cls,
                model,
                colorspace_model,
                frame,
                stage,
                attr_name,
                metadata,
                prim_paths,
                additional_label_kwargs,
                additional_widget_kwargs,
            )
        )

        if colorspace_model:
            # Returns colorspace model also so it could receive updates.
            return [model, colorspace_model]

        return [model]

    @classmethod
    def _create_filepath_for_ui_type(
        cls, stage, attr_name, metadata, prim_paths: List[Sdf.Path], additional_label_kwargs, additional_widget_kwargs
    ):
        model = None
        ui_type = cls._get_attr_value_ui_type(metadata)
        if ui_type == "filePath":
            model_kwargs = get_model_kwargs(additional_widget_kwargs)
            model_cls = get_model_cls(UsdAttributeModel, additional_widget_kwargs, key="no_allowed_tokens_model_cls")
            model = model_cls(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata, **model_kwargs
            )
            widget_kwargs = {"name": "models"}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            cls._create_path_widget(
                model, stage, attr_name, metadata, prim_paths, additional_label_kwargs, widget_kwargs
            )
        return model

    @classmethod
    def _get_layers_with_strongest_value_opinions_on_model(cls, model, stage) -> list[Sdf.Layer]:
        # Older model may not implement get_layers_with_strongest_value_opinions
        if hasattr(model, "get_layers_with_strongest_value_opinions"):
            return model.get_layers_with_strongest_value_opinions()

        # Stage may be a StageAdapter that has no GetEditTarget.
        #
        # Note: when model doesn't implement get_layers_with_strongest_value_opinions:
        # Technically It's not correct to validate against current edit target layer. Relative path can
        # be anchored to wrong layer if it's authored on layer A then edit target changed to later B.
        # But since get_layers_with_strongest_value_opinions function is not provided on the model this is best guess.
        # Here it doesn't attempt to iterate through USD layers and find the strongest spec since the model may not be a USD attribute.
        if hasattr(stage, "GetEditTarget"):
            return [stage.GetEditTarget().GetLayer()]

        # second guess to use RootLayer
        if hasattr(stage, "GetRootLayer") and (root_layer := stage.GetRootLayer()):
            return [root_layer]

        return []

    #################################################
    # Backward compatibility for builder functions that were previous exposed as private
    # Making them public (without prefix underscore) conveys better intention of their usage and avoid the need to add # noqa: PLW0212 for linter
    # No need to add NEW build functions to this alias list.
    #################################################
    _relationship_builder = relationship_builder
    _fallback_builder = fallback_builder
    _floating_point_builder = floating_point_builder
    _integer_builder = integer_builder
    _bool_builder = bool_builder
    _string_builder = string_builder
    _vec2_builder = vec2_builder
    _vec2_per_channel_builder = vec2_per_channel_builder
    _vec3_builder = vec3_builder
    _vec3_per_channel_builder = vec3_per_channel_builder
    _vec4_builder = vec4_builder
    _vec4_per_channel_builder = vec4_per_channel_builder
    _tftoken_builder = tftoken_builder
    _sdf_asset_path_builder = sdf_asset_path_builder
    _sdf_asset_path_array_builder = sdf_asset_path_array_builder
    _create_label = create_label
    _create_text_label = create_text_label
    _generate_tooltip_string = generate_tooltip_string
    _create_attribute_context_menu = create_attribute_context_menu
    _get_attr_value_range = get_attr_value_range
    _get_attr_value_range_kwargs = get_attr_value_range_kwargs
    _get_attr_value_soft_range = get_attr_value_soft_range
    _get_attr_value_soft_range_kwargs = get_attr_value_soft_range_kwargs
    _create_drag_or_slider = create_drag_or_slider
    _create_multi_float_drag_with_labels = create_multi_float_drag_with_labels
    _create_multi_int_drag_with_labels = create_multi_int_drag_with_labels
    _create_multi_drag_with_labels = create_multi_drag_with_labels
    _create_float_drag_per_channel_with_labels_and_control = create_float_drag_per_channel_with_labels_and_control
    _create_int_drag_per_channel_with_labels_and_control = create_int_drag_per_channel_with_labels_and_control
    _create_drag_per_channel_with_labels_and_control = create_drag_per_channel_with_labels_and_control
    _create_color_or_multidrag = create_color_or_multidrag
    _create_bool_per_channel = create_bool_per_channel
    _create_color_or_drag_per_channel = create_color_or_drag_per_channel
    _get_display_name = get_display_name
    _get_type_name = get_type_name
    _create_mixed_text_overlay = create_mixed_text_overlay
    _create_control_state = create_control_state
    _time_code_builder = time_code_builder
    _build_path_field = build_path_field
    _convert_asset_path = convert_asset_path
    _build_prim_path_field = build_prim_path_field
