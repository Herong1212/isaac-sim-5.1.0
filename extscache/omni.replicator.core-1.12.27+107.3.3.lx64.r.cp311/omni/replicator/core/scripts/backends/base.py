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

import inspect
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import Callable

from .io_queue import data_queue
from .telemetry import telemetry


class BackendError(Exception):
    """Base exception for errors raised by Replicator backends"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "A backend error was encountered."
        super().__init__(msg)


class BaseBackend(ABC):
    """Backend abstract class

    Backends define how to write and read data. Backends define a ``write_blob`` function that defines how to write bytes
    to a specified path and a ``read_blob`` function that defines how to read bytes from a path.

    Note: While backends are most often used to write data, they can also be used to stream data or process data in some
        other way.
    """

    @abstractmethod
    def write_blob(self, path: str, data: bytes) -> None:
        pass

    @abstractmethod
    def read_blob(self, path: str) -> bytes:
        pass

    @classmethod
    def get_name(cls) -> str:
        """Get backend name"""
        return cls.__name__

    def schedule(self, fn: Callable, *args, **kwargs) -> None:
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
        data_queue.wait_if_max_queue_size()

        if "path" in kwargs and isinstance(kwargs["path"], str):
            suffix = Path(kwargs["path"]).suffix
            telemetry.record_backend(self.get_name(), suffix)

        if "backend_instance" in inspect.signature(fn).parameters:
            kwargs["backend_instance"] = self

        if isinstance(fn, partial) or inspect.signature(fn).return_annotation is partial:
            data_queue.put(fn(*args, **kwargs))
        else:
            data_queue.put(partial(fn, *args, **kwargs))

    @staticmethod
    def is_done_writing() -> bool:
        """Check if all scheduled tasks are complete

        Returns:
            True if data queue is empty, False otherwise.
        """
        if data_queue.is_done_writing():
            telemetry.record_file_types()
            return True
        return False

    @staticmethod
    def wait_until_done() -> None:
        """Wait until all scheduled tasks are complete"""
        data_queue.wait_until_done()

    def initialize(self, *args, **kwargs) -> None:
        """Initialize the backend"""
        self.__init__(*args, **kwargs)
