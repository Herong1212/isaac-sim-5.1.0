# Frame integrity and thread safety

## Frame integrity
The Omni Timeline ensures atomicity and consistency within a frame by treating the state of a timeline object as immutable during that frame. Any modifications to the timeline are queued and only applied at the start of the subsequent frame. This design guarantees that all subsystems involved in a frame's processing observe a consistent timeline state and that frames are uninterruptible, which are crucial for the integrity of frame-based computations.

```python
import omni.timeline

# Obtain the main timeline
timeline = omni.timeline.get_timeline_interface()

# Define event callbacks
def callback_A(event):
	if event.type == omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value:
		time = event.payload['currentTime']
		print(f'Callback A was executed, current time is {time}')
		# Attempt to stop the timeline; the frame will still complete.
		timeline.stop()

def callback_B(event):
	if event.type == omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value:
		time = event.payload['currentTime']
		print(f'Callback B was executed, current time is {time}')

# Register callbacks with priority ordering.
# Numbers passed to the function are the priority orders.
timeline_sub_A = timeline.get_timeline_event_stream().create_subscription_to_pop(callback_A, 0)
timeline_sub_B = timeline.get_timeline_event_stream().create_subscription_to_pop(callback_B, 1)

# Start playback, this will trigger registered callbacks when time is changed.
# Example code assumes timeline is stopped before calling play.
timeline.play()

# Check if the timeline is playing
# Output will be False as the state change is deferred to the next frame.
print(f'Is the timeline playing? {timeline.is_playing()}')
```

In the example above, querying `is_playing()` immediately after calling `play()` returns `False`, because state changes are deferred until the next frame.
This behavior can complicate script writing when immediate state updates are required. To address this, the Omni Kit App provides an API to wait for the next frame, which is the recommended method for scripts that depend on updated state information:

```python
import asyncio
import omni.kit.app
import omni.timeline
from omni.kit.async_engine import run_coroutine

timeline = omni.timeline.get_timeline_interface()

# Define an asynchronous task
async def my_task():
	# Advance the timeline
	timeline = omni.timeline.get_timeline_interface()
	old_time = timeline.get_current_time()
	print(f'Current time (initial): {old_time}')
	new_time = timeline.get_current_time() + 1
	timeline.set_current_time(new_time)
	
	# Query the time, it still shows the old value
	print(f'Current time (within frame): {timeline.get_current_time()}')
	
	# Wait for the next frame to see the updated value
	await omni.kit.app.get_app().next_update_async()
	print(f'Current time (next frame): {timeline.get_current_time()}')

# Execute the asynchronous task
run_coroutine(my_task())
```

For scenarios where immediate state changes are necessary, Omni Timeline offers the `commit()` function. This method applies changes instantly but must be used with caution, as it is not thread-safe and triggers callbacks immediately:

```python
import omni.timeline
from omni.kit.async_engine import run_coroutine

timeline = omni.timeline.get_timeline_interface()
timeline.play()

# Apply pending changes and trigger callbacks immediately
# Caution: not thread-safe!
timeline.commit()

# Verify that the timeline is playing, prints True
print(f'Is the timeline playing? {timeline.is_playing()}')
```

## Thread safety
The Omni Timeline API is designed to be thread-safe, with the exception of the `commit()` function. When `commit()` is invoked, it executes all registered event callbacks on the **calling thread**, which can lead to issues if callbacks are expected to run on the main thread. Therefore, `commit()` should be used sparingly and only from the main thread.

Timeline callbacks are consistently executed on the **main thread**, regardless of the thread from which they were registered. The Omni Timeline does not provide a mechanism to specify the execution thread for a callback. The following example demonstrates this behavior:

```python
import omni.timeline
import threading
from time import sleep

# Function to be executed in a separate thread
def threaded_function():
	thread_id = threading.get_ident()
	print(f'Starting thread with ID: {thread_id}...')
	timeline = omni.timeline.get_timeline_interface()

	# Define and register timeline event callback
	def on_timeline(event):
		callback_thread_id = threading.get_ident()
		print(f'Timeline event callback executed on thread ID: {callback_thread_id}')

	timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
		on_timeline
	)

	# Modify the timeline from this thread
	# Callback is still called from the main thread!
	sleep(3)
	print("Requesting timeline stop...")
	timeline.stop()

	# Ensure the callback subscription stays alive until stop() takes effect
	sleep(3)

# Display the main thread ID
print(f'Main thread ID: {threading.get_ident()}')

# Start the custom thread
thread = threading.Thread(target=threaded_function)
thread.start()

# Allow time for the event callback registration and then start the timeline
sleep(1)
print("Starting timeline playback...")
timeline = omni.timeline.get_timeline_interface()
timeline.play()
```

In this example, the timeline is manipulated from a separate thread, but the callback is still invoked on the main thread. It is important to note that `commit()` should never be called from a non-main thread to avoid potential concurrency issues.
