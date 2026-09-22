# omni.kit.window.status_bar:

Omniverse Kit Status Bar

Status Bar supports setting the progress and the message using the
message bus. It\'s also possible to listen to mouse clicks.

To return to reporting Kit\'s progress, it\'s necessary to set negative
value of progress.

## Example:
```python
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.app import queue_event

PROGRESS_GLOBAL_EVT = "omni.kit.window.status_bar@progress"
ACTIVITY_GLOBAL_EVT = "omni.kit.window.status_bar@activity"
CLICKED_GLOBAL_EVT = "omni.kit.window.status_bar@clicked"

queue_event(PROGRESS_GLOBAL_EVT, payload={"progress": 0.5})
queue_event(ACTIVITY_GLOBAL_EVT, payload={"text": "Hello world"})

sub = get_eventdispatcher().observe_event(
    event_name=CLICKED_GLOBAL_EVT,
    on_event=lambda _: print("clicked")
)
```
