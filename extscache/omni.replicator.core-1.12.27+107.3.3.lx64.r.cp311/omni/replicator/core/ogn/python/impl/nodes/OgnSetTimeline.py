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

"""
This is the implementation of the OGN node defined in OgnSetTimeline.ogn
"""

import omni.graph.core as og
import omni.timeline
from omni.replicator.core import utils
from pxr import Sdf, UsdGeom


class OgnSetTimeline:
    @staticmethod
    def compute(db) -> bool:
        modify_type = db.inputs.modifyType
        value = db.inputs.value

        timeline_iface = omni.timeline.acquire_timeline_interface()

        if modify_type == "time":
            timeline_iface.set_current_time(value)
        elif modify_type == "start_time":
            timeline_iface.set_start_time(value)
        elif modify_type == "end_time":
            timeline_iface.set_end_time(value)
        elif modify_type == "frame":
            fps = float(timeline_iface.get_time_codes_per_seconds())
            timeline_iface.set_current_time(value / fps)
        elif modify_type == "start_frame":
            fps = float(timeline_iface.get_time_codes_per_seconds())
            timeline_iface.set_start_time(value / fps)
        elif modify_type == "end_frame":
            fps = float(timeline_iface.get_time_codes_per_seconds())
            timeline_iface.set_end_time(value / fps)

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
