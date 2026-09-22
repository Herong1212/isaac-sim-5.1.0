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

import sys

from .scripts import (
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

# Add modules to omni.replicator.core
sys.modules["omni.replicator.core.utils"] = utils
sys.modules["omni.replicator.core.annotators"] = annotators
sys.modules["omni.replicator.core.annotators_default"] = annotators_default
sys.modules["omni.replicator.core.augmentations_default"] = augmentations_default
sys.modules["omni.replicator.core.backends"] = backends
sys.modules["omni.replicator.core.create"] = create
sys.modules["omni.replicator.core.distribution"] = distribution
sys.modules["omni.replicator.core.example"] = example
sys.modules["omni.replicator.core.functional"] = functional
sys.modules["omni.replicator.core.get"] = get
sys.modules["omni.replicator.core.modify"] = modify
sys.modules["omni.replicator.core.orchestrator"] = orchestrator
sys.modules["omni.replicator.core.physics"] = physics
sys.modules["omni.replicator.core.randomizer"] = randomizer
sys.modules["omni.replicator.core.settings"] = settings
sys.modules["omni.replicator.core.trigger"] = trigger
sys.modules["omni.replicator.core.writers"] = writers
sys.modules["omni.replicator.core.writers_default"] = writers_default

from .scripts.annotators import AnnotatorRegistry, NodeConnectionTemplate
from .scripts.annotators_default import *
from .scripts.backends import BackendDispatch
from .scripts.extension import *
from .scripts.utils import rng, utils
from .scripts.utils.mesh_decal import create_mesh_decal
from .scripts.utils.rng import get_global_seed, set_global_seed
from .scripts.utils.utils import new_layer, open_stage
from .scripts.writers import Writer, WriterRegistry, WriterRegistryError
from .scripts.writers_default import *  # Kept for backwards compatibility
