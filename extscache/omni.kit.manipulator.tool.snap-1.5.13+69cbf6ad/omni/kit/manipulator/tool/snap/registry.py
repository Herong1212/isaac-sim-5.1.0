# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Callable, Dict, Type

import carb.settings

if TYPE_CHECKING:
    from .provider import SnapProvider


class SnapProviderRegistry:
    """A registry for managing SnapProvider instances as a singleton.

    This class handles the registration and unregistration of SnapProvider classes,
    which are used for snapping objects in a 3D environment. It allows subscribing and unsubscribing to registry change events,
    enabling other parts of the application to react to changes in the SnapProvider ecosystem.
    """

    __instance: SnapProviderRegistry = None

    @classmethod
    def get_instance(cls) -> SnapProviderRegistry:
        """Gets the singleton instance of the SnapProviderRegistry.

        Returns:
            SnapProviderRegistry: The singleton instance of the registry."""
        return cls.__instance

    def __init__(self):
        """Initializes the SnapProviderRegistry singleton instance.

        Raises:
            RuntimeError: If an instance already exists."""
        if self.__instance is not None:
            raise RuntimeError("Only one instance of SnapProviderRegistry is allowed")

        self._providers: Dict[str, Type[SnapProvider]] = {}
        self._change_subscribers: Dict[int, Callable] = {}
        self._next_change_subscriber_id: int = 1
        self._settings = carb.settings.get_settings()

        SnapProviderRegistry.__instance = self

    def destroy(self):
        """Destroys the singleton instance of the SnapProviderRegistry."""
        SnapProviderRegistry.__instance = None

    def __del__(self):
        self.destroy()

    @property
    def providers(self) -> Dict[str, Type[SnapProvider]]:
        """Gets all provider classes.

        Returns:
            Dict[str, Type[SnapProvider]]: A dictionary mapping provider names to their respective SnapProvider classes.
        """
        return self._providers

    def get_provider_class_by_name(self, name: str) -> Type[SnapProvider]:
        """Retrieves a registered SnapProvider class by its name.

        Args:
            name (str): The name of the provider class to retrieve.

        Returns:
            Type[SnapProvider] or None: The provider class if found, otherwise None."""
        return self._providers.get(name, None)

    def register_provider(self, provider_class: Type[SnapProvider]):
        """Registers a new SnapProvider class to the registry.

        Args:
            provider_class (Type[SnapProvider]): The class of the provider to be registered.

        Raises:
            ValueError: If a provider with the same name is already registered."""
        id = provider_class.get_name()
        if id in self._providers:
            raise ValueError(f"{id} already exist!")

        self._providers[id] = provider_class
        self._notify_registry_changed()

    def unregister_provider(self, provider_class: Type[SnapProvider]):
        """Unregisters an existing SnapProvider class from the registry.

        Args:
            provider_class (Type[SnapProvider]): The class of the provider to be unregistered."""
        id = provider_class.get_name()
        self._providers.pop(id, None)
        self._notify_registry_changed()

    def subscribe_to_registry_change(self, callback: Callable[[], None]) -> int:
        """Subscribes a callback to the event that is triggered when the provider registry changes.

        Args:
            callback (Callable[[], None]): The callback to be invoked when the registry changes. It is called immediately before function returns.

        Returns:
            int: An ID that can be used to unsubscribe the callback later."""
        id = self._next_change_subscriber_id
        self._next_change_subscriber_id += 1
        self._change_subscribers[id] = callback
        self._notify_registry_changed(callback)
        return id

    def unsubscribe_to_registry_change(self, id: int):
        """Unsubscribes a previously subscribed callback from the registry change event.

        Args:
            id (int): The ID returned by subscribe_to_registry_change when the callback was initially subscribed."""
        self._change_subscribers.pop(id)

    def _notify_registry_changed(self, callback: Callable[[], None] = None):
        """Notifies all subscribed callbacks that the registry has changed. If a specific callback is provided, only that callback is notified.

        Args:
            callback (Callable[[], None], optional): A specific callback to notify. If not provided, all subscribers are notified.
        """
        if callback:
            callback()
        else:
            for sub in self._change_subscribers.values():
                sub()


class RegistrationHelper:
    """A helper class for registering provider classes.

    This class is responsible for discovering and registering all provider classes that inherit from a specified base class within a given module. It ensures that all providers are registered upon initialization and unregistered when destroyed.

    Args:
        module_name: str
            Name of the module where provider classes are located.
        base_class: Type
            The base class type that all providers should inherit from."""

    def __init__(self, module_name: str, base_class: Type):
        """Initializes the RegistrationHelper and registers all provider classes that inherit from the specified base class within the given module.

        Args:
            module_name (str): The name of the module where provider classes are located.
            base_class (Type): The base class type that all providers should inherit from."""
        self._registry = SnapProviderRegistry.get_instance()
        self._provider_classes = self._get_all_provider_classes(module_name, base_class)
        self._registered = False

        for provider_class in self._provider_classes:
            self._registry.register_provider(provider_class)
        self._registered = True

    def destroy(self):
        """Unregisters all previously registered provider classes and marks the helper as not registered."""
        if self._registered:
            for provider_class in self._provider_classes:
                self._registry.unregister_provider(provider_class)
            self._registered = False

    def __del__(self):
        """Ensures that the `destroy` method is called upon the deletion of an instance."""
        self.destroy()

    def _get_all_provider_classes(self, module_name: str, base_class: Type):
        """Internal method to retrieve all provider classes from a module that inherit from a specified base class.

        Args:
            module_name (str): The name of the module to search for provider classes.
            base_class (Type): The base class type to compare against.

        Returns:
            list: A list of provider class types that were found in the module."""
        classes = []
        module = sys.modules[module_name]
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, base_class) and obj is not base_class:
                classes.append(obj)

        return classes
