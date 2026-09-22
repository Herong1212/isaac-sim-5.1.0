# pylint: disable=unnecessary-dunder-call
"""A module for building and managing transform widgets for USD primitives in Omniverse Kit applications.

This module provides functionality to create user interface elements for manipulating the transform properties (translation, rotation, scale) of USD primitives. It supports operations such as adding, multiplying, and resetting transformations directly from the UI, and handles both single and multiple selection of primitives.
"""


import asyncio
import copy
import functools
from collections import defaultdict
from enum import Enum
from typing import Any, List

import carb
import carb.settings
import omni.ext
import omni.kit.commands
import omni.timeline
import omni.ui as ui
import omni.usd
import usdrt
from omni.hydra.scene_api import get_wgs84_coords
from omni.kit.property.usd.usd_attribute_model import (
    GfMatrixAttributeModel,
    GfQuatAttributeModel,
    GfQuatEulerAttributeModel,
    GfVecAttributeModel,
    GfVecAttributeSingleChannelModel,
    UsdAttributeModel,
    UsdBase,
)
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.widget.highlight_label import HighlightLabel
from pxr import Gf, Sdf, Tf, Usd, UsdGeom

from . import xform_op_utils
from .transform_model import VecAttributeModel

# Settings constants from omni.kit.window.toolbar
TRANSFORM_OP_SETTING = "/app/transform/operation"
TRANSFORM_OP_MOVE = "move"
TRANSFORM_OP_ROTATE = "rotate"
TRANSFORM_OP_SCALE = "scale"
TRANSFORM_MOVE_MODE_SETTING = "/app/transform/moveMode"
TRANSFORM_ROTATE_MODE_SETTING = "/app/transform/rotateMode"
TRANSFORM_MODE_GLOBAL = "global"
TRANSFORM_MODE_LOCAL = "local"

LABEL_PADDING = 128
ICON_PATH = ""
quat_view_button_style = {
    "Button:hovered": {"background_color": 0xFF575757},
    "Button": {"background_color": 0xFF333333, "padding": 0, "stack_direction": ui.Direction.RIGHT_TO_LEFT},
    "Button.Label": {"color": 0xFF9E9E9E, "alignment": ui.Alignment.LEFT_CENTER},
    "Button.Tooltip": {"color": 0xFF9E9E9E},
    "Button.Image": {"color": 0xFFFFCC99, "alignment": ui.Alignment.CENTER},
}
euler_view_button_style = {
    "Button:hovered": {"background_color": 0xFF23211F},
    "Button": {"background_color": 0xFF23211F, "padding": 0, "stack_direction": ui.Direction.RIGHT_TO_LEFT},
    "Button.Label": {"color": 0xFFA07D4F, "alignment": ui.Alignment.LEFT_CENTER},
    "Button.Tooltip": {"color": 0xFF9E9E9E},
    "Button.Image": {"color": 0xFFFFCC99, "alignment": ui.Alignment.CENTER},
}


# Those modified version of models that supports
# display manipulaotr fabric value without usd value changing
class FabricGfVecAttributeSingleChannelModel(GfVecAttributeSingleChannelModel):
    """A model representing a single channel of a GfVec attribute for fabric manipulation.

    This model extends the GfVecAttributeSingleChannelModel to support the representation
    and manipulation of fabric values without changing the underlying USD values. It provides
    methods to get and set the value of the attribute as various data types (string, float, int, bool),
    and to set a fabric-specific value.

        Args:
            stage (Usd.Stage): The stage containing the attribute.
            attribute_paths (List[Sdf.Path]): A list of paths to the attributes.
            channel_index (int): The index of the channel within the GfVec attribute.
            self_refresh (bool): Whether the model should refresh itself.
            metadata (dict): Metadata associated with the attribute.
            change_on_edit_end (bool): Whether to change the value only at the end of an edit.

        Keyword Args:
            Additional keyword arguments are supported but not listed explicitly."""

    def __init__(
        self,
        stage,
        attribute_paths: List[Sdf.Path],
        channel_index: int,
        self_refresh: bool,
        metadata: dict,
        change_on_edit_end=True,
        **kwargs,
    ):
        """Initializes the FabricGfVecAttributeSingleChannelModel instance."""
        self._fabric_value = None
        super().__init__(stage, attribute_paths, channel_index, self_refresh, metadata, change_on_edit_end, **kwargs)

    def get_value_as_string(self, **kwargs) -> str:
        """Returns the value of the attribute as a string.

        Keyword Args:
            precision (int): The numeric precision for formatting the string."""
        if self._fabric_value is not None:
            return str(self._fabric_value)
        return super().get_value_as_string(**kwargs)

    def get_value_as_float(self) -> float:
        """Returns the value of the attribute as a float."""
        if self._fabric_value is not None:
            return float(self._fabric_value)
        return super().get_value_as_float()

    def get_value_as_bool(self) -> bool:
        """Returns the value of the attribute as a boolean."""
        if self._fabric_value is not None:
            return bool(self._fabric_value)
        return super().get_value_as_bool()

    def get_value_as_int(self) -> int:
        """Returns the value of the attribute as an integer."""
        if self._fabric_value is not None:
            return int(self._fabric_value)
        return super().get_value_as_int()

    def set_value(self, value):
        """Sets the value of the attribute.

        Args:
            value (float): The new value to set."""
        self._fabric_value = None
        super().set_value(value)

    def set_fabric_value(self, value):
        """Sets the fabric value of the attribute.

        Args:
            value (float): The new fabric value to set."""
        self._fabric_value = value
        self._value_changed()

    def _on_dirty(self):
        self._fabric_value = None
        super()._on_dirty()


class FabricGfMatrixAttributeModel(GfMatrixAttributeModel):
    """A class for handling matrix attribute models in the Fabric engine.

    This class provides functionality for manipulating GfMatrix-based attributes within the Fabric engine. It extends the GfMatrixAttributeModel, allowing for the display and manipulation of matrix values without altering the USD values directly.

        Args:
            stage: The Usd.Stage on which the matrix attributes exist.
            attribute_paths (List[Sdf.Path]): A list of paths to the matrix attributes.
            comp_count (int): The number of components in the matrix (e.g., 4 for a 4x4 matrix).
            tf_type (Tf.Type): The type of the transformation represented by the matrix.
            self_refresh (bool): Indicates whether the model should refresh itself automatically.
            metadata (dict): A dictionary containing metadata for the matrix attributes."""

    def __init__(
        self,
        stage,
        attribute_paths: List[Sdf.Path],
        comp_count: int,
        tf_type: Tf.Type,
        self_refresh: bool,
        metadata: dict,
    ):
        """Initializes a FabricGfMatrixAttributeModel instance."""
        self._fabric_value = False
        super().__init__(stage, attribute_paths, comp_count, tf_type, self_refresh, metadata)

    def get_item_children(self, item):
        """Gets children items of a specific item.

        Args:
            item (Item): The item to retrieve children from."""
        if not self._fabric_value:
            self._update_value()
        return self._items

    def set_value(self, *args):
        """Sets the value for the matrix attribute.

        Args:
            value (float): The new value to set for the matrix attribute."""
        self._fabric_value = False
        super().set_value(*args)

    def set_fabric_value(self, value):
        """Sets the fabric value for the matrix attribute.

        Args:
            value (float): The new fabric value to set for the matrix attribute."""
        if isinstance(value, usdrt.Gf.Matrix4d):
            self._fabric_value = True
            for i, item in enumerate(self._items):
                item.model.set_value(value[i // self._comp_count][i % self._comp_count])

    def _on_dirty(self):
        self._fabric_value = False
        super()._on_dirty()


class FabricGfQuatAttributeModel(GfQuatAttributeModel):
    """A class representing a quaternion attribute for fabric with USD support.

    This model allows for manipulation of quaternion-based transformations in a fabric context while maintaining compatibility with USD attributes.

        Args:
            stage (Usd.Stage): The USD stage to which the attribute belongs.
            attribute_paths (List[Sdf.Path]): The Sdf.Paths to the quaternion attributes.
            tf_type (Tf.Type): The type of the transformation.
            self_refresh (bool): Indicates whether the model should automatically refresh.
            metadata (dict): A dictionary containing metadata for the attribute."""

    def __init__(self, stage, attribute_paths: List[Sdf.Path], tf_type: Tf.Type, self_refresh: bool, metadata: dict):
        """Initializes the FabricGfQuatAttributeModel instance."""
        self._fabric_value = False
        super().__init__(stage, attribute_paths, tf_type, self_refresh, metadata)

    def set_value(self, *args):
        """Sets the attribute value and marks the internal fabric value as invalid.

        Args:
            value (Any): The new value to set for the attribute."""
        self._fabric_value = False
        super().set_value(*args)

    def set_fabric_value(self, value):
        """Sets the internal fabric value without changing the USD attribute.

        Args:
            value (Any): The new internal fabric value to set."""
        if isinstance(value, usdrt.Gf.Rotation):
            self._fabric_value = True
            quat = value.GetQuat()
            for i, item in enumerate(self._items):
                item.model.set_value(quat[(i + 3) % 4])  # reorder w to first item

    def _on_dirty(self):
        self._fabric_value = False
        super()._on_dirty()


class FabricGfQuatEulerAttributeModel(GfQuatEulerAttributeModel):
    """A model for representing quaternion or euler attributes for the Fabric engine.

    This model facilitates the manipulation of rotation attributes in both quaternion (quat) or euler angles. It allows
    for setting and getting rotation values, and converting between different rotation representations as required by
    the Fabric engine.

        Args:
            stage (Usd.Stage): The stage on which the attribute exists.
            attribute_paths (List[Sdf.Path]): A list of paths to the attributes.
            tf_type (Tf.Type): The transformation type, either a quaternion or euler rotation.
            self_refresh (bool): A flag indicating whether the model should refresh itself.
            metadata (dict): A dictionary containing metadata for the attribute."""

    def __init__(self, stage, attribute_paths: List[Sdf.Path], tf_type: Tf.Type, self_refresh: bool, metadata: dict):
        """Initializes a FabricGfQuatEulerAttributeModel instance."""
        self._fabric_value = False
        super().__init__(stage, attribute_paths, tf_type, self_refresh, metadata)

    def set_value(self, value):
        """Sets the value of the attribute.

        Args:
            value: The value to set."""
        self._fabric_value = False
        super().set_value(value)

    def set_fabric_value(self, value):
        """Sets the fabric value of the attribute.

        Args:
            value: The fabric value to set."""
        if isinstance(value, usdrt.Gf.Rotation):
            self._fabric_value = True
            angles = value.Decompose(usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis())
            for i, item in enumerate(self._items):
                item.model.set_value(angles[i])

    def _on_dirty(self):
        self._fabric_value = False
        super()._on_dirty()


class USDXformOpWidget:
    """A widget for manipulating USD transform operations on selected primitives.

    This widget includes UI components for translating, rotating, scaling, and applying other
    transform operations such as orient and transform to the selected USD primitives. It supports
    interactions such as mouse dragging and direct text input for precise control over the
    transform operations.

        Args:
            prim_paths (List[Sdf.Path]): Paths to the USD primitives being manipulated.
            collapsable_frame (ui.Frame): The UI frame that can be collapsed or expanded.
            stage (Usd.Stage): The USD stage where the primitives reside.
            attr_path (Sdf.Path): Path to the USD attribute representing the transform operation.
            op_name (str): Name of the transform operation (e.g., 'xformOp:translate').
            is_valid_op (bool): Indicates whether the operation is valid and should be processed.
            op_order_attr_path (Sdf.Path): Path to the 'xformOpOrder' attribute if it exists.
            op_order_index (int): Index of the operation within the 'xformOpOrder' attribute.
            label_kwargs (dict, optional): Additional keyword arguments for UI label customization."""

    def __init__(
        self,
        prim_paths,
        collapsable_frame,
        stage,
        attr_path,
        op_name,
        is_valid_op,
        op_order_attr_path,
        op_order_index,
        label_kwargs=None,
    ):
        """Initializer for the USDXformOpWidget class."""
        self._prim_paths = prim_paths
        self._collapsable_frame = collapsable_frame
        self._stage = stage
        self._attr_path = attr_path
        self._op_name = op_name
        self._is_valid_op = is_valid_op
        self._op_order_attr_path = op_order_attr_path
        self._op_order_index = op_order_index
        self._model = []
        self._right_click_menu = None
        self._label_kwargs = label_kwargs if label_kwargs is not None else {}
        self._settings = carb.settings.get_settings()
        self._quat_view = None
        self._euler_view = None
        self._display_orient_as_rotate = True
        self.rebuild()

    def __del__(self):
        self._prim_paths = None
        self._collapsable_frame = None
        self._stage = None
        self._attr_path = None
        self._op_name = None
        self._is_valid_op = False
        self._op_order_attr_path = None
        self._op_order_index = -1
        if self._model is not None:
            if isinstance(self._model, list):
                for model in self._model:
                    model.clean()
            else:
                self._model.clean()  # pylint: disable=no-member
        self._model = None
        self._right_click_menu = None

    def rebuild(self):
        pass

    def update_fabric_value_only(self, vec_value):
        """Updates the widget with a new value without affecting the USD attribute.

        Args:
            vec_value (Gf.Vec3d): The new vector value to be used for the update."""

        def set_fabric_value(model, vec_value):
            if isinstance(model, FabricGfVecAttributeSingleChannelModel):
                # pylint: disable=protected-access
                model.set_fabric_value(vec_value[model._channel_index])

        if isinstance(self._model, list):
            for model in self._model:
                set_fabric_value(model, vec_value)
        else:
            set_fabric_value(self._model, vec_value)

    def _create_inverse_widgets(self):
        # Not create inverse widgets for non-op attribute.
        if self._op_name is None:
            return
        is_inverse_op = False if self._op_name is None else xform_op_utils.is_inverse_op(self._op_name)
        if is_inverse_op:
            ui.Label("¯¹")

    def _inverse_op(self):
        if self._op_order_attr_path is not None and self._op_order_index > -1:
            order_attr = self._stage.GetObjectAtPath(self._op_order_attr_path)
            if order_attr:
                with Sdf.ChangeBlock():
                    op_order = order_attr.Get()
                    if self._op_order_index < len(op_order):
                        op_name = op_order.__getitem__(self._op_order_index)
                        if op_name == self._op_name:
                            is_inverse_op = xform_op_utils.is_inverse_op(op_name)
                            inverse_op_name = xform_op_utils.get_inverse_op_Name(op_name, not is_inverse_op)
                            self._op_name = inverse_op_name
                            op_order.__setitem__(self._op_order_index, inverse_op_name)
                            order_attr.Set(op_order)
                            # self._window().rebuild_window()
                            self._collapsable_frame.rebuild()

    def _delete_op_only(self):
        if self._op_order_attr_path is not None and self._op_order_index > -1:
            omni.kit.commands.execute(
                "RemoveXformOp",
                op_order_attr_path=self._op_order_attr_path,
                op_name=self._op_name,
                op_order_index=self._op_order_index,
            )

    def _delete_op_and_attribute(self):
        if self._op_order_attr_path is not None and self._op_order_index > -1:
            omni.kit.commands.execute(
                "RemoveXformOpAndAttrbute",
                op_order_attr_path=self._op_order_attr_path,
                op_name=self._op_name,
                op_order_index=self._op_order_index,
            )
            omni.kit.window.property.get_window().request_rebuild()

    def _delete_non_op_attribute(self):
        # pylint: disable=protected-access

        if self._stage is not None and self._op_name is None and self._attr_path is not None:
            omni.kit.commands.execute("RemoveProperty", prop_path=self._attr_path.pathString)
            omni.kit.window.property.get_window().request_rebuild()

    def _add_non_op_attribute_to_op(self):
        if self._stage is not None and self._op_name is None and self._attr_path is not None:
            omni.kit.commands.execute("EnableXformOp", op_attr_path=self._attr_path)

    # This is to toggle the value widgets for quaternion or euler angle
    def on_display_orient_as_rotate(self):
        self._display_orient_as_rotate = not self._display_orient_as_rotate
        if self._settings:
            self._settings.set("/persistent/app/uiSettings/DisplayOrientAsRotate", self._display_orient_as_rotate)
        if self._display_orient_as_rotate is True:
            self._quat_view.visible = False
            self._euler_view.visible = True
        else:
            self._quat_view.visible = True
            self._euler_view.visible = False

    # The orient label(button) has a different style for two modes
    def toggle_orient_button_style(self, button):
        # About to switch to raw mode
        if self._display_orient_as_rotate is True:
            button.set_style(euler_view_button_style)
        else:
            button.set_style(quat_view_button_style)

    def _on_orient_button_clicked(self, mouse_button, widget):
        if mouse_button != 0:
            return
        self.on_display_orient_as_rotate()
        self.toggle_orient_button_style(widget)

    def _show_right_click_menu(self, button):
        if button != 1:
            return

        if self._right_click_menu is None:
            self._right_click_menu = ui.Menu("Right Menu")
        self._right_click_menu.clear()
        with self._right_click_menu:
            # ResetXformStack
            if xform_op_utils.is_reset_xform_stack_op(self._op_name):
                text = "Disable" if self._is_valid_op else "Disable Invalid Op"
                ui.MenuItem(text, triggered_fn=lambda: self._delete_op_only())
            # valid/invalid Op
            elif self._op_name is not None and self._attr_path is not None:
                # ui.MenuItem("Inverse", triggered_fn=lambda: self._inverse_op())
                text_op_only = "Disable" if self._is_valid_op else "Disable Invalid Op"
                text_op_attr = "Delete" if self._is_valid_op else "Delete Invalid Op"
                ui.MenuItem(text_op_only, triggered_fn=lambda: self._delete_op_only())
                ui.MenuItem(text_op_attr, triggered_fn=lambda: self._delete_op_and_attribute())
            # non-op attribute
            elif self._op_name is None and self._attr_path is not None:
                ui.MenuItem("Delete", triggered_fn=lambda: self._delete_non_op_attribute())
                ui.MenuItem("Enable", triggered_fn=lambda: self._add_non_op_attribute_to_op())
            # no-attribute op
            elif self._op_name is not None and self._attr_path is None:
                ui.MenuItem("Disable Invalid Op", triggered_fn=lambda: self._delete_op_only())
        self._right_click_menu.show()

    def _create_multi_float_drag_matrix_with_labels(self, model, comp_count, _min, _max, step, labels):  #
        rect_width = 13
        spacing = 4
        with ui.ZStack():
            with ui.HStack():
                ui.Spacer(width=rect_width)
                value_widget = ui.MultiFloatDragField(
                    model, name="multivalue", min=_min, max=_max, step=step, h_spacing=rect_width + spacing, v_spacing=2
                )
            with ui.HStack():
                for i in range(comp_count):
                    if i != 0:
                        ui.Spacer(width=spacing)
                    label = labels[i]
                    with ui.ZStack(width=rect_width + 1):
                        ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                        ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                    ui.Spacer()
            mixed_overlay = []
            with ui.VStack():
                for _l1 in range(comp_count):
                    with ui.HStack():
                        for _l2 in range(comp_count):
                            ui.Spacer(width=rect_width)
                            mixed_overlay.append(UsdPropertiesWidgetBuilder.create_mixed_text_overlay())
        UsdPropertiesWidgetBuilder.create_control_state(model, value_widget, mixed_overlay)

    _toggle_orient_button_style = toggle_orient_button_style
    _on_display_orient_as_rotate = on_display_orient_as_rotate


class TransformWatchModel(ui.AbstractValueModel):
    """A class for monitoring changes to a USD transform component.

    This model tracks changes to a specific component of a transform in USD, updating its value
    as the transform changes. It is typically used for displaying transform component values in a UI.

        Args:
            component_index (int): The index of the transform component to monitor.
            stage (Usd.Stage): The USD stage where the monitored transform is located."""

    def __init__(self, component_index, stage):
        """Initializes the TransformWatchModel with a component index and USD stage."""
        super().__init__()
        self._usd_context = omni.usd.get_context()
        self._component_index = component_index
        self._value = 0.0
        self._selection = self._usd_context.get_selection()
        self._prim_paths = self._selection.get_selected_prim_paths()
        self._on_usd_changed()
        usd_watcher = omni.usd.get_watcher()
        self._subscription = usd_watcher.subscribe_to_change_info_path(self._prim_paths[0], self._on_usd_changed)

    def clean(self):
        """Cleans up resources and unsubscribes from USD changes."""
        self._usd_context = None
        self._selection = None
        self._prim_paths = None
        self._subscription.unsubscribe()
        self._subscription = None

    def _on_usd_changed(self, path=None):
        wgs_coords = get_wgs84_coords("", self._prim_paths[0])
        self.set_value(wgs_coords[self._component_index])

    def get_value_as_float(self) -> float:
        """Returns the current value as a float."""
        return self._value or 0.0

    def get_value_as_string(self) -> str:
        """Returns the current value as a string."""
        if self._value is None:
            return ""

        # General format. This prints the number as a fixed-point
        # number, unless the number is too large, in which case it
        # switches to 'e' exponent notation.
        return "{0:g}".format(self._value)

    def set_value(self, new_value: Any) -> None:
        """Sets the value of the model.

        Args:
            new_value (Any): The new value to be set."""
        try:
            value = float(new_value)
        except ValueError:
            value = 0.0
        if value != self._value:
            self._value = value
            self._value_changed()


class USDXformOpTranslateWidget(USDXformOpWidget):
    """A widget for translating selected USD primitives.

    This widget allows users to manipulate the translation of selected USD primitives in the scene. It provides an interface for editing the translation values directly or applying incremental changes.

        Args:
            prim_paths (List[Sdf.Path]): The paths to the USD primitives being manipulated.
            collapsable_frame (ui.Frame): The UI frame that should be collapsible.
            stage (Usd.Stage): The USD stage where the primitives exist.
            attr_path (Sdf.Path): The path to the translation attribute.
            op_name (str): The name of the translate operation.
            is_valid_op (bool): Indicates if the operation is valid.
            op_order_attr_path (Sdf.Path): The path to the attribute that defines the order of operations.
            op_order_index (int): The index of the operation in the operations order list.
            label_kwargs (Optional[dict]): Additional keyword arguments for custom label options."""

    @classmethod
    def display_name(cls, attr_name: str) -> str:
        """Generates a label for the translate operation based on the attribute name.

        Args:
            attr_name (str): Name of the attribute associated with the translate operation.

        Returns:
            str: A label for the translate operation."""
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        label_name = "Translate"
        if suffix:
            label_name = label_name + ":" + suffix
        return label_name

    def rebuild(self):
        """Reconstructs the widget for the translate operation.

        This method builds the widget interface for the translate operation of a USD primitive. It checks if the attribute name starts with 'xformOp:translate' and, if not, logs a warning. The method also handles inverse operations and suffixes, and creates UI components based on the attribute's metadata.
        """
        attr = self._stage.GetObjectAtPath(self._attr_path)
        attr_name = attr.GetName()
        if not attr_name.startswith("xformOp:translate"):
            carb.log_warn(f"Object {self._attr_path} is not an xformOp:translate attribute ")
            return
        is_inverse_op = False if self._op_name is None else xform_op_utils.is_inverse_op(self._op_name)
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        if is_inverse_op and suffix == "pivot":
            return
        label_name = self.display_name(attr_name)
        # label_tooltip = get_attribute_type_tooltip(attr) + " " + attr.GetName()
        metadata = attr.GetAllMetadata()
        type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey))
        label_tooltip = UsdPropertiesWidgetBuilder.generate_tooltip_string(attr.GetName(), metadata)

        self._model = []
        for i in range(3):
            self._model.append(
                FabricGfVecAttributeSingleChannelModel(
                    self._stage,
                    [path.AppendProperty(attr_name) for path in self._prim_paths],
                    i,
                    False,
                    metadata,
                    change_on_edit_end=True,
                )
            )
        vec_model = GfVecAttributeModel(
            self._stage,
            [path.AppendProperty(attr_name) for path in self._prim_paths],
            3,
            type_name.type,
            False,
            metadata,
        )

        if len(self._prim_paths) == 1:
            setattr(vec_model, "transform_widget", self)  # noqa: B010
        label = None
        with ui.HStack():
            with ui.HStack(width=LABEL_PADDING):
                if len(self._prim_paths) == 1:
                    with ui.ZStack():
                        label_tooltip = label_tooltip + "\nRight click it to disable or delete it."
                        # This rectangle is act as a hover hint helper
                        ui.Rectangle(
                            style={":hovered": {"background_color": 0xFF444444}, "background_color": 0xFF333333},
                            mouse_pressed_fn=(lambda x, y, b, m: self._show_right_click_menu(b)),
                        )
                        label = HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                else:
                    label = HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                ui.Spacer(width=2)
                self._create_inverse_widgets()
            with ui.HStack():
                range_min, range_max = UsdPropertiesWidgetBuilder.get_attr_value_range(metadata)
                kwargs = {"min": range_min, "max": range_max, "step": 1.0}
                UsdPropertiesWidgetBuilder.create_float_drag_per_channel_with_labels_and_control(
                    models=self._model,
                    metadata=metadata,
                    labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                    kwargs=kwargs,
                )

                # The vec_model is useful when we set the key for all three components together
                self._model.append(vec_model)
                UsdPropertiesWidgetBuilder.create_attribute_context_menu(label, vec_model)

        wgs_coord = get_wgs84_coords("", self._prim_paths[0].pathString)
        if len(wgs_coord) > 0:
            with ui.HStack():
                with ui.HStack(width=LABEL_PADDING):
                    label = ui.Label("WGS84", name="title", tooltip=label_tooltip)
                    ui.Spacer(width=2)
            with ui.HStack():
                with ui.VStack():
                    all_axis = ["Lat", "Lon", "Alt"]
                    colors = {"Lat": 0xFF5555AA, "Lon": 0xFF76A371, "Alt": 0xFFA07D4F}
                    component_index = 0
                    for axis in all_axis:
                        with ui.HStack():
                            with ui.HStack(width=LABEL_PADDING):
                                label = ui.Label("", name="title", tooltip=label_tooltip)
                            with ui.ZStack(width=20):
                                ui.Rectangle(
                                    width=20,
                                    height=20,
                                    style={
                                        "background_color": colors[axis],
                                        "border_radius": 3,
                                        "corner_flag": ui.CornerFlag.LEFT,
                                    },
                                )
                                ui.Label(axis, name="wgs84_label", alignment=ui.Alignment.CENTER)
                            # NOTE: Updating the WGS84 values does not update the transform translation,
                            # so make the input fields read-only for now.
                            # See https://nvidia-omniverse.atlassian.net/browse/OM-64348
                            ui.FloatDrag(TransformWatchModel(component_index, self._stage), enabled=False)
                            component_index = component_index + 1
        super().rebuild()


class USDXformOpRotateWidget(USDXformOpWidget):
    """A widget for manipulating rotation of USD primitives.

    This widget allows users to interactively adjust the rotation of selected USD primitives. It supports different rotation orders (e.g., XYZ, XZY, YXZ, etc.) and can represent rotations in both quaternion and euler angles. Users can switch between quaternion and euler views, and also change the rotation order dynamically.

        Args:
            prim_paths (List[Sdf.Path]): The paths of the selected USD primitives.
            collapsable_frame: The collapsable frame containing the widget.
            stage (Usd.Stage): The USD stage that the primitives belong to.
            attr_path (Sdf.Path): The path to the rotation attribute.
            op_name (str): The name of the rotation operation.
            is_valid_op (bool): Indicates if the operation is valid.
            op_order_attr_path (Sdf.Path): The path to the attribute that specifies the operation order.
            op_order_index (int): The index of the operation in the operation order.
            label_kwargs (dict, optional): Additional keyword arguments for label customization."""

    ROTATE_AXIS_ORDER_MAP = {
        "xformOp:rotateXYZ": ["X", "Y", "Z"],
        "xformOp:rotateXZY": ["X", "Z", "Y"],
        "xformOp:rotateYXZ": ["Y", "X", "Z"],
        "xformOp:rotateYZX": ["Y", "Z", "X"],
        "xformOp:rotateZXY": ["Z", "X", "Y"],
        "xformOp:rotateZYX": ["Z", "Y", "X"],
    }
    """Maps rotate operation names to axis order sequences.

Type:
    dict
"""

    ROTATE_AXIS_ORDER_INDEX = {
        "xformOp:rotateXYZ": [0, 1, 2],
        "xformOp:rotateXZY": [0, 2, 1],
        "xformOp:rotateYXZ": [1, 0, 2],
        "xformOp:rotateYZX": [1, 2, 0],
        "xformOp:rotateZXY": [2, 0, 1],
        "xformOp:rotateZYX": [2, 1, 0],
    }
    """Maps rotate operation names to axis order indices.

Type:
    dict
"""

    ROTATE_ORDERS = ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"]
    """List of rotation orders.

Type:
    list
"""

    @classmethod
    def display_name(cls, attr_name: str) -> str:
        """Generates a display name for the rotate widget based on attribute name.

        Args:
            attr_name (str): The name of the attribute to generate a display name for.

        Returns:
            str: The generated display name."""
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        label_name = "Rotate"
        if suffix:
            label_name = label_name + ":" + suffix
        return label_name

    def __init__(
        self,
        prim_paths,
        collapsable_frame,
        stage,
        attr_path,
        op_name,
        is_valid_op,
        op_order_attr_path,
        op_order_index,
        label_kwargs=None,
    ):
        """Initializes a USDXformOpRotateWidget instance."""
        self._rotate_order_drop_down_menu = None
        super().__init__(
            prim_paths,
            collapsable_frame,
            stage,
            attr_path,
            op_name,
            is_valid_op,
            op_order_attr_path,
            op_order_index,
            label_kwargs,
        )

    def __del__(self):
        super().__del__()
        self._rotate_order_drop_down_menu = None

    @staticmethod
    def get_rotation_order_index(order):
        """Gets the index of the rotation order from a predefined list.

        Args:
            order (str): The rotation order to get the index for.

        Returns:
            int: The index of the rotation order."""
        return USDXformOpRotateWidget.ROTATE_ORDERS.index(order)

    def _change_rotation_order(self, desired_order_index):
        attr = self._stage.GetObjectAtPath(self._attr_path)
        attr_name = attr.GetName()
        if not attr_name.startswith("xformOp:rotate"):
            carb.log_warn(f"Object {self._attr_path} is not an xformOp:rotate attribute ")
            return
        is_inverse_op = False if self._op_name is None else xform_op_utils.is_inverse_op(self._op_name)
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        current_order_index = 5
        rotate_names = attr.SplitName()
        if len(rotate_names) > 1:
            rotate_order = rotate_names[1].split("rotate", 1)[1]
            current_order_index = USDXformOpRotateWidget.get_rotation_order_index(rotate_order)
        if current_order_index == desired_order_index:
            return

        # desired_order = "XYZ"
        desired_order = USDXformOpRotateWidget.ROTATE_ORDERS[desired_order_index]
        desired_attr_name = "xformOp:rotate" + desired_order
        if suffix is not None:
            desired_attr_name += ":" + suffix
        # desired_op_name = desired_attr_name if not is_inverse_op else "!invert!" + desired_attr_name
        omni.kit.commands.execute(
            "ChangeRotationOp",
            src_op_attr_path=self._attr_path,
            op_name=self._op_name,
            dst_op_attr_name=desired_attr_name,
            is_inverse_op=is_inverse_op,
            auto_target_layer=True,
        )

        # after we finish the rotation change "close" the rotation drop-down menu
        if self._rotate_order_drop_down_menu:
            self._rotate_order_drop_down_menu.visible = False

    # A callback to generate a drop-down-menu-like popup window i.e. self._rotate_order_drop_down_menu
    # it is used to select & update the rotation order, e.g. XYZ, XZY, ZYX etc.
    def _on_mouse_click(self, button, parent, order):
        # only suitable for mouse left click
        if button != 0:
            return
        # Use a popup window to act as a drop-down menu
        self._rotate_order_drop_down_menu = ui.Window(
            "RotationOrder",
            width=60,
            height=130,
            position_x=parent.screen_position_x,
            position_y=parent.screen_position_y + parent.computed_height,
            flags=ui.WINDOW_FLAGS_POPUP
            | ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR,
        )
        rotate_check_box_style = {
            "": {
                "background_color": 0x0,
                "image_url": f"{ICON_PATH}/radio_off.svg",
                "image_width": 32,
                "image_height": 32,
            },
            ":checked": {"image_url": f"{ICON_PATH}/radio_on.svg"},
        }
        with self._rotate_order_drop_down_menu.frame:
            collection = ui.RadioCollection()
            with ui.VStack():
                for index, rotate_order in enumerate(USDXformOpRotateWidget.ROTATE_ORDERS):
                    # OM-94393 let the radio button decide the height and style
                    with ui.HStack(
                        mouse_pressed_fn=(lambda x, y, b, m, index=index: self._change_rotation_order(index)), height=0
                    ):
                        ui.RadioButton(
                            style=rotate_check_box_style,
                            radio_collection=collection,
                            aligment=ui.Alignment.LEFT,
                            height=20,
                            identifier=f"button {rotate_order}",
                        )
                        ui.Label(rotate_order)
                    if rotate_order == order:
                        collection.model.set_value(index)

    def rebuild(self):
        """Rebuilds the widget based on the current state."""
        attr = self._stage.GetObjectAtPath(self._attr_path)
        # if attr.GetResolveInfo().ValueIsBlocked():
        #    return
        attr_name = attr.GetName()
        if not attr_name.startswith("xformOp:rotate"):
            carb.log_warn(f"Object {self._attr_path} is not an xformOp:rotate attribute ")
            return
        # is_inverse_op = False if self._op_name is None else xform_op_utils.is_inverse_op(self._op_name)
        label_name = self.display_name(attr_name)
        rotate_names = attr.SplitName()
        rotate_order = "ZYX"
        if len(rotate_names) > 1:
            rotate_order = rotate_names[1].split("rotate", 1)[1]
        # label_tooltip = get_attribute_type_tooltip(attr) + " " + attr.GetName()

        metadata = attr.GetAllMetadata()
        type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey))
        self._model = []
        for i in range(3):
            self._model.append(
                FabricGfVecAttributeSingleChannelModel(
                    self._stage,
                    [path.AppendProperty(attr_name) for path in self._prim_paths],
                    i,
                    False,
                    metadata,
                    change_on_edit_end=True,
                )
            )
        vec_model = GfVecAttributeModel(
            self._stage,
            [path.AppendProperty(attr_name) for path in self._prim_paths],
            3,
            type_name.type,
            False,
            metadata,
        )
        if len(self._prim_paths) == 1:
            setattr(vec_model, "transform_widget", self)  # noqa: B010
        label_tooltip = UsdPropertiesWidgetBuilder.generate_tooltip_string(attr.GetName(), metadata)

        label = None
        with ui.HStack():
            if len(self._prim_paths) == 1:
                with ui.ZStack(width=LABEL_PADDING):
                    label_tooltip = (
                        label_tooltip
                        + "\nRight click it to disable or delete it. \nLeft click it to change the rotate order, default is XYZ."
                    )
                    # This rectangle is act as a hover hint helper
                    ui.Rectangle(
                        style={":hovered": {"background_color": 0xFF444444}, "background_color": 0xFF333333},
                        mouse_pressed_fn=(lambda x, y, b, m: self._show_right_click_menu(b)),
                    )

                    # We use a label + a triangle to hack a combo box that are closer to the design
                    label_h_stack = ui.HStack(width=LABEL_PADDING)
                    label_h_stack.set_mouse_pressed_fn(
                        lambda x, y, b, m, order=rotate_order, parent_widget=label_h_stack: self._on_mouse_click(
                            b, parent_widget, order
                        )
                    )
                    label_h_stack.identifier = "rotation dropdown button"
                    with label_h_stack:
                        label = HighlightLabel(
                            label_name,
                            name="title",
                            tooltip=label_tooltip,
                            width=35,
                            **self._label_kwargs,
                        )

                        self._create_inverse_widgets()
                        ui.Spacer(width=5)
                        # use this triangle to simulate a combo box
                        with ui.VStack():
                            ui.Spacer(height=10)
                            ui.Triangle(
                                name="default",
                                width=8,
                                height=6,
                                style={"background_color": 0xFF9E9E9E},
                                alignment=ui.Alignment.CENTER_BOTTOM,
                            )
            else:
                with ui.HStack(width=LABEL_PADDING):
                    label = HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                    ui.Spacer()
                    self._create_inverse_widgets()
            with ui.HStack():
                range_min, range_max = UsdPropertiesWidgetBuilder.get_attr_value_range(metadata)
                kwargs = {"min": range_min, "max": range_max, "step": 1.0}
                UsdPropertiesWidgetBuilder.create_float_drag_per_channel_with_labels_and_control(
                    models=self._model,
                    metadata=metadata,
                    labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                    kwargs=kwargs,
                )

                # The vec_model is useful when we set the key for all three components together
                self._model.append(vec_model)
                UsdPropertiesWidgetBuilder.create_attribute_context_menu(label, vec_model)

    def update_fabric_value_only(self, vec_value):
        """Updates the widget's fabric value without affecting the USD value.

        Args:
            vec_value (Gf.Vec3f): The vector value to update the widget with."""
        # pylint: disable=protected-access

        attr = self._stage.GetObjectAtPath(self._attr_path)
        attr_name = attr.GetName()
        axis = [usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis()]
        order = USDXformOpRotateWidget.ROTATE_AXIS_ORDER_INDEX.get(attr_name, [0, 1, 2])
        angles = vec_value.Decompose(axis[order[0]], axis[order[1]], axis[order[2]])
        for model in self._model:
            if isinstance(model, FabricGfVecAttributeSingleChannelModel):
                model.set_fabric_value(angles[order[model._channel_index]])


class USDXformOpRotateScalarWidget(USDXformOpWidget):
    """A widget for applying scalar rotation to a single axis of selected USD prims.

    This widget allows for rotation of selected prims around a single specified axis (X, Y, or Z). Users can input scalar values to directly set the rotation angle, or use a slider to adjust the angle interactively. The rotation operation can be performed in either local or global space, depending on the current transform mode setting.
    """

    @classmethod
    def display_name(cls, attr_name: str) -> str:
        """Generates the display name for the rotate operation.

        Args:
            attr_name (str): The full attribute name of the rotate operation.

        Returns:
            str: The display name for the rotate operation."""
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        label_name = "Rotate"
        if suffix:
            label_name = label_name + ":" + suffix
        return label_name

    def rebuild(self):
        """Rebuilds the widget for a scalar rotate operation attribute."""
        attr = self._stage.GetObjectAtPath(self._attr_path)
        # if attr.GetResolveInfo().ValueIsBlocked():
        #    return
        attr_name = attr.GetName()
        if not attr_name.startswith("xformOp:rotate"):
            carb.log_warn(f"Object {self._attr_path} is not an xformOp:rotate attribute ")
            return
        # is_inverse_op = False if self._op_name is None else xform_op_utils.is_inverse_op(self._op_name)
        label_name = self.display_name(attr_name)
        rotate_names = attr.SplitName()
        rotate_order = "X"
        if len(rotate_names) > 1:
            rotate_order = rotate_names[1].split("rotate", 1)[1]
        # label_tooltip = get_attribute_type_tooltip(attr) + " " + attr.GetName()

        metadata = attr.GetAllMetadata()
        self._model = UsdAttributeModel(
            self._stage, [path.AppendProperty(attr_name) for path in self._prim_paths], False, metadata
        )

        label_tooltip = UsdPropertiesWidgetBuilder.generate_tooltip_string(attr.GetName(), metadata)
        with ui.HStack():
            with ui.HStack(width=LABEL_PADDING):
                if len(self._prim_paths) == 1:
                    with ui.ZStack():
                        label_tooltip = label_tooltip + "\nRight click it to disable or delete it. "
                        # This rectangle is act as a hover hint helper
                        ui.Rectangle(
                            style={":hovered": {"background_color": 0xFF444444}, "background_color": 0xFF333333},
                            mouse_pressed_fn=(lambda x, y, b, m: self._show_right_click_menu(b)),
                        )
                        HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                else:
                    HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                self._create_inverse_widgets()
                ui.Spacer(width=2)
            with ui.HStack():
                colors = {"X": 0xFF5555AA, "Y": 0xFF76A371, "Z": 0xFFA07D4F}
                with ui.ZStack():
                    with ui.HStack():
                        range_min, range_max = UsdPropertiesWidgetBuilder.get_attr_value_range(metadata)
                        widget_kwargs = {"model": self._model, "step": 1}
                        if range_min < range_max:
                            widget_kwargs["min"] = range_min
                            widget_kwargs["max"] = range_max
                        UsdPropertiesWidgetBuilder.create_drag_or_slider(ui.FloatDrag, ui.FloatSlider, **widget_kwargs)
                        UsdPropertiesWidgetBuilder.create_control_state(self._model)
                    with ui.HStack():
                        with ui.ZStack(width=14):
                            ui.Rectangle(
                                name="vector_label",
                                style={
                                    "background_color": colors[rotate_order],
                                    "border_radius": 3,
                                    "corner_flag": ui.CornerFlag.LEFT,
                                },
                            )
                            ui.Label(rotate_order, name="vector_label", alignment=ui.Alignment.CENTER)


class USDXformOpScaleWidget(USDXformOpWidget):
    """A widget for adjusting the scale of a USD primitive's xformOp.

    This class provides a user interface within the property panel to interactively scale a USD primitive. It supports uniform and non-uniform scaling, and can work with multiple selection.

        Args:
            prim_paths (List[Sdf.Path]): The paths to the primitives being edited.
            collapsable_frame (ui.Frame): The parent frame that can be collapsed.
            stage (Usd.Stage): The stage where the primitives exist.
            attr_path (Sdf.Path): The path to the scale attribute.
            op_name (str): The name of the operation attributing to the scaling.
            is_valid_op (bool): Flag indicating if the operation is valid.
            op_order_attr_path (Sdf.Path): The path to the xformOp order attribute.
            op_order_index (int): The index of the operation in the xformOp order.
            parent_widget: The widget that contains this scale operation widget.
            label_kwargs (dict): Additional keyword arguments for label customization."""

    @classmethod
    def display_name(cls, attr_name: str) -> str:
        """Generates a display name for scale transform operations.

        Args:
            attr_name (str): The name of the attribute associated with the transform operation.

        Returns:
            str: The display name for the scale transform operation."""
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        label_name = "Scale"
        if suffix:
            label_name = label_name + ":" + suffix
        return label_name

    def __init__(
        self,
        prim_paths,
        collapsable_frame,
        stage,
        attr_path,
        op_name,
        is_valid_op,
        op_order_attr_path,
        op_order_index,
        parent_widget,
        label_kwargs=None,
    ):
        """Initializes a USDXformOpScaleWidget instance.

        Args:
            prim_paths (List[Sdf.Path]): The paths of the prims associated with the widget.
            collapsable_frame (ui.Frame): The frame that can be collapsed in the UI.
            stage (Usd.Stage): The stage in which the prims reside.
            attr_path (Sdf.Path): The path to the attribute.
            op_name (str): The name of the operation.
            is_valid_op (bool): Indicates if the operation is valid.
            op_order_attr_path (Sdf.Path): The path to the attribute that defines the order of operations.
            op_order_index (int): The index of the operation in the order.
            parent_widget: The parent widget this widget is part of.
            label_kwargs (dict, optional): Additional keyword arguments for the label."""
        self._parent_widget = parent_widget
        super().__init__(
            prim_paths,
            collapsable_frame,
            stage,
            attr_path,
            op_name,
            is_valid_op,
            op_order_attr_path,
            op_order_index,
            label_kwargs,
        )

    def rebuild(self):
        """Reconstructs the scale widget with current stage and attribute information."""

        # The scale widget uses a modified version of the single channel model that supports
        # scaling each component of the vector uniformly.
        # If link_channels is False, the single channel model behaves as usual.
        class GfVecLinkableModel(FabricGfVecAttributeSingleChannelModel):
            def __init__(
                self,
                stage: Usd.Stage,
                attribute_paths: List[Sdf.Path],
                channel_index: int,
                self_refresh: bool,
                metadata: dict,
                change_on_edit_end=True,
                link_channels=False,
                **kwargs,
            ):
                self._link_channels = link_channels
                super().__init__(
                    stage, attribute_paths, channel_index, self_refresh, metadata, change_on_edit_end, **kwargs
                )

            def set_value(self, value):
                if self._link_channels:
                    vec_value = copy.copy(self._value)
                    for i in range(3):
                        vec_value[i] = value
                    if UsdBase.set_value(self, vec_value, -1):
                        self._value_changed()
                else:
                    super().set_value(value)

            def set_default(self, comp=-1):
                if self._link_channels:
                    value = self._default_value[self._channel_index]
                    vec_value = copy.copy(self._value)
                    for i in range(3):
                        vec_value[i] = value
                    if UsdBase.set_value(self, vec_value, -1):
                        self._value_changed()
                else:
                    super().set_default(comp)

        attr = self._stage.GetObjectAtPath(self._attr_path)
        attr_name = attr.GetName()
        if not attr_name.startswith("xformOp:scale"):
            carb.log_warn(f"Object {self._attr_path} is not an xformOp:scale attribute ")
            return
        # is_inverse_op = False if self._op_name is None else xform_op_utils.is_inverse_op(self._op_name)
        label_name = self.display_name(attr_name)
        # label_tooltip = get_attribute_type_tooltip(attr) + " " + attr.GetName()

        metadata = attr.GetAllMetadata()
        type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey))

        # pylint: disable=protected-access

        self._model = []
        for i in range(3):
            self._model.append(
                GfVecLinkableModel(
                    self._stage,
                    [path.AppendProperty(attr_name) for path in self._prim_paths],
                    i,
                    False,
                    metadata,
                    True,  # change_on_edit_end
                    self._parent_widget._link_scale,
                )
            )
        vec_model = GfVecAttributeModel(
            self._stage,
            [path.AppendProperty(attr_name) for path in self._prim_paths],
            3,
            type_name.type,
            False,
            metadata,
        )
        if len(self._prim_paths) == 1:
            setattr(vec_model, "transform_widget", self)  # noqa: B010

        label_tooltip = UsdPropertiesWidgetBuilder.generate_tooltip_string(attr.GetName(), metadata)
        label = None
        with ui.HStack():
            with ui.HStack(width=LABEL_PADDING):
                if len(self._prim_paths) == 1:
                    with ui.ZStack():
                        label_tooltip = label_tooltip + "\nRight click it for more options."
                        # This rectangle is act as a hover hint helper
                        ui.Rectangle(
                            style={":hovered": {"background_color": 0xFF444444}, "background_color": 0xFF333333},
                            mouse_pressed_fn=(lambda x, y, b, m: self._show_right_click_menu(b)),
                        )
                        label = HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                else:
                    label = HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                self._create_inverse_widgets()
                if self._parent_widget._link_scale:
                    button_style = {
                        "color": 0xFF34B5FF,
                        "background_color": 0x0,
                        "Button.Image": {"image_url": f"{ICON_PATH}/link_on.svg"},
                        ":hovered": {"color": 0xFFACDCF9},
                    }
                else:
                    button_style = {
                        "color": 0x66FFFFFF,
                        "background_color": 0x0,
                        "Button.Image": {"image_url": f"{ICON_PATH}/link_off.svg"},
                        ":hovered": {"color": 0xFFFFFFFF},
                    }
                with ui.ZStack(content_clipping=True, width=25, height=25):
                    ui.Button(
                        "",
                        style=button_style,
                        clicked_fn=self._parent_widget.toggle_link_scale,
                        tooltip="Toggle link scale",
                    )
                ui.Spacer(width=70)
            with ui.HStack(identifier="scale_stack"):
                range_min, range_max = UsdPropertiesWidgetBuilder.get_attr_value_range(metadata)
                kwargs = {"min": range_min, "max": range_max, "step": 1.0}
                UsdPropertiesWidgetBuilder.create_float_drag_per_channel_with_labels_and_control(
                    models=self._model,
                    metadata=metadata,
                    labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                    kwargs=kwargs,
                )

                # The vec_model is useful when we set the key for all three components together
                self._model.append(vec_model)
                UsdPropertiesWidgetBuilder.create_attribute_context_menu(label, vec_model)


class USDXformOpOrientWidget(USDXformOpWidget):
    """A class representing the widget for manipulating the orient attribute in USD.

    This widget allows for the editing of quaternion-based orientation attributes of a USD prim. It provides a user interface for inputting quaternion values directly or modifying them through an interactive euler angle representation.

        Args:
            prim_paths (List[Sdf.Path]): The USD prim paths that the widget will operate on.
            collapsable_frame (ui.Frame): A frame in the UI that can be collapsed.
            stage (Usd.Stage): The stage where the prim paths are located.
            attr_path (Sdf.Path): The path to the orient attribute.
            op_name (str): The name of the operation for this widget.
            is_valid_op (bool): Indicates if the operation is valid.
            op_order_attr_path (Sdf.Path): The path to the attribute that specifies the order of operations.
            op_order_index (int): The index of this operation in the operation order.
            label_kwargs (dict, optional): Keyword arguments for configuring the label of the widget."""

    @classmethod
    def display_name(cls, attr_name: str) -> str:
        """Generates a display name for orient transform operation.

        Args:
            attr_name (str): The name of the attribute representing the orient transform operation.

        Returns:
            str: A string representing the display name for the orient transform operation."""
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        label_name = "Orient"
        if suffix:
            label_name = label_name + ":" + suffix
        return label_name

    def __init__(
        self,
        prim_paths,
        collapsable_frame,
        stage,
        attr_path,
        op_name,
        is_valid_op,
        op_order_attr_path,
        op_order_index,
        label_kwargs=None,
    ):
        """Initializes the USDXformOpOrientWidget instance.

        Args:
            prim_paths (List[Sdf.Path]): Paths to the USD prims to construct the widget for.
            collapsable_frame (ui.Frame): The UI frame that can be collapsed or expanded.
            stage (Usd.Stage): The stage containing the prims.
            attr_path (Sdf.Path): The path to the orient attribute.
            op_name (str): The name of the orient operation.
            is_valid_op (bool): Indicates whether the operation is valid.
            op_order_attr_path (Sdf.Path): The path to the attribute that defines the operation order.
            op_order_index (int): The index of the operation in the operation order.
            label_kwargs (dict, optional): Additional keyword arguments for label formatting."""
        self._euler_model = None
        # here change DisplayOrientAsRotate in settings and write. super class will load it in __init__
        settings = carb.settings.get_settings()
        if settings:
            if settings.get("/persistent/app/uiSettings/DisplayOrientAsRotate") is None:
                settings.set_default_bool("/persistent/app/uiSettings/DisplayOrientAsRotate", True)
            self._display_orient_as_rotate = settings.get_as_bool("/persistent/app/uiSettings/DisplayOrientAsRotate")
        super().__init__(
            prim_paths,
            collapsable_frame,
            stage,
            attr_path,
            op_name,
            is_valid_op,
            op_order_attr_path,
            op_order_index,
            label_kwargs,
        )

    def _build_orient_widgets(self, attr, attr_name, type_name, label_name, label_tooltip, metadata):
        self._model = FabricGfQuatAttributeModel(
            self._stage, [path.AppendProperty(attr_name) for path in self._prim_paths], type_name.type, False, metadata
        )
        with ui.HStack():
            kwargs = {"min": -1, "max": 1, "step": 0.01}
            value_widget, mixed_overlay = UsdPropertiesWidgetBuilder.create_multi_float_drag_with_labels(
                self._model,
                comp_count=4,
                labels=[("W", 0xFFAA5555), ("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                **kwargs,
            )
            value_widget.identifier = f"orient_{attr_name}"
            UsdPropertiesWidgetBuilder.create_control_state(self._model, value_widget, mixed_overlay)

    def _build_euler_widgets(self, attr, attr_name, type_name, label_name, label_tooltip, metadata):
        self._euler_model = FabricGfQuatEulerAttributeModel(
            self._stage, [path.AppendProperty(attr_name) for path in self._prim_paths], type_name.type, False, metadata
        )
        with ui.HStack():
            kwargs = {"min": -360, "max": 360, "step": 1}
            value_widget, mixed_overlay = UsdPropertiesWidgetBuilder.create_multi_float_drag_with_labels(
                self._euler_model,
                comp_count=3,
                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                **kwargs,
            )
            value_widget.identifier = f"euler_{attr_name}"
            UsdPropertiesWidgetBuilder.create_control_state(self._euler_model, value_widget, mixed_overlay)

    def _build_header(self, attr, attr_name, type_name, label_name, label_tooltip, metadata):
        with ui.ZStack(width=LABEL_PADDING):
            if len(self._prim_paths) == 1:
                label_tooltip = (
                    label_tooltip
                    + "\nDisplay Orient As Euler Angles. \nRight click to disable or delete it. \nLeft click to switch between Orient & Euler Angles."
                )
                # A black rect background indicates the Orient is not original data format
                _rect = ui.Rectangle(
                    style={
                        "Rectangle:hovered": {"background_color": 0xFF444444},
                        "Rectangle": {"background_color": 0xFF333333},
                    },
                    tooltip=label_tooltip,
                )
                # _rect = ui.Rectangle(tooltip=label_tooltip)
                _rect.set_mouse_pressed_fn(lambda x, y, b, m: self._show_right_click_menu(b))

            # TODO: Replace this hack when OM-24290 is fixed
            with ui.ZStack():
                _button = ui.Button(
                    label_name,
                    name="title",
                    width=50,
                    tooltip=label_tooltip if len(self._prim_paths) > 1 else "",
                    style=euler_view_button_style if self._display_orient_as_rotate else quat_view_button_style,
                )
                _button.set_mouse_pressed_fn(
                    lambda x, y, b, m, widget=_button: self._on_orient_button_clicked(b, widget)
                )
                self._create_inverse_widgets()
                with ui.HStack():
                    ui.Spacer(width=35)
                    ui.Image(f"{ICON_PATH}/orient_button.svg", width=10, alignment=ui.Alignment.CENTER)

    def rebuild(self):
        """Rebuilds the widget to represent the orient operation."""
        # attr & attr_name
        attr = self._stage.GetObjectAtPath(self._attr_path)
        attr_name = attr.GetName()
        if not attr_name.startswith("xformOp:orient"):
            carb.log_warn(f"Object {self._attr_path} is not an xformOp:orient attribute ")
            return

        # metadata
        metadata = attr.GetAllMetadata()

        # type_name
        type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey))

        # label_name
        label_name = self.display_name(attr_name)

        # label_tooltip
        label_tooltip = UsdPropertiesWidgetBuilder.generate_tooltip_string(attr.GetName(), metadata)

        with ui.HStack():
            self._build_header(attr, attr_name, type_name, label_name, label_tooltip, metadata)
            # Create two views, Quaternion view & Euler Angle view
            # self._display_orient_as_rotate True:  Euler Angle view,  False: Quaternion view
            with ui.ZStack():
                # Quaternion view is default on
                self._quat_view = ui.Frame(visible=not self._display_orient_as_rotate)
                with self._quat_view:
                    self._build_orient_widgets(attr, attr_name, type_name, label_name, label_tooltip, metadata)
                # Euler view is default off
                self._euler_view = ui.Frame(visible=self._display_orient_as_rotate)
                with self._euler_view:
                    self._build_euler_widgets(attr, attr_name, type_name, label_name, label_tooltip, metadata)

    def update_fabric_value_only(self, vec_value):
        """Updates the fabric value of the orient attribute without changing the USD value.

        Args:
            vec_value (Gf.Quat): The new fabric value to set for the orient attribute."""
        self._model.set_fabric_value(vec_value)
        self._euler_model.set_fabric_value(vec_value)


class USDXformOpTransformWidget(USDXformOpWidget):
    """A widget for applying transform operations to USD prims.

    This widget provides an interface to apply translation, rotation, and scaling operations to selected USD prims within the stage. It supports operations in both local and global coordinate spaces, and facilitates both direct manipulation and numerical input of transform values.

        Args:
            prim_paths (List[Sdf.Path]): List of paths to the prims that the transform operations are applied to.
            collapsable_frame (ui.Frame): The UI frame that this widget will be a part of.
            stage (Usd.Stage): The stage where the prims are located."""

    @classmethod
    def display_name(cls, attr_name: str) -> str:
        """Returns the display name for the transform operation.

        Args:
            attr_name (str): The name of the attribute representing the operation.

        Returns:
            str: The formatted display name."""
        suffix = xform_op_utils.get_op_name_suffix(attr_name)
        label_name = "Transform"
        if suffix:
            label_name = label_name + ":" + suffix
        return label_name

    def rebuild(self):
        """Rebuilds the widget for the transform operation."""
        attr = self._stage.GetObjectAtPath(self._attr_path)
        attr_name = attr.GetName()
        if not attr_name.startswith("xformOp:transform"):
            carb.log_warn(f"Object {self._attr_path} is not an xformOp:transform attribute ")
            return
        # is_inverse_op = False if self._op_name is None else xform_op_utils.is_inverse_op(self._op_name)
        label_name = self.display_name(attr_name)
        # label_tooltip = get_attribute_type_tooltip(attr) + " " + attr.GetName()

        metadata = attr.GetAllMetadata()
        type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey))
        self._model = FabricGfMatrixAttributeModel(
            self._stage,
            [path.AppendProperty(attr_name) for path in self._prim_paths],
            4,
            type_name.type,
            False,
            metadata,
        )
        label_tooltip = UsdPropertiesWidgetBuilder.generate_tooltip_string(attr.GetName(), metadata)
        with ui.HStack():
            with ui.HStack(width=LABEL_PADDING):
                if len(self._prim_paths) == 1:
                    with ui.ZStack():
                        label_tooltip = label_tooltip + "\nRight click it to disable or delete it."
                        # This rectangle is act as a hover hint helper
                        ui.Rectangle(
                            style={":hovered": {"background_color": 0xFF444444}, "background_color": 0xFF333333},
                            mouse_pressed_fn=(lambda x, y, b, m: self._show_right_click_menu(b)),
                        )
                        HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                else:
                    HighlightLabel(label_name, name="title", tooltip=label_tooltip, **self._label_kwargs)
                self._create_inverse_widgets()
                ui.Spacer(width=2)
            with ui.HStack():
                range_min, range_max = UsdPropertiesWidgetBuilder.get_attr_value_range(metadata)
                # TODO: make step default to 1.0 before the adaptive stepping solution is available
                step = 1.0
                self._create_multi_float_drag_matrix_with_labels(
                    self._model,
                    4,
                    range_min,
                    range_max,
                    step,
                    [("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F), ("W", 0xFFAA5555)],
                )
        wgs_coord = get_wgs84_coords("", self._prim_paths[0].pathString)
        if len(wgs_coord) > 0:
            with ui.HStack():
                with ui.HStack(width=LABEL_PADDING):
                    ui.Label("WGS84", name="title", tooltip=label_tooltip)
                    ui.Spacer(width=2)
            with ui.HStack():
                with ui.VStack():
                    all_axis = ["Lat", "Lon", "Alt"]
                    colors = {"Lat": 0xFF5555AA, "Lon": 0xFF76A371, "Alt": 0xFFA07D4F}
                    component_index = 0
                    for axis in all_axis:
                        with ui.HStack():
                            with ui.HStack(width=LABEL_PADDING):
                                ui.Label("", name="title", tooltip=label_tooltip)
                            with ui.ZStack(width=20):
                                ui.Rectangle(
                                    width=20,
                                    height=20,
                                    style={
                                        "background_color": colors[axis],
                                        "border_radius": 3,
                                        "corner_flag": ui.CornerFlag.LEFT,
                                    },
                                )
                                ui.Label(axis, name="wgs84_label", alignment=ui.Alignment.CENTER)
                            # NOTE: Updating the WGS84 values does not update the transform translation,
                            # so make the input fields read-only for now.
                            # See https://nvidia-omniverse.atlassian.net/browse/OM-64348
                            ui.FloatDrag(TransformWatchModel(component_index, self._stage), enabled=False)
                            component_index = component_index + 1

    def update_fabric_value_only(self, vec_value):
        """Updates the value of the transform operation without affecting the USD value.

        Args:
            vec_value (usdrt.Gf.Matrix4d): The new value for the transform operation."""
        self._model.set_fabric_value(vec_value)


class USDResetXformStackWidget(USDXformOpWidget):
    """A widget for resetting transformation stacks on USD prims.

    This widget provides the functionality to reset the transformation stack of selected USD primitives to a
    specified state. It invalidates all transform operations above the reset position and recalculates the
    world transform from the operations below the reset position.

        Args:
            prim_paths (List[Sdf.Path]): Paths of the selected USD primitives.
            collapsable_frame (ui.Frame): The UI frame that can be collapsed or expanded.
            stage (Usd.Stage): The current USD stage.
            attr (Usd.Attribute): The attribute associated with the reset operation.
            op_name (str): The name of the reset operation.
            is_valid_op (bool): Indicates whether the operation is valid.
            op_order_attr_path (Sdf.Path): The attribute path for the order of operations.
            op_order_index (int): The index of the reset operation in the order of operations list."""

    def rebuild(self):
        """Rebuilds the widget for USDResetXformStack.

        This method clears any existing widgets and initializes the necessary UI components for the USDResetXformStack widget.

        Args:
            prim_paths (List[Sdf.Path]): List of USD prim paths to rebuild the widget for.
            collapsable_frame (ui.Frame): The frame that can be expanded or collapsed to show or hide the widget.
            stage (Usd.Stage): The stage where the USD prims are located."""
        is_reset_xform_stack_op = xform_op_utils.is_reset_xform_stack_op(self._op_name)
        if not is_reset_xform_stack_op:
            return
        label_name = "ResetXformStack"
        label_tooltip = "Invalid all above xformOp and parent transform. Calulate world transform from the op below."
        self._model = None
        with ui.HStack():
            with ui.HStack(width=LABEL_PADDING):
                ui.Label(
                    label_name,
                    name="title",
                    tooltip=label_tooltip,
                    mouse_pressed_fn=(lambda x, y, b, m: self._show_right_click_menu(b)),
                )
                ui.Spacer(width=5)
            with ui.HStack():
                with ui.VStack():
                    ui.Spacer()
                    color = 0xFF888888 if self._is_valid_op else 0xFF444444
                    ui.Line(
                        name="ResetXformStack",
                        height=2,
                        style={"color": color, "border_width": 0.5, "alignment": ui.Alignment.BOTTOM},
                        alignment=ui.Alignment.BOTTOM,
                    )
                    ui.Spacer()


class USDNoAttributeOpWidget(USDXformOpWidget):
    """A widget representing a USD operation without an associated attribute.

    This widget is used to represent operations that are present in the xformOpOrder but do not have a corresponding attribute in the USD stage. It provides options to disable or delete the operation directly from the UI.

        Args:
            prim_paths (List[Sdf.Path]): The paths to the USD prims.
            collapsable_frame (ui.Frame): Reference to the collapsable frame that contains this widget.
            stage (Usd.Stage): The USD stage where the operation exists.
            attr (Usd.Attribute): The attribute associated with the operation, if any.
            op_name (str): The name of the operation.
            is_valid_op (bool): Flag indicating if the operation is valid.
            op_order_attr_path (Sdf.Path): The path to the attribute that specifies the operation order.
            op_order_index (int): The index of the operation in the operation order list."""

    def rebuild(self):
        """Rebuilds the widget without any specific attributes."""
        if self._op_name is None:
            return
        label_name = self._op_name
        self._model = None
        is_valid_op_name = xform_op_utils.is_valid_op_name(self._op_name)
        op_attr_name = xform_op_utils.get_op_attr_name(self._op_name)
        label_error = (
            f"Could not find attribute {op_attr_name} for this xformOp."
            if is_valid_op_name
            else "Invalid xformOp name!"
        )
        with ui.HStack():
            with ui.HStack(width=LABEL_PADDING):
                ui.Label(label_name, name="title", mouse_pressed_fn=(lambda x, y, b, m: self._show_right_click_menu(b)))
                ui.Spacer(width=5)
            with ui.HStack():
                ui.Label(label_error, name="title")


class OperationTypes(Enum):
    """An enumeration for defining operation types.

    This enumeration defines different types of operations that can be performed. It includes operations for addition, multiplication, and marking invalid operations.

        Attributes:
            ADD (int): Represents an addition operation.
            MULTIPLY (int): Represents a multiplication operation.
            INVALID (int): Represents an invalid or unrecognized operation."""

    ADD = 0
    """int: Represents an addition operation."""
    MULTIPLY = 1
    """int: Represents a multiplication operation."""
    INVALID = 2
    """int: Represents an invalid or unrecognized operation."""


class TransformWidgets:
    """A widget for transforming selected USD primitives.

    This widget provides a user interface for applying transformations such as translate, rotate, and scale to selected USD primitives. It supports uniform and non-uniform scaling, and can display and modify transformations in both global and local coordinate spaces.

        Args:
            parent_widget: A reference to the parent widget that contains this transform widget."""

    def __init__(self, parent_widget):
        """Initializes a TransformWidgets instance.

        Args:
            parent_widget: A reference to the parent widget to contain this transform widget."""
        self._settings = carb.settings.get_settings()
        self._clear_widgets()
        self._parent_widget = parent_widget
        self._offset_index = -1
        self._old_transform = ""
        self._active_fields = 0
        self._dragging = False
        self._tab_swap = 0
        self._string_translate_widget = None
        self._float_translate_widget = None
        self._string_rotate_widget = None
        self._float_rotate_widget = None
        self._string_scale_widget = None
        self._float_scale_widget = None
        self._stage = None

    def __del__(self):
        self._clear_widgets()

    def clear_widgets(self):
        self._stage = None
        self._widgets = []
        self._models = defaultdict(list)

    def _create_xform_op_widget(
        self,
        prim_paths,
        collapsable_frame,
        stage,
        attr,
        op_name=None,
        is_valid_op=False,
        op_order_attr=None,
        op_order_index=-1,
    ):
        # pylint: disable=protected-access

        op_order_path = op_order_attr.GetPath() if op_order_attr is not None and op_order_attr else None
        if xform_op_utils.is_reset_xform_stack_op(op_name):
            return USDResetXformStackWidget(
                prim_paths, collapsable_frame, stage, None, op_name, is_valid_op, op_order_path, op_order_index
            )
        if not attr:
            return USDNoAttributeOpWidget(
                prim_paths, collapsable_frame, stage, None, op_name, is_valid_op, op_order_path, op_order_index
            )
        attr_name = attr.GetName()

        def match(label):
            # pylint: disable=protected-access
            return self._parent_widget._filter.matches(label)

        highlight = self._parent_widget._filter.name
        label_kwargs = {"highlight": highlight}

        if attr_name.startswith("xformOp:translate") and match(USDXformOpTranslateWidget.display_name(attr_name)):
            return USDXformOpTranslateWidget(
                prim_paths,
                collapsable_frame,
                stage,
                attr.GetPath(),
                op_name,
                is_valid_op,
                op_order_path,
                op_order_index,
                label_kwargs,
            )
        if attr_name.startswith("xformOp:rotate") and match(USDXformOpRotateWidget.display_name(attr_name)):
            op_type_name = xform_op_utils.get_op_type_name(attr_name)
            if len(op_type_name.split("rotate", 1)[1]) == 3:
                return USDXformOpRotateWidget(
                    prim_paths,
                    collapsable_frame,
                    stage,
                    attr.GetPath(),
                    op_name,
                    is_valid_op,
                    op_order_path,
                    op_order_index,
                    label_kwargs,
                )
            if len(op_type_name.split("rotate", 1)[1]) == 1:
                return USDXformOpRotateScalarWidget(
                    prim_paths,
                    collapsable_frame,
                    stage,
                    attr.GetPath(),
                    op_name,
                    is_valid_op,
                    op_order_path,
                    op_order_index,
                    label_kwargs,
                )
        if attr_name.startswith("xformOp:orient") and match(USDXformOpOrientWidget.display_name(attr_name)):
            return USDXformOpOrientWidget(
                prim_paths,
                collapsable_frame,
                stage,
                attr.GetPath(),
                op_name,
                is_valid_op,
                op_order_path,
                op_order_index,
                label_kwargs,
            )
        if attr_name.startswith("xformOp:scale") and match(USDXformOpScaleWidget.display_name(attr_name)):
            return USDXformOpScaleWidget(
                prim_paths,
                collapsable_frame,
                stage,
                attr.GetPath(),
                op_name,
                is_valid_op,
                op_order_path,
                op_order_index,
                self._parent_widget,
                label_kwargs,
            )
        if attr_name.startswith("xformOp:transform") and match(USDXformOpTransformWidget.display_name(attr_name)):
            return USDXformOpTransformWidget(
                prim_paths,
                collapsable_frame,
                stage,
                attr.GetPath(),
                op_name,
                is_valid_op,
                op_order_path,
                op_order_index,
                label_kwargs,
            )
        return None

    def _get_common_xformop(self, prim_paths):
        def _get_xformop_order(stage, prim_path):
            prim = stage.GetPrimAtPath(prim_path)
            if not prim:
                return []
            order_attr = prim.GetAttribute("xformOpOrder")
            if not order_attr:
                return []
            xform_op_order = order_attr.Get()
            if not xform_op_order:
                return []
            return xform_op_order

        common_xform_op_order = [
            "xformOp:translate",
            "xformOp:scale",
            "xformOp:rotateX",
            "xformOp:rotateY",
            "xformOp:rotateZ",
            "xformOp:rotateXYZ",
            "xformOp:rotateXZY",
            "xformOp:rotateYXZ",
            "xformOp:rotateYZX",
            "xformOp:rotateZXY",
            "xformOp:rotateZYX",
            "xformOp:orient",
            "xformOp:transform",
        ]
        all_empty_xform_op = True
        for prim_path in prim_paths:
            xform_op_order = _get_xformop_order(self._stage, prim_path)
            common_xform_op_order = list(set(common_xform_op_order) & set(xform_op_order))
            all_empty_xform_op &= len(xform_op_order) == 0

        return common_xform_op_order, all_empty_xform_op

    def _create_multi_string_with_labels(self, ui_widget, model, labels, comp_count):
        # This is similar to the multi_float_drag function above, but without USD backing and using a given single
        # field (draggable float and string, for offset mode we need to do some string parsing to look for math operations)
        rect_width = 13
        spacing = 4
        value_widget = []
        with ui.ZStack():
            with ui.HStack():
                ui.Spacer(width=rect_width)
                items = model.get_item_children(self)
                for i in range(comp_count):
                    if i != 0:
                        ui.Spacer(width=rect_width)
                    field = model.get_item_value_model(items[i], i)
                    value_widget.append(ui_widget(field))
            with ui.HStack():
                for i in range(comp_count):
                    if i != 0:
                        ui.Spacer(width=spacing)
                    label = labels[i]
                    with ui.ZStack(width=rect_width + 1):
                        ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                        ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                    ui.Spacer()
        return value_widget

    # Two sets of fields are generated, FloatDrags are visible dragging and StringFields are visible during keyboard input
    # These functions ensure the correct fields are visible and active when single clicking, double clicking, and tab selecting
    def _on_double_click(self, transform):
        self._dragging = False
        float_widget = self._get_widget(transform)[0]
        string_widget = self._get_widget(transform)[1]
        for widget in float_widget:
            widget.visible = False
        for widget in string_widget:
            widget.visible = True

        async def focus(field):
            await omni.kit.app.get_app().next_update_async()
            field.focus_keyboard()

        string_widget[self._offset_index].focus_keyboard()
        asyncio.ensure_future(focus(string_widget[self._offset_index]))
        if self._tab_swap == 1:
            self._active_fields -= 1

    def _on_press(self):
        self._dragging = True
        self._tab_swap = 0
        self._active_fields = max(self._active_fields, 0)

    def _start_field_edit(self, index, transform):
        self._offset_index = index
        self._active_fields += 1
        self._old_transform = transform
        self._settings.set(TRANSFORM_OP_SETTING, transform)
        float_widget = self._get_widget(transform)[0]
        if float_widget[index].visible is True and self._dragging is False:
            self._tab_swap += 1
            self._on_double_click(transform)

    def _swapping(self, transform):
        return transform != self._old_transform

    async def _end_string_edit(self, transform):
        self._active_fields -= 1
        if self._swapping(transform) and self._get_widget(transform)[0][0].visible is False:
            for widget in self._get_widget(transform)[1]:
                widget.visible = False
            for widget in self._get_widget(transform)[0]:
                widget.visible = True

        # Swap back to FloatDrag fields if the user clicks off
        await asyncio.sleep(0.3)

        if self._active_fields < 1 and self._get_widget(transform)[0][0].visible is False:
            for widget in self._get_widget(transform)[1]:
                widget.visible = False
            for widget in self._get_widget(transform)[0]:
                widget.visible = True

    def _get_widget(self, transform):
        if transform == TRANSFORM_OP_MOVE:
            return self._float_translate_widget, self._string_translate_widget
        if transform == TRANSFORM_OP_ROTATE:
            return self._float_rotate_widget, self._string_rotate_widget
        return self._float_scale_widget, self._string_scale_widget

    def _get_offset_data(self, text: str):
        # See if input looks like "[op] [number]", for the four supported operations
        try:
            text = text.replace(" ", "")
            if len(text) > 0:
                operator = text[0]
                value = float(text[1:])

                if operator == "*":
                    return OperationTypes.MULTIPLY, value
                if operator == "/":
                    return OperationTypes.MULTIPLY, 1.0 / value
                if operator == "+":
                    return OperationTypes.ADD, value
                if operator == "-":
                    return OperationTypes.ADD, -value
        except ValueError:
            pass

        # If we didn't find an operation, see if the input is just a number
        try:
            value = float(text)
            return OperationTypes.ADD, value
        except ValueError:
            return OperationTypes.INVALID, 0.0

    def _on_translate_offset(self, offset_text: str, index: int, stage: Usd.Stage, prim_paths: List[Sdf.Path]):
        operation, offset_value = self._get_offset_data(offset_text)

        if operation is OperationTypes.INVALID:
            carb.log_warn("Unrecognized input provided to offset field. No operation will be applied.")
        elif stage:
            with omni.kit.undo.group():
                for path in prim_paths:
                    prim = stage.GetPrimAtPath(path)
                    prim_world_xform = omni.usd.get_world_transform_matrix(prim)

                    _, scale_orient_mat, scale, rotation_mat, translation, _ = prim_world_xform.Factor()
                    scale_mat = Gf.Matrix4d().SetScale(scale)

                    local = (
                        self._settings.get(TRANSFORM_MOVE_MODE_SETTING) is None
                        or self._settings.get_as_string(TRANSFORM_MOVE_MODE_SETTING) != TRANSFORM_MODE_GLOBAL
                    )

                    if operation is OperationTypes.ADD:
                        if local:
                            offset_vec = Gf.Vec3d([offset_value if i == index else 0 for i in range(3)])
                            offset_mat = Gf.Matrix4d().SetTranslate(offset_vec)
                            translation_mat = Gf.Matrix4d().SetTranslate(translation)
                            translation = (offset_mat * rotation_mat * translation_mat).ExtractTranslation()
                        else:
                            translation[index] += offset_value
                    elif operation is OperationTypes.MULTIPLY:
                        if local:
                            offset_vec = Gf.Vec3d([offset_value if i == index else 1 for i in range(3)])
                            offset_mat = Gf.Matrix4d().SetScale(offset_vec)
                            translation_mat = Gf.Matrix4d().SetTranslate(translation)
                            # Rotate translation into local frame, apply the scale there, rotate back out
                            translation = (
                                translation_mat * rotation_mat.GetTranspose() * offset_mat * rotation_mat
                            ).ExtractTranslation()
                        else:
                            translation[index] *= offset_value

                    translation_mat = Gf.Matrix4d().SetTranslate(translation)
                    prim_world_xform = (
                        scale_orient_mat * scale_mat * scale_orient_mat.GetTranspose() * rotation_mat * translation_mat
                    )
                    parent_world_xform = omni.usd.get_world_transform_matrix(prim.GetParent())
                    prim_local_xform = prim_world_xform * parent_world_xform.GetInverse()
                    omni.kit.commands.execute("TransformPrimCommand", path=path, new_transform_matrix=prim_local_xform)
                asyncio.ensure_future(self._end_string_edit(TRANSFORM_OP_MOVE))

    def _on_rotate_offset(self, offset_text: str, index: int, stage: Usd.Stage, prim_paths: List[Sdf.Path]):
        operation, offset_value = self._get_offset_data(offset_text)

        if operation is OperationTypes.INVALID:
            carb.log_warn("Unrecognized input provided to offset field. No operation will be applied.")
        elif stage:
            with omni.kit.undo.group():
                for path in prim_paths:
                    prim = stage.GetPrimAtPath(path)
                    prim_world_xform = omni.usd.get_world_transform_matrix(prim)

                    _, scale_orient_mat, scale, rotation_mat, translation, _ = prim_world_xform.Factor()
                    scale_mat = Gf.Matrix4d().SetScale(scale)

                    local = (
                        self._settings.get(TRANSFORM_ROTATE_MODE_SETTING) is None
                        or self._settings.get_as_string(TRANSFORM_ROTATE_MODE_SETTING) != TRANSFORM_MODE_GLOBAL
                    )

                    if operation is OperationTypes.ADD:
                        axis = Gf.Vec3d([1 if i == index else 0 for i in range(3)])
                        offset_r = Gf.Rotation(axis, offset_value)
                        offset_mat = Gf.Matrix4d().SetRotate(offset_r.GetQuat())
                        if local:
                            rotation_mat = offset_mat * rotation_mat
                        else:
                            rotation_mat = rotation_mat * offset_mat
                        translation_mat = Gf.Matrix4d().SetTranslate(translation)
                        prim_world_xform = (
                            scale_orient_mat
                            * scale_mat
                            * scale_orient_mat.GetTranspose()
                            * rotation_mat
                            * translation_mat
                        )
                        parent_world_xform = omni.usd.get_world_transform_matrix(prim.GetParent())
                        prim_local_xform = prim_world_xform * parent_world_xform.GetInverse()
                        omni.kit.commands.execute(
                            "TransformPrimCommand", path=path, new_transform_matrix=prim_local_xform
                        )
                    elif operation is OperationTypes.MULTIPLY:
                        # rotation-multiply is unlike the other offsets because it we need to know the component of the
                        # current rotation about a particular axis in order to scale it, but a rotation's component along
                        # one axis can be different depending on the representation (e.g. different euler angle orderings).
                        # Rather than deal with that, we'll just look for the prim's current rotation values
                        # and scale the specified component.
                        scale, rotation, _, translation = omni.usd.get_local_transform_SRT(prim)
                        rotation[index] *= offset_value
                        omni.kit.commands.execute("TransformPrimSRTCommand", path=path, new_rotation_euler=rotation)
                asyncio.ensure_future(self._end_string_edit(TRANSFORM_OP_ROTATE))

    def _on_scale_offset(self, offset_text: str, index: int, stage: Usd.Stage, prim_paths: List[Sdf.Path]):
        # pylint: disable=protected-access

        operation, offset_value = self._get_offset_data(offset_text)

        if operation is OperationTypes.INVALID:
            carb.log_warn("Unrecognized input provided to offset field. No operation will be applied.")
        elif stage:
            with omni.kit.undo.group():
                for path in prim_paths:
                    prim = stage.GetPrimAtPath(path)
                    prim_world_xform = omni.usd.get_world_transform_matrix(prim)

                    _, scale_orient_mat, scale, rotation_mat, translation, _ = prim_world_xform.Factor()

                    if operation is OperationTypes.ADD:
                        if self._parent_widget._link_scale:
                            scale = ((scale[index] + offset_value) / scale[index]) * scale
                        else:
                            scale[index] += offset_value
                    elif operation is OperationTypes.MULTIPLY:
                        if self._parent_widget._link_scale:
                            scale = offset_value * scale
                        else:
                            scale[index] *= offset_value
                    scale_mat = Gf.Matrix4d().SetScale(scale)

                    translation_mat = Gf.Matrix4d().SetTranslate(translation)
                    prim_world_xform = (
                        scale_orient_mat * scale_mat * scale_orient_mat.GetTranspose() * rotation_mat * translation_mat
                    )
                    parent_world_xform = omni.usd.get_world_transform_matrix(prim.GetParent())
                    prim_local_xform = prim_world_xform * parent_world_xform.GetInverse()
                    omni.kit.commands.execute("TransformPrimCommand", path=path, new_transform_matrix=prim_local_xform)
                asyncio.ensure_future(self._end_string_edit(TRANSFORM_OP_SCALE))

    def build_transform_frame(self, prim_paths, collapsable_frame, stage):
        """Builds the transformation UI for the selected USD prim(s).

        Args:
            prim_paths (List[Sdf.Path]): The USD prim paths to build the transform UI for.
            collapsable_frame (ui.Frame): The frame to contain the transform UI.
            stage (Usd.Stage): The stage the prims belong to.

        Returns:
            Tuple[defaultdict, bool]: Returns a models dict and a boolean indicating empty xform ops."""
        # pylint: disable=protected-access

        self._clear_widgets()
        # Transform Frame
        if stage is None or len(prim_paths) <= 0 or prim_paths is None:
            return None, False
        prim_path = prim_paths[0]
        prim = stage.GetPrimAtPath(prim_path)
        if not prim or not prim.IsA(UsdGeom.Xformable):
            return None, False

        self._stage = stage
        xform = UsdGeom.Xformable(prim)

        # if xformOpOrder is absent or an empty array don't return
        # we may still have xformOp that are not listed in the xformOpOrder
        order_attr = prim.GetAttribute("xformOpOrder")
        if not order_attr:
            xform_op_order = []
        xform_op_order = order_attr.Get()
        if xform_op_order is None:
            xform_op_order = []

        # when select more than two prim, get common xformop to show
        if len(prim_paths) > 1:
            common_xformop, all_empty_xform_op = self._get_common_xformop(prim_paths)
            for index, op_name in enumerate(common_xformop):
                attr_name = xform_op_utils.get_op_attr_name(op_name)
                attr = Usd.Attribute()
                if attr_name is not None:
                    attr = prim.GetAttribute(attr_name)
                widget = self._create_xform_op_widget(
                    prim_paths, collapsable_frame, stage, attr, op_name, True, order_attr, index
                )
                if widget is not None:
                    self._widgets.append(widget)
                    model = widget._model
                    # if it is a list the last one is the vector model
                    if isinstance(model, list):
                        for m in model:
                            if m is not None:
                                for sdf_path in m.get_attribute_paths():
                                    self._models[sdf_path].append(m)
                    elif model is not None:
                        for sdf_path in model.get_attribute_paths():
                            self._models[sdf_path].append(model)

                    if isinstance(widget, USDXformOpOrientWidget) and widget._euler_model is not None:
                        for sdf_path in widget._euler_model.get_attribute_paths():
                            self._models[sdf_path].append(widget._euler_model)
            return self._models, all_empty_xform_op

        # attr_xform_op_order = xform.GetXformOpOrderAttr()
        # xform_ops = xform.GetOrderedXformOps()
        has_reset_xform_stack = xform.GetResetXformStack()

        reset_index = -1
        if has_reset_xform_stack:
            for i in range(len(xform_op_order) - 1, -1, -1):
                if xform_op_utils.is_reset_xform_stack_op(xform_op_order.__getitem__(i)):
                    reset_index = i
                    break

        attr_xform_ops = []
        for _, op_name in enumerate(xform_op_order):
            attr_name = xform_op_utils.get_op_attr_name(op_name)
            if attr_name is not None:
                attr = prim.GetAttribute(attr_name)
                if attr:
                    attr_xform_ops.append(attr)

        attrs_all = [attr for attr in prim.GetAttributes() if not attr.IsHidden()]
        attr_not_in_order_xform_ops = [
            attr for attr in attrs_all if (attr.GetName().startswith("xformOp:") and attr not in attr_xform_ops)
        ]
        if len(xform_op_order) + len(attr_not_in_order_xform_ops) > 0:
            with ui.VStack(spacing=8, name="frame_v_stack"):
                ui.Spacer(height=0)
                for index, op_name in enumerate(xform_op_order):
                    is_valid_op = index >= reset_index and xform_op_utils.is_valid_op_name(op_name)
                    attr_name = xform_op_utils.get_op_attr_name(op_name)
                    attr = Usd.Attribute()
                    if attr_name is not None:
                        attr = prim.GetAttribute(attr_name)
                    widget = self._create_xform_op_widget(
                        prim_paths, collapsable_frame, stage, attr, op_name, is_valid_op, order_attr, index
                    )
                    if widget is not None:
                        self._widgets.append(widget)
                        # self._models.append(widget._model)
                        model = widget._model
                        if isinstance(model, list):
                            for m in model:
                                if m is not None:
                                    for sdf_path in m.get_attribute_paths():
                                        self._models[sdf_path].append(m)
                        elif model is not None:
                            for sdf_path in model.get_attribute_paths():
                                self._models[sdf_path].append(model)

                        if isinstance(widget, USDXformOpOrientWidget) and widget._euler_model is not None:
                            for sdf_path in widget._euler_model.get_attribute_paths():
                                self._models[sdf_path].append(widget._euler_model)

                if len(attr_not_in_order_xform_ops) > 0:
                    ui.Separator()
                    for attr in attr_not_in_order_xform_ops:
                        widget = self._create_xform_op_widget(prim_paths, collapsable_frame, stage, attr)
                        if widget is not None:
                            self._widgets.append(widget)

                ui.Spacer(height=0)
        return self._models, False

    def build_transform_offset_frame(self, prim_paths, collapsable_frame, stage):
        """Builds the transformation offset UI for the selected USD prim(s).

        Args:
            prim_paths (List[Sdf.Path]): The USD prim paths to build the offset UI for.
            collapsable_frame (ui.Frame): The frame to contain the offset UI.
            stage (Usd.Stage): The stage the prims belong to."""
        # pylint: disable=protected-access

        self._clear_widgets()

        translate_model = VecAttributeModel(
            default_value="0.0",
            begin_edit_callback=functools.partial(self._start_field_edit, transform=TRANSFORM_OP_MOVE),
            end_edit_callback=functools.partial(self._on_translate_offset, stage=stage, prim_paths=prim_paths),
        )
        rotate_model = VecAttributeModel(
            default_value="0.0",
            begin_edit_callback=functools.partial(self._start_field_edit, transform=TRANSFORM_OP_ROTATE),
            end_edit_callback=functools.partial(self._on_rotate_offset, stage=stage, prim_paths=prim_paths),
        )
        scale_model = VecAttributeModel(
            default_value="0.0",
            begin_edit_callback=functools.partial(self._start_field_edit, transform=TRANSFORM_OP_SCALE),
            end_edit_callback=functools.partial(self._on_scale_offset, stage=stage, prim_paths=prim_paths),
        )

        def match(label):
            # pylint: disable=protected-access
            return self._parent_widget._filter.matches(label)

        highlight = self._parent_widget._filter.name
        label_kwargs = {"highlight": highlight}

        height_space = 8
        with ui.VStack():
            if match("Translate"):
                self._parent_widget._any_item_visible = True
                ui.Spacer(height=height_space)
                with ui.HStack():
                    with ui.HStack(width=LABEL_PADDING):
                        HighlightLabel("Translate", name="title", **label_kwargs)
                        ui.Spacer(width=2)
                    translate_stack = ui.HStack(identifier="translate_stack")
                    with translate_stack:
                        with ui.ZStack():
                            self._string_translate_widget = self._create_multi_string_with_labels(
                                ui_widget=ui.StringField,
                                model=translate_model,
                                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                                comp_count=3,
                            )
                            for widget in self._string_translate_widget:
                                widget.visible = False
                            self._float_translate_widget = self._create_multi_string_with_labels(
                                ui_widget=ui.FloatDrag,
                                model=translate_model,
                                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                                comp_count=3,
                            )
                    translate_stack.set_mouse_double_clicked_fn(
                        lambda x, y, b, m: self._on_double_click(TRANSFORM_OP_MOVE)
                    )
                    translate_stack.set_mouse_pressed_fn(lambda x, y, b, m: self._on_press())

            if match("Rotate"):
                self._parent_widget._any_item_visible = True
                ui.Spacer(height=height_space)
                with ui.HStack():
                    with ui.HStack(width=LABEL_PADDING):
                        HighlightLabel("Rotate", name="title", **label_kwargs)
                        ui.Spacer(width=2)
                    rotate_stack = ui.HStack(identifier="rotate_stack")
                    with rotate_stack:
                        with ui.ZStack():
                            self._string_rotate_widget = self._create_multi_string_with_labels(
                                ui_widget=ui.StringField,
                                model=rotate_model,
                                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                                comp_count=3,
                            )
                            for widget in self._string_rotate_widget:
                                widget.visible = False
                            self._float_rotate_widget = self._create_multi_string_with_labels(
                                ui_widget=ui.FloatDrag,
                                model=rotate_model,
                                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                                comp_count=3,
                            )
                    rotate_stack.set_mouse_double_clicked_fn(
                        lambda x, y, b, m: self._on_double_click(TRANSFORM_OP_ROTATE)
                    )
                    rotate_stack.set_mouse_pressed_fn(lambda x, y, b, m: self._on_press())

            if match("Scale"):
                self._parent_widget._any_item_visible = True
                ui.Spacer(height=height_space)
                with ui.HStack():
                    with ui.HStack(width=LABEL_PADDING):
                        HighlightLabel("Scale", name="title", **label_kwargs)
                        if self._parent_widget._link_scale:
                            button_style = {
                                "color": 0xFF34B5FF,
                                "background_color": 0x0,
                                "Button.Image": {"image_url": f"{ICON_PATH}/link_on.svg"},
                                ":hovered": {"color": 0xFFACDCF9},
                            }
                        else:
                            button_style = {
                                "color": 0x66FFFFFF,
                                "background_color": 0x0,
                                "Button.Image": {"image_url": f"{ICON_PATH}/link_off.svg"},
                                ":hovered": {"color": 0xFFFFFFFF},
                            }
                        with ui.ZStack(content_clipping=True, width=25, height=25):
                            ui.Button(
                                "",
                                style=button_style,
                                clicked_fn=self._parent_widget.toggle_link_scale,
                                identifier="toggle_link_offset_scale",
                                tooltip="Toggle link scale",
                            )
                        ui.Spacer(width=70)
                    scale_stack = ui.HStack(identifier="scale_stack")
                    with scale_stack:
                        with ui.ZStack():
                            self._string_scale_widget = self._create_multi_string_with_labels(
                                ui_widget=ui.StringField,
                                model=scale_model,
                                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                                comp_count=3,
                            )
                            for widget in self._string_scale_widget:
                                widget.visible = False
                            self._float_scale_widget = self._create_multi_string_with_labels(
                                ui_widget=ui.FloatDrag,
                                model=scale_model,
                                labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F)],
                                comp_count=3,
                            )
                    scale_stack.set_mouse_double_clicked_fn(
                        lambda x, y, b, m: self._on_double_click(TRANSFORM_OP_SCALE)
                    )
                    scale_stack.set_mouse_pressed_fn(lambda x, y, b, m: self._on_press())

    def update_from_matrix(self, matrix: "usdrt.Gf.Matrix4d"):
        """Updates the widget from the given transformation matrix.

        Args:
            matrix (usdrt.Gf.Matrix4d): The transformation matrix to update the widget from."""
        # pylint: disable=protected-access

        transform = usdrt.Gf.Transform(matrix)
        for widget in self._widgets:
            if not widget._is_valid_op:
                continue
            if widget._op_name == "xformOp:translate":
                widget.update_fabric_value_only(transform.translation)
            elif widget._op_name.startswith("xformOp:rotate"):
                widget.update_fabric_value_only(transform.rotation)
            elif widget._op_name == "xformOp:scale":
                widget.update_fabric_value_only(transform.scale)
            elif widget._op_name == "xformOp:transform":
                widget.update_fabric_value_only(matrix)
            elif widget._op_name == "xformOp:orient":
                widget.update_fabric_value_only(transform.rotation)

    def get_widgets(self):
        return self._widgets

    _clear_widgets = clear_widgets
