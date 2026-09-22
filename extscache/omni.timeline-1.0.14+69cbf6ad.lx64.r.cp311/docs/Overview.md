```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Omni Timeline extension provides a programming interface for managing timeline operations within Omniverse. This extension enables developers to programmatically control the playback and timing of the main timeline, as well as to create custom timeline instances for special use cases. It supports the registration of callback functions, which are triggered upon various timeline state changes, such as updates to the current time. 

## Timeline control

### Time bounds

A timeline defines an interval for playback, bounded by a start and end time. Developers can programmatically set and query the current time. For more details on time units, conversions, and the interpretation of time parameters refer to the [Time parameters](TIME_PARAMETERS) documentation page. 

The following example sets the time bounds of the timeline:

```python
import omni.timeline

timeline = omni.timeline.get_timeline_interface()
# Set the start time to 5 seconds; subsequent play() calls will start from this point.
timeline.set_start_time(5)

# Set the end time to 10 seconds; subsequent playbacks will end or restart at this point, depending on the loop mode.
timeline.set_end_time(10)
```

### Playback and time stepping

A timeline steps through time in intervals called frames. The duration of these frames is determined by the `timeCodesPerSecond` parameter and the method used for time stepping. The main timeline is tied to the simulation time of Kit, meaning that advancing the timeline triggers computations of all registered subsystems, such as animation and simulation.
Detailed explanations of frames, time stepping modes, and their implications on execution are available in the [Time stepping](TIME_STEPPING) documentation. 

The following code example illustrates manual time stepping and initiating automatic time updates (playback):

```python
import omni.timeline

timeline = omni.timeline.get_timeline_interface()
# Manually advance the timeline by one frame, triggering updates in registered subsystems.
# For instance, animation and simulation extensions are called if they are loaded.
timeline.forward_one_frame()

# Start automatic playback; the timeline will continuously update and trigger subsystems accordingly.
timeline.play()
```

### Frame integrity

With the release of Kit 105, the timeline state is made immutable during a frame to ensure consistency across all subsystems contributing to that frame. This immutability guarantees that all subsystems perceive the same state during their computations. Changes to the timeline become visible only in the subsequent frame. For more details refer to the [Frame integrity and thread safety](FRAME_INTEGRITY) documentation page. The code example below illustrates this concept:

```python
import omni.timeline

timeline = omni.timeline.get_timeline_interface()
# Assuming the timeline is stopped, start playback.
timeline.play()

# Is the timeline playing?
# No. Changes are visible in the next frame.
print(timeline.is_playing())
```

### Timeline instances

The function `omni.timeline.get_timeline_interface()` in the examples above returns the **main** timeline, which controls the main stage of Kit.
In scenarios where multiple stages are used simultaneously, creating [additional timeline instances](MULTIPLE_TIMELINES) can be beneficial. These instances can be controlled independently, allowing for complex timeline management across different stages.

## Example usage

Omni Timeline provides the same set of API in C++ and Python. For more examples, please consult the [Python](USAGE_PYTHON) and [C++](USAGE_CPP) usage pages.

## User Guide

- [](USAGE_PYTHON)
- [](USAGE_CPP)
- [](CHANGELOG)

