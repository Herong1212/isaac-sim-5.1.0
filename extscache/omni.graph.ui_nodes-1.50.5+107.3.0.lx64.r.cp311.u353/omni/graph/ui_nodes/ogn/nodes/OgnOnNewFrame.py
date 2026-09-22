"""
This is the implementation of the OGN node defined in OgnOnNewFrame.ogn
"""

from contextlib import suppress

import omni.graph.core as og
import omni.usd
from omni.graph.ui_nodes.ogn.OgnOnNewFrameDatabase import OgnOnNewFrameDatabase
from omni.kit.viewport.utility import get_viewport_from_window_name


class OgnOnNewFrameInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information."""
        # This subscription object controls the lifetime of our callback, it will be
        # cleaned up automatically when our node is destroyed
        self.sub = None
        # Set when the callback has triggered
        self.is_set = False
        # The last payload received
        self.payload = None
        # The node instance handle
        self.node = None
        # The viewport we are watching frames for
        self.viewport_handle = None

    def on_event(self, e):
        """The event callback"""
        if e is None:
            return
        self.is_set = True
        viewport_handle = e.payload["viewport_handle"]
        if viewport_handle != self.viewport_handle:
            return
        self.payload = e.payload

        # Tell the evaluator we need to be computed
        if self.node.is_valid():
            self.node.request_compute()

    def first_time_subscribe(self, node: og.Node, viewport_handle: int) -> bool:
        """Checked call to set up carb subscription
        Args:
            node: The node instance
            viewport_handle: The handle for the viewport to watch
        Returns:
            True if we subscribed, False if we are already subscribed
        """
        if self.sub is not None and self.viewport_handle != viewport_handle:
            # event name changed since we last subscribed, unsubscribe
            self.sub.unsubscribe()
            self.sub = None

        if self.sub is None:
            self.sub = (
                omni.usd.get_context()
                .get_rendering_event_stream()
                .create_subscription_to_push_by_type(
                    int(omni.usd.StageRenderingEventType.NEW_FRAME),
                    self.on_event,
                    name=f"omni.graph.action.__on_new_frame.{node.node_id()}",
                )
            )
            self.viewport_handle = viewport_handle
            self.node = node
            self.payload = None
            return True

        return False

    def try_pop_event(self):
        """Pop the payload of the last event received, or None if there is no event to pop"""
        if self.is_set:
            self.is_set = False
            payload = self.payload
            self.payload = None
            return payload
        return None


# ======================================================================


class OgnOnNewFrame:
    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnOnNewFrameInternalState()

    @staticmethod
    def compute(db) -> bool:
        viewport_name = db.inputs.viewport
        viewport_api = get_viewport_from_window_name(viewport_name)
        if not viewport_api:
            return True

        state = db.per_instance_state

        # XXX: Note this may be incorrect, viewport_handle is not stable (and may be None)
        viewport_handle = viewport_api.frame_info.get("viewport_handle")
        if state.first_time_subscribe(db.node, viewport_handle):
            return True

        payload = state.try_pop_event()

        if payload is None:
            return True

        # Copy the event dict contents into the output bundle
        db.outputs.frameNumber = payload["frame_number"]
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True

    # ----------------------------------------------------------------------------
    @staticmethod
    def release(node):
        # Unsubscribe right away instead of waiting for GC cleanup, we don't want our callback firing
        # after the node has been released.
        with suppress(og.OmniGraphError):
            state = OgnOnNewFrameDatabase.per_instance_internal_state(node)
            if state.sub:
                state.sub.unsubscribe()
                state.sub = None
