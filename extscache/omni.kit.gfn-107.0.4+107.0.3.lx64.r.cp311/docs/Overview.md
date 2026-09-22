# GeForce NOW Runtime SDK Integration

omni.kit.gfn links Omniverse Kit with the GFN runtime SDK.
It allows startup and shutdown of the SDK, retrieving GFN partner secure data,
and communicating with the client website containing the embedded GFN stream.

## Startup

Acquire the interface and call `startup` to initialize the GFN SDK.

```python
from omni.kit.gfn import get_geforcenow_interface
gfn = get_geforcenow_interface()
gfn.startup()
```

Alternatively, set
```toml
exts."omni.kit.gfn".auto_startup_gfn = true
```
to automatically initialize the GFN SDK during extension startup.

## Session Init Callback

Register any GFN SDK Session Init callbacks before calling `startup`.

```python
from omni.kit.gfn import get_geforcenow_interface

def on_session_init(self, params):
    print("session init", params)

gfn = get_geforcenow_interface()
cb_id = gfn.register_on_session_init_callback(on_session_init)
gfn.startup()
```

Registered callback id's can be deregistered.

```python
# cleanup / shutdown
gfn.deregister_on_session_init_callback(cb_id)
```

## Sending messages

Send messages to the GFN client by using the Kit application message bus.
Use `omni.kit.livestream.send_message` for the event type, and a `message` item for the event payload.

```python
import carb.events
import omni.kit.app

event_type = carb.events.type_from_string("omni.kit.livestream.send_message")
payload = {"message": "Hello GFN!"}
message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
message_bus.push(event_type, payload=payload)
```

## Receiving messages

Receive messages from the GFN client by using the Kit application message bus.
Use `omni.kit.livestream.receive_message` for the event type, and the message will be in the `message` item of the event payload.

```python
import carb.events
import omni.kit.app

def on_event(event: carb.events.IEvent):
    message = event.payload["message"]
    print("received", message)

event_type = carb.events.type_from_string("omni.kit.livestream.receive_message")
message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
sub = message_bus.create_subscription_to_pop_by_type(event_type, on_event)
```
