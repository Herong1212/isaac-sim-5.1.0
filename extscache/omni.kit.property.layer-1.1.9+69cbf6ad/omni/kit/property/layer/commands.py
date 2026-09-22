"""This module provides commands for modifying USD stage axis and layer metadata in an undoable manner."""

__all__ = ["ModifyStageAxisCommand", "ModifyLayerMetadataCommand"]

import contextlib
import weakref

import omni.kit.commands
from omni.kit.usd.layers import LayerUtils
from pxr import Sdf, Usd, UsdGeom, UsdPhysics

from .types import LayerMetaType


class ModifyStageAxisCommand(omni.kit.commands.Command):
    """Modify stage up axis undoable **Command**.

    This command changes the up axis of a given USD stage to a specified axis. It keeps track of the original axis to allow undo operations.

    Args:
        stage: A weak reference to the USD stage that will be modified.
        axis (str): The new up axis to be set on the stage ('X', 'Y', or 'Z')."""

    def __init__(self, stage, axis):
        """Initialize the ModifyStageAxisCommand."""
        if stage:
            self._stage = weakref.ref(stage)
        else:
            self._stage = None
        self._new_axis = axis
        self._old_axis = None

    def do(self):
        """Executes the command to modify the stage up axis."""
        if self._stage and self._stage():
            self._old_axis = UsdGeom.GetStageUpAxis(self._stage())
            UsdGeom.SetStageUpAxis(self._stage(), self._new_axis)

    def undo(self):
        """Reverts the stage up axis to its previous state."""
        if self._stage and self._stage() and self._old_axis:
            UsdGeom.SetStageUpAxis(self._stage(), self._old_axis)


class ModifyLayerMetadataCommand(omni.kit.commands.Command):
    """A command for modifying layer metadata in an undoable manner.

    This command allows for the modification of various metadata fields of a layer within a stage. It captures the current state of the metadata so that it can be restored on undo.

    Args:
        layer_identifier (str): The unique identifier of the layer to modify.
        parent_layer_identifier (str): The unique identifier of the parent layer, if the target layer is a sublayer. None if the layer is a root layer.
        meta_index (:obj:`LayerMetaType`): The type of metadata to modify.
        value: The new value to set for the specified metadata field.
    """

    def __init__(self, layer_identifier, parent_layer_identifier, meta_index, value):
        """Initializes the ModifyLayerMetadataCommand with the provided metadata information."""

        super().__init__()
        self._layer_identifer = layer_identifier
        self._parent_layer_identifier = parent_layer_identifier
        self._meta_index = meta_index
        self._new_value = value
        self._old_value = None

    def _set_value(self, meta_type, value):
        layer = Sdf.Find(self._layer_identifer)
        if not layer:
            return

        if self._parent_layer_identifier:
            parent_layer = Sdf.Find(self._parent_layer_identifier)
        else:
            parent_layer = None

        with contextlib.suppress(Exception):
            if meta_type == LayerMetaType.COMMENT:
                self._old_value = layer.comment
                layer.comment = str(value)
            elif meta_type == LayerMetaType.DOC:
                self._old_value = layer.documentation
                layer.documentation = str(value)
            elif meta_type == LayerMetaType.START_TIME:
                self._old_value = layer.startTimeCode
                layer.startTimeCode = float(value)
            elif meta_type == LayerMetaType.END_TIME:
                self._old_value = layer.endTimeCode
                layer.endTimeCode = float(value)
            elif meta_type == LayerMetaType.TIMECODES_PER_SECOND:
                self._old_value = layer.timeCodesPerSecond
                layer.timeCodesPerSecond = float(value)
            elif meta_type == LayerMetaType.FPS_PER_SECOND:
                self._old_value = layer.framesPerSecond
                layer.framesPerSecond = float(value)
            elif meta_type == LayerMetaType.UNITS:
                stage = Usd.Stage.Open(layer, None, None, Usd.Stage.LoadNone)
                meters = UsdGeom.GetStageMetersPerUnit(stage)
                self._old_value = meters
                UsdGeom.SetStageMetersPerUnit(stage, float(value))
            elif meta_type == LayerMetaType.KG_PER_UNIT:
                stage = Usd.Stage.Open(layer, None, None, Usd.Stage.LoadNone)
                kilograms = UsdPhysics.GetStageKilogramsPerUnit(stage)
                self._old_value = kilograms
                UsdPhysics.SetStageKilogramsPerUnit(stage, float(value))
            elif parent_layer and meta_type == LayerMetaType.LAYER_OFFSET:
                layer_index = LayerUtils.get_sublayer_position_in_parent(
                    self._parent_layer_identifier, layer.identifier
                )
                offset = parent_layer.subLayerOffsets[layer_index]
                self._old_value = offset.offset
                parent_layer.subLayerOffsets[layer_index] = Sdf.LayerOffset(float(value), offset.scale)
            elif parent_layer and meta_type == LayerMetaType.LAYER_SCALE:
                layer_index = LayerUtils.get_sublayer_position_in_parent(
                    self._parent_layer_identifier, layer.identifier
                )
                offset = parent_layer.subLayerOffsets[layer_index]
                self._old_value = offset.scale
                parent_layer.subLayerOffsets[layer_index] = Sdf.LayerOffset(offset.offset, float(value))

    def do(self):
        """Executes the command to modify layer metadata."""
        self._set_value(self._meta_index, self._new_value)

    def undo(self):
        """Reverts the changes made by the 'do' method."""
        self._set_value(self._meta_index, self._old_value)
