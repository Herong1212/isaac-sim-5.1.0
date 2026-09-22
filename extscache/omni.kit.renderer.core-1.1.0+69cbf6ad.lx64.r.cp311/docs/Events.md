# Event Reference

All omni.kit.renderer events are based on an `omni::kit::IAppWindow` instance. The event names are composed as follows:

`omni.kit.renderer:renderer:<IAppWindow pointer>:<event name>`

The `<IAppWindow pointer>` is composed as by the `%p` printf format specifier. Event names are case sensitive.

Events with an empty `<IAppWindow pointer>` are aliased to the default window.

For ease of generating the event names for use with `carb::eventdispatcher::IEventDispatcher`, there exists
an enum {cpp:enum}`omni::kit::renderer::RendererEventType` in C++ and {py:class}`omni.kit.renderer.bind.RendererEventType` in Python.
These enums can be used with helper functions {cpp:func}`omni::kit::renderer::getRendererEventName` and
{py:func}`omni.kit.renderer.bind.get_renderer_event_name` to generate the event name. Conversely, the event name
can be passed to helper functions {cpp:func}`omni::kit::renderer::getRendererEventType` and
{py:func}`omni.kit.renderer.bind.get_renderer_event_type` to convert back to the event type enum and optionally
retrieve the `omni::kit::IAppWindow` instance as well.

## Renderer Events

As listed below, the String Event Name corresponds to the `<event name>` above.

### Pre Begin Frame

Sent on the main thread when rendering is about to start.

* C++ Enum: {cpp:enumerator}`RendererEventType::ePreBeginFrame <omni::kit::renderer::RendererEventType::ePreBeginFrame>`
* Python Enum: {py:attr}`RendererEventType.PRE_BEGIN_FRAME <omni.kit.renderer.bind.RendererEventType.PRE_BEGIN_FRAME>`
* String event name: `pre_begin_frame`

Arguments:
* `dt` (float) - Time since last frame in seconds.
* `commandListHandle` (int64) - The handle for the frame's command list.
* `saveDrawData` (bool) - If `true`, the frame won't be displayed due to prepare failure (i.e. swap-chain being resized or not ready, window minimized, etc.). `false` for a normal frame.
* `draw_frozen` (bool) - (optional) If `true`, the window's drawing is frozen.

### Pre Begin Render Pass

Sent on the main thread or present thread after Pre Begin Frame but immediately before the Begin Render Pass command is executed.

* C++ Enum: {cpp:enumerator}`RendererEventType::ePreBeginRenderPass <omni::kit::renderer::RendererEventType::ePreBeginRenderPass>`
* Python Enum: {py:attr}`RendererEventType.PRE_BEGIN_RENDER_PASS <omni.kit.renderer.bind.RendererEventType.PRE_BEGIN_RENDER_PASS>`
* String event name: `pre_begin_render_pass`

Arguments:
* `commandListHandle` (int64) - The handle for the frame's command list.
* `saveDrawData` (bool) - Always `false`.

### Render Frame

Sent on the main thread immediately after clear and before the render pass ends.

* C++ Enum: {cpp:enumerator}`RendererEventType::eRenderFrame <omni::kit::renderer::RendererEventType::eRenderFrame>`
* Python Enum: {py:attr}`RendererEventType.RENDER_FRAME <omni.kit.renderer.bind.RendererEventType.RENDER_FRAME>`
* String event name: `render_frame`

Arguments:
* `dt` (float) - Time since last frame in seconds.
* `commandListHandle` (int64) - The handle for the frame's command list.
* `saveDrawData` (bool) - If `true`, the frame won't be displayed due to prepare failure (i.e. swap-chain being resized or not ready, window minimized, etc.). `false` for a normal frame.
* `draw_frozen` (bool) - (optional) If `true`, the window's drawing is frozen.

### Post End Render Pass

Sent on the main thread or present thread after the render pass ends.

* C++ Enum: {cpp:enumerator}`RendererEventType::ePostEndRenderPass <omni::kit::renderer::RendererEventType::ePostEndRenderPass>`
* Python Enum: {py:attr}`RendererEventType.POST_END_RENDER_PASS <omni.kit.renderer.bind.RendererEventType.POST_END_RENDER_PASS>`
* String event name: `post_end_render_pass`

Arguments:
* `commandListHandle` (int64) - The handle for the frame's command list.
* `saveDrawData` (bool) - Always `false`.

### Post End Render Frame

Sent on the main thread following Post Present Frame Buffer.

* C++ Enum: {cpp:enumerator}`RendererEventType::ePostEndRenderFrame <omni::kit::renderer::RendererEventType::ePostEndRenderFrame>`
* Python Enum: {py:attr}`RendererEventType.POST_END_RENDER_FRAME <omni.kit.renderer.bind.RendererEventType.POST_END_RENDER_FRAME>`
* String event name: `post_end_render_frame`

Arguments:
* `dt` (float) - Time since last frame in seconds.
* `saveDrawData` (bool) - If `true`, the frame won't be displayed due to prepare failure (i.e. swap-chain being resized or not ready, window minimized, etc.). `false` for a normal frame.
* `draw_frozen` (bool) - (optional) If `true`, the window's drawing is frozen.

### Post Present Frame Buffer

Sent on the main thread or present thread at the end of rendering.

* C++ Enum: {cpp:enumerator}`RendererEventType::ePostPresentFrameBuffer <omni::kit::renderer::RendererEventType::ePostPresentFrameBuffer>`
* Python Enum: {py:attr}`RendererEventType.POST_PRESENT_FRAME_BUFFER <omni.kit.renderer.bind.RendererEventType.POST_PRESENT_FRAME_BUFFER>`
* String event name: `post_present_frame_buffer`

Arguments:
* `dt` (float) - Time since last frame in seconds.

### Present Render Frame

Sent on the present thread to update the viewport. Sent before Post End Render Pass.

* C++ Enum: {cpp:enumerator}`RendererEventType::ePresentRenderFrame <omni::kit::renderer::RendererEventType::ePresentRenderFrame>`
* Python Enum: {py:attr}`RendererEventType.PRESENT_RENDER_FRAME <omni.kit.renderer.bind.RendererEventType.PRESENT_RENDER_FRAME>`
* String event name: `present_render_frame`

Arguments:
* `dt` (float) - Time since last frame in seconds.
* `commandListHandle` (int64) - The handle for the frame's command list.
* `viewportDataCount` (size_t) - The number of entries in the `viewportDataPtr` array.
* `viewportDataPtr` (uintptr_t) - A value that can be casted to `omni::kit::renderer::IRendererHydraViewportData*`, an array of length `viewportDataCount`.
  **WARNING**: This pointer value may only be safely accessed in the event handler and must not be stored anywhere.

## Legacy Events

Previously, each event type was sent through a separate Event Stream. While still currently supported, this
is now deprecated.

### Converting C++

Old:
```c++
using namespace omni::kit::renderer;

IRenderer* renderer = carb::getCachedInterface<IRenderer>();
if (renderer)
{
    carb::events::IEventStream* preBeginFrameEventStream = renderer->getPreBeginFrameEventStream(appWindow);
    m_subscription = carb::events::createSubscriptionToPop(
        preBeginFrameEventStream,
        [this](carb::events::IEvents* event) { this->onPreBeginFrame(event); },
        carb::events::kDefaultOrder,
        "My subscription name"
    );
}
```

New:
```cpp
using namespace omni::kit::renderer;

auto dispatcher = carb::getCachedInterface<carb::eventdispatcher::IEventDispatcher>();
m_subscription = dispatcher->observeEvent(
    carb::RStringKey("My observer name"),
    carb::eventdispatcher::kDefaultOrder,
    getRendererEventName(RendererEventType::ePreBeginFrame, appWindow),
    [this](const carb::eventdispatcher::Event& event) { this->onPreBeginFrame(event); }
);
```

Reading arguments from the event is easier with Events 2.0 as generally `Event::getValueOr<>()` can be used
instead of reading dictionary values.

### Converting Python

Old:
```python
import omni.kit.renderer
import carb.events

renderer = omni.kit.renderer.bind.acquire_renderer_interface()
stream = renderer.get_pre_begin_frame_event_stream(app_window)

self.subscription = stream.create_subscription_to_pop(
    on_event,
    carb.events.DEFAULT_ORDER, # optional
    "My subscription name"
)
```

New:
```python
from omni.kit.renderer import bind as okr
import carb.eventdispatcher

self.subscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
    observer_name="My observer name",
    event_name=okr.get_renderer_event_name(okr.RendererEventType.PRE_BEGIN_FRAME, app_window),
    order=carb.eventdispatcher.DEFAULT_ORDER, # optional
    on_event=on_event
)
```
