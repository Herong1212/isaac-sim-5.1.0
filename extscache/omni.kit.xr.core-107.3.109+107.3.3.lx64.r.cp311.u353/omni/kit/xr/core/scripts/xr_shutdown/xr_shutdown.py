# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import weakref
from collections.abc import Iterable
from typing import Any, Callable, List, Tuple

import carb.settings


class XRShutdown:
    _weak_object_tracking_set: dict
    _shutdown_tasks: list

    @classmethod
    def _get_shutdown_tasks_list(cls) -> List[Tuple[Callable[[], Any], str, str]]:
        """
        Gets a list of all shutdown tasks.

        Should not be used unless you know what you're doing
        """
        # Workaround - store this array on XRCore instead of locally in case of import/reload issues
        if not hasattr(cls, "_shutdown_tasks"):
            cls._shutdown_tasks = []

        return cls._shutdown_tasks

    @classmethod
    def _get_weak_object_tracking_set(cls, module: str) -> weakref.WeakSet:
        """
        Gets a list of all objects weak-tracked to assert they have been deleted on shutdown
        """
        # Workaround - store this array on XRCore instead of locally in case of import/reload issues
        if not hasattr(cls, "_weak_object_tracking_set"):
            cls._weak_object_tracking_set = {}

        if module not in cls._weak_object_tracking_set.keys():
            cls._weak_object_tracking_set[module] = weakref.WeakSet()

        return cls._weak_object_tracking_set[module]

    @classmethod
    def add_shutdown_function(cls, fn: Callable[[], Any], module: str, description: str) -> None:
        """
        Adds a new task (and optional description) to the list of operations upon shutdown.

        Examples include releasing singletons or ensuring the scene is in a clean state

        Args:
            fn: a function that is called upon shutdown
            description: an optional string useful for debug
        """
        cls._get_shutdown_tasks_list().append((fn, module, description))

    @classmethod
    def assert_object_deletion_upon_shutdown(cls, obj: Any):
        """
        Track an object to assert that it does not exist when shutdown occurs

        Args:
            obj: an object that should be asserted to have been cleaned up before shutdown
        """
        cls._get_weak_object_tracking_set(obj.__class__.__module__).add(obj)

    @classmethod
    def run_shutdown_functions(cls, module: str):
        """
        Runs and clears all registered shutdown functions.

        Note that these are run in reverse order, for symmetry
        """

        if hasattr(cls, "_shutdown_tasks"):

            keep_list = []
            delete_list = []
            for item in cls._shutdown_tasks:
                if item[1].startswith(module):
                    delete_list.append(item)
                else:
                    keep_list.append(item)

            cls._shutdown_tasks = keep_list

            for shutdown_function in reversed(delete_list):
                try:
                    shutdown_function[0]()
                except Exception:
                    import traceback

                    carb.log_error("An XR component was unable to shutdown\n" + traceback.format_exc())

        if hasattr(cls, "_weak_object_tracking_set"):
            import gc

            for path in cls._weak_object_tracking_set:

                object_set = cls._weak_object_tracking_set[path]
                if path.startswith(module):
                    for obj in object_set:
                        carb.log_error("A python XR object was not deleted before shutdown:  " + str(obj))
                        carb.log_warn("Referred to by:")
                        for referrer in gc.get_referrers(obj):
                            if isinstance(referrer, Iterable):
                                carb.log_warn(" - [iterable object]: " + str(type(referrer)))
                                for subreferrer in gc.get_referrers(referrer):
                                    carb.log_warn("   - " + str(subreferrer))
                            else:
                                carb.log_warn(" - " + str(referrer))
                    object_set.clear()
            gc.collect()
