"""
This is the implementation of the OGN node defined in OgnOnCustomEvent.ogn
"""

import codecs
import pickle
from contextlib import suppress

import carb.events
import omni.graph.core as og
import omni.kit.app
from omni.graph.action_core import get_interface
from omni.graph.action_nodes.ogn.OgnOnCustomEventDatabase import OgnOnCustomEventDatabase


def registered_event_name(event_name):
    """Returns the internal name used for the given custom event name"""
    n = "omni.graph.action." + event_name
    return carb.events.type_from_string(n)


payload_path = "!path"


class OgnOnCustomEventInternalState:
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
        # The event_name we used to subscribe
        self.sub_event_name = ""
        # The node instance handle
        self.node = None

    def on_event(self, custom_event):
        """The event callback"""
        if custom_event is None:
            return
        self.is_set = True
        self.payload = custom_event.payload
        # Tell the evaluator we need to be computed
        if self.node.is_valid():
            self.node.request_compute()

    def first_time_subscribe(self, node: og.Node, event_name: str) -> bool:
        """Checked call to set up carb subscription
        Args:
            node: The node instance
            event_name: The name of the carb event
        Returns:
            True if we subscribed, False if we are already subscribed
        """
        if self.sub is not None and self.sub_event_name != event_name:
            # event name changed since we last subscribed, unsubscribe
            self.sub.unsubscribe()
            self.sub = None

        if self.sub is None:
            # Add a subscription for the given event name. This is a pop subscription, so we expect a 1-frame
            # lag between send and receive
            reg_event_name = registered_event_name(event_name)
            message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
            self.sub = message_bus.create_subscription_to_pop_by_type(reg_event_name, self.on_event)
            self.sub_event_name = event_name
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


class OgnOnCustomEvent:
    """
    This node triggers when the specified message bus event is received
    """

    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnOnCustomEventInternalState()

    @staticmethod
    def compute(db) -> bool:
        event_name = db.inputs.eventName
        if not event_name:
            return True

        state = db.per_instance_state

        if state.first_time_subscribe(db.node, event_name):
            return True

        # Drop events if we are disabled
        if db.inputs.onlyPlayback and (not db.node.get_graph().get_default_graph_context().get_is_playing()):
            state.try_pop_event()
            return True

        payload = state.try_pop_event()

        if payload is None:
            return True

        # Copy the event dict contents into the output bundle
        db.outputs.bundle.clear()
        for name in payload.get_keys():
            # Special 'path' entry gets copied to output attrib
            if name == payload_path:
                db.outputs.path = payload[name]
                continue
            as_str = payload[name]
            arg_obj = pickle.loads(codecs.decode(as_str.encode(), "base64"))
            attr_type, attr_value = arg_obj
            new_attr = db.outputs.bundle.insert((attr_type, name))
            new_attr.value = attr_value

        get_interface().set_execution_enabled("outputs:execOut")
        return True

    # ----------------------------------------------------------------------------
    @staticmethod
    def release(node):
        # Unsubscribe right away instead of waiting for GC cleanup, we don't want our callback firing
        # after the node has been released.
        with suppress(og.OmniGraphError):
            state = OgnOnCustomEventDatabase.per_instance_internal_state(node)
            if state.sub:
                state.sub.unsubscribe()
                state.sub = None

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
