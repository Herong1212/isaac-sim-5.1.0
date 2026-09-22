# omni.usd Event Reference

All omni.usd events are based on the USD Context name. The default Context is an empty string (`""`). The USD Context
name should be inserted where `<context>` appears in event names below.

## Stage Events

Stage events follow the naming scheme `omni.usd:<context>:stage:<event>`. The events are listed in the {cpp:enum}`omni::usd::StageEventType` enum.
Helper functions {cpp:func}`omni::usd::UsdContext::stageEventName` and {py:func}`omni.usd.UsdContext.stage_event_name` exist to produce an
event name from the `StageEventType` enum value and the USD Context's name. The reverse of this are the helper functions
{cpp:func}`omni::usd::stageEventType` and {py:func}`omni.usd.stage_event_type` which take the stage event name and return
the corresponding `StageEventType` enum value.

For brevity, only the `<event>` portion of the event name appears in the list below.

### Saving

Event: `saving`

Dispatched before saving begins.

Parameters:
* `savingSublayers` (array of strings) - the sublayer paths that are being saved.
* `savingRootLayer` (string) - [optional] the new root layer path.

### Saved

Event: `saved`

Dispatched when saving has completed successfully.

Parameters:
* `savedLayers` (array of strings) - the layer paths that were saved.

### Save Failed

Event: `save_failed`

Dispatched when and if a stage save fails.

Parameters:
* `cancelled` (bool) - [optional] If true, the failure was due to cancellation.

### Opening

Event: `opening`

Dispatched after the previous stage has closed but before loading a new URL, creating a new stage, or transferring a stage.

Parameters:
* `val` (string) - The stage URL that will be opened, or an empty string for a new stage.

### Opened

Event: `opened`

Dispatched after a new stage has been created, a stage has been transferred, or a stage URL has been opened successfully.

Parameters:
* `val` (string) - The stage URL that was opened, or the name of the default prim for a new stage.

### Open Failed

Event: `open_failed`

Dispatched if a failure occurs when opening a stage URL, creating a new stage, or transferring a stage.

Parameters:
* `val` (string) - [optional] The stage URL that was opened, or the name of the default prim for a new stage.

### Closing

Event: `closing`

Dispatched when a stage begins closing.

Parameters: None

### Closed

Event: `closed`

Dispatched when a stage has finished closing.

Parameters: None

### Selection Changed

Event: `selection_changed`

Dispatched during frame update if the USD prim selection has changed.

Parameters:
* `source` (string) - The source reporting selection change. Currently either `usd` or `fabric`.

### Assets Loading

Event: `assets_loading`

Dispatched during frame update if asset load has started.

Parameters: None

### Assets Loaded

Event: `assets_loaded`

Dispatched during frame update if asset load has completed, that is, no assets are currently loading after `assets_loading` was dispatched.

Parameters: None

### Gizmo Tracking Changed

Event: `gizmo_tracking_changed`

Dispatched during render if an object was picked (hovered) and is now not, or vice versa.

Parameters:
* `tracked` (bool) - whether an object is currently tracked or not.

### Settings Loaded

Event: `settings_loaded`

Dispatched after settings have been loaded (or reset) for the stage.

Parameters: None

### Settings Saved

Event: `settings_saving`

Dispatched after `saving` when the settings begin to be saved.

Parameters: None

### OmniGraph Start Play

Event: `og_start_play`

Dispatched during frame update if the stage has started OmniGraph execution.

Parameters: None

### OmniGraph Stop Play

Event: `og_stop_play`

Dispatched during frame update if the stage has stopped OmniGraph execution.

Parameters: None

### Simulation Start Play

Event: `sim_start_play`

Dispatched during frame update if the stage has started to play the simulation.

Parameters: None

### Simulation Stop Play

Event: `sim_stop_play`

Dispatched during frame update if the stage has stopped playing the simulation.

Parameters: None

### Animation Start Play

Event: `anim_start_play`

Dispatched during frame update if the stage has started to play animations.

Parameters: None

### Animation Stop Play

Event: `anim_stop_play`

Dispatched during frame update if the stage has stopped playing animations.

Parameters: None

### Dirty State Changed

Event: `dirty_state_changed`

Dispatched during frame update if the stage has changes that are not yet saved.

Parameters: None

### Active Light Count Changed

Event: `active_lights_changed`

Dispatched during frame update if the number of active lights has changed.

Parameters:
* `activeLightsCount` (string) - A string representing the number of lights.

### Hierarchy Changed

Event: `hierarchy_changed`

Dispatched during `PXR_NS::UsdNotice::ObjectsChanged` notice listener if the list of re-synced paths contains an absolute
root or prim path.

Parameters: None

## Rendering Events

Stage Rendering events follow the naming scheme `omni.usd:<context>:rendering:<event>`. The events are listed in the {cpp:enum}`omni::usd::StageRenderingEventType` enum.
Helper functions {cpp:func}`omni::usd::UsdContext::stageRenderingEventName` and {py:func}`omni.usd.UsdContext.stage_rendering_event_name` exist to produce an
event name from the `StageRenderingEventType` enum value and the USD Context's name. The reverse of this are the helper functions
{cpp:func}`omni::usd::stageRenderingEventType` and {py:func}`omni.usd.stage_rendering_event_type` which take the stage event name and return
the corresponding `StageRenderingEventType` enum value.

Stage Rendering events can be `immediate`, that is, immediately when the situation occurs that causes the event, or
*deferred* to a safer point slightly later. In most cases it is recommended to use the *deferred* event. This is specified
as an optional argument to the above functions.

For brevity, only the `<event>` portion of the event name appears in the list below.

### New Frame

Event: `new_frame`

Dispatched when a new rendering frame completes and becomes available for a Viewport.

Parameters:
* `viewport_handle` (uint64) - the viewport handle.
* `swh_frame_number` (int64) - the frame number from the `FrameIdentifier` in `results`.
* `results` (uint64) - pointer to `omni::usd::hydra::HydraRenderProduct`.
* `product_path_handle` (uint64) - `omni::usd::PathH` path handle.
* `frame_number` (int64) - the frame number from `results`; total number of frames rendered.
* `render_status` (`omni::usd::hydra::RenderStatus`) - render status from `result`.
* `progression` (uint32) - progression, e.g. samples per pixel from path tracing.
* `stats` (uint64) - pointer to `omni::usd::hydra::HydraRenderStats`, may be `nullptr`.

### Hydra Engine Frames Added/Complete

Event: `frames_added`

Dispatched when frames are added to the GPU queue for a single hydra engine, but has not been
rendered yet. This event may not have the `render_results` parameter listed below.


Event: `frames_complete`

Dispatched when frames are complete for a single hydra engine render() invocation.

Parameters:
* `average_frame_time_ns` (float) - the average frame time in nanoseconds.
* `swh_frame_number` (int64) - the frame number from the `FrameIdentifier` in the first viewport result.
* `render_results` (`carb::variant::VariantArrayPtr` [C++] / `tuple` [py]) [optional] - An array of `carb::variant::VariantMap` [C++] or `dict` [py] objects with the following key/value pairs:
  * `viewport_handle` (uint64) - the viewport handle.
  * `product` (uint64) - pointer to `omni::usd::hydra::HydraRenderProduct`.
  * `subframe_count` (int32) - sub-frame count.

### Recording Complete

Event `recording_complete`

Dispatched when recording of the frame is complete, but the frame has not yet been submitted for
execution.

Parameters:
* `results` (uint64) - pointer to `omni::usd::hydra::HydraRenderProduct`.
* `product_path_handle` (uint64) - `omni::usd::PathH` path handle.
* `rendergraph` (`carb::IObjectPtr`) - pointer to `gpu::rendergraph::IRenderGraph`.
