import codecs
import pickle
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Iterable, Optional, Tuple

# import omni.graph.core as og
import omni.kit.app

from .type_definitions import AutoNodeDefinitionGenerator, AutoNodeDefinitionWrapper, TypeRegistry
from .util import is_private, python_name_to_ui_name, sanitize_qualname

# import carb.events


payload_path = "!path"


# ================================================================================
class IEventStream(ABC):

    _event_type = None

    def __init__(self):
        raise RuntimeError("IEventStream: interfaces can't be instantiated.")

    # --------------------------------------------------------------------------------
    @abstractmethod
    def create_subscription_to_pop(self, callback: Callable, name: Optional[str]):
        pass

    # --------------------------------------------------------------------------------
    @abstractmethod
    def create_subscription_to_self(self, callback: Callable, name: Optional[str]):
        pass

    # --------------------------------------------------------------------------------
    @abstractmethod
    def create_subscription_to_pop_by_type(self, callback: Callable, event_type: Enum, name: Optional[str]):
        pass

    # --------------------------------------------------------------------------------
    @abstractmethod
    def create_subscription_to_push_by_type(self, callback: Callable, event_type: Enum, name: Optional[str]):
        pass

    # --------------------------------------------------------------------------------
    @classmethod
    def get_event_type(cls):
        return cls._event_type

    # --------------------------------------------------------------------------------
    @classmethod
    def __class_getitem__(cls, key: Enum):
        sanitized = sanitize_qualname(key.__name__)

        def create_subscription_to_pop_by_type(self, callback: Callable, event_type: key, name: Optional[str]):
            pass

        def create_subscription_to_push_by_type(self, callback: Callable, event_type: key, name: Optional[str]):
            pass

        ret = type(
            f"IEventStream_{sanitized}",
            (cls,),
            {
                "_event_type": key,
                "create_subscription_to_pop_by_type": create_subscription_to_pop_by_type,
                "create_subscription_to_push_by_type": create_subscription_to_push_by_type,
            },
        )
        return ret


# ================================================================================
class EventSubscriptionType(Enum):
    NONE = 0
    POP = 1
    PUSH = 2
    ALL = 3


# ================================================================================
class OgnOnEventInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self, event_stream):
        """Instantiate the per-node state information."""
        # This subscription object controls the lifetime of our callback, it will be
        # cleaned up automatically when our node is destroyed
        self.sub = None
        # Set when the callback has triggered
        self.is_set = False
        # The last payload received
        self.payload = None
        # the event emitted
        # FIXME (OS): Handle push too
        self.subscription = event_stream.create_subscription_to_pop(self.on_event)

    # --------------------------------------------------------------------------------
    def on_event(self, custom_event):
        """The event callback"""
        if custom_event is None:
            return
        self.is_set = True
        self.payload = custom_event.payload

    # --------------------------------------------------------------------------------
    def try_pop_event(self):
        """Pop the payload of the last event received, or None if there is no event to pop"""
        if self.is_set:
            self.is_set = False
            payload = self.payload
            self.payload = None
            return payload
        return None


# ================================================================================
class OgnOnEvent:
    """
    This node triggers when the specified message bus event is received
    """

    def __init_subclass__(cls, event_name: str, event_stream: Callable, **kwargs):
        cls.event_name = event_name
        cls.event_stream = event_stream
        cls.event_type = kwargs.get("event_type", None)
        cls.subscription_type = kwargs.get("subscription_type", EventSubscriptionType.POP)

    # --------------------------------------------------------------------------------
    @classmethod
    def internal_state(*args):  # pylint: disable=bad-classmethod-argument
        """Returns an object that will contain per-node state information"""
        cls = args[0]
        internal_state = OgnOnEventInternalState(cls.event_stream)
        return internal_state

    # --------------------------------------------------------------------------------
    @classmethod
    def initialize(*args):  # pylint: disable=bad-classmethod-argument
        # cls = args[0]
        # graph_context = args[1]
        # node = args[2]
        pass

    # --------------------------------------------------------------------------------
    @classmethod
    def release(*args):  # pylint: disable=bad-classmethod-argument
        # node = args[1]
        pass

    # --------------------------------------------------------------------------------
    @classmethod
    def compute(*args) -> bool:  # pylint: disable=bad-classmethod-argument
        """Compute the outputs from the current input"""
        # cls = args[0]
        db = args[1]

        state = db.internal_state

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

        db.outputs.execOut = True
        return True


# ================================================================================
class AutoNodeEventStreamWrapper(AutoNodeDefinitionWrapper):
    def __init__(self, event_stream: IEventStream, event_name: str, module_name: str, **kwargs):
        super().__init__()
        self.event_name = event_name
        self.event_stream = event_stream
        self.event_type = event_stream.get_event_type()
        self.module_name = module_name
        self.subscription_type = kwargs.get("subscription_type", EventSubscriptionType.POP)

    # --------------------------------------------------------------------------------
    def get_ogn(self):
        event_ogn = {
            f"On{self.event_name}": {
                "description": [
                    "Event node which fires when the specified custom event is sent.",
                    "This node is used in combination with SendCustomEvent",
                ],
                "version": 1,
                "uiName": f"On {python_name_to_ui_name(self.event_name)}",
                "language": "Python",
                "state": {},
                "inputs": {},
                "outputs": {
                    "path": {
                        "type": "token",
                        "description": "The path associated with the received custom event",
                        "uiName": "Path",
                    },
                    "bundle": {"type": "bundle", "description": "Bundle received with the event", "uiName": "Bundle"},
                    "execOut": {
                        "type": "execution",
                        "description": "Executes when the event is received",
                        "uiName": "Received",
                    },
                },
            }
        }

        return event_ogn

    # --------------------------------------------------------------------------------
    def get_node_impl(self):
        class OgnOnEventWrapper(
            OgnOnEvent, event_name=self.event_name, event_stream=self.event_stream, event_type=self.event_type
        ):
            pass

        return OgnOnEventWrapper

    # --------------------------------------------------------------------------------
    def get_unique_name(self):
        return self.event_name

    # --------------------------------------------------------------------------------
    def get_module_name(self):
        return self.module_name


# ================================================================================
class OgnForwardEventInternalState:
    """Convenience class for maintaining per-node state information"""

    # --------------------------------------------------------------------------------
    def __init__(self, event_stream):
        """Instantiate the per-node state information."""
        # This subscription object controls the lifetime of our callback, it will be
        # cleaned up automatically when our node is destroyed
        self.event_stream: IEventStream = event_stream
        self.event_name: str = ""
        self.subscription = None

    # --------------------------------------------------------------------------------
    def start_forwarding(self):
        # FIXME (OS): Handle push too
        self.subscription = self.event_stream.create_subscription_to_pop(self.on_event)

    # --------------------------------------------------------------------------------
    def stop_forwarding(self):
        self.subscription = None

    # --------------------------------------------------------------------------------
    def on_event(self, custom_event):
        """The event callback"""
        if custom_event is None:
            return
        # Returns the internal name used for the given custom event name
        n = "omni.graph.action." + self.event_name
        omni.kit.app.queue_event(n, custom_event)


# ================================================================================
class OgnForwardEvent:
    """
    This node triggers when the specified message bus event is received
    """

    # --------------------------------------------------------------------------------
    def __init_subclass__(cls, event_name: str, event_stream: Callable, **kwargs):
        cls.event_name = event_name
        cls.event_stream = event_stream
        cls.event_type = kwargs.get("event_type", None)
        cls.subscription_type = kwargs.get("subscription_type", EventSubscriptionType.POP)

    # --------------------------------------------------------------------------------
    @classmethod
    def internal_state(*args):  # pylint: disable=bad-classmethod-argument
        """Returns an object that will contain per-node state information"""
        cls = args[0]
        internal_state = OgnForwardEventInternalState(cls.event_stream)
        return internal_state

    # --------------------------------------------------------------------------------
    @classmethod
    def compute(*args) -> bool:  # pylint: disable=bad-classmethod-argument
        """Compute the outputs from the current input"""
        # cls = args[0]
        db = args[1]

        state = db.internal_state

        if db.inputs.start_forwarding:
            evstream_id = db.inputs.event_stream
            state.event_stream = TypeRegistry.remove_from_graph(evstream_id).value
            state.event_name = db.inputs.event_name
            state.start_forwarding()
        if db.inputs.stop_forwarding:
            state.stop_forwarding()

        db.outputs.execOut = True
        return True


# ================================================================================
class AutoNodeEventStreamForwardWrapper(AutoNodeDefinitionWrapper):
    def __init__(self, event_stream: IEventStream, event_name: str, module_name: str, **kwargs):
        super().__init__()
        self.event_name = event_name
        self.event_stream = event_stream
        self.event_type = event_stream.get_event_type()
        self.module_name = module_name
        self.subscription_type = kwargs.get("subscription_type", EventSubscriptionType.POP)

    # --------------------------------------------------------------------------------
    def get_ogn(self):
        event_ogn = {
            f"Forward{self.event_name}": {
                "description": [
                    "This event forwards the output of this event stream to another named event stream",
                    "It can be used in combination with OnCustomEvent.",
                ],
                "version": 1,
                "uiName": f"Forward {python_name_to_ui_name(self.event_name)}",
                "language": "Python",
                "state": {},
                "inputs": {
                    "start_forwarding": {
                        "description": "Trigger this to begin forwarding events from the wrapped event stream"
                        " to the main event stream",
                        "type": "execution",
                        "uiName": "Start forwarding events",
                    },
                    "stop_forwarding": {
                        "description": "Trigger this to stop any event forwarding to the main event stream.",
                        "type": "execution",
                        "uiName": "Stop forwarding",
                    },
                    "event_stream": {
                        "description": "Event stream to forward from",
                        "type": "objectId",
                        "uiName": "Event stream",
                        "metadata": {"python_type_desc": "IEventStream"},
                    },
                    "event_name": {
                        "description": "Name for outgoing events, to be used in 'On Custom Event' nodes.",
                        "type": "string",
                        "uiName": "Event Name",
                    },
                },
                "outputs": {
                    "execOut": {
                        "type": "execution",
                        "description": "Executes when the event is received",
                        "uiName": "Received",
                    }
                },
            }
        }

        return event_ogn

    # --------------------------------------------------------------------------------
    def get_node_impl(self):
        class OgnForwardEventWrapper(
            OgnForwardEvent, event_name=self.event_name, event_stream=self.event_stream, event_type=self.event_type
        ):
            pass

        return OgnForwardEventWrapper

    # --------------------------------------------------------------------------------
    def get_unique_name(self):
        return self.event_name

    # --------------------------------------------------------------------------------
    def get_module_name(self):
        return self.module_name


# ================================================================================
class EventAutoNodeDefinitionGenerator(AutoNodeDefinitionGenerator):

    _name = "IEventStream"

    # --------------------------------------------------------------------------------
    @classmethod
    def generate_from_definitions(  # noqa: PLW0221
        cls, target_type: type, type_name_sanitized: str, type_name_short: str, module_name: str
    ) -> Tuple[Iterable[AutoNodeDefinitionWrapper], Iterable[str]]:

        members_covered = set()
        generators = set()

        if issubclass(target_type, IEventStream):
            generators.add(
                AutoNodeEventStreamWrapper(
                    event_stream=target_type, event_name=type_name_short, module_name=module_name
                )
            )
            generators.add(
                AutoNodeEventStreamForwardWrapper(
                    event_stream=target_type, event_name=type_name_short, module_name=module_name
                )
            )
            members_covered.update(key for key in IEventStream.__dict__ if not is_private(key))

        return generators, members_covered
