__all__ = ["PrimSpecItem"]
import omni
import omni.ui as ui
import omni.usd

from omni.kit.usd.layers import LayerUtils
from typing import List, Set
from .models.prim_name_model import PrimNameModel
from .layer_settings import LayerSettings
from .globals import LayerGlobals
from pxr import Sdf, Trace


class PrimSpecSpecifier:
    DEF_ONLY = 1
    DEF_WITH_REFERENCE = 2
    DEF_WITH_PAYLOAD = 3
    OVER_ONLY = 4
    OVER_WITH_REFERENCE = 5
    OVER_WITH_PAYLOAD = 6
    UNKNOWN = 7


def get_prim_specifier(spec):
    if not spec:
        return PrimSpecSpecifier.UNKNOWN

    if spec.HasInfo(Sdf.PrimSpec.PayloadKey):
        op = spec.GetInfo(Sdf.PrimSpec.PayloadKey)
        items = []
        items = op.ApplyOperations(items)
        has_payload = len(items) > 0
    else:
        has_payload = False

    if spec.HasInfo(Sdf.PrimSpec.ReferencesKey):
        op = spec.GetInfo(Sdf.PrimSpec.ReferencesKey)
        items = []
        items = op.ApplyOperations(items)
        has_reference = len(items) > 0
    else:
        has_reference = False

    if spec.specifier == Sdf.SpecifierOver:
        if has_reference:
            return PrimSpecSpecifier.OVER_WITH_REFERENCE
        elif has_payload:
            return PrimSpecSpecifier.OVER_WITH_PAYLOAD
        else:
            return PrimSpecSpecifier.OVER_ONLY
    elif spec.specifier == Sdf.SpecifierDef:
        if has_reference:
            return PrimSpecSpecifier.DEF_WITH_REFERENCE
        elif has_payload:
            return PrimSpecSpecifier.DEF_WITH_PAYLOAD
        else:
            return PrimSpecSpecifier.DEF_ONLY
    else:
        return PrimSpecSpecifier.UNKNOWN


class PrimSpecItem(ui.AbstractItem):
    """A single AbstractItemModel item that represents a single prim"""

    def __init__(self, usd_context, path: Sdf.Path, layer_item):
        """Initializes a PrimSpecItem object.

        Args:
            usd_context (omni.usd.UsdContext): The USD context.
            path (Sdf.Path): The path to the prim.
            layer_item (LayerItem): The layer item.
        """
        super().__init__()
        self._usd_context = usd_context
        self._path: Sdf.Path = path
        self._layer_item = layer_item
        self._type_name: str = None
        self._name_model = None
        self._specifier: PrimSpecSpecifier = PrimSpecSpecifier.UNKNOWN
        self._has_missing_reference = False
        self._instanceable = False
        self._pending_to_update_flags = True
        self._flags_initialized = False

        # Link if it's existed
        self._links_initialized = False
        self._linked = False
        self._locked = False

        # Filtering
        self._filtered = False

    def _get_name_model(self):
        if not self._name_model:
            self._name_model = PrimNameModel(self)

        return self._name_model

    def destroy(self):
        """Destroys the item object."""
        if self._name_model:
            self._name_model.destroy()
        self._name_model = None
        self._layer_item = None
        self._flags_initialized = False

    @property
    def layer_item(self):
        """
        Gets the relate layer item.

        Returns:
            :obj:'LayerItem'
        """
        return self._layer_item

    def _initialize_link_and_lock_states(self):
        if not self._links_initialized:
            links = omni.kit.usd.layers.get_spec_layer_links(self._usd_context, self._path, False)
            if links:
                self._linked = True
            else:
                self._linked = False

            self._locked = omni.kit.usd.layers.is_spec_locked(self._usd_context, self._path)
            self._links_initialized = True

    @property
    def locked(self):
        """
        If the object is locked.

        Returns:
            bool: True if the object is locked, False otherwise.
        """
        self._initialize_link_and_lock_states()
        return self._locked

    @locked.setter
    def locked(self, value):
        """
        Setter method for the 'locked' property.

        Args:
            value (bool): The new value to set for the 'locked' property
        """
        self._initialize_link_and_lock_states()
        if value != self._locked:
            self._locked = value
            if self._name_model:
                self._name_model._value_changed()

    @property
    def linked(self):
        """
        If the object is linked.

        Returns:
            bool: True if the object is linked, False otherwise.
        """
        self._initialize_link_and_lock_states()
        return self._linked

    @linked.setter
    def linked(self, value):
        """
        Setter method for the 'linked' property.

        Args:
            value (bool): The new value to set for the 'linked' property
        """
        self._initialize_link_and_lock_states()
        if value != self._linked:
            self._linked = value
            if self._name_model:
                self._name_model._value_changed()

    @property
    def name(self):
        """Name of this prim spec in stage."""
        self.__update_flags_internal()
        return self._path.name

    @property
    def path(self):
        """Path of this prim spec in stage."""
        return self._path

    @property
    def prim_spec(self):
        """Handle of Sdf.PrimSpec."""
        self.__update_flags_internal()
        if self.layer:
            return self.layer.GetPrimAtPath(self._path)

        return None

    @property
    def layer(self):
        """Handle of Sdf.Layer this prim spec resides in."""
        return self._layer_item._layer

    @property
    def type_name(self):
        """Type name of this prim spec in stage."""
        self.__update_flags_internal()
        return self._type_name

    @property
    def children(self):
        """List of children."""

        # OM-45514: All prim_spec_items are maintained centralized inside layer item
        # to remove memory cost.
        return self._layer_item._get_item_children(self._path)

    @property
    def parent(self):
        """Parent spec."""

        if self._path == Sdf.Path.absoluteRootPath or not self._layer_item:
            return None

        parent_path = self._path.GetParentPath()
        found, _ = self._layer_item._get_item_from_cache(parent_path)

        return found

    @property
    def specifier(self):
        """Specifier of prim spec."""

        self.__update_flags_internal()
        return self._specifier

    @property
    def has_missing_reference(self):
        """If this prim spec includes missing references."""

        self.__update_flags_internal()
        return self._has_missing_reference

    @property
    def instanceable(self):
        """
        If this prim spec is instanceable.

        Returns:
            bool
        """
        self.__update_flags_internal()
        return self._instanceable

    @property
    def filtered(self):
        """
        If this prim spec is filtered in the search list.

        Returns:
            bool
        """
        return self._filtered

    @filtered.setter
    def filtered(self, value):
        """
        Setter method for the 'filtered' property.

        Args:
            value (bool): The new value to set for the 'filtered' property.
        """
        self._filtered = value

    @property
    def has_children(self):
        """
        If the object has children.

        Returns
            bool
        """
        return len(self.children) > 0

    def on_layer_muteness_changed(self):
        """Callback function for handling layer muteness changes."""
        if self._name_model:
            self._name_model._value_changed()
            for child in self.children:
                child.on_layer_muteness_changed()

    def on_layer_edit_mode_changed(self):
        """Callback function for handling layer edit mode changes."""
        self._links_initialized = False
        if self._name_model:
            self._name_model._value_changed()

    def update_flags(self):
        """ Updates the flags for this item object."""
        # Do lazy load only if it's necessary.
        # Since tree widget only populates visible items,
        # this is helpful for loading large stage.
        self._pending_to_update_flags = True

        if self._flags_initialized:
            # If it's to refresh flags, loading it immediately.
            self.__update_flags_internal()

    def __update_flags_internal(self):
        if not self._pending_to_update_flags:
            return True

        self._flags_initialized = True
        self._pending_to_update_flags = False
        layer = self._layer_item.layer
        stage = self._usd_context.get_stage()
        if not stage or not layer:
            return False

        prim_spec = self.prim_spec
        if not prim_spec:
            return False

        specifier = get_prim_specifier(prim_spec)

        changed = False
        if self._specifier != specifier:
            changed = True
            self._specifier = specifier

        prim = stage.GetPrimAtPath(self._path)
        if prim:
            type_name = prim.GetTypeName()
            instanceable = prim.GetMetadata("instanceable")
            if not instanceable:
                instanceable = False
        else:
            type_name = None
            instanceable = False

        if self._instanceable != instanceable:
            changed = True
            self._instanceable = instanceable

        if self._type_name != type_name:
            changed = True
            self._type_name = type_name

        if LayerSettings().show_missing_reference:
            has_missing_reference = self._has_missing_references(layer, prim_spec)
            if self._has_missing_reference != has_missing_reference:
                changed = True
                self._has_missing_reference = has_missing_reference

        if changed and self._name_model:
            self._name_model._value_changed()
            return True

        return False

    def _has_missing_reference_in_layer(self, layer_identifier):
        queue = [layer_identifier]
        accessed_layers = []
        while len(queue) > 0:
            identifier = queue.pop(0)
            if identifier in accessed_layers:
                continue

            accessed_layers.append(identifier)
            if LayerGlobals.is_layer_missing(identifier):
                return True

            layer = Sdf.Find(identifier)
            if not layer:
                LayerGlobals.add_missing_layer(identifier)
            if layer:
                for reference in layer.externalReferences:
                    if len(reference) > 0:
                        absolute_path = layer.ComputeAbsolutePath(reference)
                        queue.append(absolute_path)
            else:
                return True

        return False

    def _has_missing_references(self, layer, prim_spec):
        def has_missing_item(items):
            for item in items:
                if omni.usd.is_usd_readable_filetype(item.assetPath):
                    filename = layer.ComputeAbsolutePath(item.assetPath)
                    if self._has_missing_reference_in_layer(filename):
                        return True

            return False

        reference_list = prim_spec.referenceList
        # DON'T USE referencelist.prependedItems since it's VERY SLOW to
        # access.
        return has_missing_item(reference_list.GetAddedOrExplicitItems())

    def get_item_value_model(self, column_id):
        """
        Retrieves the value of an item in the model based on the given column ID.

        Args:
            column_id (int): The ID of the column for which to retrieve the item value.

        Returns:
            omni.ui.AbstractValueModel: The value of the item in the model.
        """

        if column_id == 0:
            return self._get_name_model()

        return None

    def __repr__(self):
        return f"<Omni::UI Prim Spec Item '{self._path}'>"

    def __str__(self):
        return f"{self._path}"
