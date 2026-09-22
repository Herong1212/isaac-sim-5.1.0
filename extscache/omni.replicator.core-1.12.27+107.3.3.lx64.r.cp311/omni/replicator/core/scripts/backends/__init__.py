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

import asyncio

from . import io_queue, registry
from .base import BaseBackend

# from .swift import SwiftBackend
from .disk import DiskBackend

# must import backend here otherwise the backend will not be initialized and registered
from .dispatcher import BackendDispatch
from .group import BackendGroup
from .registry import BackendRegistry, get, register, unregister
from .s3 import S3Backend
from .sequential import Sequential


def register_backends():
    BackendRegistry.register_backend(DiskBackend)
    BackendRegistry.register_backend(BackendGroup)
    BackendRegistry.register_backend(S3Backend)
