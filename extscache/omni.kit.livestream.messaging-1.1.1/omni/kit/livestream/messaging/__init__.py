from .scripts.extension import *

def register_event_type_to_send(event_name: str):
    "Register a new event_name to monitor message bus for sending to client"
    LivestreamMessaging.instance.register_event_type_to_send(event_name)

def unregister_event_type_to_send(event_name: str):
    "Unregister an event_name to stop monitoring to send"
    LivestreamMessaging.instance.unregister_event_type_to_send(event_name)

def clear_event_types_to_send():
    "Clear all event names from monitoring to send"
    LivestreamMessaging.instance.clear_event_types_to_send()
