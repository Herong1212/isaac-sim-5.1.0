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

import omni.kit
import omni.kit.test
from omni.replicator.core.scripts.annotators_default import *
from omni.replicator.core.scripts.extension import *
from omni.replicator.core.scripts.writers_default import *


class TestImport(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

    async def test_import(self):
        """Test that from omni.replicator.core.scripts import <x> still works to preserve backward compatibility"""

        try:
            from omni.replicator.core import BackendDispatch
            from omni.replicator.core.scripts import (
                AnnotatorRegistry,
                BackendDispatch,
                annotators,
                augmentations_default,
                create,
                distribution,
                example,
                get,
                modify,
                orchestrator,
                physics,
                randomizer,
                settings,
                trigger,
                writers,
            )
            from omni.replicator.core.scripts.utils import rng, utils
            from omni.replicator.core.scripts.utils.rng import get_global_seed, set_global_seed
            from omni.replicator.core.scripts.utils.utils import new_layer
            from omni.replicator.core.scripts.writers import Writer, WriterRegistry, WriterRegistryError
        except Exception as e:
            raise e
