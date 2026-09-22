# pylint: disable=protected-access
"""Provides a widget for editing transformation attributes of USD prims in the user interface."""


import traceback
from collections import defaultdict
from functools import lru_cache
from typing import Any, Dict, Set

import carb
import omni.ui as ui
import omni.usd
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.property.usd import ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT
from omni.kit.property.usd.usd_attribute_model import GfVecAttributeSingleChannelModel
from omni.kit.property.usd.usd_property_widget import (
    UsdPropertiesWidget,
    get_group_properties_clipboard,
    set_group_properties_clipboard,
)
from omni.kit.widget.settings import get_style
from omni.kit.window.property.templates import GroupHeaderContextMenu, GroupHeaderContextMenuEvent
from pxr import Sdf, Tf, Trace, Usd, UsdGeom

from .transform_builder import TransformWidgets
from .xform_op_utils import _add_trs_op


@lru_cache()
def _get_plus_glyph():
    return ui.get_custom_glyph_code("${glyphs}/menu_context.svg")


class TransformAttributeWidget(UsdPropertiesWidget):
    """A class for managing transformation attributes of USD prims.

    This widget is designed to interact with and manipulate transformation attributes of USD prims within a user interface. It extends the UsdPropertiesWidget to provide a specialized interface for handling transformations, including features such as adding new transform operations, copying, pasting, and resetting transformation values, and toggling between different modes like offset mode.

        Args:
            title (str): The title of the widget.
            collapsed (bool): A flag indicating whether the widget starts in a collapsed state."""

    def __init__(self, title: str, collapsed: bool):
        """Initializer for TransformAttributeWidget."""
        super().__init__(title="Transform", collapsed=False, enable_adapter=True)
        self._transform_widget = TransformWidgets(self)
        self._listener = None
        self._models = defaultdict(list)
        self._offset_mode = False
        self._link_scale = False
        self._any_item_visible = False
        self._bus_sub = None

    def on_new_payload(self, payload):
        """Handles a new payload for the widget.

        Args:
            payload (dict): The new payload to be handled by the widget.

        Returns:
            bool: True if the payload is handled successfully, False otherwise."""
        if not super().on_new_payload(payload):
            return False

        stage = self._payload.get_stage()
        if not stage or not self._payload:
            return False

        for path in self._payload:
            prim = stage.GetPrimAtPath(path)
            if not prim.IsA(UsdGeom.Xformable):
                return False
        return True

    def clean(self):
        """Cleans up the widget and its resources."""
        if self._transform_widget:
            self._transform_widget.clear_widgets()
            self._transform_widget = None
        super().clean()

    def build_items(self):
        """Builds the items for the transform attribute widget."""
        self.reset()

        if len(self._payload) == 0:
            return

        last_prim = self._get_prim(self._payload[-1])
        if not last_prim:
            return

        stage = last_prim.GetStage()
        if not stage:
            return

        self._listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)
        self._bus_sub = get_eventdispatcher().observe_event(
            event_name=ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT, on_event=self._on_bus_event
        )

        # manipulator.prim write "omni:fabric:localMatrix", we need track it here
        attr_names = ["omni:fabric:localMatrix"]
        self.add_listener_adapters(attr_names)

        # for prim_path in self._payload:
        if self._payload is not None:
            self._models = None
            if self._offset_mode:
                self._transform_widget.build_transform_offset_frame(self._payload, self._collapsable_frame, stage)
            else:
                self._models, all_empty_xformop = self._transform_widget.build_transform_frame(
                    self._payload, self._collapsable_frame, stage
                )
                if len(self._transform_widget.get_widgets()) > 0:
                    self._any_item_visible = True
                else:
                    # OM-51604 When no xformOpOrder element nor xformOp attributes, a special widget and button for it
                    label_style = {"font_size": 18}
                    with ui.VStack(spacing=8):
                        if len(self._payload) == 1:
                            ui.Label("This prim has no transforms", style=label_style, alignment=ui.Alignment.CENTER)
                            ui.Button(f"{_get_plus_glyph()} Add Transforms", clicked_fn=self._on_add_transform)
                        elif all_empty_xformop is False:
                            ui.Label(
                                "The selected prims have no common transforms to display",
                                style=label_style,
                                alignment=ui.Alignment.CENTER,
                            )
                        else:
                            ui.Label(
                                "None of the selected prims has transforms",
                                style=label_style,
                                alignment=ui.Alignment.CENTER,
                            )
                            ui.Button(f"{_get_plus_glyph()} Add Transforms", clicked_fn=self._on_add_transform)

            if self._models is None:
                self._models = defaultdict(list)

        # Register the Copy/Paste/Reset All content context menu
        self._build_header_context_menu("Tranform")

    @Trace.TraceFunction
    def _on_usd_changed(self, notice, stage):
        if stage != self._payload.get_stage() and isinstance(stage, Usd.Stage):
            return

        for path in notice.GetChangedInfoOnlyPaths():
            # if anyone changes the xformOpOrder of the current prim rebuild the collapsable frame
            # OMPE-33460: it is possible to get path like "/" from GetChangedInfoOnlyPaths(),
            # and an empty path will be returned by GetPrimPath(). Passing empty path to Sdf.Path()
            # will result in "Ill-formed SdfPath" warning message. So empty path is filtered here.
            _path = str(path.GetPrimPath())
            if not _path:
                continue
            if Sdf.Path(_path) in self._payload:
                attr_name = path.name
                if attr_name == "xformOpOrder":
                    super().request_rebuild()
                    return

                if attr_name == "omni:fabric:localMatrix":
                    matrix = stage.GetAttributeAtPath(path).Get()
                    self._transform_widget.update_from_matrix(matrix)

        super()._on_usd_changed(notice, stage)

    def _build_frame_header(self, collapsed, text: str, group_id: str = None):
        """Custom header for CollapsableFrame"""
        if group_id is None:
            group_id = text

        if collapsed:
            alignment = ui.Alignment.RIGHT_CENTER
            width = 5
            height = 7
        else:
            alignment = ui.Alignment.CENTER_BOTTOM
            width = 7
            height = 5

        header_stack = ui.HStack(spacing=8)
        with header_stack:
            with ui.VStack(width=0):
                ui.Spacer()
                ui.Triangle(
                    style_type_name_override="CollapsableFrame.Header", width=width, height=height, alignment=alignment
                )
                ui.Spacer()
            ui.Label(text, style_type_name_override="CollapsableFrame.Header", width=ui.Fraction(1))

            button_style = {
                "Button.Image": {
                    "color": 0xFFFFFFFF,
                    "alignment": ui.Alignment.CENTER,
                },
            }

            if self._offset_mode:
                default_style = get_style()
                label_style = default_style.get("CollapsableFrame.Header", {})
                label_style.update({"color": 0xFFFFC734})
                ui.Label("Offset", style=label_style, width=ui.Fraction(1))
                ui.Spacer(width=ui.Fraction(5))
                button_style["Button.Image"]["image_url"] = "${glyphs}/offset_active_dark.svg"
            else:
                ui.Spacer(width=ui.Fraction(6))
                button_style["Button.Image"]["image_url"] = "${glyphs}/offset_dark.svg"

            with ui.ZStack(content_clipping=True, width=25, height=25):
                ui.Button(
                    "",
                    style=button_style,
                    clicked_fn=self._toggle_offset_mode,
                    identifier="offset_mode_toggle",
                    tooltip="Toggle offset mode",
                )

        def show_attribute_context_menu(b):
            if b != 1:
                return

            event = GroupHeaderContextMenuEvent(group_id=group_id, payload=[])
            GroupHeaderContextMenu.on_mouse_event(event)

        header_stack.set_mouse_pressed_fn(lambda x, y, b, _: show_attribute_context_menu(b))

    def _toggle_offset_mode(self):
        self._offset_mode = not self._offset_mode
        self.request_rebuild()

    def toggle_link_scale(self):
        self._link_scale = not self._link_scale
        self.request_rebuild()

    def _on_add_transform(self):
        _add_trs_op(self._payload)
        self.request_rebuild()

    def _build_header_context_menu(self, group_id: str):

        # ------Copy All Context Menu--------
        def can_copy(objects):
            # Only support single selection copy
            return len(self._payload) == 1

        def on_copy(objects):
            prim = self._get_prim(self._payload[-1])
            xform_op_order_attr = prim.GetAttribute("xformOpOrder")
            if not xform_op_order_attr:
                return
            xform_op_order = xform_op_order_attr.Get()

            visited_models = set()

            properties_to_copy: Dict[Sdf.Path, Any] = {}
            for models in self._models.values():
                for model in models:
                    if model in visited_models:
                        continue

                    visited_models.add(model)

                    # Skip "Mixed"
                    if model.is_ambiguous():
                        continue

                    paths = model.get_property_paths()
                    if paths:
                        # No need to copy single channel model. Each vector attribute also has a GfVecAttributeModel
                        if isinstance(model, GfVecAttributeSingleChannelModel):
                            continue
                        properties_to_copy[paths[-1]] = model.get_value()
            if properties_to_copy:
                properties_to_copy[Sdf.Path(xform_op_order_attr.GetName())] = xform_op_order
                set_group_properties_clipboard(properties_to_copy)

        menu = {
            "name": "Copy All Property Values in Transform",
            "show_fn": lambda objects: True,
            "enabled_fn": can_copy,
            "onclick_fn": on_copy,
        }

        self._group_menu_entries.append(self._register_header_context_menu_entry(menu, "Transform"))

        # ------Paste All Context Menu--------
        def can_paste(objects):
            # Only support single selection copy
            properties_to_paste = get_group_properties_clipboard()
            if not properties_to_paste:
                return False
            # Can't paste if the copied content doesn't have xformOpOrder key
            source_xform_op_order_value = properties_to_paste[Sdf.Path("xformOpOrder")]
            if source_xform_op_order_value is None:
                return False

            prim = self._get_prim(self._payload[-1])
            if not prim:
                return False
            xform_op_order_attr = prim.GetAttribute("xformOpOrder")
            # Can't paste if the target prim doesn't have xformOpOrder
            if not xform_op_order_attr:
                return False
            target_xform_op_order_value = xform_op_order_attr.Get()
            # Can't paste if the copied content and target prim's xformOpOrder doesn't match
            if not target_xform_op_order_value or source_xform_op_order_value != target_xform_op_order_value:
                return False
            return True

        def on_paste(objects):
            properties_to_copy = get_group_properties_clipboard()
            if not properties_to_copy:
                return

            unique_model_prim_paths: Set[Sdf.Path] = set()
            for prop_path in self._models:
                unique_model_prim_paths.add(prop_path.GetPrimPath())

            with omni.kit.undo.group():
                try:
                    for path, value in properties_to_copy.items():
                        for prim_path in unique_model_prim_paths:
                            paste_to_model_path = prim_path.AppendProperty(path.name)
                            models = self._models.get(paste_to_model_path, [])
                            for model in models:
                                # No need to paste single channel model. Each vector attribute also has a GfVecAttributeModel
                                if isinstance(model, GfVecAttributeSingleChannelModel):
                                    continue
                                model.set_value(value)
                except Exception:  # pylint: disable=broad-exception-caught
                    carb.log_error(f"on_paste error:{traceback.format_exc()}")

        menu = {
            "name": "Paste All Property Values to Transform",
            "show_fn": lambda objects: True,
            "enabled_fn": can_paste,
            "onclick_fn": on_paste,
        }
        self._group_menu_entries.append(self._register_header_context_menu_entry(menu, "Transform"))

        # ------Reset All Context Menu------
        def can_reset(objects):
            for models in self._models.values():
                for model in models:
                    if model.is_different_from_default():
                        return True
            return False

        def on_reset(objects):
            for models in self._models.values():
                for model in models:
                    model.set_default()

        menu = {
            "name": "Reset All Property Values in Transform",
            "show_fn": lambda objects: True,
            "enabled_fn": can_reset,
            "onclick_fn": on_reset,
        }

        self._group_menu_entries.append(self._register_header_context_menu_entry(menu, "Transform"))

    _toggle_link_scale = toggle_link_scale
