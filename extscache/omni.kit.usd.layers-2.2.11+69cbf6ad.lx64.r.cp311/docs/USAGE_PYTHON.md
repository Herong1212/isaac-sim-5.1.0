(usage-python)=

# Python Usage Examples
Currently, it supports both C++ and Python APIs to query layer states and control workflows. However, Python is full-fledged and the recommended way
to access all APIs. Therefore, it will only introduce the steps for accessing Python APIs below.

## General Usages

### Gets Interfaces Bound to a UsdContext
All APIs are under module {py:mod}`omni.kit.usd.layers`, and each {py:class}`omni.usd.UsdContext` has a separate instance of {py:class}`omni.kit.usd.layers.Layers`, through which you can get all interfaces. Here are the common steps to use Python APIs for accessing different interfaces:

1. Imports package:

```python
   import omni.kit.usd.layers as layers
```

2. Gets layers instance to specific UsdContext:

```python
   layers_interface = layers.get_layers(usd_context_name or instance_of_usd_context)
```

3. Gets specific interfaces:

```python
   layers_state = layers_interface.get_layers_state()       # Layer State Management Interfaces
   live_syncing = layers_interface.get_live_syncing()       # Live Session Interfaces
   auto_authoring = layers_interface.get_auto_authoring()   # Auto Authoring Interfaces
   specs_linking = layers_interface.get_specs_linking()     # Specs Linking Interfaces
   specs_locking = layers_interface.get_specs_locking()     # Specs Locking Interfaces
   ...
```

4. If you want to subscribe state changes from layers:

```python
   def on_events(events: carb.events.IEvent):
       payload = layers.get_layer_event_payload(events)
       if payload.event_type == layers.LayerEventType.XXXXXX:
           ...
       ...

   subscription = layers.get_event_stream().create_subscription_to_pop(on_events, name="xxxx")
   ...
```

### Subsribing to Changes
All state changes or notifications from all interfaces under module {py:mod}`omni.kit.usd.layers` are notified in the same Carbonite event stream, you can access it through the layers instance like:
```python
   def on_events(events: carb.events.IEvent):
       payload = layers.get_layer_event_payload(events)
       if payload.event_type == layers.LayerEventType.XXXXXX:
           ...
       ...
   layers_interface = layers.get_layers(usd_context_name or instance_of_usd_context)
   subscription = layers_interface.get_event_stream().create_subscription_to_pop(on_events, name="xxxx")
   ...
```
It's recommended to use {py:func}`carb.events.IEventStream.create_subscription_to_pop_by_type` to only subscribe events that you are interested
instead of monitoring all to avoid over-subscription. For all event types, you can refer {py:class}`omni.kit.usd.layers.LayerEventType`
to provide more information.

### Layer Commands and Utils
Besides those interfaces, module {py:mod}`omni.kit.usd.layers` also provides {py:class}`omni.kit.usd.layers.LayerUtils` to operate layers easily,
and undoable commands for layer operations.

### Error Handling
For all APIs, you can check the return value to see if the API call is failed or not. If you want to get more information, you can get the
detailed error type with function {py:func}`omni.kit.usd.layers.Layers.get_last_error_type` and string with function {py:func}`omni.kit.usd.layers.Layers.get_last_error_string`. See {py:class}`omni.kit.usd.layers.LayerErrorType` for all error types and its description.
REMINDER: you need to check the error type after the API call immediately as new API call will clear the error type.

## Threading Safety
All interfaces of module {py:mod}`omni.kit.usd.layers` are not thread-safe. They should be called in the same loop/thread as the UsdContext it binds to.

## Examples
This section will provide examples and tutorials for specific applications.

### Example 1: Create, Join/Stop, and query a Live Session for Root Layer
```python
import omni.usd
import omni.kit.usd.layers as layers

usd_context = omni.usd.get_context()
stage = usd_context.get_stage()

layers_interface = layers.get_layers(usd_context)
live_syncing = layers_interface.get_live_syncing()

root_layer = stage.GetRootLayer()
session_name = "test"
live_session = live_syncing.find_live_session_by_name(root_layer.identifier, "test")

# If session does not exist, creating a new one.
if not live_session:
   live_session = live_syncing.create_live_session("test", layer_identifier=root_layer.identifier)

success = live_syncing.join_live_session(live_session)
...

# Gets the current Live Session for specific layer.
current_live_session = live_syncing.get_current_live_session(root_layer.identifier)
...

# Checks if a base layer is in Live Session.
in_live_session = live_syncing.is_layer_in_live_session(root_layer.identifier)
...

# Stops Live Session.
live_syncing.stop_live_session(self.root_layer.identifier)
```