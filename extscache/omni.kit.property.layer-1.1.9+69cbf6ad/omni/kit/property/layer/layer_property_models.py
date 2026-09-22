# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides models for representing and editing paths, world axes, and metadata of USD layer items in a UI context."""


__all__ = ["LayerPathModel", "LayerWorldAxisItem", "LayerWorldAxisModel", "LayerMetaModel"]

import asyncio
import weakref

import omni.kit.commands
import omni.timeline
import omni.ui as ui
import omni.usd
from omni.kit.usd.layers import LayerUtils
from pxr import Sdf, Usd, UsdGeom, UsdPhysics

from .types import LayerMetaType

layer_widget_available = False
try:
    import omni.kit.widget.layers  # noqa: PLC0412
except ModuleNotFoundError:
    pass
else:
    layer_widget_available = True


class LayerPathModel(ui.SimpleStringModel):
    """A model representing the path of a layer within a layer hierarchy.

    This model is designed to interact with layer items and provide a way to edit and retrieve the path identifier for a given layer. It also includes functionality to handle the beginning and end of an edit operation, as well as utility methods to check if a layer is reserved or anonymous.

    Args:
        layer_item (:obj:`weakref`): A weak reference to the layer item associated with this model."""

    def __init__(self, layer_item: weakref):
        """Initializer for the LayerPathModel."""
        super().__init__()
        self._layer_item = layer_item
        if self._layer_item and self._layer_item():
            self._identifier = self._layer_item().identifier
        else:
            self._identifier = None

    def get_value_as_string(self):
        """Gets the layer identifier as a string.

        Returns:
            str: The layer identifier."""
        return self._identifier

    def set_value(self, value):
        """Sets a new value for the layer identifier.

        Args:
            value (str): The new value for the layer identifier."""
        if value != self._identifier:
            self._identifier = value
            self._value_changed()

    def begin_edit(self):
        """Begins editing process for the layer path model."""

    def end_edit(self):
        """Ends editing process and applies changes to the layer path model."""
        if not self._layer_item or not self._layer_item():
            return

        value = self.get_value_as_string()
        layer_item = self._layer_item()
        if not layer_item.reserved:
            sublayer_position = LayerUtils.get_sublayer_position_in_parent(
                layer_item.parent.identifier, layer_item.identifier
            )
            omni.kit.commands.execute(
                "ReplaceSublayer",
                layer_identifier=layer_item.parent.identifier,
                sublayer_position=sublayer_position,
                new_layer_path=value,
            )

        # OMPE-27653: Remove dependency on omni.kit.widget.layers
        if not layer_widget_available:
            return

        # OM-76598: Delay frames until layer item is initialized.
        async def focus_on_layer_item(path):
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            layer_instance = omni.kit.widget.layers.get_instance()
            layer_instance.set_current_focused_layer_item(path)

        asyncio.ensure_future(focus_on_layer_item(value))

    def replace_layer(self, value):
        """Replaces the layer with a new value and ends the editing process.

        Args:
            value (str): The new value for the layer identifier."""
        self.set_value(value)
        self.end_edit()

    def is_reserved_layer(self):
        """Checks whether the layer is reserved or not.

        Returns:
            bool: True if the layer is reserved, False otherwise."""
        if not self._layer_item or not self._layer_item():
            return True

        return self._layer_item().reserved

    def anonymous(self):
        """Checks if the layer is anonymous.

        Returns:
            bool: True if the layer is anonymous, False otherwise."""
        if not self._layer_item or not self._layer_item() or not self._layer_item().layer:
            return True

        return self._layer_item().anonymous


class LayerWorldAxisItem(ui.AbstractItem):
    """A class representing a single axis item in a world layer.

    The class encapsulates the axis information for the layer as a UI item.

    Args:
        text (str): The text representation of the axis."""

    def __init__(self, text):
        """Initializes the world axis item with the given display text."""
        super().__init__()
        self.model = ui.SimpleStringModel(text)


class LayerWorldAxisModel(ui.AbstractItemModel):
    """A model representing the world axis of a layer in a 3D scene.

    The model manages the up-axis orientation for a given stage layer, enabling the user to switch between Y-up and Z-up world axes. It provides a UI representation for axis selection and executes the necessary commands to update the stage when a change is made.

    Args:
        layer_item (weakref): A weak reference to the associated layer item."""

    def __init__(self, layer_item: weakref):
        """Constructor for LayerWorldAxisModel."""
        super().__init__()

        self._layer_item = layer_item
        self._items = [LayerWorldAxisItem(text) for text in [UsdGeom.Tokens.y, UsdGeom.Tokens.z]]
        self._current_index = ui.SimpleIntModel()
        self.on_value_changed()
        self._current_index.add_value_changed_fn(self._current_index_changed)

    def get_item_children(self, item):
        """Retrieves children of the given item.

        Args:
            item (:obj:`ui.AbstractItem`): The item to get children from."""
        return self._items

    def get_item_value_model(self, item, column_id):
        """Gets the value model for the specified item and column.

        Args:
            item (:obj:`ui.AbstractItem`): The item to get value model for.
            column_id (int): The column identifier."""
        if item is None:
            return self._current_index

        return item.model

    def _current_index_changed(self, model):
        if not self._layer_item or not self._layer_item():
            return

        stage = Usd.Stage.Open(self._layer_item().layer)
        index = model.as_int
        if index == 0:
            omni.kit.commands.execute("ModifyStageAxis", stage=stage, axis=UsdGeom.Tokens.y)
        elif index == 1:
            omni.kit.commands.execute("ModifyStageAxis", stage=stage, axis=UsdGeom.Tokens.z)
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

        self._item_changed(None)

    def get_usd_token_name(self):
        """Retrieves the USD token name for the up axis."""
        return UsdGeom.Tokens.upAxis

    def on_value_changed(self):
        """Updates the value based on the layer item's current state."""
        if self._layer_item and self._layer_item():
            layer = self._layer_item().layer
            stage = Usd.Stage.Open(layer)
            up_axis = UsdGeom.GetStageUpAxis(stage)
            index = 0 if up_axis == UsdGeom.Tokens.y else 1
            self._current_index.set_value(index)


class LayerMetaModel(ui.AbstractValueModel):
    """A model for representing and editing metadata of a USD layer item.

    This model allows for the storage and manipulation of different types of metadata associated with a layer, such as comments, documentation, start and end times, timecodes per second, and more. It provides functionality to retrieve the current metadata value as a string and to set a new value for the metadata. The model also handles the beginning and ending of metadata editing sessions.

    Args:
        layer_item (weakref): A weak reference to the layer item associated with this metadata model.
        meta_type (:obj:`LayerMetaType`): The type of metadata this model represents."""

    def __init__(self, layer_item: weakref, meta_type: LayerMetaType):
        """Initializes a LayerMetaModel instance."""
        super().__init__()
        self._layer_item = layer_item
        self._meta_type = meta_type
        self._value = self._get_value_as_string()

    def get_value_as_string(self):
        """Returns the string representation of the current metadata value.

        Returns:
            str: The current metadata value as a string."""
        return self._value

    def _get_value_as_string(self):
        if not self._layer_item or not self._layer_item():
            return None

        layer = self._layer_item().layer
        if not layer:
            return None

        if self._meta_type == LayerMetaType.COMMENT:
            return str(layer.comment)
        if self._meta_type == LayerMetaType.DOC:
            return str(layer.documentation)
        if self._meta_type == LayerMetaType.START_TIME:
            return str(layer.startTimeCode)
        if self._meta_type == LayerMetaType.END_TIME:
            return str(layer.endTimeCode)
        if self._meta_type == LayerMetaType.TIMECODES_PER_SECOND:
            return str(layer.timeCodesPerSecond)
        if layer.HasFramesPerSecond() and self._meta_type == LayerMetaType.FPS_PER_SECOND:
            return str(layer.framesPerSecond)
        if self._meta_type == LayerMetaType.UNITS:
            stage = Usd.Stage.Open(layer, None, None, Usd.Stage.LoadNone)
            meters = UsdGeom.GetStageMetersPerUnit(stage)
            return str(meters)
        if self._meta_type == LayerMetaType.KG_PER_UNIT:
            stage = Usd.Stage.Open(layer, None, None, Usd.Stage.LoadNone)
            kilograms = UsdPhysics.GetStageKilogramsPerUnit(stage)
            return str(kilograms)
        if self._layer_item().parent and self._meta_type == LayerMetaType.LAYER_OFFSET:
            parent = self._layer_item().parent
            layer_index = LayerUtils.get_sublayer_position_in_parent(parent.identifier, layer.identifier)
            offset = parent.layer.subLayerOffsets[layer_index]
            return str(offset.offset)
        if self._layer_item().parent and self._meta_type == LayerMetaType.LAYER_SCALE:
            parent = self._layer_item().parent
            layer_index = LayerUtils.get_sublayer_position_in_parent(parent.identifier, layer.identifier)
            offset = parent.layer.subLayerOffsets[layer_index]
            return str(offset.scale)

        return None

    def set_value(self, value):
        """Sets a new metadata value.

        Args:
            value (str): The new value for the metadata."""
        if value != self._value:
            self._value = value
            self._value_changed()

    def end_edit(self):
        """Finalizes the editing process and applies changes."""
        if not self._layer_item or not self._layer_item():
            return

        layer = self._layer_item().layer
        if not layer:
            return

        if self._layer_item().parent:
            parent_layer_identifier = self._layer_item().parent.identifier
        else:
            parent_layer_identifier = None

        layer_identifier = layer.identifier
        omni.kit.commands.execute(
            "ModifyLayerMetadata",
            layer_identifier=layer_identifier,
            parent_layer_identifier=parent_layer_identifier,
            meta_index=self._meta_type,
            value=self._value,
        )

    def begin_edit(self):
        """Prepares the model for editing."""

    def get_usd_token_name(self):
        """Retrieves the USD token name for the current metadata type.

        Returns:
            str: The USD token name."""
        if self._meta_type == LayerMetaType.COMMENT:
            return Sdf.Layer.CommentKey
        if self._meta_type == LayerMetaType.DOC:
            return Sdf.Layer.DocumentationKey
        if self._meta_type == LayerMetaType.START_TIME:
            return Sdf.Layer.StartTimeCodeKey
        if self._meta_type == LayerMetaType.END_TIME:
            return Sdf.Layer.EndTimeCodeKey
        if self._meta_type == LayerMetaType.TIMECODES_PER_SECOND:
            return Sdf.Layer.TimeCodesPerSecondKey
        if self._meta_type == LayerMetaType.FPS_PER_SECOND:
            return Sdf.Layer.FramesPerSecondKey
        if self._meta_type == LayerMetaType.UNITS:
            return UsdGeom.Tokens.metersPerUnit
        if self._meta_type == LayerMetaType.KG_PER_UNIT:
            return UsdPhysics.Tokens.kilogramsPerUnit
        if self._meta_type == LayerMetaType.LAYER_OFFSET:
            return "subLayerOffsets_offset"  # USD has no python bindings for this key
        if self._meta_type == LayerMetaType.LAYER_SCALE:
            return "subLayerOffsets_scale"  # USD has no python bindings for this key

        return ""

    def on_value_changed(self):
        """Updates the model's value based on the latest changes."""
        self.set_value(self._get_value_as_string())
