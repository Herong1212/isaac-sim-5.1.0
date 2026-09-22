"""
This is the implementation of the OGN node defined in OgnOnStageEvent.ogn
"""

from contextlib import suppress

import carb
import omni.graph.core as og
import omni.kit.app
import omni.usd
from omni.graph.action_core import get_interface
from omni.graph.action_nodes.ogn.OgnOnStageEventDatabase import OgnOnStageEventDatabase

# global map of the token to python enum, should match the allowedTokens
event_name_to_enum = {
    "Assets Loaded": omni.usd.StageEventType.ASSETS_LOADED,
    "Assets Load Aborted": omni.usd.StageEventType.ASSETS_LOAD_ABORTED,
    "Closed": omni.usd.StageEventType.CLOSED,
    "Closing": omni.usd.StageEventType.CLOSING,
    "Gizmo Tracking Changed": omni.usd.StageEventType.GIZMO_TRACKING_CHANGED,
    "MDL Param Loaded": omni.usd.StageEventType.MDL_PARAM_LOADED,
    "Opened": omni.usd.StageEventType.OPENED,
    "Open Failed": omni.usd.StageEventType.OPEN_FAILED,
    "Saved": omni.usd.StageEventType.SAVED,
    "Save Failed": omni.usd.StageEventType.SAVE_FAILED,
    "Selection Changed": omni.usd.StageEventType.SELECTION_CHANGED,
    "Hierarchy Changed": omni.usd.StageEventType.HIERARCHY_CHANGED,
    "Settings Loaded": omni.usd.StageEventType.SETTINGS_LOADED,
    "Settings Saving": omni.usd.StageEventType.SETTINGS_SAVING,
    "OmniGraph Start Play": omni.usd.StageEventType.OMNIGRAPH_START_PLAY,
    "OmniGraph Stop Play": omni.usd.StageEventType.OMNIGRAPH_STOP_PLAY,
    "Simulation Start Play": omni.usd.StageEventType.SIMULATION_START_PLAY,
    "Simulation Stop Play": omni.usd.StageEventType.SIMULATION_STOP_PLAY,
    "Animation Start Play": omni.usd.StageEventType.ANIMATION_START_PLAY,
    "Animation Stop Play": omni.usd.StageEventType.ANIMATION_STOP_PLAY,
}


class OgnOnStageEventInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information."""
        # This subscription object controls the lifetime of our callback, we will clean it up upon release
        self.sub = None
        # Set when the callback has triggered
        self.is_set = False
        # The last payload received
        self.payload: carb.dictionary.Item = None
        # The event_name we used to subscribe
        self.sub_event_type = ""
        # The node instance handle
        self.node = None
        # Counter to determine when an animation pause was detected
        self._was_paused = 0
        # cache of the int-valued event types
        self._stop_play_events = [
            int(e)
            for e in (
                omni.usd.StageEventType.OMNIGRAPH_STOP_PLAY,
                omni.usd.StageEventType.SIMULATION_STOP_PLAY,
                omni.usd.StageEventType.ANIMATION_STOP_PLAY,
            )
        ]
        self._start_play_events = [
            int(e)
            for e in (
                omni.usd.StageEventType.OMNIGRAPH_START_PLAY,
                omni.usd.StageEventType.SIMULATION_START_PLAY,
                omni.usd.StageEventType.ANIMATION_START_PLAY,
            )
        ]
        self._timeline = omni.timeline.get_timeline_interface()

    def _on_stage_event(self, e: carb.events.IEvent):
        """The event callback"""
        if e is None:
            return
        # Maintain book-keeping for pause/resume so we can ignore them
        if e.type in self._stop_play_events:
            is_stopped = self._timeline.is_stopped()
            if not is_stopped:
                # This is actually a PAUSE, because the timeline is not stopped
                self._was_paused += 1
                return
        elif (e.type in self._start_play_events) and (self._was_paused > 0):
            # This is actually an UNPAUSE, because we previously detected a PAUSE
            self._was_paused -= 1
            return

        if e.type != int(self.sub_event_type):
            return
        self.is_set = True
        self.payload = e.payload
        # Tell the evaluator we need to be computed
        if self.node.is_valid():
            self.node.request_compute()

    def first_time_subscribe(self, node: og.Node, event_type: omni.usd.StageEventType) -> bool:
        """Checked call to set up carb subscription
        Args:
            node: The node instance
            event_type: The stage event type
        Returns:
            True if we subscribed, False if we are already subscribed
        """
        if self.sub is not None and self.sub_event_type != event_type:
            # event name changed since we last subscribed, unsubscribe
            self.sub.unsubscribe()
            self.sub = None

        if self.sub is None:
            # Add a subscription for the given event type.
            self.sub = (
                omni.usd.get_context()
                .get_stage_event_stream()
                .create_subscription_to_push(
                    self._on_stage_event, name=f"omni.graph.action.__onstageevent.{node.node_id()}"
                )
            )
            self.sub_event_type = event_type
            self.node = node
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


class OgnOnStageEvent:
    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnOnStageEventInternalState()

    @staticmethod
    def release(node):
        # Unsubscribe right away instead of waiting for GC cleanup, we don't want our callback firing
        # after the node has been released.
        with suppress(og.OmniGraphError):
            state = OgnOnStageEventDatabase.per_instance_internal_state(node)
            if state.sub:
                state.sub.unsubscribe()
                state.sub = None

    @staticmethod
    def compute(db) -> bool:
        event_name = db.inputs.eventName
        if not event_name:
            return True

        state = db.per_instance_state

        # Check the validity of the input
        try:
            event_type = event_name_to_enum[event_name]
        except KeyError:
            db.log_error(f"{event_name} is not a recognized Stage Event")
            return False

        if state.first_time_subscribe(db.node, event_type):
            return True

        payload = state.try_pop_event()

        # Drop events if we are disabled, unless we are a 'stop' event - this is a special case because STOP only comes
        # after we are no longer playing.
        if (
            db.inputs.onlyPlayback
            and (not db.node.get_graph().get_default_graph_context().get_is_playing())
            and (
                event_type
                not in (
                    omni.usd.StageEventType.OMNIGRAPH_STOP_PLAY,
                    omni.usd.StageEventType.SIMULATION_STOP_PLAY,
                    omni.usd.StageEventType.ANIMATION_STOP_PLAY,
                )
            )
        ):
            return True

        if payload is None:
            return True

        get_interface().set_execution_enabled("outputs:execOut")
        return True

    # ----------------------------------------------------------------------------
    @staticmethod
    def update_node_version(context: og.GraphContext, node: og.Node, old_version: int, new_version: int):
        if old_version < new_version and old_version < 2:
            # We added inputs:onlyPlayback default true - to maintain previous behavior we should set this to false
            node.create_attribute(
                "inputs:onlyPlayback",
                og.Type(og.BaseDataType.BOOL),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                False,
            )
        return True
