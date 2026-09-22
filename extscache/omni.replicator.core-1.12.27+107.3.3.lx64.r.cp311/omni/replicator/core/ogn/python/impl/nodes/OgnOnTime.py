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
import math

import carb.events
import omni.graph.core as og
import omni.physx
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core.ogn.OgnOnTimeDatabase import OgnOnTimeDatabase


class OgnOnTimeInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information."""
        self.is_started = False
        self.impulse = False

        self.sub_orchestrator = None
        # Set when the callback has triggered
        self.is_set = False
        # The last event received
        self.payload = None
        # The node instance handle
        self.node_path = None
        self.graph = None
        self.capture_time = 0.0
        self.last_capture_time = 0.0
        self.num_executions = 0
        self.last_trigger_time = 0.0
        self.reference_time_numerator = -1.0
        self.reference_time_denominator = -1.0

    def on_update(self, event):
        """The event callback"""
        if event is None:
            return
        self.is_set = True

        self.payload = event.payload

        # Tell the evaluator we need to be computed
        if self.graph:
            node = self.graph.get_node(self.node_path)
            if node.is_valid():
                node.request_compute()

    def reset_num_execs(self):
        rep.orchestrator._orchestrator._initialize_call_count("trigger", self.node_path)
        self.num_executions = 0
        self.frame_counter = 0
        self.cur_frame = 0
        self.last_trigger_time = 0.0
        self.last_capture_time = 0.0
        if self.graph:
            node = self.graph.get_node(self.node_path)
            if node and node.get_attribute_exists("outputs:execCounts"):
                og.AttributeValueHelper(node.get_attribute("outputs:execCounts")).set(0, update_usd=True)

    def on_orchestrator(self, event):
        if event is None:
            return
        if event.has_key("command"):
            if event.get("command") == "initialize":
                self.reset_num_execs()
            if event.get("command") == "start":
                self.is_started = True
            elif event.get("command") == "stop":
                self.is_started = False
                self.reset_num_execs()
            elif event.get("command") == "preview":
                self.impulse = True
        elif event.has_key("trigger_frame"):
            self.impulse = True
        elif event.has_key("trigger"):
            self.reference_time_numerator, self.reference_time_denominator = event.get("trigger")
            timeline_iface = omni.timeline.get_timeline_interface()
            self.last_capture_time = self.capture_time
            self.capture_time = timeline_iface.get_current_time()

            # Handle looped timeline
            if timeline_iface.is_looping() and self.last_capture_time and self.capture_time < self.last_capture_time:
                self.last_trigger_time = self.last_trigger_time - timeline_iface.get_end_time() - self.capture_time

        # Tell the evaluator we need to be computed
        if self.graph:
            node = self.graph.get_node(self.node_path)
            if node.is_valid():
                node.request_compute()

    def _physics_timer_callback_fn(self, dt):
        self.cur_time += dt

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
                observer_name="OgnOnTime", event_name=rep.orchestrator.ORCHESTRATOR_EVENT, on_event=self.on_orchestrator
            )
            self.node_path = node.get_prim_path()
            self.graph = node.get_graph()
            exit_val = True

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


class OgnOnTime:
    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnOnTimeInternalState()

    @staticmethod
    def release(node):
        state = OgnOnTimeDatabase.shared_internal_state(node)
        if state.sub_orchestrator is not None:
            state.sub_orchestrator.reset()
        rep.orchestrator._release_trigger(node.get_prim_path())

    @staticmethod
    def initialize(context, node):
        state = OgnOnTimeDatabase.shared_internal_state(node)
        state.first_time_subscribe(node)

    @staticmethod
    def compute(db) -> bool:
        max_execs = db.inputs.maxExecs
        state = db.shared_state
        interval = db.inputs.interval
        trigger_on_last = db.inputs.triggerOnLastFrame

        # Note: paused status is valid, as the node may be executed on a played frame that has been paused
        if not rep.orchestrator.get_is_started() and not rep.orchestrator.get_is_paused() and not state.impulse:
            return True

        offset = 0.0
        if trigger_on_last:
            offset = min(1.0 / omni.timeline.get_timeline_interface().get_time_codes_per_seconds(), interval)
        target_time = (state.last_trigger_time + interval if state.last_trigger_time else interval) - offset
        is_at_interval = math.isclose(state.capture_time, target_time, rel_tol=1e-6) or state.capture_time > target_time
        is_within_num_frames = state.num_executions < max_execs or max_execs == 0
        is_started = rep.orchestrator.get_status() in [
            rep.orchestrator.Status.STARTED,
            rep.orchestrator.Status.STEPPING,
        ]

        if is_within_num_frames and is_started and is_at_interval:
            stage = omni.usd.get_context().get_stage()
            state.frame_counter = 0

            # Reset physics
            if db.inputs.resetPhysics and stage.GetPrimAtPath("/PhysicsScene").IsValid():
                physx_interface = omni.physx.acquire_physx_interface()
                physx_interface.reset_simulation()

            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            db.outputs.reference_time_numerator = state.reference_time_numerator
            db.outputs.reference_time_denominator = state.reference_time_denominator
            if max_execs:
                rep.orchestrator._orchestrator._increment_call_count("trigger", db.node.get_prim_path())
            state.last_trigger_time = state.capture_time + offset
            state.num_executions += 1
            rep.orchestrator.set_minimum_next_rt_subframes(db.inputs.rtSubframes)

        if state.impulse and not trigger_on_last:
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        # Check if max executions reached
        if state.num_executions >= max_execs and max_execs > 0 and not state.impulse:
            # Disable trigger and reset last_exec_frame
            # state.last_exec_frame = None
            rep.orchestrator._orchestrator._set_active_status("trigger", db.node.get_prim_path(), False)
        state.impulse = False
        db.outputs.execCounts = state.num_executions
        return True
