# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from enum import IntEnum, auto
from typing import Callable, Dict

import carb
import omni.ext
from pxr import Usd

from .core_adapter import StageAdapter


class RegistryEventType(IntEnum):
    ADAPTER_ADDED = auto()
    ADAPTER_REMOVED = auto()


class SceneDescriptionAdapterRegistry:
    """
    Registry for stage adapters.
    """

    def __init__(self):
        self._scene_description_adapters: Dict[str, Callable[[Usd.Stage], StageAdapter]] = {}
        self._event_stream = carb.events.get_events_interface().create_event_stream()
        self._adapter_registry = None

    @property
    def event_stream(self) -> carb.events.IEventStream:
        return self._event_stream

    @property
    def registered_adapters(self) -> Dict[str, Callable[[Usd.Stage], StageAdapter]]:
        return self._scene_description_adapters

    def register_stage_adapter(self, name: str, adapter_type: Callable[[Usd.Stage], StageAdapter]):
        """
        Register a stage adapter. Sends out an event after an adapter is added.
        """
        self._scene_description_adapters[name] = adapter_type
        self._event_stream.dispatch(RegistryEventType.ADAPTER_ADDED, payload={"adapter_name": name})

    def unregister_stage_adapter(self, name: str):
        """
        Unregister a stage adapter given a name. Sends out an event after an adapter is removed.
        """
        if name in self._scene_description_adapters:
            del self._scene_description_adapters[name]
            self._event_stream.dispatch(RegistryEventType.ADAPTER_REMOVED, payload={"adapter_name": name})
        else:
            carb.log_warn(f"No such adapter name exists: {name}")

    def instantiate_all_stage_adapters(self, stage: Usd.Stage) -> Dict[str, StageAdapter]:
        """
        Returns a dictionary of valid registered adapters where the key is the adapter and the value is the name (str).
        """
        valid_adapters: Dict[str, StageAdapter] = {}
        if isinstance(stage, Usd.Stage):
            for key, item in self._scene_description_adapters.items():
                adapter_stage = item(stage)
                if adapter_stage.stage:
                    valid_adapters[key] = adapter_stage
        return valid_adapters


class CorePropertyAdapterExtension(omni.ext.IExt):
    _core_instance = None

    def __init__(self):
        super().__init__()
        self._adapter_registry = None

    def on_startup(self, ext_id):
        CorePropertyAdapterExtension._core_instance = self
        self._adapter_registry = SceneDescriptionAdapterRegistry()

    def on_shutdown(self):
        self._adapter_registry = None

    @property
    def adapter_registry(self) -> SceneDescriptionAdapterRegistry:
        return self._adapter_registry


def get_adapter_registry():
    """
    Returns the adapter registry.
    """
    return CorePropertyAdapterExtension._core_instance.adapter_registry  # pylint: disable=protected-access
