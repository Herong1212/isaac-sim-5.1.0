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

from typing import Callable, List

from .base import BaseBackend

HASH_TYPE_STR = "md5"


class BackendGroup(BaseBackend):
    """Group multiple backends
    Group multiple backends to write data to multiple end points simultaneously. For example, you may want to stream
    data to a robot and also write the data to local disk as a backup or to create an offline dataset.

    Args:
        backends: List of backends to group together.
    """

    def __init__(self, backends: List[BaseBackend]) -> None:
        if not all([isinstance(bk, BaseBackend) for bk in backends]):
            invalid_backends = [bk for bk in backends if not isinstance(bk, BaseBackend)]
            raise ValueError(f"Found invalid backend(s): {invalid_backends}")
        self._backends = backends
        self._backend_names = [bk.get_name() for bk in backends]

    def schedule(self, fn: Callable, *args, **kwargs):
        """Schedule a task to be executed asynchronously

        Append a task to a data queue that will be executed by multithreaded workers at a later time. This is often
        desirable so as to avoid bottlenecking the simulation thread with I/O tasks.

        Note: Because scheduled tasks are not executed immediately, special care must be given to manage the lifetime
            of passed objects.

        Args:
            fn: Task function to be performed asynchronously.bind
            *args: Positional arguments to parametrize task.
            **kwargs: Keyword arguments to parametrize task.
        """
        for backend in self._backends:
            backend.schedule(fn, *args, **kwargs)

    def read_blob(self, path: str) -> bytes:
        """Read data
        Read blob will try to read from the given path with each backend and return the first successful payload.

        Args:
            path: Data path to read from
        """
        for backend in self._backends:
            try:
                return backend.read_blob(path)
            except Exception:
                continue
        raise ValueError(f"Unable to read from path {path} with backends {self._backend_names}.")

    def write_blob(self, path: str, data: bytes) -> None:
        """Schedule a write data blob task
        Legacy function. Schedule to write data blob with each dispatcher backend.

        Args:
            path (str): Path to write data to.
            data: Data to write.
        """
        for backend in self._backends:
            backend.schedule(backend.write_blob, data=data, path=path)
