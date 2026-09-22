```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```


# Overview
omni.activity.core is a backbone extension for profiling activities and progress.

It works together with omni.activity.pump and omni.activity.profiler, provides APIs to start and end the activity pump streaming, allows to send activity progress and create callbacks to subscribe to event dispatching and updating.

It works together with omni.activity.ui to display application activity information to the users.
Users can also create customized UI interfaces to monitor the progress and activities with data provided from omni.activity.core.

## Important API List
- **EventType**: Type of the activity event.
- **IActivity**: The activity and the progress processor.
- **IEvent**: The event contains custom data. It can be speed, progress, etc.
- **INode**: Representation of each dispatched information element. Nodes can contain other nodes and events.
- **begin**: Send began typed activity event.
- **ended**: Send end typed activity event.
- **disable**: Disable activity dispatching.
- **enable**: Enable activity dispatching.
- **get_instance**: Return the global IActivity singleton instance.
- **progress**: Send progress payload in the activity event.
- **updated**: Send updated typed activity event.

## General Use Case
For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.


## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
