# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageColumnDelegateRegistry"]

from .abstract_stage_column_delegate import AbstractStageColumnDelegate
from .event import Event
from .event import EventSubscription
from .singleton import Singleton
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
import carb


class StageColumnDelegateRegistryBase:
    """Base class for delegate registry"""

    def __init__(self):
        self._delegates: Dict[str, Callable[[], AbstractStageColumnDelegate]] = {}
        self._names: List[str] = []
        self._on_delegates_changed = Event()
        self.__delegate_changed_sub = self.subscribe_delegate_changed(self.__delegate_changed)

    def register_column_delegate(self, name: str, delegate: Callable[[], AbstractStageColumnDelegate]):
        ...

    def get_column_delegate_names(self) -> List[str]:
        """Returns all the column delegate names"""
        return self._names

    def get_column_delegate(self, name: str) -> Optional[Callable[[], AbstractStageColumnDelegate]]:
        """Returns the type of derived from AbstractColumnDelegate for the given name"""
        return self._delegates.get(name, None)

    def subscribe_delegate_changed(self, fn: Callable[[], None]) -> EventSubscription:
        """
        Return the object that will automatically unsubscribe when destroyed.
        """
        return EventSubscription(self._on_delegates_changed, fn)

    def __delegate_changed(self):
        self._names = list(sorted(self._delegates.keys()))



@Singleton
class StageColumnDelegateRegistry(StageColumnDelegateRegistryBase):
    """
    Singleton registry object that keeps all the column delegates. Used for adding custom columns to the stage widget.
    """

    class _ColumnDelegateSubscription:
        """
        Event subscription.

        Event has callback while this object exists.
        """

        def __init__(self, name, delegate):
            """
            Save name and type to the list.
            """
            self._name = name
            StageColumnDelegateRegistry()._delegates[self._name] = delegate
            StageColumnDelegateRegistry()._on_delegates_changed()

        def __del__(self):
            """Called by GC."""
            del StageColumnDelegateRegistry()._delegates[self._name]
            StageColumnDelegateRegistry()._on_delegates_changed()

    def register_column_delegate(self, name: str, delegate: Callable[[], AbstractStageColumnDelegate]) -> _ColumnDelegateSubscription:
        """
        Add a new column delegate to the registry.

        Args:
            name (str): the name of the engine as it appears in the menu.
            delegate (Callable[[], AbstractStageColumnDelegate]): the type derived from AbstractColumnDelegate. Stage
                widget will create an object of this type when building widgets for the custom column.
        Returns:
            StageColumnDelegateRegistry: The subscription object.
        """
        if name in self._delegates:
            carb.log_warn(f"Column delegate with name {name} is registered already.")
            return

        return self._ColumnDelegateSubscription(name, delegate)
