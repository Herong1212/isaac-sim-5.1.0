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

from . import (
    annotators,
    annotators_default,
    augmentations_default,
    backends,
    create,
    distribution,
    example,
    functional,
    get,
    modify,
    orchestrator,
    physics,
    randomizer,
    settings,
    trigger,
    utils,
    writers,
    writers_default,
)
from .annotators import AnnotatorRegistry, NodeConnectionTemplate
from .backends import BackendDispatch
from .extension import Extension, get_extension
from .utils import get_decal_bounds_transform_from_normalized, rng
from .utils.rng import get_global_seed, set_global_seed
from .utils.utils import new_layer, open_stage
from .writers import Writer, WriterRegistry, WriterRegistryError

if os.environ.get("SPHINX"):
    annotators_default.register_annotators()
    augmentations_default.register_augmentations()
    backends.register_backends()
    writers_default.register_writers()
    AnnotatorRegistry._write_docs()
