"""
This is the implementation of the OGN node defined in OgnSendCustomEvent.ogn
"""

import codecs
import pickle

import carb.events
import omni.kit.app
from omni.graph.action_core import get_interface


def registered_event_name(event_name):
    """Returns the internal name used for the given custom event name"""
    n = "omni.graph.action." + event_name
    return carb.events.type_from_string(n)


payload_path = "!path"


# ======================================================================
class OgnSendCustomEvent:
    """
    This node triggers when the specified message bus event is received
    """

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""

        event_name = db.inputs.eventName
        if not event_name:
            return True

        path = db.inputs.path
        input_bundle = db.inputs.bundle

        reg_event_name = registered_event_name(event_name)
        message_bus = omni.kit.app.get_app().get_message_bus_event_stream()

        payload = {}

        if input_bundle.valid:
            # Copy the contents of the input bundle into the event dict
            for attr in input_bundle.attributes:
                tp = attr.type
                arg_obj = (tp, attr.value)
                # Since we are python at both ends, easiest to pickle the attrib values so we
                # can re-animate them on the other side
                as_str = codecs.encode(pickle.dumps(arg_obj), "base64").decode()
                payload[attr.name] = as_str

        if path:
            payload[payload_path] = path

        message_bus.push(reg_event_name, payload=payload)

        get_interface().set_execution_enabled("outputs:execOut")

        return True
