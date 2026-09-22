# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.graph.core as og
from omni.graph.action_core import get_interface

# Set True to enable verbose debugging prints to console
DEBUG_PRINT = False


# ==============================================================================================================


class OgnCountdown:
    @staticmethod
    def initialize(_, node):
        og.Controller.attribute("state:count", node).set(-1)

    @staticmethod
    def compute(db) -> bool:
        i_ag = get_interface()

        def print_state(state_string: str):
            print(f"{db.node.get_prim_path()} {state_string}")

        count = db.state.count
        duration = db.inputs.duration
        count += 1
        tick_value = count + 1
        alpha = 0
        is_exec_in = i_ag.get_execution_enabled("inputs:execIn")
        if is_exec_in:
            if DEBUG_PRINT:
                print_state("START")
            # Reset our state
            count = 0
            tick_value = count + 1
            if not i_ag.get_latent_state():
                i_ag.start_latent_state()
            i_ag.set_execution_enabled("outputs:tick")
        else:
            if duration < count:
                # Finished
                i_ag.end_latent_state()
                i_ag.set_execution_enabled("outputs:finished")
                tick_value = count - 1
                alpha = 1.0
                count = -1
                if DEBUG_PRINT:
                    print_state("FINISHED")
            else:
                # Still ticking
                alpha = count / max(duration, 1)
                period = db.inputs.period
                if (period == 0) or ((count % db.inputs.period) == 0):  # noqa: S001
                    i_ag.set_execution_enabled("outputs:tick")
                if DEBUG_PRINT:
                    print_state("TICK")

        # Write outputs
        db.state.count = count
        db.outputs.alpha = alpha
        db.outputs.tickValue = tick_value

        return True
