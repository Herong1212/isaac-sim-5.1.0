import json
import carb
import carb.events
import carb.settings
import omni.ext
import omni.kit.app


class LivestreamMessaging(omni.ext.IExt):
    instance = None

    def __init__(self):
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._receive_event_sub = None
        self._send_event_names = {}
        self._send_event_subs = {}
        self._sender_id = 0

    def on_startup(self):
        # Setup to receive messages from gfn or livestream plugins
        event_type = carb.events.type_from_string(self._settings.get("exts/omni.kit.livestream.messaging/receive_message_event"))
        bus = omni.kit.app.get_app().get_message_bus_event_stream()
        self._receive_event_sub = bus.create_subscription_to_pop_by_type(event_type, self._on_message_received)

        self._sender_id = carb.events.acquire_events_interface().acquire_unique_sender_id()

        LivestreamMessaging.instance = self

    def on_shutdown(self):
        self.clear_event_types_to_send()
        carb.events.acquire_events_interface().release_unique_sender_id(self._sender_id)
        LivestreamMessaging.instance = None

    def register_event_type_to_send(self, event_name: str):
        "Register a new event_name to monitor message bus for sending to client"
        event_type = carb.events.type_from_string(event_name)
        self._send_event_names[event_type] = event_name
        bus = omni.kit.app.get_app().get_message_bus_event_stream()
        self._send_event_subs[event_type] = bus.create_subscription_to_pop_by_type(event_type, self._on_message_to_send)

    def unregister_event_type_to_send(self, event_name: str):
        "Unregister an event_name to stop monitoring to send"
        event_type = carb.events.type_from_string(event_name)
        if event_type in self._send_event_subs:
            self._send_event_subs[event_type].unsubscribe()
            del self._send_event_subs[event_type]
            del self._send_event_names[event_type]

    def clear_event_types_to_send(self):
        "Clear all event names from monitoring to send"
        names = list(self._send_event_names.values())
        for name in names:
            self.unregister_event_type_to_send(name)

    def _on_message_received(self, event: carb.events.IEvent):
        if "message" in event.payload:
            try:
                event_dict = json.loads(event.payload["message"])
            except json.JSONDecodeError as e:
                carb.log_warn(f"Message received is not valid json: {e}")
                return
            # Unpack new event_type and payload inside message
            if "event_type" in event_dict and "payload" in event_dict:
                new_event_type = carb.events.type_from_string(event_dict["event_type"])
                new_payload = event_dict["payload"]
                bus = omni.kit.app.get_app().get_message_bus_event_stream()
                bus.push(new_event_type, sender=self._sender_id, payload=new_payload)
            else:
                carb.log_warn("Message received without 'event_type' and 'payload' keys")
        else:
            carb.log_error("Message received without 'message' key")

    def _on_message_to_send(self, event: carb.events.IEvent):
        # Avoid feedback loop if we were the one to convert and send the message
        if event.sender == self._sender_id:
            return

        if event.type in self._send_event_names:
            # Wrap in generic event type which gfn and livestream plugins listen for
            new_event_type = carb.events.type_from_string(self._settings.get("exts/omni.kit.livestream.messaging/send_message_event"))
            new_payload_dict = {
                "event_type": self._send_event_names[event.type],
                "payload": event.payload.get_dict(),
            }
            new_payload = json.dumps(new_payload_dict)
            bus = omni.kit.app.get_app().get_message_bus_event_stream()
            bus.push(new_event_type, sender=self._sender_id, payload={"message": new_payload})
        else:
            carb.log_error("Message to send event name not found")
