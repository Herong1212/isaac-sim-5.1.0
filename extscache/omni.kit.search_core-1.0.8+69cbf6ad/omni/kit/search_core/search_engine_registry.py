# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from .singleton import Singleton
from omni.kit.widget.nucleus_info import is_service_available


@Singleton
class SearchEngineRegistry:
    """
    Singleton that keeps all the search engines. It's used to put custom
    search engine to the content browser.
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

    class _EngineSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, name, model_type):
            """
            Save name and type to the list.
            """
            self._name = name
            SearchEngineRegistry()._engines[self._name] = model_type
            SearchEngineRegistry()._on_engines_changed()

        def __del__(self):
            """Called by GC."""
            del SearchEngineRegistry()._engines[self._name]
            SearchEngineRegistry()._on_engines_changed()

    def __init__(self):
        self._engines = {}
        self._on_engines_changed = self._Event()

    def register_search_model(self, name, model_type):
        """
        Add a new engine to the registry.

        name: the name of the engine as it appears in the menu.
        model_type: the type derived from AbstractSearchModel. Content
                    browser will create an object of this type when it needs
                    a new search.
        """
        if name in self._engines:
            # TODO: Warning
            return

        return self._EngineSubscription(name, model_type)

    def get_search_names(self):
        """Returns all the search names"""
        return list(sorted(self._engines.keys()))

    def get_available_search_names(self, server: str):
        """Returns available search names in given server"""
        search_names = list(sorted(self._engines.keys()))
        available_search_names = []
        for name in search_names:
            if "Service" not in name or is_service_available(name, server):
                available_search_names.append(name)
        return available_search_names

    def get_search_model(self, name):
        """Returns the type of derived from AbstractSearchModel for the given name"""
        return self._engines.get(name, None)

    def subscribe_engines_changed(self, fn):
        """
        Add the provided function to engines changed event subscription callbacks.
        Return the object that will automatically unsubscribe when destroyed.
        """
        return self._EventSubscription(self._on_engines_changed, fn)
