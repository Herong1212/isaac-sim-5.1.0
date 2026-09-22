# Creating timeline objects

## The main timeline
Calling `omni.timeline.get_timeline_interface()` without parameters returns the *main* timeline object. This timeline is tied to the main stage of Kit (more specifically, to the main `UsdContext`) and is instantiated at the application's startup.
Most Kit extensions interact with the main timeline due to its central role in managing the temporal aspects of the primary stage.

## New timeline objects
For specific use cases, such as developing an animated asset preview in a secondary viewport, it may be necessary to manage a separate timeline. This can be achieved by passing an optional parameter to `get_timeline_interface` that specifies a unique name for the new timeline object. The following code example demonstrates how to create and manipulate an independent timeline:

```python
import omni.timeline

# Retrieve or create a timeline with a specified name
timeline_name = "name_of_the_timeline"
timeline = omni.timeline.get_timeline_interface(timeline_name)

# Configure and control the timeline independently of other timelines
# Default values of new timeline objects are not copied from the main timeline
timeline.set_end_time(10)
timeline.set_start_time(0)
timeline.set_time_codes_per_second(30)
timeline.play()
timeline.set_current_time(5)

# Explicitly destroy the timeline when it is no longer needed
omni.timeline.destroy_timeline(timeline_name)
```

Notes:
- All timeline objects, including the main timeline, are running on the same thread and thus follow the exact same time stepping behaviour. 
- There are no ordering guarantees between callbacks of different timeline objects.
- For the main timeline, various settings, such as start time, end time, and time codes per second are copied from the main stage. This is not the case for custom timelines, make sure to initialize them properly before use.

## Director timeline
By default, users and Kit extensions have full control over all existing timeline objects. 
In certain scenarios, this control needs to be disabled, and a timeline needs to be controlled by a single source.
A good example is Live sync, where we may want to allow only a priviliged user to control the timelines of all participating Kit instances.

When a *director* timeline is assigned to a timeline instance, it mimics everything that the director is doing and disables all direct state changes, even through the Omni Timeline API. This is demonstrated in the following code example:

```python
import omni.timeline

# Create a new timeline, which will be the "director"
# Note: the exact name does not matter, we can call it however we like
director_timeline = omni.timeline.get_timeline_interface("director")

# When a director is set, all its time parameters and play state are copied to the directed timeline
# New timeline objects start with default settings, make sure we start with something useful
director_timeline.set_start_time(0)
director_timeline.set_end_time(10)
director_timeline.set_time_codes_per_second(30)

# Assign the director timeline to control the main timeline
# All time parameters and play state are copied from the director timeline
main_timeline = omni.timeline.get_timeline_interface()
main_timeline.set_director(director_timeline)

# Attempts to change the state of the main timeline directly will be ignored
main_timeline.play()  # This will have no effect

# Play both timelines
director_timeline.play()

# To regain direct control, remove the director
main_timeline.set_director(None)
main_timeline.stop() # Comment out the previous line and main_timeline will keep playing!
```