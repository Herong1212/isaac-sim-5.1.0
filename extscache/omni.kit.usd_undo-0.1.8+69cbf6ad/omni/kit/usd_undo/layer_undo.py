"""Contains the class of UsdLayerUndo and UsdEditTargetUndo"""

from pxr import Sdf, Usd


class UsdLayerUndo:
    """A class for managing undo operations on USD layers.

    This class encapsulates the functionality to reserve changes, perform undo operations, and reset the undo stack for a USD layer. It is designed to work with Sdf.Layer objects, allowing for precise control over the changes made to the layer.

    Args:
        layer: Sdf.Layer
            The Sdf.Layer object on which the undo operations are performed."""

    class Key:
        """A class to represent a key in the undo system for USD layers.

        Args:
            path: Sdf.Path
                The path associated with the change to be undone.
            info: Any
                Optional information associated with the path, such as a specific attribute or metadata key."""

        def __init__(self, path, info):
            self.path = path
            self.info = info

    def __init__(self, layer: Sdf.Layer):
        """Initializes the UsdLayerUndo instance.

        Args:
            layer (Sdf.Layer): The USD layer to be managed by this undo instance."""
        self._layer = layer
        self._layer_id = self._layer.identifier
        self.reset()

    def reserve(self, path: Sdf.Path, info=None):
        """Reserves the changes made to the path in the USD layer to allow undo operations.

        Args:
            path (Sdf.Path): The path in the USD layer to reserve.
            info (optional): Additional information about the reservation, default is None."""
        # Check if it's included by any reserved paths
        path = Sdf.Path(path)
        for added_key in self._paths:
            if path.HasPrefix(added_key.path) and added_key.info is None:
                return

        # Check if it includes any reserved paths
        if info is None:
            for added_key in self._paths:
                if added_key.path.HasPrefix(path):
                    self._paths.pop(added_key)

        # If it doesn't exist, it's new data. No need to reserve anything.
        new_data = None
        spec = self._layer.GetObjectAtPath(path)
        if spec is None:
            new_data = True
        elif info is None:
            new_data = False
        else:
            info_value = spec.GetInfo(info)

            if info_value is not None:
                if info_value.__class__.__name__.endswith("ListOp"):
                    if not (
                        info_value.explicitItems
                        or info_value.addedItems
                        or info_value.prependedItems
                        or info_value.appendedItems
                        or info_value.deletedItems
                        or info_value.orderedItems
                    ):
                        info_value = None

            new_data = info_value is None

        key = self.Key(path, info)
        self._paths[key] = new_data
        if new_data:
            return

        # Reserve existing data
        def create_spec(path: Sdf.Path):
            """Creates a spec for the given path in the layer.

            This method is used internally to create a new spec for a given path within the layer if it does not already exist. It handles the creation of both Prim specs and Variant specs based on the type of the path.

            Args:
                path (Sdf.Path): The Sdf.Path for which to create the spec.

            Returns:
                The newly created spec (either a Prim spec, a VariantSet spec, or a Variant spec), or the existing parent spec if the path is already present in the layer.

            Raises:
                Exception: If the path is a property path, since property info creation is not supported."""
            parent = self._reserve_layer.GetObjectAtPath(path.GetParentPath())
            if parent is None:
                parent = create_spec(path.GetParentPath())

            if path.IsPrimPath():
                return Sdf.CreatePrimInLayer(self._reserve_layer, path)
            elif path.IsPrimVariantSelectionPath():
                variant_set_name, variant_name = path.GetVariantSelection()
                variant_set = Sdf.VariantSetSpec(parent, variant_set_name)
                if variant_name:
                    return Sdf.VariantSpec(variant_set, variant_name)
                else:
                    return variant_set

        if info is None:
            create_spec(path)
            Sdf.CopySpec(self._layer, path, self._reserve_layer, path)
        else:
            # We must know attribute type to create it in layer. So we don't handle it here.
            if path.IsPropertyPath():
                raise Exception("Property info is not supported.")

            reserve_spec = create_spec(path)
            reserve_spec.SetInfo(info, info_value)

    def undo(self):
        """Undoes the last set of changes reserved by the reserve method.

        Raises:
            Exception: If the layer cannot be found."""
        if not self._layer:
            self._layer = Sdf.Layer.Find(self._layer_id)

        if self._layer is None:
            raise Exception(f"Layer {self._layer_id} can not be found.")

        with Sdf.ChangeBlock():
            batch_edit = Sdf.BatchNamespaceEdit()
            for key, new_data in self._paths.items():
                spec = self._layer.GetObjectAtPath(key.path)
                reserve_spec = self._reserve_layer.GetObjectAtPath(key.path)

                if new_data:
                    if spec:
                        if key.info is None:
                            if isinstance(spec, Sdf.VariantSetSpec):
                                del spec.owner.variantSets[spec.name]
                            elif isinstance(spec, Sdf.VariantSpec):
                                spec.owner.RemoveVariant(spec)
                            else:
                                batch_edit.Add(Sdf.NamespaceEdit.Remove(key.path))
                        else:
                            spec.ClearInfo(key.info)
                elif key.info is None:
                    # Restore spec
                    Sdf.CopySpec(self._reserve_layer, key.path, self._layer, key.path)
                else:
                    # Restore spec info
                    spec.SetInfo(key.info, reserve_spec.GetInfo(key.info))

            self._layer.Apply(batch_edit)

    def reset(self):
        """Resets the internal state of the UsdLayerUndo instance, clearing any changes reserved."""
        self._reserve_layer = Sdf.Layer.CreateAnonymous()
        self._paths = {}


class UsdEditTargetUndo(UsdLayerUndo):
    """A class for managing undo operations on a USD edit target.

    This class provides methods to reserve and undo changes made to a USD layer through an edit target.

    Args:
        edit_target: Usd.EditTarget
            The edit target to be managed for undo operations."""

    def __init__(self, edit_target: Usd.EditTarget):
        """Initializes a UsdEditTargetUndo instance with the given edit target.

        Args:
            edit_target (Usd.EditTarget): The edit target to be managed for undo operations."""
        self._edit_target = edit_target

        super().__init__(self._edit_target.GetLayer())

    def reserve(self, path: Sdf.Path, info=None):
        """Reserves the specified path and info for undo, mapped to the edit target's namespace.

        Args:
            path (Sdf.Path): The path to be reserved.
            info (str, optional): The info key to be reserved. If None, the entire spec is reserved."""
        super().reserve(self._edit_target.MapToSpecPath(path), info)
