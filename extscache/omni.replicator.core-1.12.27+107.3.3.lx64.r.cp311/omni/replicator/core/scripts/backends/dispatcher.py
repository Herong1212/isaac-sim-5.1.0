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
import io
import os
from typing import Union

import carb
import numpy as np
import warp as wp
from PIL import Image

from ..functional.io_functions import write_exr, write_image, write_np
from .base import BackendError
from .disk import DiskBackend
from .group import BackendGroup
from .io_queue import data_queue
from .registry import BackendRegistry

HASH_TYPE_STR = "md5"


class BackendDispatch(BackendGroup):
    """Automatically select one or more backend from specified arguments.
    Legacy class provided for backwards compatibility. Prefer to specify a backend directly (eg. `backend = rep.backends.get("DiskBackend")`).
    Backend Dispatcher automatically parses a config and/or keyword arguments (kwargs) based on the initialization
    rules defined in the __init__ function, allowing you to customize and filter valid backends.
    """

    def __init__(self, config: dict = None, **kwargs) -> None:
        # LEGACY
        if config is not None:
            if "use_s3" in config and "paths" in config and "s3_bucket" in config["paths"]:
                kwargs.update(
                    {
                        "bucket": config["paths"].get("s3_bucket"),
                        "key_prefix": config["paths"]["out_dir"],
                        "region": config["paths"].get("s3_region"),
                        "endpoint_url": config["paths"].get("s3_endpoint_url"),
                    }
                )
            elif "paths" in config and "out_dir" in config["paths"]:
                kwargs.update({"output_dir": config["paths"]["out_dir"]})

        self._deferred_path = []
        registered_backends = BackendRegistry.get_registered_backends()
        backends = []
        backend_names = []
        for backend_name in registered_backends:
            # do validation in each derived class
            # If you want to customize your own class, simply register it using the BackendRegistry and provide the
            # corresponding parameters in the config dictionary used to initialize BackendDispatch.
            registered_backend = BackendRegistry._backends.get(backend_name)
            try:
                allowed_kwargs = inspect.signature(registered_backend).parameters
                valid_kwargs = {}
                for kw in allowed_kwargs:
                    if kw in kwargs:
                        valid_kwargs[kw] = kwargs[kw]
                registered_backend_instance = registered_backend(**valid_kwargs)
                backends.append(registered_backend_instance)
                backend_names.append(backend_name)
            except TypeError:
                # Skip backends where arguments are invalid
                pass
            except BackendError as e:
                carb.log_warn(f"Unable to initialize `{backend_name}`: {e}")
        if len(backends) == 0:
            raise ValueError(f"No backend could be initialized with parameters provided: {kwargs}")
        elif len(backends) == 1:
            carb.log_info(f"Successfully initialized 1 backend: {backend_names[0]}")
            self.output_dir = backends[0].output_dir  # for backward compatibility
        else:
            carb.log_info(
                f"Successfully initialized {len(backends)} backends: {' '.join([bn for bn in backend_names])}. "
                "The BackendDispatch class does not have a 'self.output_dir' attribute because there are multiple backends."
            )
        super().__init__(backends=backends)

    @staticmethod
    def set_max_queue_size(value: int) -> None:
        """Set maximum data queue size.
        Legacy function

        Args:
            value: New maximum queue size.
        """
        data_queue.max_queue_size = int(value)

    def write_blob(self, path: str, data: bytes) -> None:
        """Schedule a write data blob task
        Legacy function. Schedule to write data blob with each dispatcher backend.

        Args:
            data: Data to write.
            path: Path to write data to.
        """
        for backend in self._backends:
            backend.schedule(backend.write_blob, data=data, path=path)

    def write_image(self, path: str, data: Union[np.ndarray, wp.array, Image.Image]) -> None:
        """Write image data.
        Legacy function. Schedule to write image data with each dispatcher backend.

        Args:
            data: Data to write
            path: Path to write data to.
        """
        for backend in self._backends:
            backend.schedule(write_image, data=data, path=path, backend_instance=backend)

    def write_array(self, path: str, data: Union[np.ndarray, wp.array]) -> None:
        """Write array data.
        Legacy function. Schedule to write image data with each dispatcher backend.

        Args:
            data: Data to write
            path: Path to write data to.
        """
        if isinstance(data, wp.array):
            data = data.numpy()

        for backend in self._backends:
            backend.schedule(write_np, data=data, path=path, backend_instance=backend)

    def write_exr(self, path: str, data: Union[np.ndarray, wp.array], exr_flag=None) -> None:
        """Write EXR data.
        Legacy function. Schedule to write EXR data with each dispatcher backend.

        Args:
            data: Data to write
            path: Path to write data to.
            exr_flag from FIF_EXR:
                imageio.plugins.freeimage.IO_FLAGS.EXR_DEFAULT: Save data as half with piz-based wavelet compression
                imageio.plugins.freeimage.IO_FLAGS.EXR_FLOAT: Save data as float instead of as half (not recommended)
                imageio.plugins.freeimage.IO_FLAGS.EXR_NONE: Save with no compression
                imageio.plugins.freeimage.IO_FLAGS.EXR_ZIP: Save with zlib compression, in blocks of 16 scan lines
                imageio.plugins.freeimage.IO_FLAGS.EXR_PIZ: Save with piz-based wavelet compression
                imageio.plugins.freeimage.IO_FLAGS.EXR_PXR24: Save with lossy 24-bit float compression
                imageio.plugins.freeimage.IO_FLAGS.EXR_B44: Save with lossy 44% float compression - goes to 22% when combined with EXR_LC
                imageio.plugins.freeimage.IO_FLAGS.EXR_LC: Save images with one luminance and two chroma channels, rather than as RGB (lossy compression)
        """
        for backend in self._backends:
            backend.schedule(write_exr, data=data, path=path, exr_flag=exr_flag, backend_instance=backend)
