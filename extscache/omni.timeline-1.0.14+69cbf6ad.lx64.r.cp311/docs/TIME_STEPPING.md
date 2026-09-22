# Time stepping 
## Frames and discretization
In the realm of animation and simulation, time is discretized into frames, each representing a distinct *interval* with a defined start and end. The state of the virtual world is updated by the engine's subsystems, such as physics or skeleton animation, for each of these intervals.

The following pseudo-code outlines how all simulation and game engines, including Omniverse, update the state of the virtual world:
```
for each subsystem in registered_subsystems
    subsystem.update(current_time, elapsed_time)
```

Here, `current_time` refers to the beginning or the end of the frame (in Omniverse it is the latter) and `elapsed_time` (also referred to as *delta time* or *dt*) is the *duration* or *length* of the frame.

Registering a callback to the timeline that responds to changes in the current time integrates the callback into the system state update process:
```python
import omni.timeline

# Obtain the main timeline
timeline = omni.timeline.get_timeline_interface()

# Called every time the current time changes, by any means
def on_time_update(event):
	# Frame duration (dt)
	frame_duration = event.payload['dt']
    # End time of the frame
	end_time_of_frame = event.payload['currentTime']

	# Perform custom computations for the frame, such as simulation, animation, UI updates etc.

# Subscribe to the timeline event stream for current time changes
timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop_by_type(
	omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, 
	on_time_update
)
```

Note that in the example `on_time_update` callback is invoked whenever the timeline's current time changes, including during automatic updates when the timeline is playing or manual calls to time-changing APIs.

## Variable and Fixed time stepping
Animation and simulation subsystems have distinct requirements for timeline playback. For smooth real-time playback, the elapsed simulation time within the virtual world, which is the duration of a frame, should match the elapsed wall clock time in the real world. However, this wall clock time can vary due to factors like system load or the computational demands of engine updates, making it non-deterministic. Animation subsystems generally prioritize smooth playback, while simulation systems prefer a consistent frame length for reliable numerical integration and reproducibility, leading to either equal or varying frame lengths based on the engine's design. Omniverse supports both approaches.

**Variable time stepping** does not maintain a uniform frame length; instead, it uses the elapsed wall clock time since the last frame to determine the length of the current frame. This method ensures that wall clock and simulation times remain in sync, allowing for smooth animation playback even when frame computation times fluctuate.
However, Variable time stepping has drawbacks. Most simulation engines discretize time into uniformly timed frames, which can lead to inconsistencies with animation, particularly when system performance decreases. In such cases, a single frame may encompass a larger time interval. To prevent further system slowdown, simulation engines often clamp these large frame lengths. Additionally, user interfaces typically display frames as a uniform grid, but with Variable time stepping, the actual simulation time seldom aligns with these UI frame borders, and the engine might perform an arbitrary number of updates for a given UI frame, sometimes none at all.

*In scenarios where system performance degrades, Variable time stepping might result in the engine skipping over frames, potentially omitting simulation updates, yet playback time continues to align with wall clock time.*

Conversely, **Fixed time stepping** maintains frames of uniform length, determined by the reciprocal of the `timeCodesPerSecond` parameter of the timeline. This uniformity facilitates the consistency of animation and simulation, leading to deterministic playback.
The primary challenge with Fixed time stepping is ensuring real-time playback and smoothness. 

*When system performance lags, simulation time progresses slower than real-time under Fixed time stepping, but frames are not skipped, preserving the continuity of simulation updates.*

As a general guideline
* Use Variable time stepping when:
    * Reproducibility is not essential.
    * Only animation is present without simulation.
    * Smooth and/or real-time playback is a priority.
* Use Fixed time stepping when:
    * Reproducibility is crucial.
    * Both animation and simulation are present and interact.

Starting with Kit version 105, **Fixed time stepping is the default** due to Omniverse's focus on simulation.

As Omniverse is primarily a simulation platform, starting from Kit version 105 **Fixed time stepping is the default setting**.

To toggle between time stepping modes, use the `/app/player/useFixedTimeStepping` Carbonite setting. Note that the timeline must be restarted (by calling `stop` and then `play`) for changes to take effect:
```python
import carb.settings
import omni.timeline

# Acquire the settings interface
settings = carb.settings.acquire_settings_interface()

# Enable Variable time stepping by disabling Fixed time setting 
settings.set("/app/player/useFixedTimeStepping", False)

# Restart the timeline to apply the new time stepping mode
timeline = omni.timeline.get_timeline_interface()
timeline.stop()
timeline.play()
```

When stepping time programmatically (outside of automatic playback), the time is always advanced by a fixed frame length:

```python
import omni.timeline

# Obtain the main timeline object
timeline = omni.timeline.get_timeline_interface()

# Steps time by the reciprocal of timeline.get_time_codes_per_seconds()
timeline.forward_one_frame()
```

## Connection to real-time playback and pacing
### Synchronizing wall clock time and simulation time
Variable time stepping inherently synchronizes simulation time with wall clock time, facilitating real-time playback. 
Fixed time stepping requires careful scheduling of system updates to match the fixed frame length with elapsed wall clock time. 
Omniverse Kit attempts to achieve this through thread pacing, the exact method is considered as implementation detail.
If computation time of system updates exceed the fixed simulation time length, playback will slow down relative to real-time.

To adjust pacing with Fixed time stepping, the `play_every_frame` API (alternatively the `/app/player/useFastMode` Carbonite setting) can be used, which accelerates playback when the system is capable:
```python
import omni.timeline
import carb.settings

# Obtain the main timeline object
timeline = omni.timeline.get_timeline_interface()

# Query the current value of the play_every_frame setting
print(f'Current value of the setting: {timeline.get_play_every_frame()}')

# Configure Kit to not wait for wall clock time to catch up between updates
# This setting is effective only with Fixed time stepping
timeline.set_play_every_frame(True)

# Acquire the settings interface
settings = carb.settings.acquire_settings_interface()

# The following setting has the exact same effect as set_play_every_frame
settings.set("/app/player/useFastMode", True)
```

### Frame rate with Fixed time stepping
The main thread that is running Kit system updates, including timeline callbacks, may need to operate at a higher frequency than system updates alone would require. 
In the current implementation, the actual frame rate is the smallest integer multiple of `timeCodesPerSecond` parameter of the timeline that exceeds the desired frame rate, `targetFrameRate`:

```python
import omni.timeline

# Obtain the main timeline object
timeline = omni.timeline.get_timeline_interface()

# Set fixed frame length to 1/30
timeline.set_time_codes_per_second(30)

# Set the target frame rate to 50
# The effective frame rate, i.e. the refresh rate of the main thread, becomes 2 * 30 = 60
# It works only with Fixed time stepping
timeline.set_target_framerate(50)

# Alternatively, use the following Carbonite setting to achieve the same result
import carb.settings
settings = carb.settings.acquire_settings_interface()
settings.set("/app/player/targetRunLoopFrequency", 50)
```

Tip: If Fixed time stepping causes the system to slow down, consider reducing the target frame rate before other adjustments.

### Compensation for long-lasting frames in Fixed time stepping
Occasionally, frames may take longer to compute than the fixed frame length, slowing down playback. To compensate and maintain alignment with wall clock time, the `/app/player/CompensatePlayDelayInSecs` setting allows for faster-than-real-time playback until simulation time catches up.
This is done by calling system updates more frequently, with unmodified simulation frame length.

```python
import carb.settings

# Acquire the settings interface
settings = carb.settings.acquire_settings_interface()

# Set the maximum allowed difference from real-time before increasing update frequency
settings.set("/app/player/CompensatePlayDelayInSecs", desired_delay_compensation)
```

The value of this setting determines the maximum allowed difference from real-time before system updates are called more frequently. 
The default value is set to zero, meaning that this effect is turned off.

## Sub-stepping
High-frequency interactions between subsystems, such as cloth simulation on an animated character, may necessitate *sub-stepping*, where each frame is divided into equal-length *sub-steps* or *ticks*. By default, there is one tick per frame, but this can be adjusted:

```python
import omni.timeline

# Obtain the main timeline object
timeline = omni.timeline.get_timeline_interface()

# Set the sub-stepping rate
timeline.set_ticks_per_frame(3)

# Define event callbacks
def subsystem_A(event):
	if event.type == omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value:
		tick = event.payload['tick']
		print(f'Subsystem A was executed, tick index is {tick}')

def subsystem_B(event):
	if event.type == omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value:
		tick = event.payload['tick']
		print(f'Subsystem B was executed, tick index is {tick}')

# Register two new "subsystems"
timeline_sub_A = timeline.get_timeline_event_stream().create_subscription_to_pop(
	subsystem_A,
    0  # A runs before B
)
timeline_sub_B = timeline.get_timeline_event_stream().create_subscription_to_pop(
	subsystem_B,
    1  # B runs after A
)

# Advance the timeline, triggering the subsystem callbacks for each sub-step
timeline.forward_one_frame()
```

Running the above code will execute each subsystem callback three times per frame, once for each sub-step and will print:
```
Subsystem A was executed, tick index is 0
Subsystem B was executed, tick index is 0
Subsystem A was executed, tick index is 1
Subsystem B was executed, tick index is 1
Subsystem A was executed, tick index is 2
Subsystem B was executed, tick index is 2
```