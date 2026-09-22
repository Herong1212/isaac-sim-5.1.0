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
The trigger gate takes in two types of executions: the main execution and trigger executions.
The execution signal is allowed to pass if, for each change of the sync value, the main execution
and one or more of the trigger executions as fired. Only one execution output is allowed to pass
for each sync value change.
"""
from collections import deque

import omni.graph.core as og


class OgnTriggerGateInternalState:
    def __init__(self):
        self.num_trigger_execs = 0
        self.is_exec = 0
        self.sync_value = -1
        self.exec = False
        self.active = True
        self.frames = deque(maxlen=10)

    def reset(self, sync_value):
        self.sync_value = sync_value
        self.active = True


class OgnTriggerGate:
    @staticmethod
    def internal_state():
        return OgnTriggerGateInternalState()

    @staticmethod
    def compute(db) -> bool:
        num_trigger_exec = db.node.get_attribute("inputs:triggerExec").get_upstream_connection_count()
        if num_trigger_exec == 0:
            db.outputs.exec = og.ExecutionAttributeState.ENABLED
            return True

        db.outputs.exec = og.ExecutionAttributeState.DISABLED
        sync_value = db.inputs.syncValue
        state = db.shared_state

        if db.inputs.exec > 0 and (sync_value != state.sync_value or sync_value == 0):
            state.reset(sync_value)

        if db.inputs.triggerExec > 0:
            for trigger_exec_out in db.node.get_attribute("inputs:triggerExec").get_upstream_connections():
                if trigger_exec_out.get():
                    trigger_node = trigger_exec_out.get_node()
                    if trigger_node.get_attribute_exists("outputs:swhFrameNumber"):
                        state.frames.append(trigger_node.get_attribute("outputs:swhFrameNumber").get())

        if state.active and sync_value in state.frames:
            db.outputs.exec = og.ExecutionAttributeState.ENABLED
            state.num_trigger_execs = 0
            state.active = False  # ensures that node executes only once per sync value

        db.outputs.syncValue = db.inputs.syncValue
        return True
