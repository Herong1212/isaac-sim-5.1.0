# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines the PrimDataAccessorRegistry class, which manages the registration and unregistration of data accessor functions for specific data tags."""


from __future__ import annotations

import carb.events
import omni.kit.app

from .settings_constants import DataRegistryEventTypes as da_ev_c


# from omni.kit.viewport.manipulator.transform import DataAccessorRegistry
# class PrimDataAccessorRegistry(DataAccessorRegistry):
class PrimDataAccessorRegistry:
    """A registry for managing data accessors within the application.

    This class serves as a central hub to register and unregister data accessors, which are functions responsible for manipulating and accessing data associated with specific tags. It provides methods to add and remove data accessors, retrieve the current list of registered data accessors, and manage an event stream to notify about changes in data accessor registration.

    The class maintains an internal dictionary to map data tags to their corresponding data accessor functions. It also holds an event stream object to emit events when data accessors are added or removed.
    """

    def __init__(self):
        """Initializes the PrimDataAccessorRegistry with default values."""
        self._data_accessors_func = {}
        self._event_stream = carb.events.get_events_interface().create_event_stream()

    def get_event_stream(self):
        """Returns the event stream associated with the registry."""
        return self._event_stream

    def register_data_accessor(self, func, data_tag):
        """Registers a new data accessor function.

        Args:
            func (Callable): The function to be registered as a data accessor.
            data_tag (str): Identifier for the data accessor."""
        self._data_accessors_func[data_tag] = func
        self._event_stream.dispatch(da_ev_c.DATA_ACCESSOR_ADDED, payload={"data_tag": data_tag})

    def unregister_data_accessor(self, data_tag):
        """Unregisters an existing data accessor.

        Args:
            data_tag (str): Identifier for the data accessor to be unregistered."""
        if data_tag in self._data_accessors_func:
            del self._data_accessors_func[data_tag]
        self._event_stream.dispatch(da_ev_c.DATA_ACCESSOR_REMOVED, payload={"data_tag": data_tag})

    def get_data_accessors_func(self):
        """Returns the dictionary of registered data accessor functions."""
        return self._data_accessors_func

    def destroy(self):
        """Cleans up resources and references, preparing the registry for destruction."""
        self._data_accessors_func = None
        self._event_stream = None
