# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["_make_registry"]

from typing import Callable, Sequence


class _Factory:
    """A wrapper class for a factory function or class with an optional identifier.

    This class is used to represent a factory and provide a callable interface, along with a string
    representation, and a property to access the factory's identifier.

    Args:
        factory: Callable
            The factory function or class to be wrapped.
        factory_id: str
            The identifier for the factory. Defaults to the class name if not provided."""

    def __init__(self, factory: Callable, factory_id: str = None):
        """Initializes the internal factory instance with provided callable and identifier.

        Args:
            factory (Callable): The factory function or class to be wrapped.
            factory_id (str, optional): The identifier for the factory. If not provided, the class name of the factory will be used.
        """
        self.__factory = factory
        self.__factory_id = factory_id if factory_id else factory.__class__.__name__

    def __call__(self, *args, **kwargs):
        """Allows the _Factory instance to be called like a function, which calls the wrapped factory.

        Args:
            *args: Variable length argument list to be passed to the factory callable.
            **kwargs: Arbitrary keyword arguments to be passed to the factory callable.

        Returns:
            The result of the factory callable.
        """
        return self.__factory(*args, **kwargs)

    def __repr__(self) -> str:
        """Generates a string representation of the _Factory instance, including its identifier.

        Returns:
            str: A string representation of the _Factory instance.
        """
        return f"<class {self.__class__.__name__} {self.__factory_id}>"

    @property
    def factory_id(self):
        """Property that returns the identifier of the factory.

        Returns:
            The factory identifier.
        """
        return self.__factory_id


def _make_registry():
    """Creates and returns the _Registry class.

    This function constructs a nested _Registry class that is used to manage the registration and deregistration of
    viewport factories. It provides mechanisms to add or remove factories, invoke callbacks when factories are loaded
    or unloaded, and retrieve factories in a specified order.

    Returns:
        _Registry: A class capable of registering and deregistering viewport factories, managing callbacks for factory
            load events, and providing ordered access to the factories.
    """

    def invoke_load_callback(callback, recorded_known, factories):
        """Invokes the provided callback function for each factory object that is not already recorded.
        This internal function iterates over a list of factory objects, checks if they are in the set of
        recorded known factories, and if not, adds them to the set and invokes the callback with the factory
        object and a boolean flag indicating the factory is being loaded (True).

        Args:
            callback (Callable): The callback function to be invoked for each new factory object.
            recorded_known (set): A set of known factory objects that have already been processed.
            factories (list): A list of factory objects to be processed.
        """
        for fac_object in factories:
            if fac_object not in recorded_known:
                recorded_known.add(fac_object)
                callback(fac_object, True)

    class _Registry:
        """A class to manage the registration and deregistration of viewport factories.

        This class provides functionality to add or remove factories, invoke callbacks when factories are loaded or unloaded, and retrieve factories in a specified order.
        """

        __g_registered_factories = []
        __g_registered_callbacks = {}

        @classmethod
        def add_notifier(cls, callback):
            """Registers a callback to be invoked when a new factory is added.

            The callback will be invoked immediately for all currently registered factories.

            Args:
                callback (Callable): The callback function to be registered.
            """
            # Invoke the callback for all currently registered scenes
            cls.__g_registered_callbacks[callback] = set()
            invoke_load_callback(callback, cls.__g_registered_callbacks[callback], cls.__g_registered_factories)

        @classmethod
        def remove_notifier(cls, callback):
            """Removes a previously registered callback.

            Args:
                callback (Callable): The callback function to be unregistered.
            """
            try:
                del cls.__g_registered_callbacks[callback]
            except KeyError:
                pass

        @classmethod
        def ordered_factories(
            cls, order: Sequence[str], append_unkown: bool = True, ignore_unknown: Sequence[str] = tuple()
        ):
            """Returns an ordered list of factory identifiers and corresponding factory instances.

            Args:
                order (Sequence[str]): A sequence of factory identifiers specifying the desired order.
                append_unkown (bool, optional): If True, append factories not found in `order` to the end of the list.
                ignore_unknown (Sequence[str], optional): A sequence of factory identifiers to exclude from the appended unknowns.

            Returns:
                List[Tuple[str, _Factory]]: An ordered list of tuples containing factory identifiers and the corresponding factory instances.
            """
            ordered = []
            known = set()

            def find_factory(factory_id):
                known.add(factory_id)
                for fact_obj in cls.__g_registered_factories:
                    if fact_obj.factory_id == factory_id:
                        return fact_obj
                return None

            for factory_id in order:
                ordered.append((factory_id, find_factory(factory_id)))
            if append_unkown:
                for fact_obj in cls.__g_registered_factories:
                    if (fact_obj.factory_id not in known) and (fact_obj.factory_id not in ignore_unknown):
                        ordered.append((fact_obj.factory_id, fact_obj))
            return ordered

        def __init__(self, factory, factory_id: str = None):
            """Initializes a registry entry for the given factory.

            This will also invoke the load callbacks for the new factory.

            Args:
                factory (Callable): The factory function or class to register.
                factory_id (str, optional): The identifier for the factory. If not provided, the class name of the factory will be used.
            """
            # Save the types for de-registration
            self.__factory = _Factory(factory, factory_id)
            # Record them in the global-list for notifiers registered later
            self.__g_registered_factories.append(self.__factory)
            # Invoke all callbacks for new items
            for callback, recorded_known in self.__g_registered_callbacks.items():
                invoke_load_callback(callback, recorded_known, [self.__factory])

        def destroy(self):
            """Removes the factory from the registry and invokes the unload callbacks.

            After calling this method, the factory will no longer be registered and callbacks will be notified of its removal.
            """
            fac_object = self.__factory
            self.__factory = None
            try:
                self.__g_registered_factories.remove(fac_object)
            except (ValueError, KeyError):
                pass
            for callback, recorded_known in self.__g_registered_callbacks.items():
                if fac_object in recorded_known:
                    recorded_known.remove(fac_object)
                    try:
                        callback(fac_object, False)
                    except Exception:
                        import carb
                        import traceback

                        carb.log_error(
                            f"Error unloading {fac_object.factory_id} with {callback}. Traceback:\n{traceback.format_exc()}"
                        )

        def __del__(self):
            """Destructor for the _Registry instance.

            Ensures that the factory is properly destroyed and callbacks are notified upon the instance's deletion.
            """
            self.destroy()

    return _Registry
