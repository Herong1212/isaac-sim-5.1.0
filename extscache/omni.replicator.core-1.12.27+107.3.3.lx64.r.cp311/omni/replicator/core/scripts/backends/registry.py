# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, List, Union

import carb

from .base import BaseBackend


class BackendRegistry:
    """Registry of backends

    Backends define how to read/write blobs of bytes data.
    """

    _backends = {}

    @classmethod
    def register_backend(cls, backend: BaseBackend) -> None:
        """Register a backend.

        Args:
            backend: Backend to register, must be derived from BaseBackend. The backend is registered
                under its class name.

        Example:
            >>> import omni.replicator.core as rep
            >>> class PassBackend(rep.backends.BaseBackend):
            ...     def __init__(self, **kwargs):
            ...         pass
            ...     def write_blob(self, **kwargs):
            ...         pass
            ...     def read_blob(self, **kwargs):
            ...         pass
            >>> rep.backends.BackendRegistry.register_backend(PassBackend)
        """
        name = backend.get_name()

        if name in cls._backends:
            carb.log_warn(f"Backend {name} is already registered, overwriting backend")
            cls._backends.pop(name)

        cls._backends[name] = backend

    @classmethod
    def unregister_backend(cls, backend: BaseBackend) -> None:
        """Unregister a backend.

        Args:
            name: Name of backend to unregister

        Example:
            >>> import omni.replicator.core as rep
            >>> class PassBackend(rep.backends.BaseBackend):
            ...     def __init__(self, **kwargs):
            ...         pass
            ...     def write_blob(self, **kwargs):
            ...         pass
            ...     def read_blob(self, **kwargs):
            ...         pass
            >>> rep.backends.BackendRegistry.register_backend(PassBackend)
            >>> rep.backends.BackendRegistry.unregister_backend("PassBackend")
        """
        if isinstance(backend, str):
            name = backend
        elif isinstance(backend, BaseBackend):
            name = backend.get_name()
        else:
            raise ValueError(
                f"Unable to unregister backend of type {type(backend)}, backend must be specified as a string name or as a BaseBackend object."
            )
        try:
            del cls._backends[name]
        except KeyError:
            carb.log_warn(f"No registered backend found with name `{name}`.")

    @classmethod
    def get_registered_backends(cls) -> List:
        """Returns a list of registered backends.

        Returns:
            List of the names of registered backends.

        Example:
            >>> import omni.replicator.core as rep
            >>> registered_backends = rep.backends.BackendRegistry.get_registered_backends()
        """
        return list(cls._backends.keys())

    @classmethod
    def get_backend(cls, name: str, init_params: dict = None) -> BaseBackend:
        """Get backend from registry

        Args:
            name: Backend name
            init_params: Dictionary of initialization parameters with which to initialize writer

        Example
            >>> import omni.replicator.core as rep
            >>> class PassBackend(rep.backends.BaseBackend):
            ...     def __init__(self, param1):
            ...         pass
            ...     def write_blob(self, **kwargs):
            ...         pass
            ...     def read_blob(self, **kwargs):
            ...         pass
            >>> rep.backends.BackendRegistry.register_backend(PassBackend)
            >>> backend = rep.backends.BackendRegistry.get_backend("PassBackend")
            >>> backend.initialize(param1=1)
            >>> backend.get_name()
            'PassBackend'
        """
        if not isinstance(name, str):
            raise ValueError(f"Invalid name `{name}` of type `{type(name)}`")
        if not name in cls._backends:
            raise ValueError(f"No backend of name {name} registered")

        backend = cls._backends[name].__new__(cls._backends[name])

        if init_params:
            backend.initialize(**init_params)

        return backend


def get(name: str, init_params: dict = None) -> BaseBackend:
    """Get backend from registry

    Args:
        name: Backend name
        init_params: Dictionary of initialization parameters with which to initialize writer

    Example
        >>> import omni.replicator.core as rep
        >>> class PassBackend(rep.backends.BaseBackend):
        ...     def __init__(self, param1):
        ...         pass
        ...     def write_blob(self, **kwargs):
        ...         pass
        ...     def read_blob(self, **kwargs):
        ...         pass
        >>> rep.backends.register(PassBackend)
        >>> backend = rep.backends.get("PassBackend", init_params={"param1": 1})
        >>> backend.get_name()
        'PassBackend'
    """
    return BackendRegistry.get_backend(name, init_params=init_params)


def register(backend: BaseBackend) -> None:
    """Register a backend.

    Args:
        backend: Backend to register, must be derived from BaseBackend

    Example:
        >>> import omni.replicator.core as rep
        >>> class PassBackend(rep.backends.BaseBackend):
        ...     def __init__(self, **kwargs):
        ...         pass
        ...     def write_blob(self, **kwargs):
        ...         pass
        ...     def read_blob(self, **kwargs):
        ...         pass
        >>> rep.backends.register(PassBackend)
    """
    if not issubclass(backend, BaseBackend):
        raise ValueError(f"Invalid backend of type {type(backend)}. Backend must be derived from `BaseBackend`")

    BackendRegistry.register_backend(backend)


def unregister(backend: Union[str, BaseBackend]) -> None:
    """Unregister a backend.

    Args:
        name: Name of backend to unregister

    Example:
        >>> import omni.replicator.core as rep
        >>> class PassBackend(rep.backends.BaseBackend):
        ...     def __init__(self, **kwargs):
        ...         pass
        ...     def write_blob(self, **kwargs):
        ...         pass
        ...     def read_blob(self, **kwargs):
        ...         pass
        >>> rep.backends.register(PassBackend)
        >>> rep.backends.unregister("PassBackend")
    """
    BackendRegistry.unregister_backend(backend)
