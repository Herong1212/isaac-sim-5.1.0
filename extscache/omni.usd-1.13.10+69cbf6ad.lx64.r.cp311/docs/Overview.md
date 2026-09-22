```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

## Introduction

The Omni USD extension ({py:mod}`omni.usd`) is the Python frontend of {py:mod}`omni.usd.core`. It serves to load and initialize Pixar USD library, and Omniverse USD Resolver that supports opening USD from Omniverse/HTTP urls. It
provides synchronous and asynchronous interfaces in C++ and Python to manage {py:class}`omni.usd.UsdContext`, which will be introduced in section [UsdContext](#usdcontext). Besides those, this extension also provides common utilities and undoable commands for wrapped USD operations that can be shared for other extensions. It is the foundation component for all other extentions that need to access USD.

## UsdContext
{py:class}`omni.usd.UsdContext` is the container for a {cpp:class}`PXR_NS::UsdStage` that manages the lifecycle of a UsdStage instance. Because of historical reasons, UsdContext also undertakes extra responsibilities, including managing Hydra Engines
and rendering threads, selections, and etc. Developers can create multiple instances of UsdContext, while
a default instance of UsdContext is instantiated after initialization of **omni.usd** extension, which can be accessed through API {py:func}`omni.usd.get_context`. Most of the components instantiated by Kit application use default UsdContext as the source of a UsdStage, like Viewport, Stage Window, and Layer Window. Therefore, all status changes from default UsdContext and all authoring to the stage inside it will be synced by those components, and rendered if they are enabled.

## Programming Guide
The following section mainly introduces how to program with {py:mod}`omni.usd` in Python. For its C++ counterpart, you can refer to class {cpp:class}`omni::usd::UsdContext` for reference.

### UsdContext
As mentioned above, UsdContext is a thin container for a UsdStage. It doesn't encapsulate all APIs of UsdStage, but
exposes the UsdStage instance for developers to interact with, so that developers could still use native USD API to interact with a stage.

#### How to Access Default UsdContext and Manage Stage
Here are the common steps to get the default UsdContext and open/close a stage.

##### Python

1. Import package:

```python
   import omni.usd
```

2. Get the default UsdContext:

```python
   usd_context = omni.usd.get_context()
```

3. Open a stage:

```python
   result, error_str = await usd_context.open_stage_async(stage_url)

   # Gets UsdStage handle
   stage = usd_context.get_stage()
```

4. Save a stage:

UsdContext provides APIs to save stage. Unlike the USD API {py:func}`Usd.Stage.Save`, {py:func}`omni.usd.UsdContext.save_stage_async`,  {py:func}`omni.usd.UsdContext.save_as_stage_async` or {py:func}`omni.usd.UsdContext.save_layers_async` only saves layers in the local layer stack. It also provides more options for developers to choose
which set of layers to save.

```python
   # Saves the current stage (all layers in the local layer stack).
   result, error_str = await usd_context.save_stage_async()

   ...
   # Saves the current stage to a new location.
   result, error_str = await usd_context.save_as_stage_async(new_location_url)

   ...
   # Saves a specified set of layers only.
   result, error_str, saved_layers = await usd_context.save_layers_async("", list_of_layer_identifiers)

   ...
   # Saves a specified set of layers and also save-as root layer to a new location.
   # Unlike save_as_stage_async, it only saves those layers specified if they have pending edits. Those
   # layers that are not given but have pending edits will keep pending edits still.
   result, error_str, saved_layers = await usd_context.save_layers_async(new_root_location, list_of_layer_identifiers)
```

5. Close a stage:

```python
   error_str = await usd_context.close_stage_async()
```

You can also attach an already opened stage with USD API to the UsdContext, like so:

```python
   from pxr import Usd
   stage = Usd.Stage.Open(stage_url)

   # More setups to stage before it's attached to a UsdContext.
   ...

   result, error_str = await usd_context.attach_stage_async(stage)
```

Along with those async APIs, synchronous APIs are supported also without "_async" suffix. It's recommended to use asynchronous
APIs to avoid blocking main thread.

##### C++
In C++, you need to include header `<omni/usd/UsdContext.h>` to access UsdContext.

```cpp
#include <omni/usd/UsdContext.h>

...
auto usdContext = omni::usd::UsdContext::getContext();
...
```

### How to subscribe to Stage Events

See the [Event Reference](./Events).

Through the APIs of UsdContext, developers can also query status changes of the stage with
{py:func}`omni.usd.UsdContext.get_stage_state`, and subscribe to event changes via {py:class}`carb.eventdispatcher.IEventDispatcher`:

#### Python
```python
import omni.usd
import carb
import carb.eventdispatcher


def on_stage_opening(event: carb.eventdispatcher.Event):
   pass

def on_stage_opened(event: carb.eventdispatcher.Event):
   pass

def on_stage_closing(event: carb.eventdispatcher.Event):
   pass

usd_context = omni.usd.get_context()
observers = [
    get_eventdispatcher().observe_event(
       observer_name="my observer name for debugging",
       event_name=usd_context.stage_event_name(event),
       on_event=func
    )
    for event, func in (
       (omni.usd.StageEventType.OPENING, on_stage_opening),
       (omni.usd.StageEventType.OPENED, on_stage_opened),
       (omni.usd.StageEventType.CLOSING, on_stage_closing),
       # ...
    )
]

# When the observers list is cleared to None, the observation of the events will end.
```

#### C++

```cpp
#include <omni/usd/UsdContext.h>
#include <carb/eventdispatcher/IEventDispatcher.h>

// ...

auto usdContext = omni::usd::UsdContext::getContext();
auto stageEvtObs = carb::getCachedInterface<carb::eventdispatcher::IEventDispatcher>()->observeEvent(
    carb::RStringKey("my observer name for debugging"),
    carb::eventdispatcher::kDefaultOrder,
    usdContext->stageEventName(omni::usd::StageEventType::eOpened),
    [](const carb::eventdispatcher::Event& e) {
        // handle Opened event  
    }
);

// If more event subscriptions are needed, store the observers in an array or vector

// Save `stageEvtObs` somewhere. When it goes out of scope or is reset() the observation of the event ends.
```

You can refer to {py:class}`omni.usd.StageEventType` for a full list of supported events.

### How to Create Another UsdContext
Module omni.usd supports multiple UsdContexts so it can have different stages opened in addition to the default one, and also
different Hydra Engines attached to render other viewports. UsdContext is indexed with unique name string, therefore
you need to provide unique name string when you want to create/access specific UsdContext. You can refer to {py:func}`omni.usd.create_context` and
{py:class}`omni.usd.destroy_context` for creating/destroying a UsdContext. And you can get the context through {py:class}`omni.usd.get_context` with `name` argument to access it.

### Selections
UsdContext also provides interfaces to manage prim selections in a stage. Through which, you can set/query user selections
with API, and also it provides event to detect selection changes. See {py:class}`omni.usd.Selection` for more details.

#### Python
```python
import omni.usd

context = omni.usd.get_context()
selection = context.get_selection()

...

# How to select multiple prims
# [...] is a list of prim paths in string type.
selection.set_selected_prim_paths([...], True)

...

# How to select/unselect single prim, where:
# select_or_unselect means if you want to select a prim or unselect a prim.
# clear_selected_or_not means if you want to clear all selected prims before this action.
selection.set_prim_path_selected(prim_path_in_str, select_or_unselect, True, clear_selected_or_not, True)

...

# How to clear all selected prims
selection.clear_selected_prim_paths()

...

# How to check if a prim is selected or not.
if selection.is_prim_path_selected(prim_path_in_str):
   ...

# How to get all selected prim paths.
prim_paths = selection.get_selected_prim_paths()

...

# How to select all prims with specific types, where [...] is a list of prim type names.
selection.select_all_prims([...])
```

#### C++
```cpp
#include <omni/usd/UsdContext.h>
#include <carb/events/EventsUtils.h>

...
auto usdContext = omni::usd::UsdContext::getContext();
auto selection = usdContext->getSelection();
...
```

In order to subscribe to selection changes, you can refer to "[How to subscribe to Stage Events](#how-to-subscribe-to-stage-events)"
for reference.

### Commands
Module {py:mod}`omni.usd` provides a set of pre-defined undoable USD commands to help other extensions to implement undo/redo workflow
around USD. For the full list of commands supported, you can refer to {py:mod}`omni.usd.commands`. You can also refer to {py:mod}`omni.kit.commands` for the details of command system supported in Kit.

### Utils
Module {py:mod}`omni.usd` extends several metadata for instructing UI implementation, and it provides encapsulated APIs
for each access to those metadata. For example, you can instruct Stage Window to not show the specific prim, or you
can instruct UI to avoid removing your prim. You can refer to {py:mod}`omni.usd.editor` for more details about all APIs provided.

Besides that, {py:mod}`omni.usd` provides a lot utils that encapsulate common USD operations that may be helpful for developers to use, which you can refer to API doc for reference.

## Thread Safety
UsdStage access is not threadsafe, therefore, you should avoid authoring USD with multiple writers in Python as omni.usd doesn't
provide thread-safety APIs but exposes UsdStage handle. In C++,
you need to ensure all write accesses are locked with USD lock (see {cpp:class}`omni::usd::UsdContext` for more details.)

## API Changes

Since Kit 106.0, old layer interface accessed through **omni.usd.UsdContext.get_layers** is removed which was deprecated since Kit 104.0. In order to
access corresponding APIs, you'd have to refer {py:mod}`omni.kit.usd.layers` for more details.
