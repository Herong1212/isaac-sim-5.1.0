# App/Subscribe to Update Events
import carb.eventdispatcher
import omni.kit.app

def on_update(e: carb.eventdispatcher.Event):
	print(f"Update: {e['dt']}")

sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
	order=0,
	event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
	on_event=on_update,
	observer_name="My Subscription Name"
)
