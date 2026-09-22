# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["Layers"]

import omni.usd

from .._omni_kit_usd_layers import LayerEditMode, LayerErrorType
from .layers_state import LayersState
from .specs_locking import SpecsLocking
from .auto_authoring import AutoAuthoring
from .specs_linking import SpecsLinking
from .live_syncing import LiveSyncing


class Layers:
    """
    Layers is the Python container of ILayersInstance, through which you can access all interfaces. For each UsdContext,
    it has a separate Layers instance.
    """

    def __init__(self, layers_instance, usd_context: omni.usd.UsdContext) -> None:
        self._layers_instance = layers_instance
        self._usd_context = usd_context
        if self._layers_instance:
            self._layers_state = LayersState(layers_instance, usd_context)
            self._specs_locking = SpecsLocking(layers_instance, usd_context)
            self._auto_authoring = AutoAuthoring(layers_instance, usd_context)
            self._specs_linking = SpecsLinking(layers_instance, usd_context)
            self._live_syncing = LiveSyncing(layers_instance, usd_context, self._layers_state)
        else:
            self._layers_state = None
            self._specs_locking = None
            self._auto_authoring = None
            self._specs_linking = None
            self._live_syncing = None

    def _destroy(self):
        if self._specs_locking:
            self._specs_locking._destroy()
            self._specs_locking = None
        if self._auto_authoring:
            self._auto_authoring._destroy()
            self._auto_authoring = None
        if self._specs_linking:
            self._specs_linking._destroy()
            self._specs_linking = None
        if self._live_syncing:
            self._live_syncing.stop_all_live_sessions()
            self._live_syncing._destroy()
            self._live_syncing = None
        if self._layers_state:
            self._layers_state._destroy()
            self._layers_state = None
        self._usd_context = None

    def get_layers_state(self) -> LayersState:
        """Gets LayersState interface."""

        return self._layers_state

    def get_specs_locking(self) -> SpecsLocking:
        """Gets SpecsLocking interface."""

        return self._specs_locking

    def get_auto_authoring(self) -> AutoAuthoring:
        """Gets AutoAuthoring interface."""

        return self._auto_authoring

    def get_specs_linking(self) -> SpecsLinking:
        """Gets SpecsLinking interface."""

        return self._specs_linking

    def get_live_syncing(self) -> LiveSyncing:
        """Gets LiveSyncing interface."""

        return self._live_syncing

    def get_event_stream(self):
        """Gets event stream of Layers instance."""

        return self._layers_instance.get_event_stream()

    def get_edit_mode(self) -> LayerEditMode:
        """Gets the current edit mode."""

        return self._layers_instance.get_edit_mode()

    def set_edit_mode(self, edit_mode: LayerEditMode):
        """Sets the current edit mode."""

        self._layers_instance.set_edit_mode(edit_mode)

    def get_last_error_type(self) -> LayerErrorType:
        """Gets the last error type."""

        return self._layers_instance.get_last_error_type()

    def get_last_error_string(self):
        """Gets the last error string."""

        return self._layers_Instance.get_last_error_string()

    @property
    def usd_context(self) -> omni.usd.UsdContext:
        """The UsdContext this instance is bound to."""

        return self._usd_context
