__all__ = ["PrimSelectionPayload"]

import weakref
from typing import List

from pxr import Sdf, Usd


class PrimSelectionPayload:
    """A class to encapsulate the selection payload for a USD stage's prim paths.

    This class holds a weak reference to a USD stage and a list of SDF paths representing selected prims. It provides methods to interact with the selection data, including checking the length, iteration, indexing, and determining if the selection exceeds a predefined large selection count.

    Args:
        stage (weakref.ReferenceType(:obj:`Usd.Stage`)): A weak reference to the stage from which prims are selected.
        paths (List[:obj:`Sdf.Path`]): A list of SDF paths to selected prims.
    """

    def __init__(self, stage: weakref.ref[Usd.Stage], paths: List[Sdf.Path]):
        """Initializes a new instance of the PrimSelectionPayload."""
        self._stage = stage  # weakref
        self._payload = paths
        self._ignore_large_selection_override = False

        import omni.kit.property.usd

        self._large_selection_count = omni.kit.property.usd.get_large_selection_count()

    def __len__(self):
        # Ignore payload if stage is not valid anymore
        if self._stage is None or self._stage() is None:
            return 0

        return len(self._payload)

    # Forward calls to list to keep backward compatibility/easy access
    def __iter__(self):
        return self._payload.__iter__()

    def __getitem__(self, key):
        return self._payload.__getitem__(key)

    def __setitem__(self, key, value):  # pragma: no cover
        return self._payload.__setitem__(key, value)

    def __delitem__(self, key):  # pragma: no cover
        return self._payload.__delitem__(key)

    def __bool__(self):
        return self._stage is not None and self._stage() is not None and len(self._payload) > 0

    def get_stage(self):
        """Retrieves the stage associated with the payload.

        Returns:
            :obj:`weakref.ReferenceType(Usd.Stage)`: The stage if available, otherwise None."""
        return self._stage() if self._stage else None  # weakref -> ref

    def get_paths(self) -> List[Sdf.Path]:
        """Gets the list of paths stored in the payload.

        Returns:
            List[:obj:`Sdf.Path`]: The paths associated with this payload."""
        return self._payload

    def set_large_selection_override(self, state: bool):
        """Sets the override state for large selection handling.

        Args:
            state (bool): True to ignore large selection checks."""
        self._ignore_large_selection_override = state

    def get_large_selection_count(self):
        """Gets the count of items considered as a large selection.

        Returns:
            int: The count used to determine large selections."""
        return self._large_selection_count

    def is_large_selection(self) -> bool:
        """Determines if the current selection is considered large.

        Returns:
            bool: True if the selection is large, otherwise False."""
        if not self._ignore_large_selection_override:
            return bool(self._large_selection_count and len(self._payload) > self._large_selection_count)
        return False

    def cleanup_payload(self):
        """Removes any deleted prims from payload list and returns valid payload"""
        stage = self.get_stage()
        cleaned = False
        new_paths = []

        for path in self.get_paths():
            prim = stage.GetPrimAtPath(path)
            if prim:
                new_paths.append(path)
            else:
                cleaned = True

        if cleaned:
            return PrimSelectionPayload(weakref.ref(stage), new_paths)
        return self
