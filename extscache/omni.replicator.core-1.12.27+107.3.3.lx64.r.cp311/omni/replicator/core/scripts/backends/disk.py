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

import os
from pathlib import Path

import carb

from .base import BaseBackend


def validate_out_dir(out_dir: str) -> str:
    out_dir = Path(out_dir).expanduser()  # Expand ~ first

    if Path(out_dir).is_absolute():  # Given output path is an absolute path
        return out_dir.as_posix()

    # Given output path is relative, check for default setting
    root_dir = carb.settings.get_settings().get("/omni/replicator/backends/disk/root_dir")
    if root_dir:
        return Path(root_dir).expanduser().joinpath(out_dir).resolve().as_posix()

    # No default setting, use home directory as base directory
    home_dir = Path.home()
    def_rep_folder = "omni.replicator_out"  # default replicator output folder
    valid_out_dir = home_dir.joinpath(def_rep_folder).joinpath(out_dir).resolve().as_posix()
    carb.log_warn(
        "No root directory specified in carb setting `/omni/replicator/backends/disk/root_dir`. "
        f"Writing data to {valid_out_dir}"
    )
    return valid_out_dir


class DiskBackend(BaseBackend):
    """Disk writing backend

    Backend to write data to disk to a specified output directory.

    Args:
        output_dir: Root output directory. If specified as a relative path, output will be relative to the path specified
            by the setting ``/omni/replicator/backends/disk/root_dir``. If no root directory is specified, the root_dir
            is specified as `<home_dir>/omni.replicator_out`.
        overwrite: If ``True``, overwrite existing folder of the same output path. If ``False``, a suffix in the format
            of ``_000N`` is added to the output directory name, where ``N`` is the next available number. Defaults
            to True.
    """

    def __init__(self, output_dir: str, overwrite: bool = True) -> None:
        self.output_dir = self._create_output_folder(output_dir=validate_out_dir(output_dir), overwrite=overwrite)
        carb.log_info(f"Local data will be saved to: {self.output_dir}")

        # Re-assign <read/write>_blob from static to instanced versions
        self.write_blob = self._write_blob_instance
        self.read_blob = self._read_blob_instance

    @staticmethod
    def _create_output_folder(output_dir: str, overwrite: bool = True) -> None:
        if overwrite is True:
            os.makedirs(output_dir, exist_ok=True)
        else:
            # this creates a new folder if one already exists that has the lowest number tag that does not exist yet
            if os.path.exists(output_dir):
                padding = 0
                _output_dir_orig = str(output_dir)
                while os.path.exists(output_dir):
                    padding += 1
                    output_dir = f"{_output_dir_orig}_{padding:04}"

            os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _write_blob_instance(self, path: str, data: bytes) -> None:
        """Write a blob of bytes (with class instance)
        Write blob to disk at specified path with initialized backend.

        Args:
            path: Path to write data to.
            data: Data to write to disk, provided as bytes.
        """
        full_path = self.resolve_path(path)
        dirname = os.path.dirname(full_path)
        os.makedirs(dirname, exist_ok=True)
        carb.log_info(f"Writing {full_path}")
        with open(full_path, "wb") as fp:
            fp.write(data)

    @staticmethod
    def read_blob(path) -> bytes:
        """Return blob of bytes

        Args:
            path: Path of file to read.

        Returns:
            Bytes data.
        """
        if os.path.isabs(path):
            full_path = path
        else:
            output_dir = validate_out_dir("")
            full_path = os.path.join(output_dir, path)

        return open(full_path, "rb").read()

    def _read_blob_instance(self, path) -> bytes:
        """Return blob of bytes

        Args:
            path: Path of file. If relative path is provided, it is read relative to the backend's output directory.

        Returns:
            Bytes data.
        """
        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.path.join(self.output_dir, path)

        return open(full_path, "rb").read()

    def resolve_path(self, path: str) -> str:
        """Join path to output directory

        Args:
            path: Partial path to resolve with output_dir

        Returns:
            Full file path
        """
        return Path(self.output_dir).expanduser().joinpath(path).resolve().as_posix()

    @staticmethod
    def write_blob(path: str, data: bytes) -> None:
        """Write blob to disk (uninitialized backend)
        Write blob to disk at specified path with uninitialized backend.

        Args:
            path: Path to write data to. If specified as a relative path, output will be relative to the path specified
                by the setting ``/omni/replicator/backends/disk/root_dir``. If no root directory is specified, the
                root_dir is specified as `<home_dir>/omni.replicator_out`.
            data: Data to write to disk.
        """
        if os.path.isabs(path):
            full_path = path
        else:
            output_dir = validate_out_dir("")
            full_path = os.path.join(output_dir, path)

        dirname = os.path.dirname(full_path)
        os.makedirs(dirname, exist_ok=True)
        carb.log_info(f"Writing {full_path}")
        with open(full_path, "wb") as fp:
            fp.write(data)
