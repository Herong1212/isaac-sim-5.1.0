# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from omni.graph.action_core import get_interface

class InternalState:
    def __init__(self):
        self.num_accumulated_exec_in = 0
        self.sync_value = (0, 0)

class OgnSdTestRationalTimeSyncGate:

    @classmethod
    def internal_state(*args):
        return InternalState()

    @staticmethod
    def compute(db) -> bool:
        attrib = db.node.get_attribute("inputs:execIn")
        accumulation_threshold = attrib.get_upstream_connection_count()
        sync_value = (db.inputs.rationalTimeNumerator, db.inputs.rationalTimeDenominator)
        state = db.internal_state
        reset = sync_value != state.sync_value
        state.num_accumulated_exec_in = 1 if reset else min(state.num_accumulated_exec_in + 1, accumulation_threshold)
        state.sync_value = sync_value
        db.outputs.rationalTimeNumerator = sync_value[0]
        db.outputs.rationalTimeDenominator = sync_value[1]
        if state.num_accumulated_exec_in >= accumulation_threshold:
            i_ag = get_interface()
            i_ag.set_execution_enabled("outputs:execOut")
        return True
