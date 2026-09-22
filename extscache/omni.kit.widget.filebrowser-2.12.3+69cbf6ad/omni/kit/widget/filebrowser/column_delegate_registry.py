# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Manage Registration of column delegates to be used by :obj:`FileBrowserTreeView`.
"""
__all__ = ["ColumnDelegateRegistry"]
from .singleton import Singleton
from .abstract_column_delegate import AbstractColumnDelegate
import carb
from typing import List, Callable, Optional

@Singleton
class ColumnDelegateRegistry:
    """
    Singleton that keeps all the column delegated. It's used to put custom
    columns to the content browser.
    """

    class _Event(list):
        """
        A list of callable objects. Calling an instance of this will cause a
        call to each item in the list in ascending order by index.
        """

        def __call__(self, *args, **kwargs):
            """Called when the instance is “called” as a function"""
            # Call all the saved functions
            for f in self:
                f(*args, **kwargs)

        def __repr__(self):
            """
            Called by the repr() built-in function to compute the “official”
            string representation of an object.
            """
            return f"Event({list.__repr__(self)})"

    class _EventSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, event, fn):
            """
            Save the function, the event, and add the function to the event.
            """
            self._fn = fn
            self._event = event
            event.append(self._fn)

        def __del__(self):
            """Called by GC."""
            self._event.remove(self._fn)

    class _ColumnDelegateSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, name, delegate):
            """
            Save name and type to the list.
            """
            self._name = name
            ColumnDelegateRegistry()._delegates[self._name] = delegate
            ColumnDelegateRegistry()._on_delegates_changed()

        def __del__(self):
            """Called by GC."""
            del ColumnDelegateRegistry()._delegates[self._name]
            ColumnDelegateRegistry()._on_delegates_changed()

    def __init__(self):
        self._delegates = {}
        self._names: List[str] = []
        self._on_delegates_changed = self._Event()
        self.__delegate_changed_sub = self.subscribe_delegate_changed(self.__delegate_changed)

    def register_column_delegate(self, name: str, delegate: AbstractColumnDelegate):
        """
        Add a new engine to the registry.

        Args:
        name: the name of the engine as it appears in the menu.
        delegate: the type derived from AbstractColumnDelegate. Content
                  browser will create an object of this type to build widgets
                  for the custom column.
        """
        if name in self._delegates:
            carb.log_warn("Unknown column delegate: {}".format(name))
            return

        return self._ColumnDelegateSubscription(name, delegate)

    def get_column_delegate_names(self):
        """Return all the column delegate names"""
        return self._names

    def get_column_delegate(self, name) -> Optional[AbstractColumnDelegate]:
        """Return the type of derived from AbstractColumnDelegate for the given name"""
        return self._delegates.get(name, None)

    def subscribe_delegate_changed(self, fn: Callable):
        """
        Return the object that will automatically unsubscribe when destroyed.
        """
        return self._EventSubscription(self._on_delegates_changed, fn)

    def __delegate_changed(self):
        self._names = list(sorted(self._delegates.keys()))
