# Python Usage Examples


## Controlling the timeline
This example demonstrates how to use various API functions to control the timeline's state:
```python
import omni.timeline

# Obtain the main timeline object
timeline = omni.timeline.get_timeline_interface()

# Start playing the timeline
timeline.play()

# Check if the timeline is playing
# Output will be False as state changes are applied in the next frame
print(f'Is the timeline playing? {timeline.is_playing()}')

# Set the current time to t = 3 seconds
timeline.set_current_time(3)

# Perform additional operations...

# Pause the timeline
timeline.pause()

# Advance the timeline by one frame
# Frame duration can be adjusted using timeline.set_time_codes_per_second
timeline.forward_one_frame()
```

## Registering callbacks for timeline state changes
The following code example shows how to register a callback to respond to various timeline state changes:

```python
import omni.timeline

# Obtain the main timeline object
timeline = omni.timeline.get_timeline_interface()

# Define a callback function to handle timeline events
def on_timeline_events(event):
	if event.type == omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value:
		# Difference between the last current time and the new one
		# Clamped to zero if it would be negative
		dt = event.payload['dt']
		# Retrieve the new current time
		current_time = event.payload['currentTime']
		print(f'Current time changed, dt = {dt}s, end of frame = {current_time}s')
	if event.type == omni.timeline.TimelineEventType.PLAY.value:
		print(f'Timeline is now playing')
	if event.type == omni.timeline.TimelineEventType.STOP.value:
		print(f'Timeline is now stopped')
	if event.type == omni.timeline.TimelineEventType.PAUSE.value:
		print(f'Timeline is now paused')
	if event.type == omni.timeline.TimelineEventType.START_TIME_CHANGED.value:
		start_time = event.payload['startTime']
		print(f'Timeline has a new start time: {start_time}s')
	# For more events, please consult the TimelineEventType documentation

# Register a callback that listens to all timeline events
timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
	on_timeline_events
)

# Demonstrate the callback functionality by triggering various timeline events
timeline.set_start_time(1)
timeline.play()
timeline.set_current_time(3)
timeline.pause()
timeline.stop()
```