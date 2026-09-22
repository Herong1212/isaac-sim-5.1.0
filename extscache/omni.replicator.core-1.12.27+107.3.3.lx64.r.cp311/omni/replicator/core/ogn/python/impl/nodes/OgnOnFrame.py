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
This is the implementation of the OGN node defined in OgnOnNewFrame.ogn
"""
import carb.events
import omni.graph.core as og
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core import orchestrator
from omni.replicator.core.ogn.OgnOnFrameDatabase import OgnOnFrameDatabase


def get_time(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator / denominator


class OgnOnFrameInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information."""
        self.is_started = False
        self.impulse = False
        self.interval_counter = 0
        self._num_executions = 0

        self.sub_frame = None
        self.sub_orchestrator = None
        # Set when the callback has triggered
        self.is_set = False
        # The last event received
        self.payload = None
        # The node instance handle
        self.node = None
        # The viewport we are watching frames for
        self.viewport_handle = None

        self._last_capture_time = 0.0, 0.0
        self._capture_time = None
        self._is_writer_trigger = False

    def reset(self):
        self._num_executions = 0
        self.interval_counter = 0
        self._last_capture_time = 0.0, 0.0
        self._capture_time = None

    def on_new_frame(self, event):
        """The event callback"""
        if event is None:
            return
        self.is_set = True

        self.payload = event.payload

        # Tell the evaluator we need to be computed
        if self.node.is_valid():
            self.node.request_compute()
            og.Controller.evaluate_sync(graph_id=self.node.get_graph())

    def on_orchestrator(self, event):
        if event is None:
            return
        if event.has_key("command"):
            if event.get("command") == "initialize":
                self.reset()
            if event.get("command") == "start":
                self.is_started = True
            elif event.get("command") == "stop":
                self.is_started = False
            elif event.get("command") == "preview":
                self.impulse = True
        elif event.has_key("trigger_frame"):
            self.impulse = True
        elif event.has_key("trigger"):
            if self._capture_time is None:
                if self._is_writer_trigger:
                    self._last_capture_time = -1.0, 1.0
                else:
                    self._last_capture_time = event.get("trigger")
            self._capture_time = event.get("trigger")
        else:
            return

        # Tell the evaluator we need to be computed
        if self.node.is_valid():
            self.node.request_compute()

    def first_time_subscribe(self, node: og.Node) -> bool:
        """Checked call to set up carb subscription
        Args:
            node: The node instance
            viewport_handle: The handle for the viewport to watch
        Returns:
            True if we subscribed, False if we are already subscribed
        """

        exit_val = False

        if self.sub_orchestrator is None:
            # Add a subscription for the given event name. This is a pop subscription, so we expect a 1-frame
            # lag between send and receive
            self.sub_orchestrator = carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="OgnOnFrame",
                event_name=rep.orchestrator.ORCHESTRATOR_EVENT,
                on_event=self.on_orchestrator,
            )
            self.node = node
            exit_val = True

            self._is_writer_trigger = self.node.get_graph().get_path_to_graph() == "/WriterOrchestrator"

        return exit_val

    def try_pop_event(self):
        """Pop the payload of the last event received, or None if there is no event to pop"""
        if self.is_set:
            self.is_set = False
            payload = self.payload
            self.payload = None
            return payload
        return None


# ======================================================================


class OgnOnFrame:
    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnOnFrameInternalState()

    @staticmethod
    def release(node):
        state = OgnOnFrameDatabase.shared_internal_state(node)
        if state.sub_frame:
            state.sub_frame.unsubscribe()
        state.sub = None
        if state.sub_orchestrator is not None:
            state.sub_orchestrator.reset()
        rep.orchestrator._release_trigger(node.get_prim_path())

    @staticmethod
    def initialize(context, node):
        state = OgnOnFrameDatabase.shared_internal_state(node)
        state.first_time_subscribe(node)

    @staticmethod
    def compute(db) -> bool:
        max_execs = db.inputs.maxExecs
        state = db.shared_state

        if state.impulse:
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            state._last_capture_time = state._capture_time
            state.impulse = False
            return True

        is_started = rep.orchestrator.get_status() in [orchestrator.Status.STARTED, orchestrator.Status.STEPPING]
        if not is_started or state._capture_time is None or state._last_capture_time is None:
            return True

        # Enable downstream execution if the frame number is equal or higher than input interval and within numFrames
        is_within_num_frames = max_execs == 0 or state._num_executions < max_execs
        is_capture_time = (
            get_time(*state._capture_time) > get_time(*state._last_capture_time) and not orchestrator.get_is_stopped()
        )
        is_orchestrator_running = orchestrator.get_status() in [
            orchestrator.Status.STARTED,
            orchestrator.Status.STOPPING,
        ]
        if is_within_num_frames and is_capture_time:  # and is_orchestrator_running:
            state._last_capture_time = state._capture_time
            state.interval_counter += 1
            if state.interval_counter >= db.inputs.interval:
                state._num_executions += 1
                db.outputs.execCounts = state._num_executions
                db.outputs.reference_time_numerator = state._capture_time[0]
                db.outputs.reference_time_denominator = state._capture_time[1]
                db.outputs.execOut = og.ExecutionAttributeState.ENABLED
                if max_execs:
                    rep.orchestrator._orchestrator._increment_call_count("trigger", db.node.get_prim_path())
                state.interval_counter = 0
                rep.orchestrator.set_minimum_next_rt_subframes(db.inputs.rtSubframes)
                if carb.settings.get_settings().get("/omni/replicator/debug"):
                    carb.log_info(
                        f"    on-frame {state._last_capture_time} ({state._num_executions} out of {max_execs})"
                    )

        if state._num_executions == max_execs and max_execs > 0:
            rep.orchestrator._orchestrator._set_active_status(
                "trigger", db.node.get_prim_path(), False, state._capture_time
            )
        return True
