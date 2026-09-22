# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
"""Project helper functions."""

# Standard Library
from pathlib import Path
from typing import Optional

# NVIDIA
from nvidia.srl.basics.types import PathLike


def get_project_root_path(cwd_path: Optional[PathLike] = None) -> Path:
    """Finds the project root by looking for the .git directory from the current path.

    Args:
        cwd_path: Path to use as the current working directory.
    """
    if cwd_path is None:
        cwd_path = Path.cwd()
    if not isinstance(cwd_path, Path):
        cwd_path = Path(cwd_path)
    if (cwd_path / ".git").exists():
        return cwd_path.resolve().absolute()
    for parent in cwd_path.resolve().parents:
        if (parent / ".git").exists():
            return parent.resolve().absolute()
    raise RuntimeError(f"No '.git' directory found from the current path of '{cwd_path}'.")
