# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from datetime import datetime
import abc


class AbstractSearchItem:
    """AbstractSearchItem represents a single file in the file browser."""

    @property
    def path(self):
        """Gets the full path that goes to usd when Drag and Drop.

        Returns:
            str: The full path as a string.
        """
        return ""

    @property
    def name(self):
        """Gets the name as it appears in the widget.

        Returns:
            str: The name of the search item as shown in the widget.
        """
        return ""

    @property
    def date(self):
        """Gets the date of the search item.

        Returns:
            datetime: The date of the search item.
        """
        # TODO: Grid View needs datatime, but Tree View needs a string. We need to make them the same.
        return datetime.now()

    @property
    def size(self):
        """Gets the size of the search item.

        Returns:
            int: The size of the search item.
        """
        # TODO: Grid View needs int, but Tree View needs a string. We need to make them the same.
        return 0

    @property
    def icon(self):
        """Gets the icon of the search item.

        Returns:
            object: The icon representing the search item.
        """
        pass

    @property
    def is_folder(self):
        """Gets whether the search item is a folder.

        Returns:
            bool: True if the search item is a folder, False otherwise.
        """
        pass

    def __getitem__(self, key):
        """Access to methods by text for _RedirectModel"""
        return getattr(self, key)


class SearchLifetimeObject(metaclass=abc.ABCMeta):
    """SearchLifetimeObject encapsulates a callback to be called when a search is finished.
    It is the responsibility of the implementers of AbstractSearchModel to keep the object argument alive until the search is completed if the search runs long.

    Args:
        callback (callable): The callback function to be executed when the search is finished.
    """

    def __init__(self, callback):
        """Initialize SearchLifetimeObject with a callback."""
        self._callback = callback

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Call the callback if it exists and then reset the callback to None."""
        if self._callback:
            self._callback()
        self._callback = None


class AbstractSearchModel(metaclass=abc.ABCMeta):
    """AbstractSearchModel represents the search results. It supports async mode. If the search engine requires time to process the request, it can return an empty list and perform the search in async mode. As soon as a result is ready, the model should call `self._item_changed()`. This will cause the view to reload the model. It is also possible to return the search result with portions.

    __init__ is usually called with the named arguments search_text and current_dir, and optionally a search_lifetime object.
    """

    class _Event(set):
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
            return f"Event({set.__repr__(self)})"

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
            event.add(self._fn)

        def __del__(self):
            """Called by GC."""
            self._event.remove(self._fn)

    def __init__(self):
        """Initializes the AbstractSearchModel instance. Sets up the internal event handling."""
        # TODO: begin_edit/end_edit
        self.__on_item_changed = self._Event()

    @property
    @abc.abstractmethod
    def items(self):
        """Gets the search model items.

        Returns:
            object: The collection of items representing the search results.
        """
        pass

    def destroy(self):
        """Cancels the current search operation."""
        pass

    def _item_changed(self, item=None):
        """Call the event object that has the list of functions"""
        self.__on_item_changed(item)

    def subscribe_item_changed(self, fn):
        """Returns the subscription object that unsubscribes automatically upon destruction.

        Args:
            fn (callable): Callback invoked when an item change occurs.
        """
        return self._EventSubscription(self.__on_item_changed, fn)
