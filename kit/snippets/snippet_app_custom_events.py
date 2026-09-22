# App/Create Custom Event
from carb.eventdispatcher import get_eventdispatcher, Event
import omni.kit.app

# Event is unique name. Events are typically deferred and delivered during app update.
# [ext name].[event name] is a recommended naming convention:
MY_CUSTOM_EVENT: str = "omni.my.extension.MY_CUSTOM_EVENT"
# The immediate event is sent immediately when the event is queued, instead of waiting for the next update.
MY_CUSTOM_EVENT_IMMEDIATE: str = MY_CUSTOM_EVENT + ":immediate"

# Event functions receive the event, which has `event_name` and optional arguments.
# Only events that you are observing will be delivered to your event function
def on_event(e: Event):
    assert e.event_name == MY_CUSTOM_EVENT
    print(e.event_name, e['data'], e['x'])

# Events are managed globally through eventdispatcher and can be observed as such.
# The on_event() function will be called during the next app update after the event is queued.
sub = get_eventdispatcher().observe_event(
    observer_name="my observer", # a debug name for profiling and debugging
    event_name=MY_CUSTOM_EVENT,
    on_event=on_event
)

# When sub is collected or `reset()` the subscription ends.

# Observing the _IMMEDIATE event will not wait for the next app update and will be called immediately when the event is queued.
imm_sub = get_eventdispatcher().observe_event(
    observer_name="my immediate observer",
    event_name=MY_CUSTOM_EVENT_IMMEDIATE,
    on_event=on_event
)

# Queuing the event:
omni.kit.app.queue_event(MY_CUSTOM_EVENT, payload={"data": 2, "x": "y"})
