# USD/Subscribe to USD Stage Events
import carb.eventdispatcher
import omni.usd

#
# Single event
#

def on_opened_event(e: carb.eventdispatcher.Event):
	print(f"Stage Opened Event: {e.event_name} {e.payload}")


stage_event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
	observer_name="My subscriber name",
	event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.OPENED),
	on_event=on_opened_event
)

#
# Multiple events
#

def on_stage_opened(e: carb.eventdispatcher.Event):
	print(f"Stage {e['val']} is opening")

def on_stage_closing():
	print("Stage is closing")

stage_event_subs = [
	carb.eventdispatcher.get_eventdispatcher().observe_event(
		observer_name="My subscriber name",
		event_name=omni.usd.get_context().stage_event_name(event),
		on_event=func
	)
	for event, func in (
		(omni.usd.StageEventType.OPENED, on_stage_opened),
		(omni.usd.StageEventType.CLOSING, lambda _: on_stage_closing()),
	)
]
