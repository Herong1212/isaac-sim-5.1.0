# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

# Replicator/Simple Pipeline
import omni.replicator.core as rep
from omni.replicator.core.distribution import uniform

camera = rep.create.camera(position=(0, 0, 1000))
render_product = rep.create.render_product(camera, (1024, 1024))

torus = rep.create.torus(semantics=[("class", "torus")])
sphere = rep.create.sphere(semantics=[("class", "sphere")])
cube = rep.create.cube(semantics=[("class", "cube")])

plane = rep.create.plane(scale=10, visible=False)

with rep.trigger.on_frame(max_execs=10):
    with rep.create.group([torus, sphere, cube]):
        rep.modify.pose(
            position=uniform((-100, -100, -100), (200, 200, 200)),
            scale=uniform(0.1, 2),
        )

# Initialize and attach writer
writer = rep.writers.get("BasicWriter")
writer.initialize(output_dir="_output", rgb=True)
writer.attach([render_product])
