# Time parameters
## Time unit in the API
The Omni Timeline API utilizes seconds as the standard unit of time. All methods within the API that accept or return time-related parameters do so using seconds as the base unit[^1].
[^1]: The only exception is `play`, the parameters of which are in time codes for backward compatibility.

## Relationship with USD time codes
The core data format of Omniverse, USD, defines its own time representation called [UsdTimeCode](https://openusd.org/release/api/class_usd_time_code.html). `UsdTimeCode` is defined as 
> *unitless, generic time measurement that serves as the ordinate for time-sampled data in USD files. A client of USD relies on the UsdStage (which in turn consults metadata authored in its root layer) to define the mapping of TimeCodes to units like seconds and frame.*

The metadata of this mapping is the `timeCodesPerSecond` parameter of the USD stage, which is synchronized with the identically named parameter in Omni Timeline. 
To convert `UsdTimeCode` to seconds, divide the `UsdTimeCode` value by the `timeCodesPerSecond` value of the associated timeline.

Omni Timeline provides helper methods to facilitate conversions between time codes and seconds, based on the `timeCodesPerSecond` parameter:
```python Python
import omni.timeline

# Obtain the timeline interface
timeline = omni.timeline.get_timeline_interface()

# Set the conversion factor
tcps = 30
timeline.set_time_codes_per_second(tcps)

# Note: wait a frame here for set_time_codes_per_second to take effect (omitted)

# Convert time between seconds and time codes
time_in_seconds = 2.5
time_in_timecodes = timeline.time_to_time_code(time_in_seconds)
print(f'Time in time codes: {time_in_timecodes}')  # Output: 75 (2.5 s * 30 tc/s)
time_in_seconds_again = timeline.time_code_to_time(time_in_timecodes)
print(f'Time in seconds: {time_in_seconds_again}')
```

## Time bounds and current time
In parallel with USD's definition of start and end `UsdTimeCode` for a stage, Omni Timeline defines its start and end times in seconds. 
These bounds are synchronized with the main stage. 
Any changes to the start or end `UsdTimeCode` of the main USD stage are reflected in the [main timeline](MULTIPLE_TIMELINES)'s start or end time, and vice versa.

As explained in the [Time stepping](TIME_STEPPING) documentation, the timeline is segmented into frames. The
*start time* of a timeline defines the beginning of its first frame. Frames may end at or after the *end time*, but no frame is allowed to start after it. Note that end time does not need to fall on a frame border. When the timeline bounds define an integer number of frames, the end time is the end of the last frame.

The *current time* is defined as the beginning of the *next* frame. Note that during frame computation, Kit transitions from one point in time to another, making a frame a time interval. 
Thus, the current time is effectively the **end** of the ongoing frame (the point in time to which the frame is transitioning), and time is incremented *before* the invocation of callbacks registered with the timeline. This may differ from the current time concept in other software. 

The following code example helps clarifying the interpretation of current time:
```python
import omni.timeline

# Obtain the main timeline
timeline = omni.timeline.get_timeline_interface()

# Define a callback for time updates
def on_time_update(event):
	# Retrieve the end time of the current frame
	time = timeline.get_current_time()
	print(f'Current time from timeline: {time}')
	
	# Retrieve the end time of the current frame from the event payload
	time_from_event = event.payload['currentTime']
	print(f'Current time from event: {time}')
	
	# Calculate the start time of the current frame
	start_time_of_frame = time - event.payload['dt']
	print(f'Start time of the current frame: {start_time_of_frame}')

# Subscribe to the timeline event stream
timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop_by_type(
	omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, 
	on_time_update
)

# Display the current time, i.e. the start time of the next frame, before callbacks
print(f'Time before callbacks: {timeline.get_current_time()}')

# Advance to the next frame
timeline.forward_one_frame()
```