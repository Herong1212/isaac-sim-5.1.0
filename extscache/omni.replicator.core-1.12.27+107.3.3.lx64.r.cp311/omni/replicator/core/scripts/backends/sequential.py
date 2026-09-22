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
from functools import partial
from typing import Any, Callable, List

from .base import BaseBackend


class Sequential:
    """
    Setup a sequence of tasks.
    Used to defined a sequence tasks. Tasks may be defined as lambdas, functions or classes. Calling a Sequential instance
    returns a partial function that can be scheduled to run on background threads. This is often desirable to avoid
    I/O or post processing tasks from blocking the simulation thread.

    Args:
        *tasks: List of functions representing tasks to be executed in sequence. Tasks must have compatible inputs/outputs
            to be sequenced together.

    Note: Calling a Sequential instance returns a Python partial function.

    Example 1:
        >>> import omni.replicator.core.functional as F
        >>> import numpy as np
        >>> from functools import partial
        >>> from omni.replicator.core import backends
        >>> # Define function and class to go into a task sequence
        >>> def pad(x, pad_value, pad_length):
        ...     return f"{x:{pad_value}>{pad_length}}"
        >>> class add_prefix:
        ...     def __init__(self, prefix):
        ...         self.prefix = prefix
        ...     def __call__(self, x):
        ...         return f"{self.prefix}{x}"
        >>> sequence_path = Sequential(
        ...     lambda x: x * 2,
        ...     partial(pad, pad_value=0, pad_length=5),
        ...     add_prefix("frame_"),
        ...     lambda x, ext="png": f"{x}.{ext}",
        ... )
        >>> # Test sequence
        >>> sequence_path(1)()
        'frame_00002.png'
        >>> # Setup data task sequence
        >>> sequence_data = Sequential(
        ...     lambda x, factor=2: x * factor,
        ...     lambda x, offset=10: x + offset,
        ... )
        >>> # Test sequence
        >>> seq_partial = sequence_data(np.ones(1))
        >>> type(seq_partial)
        <class 'functools.partial'>
        >>> seq_partial()
        array([12.])
        >>> # Setup Backend
        >>> backend_abs = backends.BackendDispatch(output_dir="_out")
        >>> test_frame_num = 5
        >>> test_data = np.ones((100, 100, 4))
        >>> backend_abs.schedule(F.write_image, path=sequence_path(test_frame_num), data=sequence_data(test_data))


    For more complex operations, sequenced tasks can accept and return tuples or dictionaries to further parameterize
    downstream tasks. Note that sequenced funtions should return and ingest the same arguments to be compatible with
    each other.


    Example 2:
        >>> import omni.replicator.core.functional as F
        >>> import numpy as np
        >>> from omni.replicator.core import backends
        >>> # Define functions to go into a task sequence
        >>> def add_empty_suffix(path, data):
        ...     import os   # import goes here as it will go out of scope on execution
        ...     if data.sum() == 0:
        ...         path_og, ext = os.path.splitext(path)
        ...         path = f"{path_og}_empty{ext}"
        ...     return path, data
        >>> def empty_data_message(path, data):
        ...     if data.sum() == 0:
        ...         print(f"Writing empty image of size {data.shape} to {path}")
        ...     return {"path": path, "data": data}
        >>> sequence_write_image = backends.Sequential(
        ...     add_empty_suffix,
        ...     empty_data_message,
        ...     F.write_image,
        ... )
        >>> # Test sequence
        >>> sequence_write_image("path/to/image.png", np.zeros((10, 10, 3)))()
        Writing empty image of size (10, 10, 3) to path/to/image_empty.png
        >>> # Setup Backend
        >>> backend_abs = backends.BackendDispatch(output_dir="_out")
        >>> test_path = "exr_data.exr"
        >>> test_data = np.zeros((10, 10, 3), dtype=np.float32)
        >>> backend_abs.schedule(sequence_write_image, path=test_path, data=test_data)
    """

    def __init__(self, *tasks: List[Callable]):
        self.tasks = tasks

    def __call__(self, *args, backend_instance: BaseBackend = None, **kwargs) -> partial:
        """This initializes a sequence of functions with specific parameters.
            It is important to note that calling a Sequential object does not immediately execute the sequence.
            This design allows for safe usage within a 'schedule' call. The sequence can then be executed asynchronously
            at a chosen time.

        Args:
            backend_instance: Optionally specify the backend to use. This parameter is automatically provided
                when called from a `<backend>.schedule()` call.
            *args: Optional positional parameters.
            **kwargs: Optional keyword parameters.

        Returns:
            Partial function of the sequence of tasks.
        """
        return partial(self.execute, *args, backend_instance=backend_instance, **kwargs)

    def execute(self, *args, backend_instance=None, **kwargs) -> Any:
        """Executes sequence of tasks with specified parameters

        Args:
            backend_instance: Optionally specify the backend to use. This parameter is automatically provided
                when called from a `<backend>.schedule()` call.
            *args: Optional positional parameters.
            **kwargs: Optional keyword parameters.
        """
        for task in self.tasks:
            # Insert backend instance in kwargs if needed
            if backend_instance and "backend_instance" in inspect.signature(task).parameters:
                kwargs["backend_instance"] = backend_instance
            if callable(task):
                result = task(*args, **kwargs)
            else:
                raise ValueError("Sequential: Unsupported function or class type")

            args, kwargs = [], {}
            if isinstance(result, dict):
                kwargs = result
            elif isinstance(result, tuple):
                args = result
            else:
                args = (result,)

        return result
