# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LayerItem"]
import carb
import omni
import omni.ui as ui
import omni.usd
import os
import omni.kit.usd.layers as layers

from .models.layer_live_update_model import LayerLiveUpdateModel
from .models.lock_model import LockModel
from .models.muteness_model import MutenessModel
from .models.layer_name_model import LayerNameModel
from .models.save_model import SaveModel
from .models.layer_latest_model import LayerLatestModel
from .models.live_session_user_model import LiveSessionUserModel
from .layer_settings import LayerSettings
from .path_utils import PathUtils
from .prim_spec_item import PrimSpecItem

from typing import List, Dict, Set, Union
from pxr import Sdf, Trace
from omni.kit.usd.layers import LayerUtils


class LayerItem(ui.AbstractItem):
    """A single AbstractItemModel item that represents a single sublayer"""

    def __init__(self, usd_context, identifier: str, layer: Sdf.Layer, model, parent_item):
        """
        Initializes a new instance of the LayerItem class.

        Args:
            usd_context (omni.usd.UsdContext): The USD context associated with the item.
            identifier (str): The identifier of the item.
            layer (Sdf.Layer): The Sdf.Layer object associated with the item.
            model (LayerModel): The model associated with the item.
            parent_item (LayerItem): The parent item of the item.
        """
        super().__init__()
        self._usd_context = usd_context
        self._model = model

        self._layer = layer
        self._parent = parent_item

        # Models
        self._name_model = LayerNameModel(self)
        self._save_model = SaveModel(self)
        self._local_mute_model = MutenessModel(self._usd_context, self, True)
        self._global_mute_model = MutenessModel(self._usd_context, self, False)
        self._live_update_model = LayerLiveUpdateModel(self._usd_context, self)
        self._latest_model = LayerLatestModel(self._usd_context, self)
        self._lock_model = LockModel(self)
        self._first_live_session_user_model = LiveSessionUserModel(None)
        self._second_live_session_user_model = LiveSessionUserModel(None)
        self._ellipsis_model = ui.SimpleStringModel("...")

        # Children
        self._sublayers: List[LayerItem] = []

        # Prim Spec of Sdf.Path.absoluteRootPath.
        # It's root of children specs.
        self._absolute_root_prim_spec = PrimSpecItem(self._usd_context, Sdf.Path.absoluteRootPath, self)

        # Cache for quick prim item access indexed by prim path
        self._prim_specs_cache: Dict[Sdf.Path, PrimSpecItem] = {}
        self._prim_specs_cache[Sdf.Path.absoluteRootPath] = self._absolute_root_prim_spec

        # Filtering for search.
        self._filtered = False
        # True if it has a child that is filtered
        self._child_filtered = False

        # If this item is root layer or session layer
        self._is_reserved_layer = False

        # Layer info
        self._identifier = identifier
        self._is_omni_layer = PathUtils.is_omni_objects_enabled_path(self._identifier)
        self._is_omni_live_layer = PathUtils.is_omni_live(self._identifier)
        stage = self._usd_context.get_stage()

        # Gets layer name
        self._layers = layers.get_layers(self._usd_context)

        self._layers_state = self._layers.get_layers_state()

        self._layers_specs_locking = self._layers.get_specs_locking()

        self._layers_specs_linking = self._layers.get_specs_linking()

        self._layers_live_syncing = self._layers.get_live_syncing()

        if stage.GetRootLayer().identifier == identifier:
            self._is_reserved_layer = True
        elif stage.GetSessionLayer().identifier == identifier:
            self._is_reserved_layer = True

        # If this layer is missing.
        self._is_missing_layer = False if self._layer else True

        live_session = self._layers_live_syncing.get_live_session_for_live_layer(self._identifier)
        self._is_live_session_layer = live_session is not None
        if self._is_live_session_layer:
            self._name = f"Session '{live_session.name}'"
            self.__update_live_session_user_models(live_session)
            self._session_url = live_session.url
        else:
            self._name = self._layers_state.get_layer_name(identifier)
            self._session_url = None

        self._user_join_event_subscription = self._layers.get_event_stream().create_subscription_to_pop_by_type(
            layers.LayerEventType.LIVE_SESSION_USER_JOINED,
            self._on_layer_events, name="Layers Item User Join"
        )
        self._user_left_event_subscription = self._layers.get_event_stream().create_subscription_to_pop_by_type(
            layers.LayerEventType.LIVE_SESSION_USER_LEFT,
            self._on_layer_events, name="Layers Item User Left"
        )

        self._is_read_only = self._layers_state.is_layer_readonly_on_disk(identifier)

        # If this item is edit target
        self._is_edit_target = False

        # If this item includes children that are edit targets
        self._has_edit_target = False

        # Initializes edit layer status.
        # Edit layer is a concept that when stage is in auto-authoring mode,
        # it's where the new prims will be hosted in.
        self._is_edit_layer_in_auto_authoring_mode = False

        # If this item includes children that are edit layers
        self._has_edit_layer = False

        # If layer is dirty or not
        self._is_dirty = self._layer.dirty if self._layer else False

        # Current saved muteness, which is used to check if it's chnaged.
        self._old_mute_state = stage.IsLayerMuted(self.identifier)

        # Current saved lock status, which is used to check if it's changed.
        self._locked_status = self._layers_state.is_layer_locked(self._identifier)

        # If the layer item is selected in the treeview.
        # FIXME: WA for refreshing selection status.
        self._selected = False

        # If this layer item is in the session layer tree.
        self._is_from_session_layer = False

        self._outdated = self._layers_state.is_layer_outdated(self._identifier)

        self._auto_reload = self._layers_state.is_auto_reload_layer(self._identifier)

        self._has_content = len(self._layer.rootPrims) > 0 if self._layer else False

        self.update_flags()

    def destroy(self):
        """Clean up used model and subscription."""
        if self._name_model:
            self._name_model.destroy()
        self._name_model = None

        if self._local_mute_model:
            self._local_mute_model.destroy()
        self._local_mute_model = None

        if self._global_mute_model:
            self._global_mute_model.destroy()
        self._global_mute_model = None

        if self._save_model:
            self._save_model.destroy()
        self._save_model = None

        if self._lock_model:
            self._lock_model.destroy()
        self._lock_model = None

        if self._live_update_model:
            self._live_update_model.destroy()
        self._live_update_model = None

        if self._latest_model:
            self._latest_model.destroy()
        self._latest_model = None

        if self._first_live_session_user_model:
            self._first_live_session_user_model.destroy()
            self._first_live_session_user_model = None

        if self._second_live_session_user_model:
            self._second_live_session_user_model.destroy()
            self._second_live_session_user_model = None

        self._ellipsis_model = None

        for sublayer in self.sublayers:
            sublayer.destroy()
        self.sublayers.clear()

        if self._absolute_root_prim_spec:
            self._absolute_root_prim_spec.destroy()
        self._clear_cache()

        self._layer = None
        self._layers = None
        self._layers_state = None
        self._layers_specs_linking = None
        self._layers_specs_locking = None
        self._layers_live_syncing = None
        self._model = None
        self._parent = None
        self._user_join_event_subscription = None
        self._user_left_event_subscription = None

    def _on_layer_events(self, event):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        if (
            payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_JOINED or
            payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT
        ):
            # Updates peer user models for live session layer only.
            if not self.is_live_session_layer:
                return

            # Gets base layer identifier for this live session layer
            base_layer = self.base_layer
            if not base_layer:
                carb.log_warn(f"Base layer for live layer {self._identifier} cannot be found.")
                return

            base_layer_identifier = base_layer.identifier
            if not payload.is_layer_influenced(base_layer_identifier):
                return

            live_session = self._layers_live_syncing.get_current_live_session(base_layer_identifier)
            if live_session:
                self.__update_live_session_user_models(live_session)

    @property
    def layer(self):
        """
        Getter method for the 'layer' property.

        Returns:
            Sdf.Layer: The layer associated with the item.
        """
        return self._layer

    @property
    def is_omni_layer(self):
        """
        If the item represents an omni layer.

        Returns:
            bool: True if the item represents an omni layer, False otherwise.
        """
        return self._is_omni_layer

    @property
    def is_omni_live_path(self):
        """
        If the item represents an omni live layer.

        Returns:
            bool: True if the item represents an omni live layer, False otherwise.
        """
        return self._is_omni_live_layer

    @property
    def model(self):
        """
        Getter method for the 'model' property.

        Returns:
            :obj:'LayerModel': The model associated with the item.
        """
        return self._model

    @property
    def usd_context(self):
        """
        Getter method for the 'usd_context' property.

        Returns:
            Usd.Context: The USD context associated with the item.
        """
        return self._usd_context

    @property
    def from_session_layer(self):
        """
        If this layer is under the session layer.

        Returns:
            bool
        """
        return self._is_from_session_layer

    @property
    def sublayers(self):
        """
        Subayer items under this layer.

        Returns:
            List[LayerItem]
        """
        return self._sublayers

    @sublayers.setter
    def sublayers(self, value):
        self._sublayers = value

    @property
    def absolute_root_spec(self):
        """The prim spec that represents the root of prim tree."""
        return self._absolute_root_prim_spec

    @property
    def prim_specs(self):
        """Prim specs under this layer."""
        return self._absolute_root_prim_spec.children

    @property
    def outdated(self):
        """If this layer item is outdated."""
        return self._outdated

    @property
    def has_children(self):
        """If this layer item has children."""
        return len(self._sublayers) > 0 or self._absolute_root_prim_spec.has_children

    @property
    def parent(self):
        """Parent layer item."""
        return self._parent

    @property
    def filtered(self):
        """If this layer item is filtered in the search list."""
        return self._filtered or self._child_filtered

    @property
    def identifier(self):
        """Identifier of this layer item."""
        return self._identifier

    @property
    def name(self):
        """Name of this layer item."""
        return self._name

    @property
    def reserved(self):
        """If this is the root or session layer."""
        return self._is_reserved_layer

    @property
    def anonymous(self):
        """If this layer is anonymous layer."""
        if self._layer:
            return self._layer.anonymous
        else:
            return Sdf.Layer.IsAnonymousLayerIdentifier(self._identifier)

    @property
    def dirty(self):
        """If this layer has unsaved changes."""
        return self._is_dirty

    @dirty.setter
    def dirty(self, value):
        if self._is_dirty != value:
            self._is_dirty = value
            self._save_model._value_changed()

    @property
    def auto_reload(self):
        """Reload changes automatically."""
        return self._auto_reload

    @auto_reload.setter
    def auto_reload(self, value):
        if self._auto_reload != value:
            self._auto_reload = value

    @property
    def version(self):
        """
        The version of this layer. It only applies to omniverse layer.

        Returns:
            str
        """
        return ""

    @property
    def latest(self):
        """
        If this layer is latest. It only applies to omniverse layer.

        Returns:
            bool
        """
        if self.is_omni_live_path:
            return True

        return not self._outdated

    @property
    def live(self):
        """
        If this live is in live sync. It only applies to omniverse layer.

        Returns:
            bool
        """
        if not self._layer or not self.can_live_update:
            return False

        _, ext = os.path.splitext(self.identifier)
        if ext == '.live':
            return True

        return False

    @property
    def is_live_session_layer(self):
        """
        A layer is a live session layer if it's from a live session and it's the root layer
        of that session with extension .live.

        Returns:
            bool
        """

        return self._is_live_session_layer

    @property
    def base_layer(self):
        """
        If this layer is a live session layer, this property can be used to access its
        base layer item.

        Returns:
            :obj:'LayerItem'
        """

        if not self.is_live_session_layer:
            return None

        current_live_session = self._layers_live_syncing.get_live_session_for_live_layer(self.identifier)
        return self.model.get_layer_item_by_identifier(current_live_session.base_layer_identifier)

    @property
    def is_in_live_session(self):
        """
        A layer is in live session means it joins a live session. This is only true when it's
        the base layer of the live session. For live session layer, it's false.

        Returns:
            bool
        """

        return self._layers_live_syncing.is_layer_in_live_session(self.identifier)

    @property
    def live_session_layer(self):
        """
        If this layer is in live session, this property can be used to access its
        corresponding live session layer item.

        Returns:
            :obj:'LayerItem'
        """

        if not self.is_in_live_session:
            return None

        current_live_session = self._layers_live_syncing.get_current_live_session(self.identifier)
        return self.model.get_layer_item_by_identifier(current_live_session.root)

    @property
    def current_live_session(self):
        """
        If this layer is in a live session or it's a live session layer, it's to return the live session.

        Returns:
            :obj:'LiveSession'
        """
        if self._session_url:
            return self._layers_live_syncing.get_live_session_by_url(self._session_url)
        else:
            return self._layers_live_syncing.get_current_live_session(self.identifier)

    @property
    def muted_or_parent_muted(self):
        """
        If this layer is muted or its parent is muted.

        Returns:
            bool
        """
        parent = self
        while parent and not parent.muted:
            parent = parent.parent

        return not not parent

    @property
    def muted(self):
        """
        If this layer is muted..

        Returns:
            bool
        """
        stage = self._usd_context.get_stage()
        if not stage:
            return True

        return stage.IsLayerMuted(self._identifier)

    @muted.setter
    def muted(self, value):
        """
        Set this layer's is muteness.

        Args:
            value(bool): Muteness to set.
        """
        stage = self._usd_context.get_stage()
        if not stage:
            return True

        omni.kit.commands.execute("SetLayerMuteness", layer_identifier=self._identifier, muted=value)

    @property
    def globally_muted(self):
        """
        Globally mute is the mute value saved in custom data. The muteness of USD
        layer is dependent on the muteness scope (local or global). When it's in global mode,
        the muteness of USD layer is the same as this value.

        Returns:
            bool
        """
        return self._layers_state.is_layer_globally_muted(self._identifier)

    @property
    def locally_muted(self):
        """
        Local mute is the muteness when it's in local scope.

        Returns:
            bool
        """
        return self._layers_state.is_layer_locally_muted(self._identifier)

    @property
    def selected(self):
        """If this layer is selected in layer window."""
        return self._selected

    @selected.setter
    def selected(self, value):
        """
        Sets the selected state of the layer and notifies the model if the state changes.

        Args:
            value (bool): The new selected state to be set for the layer.
        """
        if self._selected != value and self.model:
            self._selected = value
            self.model._item_changed(self)

    @property
    def missing(self):
        """Indicates whether the layer is missing."""
        return self._is_missing_layer

    @missing.setter
    def missing(self, value):
        """
        Sets the missing state of the layer and triggers a model update.

        Args:
            value (bool): The new missing state to be set for the layer.
        """
        self._is_missing_layer = value
        self._name_model._value_changed()

    @property
    def editable(self):
        """Indicates whether the layer is writable."""
        return self._layers_state.is_layer_writable(self._identifier)

    @property
    def read_only_on_disk(self):
        """Indicates whether the layer is read-only on disk."""
        return self._is_read_only

    @property
    def can_live_update(self):
        """Indicates whether the layer supports live updates."""
        return self._is_omni_layer

    @property
    def edit_layer_in_auto_authoring_mode(self):
        """Indicates whether the layer is being edited in auto-authoring mode."""
        return self._is_edit_layer_in_auto_authoring_mode

    @edit_layer_in_auto_authoring_mode.setter
    def edit_layer_in_auto_authoring_mode(self, value):
        """
        Sets the edit mode state of the layer and notifies the model if the state changes.

        Args:
            value (bool): The new edit mode state to be set for the layer.
        """
        if not self.model.auto_authoring_mode and not self.model.spec_linking_mode:
            return

        old_value = self._is_edit_layer_in_auto_authoring_mode
        if old_value != value:
            self._is_edit_layer_in_auto_authoring_mode = value
            self.model._item_changed(self)

            # Clears parent flags.
            parent = self.parent
            while parent:
                parent._has_edit_layer = self._is_edit_layer_in_auto_authoring_mode
                parent._name_model._value_changed()
                parent = parent.parent

    @property
    def is_edit_target(self):
        """
        Returns whether layer item is the edit target.

        Returns:
            bool
        """
        return self._is_edit_target

    @is_edit_target.setter
    def is_edit_target(self, value):
        """
        Sets the value of the edit target property and notifies the model of the item change.

        Args:
            value (bool): The value to set for edit target property.
        """
        old_value = self._is_edit_target
        if old_value != value:
            self._is_edit_target = value
            self.model._item_changed(self)

            # Clears parent flags.
            parent = self.parent
            while parent:
                parent._has_edit_target = self._is_edit_target
                parent._name_model._value_changed()
                parent = parent.parent

    @property
    def has_child_edit_target(self):
        """
        Returns whether the layer item has a child with an edit target.

        Returns:
            bool: True if the layer item has a child with an edit target, False otherwise.
        """
        return self._has_edit_target

    @property
    def has_child_edit_layer(self):
        """
        Returns whether the layer item has a child with an edit layer.

        Returns:
            bool: True if the layer item has a child with an edit layer, False otherwise.
        """
        return self._has_edit_layer

    @property
    def locked(self):
        """
        Returns the locked status of the layer item.

        Returns:
            bool: True if the layer item is locked, False otherwise.
        """
        return self._locked_status

    @locked.setter
    def locked(self, value):
        """
        Sets the locked status of the layer item.

        Args:
            value (bool): The locked status to set for the layer item.
        """
        omni.kit.commands.execute(
            "LockLayer", layer_identifier=self._identifier, locked=value
        )

    @property
    def has_content(self):
        """
        Returns whether the layer item has content.

        Returns:
            bool: True if the layer item has content, False otherwise.
        """
        return self._has_content

    @property
    def add_sublayer(self, sublayer_item):
        """
        Adds a sublayer item to the layer item.

        Args:
            sublayer_item(:obj:'LayerItem'): The sublayer item to be added.
        """
        if sublayer_item not in self._sublayers:
            self._sublayers.append(sublayer_item)

    def __update_live_session_user_models(self, live_session):
        user_count = len(live_session.peer_users)
        self._first_live_session_user_model.peer_user = None
        self._second_live_session_user_model.peer_user = None
        if user_count >= 1:
            self._first_live_session_user_model.peer_user = live_session.peer_users[0]

        if user_count >= 2:
            self._second_live_session_user_model.peer_user = live_session.peer_users[1]

        self.model._item_changed(self)

    def update_flags(self):
        """ Updates the flag attributes of the layer item."""
        stage = self._usd_context.get_stage()
        if stage:
            if self.layer and self.layer.identifier != self._identifier:
                self._identifier = self.layer.identifier
                self._name_model._value_changed()
            self.edit_layer_in_auto_authoring_mode = self.model.default_edit_layer == self.identifier

            edit_target_identifier = LayerUtils.get_edit_target(stage)
            if edit_target_identifier:
                is_edit_target = self._identifier == edit_target_identifier
            else:
                is_edit_target = False
            self.is_edit_target = is_edit_target

            # If layer is from session layer tree or not.
            session_layer_identifier = stage.GetSessionLayer().identifier
            parent = self
            while parent and parent._identifier != session_layer_identifier:
                parent = parent.parent

            self._is_from_session_layer = not not parent

    def reload(self):
        """ Reload the layer of this layer item. """
        if self.layer:
            self.layer.Reload()

    def save(self, on_save_done=None):
        """
        Save the layer of this layer item.

        Args:
            on_save_done (Callable, optional): Callback function to be called when save is done.
                Signature is fn(bool, str, List[str])->None. Defaults to None.

        """
        if not self._layer:
            carb.log_warn(f"You cannot save a missing layer: {self._identifier}")
            return

        if self.is_live_session_layer:
            return

        success = self._layer.Save()
        if not success:
            error = f"Failed to save layer {self._identifier} because of permission issue."
        else:
            error = ""
        if on_save_done:
            on_save_done(success, error, [self._identifier])
        if success:
            LayerUtils.create_checkpoint(self._identifier, "")

    def _notify_muteness_changed(self):
        self._name_model._value_changed()
        self._local_mute_model._value_changed()
        self._global_mute_model._value_changed()
        self._save_model._value_changed()

        self._absolute_root_prim_spec.on_layer_muteness_changed()
        for sublayer in self.sublayers:
            sublayer._notify_muteness_changed()

    def on_muteness_changed(self):
        """ Handles the change of muteness state."""
        stage = self._usd_context.get_stage()
        if not stage:
            return

        muted = stage.IsLayerMuted(self._identifier)
        if self._old_mute_state != muted:
            self._old_mute_state = muted
            self._notify_muteness_changed()

    def on_live_session_state_changed(self):
        """ Handles the change of live session state."""
        live_session = self._layers_live_syncing.get_live_session_for_live_layer(self._identifier)
        is_live_session_layer = live_session is not None
        if is_live_session_layer:
            name = f"Session '{live_session.name}'"
            self._session_url = live_session.url
        else:
            name = self._layers_state.get_layer_name(self.identifier)

        if self._is_live_session_layer != is_live_session_layer:
            refresh_all = True
            self._is_live_session_layer = is_live_session_layer
            self.model._item_changed(self)
            # Refresh base layer
            if self.base_layer:
                self.model._item_changed(self.base_layer)
        else:
            refresh_all = False

        if self._name != name:
            self._name = name
            if not refresh_all:
                self._name_model._value_changed()

        if not refresh_all:
            self._live_update_model._value_changed()
            self._save_model._value_changed()

    def on_muteness_scope_changed(self):
        """ Handles the change of muteness scope. """
        stage = self._usd_context.get_stage()
        if not stage:
            return

        muted = stage.IsLayerMuted(self._identifier)
        if self._old_mute_state != muted:
            self.on_muteness_changed()
        else:
            self._local_mute_model._value_changed()
            self._global_mute_model._value_changed()

    def on_layer_lock_changed(self):
        """ Handles the change of layer lock status. """
        stage = self._usd_context.get_stage()
        if not stage:
            return

        locked = LayerUtils.get_layer_lock_status(stage.GetRootLayer(), self._identifier)
        is_read_only = self._layers_state.is_layer_readonly_on_disk(self._identifier)
        if locked != self._locked_status or is_read_only != self._is_read_only:
            self._locked_status = locked
            self._lock_model._value_changed()
            self._name_model._value_changed()
            self._save_model._value_changed()

    def on_layer_edit_mode_changed(self):
        """ Notifies all items in the prim specs cache about the change in layer edit mode."""
        for _, item in self._prim_specs_cache.items():
            item.on_layer_edit_mode_changed()

    def on_layer_outdate_state_changed(self):
        """Updates the layer's auto-reload and outdated status based on the current state."""
        auto_reload = self._layers_state.is_auto_reload_layer(self._identifier)
        if self._auto_reload != auto_reload:
            self._auto_reload = auto_reload

        outdated = self._layers_state.is_layer_outdated(self._identifier)
        if self._outdated != outdated:
            self._outdated = outdated
            self._latest_model._value_changed()
            self._name_model._value_changed()
            this_layer = self.model.get_layer_item_by_identifier(self._identifier)
            if this_layer:
                self.model._item_changed(this_layer)

    @Trace.TraceFunction
    def on_content_changed(self, changed_prim_spec_paths: List[str]):
        """
        Handles updates to content based on changes in prim spec paths.

        Args:
            changed_prim_spec_paths (List[str]): A list of string paths representing the prims that have changed.

        Returns:
            Tuple[Set[PrimSpecItem], Set[PrimSpecItem]]: Two sets containing updated prim spec items. The first set
            contains items where flags have been updated, and the second set contains items where children have been
            updated.
        """
        flags_update: Set[PrimSpecItem] = set([])
        children_update: Set[PrimSpecItem] = set([])

        if LayerSettings().show_layer_contents and changed_prim_spec_paths:
            carb.log_verbose(f"Handle changed {len(changed_prim_spec_paths)} prims for layer {self.identifier}.")

            # Finds its common path and loads its subtree
            all_parent_paths = [Sdf.Path(path) for path in changed_prim_spec_paths]
            common_prefix = all_parent_paths[0]
            for path in all_parent_paths[1:]:
                common_prefix = Sdf.Path.GetCommonPrefix(common_prefix, path)
            flag_updated_prims, children_updated_prims = self._load_prim_spec_subtree(common_prefix)
            flags_update.update(flag_updated_prims)
            children_update.update(children_updated_prims)

            carb.log_verbose(f"Handle changed prims for layer {self.identifier} done.")

        has_content = len(self._layer.rootPrims) > 0 if self._layer else False
        if self._has_content != has_content:
            self._has_content = has_content
            if self.is_live_session_layer:
                self._save_model._value_changed()

        return flags_update, children_update

    @Trace.TraceFunction
    def find_all_specs(self, paths: List[Sdf.Path]):
        """
        Find the child node with given name and return the list of all the
        parent nodes and the found node. It populates the children during
        search.

        Args:
            paths (List[Sdf.Path]): Paths of child prims to find.

        Returns:
            List[PrimSpecItem]
        """
        result = []
        for path in paths:
            prim_spec = self._layer.GetPrimAtPath(path)
            if not prim_spec:
                continue

            item, created = self._get_item_from_cache(path, True)

            # Create all parents
            if created:
                self._create_all_parent_items(item)

            result.append(item)

        return result

    def _create_all_parent_items(self, item: PrimSpecItem, filtered=False):
        parent_path = item.path.GetParentPath()
        while parent_path != Sdf.Path.absoluteRootPath:
            parent_item, created = self._get_item_from_cache(parent_path, True)
            if filtered:
                if parent_item.filtered:
                    break
                else:
                    parent_item.filtered = True
            elif not created:
                break

            parent_path = parent_path.GetParentPath()

    def prefilter(self, text: str):
        """
        Applies prefiltering with the given text.

        Args:
            text (str): The text to be prefiltered.
        """
        if not self._layer:
            return

        text = text.lower()

        # Clear all old states
        for _, child in self._prim_specs_cache.items():
            child.filtered = False

        self._prefilter_internal(text)

    @Trace.TraceFunction
    def _prefilter_internal(self, text: str):
        """Recursively mark items that meet the filtering rule"""

        # Has the search string in the name
        self._filtered = not text or text in self._name.lower()
        self._child_filtered = False
        for child in self._sublayers:
            child.prefilter(text)
            if not self._child_filtered:
                self._child_filtered = child._child_filtered or child._filtered

        if not text:
            return

        # FIXME: Don't use Sdf.PrimSpec.nameChildren to traverse whole stage as it's pretty slow.
        def on_prim_spec_path(prim_spec_path):
            if prim_spec_path.IsPropertyPath() or prim_spec_path == Sdf.Path.absoluteRootPath:
                return

            prim_spec_item, _ = self._get_item_from_cache(prim_spec_path)
            if prim_spec_item and prim_spec_item.filtered:
                return

            if text in prim_spec_path.name.lower():
                prim_spec_item, _ = self._get_item_from_cache(prim_spec_path, True)
                prim_spec_item.filtered = True
                self._child_filtered = True
                self._create_all_parent_items(prim_spec_item, True)

        self._layer.Traverse(Sdf.Path.absoluteRootPath, on_prim_spec_path)

    @Trace.TraceFunction
    def _load_prim_spec_subtree(self, prim_spec_path):
        carb.log_verbose(f"Load prim spec tree rooted from {prim_spec_path}")

        old_prim_specs = []
        flags_updated_prim_specs: Set[PrimSpecItem] = set([])
        children_updated_specs: Set[PrimSpecItem] = set([])

        if prim_spec_path == self._absolute_root_prim_spec.path:
            children_updated_specs.add(self._absolute_root_prim_spec)

        item, _ = self._get_item_from_cache(prim_spec_path)
        # This is new item, returning and refreshing it immediately if its parent is existed.
        if not item:
            parent, _ = self._get_item_from_cache(prim_spec_path.GetParentPath())
            if parent:
                children_updated_specs.add(parent)

            return flags_updated_prim_specs, children_updated_specs

        for path, item in self._prim_specs_cache.items():
            if item == self._absolute_root_prim_spec:
                continue

            if path.HasPrefix(prim_spec_path):
                old_prim_specs.append(item)

        if self._layer:
            for item in old_prim_specs:
                prim_spec = self._layer.GetPrimAtPath(item.path)
                if prim_spec:
                    flags_updated_prim_specs.add(item)
                    children_updated_specs.add(item)
                else:
                    # Prim spec is removed
                    parent = item.parent
                    if parent:
                        children_updated_specs.add(parent)

                    self._remove_cache_item(item.path)
        else:
            # Remove destroyed prim specs from cache.
            for item in old_prim_specs:
                parent_item = item.parent
                if parent_item:
                    children_updated_specs.add(parent_item)
                self._remove_cache_item(item.path)

        # Left old prim specs are destroyed ones.
        return flags_updated_prim_specs, children_updated_specs

    def update_spec_links_status(self, spec_paths: List[Union[str, Sdf.Path]]):
        """
        Updates the status of spec links for the provided spec paths.

        Args:
            spec_paths (List[Union[str, Sdf.Path]]): The list of spec paths to update.
        """
        if not spec_paths:
            return

        for spec_path in spec_paths:
            spec_path = Sdf.Path(spec_path)
            if not spec_path.IsPrimPath():
                continue

            spec, _ = self._get_item_from_cache(spec_path)
            if spec:
                spec.linked = self._layers_specs_linking.is_spec_linked(spec_path)

    def update_spec_locks_status(self, spec_paths: List[Union[str, Sdf.Path]]):
        """
        Updates the status of spec locks for the provided spec paths.

        Args:
            spec_paths (List[Union[str, Sdf.Path]]): The list of spec paths to update.
        """
        if not spec_paths:
            return

        for spec_path in spec_paths:
            spec_path = Sdf.Path(spec_path)
            if not spec_path.IsPrimPath():
                continue

            spec, _ = self._get_item_from_cache(spec_path)
            if spec:
                spec.locked = self._layers_specs_locking.is_spec_locked(spec_path)

    def get_item_value_model(self, column_id):
        """
        Returns the value model associated with the specified column ID.

        Args:
            column_id (int): The ID of the column.

        Returns:
            model(omni.ui.AbstractValueModel): The value model associated with the column.

        """
        if column_id == 0:
            return self._name_model
        elif column_id == 1:
            return self._live_update_model
        elif column_id == 2:
            return self._save_model
        elif column_id == 3:
            return self._local_mute_model
        else:
            if self.is_live_session_layer:
                if column_id == 4:
                    return self._first_live_session_user_model
                elif column_id == 5:
                    return self._second_live_session_user_model
                elif column_id == 6:
                    return self._ellipsis_model
            else:
                if column_id == 4:
                    return self._global_mute_model
                elif column_id == 5:
                    return self._latest_model
                elif column_id == 6:
                    return self._lock_model

        return None

    def _remove_cache_item(self, prim_spec_path):
        if prim_spec_path == Sdf.Path.absoluteRootPath:
            return False

        item = self._prim_specs_cache.pop(prim_spec_path, None)
        if item:
            item.destroy()

    def _clear_cache(self):
        for _, item in self._prim_specs_cache.items():
            item.destroy()
        self._prim_specs_cache.clear()

    def _get_item_from_cache(self, prim_spec_path: Sdf.Path, create=False):
        item = self._prim_specs_cache.get(prim_spec_path, None)
        created = False
        if not item and create:
            created = True
            item = PrimSpecItem(self._usd_context, prim_spec_path, self)
            self._prim_specs_cache[prim_spec_path] = item

        return item, created

    @Trace.TraceFunction
    def _get_item_children(self, prim_spec_path: Sdf.Path):
        item = self._prim_specs_cache.get(prim_spec_path, None)
        if not item or not item.prim_spec:
            return []

        all_children = []
        for child in item.prim_spec.nameChildren:
            child_item = self._prim_specs_cache.get(child.path, None)
            if not child_item:
                child_item = PrimSpecItem(self._usd_context, child.path, self)
                self._prim_specs_cache[child.path] = child_item

            all_children.append(child_item)

        return all_children

    def __repr__(self):
        return f"<Omni::UI Layer Item '{self.identifier}'>"

    def __str__(self):
        return f"{self.identifier}"
