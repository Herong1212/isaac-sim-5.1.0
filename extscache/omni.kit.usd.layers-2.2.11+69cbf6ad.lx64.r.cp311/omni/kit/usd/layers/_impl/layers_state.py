# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "LayersState", "SETTINGS_AUTO_RELOAD_SUBLAYERS", "SETTINGS_AUTO_RELOAD_NON_SUBLAYERS",
    "SETTINGS_IGNORE_OUTDATE_NOTIFICATION"
]

import carb
from carb.eventdispatcher import get_eventdispatcher
import omni.usd
import omni.client

from typing import List, Set
from pxr import Sdf
from urllib.parse import unquote
from .layer_utils import LayerUtils
from .interface_utils import get_layer_event_payload
from .._omni_kit_usd_layers import (
    acquire_layers_state_interface,
    release_layers_state_interface,
    ILayersInstance,
)
from .event import LayerEventType


SETTINGS_AUTO_RELOAD_SUBLAYERS = "/persistent/ext/omni.kit.usd.layers/auto_reload_sublayers"
SETTINGS_AUTO_RELOAD_NON_SUBLAYERS = "/persistent/ext/omni.kit.widget.stage/auto_reload_non_sublayers"
SETTINGS_IGNORE_OUTDATE_NOTIFICATION = "/persistent/ext/omni.kit.user.layers/ignore_outdate_notification"


class LayersState:
    def __init__(self, layers_instance: ILayersInstance, usd_context) -> None:
        self._layers_instance = layers_instance
        self._layers_state_interface = acquire_layers_state_interface()
        self._dictionary = carb.dictionary.get_dictionary()
        self._usd_context = usd_context
        self._layers_event_stream = self._layers_instance.get_event_stream()
        self._layers_event_sub = self._layers_event_stream.create_subscription_to_pop_by_type(
            LayerEventType.OUTDATE_STATE_CHANGED, self._on_layer_event, name="omni.kit.usd.layers.LayersState"
        )
        self._outdate_notification = None
        self._stage_event_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.usd.layers:layers_state",
            event_name=self._usd_context.stage_event_name(omni.usd.StageEventType.CLOSING),
            on_event=lambda _: self._on_stage_closing()
        )
        self._auto_reload_layers = set()

    def _on_stage_closing(self):
        self._auto_reload_layers = set()
        if self._outdate_notification:
            self._outdate_notification.dismiss()
            self._outdate_notification = None

    def _on_layer_event(self, event: carb.events.IEvent):
        payload = get_layer_event_payload(event)
        if not payload:
            return

        if payload.event_type != LayerEventType.OUTDATE_STATE_CHANGED:
            return

        auto_reload_sublayers = carb.settings.get_settings().get(SETTINGS_AUTO_RELOAD_SUBLAYERS) or False
        auto_reload_nonsublayers = carb.settings.get_settings().get(SETTINGS_AUTO_RELOAD_NON_SUBLAYERS) or False
        ignore_outdate_notification = carb.settings.get_settings().get(SETTINGS_IGNORE_OUTDATE_NOTIFICATION) or False
        if auto_reload_sublayers and auto_reload_nonsublayers:
            self.reload_all_outdated_layers()
        else:
            if auto_reload_sublayers:
                self.reload_outdated_sublayers()

            if auto_reload_nonsublayers:
                self.reload_outdated_non_sublayers()
            else:
                to_reload_layers = []
                for identifier in payload.identifiers_or_spec_paths:
                    identifier = omni.client.normalize_url(identifier)
                    if identifier in self._auto_reload_layers:
                        to_reload_layers.append(identifier)

                LayerUtils.reload_all_layers(to_reload_layers)

        try:
            import omni.kit.notification_manager as nm

            outdated_layers = self.get_all_outdated_layer_identifiers(not_in_session=True, not_auto=True)
            if not outdated_layers:
                if self._outdate_notification:
                    self._outdate_notification.dismiss()
                    self._outdate_notification = None
            elif not self._outdate_notification or self._outdate_notification.dismissed:
                if not ignore_outdate_notification:
                    self._outdate_notification = nm.post_notification(
                        "Base USD files have been changed, please fetch changes.",
                        hide_after_timeout=False,
                        button_infos=[
                            nm.NotificationButtonInfo("FETCH", on_complete=self.reload_all_outdated_layers),
                            nm.NotificationButtonInfo("CANCEL", on_complete=None),
                        ]
                    )
        except Exception:
            pass

    @property
    def usd_context(self):
        return self._usd_context

    def _destroy(self):
        self._stage_event_sub = None
        self._layers_instance = None
        if self._outdate_notification:
            self._outdate_notification.dismiss()
            self._outdate_notification = None
        release_layers_state_interface(self._layers_state_interface)

    def set_muteness_scope(self, global_scope: bool) -> None:
        self._layers_state_interface.set_muteness_scope(self._layers_instance, global_scope)

    def is_muteness_global(self) -> bool:
        """
        Global muteness is an extended concept for Omniverse so muteness can be authored into
        USD for persistence. When you set muteness scope as global with set_muteness_scope,
        all muteness of sublayers will be stored to root layer's custom data and it will be
        loaded for next stage open.
        """

        return self._layers_state_interface.is_muteness_global(self._layers_instance)

    def is_layer_locally_muted(self, layer_identifier: str) -> bool:
        return self._layers_state_interface.is_layer_locally_muted(self._layers_instance, layer_identifier)

    def is_layer_globally_muted(self, layer_identifier: str) -> bool:
        """
        Checks if layer is globally muted or not in this usd context.
        Global muteness is a customize concept in Kit that's not from USD. It's used for complement
        the USD muteness, that works for two purposes:
        1. It's stage bound. So a layer is globally muted in this stage will not influence others.
        2. It's persistent. Right now, it's saved inside the custom data of root layer.

        After stage load, it will be read to initialize the muteness of layers. Also, global muteness
        only takes effective when it's in global state mode. See omni.usd.UsdContext.set_layer_muteness_scope
        about how to switch muteness scope. When it's not in global state mode, authoring global
        muteness will not incluence layer's muteness in stage.
        """

        return self._layers_state_interface.is_layer_globally_muted(self._layers_instance, layer_identifier)

    def is_layer_writable(self, layer_identifier: str) -> bool:
        """
        Checks if layer is writable. A layer is writable means it can be set as edit target, which should satisfy:
        1. It's not read-only on disk.
        2. It's not locked by set_layer_lock_state.
        3. It's not muted.
        It still can be set as edit target with scripts, while this can be used for guardrails.
        """

        return self._layers_state_interface.is_layer_writable(self._layers_instance, layer_identifier)

    def is_layer_readonly_on_disk(self, layer_identifier: str) -> bool:
        """
        Checks if this layer is physically read-only on disk.
        """

        return self._layers_state_interface.is_layer_readonly_on_disk(self._layers_instance, layer_identifier)

    def is_layer_savable(self, layer_identifier: str) -> bool:
        """
        Checks if this layer is savable. If it's savable means it's true by checking is_layer_writable and not anonymous.
        """

        return self._layers_state_interface.is_layer_savable(self._layers_instance, layer_identifier)

    def set_layer_lock_state(self, layer_identifier: str, locked: bool) -> None:
        """
        Layer lock is an extended concept in Omniverse that works for lock this layer temporarily without real change
        the file permission of this layer. It's just authored as a meta inside layer's custom data section, and read by
        UI.
        """

        self._layers_state_interface.set_layer_lock_state(self._layers_instance, layer_identifier, locked)

    def is_layer_locked(self, layer_identifier: str) -> bool:
        return self._layers_state_interface.is_layer_locked(self._layers_instance, layer_identifier)

    def set_layer_name(self, layer_identifier: str, name: str) -> None:
        self._layers_state_interface.set_layer_name(self._layers_instance, layer_identifier, name)

    def get_layer_name(self, layer_identifier: str) -> str:
        name = self._layers_state_interface.get_layer_name(self._layers_instance, layer_identifier)
        if not name:
            if Sdf.Layer.IsAnonymousLayerIdentifier(layer_identifier):
                layer = Sdf.Find(layer_identifier)
                if layer:
                    name = LayerUtils.get_custom_layer_name(layer)
                else:
                    name = layer_identifier
            else:
                name = Sdf.Layer.GetDisplayNameFromIdentifier(layer_identifier)

        return unquote(name)

    def get_layer_owner(self, layer_identifier: str) -> str:
        """Gets file owner of layer file. It's empty if file system does not support it."""

        return self._layers_state_interface.get_layer_owner(self._layers_instance, layer_identifier)

    def is_layer_outdated(self, layer_identifier: str) -> bool:
        """If layer is out of sync. This only works for layer inside Nucleus server but not local disk."""

        return self._layers_state_interface.is_layer_outdated(self._layers_instance, layer_identifier)

    def _populate_all_identifiers(self, item: carb.dictionary.Item, not_in_session=True, not_auto=False):
        all_layer_identifiers = []
        count = self._dictionary.get_item_child_count(item)
        import omni.kit.usd.layers as layers
        live_syncing = layers.get_live_syncing()

        for i in range(count):
            layer_item = self._dictionary.get_item_child_by_index(item, i)
            layer_id = self._dictionary.get_as_string(layer_item)

            skip = False
            if not_in_session and live_syncing.is_layer_in_live_session(layer_id):
                skip = True

            if not_auto and self.is_auto_reload_layer(layer_id):
                skip = True

            if not skip:
                all_layer_identifiers.append(layer_id)

        return all_layer_identifiers

    def get_local_layer_identifiers(
        self, include_session_layers=False, include_anonymous_layers=True,
        include_invalid_layers=False
    ) -> List[str]:
        """Gets layer identifiers in the local layer stack of the current stage."""

        item = self._layers_state_interface.get_local_layer_identifiers(
            self._layers_instance, include_session_layers, include_anonymous_layers, include_invalid_layers
        )
        if not item:
            return []

        all_layer_identifiers = self._populate_all_identifiers(item, not_in_session=False)
        self._dictionary.destroy_item(item)

        return all_layer_identifiers

    def get_dirty_layer_identifiers(self, not_in_session=False) -> List[str]:
        """Gets all layer identifiers that have pending edits that are not saved."""

        item = self._layers_state_interface.get_dirty_layer_identifiers(self._layers_instance)
        if not item:
            return []

        all_layer_identifiers = self._populate_all_identifiers(item, not_in_session)
        self._dictionary.destroy_item(item)

        return all_layer_identifiers

    def get_all_outdated_layer_identifiers(self, not_in_session=False, not_auto=False) -> List[str]:
        """Gets all layer identifiers in the stage that are outdated currently while skipping any live-sessions"""

        item = self._layers_state_interface.get_all_outdated_layer_identifiers(self._layers_instance)
        if not item:
            return []

        all_layer_identifiers = self._populate_all_identifiers(item, not_in_session, not_auto)
        self._dictionary.destroy_item(item)

        return all_layer_identifiers

    def get_outdated_sublayer_identifiers(self, not_in_session=False, not_auto=False) -> List[str]:
        """Ges all sublayer identifiers in the local layer stack of the stage that are outdated currently."""

        item = self._layers_state_interface.get_outdated_sublayer_identifiers(self._layers_instance)
        if not item:
            return []

        all_layer_identifiers = self._populate_all_identifiers(item, not_in_session, not_auto)
        self._dictionary.destroy_item(item)

        return all_layer_identifiers

    def get_outdated_non_sublayer_identifiers(self, not_in_session=False, not_auto=False) -> List[str]:
        """
        Ges all layer identifiers except ones in the local layer stack of the stage that are outdated currently.
        Those layers include ones that are inserted as references or payloads.
        """

        item = self._layers_state_interface.get_outdated_non_sublayer_identifiers(self._layers_instance)
        if not item:
            return []

        all_layer_identifiers = self._populate_all_identifiers(item, not_in_session, not_auto)
        self._dictionary.destroy_item(item)

        return all_layer_identifiers

    def reload_all_outdated_layers(self, not_in_session=True, not_auto=False) -> None:
        """Reloads all oudated layers to fetch latest updates. We only want to reload layers that are not in session"""

        if not_in_session:
            layer_identifiers = self.get_all_outdated_layer_identifiers(not_in_session, not_auto)
            LayerUtils.reload_all_layers(layer_identifiers)
        else:
            self._layers_state_interface.reload_all_outdated_layers(self._layers_instance)

    def reload_outdated_sublayers(self, not_in_session=True, not_auto=False) -> None:
        """Reloads all oudated sublayers that are in the stage's local layer stack to fetch latest changes."""

        if not_in_session:
            layer_identifiers = self.get_outdated_sublayer_identifiers(not_in_session, not_auto)
            LayerUtils.reload_all_layers(layer_identifiers)
        else:
            self._layers_state_interface.reload_outdated_sublayers(self._layers_instance)

    def reload_outdated_non_sublayers(self, not_in_session=True, not_auto=False) -> None:
        """
        Reloads all outdated non-sublayers in the stage to fetch latest changes. If a layer is both inserted
        as sublayer and reference, it will be treated as sublayer only and will not be reloaded in this function.
        """

        if not_in_session:
            layer_identifiers = self.get_outdated_non_sublayer_identifiers(not_in_session, not_auto)
            LayerUtils.reload_all_layers(layer_identifiers)
        else:
            self._layers_state_interface.reload_outdated_non_sublayers(self._layers_instance)

    def has_local_layer(self, layer_identifier) -> bool:
        """Layer is in the local layer stack of current stage."""

        stage = self._usd_context.get_stage()
        if not stage:
            return False

        layer = Sdf.Find(layer_identifier)
        if not layer:
            return False

        return stage.HasLocalLayer(layer)

    def has_used_layer(self, layer_identifier) -> bool:
        """Layer is in the used layers of current stage."""

        stage = self._usd_context.get_stage()
        if not stage:
            return False

        layer = Sdf.Find(layer_identifier)
        if not layer:
            return False

        return layer in stage.GetUsedLayers()

    def is_auto_reload_layer(self, layer_identifier: str) -> bool:
        """Whether layer will be auto-reloaded when it's outdated or not."""

        return layer_identifier in self._auto_reload_layers

    def add_auto_reload_layer(self, layer_identifier: str):
        """Adds layer into auto-reload list. So if layer is outdated, it will be auto-reloaded."""

        stage = self._usd_context.get_stage()
        if not stage:
            return False

        layer_identifier = omni.client.normalize_url(layer_identifier)
        layer = Sdf.Find(layer_identifier)
        # Layer must be in the local layer stack of current stage.
        if not layer or layer not in stage.GetUsedLayers():
            return False

        if layer_identifier not in self._auto_reload_layers:
            self._auto_reload_layers.add(layer_identifier)
            self.__send_layer_event(layer_identifier, LayerEventType.AUTO_RELOAD_LAYERS_CHANGED)
            if self.is_layer_outdated(layer_identifier):
                LayerUtils.reload_all_layers(layer_identifier)

        return True

    def remove_auto_reload_layer(self, layer_identifier: str):
        """Remove layer from auto-reload list."""

        layer_identifier = omni.client.normalize_url(layer_identifier)

        if layer_identifier in self._auto_reload_layers:
            self._auto_reload_layers.discard(layer_identifier)
            self.__send_layer_event(layer_identifier, LayerEventType.AUTO_RELOAD_LAYERS_CHANGED)

    def get_auto_reload_layers(self) -> List[str]:
        """Returns a list of layer identifiers that are configured as auto-reload when they are outdated."""

        return list(self._auto_reload_layers)

    def __send_layer_event(self, layer_identifier, event_type: LayerEventType):
        payload = {"layer_identifier": layer_identifier}
        self._layers_event_stream.push(int(event_type), 0, payload)
