# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import weakref
from typing import Any, Protocol

from ..xr_shutdown import XRShutdown

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Use these at your own risk, and forward-compatability is not supported


class XRSingletonType(Protocol):

    @classmethod
    def _delete_singleton(cls) -> None: ...

    @classmethod
    def get_singleton(cls) -> Any: ...


def XRSingleton():
    """
    A singleton decorator.

    Destructs each singleton when Extension is torn down.

    New functions:
        get_singleton(): gets the singleton
        delete_singleton(): deletes the singleton
    """

    def decorator(cls):
        instances = {}

        XRShutdown.add_shutdown_function(
            instances.clear, cls.__module__, "Ensure all decorated XRSingleton cached instances are cleared"
        )

        clscall_fn = cls.__call__

        @classmethod
        def _delete_singleton(cls):
            """
            This function deletes the singleton.
            For hot reload we need to be able to delete the singleton.
            """

            if cls in instances:
                del instances[cls]

        cls._delete_singleton = _delete_singleton

        @classmethod
        def get_singleton(cls, *args, **kwargs):
            """
            Get the singleton
            """

            if cls not in instances:
                instances[cls] = clscall_fn(*args, **kwargs)
                XRShutdown.assert_object_deletion_upon_shutdown(instances[cls])
                XRShutdown.add_shutdown_function(cls._delete_singleton, cls.__module__, "delete singleton")

            return weakref.proxy(instances[cls])

        cls.get_singleton = get_singleton

        return cls

    return decorator
