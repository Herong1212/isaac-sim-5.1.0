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

import numpy as np
import omni.graph.core as og
import omni.usd
from omni.replicator.core import utils
from pxr import UsdGeom


class OgnOrbit:
    @staticmethod
    def initialize(graph_context, node):
        node.get_attribute("inputs:barycentrePrim").register_value_changed_callback(OgnOrbit.on_mode_change)
        node.get_attribute("inputs:barycentreCoordinates").register_value_changed_callback(OgnOrbit.on_mode_change)

    @staticmethod
    def on_mode_change(attr) -> None:
        attr_name = attr.get_name()[7:]
        node = attr.get_node()
        mode_attr = node.get_attribute("inputs:barycentreMode")
        if attr_name == "barycentreCoordinates":
            mode_attr.set("Coordinates")
        elif attr_name == "barycentrePrim":
            mode_attr.set("Prim")

    @staticmethod
    def compute(db) -> bool:
        stage = omni.usd.get_context().get_stage()
        barycentre_mode = db.inputs.barycentreMode
        if barycentre_mode == "Prim":
            barycentre_prim_paths = db.inputs.barycentrePrim
            if len(barycentre_prim_paths) == 0:
                return False

            positions = []
            for prim_path in barycentre_prim_paths:
                prim = stage.GetPrimAtPath(str(prim_path))
                if not prim:
                    db.log_error(f"No prim found at {prim_path}")
                timeline_iface = omni.timeline.get_timeline_interface()
                time = timeline_iface.get_current_time() * timeline_iface.get_time_codes_per_seconds()
                positions.append(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(time).ExtractTranslation())
            barycentre_coords = np.mean(np.array(positions), axis=0)
        else:
            barycentre_coords = db.inputs.barycentreCoordinates

        distance = db.inputs.distance
        azimuth = np.radians(db.inputs.azimuth)
        elevation = np.radians(db.inputs.elevation)

        x = np.cos(azimuth) * np.cos(elevation) * distance
        y = np.sin(azimuth) * np.cos(elevation) * distance
        z = np.sin(elevation) * distance

        if UsdGeom.GetStageUpAxis(stage) == "Y":
            z, y = y, z

        values = np.hstack([x, y, z]).reshape(-1, 3) + barycentre_coords

        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        db.outputs.values = values
        return True
