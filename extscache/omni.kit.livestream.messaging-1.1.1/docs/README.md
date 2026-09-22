# Parse messages as json and push to message bus

Provides json messaging functionality between Kit and the web client using
generic messaging such as omni.kit.gfn or omni.kit.streamsdk.plugins.

It takes a message bus event of event_type `omni.kit.livestream.receive_message` and
payload `{"event_type": "SetColor", "payload": { ... }}` and parses the payload as json
and pushes a new event on the bus with event_type `SetColor` and the `payload` unpacked
to the event payload dictionary.

It also provids an API to register custom event types to listen to for sending to the client
using the generic `omni.kit.livestream.send_message` event type.

```python
import omni.kit.livestream.messaging as messaging
messaging.register_event_type_to_send("SetColor")
```
