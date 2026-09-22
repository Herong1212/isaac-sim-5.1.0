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
import carb.events
import omni.graph.core as og
import omni.replicator.core as rep
from omni.replicator.core.ogn.OgnScheduleWriterDatabase import OgnScheduleWriterDatabase


class OgnScheduleWriterInternalState:
    def __init__(self):
        self.writer = None
        self.node = None
        self.is_triggered = rep.orchestrator.get_status() in [
            rep.orchestrator.Status.STARTED,
            rep.orchestrator.Status.STEPPED,
        ]
        self.sub_orchestrator = None

    def on_orchestrator(self, event):
        if event is None or not self.is_triggered or not self.node:
            return
        if self.writer is None:
            if self.node:
                self.writer = rep.writers.WriterRegistry._get_attached_writer(
                    self.node.get_attribute("inputs:writer_id").get()
                )
        if event.has_key("capture") and self.node and self.node.is_valid():
            if not self.writer:
                self.node.log_compute_message(
                    og.Severity.ERROR,
                    f"No attached writer matching ID `{self.node.get_attribute('inputs:writer_id').get()}` found.",
                )
            self.is_triggered = False
            self.writer._schedule(event.get("capture"))
        elif event.has_key("command") and event.get("command") == "initialize":
            # Set triggered to true to capture first frame
            self.is_triggered = False
        elif event.has_key("command") and event.get("command") == "stop":
            self.is_triggered = False

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
                observer_name="OgnScheduleWriter",
                event_name=rep.orchestrator.ORCHESTRATOR_EVENT,
                on_event=self.on_orchestrator,
            )
            self.node = node
            exit_val = True

        return exit_val

    def reset(self):
        if self.sub_orchestrator is not None:
            self.sub_orchestrator.reset()
        rep.orchestrator._release_trigger(self.node.get_prim_path())
        self.writer = None
        self.node = None
        self.sub_orchestrator = None


class OgnScheduleWriter:
    @staticmethod
    def internal_state() -> OgnScheduleWriterInternalState:
        return OgnScheduleWriterInternalState()

    @staticmethod
    def release(node) -> None:
        state = OgnScheduleWriterDatabase.shared_internal_state(node)
        state.reset()
        state.node = None

    @staticmethod
    def initialize(context, node) -> None:
        state = OgnScheduleWriterDatabase.shared_internal_state(node)
        state.first_time_subscribe(node)
        fn = OgnScheduleWriter.on_writer_changed
        node.get_attribute("inputs:writer_id").register_value_changed_callback(fn)

    @staticmethod
    def on_writer_changed(attr) -> None:
        node = attr.get_node()
        state = OgnScheduleWriterDatabase.shared_internal_state(node)
        try:
            state.writer = rep.writers.WriterRegistry._get_attached_writer(attr.get())
        except rep.WriterRegistryError as e:
            state.writer = None
            node.log_compute_message(og.Severity.WARNING, e.args[0])

    @staticmethod
    def compute(db) -> bool:
        if not db.inputs.writer_id:
            return

        state = db.shared_state

        if state.writer is None:
            state.writer = rep.writers.WriterRegistry._get_attached_writer(db.inputs.writer_id)
        state.is_triggered = True
        return True
