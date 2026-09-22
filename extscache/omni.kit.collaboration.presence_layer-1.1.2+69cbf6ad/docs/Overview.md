```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Introduction
Presence Layer works for providing storage to exchange persistent data for all users in the same
Live Session (see module {py:mod}`omni.kit.usd.layers`). The theory is that it uses .live layer as transport layer, on top of which all user data is structured as USD prim. It provides
easy API to access the data without using raw USD API, and also event stream to subscribe the data changes. Currently,
it's used for spatial awareness, which includes the following applications:

* Bound Camera.
* Selections.
* User Following.

User can exchange and synchronize their local states of the above applications into the Presence Layer for other users to be aware of.

# Limitation
Currently, Presence Layer is created only when Root Layer enters a Live Session, no support for other layers in the layer stack.

# How can I Extend Precense Layer to Share Data not Listed?
Presence Layer currently exposes the raw underlying storage, which is a USD stage, so it shares all the benefits of USD and you can operate the stage with USD API to extend your own functionality. You can see {py:class}`omni.kit.collaboration.presence_layer.PresenceAPI` for reference.

# Programming Guide
## Subscribe Spatial Awareness Events
Here is an example to subscribe spatial awareness events with Presence Layer, in a stage (specifically the Root Layer) that has already joined a Live Session (see {py:class}`omni.kit.usd.layers.LiveSyncing`):

```python
import omni.usd
import omni.kit.usd.layers as layers
import omni.kit.collaboration.presence_layer as pl

def _on_layers_event(event):
    nonlocal payload
    p = pl.get_presence_layer_event_payload(event)

    if not p.event_type:
        return

    if p.event_type == pl.PresenceLayerEventType.SELECTIONS_CHANGED:
        ... # Peer Client's selections changed.
    elif p.event_type == pl.PresenceLayerEventType.LOCAL_FOLLOW_MODE_CHANGED:
        ... # Local Client enters into following mode.
    elif p.event_type == pl.PresenceLayerEventType.BOUND_CAMERA_CHANGED:
        ... # Peer Client changes its bound camera.
    elif p.event_type == pl.PresenceLayerEventType.BOUND_CAMERA_PROPERTIES_CHANGED:
        ... # Peer Client changes the properties of its bound camera.
    elif p.event_type == pl.PresenceLayerEventType.BOUND_CAMERA_RESYNCED:
        ... # Peer Client's bound camera resynced.

usd_context = omni.usd.get_context()
layers_interface = layers.get_layers(usd_context)
subscription = layers_interface.get_event_stream().create_subscription_to_pop(
    _on_layers_event, name="xxxxxxxxx"
)
...
```

As you can see above, all events from Presence Layer are sent through event stream from {py:class}`omni.kit.usd.layers.Layers` as Presence Layer is part of Live Syncing workflow.

## Send Spatial Awareness Events with Scripting
```python
import omni.usd
import omni.kit.collaboration.presence_layer as pl

...

usd_context = omni.usd.get_context()

# Gets instance of Presence Layer bound to an UsdContext.
presence_layer = pl.get_presence_layer_interface(usd_context)

# Boradcasts local bound camera to other clients
your_bound_camera_path = ...
presence_layer.broadcast_local_bound_camera(your_local_camera_path)

# Enters into following mode
following_user_id = ...
presence_layer.enter_follow_mode(following_user_id)
...

# Quits following mode
presence_layer.quit_follow_mode()
```

You can refer {py:class}`omni.kit.usd.layers.LiveSyncing` and {py:class}`omni.kit.usd.layers.LiveSession` about how to get the current Live Session and all of its joined users.
