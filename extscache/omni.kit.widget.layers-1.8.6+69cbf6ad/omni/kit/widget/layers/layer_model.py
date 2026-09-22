# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LayerModel"]
from .layer_settings import LayerSettings
from .layer_model_utils import LayerModelUtils
from .path_utils import PathUtils
from .layer_item import LayerItem
from .prim_spec_item import PrimSpecItem
from .globals import LayerGlobals

from pxr import Sdf
from pxr import Usd
from pxr import Tf
from pxr import Trace
from typing import Dict, Set, List, Callable
from omni.kit.usd.layers import LayerUtils
from omni.kit.async_engine import run_coroutine

import omni
import omni.ui as ui
import omni.kit.notification_manager as nm
import omni.kit.usd.layers as layers
import omni.usd
import os
import carb
from carb.eventdispatcher import get_eventdispatcher


class LayerModel(ui.AbstractItemModel):
    """Class representing the Layer Model."""
    def __init__(self, usd_context, layer_settings=None):
        """
        Initialize.

        Args:
            usd_context(omni.usd.UsdContext): The USD context for the layers.
            layer_settings(LayerSettings): The layer settings.
        """
        super().__init__()

        self._usd_context = usd_context
        self._layers = layers.get_layers(self._usd_context)
        self._layers_state = self._layers.get_layers_state()
        self._layers_auto_authoring = self._layers.get_auto_authoring()
        self._layers_specs_linking = self._layers.get_specs_linking()
        self._layers_live_syncing = self._layers.get_live_syncing()
        self._app = omni.kit.app.get_app()
        self._layer_settings = layer_settings if layer_settings else LayerSettings()

        # Cache for fast sublayer accessing
        self._sublayers_cache: Dict[str, List[LayerItem]] = {}

        # Pending changed prim specs.
        self._pending_changed_prim_spec_paths: Dict[str, Set[str]] = {}

        self._dirtiness_listeners = []
        self._stage_attach_listeners = []
        self._muteness_scope_listeners = []
        self._dirtiness_subscription = None

        self._root_layer: LayerItem = None
        self._session_layer: LayerItem = None

        # It's an array as the same layer may appear multiple times
        self._edit_target_identifier: str = None

        # The string that the shown objects should have.
        self._filter_name_text: str = None

        # Notifications
        self._base_layers_changed_notification = None
        self._authoring_layer_changed_notification = None

        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.widget.layers:layer_model",
                event_name=usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self._on_attach()),
                (omni.usd.StageEventType.CLOSING, lambda _: self._on_detach()),
                (omni.usd.StageEventType.SAVED, lambda _: self._on_stage_saved()),
                (omni.usd.StageEventType.SETTINGS_SAVING, lambda _: self._on_stage_settings_saving()),
            )
        ]

        self._merging_live_layers = False

        self._on_attach()

    def destroy(self):
        """Destroys the LayerModel instance."""
        self._clear()
        self._dirtiness_listeners.clear()
        self._stage_attach_listeners.clear()
        self._muteness_scope_listeners.clear()
        self._base_layers_changed_notification = None
        self._authoring_layer_changed_notification = None
        self._stage_event_sub = None
        self._layers = None
        self._layers_state = None
        self._layers_auto_authoring = None
        self._layers_specs_linking = None
        self._layers_live_syncing = None

    def _clear(self):
        LayerGlobals.on_stage_detached()
        if self._root_layer:
            self._root_layer.destroy()
        self._root_layer = None

        if self._session_layer:
            self._session_layer.destroy()
        self._session_layer = None

        # It's an array as the same layer may appear multiple times
        self._edit_target_identifier = None

        # The string that the shown objects should have.
        self._filter_name_text = None

        self._clear_sublayer_cache()

        self._update_subscription = None

        self._layers_event_subscription = None

    def _initialize_subscriptions(self):
        self._update_subscription = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            observer_name="omni.kit.widget.layers"
        )

        self._layers_event_subscription = self._layers.get_event_stream().create_subscription_to_pop(
            self._on_layer_events, name="Layers Model Extension"
        )

    @property
    def usd_context(self):
        """
        UsdContext corresponding to this model.

        Returns:
            :obj:'omni.usd.UsdContext'.
        """
        return self._usd_context

    @property
    def root_layer_item(self):
        """
        Root layer item.

        Returns:
            :obj:'LayerItem'.
        """
        return self._root_layer

    @property
    def session_layer_item(self):
        """
        The session layer item

        Returns:
            :obj:'LayerItem'.
        """
        return self._session_layer

    @property
    def is_in_live_session(self):
        """
        If the layer is in live session.

        Returns:
            bool: True if the stage is in live session, False otherwise.
        """
        return self._layers_live_syncing.is_stage_in_live_session()

    @property
    def normal_mode(self):
        """
        If the edit mode is 'NORMAL'.

        Returns:
            bool: True if the edit mode is 'NORMAL', False otherwise.
        """
        return self._layers.get_edit_mode() == layers.LayerEditMode.NORMAL

    @property
    def auto_authoring_mode(self):
        """
        If the edit mode is 'AUTO_AUTHORING'.

        Returns:
            bool: True if the edit mode is 'AUTO_AUTHORING', False otherwise.
        """
        return self._layers.get_edit_mode() == layers.LayerEditMode.AUTO_AUTHORING

    @auto_authoring_mode.setter
    def auto_authoring_mode(self, value):
        """
        Setter method for the 'auto_authoring_mode' property.
        This property sets the edit mode based on the given value.

        Args:
            value (bool): True to set layers to auto authoring mode, False to normal mode.
        """
        if value:
            edit_mode = layers.LayerEditMode.AUTO_AUTHORING
        else:
            edit_mode = layers.LayerEditMode.NORMAL
        self._layers.set_edit_mode(edit_mode)

    @property
    def spec_linking_mode(self):
        """
        If the edit mode is 'SPECS_LINKING'.

        Returns:
            bool: True if the edit mode is 'SPECS_LINKING', False otherwise.
        """
        return self._layers.get_edit_mode() == layers.LayerEditMode.SPECS_LINKING

    @spec_linking_mode.setter
    def spec_linking_mode(self, value):
        """
        Setter method for the 'spec_linking_mode' property.
        This property sets the edit mode based on the given value.

        Args:
            value (bool): True to set layers to spec linking mode, False to normal mode.
        """
        if value:
            edit_mode = layers.LayerEditMode.SPECS_LINKING
        else:
            edit_mode = layers.LayerEditMode.NORMAL
        self._layers.set_edit_mode(edit_mode)

    @property
    def default_edit_layer(self):
        """
        The default edit layer. (Only useful when edit mode is AUTO_AUTHORING or SPECS_LINKING).

        Returns:
            str: The default edit layer.
        """
        return self._layers_auto_authoring.get_default_layer()

    @default_edit_layer.setter
    def default_edit_layer(self, value):
        """
        Setter method for the 'default_edit_layer' property.
        This property sets the default edit layer.

        Args:
            value (str): The new value for the 'default_edit_layer' property.
        """
        self._layers_auto_authoring.set_default_layer(value)

    @property
    def global_muteness_scope(self):
        """
        If the layers' muteness scope is global.

        Returns:
            bool: True if the layers' muteness scope is global, False otherwise.
        """
        return self._layers_state.is_muteness_global()

    @global_muteness_scope.setter
    def global_muteness_scope(self, value: bool):
        """
        Setter method for the 'global_muteness_scope' property.

        Args:
            value (bool): The new value for the layers muteness scope.
        """
        self._layers_state.set_muteness_scope(value)

    def add_dirtiness_listener(self, fn: Callable[[], None]):
        """
        Add a dirtiness listener.

        Args:
            fn (Callable[[], None]): The function to be added as a dirtiness listener.
        """
        if fn and fn not in self._dirtiness_listeners:
            self._dirtiness_listeners.append(fn)

    def add_stage_attach_listener(self, fn: Callable[[bool], None]):
        """
        Add a stage attachment listener.

        Args:
            fn (Callable[[bool], None]): The function to be added as a stage attachment listener.
        """
        if fn and fn not in self._stage_attach_listeners:
            self._stage_attach_listeners.append(fn)

    def add_layer_muteness_scope_listener(self, fn: Callable[[], None]):
        """
        Add a muteness scope listener.

        Args:
            fn (Callable[[], None]): The function to be added as a muteness scope listener.
        """
        if fn and fn not in self._muteness_scope_listeners:
            self._muteness_scope_listeners.append(fn)

    def _on_layer_events(self, event: carb.events.IEvent):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        if payload.event_type == layers.LayerEventType.MUTENESS_STATE_CHANGED:
            self._on_layer_muteness_changed()
        elif payload.event_type == layers.LayerEventType.MUTENESS_SCOPE_CHANGED:
            self._on_layer_muteness_scope_changed()
        elif payload.event_type == layers.LayerEventType.LOCK_STATE_CHANGED:
            self._on_layer_lock_update()
        elif payload.event_type == layers.LayerEventType.EDIT_MODE_CHANGED:
            self._on_layer_edit_mode_update()
        elif payload.event_type == layers.LayerEventType.DEFAULT_LAYER_CHANGED:
            self._on_default_edit_layer_update()
        elif payload.event_type == layers.LayerEventType.EDIT_TARGET_CHANGED:
            edit_target_identifier = LayerUtils.get_edit_target(self._usd_context.get_stage())
            self._update_edit_target(edit_target_identifier)
        elif payload.event_type == layers.LayerEventType.SUBLAYERS_CHANGED:
            self._on_sublayer_changed()
        elif payload.event_type == layers.LayerEventType.PRIM_SPECS_CHANGED:
            for layer_identifier, spec_paths in payload.layer_spec_paths.items():
                self._on_prim_spec_changed(layer_identifier, spec_paths)
        elif payload.event_type == layers.LayerEventType.DIRTY_STATE_CHANGED:
            self._update_dirtiness()
        elif payload.event_type == layers.LayerEventType.SPECS_LINKING_CHANGED:
            for layer_identifier, spec_paths in payload.layer_spec_paths.items():
                self._on_spec_links_changed(spec_paths)
        elif payload.event_type == layers.LayerEventType.SPECS_LOCKING_CHANGED:
            self._on_spec_locks_changed(payload.identifiers_or_spec_paths)
        elif payload.event_type == layers.LayerEventType.OUTDATE_STATE_CHANGED:
            outdated_layer_identifiers = payload.identifiers_or_spec_paths
            for layer_identifier in outdated_layer_identifiers:
                sublayers = self._sublayers_cache.get(layer_identifier, [])
                for sublayer in sublayers:
                    sublayer.on_layer_outdate_state_changed()
        elif payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            for _, layer_items in self._sublayers_cache.items():
                for layer_item in layer_items:
                    layer_item.on_live_session_state_changed()
        elif payload.event_type == layers.LayerEventType.LAYER_FILE_PERMISSION_CHANGED:
            outdated_layer_identifiers = payload.identifiers_or_spec_paths
            for layer_identifier in outdated_layer_identifiers:
                sublayers = self._sublayers_cache.get(layer_identifier, [])
                for sublayer in sublayers:
                    sublayer.on_layer_lock_changed()

    def _on_spec_links_changed(self, spec_paths: List[str]):
        for _, layer_items in self._sublayers_cache.items():
            for layer_item in layer_items:
                layer_item.update_spec_links_status(spec_paths)

    def _on_spec_locks_changed(self, spec_paths: List[str]):
        for _, layer_items in self._sublayers_cache.items():
            for layer_item in layer_items:
                layer_item.update_spec_locks_status(spec_paths)

    def _on_prim_spec_changed(self, layer_identifier: str, prim_spec_paths: List[str]):
        paths = self._pending_changed_prim_spec_paths.get(layer_identifier, None)
        if not paths:
            self._pending_changed_prim_spec_paths[layer_identifier] = set(prim_spec_paths)
        else:
            paths.update(prim_spec_paths)

    def _on_sublayer_changed(self):
        all_items = []
        for _, sublayer_items in self._sublayers_cache.items():
            all_items.extend(sublayer_items)

        for item in all_items:
            self._load_sublayers(item)

    def _update_default_edit_layer(self, default_edit_layer):
        if not self.normal_mode:
            # Clears old status
            for _, sublayer_items in self._sublayers_cache.items():
                for sublayer_item in sublayer_items:
                    sublayer_item.edit_layer_in_auto_authoring_mode = False

            sublayer_items = self._sublayers_cache.get(default_edit_layer, [])
            for item in sublayer_items:
                item.edit_layer_in_auto_authoring_mode = True

    def _on_layer_edit_mode_update(self):
        for _, sublayer_items in self._sublayers_cache.items():
            for sublayer_item in sublayer_items:
                sublayer_item.on_layer_edit_mode_changed()

        edit_mode = self._layers.get_edit_mode()
        if edit_mode == layers.LayerEditMode.AUTO_AUTHORING or edit_mode == layers.LayerEditMode.SPECS_LINKING:
            for _, sublayer_items in self._sublayers_cache.items():
                for sublayer_item in sublayer_items:
                    sublayer_item.is_edit_target = False
        else:
            for _, sublayer_items in self._sublayers_cache.items():
                for sublayer_item in sublayer_items:
                    sublayer_item.edit_layer_in_auto_authoring_mode = False
            self._edit_target_identifier = ""

    def _on_default_edit_layer_update(self):
        if not self.normal_mode and self._layer_settings.show_info_notification:
            if not self._authoring_layer_changed_notification or self._authoring_layer_changed_notification.dismissed:
                self._authoring_layer_changed_notification = nm.post_notification(
                    f"Default Edit Layer has been changed.",
                    duration=3,
                    status=nm.NotificationStatus.INFO)

        self._update_default_edit_layer(self._layers_auto_authoring.get_default_layer())

    def _on_layer_lock_update(self):
        stage = self._usd_context.get_stage()
        if not stage:
            return

        carb.log_info("Layer lock status changed.")

        # If there is live update change of global muteness
        for _, sublayers in self._sublayers_cache.items():
            for sublayer in sublayers:
                sublayer.on_layer_lock_changed()
                if (
                    not self.normal_mode and
                    sublayer.identifier == self.default_edit_layer and
                    sublayer.locked
                ):
                    self.default_edit_layer = self.root_layer_item.identifier

        # Switches to root layer as edit target if current one is locked.
        edit_target_identifier = LayerUtils.get_edit_target(stage)
        locked = LayerUtils.get_layer_lock_status(
            stage.GetRootLayer(), self._edit_target_identifier
        )
        if not edit_target_identifier or locked:
            self.set_edit_target(self._root_layer, True)

    def _on_layer_muteness_changed(self):
        carb.log_info("Muteness changed.")

        # If there is live update change of global muteness
        for _, sublayers in self._sublayers_cache.items():
            for sublayer in sublayers:
                sublayer.on_muteness_changed()

        stage = self._usd_context.get_stage()
        if stage:
            edit_target_identifier = LayerUtils.get_edit_target(stage)
            if (
                not edit_target_identifier or
                (self._edit_target_identifier and stage.IsLayerMuted(self._edit_target_identifier))
            ):
                self.set_edit_target(self._root_layer, True)

    def _on_layer_muteness_scope_changed(self):
        carb.log_info("Muteness scope changed.")

        # Notify all items to refresh ui
        for _, sublayers in self._sublayers_cache.items():
            for sublayer in sublayers:
                sublayer.on_muteness_scope_changed()

        # Notify listeners
        for fn in self._muteness_scope_listeners:
            fn()

    def _update_dirtiness(self):
        # FIXME: It has an issue that sometimes it cannot receive dirtiness
        # change. It has to query this per frame currently.
        notify = False
        for _, items in self._sublayers_cache.items():
            for item in items:
                if item.layer and item.dirty != item.layer.dirty:
                    item.dirty = item.layer.dirty
                    if not notify:
                        notify = True

        if notify:
            for listener in self._dirtiness_listeners:
                listener()

    @Trace.TraceFunction
    def _handle_pending_prim_specs(self):
        # Handling pending changed prim spec paths
        for changed_layer, paths in self._pending_changed_prim_spec_paths.items():
            layer_items = self._sublayers_cache.get(changed_layer, [])
            for layer_item in layer_items:
                flags_updated, children_updated = layer_item.on_content_changed(paths)
                for prim_spec_item in flags_updated:
                    prim_spec_item.update_flags()

                for prim_spec_item in children_updated:
                    if prim_spec_item.path.IsAbsoluteRootPath():
                        self._item_changed(layer_item)
                    else:
                        self._item_changed(prim_spec_item)
        self._pending_changed_prim_spec_paths.clear()

    def _on_update(self, _):
        stage = self._usd_context.get_stage()
        if not stage:
            return

        if self._pending_changed_prim_spec_paths:
            self._handle_pending_prim_specs()

        if self._authoring_layer_changed_notification and self._authoring_layer_changed_notification.dismissed:
            self._authoring_layer_changed_notification = None

    def _reset_root(self):
        stage = self._usd_context.get_stage()
        if stage:
            self._root_layer = LayerItem(
                self._usd_context, stage.GetRootLayer().identifier, stage.GetRootLayer(), self, None
            )
            self._load_sublayers(self._root_layer)
            self._session_layer = LayerItem(
                self._usd_context, stage.GetSessionLayer().identifier, stage.GetSessionLayer(), self, None
            )
            self._load_sublayers(self._session_layer)
            self._cache_sublayer(self._root_layer)
            self._cache_sublayer(self._session_layer)
        self._item_changed(None)

    @Trace.TraceFunction
    def _on_stage_saved(self):
        if self.root_layer_item and self.root_layer_item.layer:
            # https://nvidia-omniverse.atlassian.net/browse/OM-34143
            # It's on-the-fly save-as that only changes identifier
            if self.root_layer_item.identifier != self.root_layer_item.layer.identifier:
                # https://nvidia-omniverse.atlassian.net/browse/OM-34885
                # Update current edit target identifier to avoid update it to custom data
                # of root layer to make it dirty.
                if self._edit_target_identifier == self.root_layer_item.identifier:
                    self._edit_target_identifier = self.root_layer_item.layer.identifier

                self._sublayers_cache.pop(self.root_layer_item.identifier)
                self._sublayers_cache[self.root_layer_item.layer.identifier] = [self.root_layer_item]
                self.root_layer_item.update_flags()

    @Trace.TraceFunction
    def _on_stage_settings_saving(self):
        stage = self._usd_context.get_stage()
        LayerUtils.save_authoring_layer_to_custom_data(stage)

    @Trace.TraceFunction
    def _on_attach(self):
        """Called when opening a new stage"""
        self._clear()
        stage = self._usd_context.get_stage()
        if stage:
            LayerGlobals.on_stage_attached(stage)

            # Restore authoring layer. Don't restore edit target when root is in
            # a live session.
            if not self._layers_live_syncing.get_current_live_session():
                LayerUtils.restore_authoring_layer_from_custom_data(stage)

            # Initialize edit target
            edit_target_identifier = LayerUtils.get_edit_target(stage)
            if edit_target_identifier:
                self._edit_target_identifier = edit_target_identifier
            else:
                self._edit_target_identifier = stage.GetRootLayer().identifier
                edit_target = stage.GetEditTargetForLocalLayer(stage.GetRootLayer())
                stage.SetEditTarget(edit_target)

            self._initialize_subscriptions()

            # Initialize root items.
            self._reset_root()

            # Restores edit mode
            if self._layer_settings.enable_auto_authoring_mode:
                self.auto_authoring_mode = self._layer_settings.enable_auto_authoring_mode

            # Restores edit mode
            if self._layer_settings.enable_spec_linking_mode:
                self.spec_linking_mode = self._layer_settings.enable_spec_linking_mode

            # Notify listeners
            for fn in self._stage_attach_listeners:
                fn(True)

    def _on_detach(self):
        """Called when close the stage"""
        # Notify listeners
        for fn in self._stage_attach_listeners:
            fn(False)

        self._clear()
        self._item_changed(None)

    def can_item_have_children(self, item):
        """
        Check if an item can have children.

        Args:
            item(omni.ui.AbstractItem): The item to check.
        """
        stage = self._usd_context.get_stage()
        if not stage:
            return False

        show_contents = self._layer_settings.show_layer_contents
        show_metricsassembler = self._layer_settings.show_metricsassembler_layer
        if item is None:
            if show_contents:
                return self._session_layer.filtered or self._root_layer.filtered
            else:
                return self._root_layer.filtered

        prim_spec_item = None
        layer_item = None
        if show_contents:
            if isinstance(item, PrimSpecItem):
                prim_spec_item = item
            elif isinstance(item, LayerItem):
                prim_spec_item = item.absolute_root_spec
                layer_item = item
        elif isinstance(item, LayerItem):
            layer_item = item

        if not self._filter_name_text:
            if show_metricsassembler:
                if layer_item and len(layer_item.sublayers) > 0:
                    return True
            else:
                if layer_item:
                    filtered_sublayers = [sublayer for sublayer in layer_item.sublayers if not sublayer.identifier.startswith("metrics:")]
                    if len(filtered_sublayers) > 0:
                        return True

            if prim_spec_item and prim_spec_item.prim_spec:
                return len(prim_spec_item.prim_spec.nameChildren) > 0
        else:
            if layer_item:
                if show_metricsassembler:
                    for sublayer in layer_item.sublayers:
                        if sublayer.filtered:
                            return True
                else:
                    filtered_sublayers = [sublayer for sublayer in layer_item.sublayers if not sublayer.identifier.startswith("metrics:")]
                    for sublayer in filtered_sublayers:
                        if sublayer.filtered:
                            return True

            if prim_spec_item and prim_spec_item.prim_spec:
                for child in prim_spec_item.prim_spec.nameChildren:
                    layer_item = prim_spec_item.layer_item
                    child_item, _ = layer_item._get_item_from_cache(child.path)
                    if child_item and child_item.filtered:
                        return True

        return False

    def get_item_children(self, item):
        """
        Get the children of an item, reimplemented from AbstractItemModel.

        Args:
            item(omni.ui.AbstractItem): The item whose children are to be retrieved.

        Returns:
            List: A list containing the children of the item.
        """
        if item is None:
            if self._layer_settings.show_session_layer:
                return [self._session_layer, self._root_layer]
            else:
                return [self._root_layer]

        show_contents = self._layer_settings.show_layer_contents
        show_metricsassembler = self._layer_settings.show_metricsassembler_layer

        if not self._filter_name_text:
            # If _filter_name_text is empty, then user didn't request filtered result and we can just return children.
            if isinstance(item, PrimSpecItem):
                if show_contents:
                    return item.children
                else:
                    return None
            elif isinstance(item, LayerItem):
                if show_metricsassembler:
                    if show_contents:
                        return item.prim_specs + item.sublayers
                    else:
                        return item.sublayers
                else:
                    filtered_sublayers = [sublayer for sublayer in item.sublayers if not sublayer.identifier.startswith("metrics:")]
                    if show_contents:
                        return item.prim_specs + filtered_sublayers
                    else:
                        return filtered_sublayers
            else:
                return None
        else:
            # Return
            if isinstance(item, PrimSpecItem):
                if show_contents:
                    return [child for child in item.children if child.filtered]
                else:
                    return None
            elif isinstance(item, LayerItem):
                filtered_sublayers = [sublayer for sublayer in item.sublayers if sublayer.filtered]
                if not show_metricsassembler:
                    filtered_sublayers = [sublayer for sublayer in filtered_sublayers if not sublayer.identifier.startswith("metrics:")]
                if show_contents:
                    filtered_prims = [prim_spec for prim_spec in item.prim_specs if prim_spec.filtered]
                else:
                    filtered_prims = []
                return filtered_prims + filtered_sublayers
            else:
                return None

    def _update_edit_target(self, layer_identifier: str):
        if (
            layer_identifier
            and layer_identifier != self._edit_target_identifier
            and layer_identifier in self._sublayers_cache
        ):
            new_edit_target_identifier = layer_identifier
            edit_target_items = self._sublayers_cache.get(layer_identifier)

            if self.normal_mode and self._layer_settings.show_info_notification:
                if not self._authoring_layer_changed_notification or self._authoring_layer_changed_notification.dismissed:
                    self._authoring_layer_changed_notification = nm.post_notification(
                        "Authoring Layer has been changed.",
                        duration=3,
                        status=nm.NotificationStatus.INFO)

                carb.log_info(f"Switching authoring layer from {self._edit_target_identifier} to {layer_identifier}")

            # Clear old authoring items
            old_edit_target_items = self._sublayers_cache.get(self._edit_target_identifier, [])
            for layer_item in old_edit_target_items:
                layer_item.is_edit_target = False

            self._edit_target_identifier = new_edit_target_identifier
            for layer_item in edit_target_items:
                layer_item.is_edit_target = True

    def set_edit_target(self, layer_item: LayerItem, saved=False):
        """
        Sets the edit target with the given layer item's identifier.

        Args:
            layer_item (:obj:'LayerItem'): The LayerItem to set as the edit target.
            saved (bool): Whether the edit target has been saved (default: False).
        """
        if not LayerModelUtils.can_set_as_edit_target(layer_item):
            return

        omni.kit.commands.execute("SetEditTarget", layer_identifier=layer_item.identifier)

    def get_item_value_model_count(self, item):
        """
        Reimplemented from AbstractItemModel, returns the number of value models for the given item.

        Args:
            item: The item to get the value model count for.

        Returns:
            int: The number of value models (7)."""
        return 7

    def get_item_value_model(self, item, column_id):
        """
        Reimplemented from AbstractItemModel.
        Returns the value model for the given item and column ID.

        Args:
            item(:obj:'LayerItem'): The item to get the value model for.
            column_id(int): The column ID to get the value model for.

        Returns:
            omni.ui.AbstractValueModel
        """
        if item is None:
            return None

        return item.get_item_value_model(column_id)

    def drop_accepted(self, target_item, source, drop_location=-1):
        """
        Reimplemented from AbstractItemModel. Called to highlight target when drag and drop.
        Returns whether the drop is accepted.

        Args:
            target_item(:obj:'LayerItem'): The target item to drop onto.
            source(:obj:'LayerItem'): The source item being dragged.
            drop_location(int): The location to drop the item (default: -1).

        Returns:
            bool: True if the drop is accepted, False otherwise.
        """

        if not source:
            return False

        if target_item and isinstance(target_item, LayerItem) and isinstance(source, PrimSpecItem):
            return LayerModelUtils.can_move_prim_spec_to_layer(target_item, source)
        elif target_item and isinstance(target_item, LayerItem) and isinstance(source, LayerItem):
            return LayerModelUtils.can_move_layer(target_item, source, drop_location)
        elif isinstance(source, str) or type(source).__name__ in ["NucleusItem", "FileSystemItem"]:
            # Drag and drop from the content browser
            if target_item and isinstance(target_item, LayerItem):
                if not LayerModelUtils.can_create_layer_to_location(target_item, drop_location):
                    return False

            return True

        try:
            from omni.kit.widget.versioning.checkpoints_model import CheckpointItem
            if isinstance(source, CheckpointItem):
                if target_item and isinstance(target_item, LayerItem):
                    if not LayerModelUtils.can_create_layer_to_location(target_item, drop_location):
                        return False
                return True
        except:
            pass

        return False

    def drop(self, target_item, source, drop_location=-1):
        """
        Reimplemented from AbstractItemModel. Called when dropping something to the item.

        Args:
            target_item(:obj:'LayerItem'): The target item to drop onto.
            source(:obj:'LayerItem'): The source item being dragged.
            drop_location(int): The location to drop the item (default: -1).
        """

        if not source:
            return

        if not target_item:
            target_item = self.root_layer_item
            sublayer_position = 0
        elif isinstance(target_item, PrimSpecItem):
            target_item = target_item.layer_item
            sublayer_position = 0
        elif not isinstance(target_item, LayerItem):
            return
        elif drop_location != -1 and target_item.parent:
            # Finds insert position in its parent
            target_item = target_item.parent
            sublayer_position = drop_location - len(target_item.prim_specs)
        # OMPRW-473: If the target is another item, sublayer position should also be -1
        elif drop_location == -1:
            sublayer_position = -1
        else:
            sublayer_position = 0

        if not target_item:
            return

        if type(source).__name__ in ["NucleusItem", "FileSystemItem"]:
            # Drag and drop from the TreeView of Content Browser
            source = source._path

        if type(source).__name__ == "CheckpointItem":
            # Drag and drop from the TreeView of Content Browser
            source = source.get_full_url()

        if (
            (
                # Cannot modify target layer when it's in live session already
                (target_item.is_in_live_session or self.root_layer_item.is_in_live_session) and
                not target_item.is_live_session_layer
            ) or
            (
                # Cannot add sublayer for live session layer.
                (isinstance(source, LayerItem) or isinstance(source, str)) and
                target_item.is_live_session_layer
            )
        ):
            nm.post_notification("Cannot modify target layer in live-syncing mode.")
            return

        if target_item and isinstance(target_item, LayerItem) and isinstance(source, PrimSpecItem) and drop_location == -1:
            LayerModelUtils.move_prim_spec(self, target_item, source)
        elif target_item and isinstance(target_item, LayerItem) and isinstance(source, LayerItem):
            LayerModelUtils.move_layer(target_item, source, sublayer_position)
        elif isinstance(source, str):
            # Drag and drop from the content browser
            with omni.kit.undo.group():
                for source_url in source.splitlines():
                    if omni.usd.is_usd_readable_filetype(source_url):
                        omni.kit.commands.execute(
                            "CreateSublayer",
                            layer_identifier=target_item.identifier,
                            sublayer_position=sublayer_position,
                            new_layer_path=source_url,
                            transfer_root_content=False,
                            create_or_insert=False,
                        )

    def get_drag_mime_data(self, item):
        """
        Returns Multipurpose Internet Mail Extensions (MIME) data for be able to drop this item somewhere.

        Args:
            item(:obj:'omni.ui.AbstractItem'): The target item to drop.

        Returns:
            str
        """
        # As we don't do Drag and Drop to the operating system, we return the string.
        if isinstance(item, LayerItem):
            return item.identifier if item else ""
        elif isinstance(item, PrimSpecItem):
            return str(item.path) if item else "/"

    @Trace.TraceFunction
    def find_all_specs(self, paths: List[Sdf.Path]):
        """
        Return the list of all the parent nodes and the node representing the given path.

        Args:
            paths(List[Sdf.Path]): Paths to find specs.

        Returns:
            Tuble(LayerItem, List[PrimSpecItem])
        """
        if self._edit_target_identifier:
            edit_target_items = self._sublayers_cache.get(self._edit_target_identifier, [])
            if edit_target_items:
                edit_target = next(iter(edit_target_items))
                return edit_target, edit_target.find_all_specs(paths)

        return None, []

    @Trace.TraceFunction
    def filter_by_text(self, filter_name_text):
        """
        Specify the filter string that is used to reduce the model.

        Args:
            filter_name_text(str): String used to filter layer's name text.
        """
        if self._filter_name_text == filter_name_text:
            return

        self._filter_name_text = filter_name_text
        if filter_name_text:
            self._session_layer.prefilter(filter_name_text.lower())
            self._root_layer.prefilter(filter_name_text.lower())

        self._item_changed(None)

    def refresh(self):
        """Force full re-update"""

        self._item_changed(None)
        for _, sublayers in self._sublayers_cache.items():
            for sublayer in sublayers:
                self._item_changed(sublayer)

    def has_outdated_layers(self):
        """
        Checks if there are any outdated layers in the sublayers cache.

        Returns:
            bool: True if there are any outdated layers, False otherwise.
        """
        for _, sublayers in self._sublayers_cache.items():
            if sublayers:
                sublayer = next(iter(sublayers))
                if not sublayer.latest:
                    return True
        return False

    def has_dirty_layers(self, include_omni_layers=True, include_local_layers=True):
        """
        Checks if there are any dirty layers in the current stage.

        Args:
            include_omni_layers (bool, optional): Whether to include omni layers.
                                                Defaults to True.
            include_local_layers (bool, optional): Whether to include local layers.
                                                Defaults to True.

        Returns:
            bool: True if there are any dirty layers, False otherwise.
        """
        stage = self._usd_context.get_stage()
        sublayers = LayerUtils.get_all_sublayers(stage)
        for sublayer_identifier in sublayers:
            is_omni_layer = PathUtils.is_omni_objects_enabled_path(sublayer_identifier)
            if Sdf.Layer.IsAnonymousLayerIdentifier(sublayer_identifier):
                continue

            if not include_omni_layers and is_omni_layer:
                continue
            if not include_local_layers and not is_omni_layer:
                continue

            sublayer = Sdf.Find(sublayer_identifier)
            if not sublayer:
                continue

            is_writable = LayerUtils.is_layer_writable(sublayer_identifier)
            if is_writable and sublayer.dirty:
                return True

        return False

    def get_all_dirty_layer_identifiers(self, include_omni_layers=True, include_local_layers=True):
        """
        Returns a list of all dirty layer identifiers.

        Args:
            include_omni_layers(bool): Whether to include Omni layers (default: True).
            include_local_layers(bool): Whether to include local layers (default: True).

        Returns:
            List[str]
        """
        dirty_layer_sublayers = []
        stage = self._usd_context.get_stage()
        sublayers = LayerUtils.get_all_sublayers(stage)
        for sublayer_identifier in sublayers:
            if Sdf.Layer.IsAnonymousLayerIdentifier(sublayer_identifier):
                continue

            if not include_omni_layers and PathUtils.is_omni_objects_enabled_path(sublayer_identifier):
                continue

            if not include_local_layers and not PathUtils.is_omni_objects_enabled_path(sublayer_identifier):
                continue

            sublayer = Sdf.Find(sublayer_identifier)
            if not sublayer:
                continue

            is_writable = LayerUtils.is_layer_writable(sublayer_identifier)
            if is_writable and sublayer.dirty:
                dirty_layer_sublayers.append(sublayer_identifier)

        return dirty_layer_sublayers

    def get_layer_item_by_identifier(self, layer_identifier):
        """
        Find the first layer item that has the identifier

        Args:
            layer_identifier(str): The identifier of the layer item to find.

        Returns:
            :obj:'LayerItem': The first layer item with the given identifier, or None if not found.
        """
        layer_items = self._sublayers_cache.get(layer_identifier, None)

        return next(iter(layer_items)) if layer_items else None

    def has_any_layers_locked(self):
        """
        Checks if any layers are locked.

        Returns:
            bool: True if any layers are locked, False otherwise.
        """
        all_sublayers = LayerUtils.get_all_sublayers(self._usd_context.get_stage())
        for sublayer in all_sublayers:
            locked = self._layers_state.is_layer_locked(sublayer)
            if locked:
                return True

        return False

    def save_layers(self, layer_identifiers, on_save_done: Callable[[bool, str, List[str]], None] = None):
        """
        Saves multiple layers asynchronously and executes a callback on completion.

        Args:
            layer_identifiers (List[str]): A list of identifiers for the layers to be saved.
            on_save_done (Callable[[bool, str, List[str]], None], optional): A callback function to be called upon
                completion of the save operation. The function singature is: on_save_done(bool, str, List[str]).
        """
        async def save_layers():
            result, error, saved_layers = await self._usd_context.save_layers_async(
                "", layer_identifiers
            )

            if on_save_done:
                on_save_done(result, error, saved_layers)

        run_coroutine(save_layers())

    def _is_sublayer_cached(self, layer_item: LayerItem):
        cached_items = self._sublayers_cache.get(layer_item.identifier, None)
        if not cached_items:
            return False

        return layer_item in cached_items

    def _cache_sublayer(self, layer_item: LayerItem):
        cached_items = self._sublayers_cache.get(layer_item.identifier, None)
        if cached_items:
            if layer_item not in cached_items:
                cached_items.append(layer_item)
        else:
            self._sublayers_cache[layer_item.identifier] = [layer_item]

    def _remove_cached_sublayer(self, layer_item: LayerItem):
        cached_items = self._sublayers_cache.get(layer_item.identifier, None)
        if layer_item in cached_items:
            cached_items.remove(layer_item)
        layer_item.destroy()

    def _clear_sublayer_cache(self):
        for _, sublayers in self._sublayers_cache.items():
            for sublayer in sublayers:
                sublayer.destroy()
        self._sublayers_cache.clear()

    def _gather_all_sublayer_descendants(self, item: LayerItem):
        all_children = item.sublayers
        for child in item.sublayers:
            all_children.extend(self._gather_all_sublayer_descendants(child))

        return all_children

    @Trace.TraceFunction
    def _load_sublayers(self, layer_item: LayerItem):
        carb.log_info(f"Load sublayers of layer {layer_item.identifier}.")

        if not layer_item.layer:
            return

        layer = layer_item.layer
        all_sublayer_items = []
        sublayer_paths = layer.subLayerPaths
        changed = False
        index = 0

        old_sublayer_items = layer_item.sublayers[:]
        for sublayer_path in sublayer_paths:
            # If it existed item, use it, don't recreate it.
            # If it's re-ordered, refresh list.
            sublayer_identifier = layer.ComputeAbsolutePath(sublayer_path)
            if self._layers_auto_authoring.is_auto_authoring_layer(sublayer_identifier):
                continue

            found_old = False
            index_matched = False
            for i in range(len(old_sublayer_items)):
                if os.path.normpath(sublayer_identifier) == os.path.normpath(old_sublayer_items[i].identifier):
                    found_old = old_sublayer_items[i]
                    index_matched = i == index

            if not index_matched:
                changed = True

            if found_old:
                sublayer_item = found_old
                old_sublayer_items.remove(found_old)
            else:
                # Create a new item
                sublayer = Sdf.Find(sublayer_identifier)
                sublayer_item = LayerItem(self._usd_context, sublayer_identifier, sublayer, self, layer_item)

                # Checks if there are any circular references.
                # If yes, skips to load its sublayer tree.
                parent = sublayer_item.parent
                while parent and parent.identifier != sublayer_item.identifier:
                    parent = parent.parent

                if not parent:
                    self._load_sublayers(sublayer_item)

                # Add cache item
                self._cache_sublayer(sublayer_item)

            # Initialize flags
            sublayer_item.update_flags()
            all_sublayer_items.append(sublayer_item)
            index += 1

        # This means some sublayers have been deleted
        if len(old_sublayer_items) > 0:
            changed = True

            # Remove all cached items and all its descendants
            all_destroyed_items = []
            for item in old_sublayer_items:
                all_destroyed_items.append(item)
                all_destroyed_items.extend(self._gather_all_sublayer_descendants(item))

            for descendant in all_destroyed_items:
                self._remove_cached_sublayer(descendant)

        layer_item.sublayers = all_sublayer_items

        if changed:
            self._item_changed(layer_item)

    def flatten_all_layers(self):
        """ Flatten all layers if there is not layer locked. """
        if self.has_any_layers_locked():
            return

        omni.kit.commands.execute("FlattenLayers")
