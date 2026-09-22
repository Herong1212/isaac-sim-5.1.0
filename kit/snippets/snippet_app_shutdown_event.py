# App/Subscribe to Shutdown Events
import omni.kit.app
from carb.eventdispatcher import get_eventdispatcher

def on_post_quit_event(_):
    print("We are about to shutdown")

def on_pre_shutdown_event(_):
    print("We are shutting down")

sub1 = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_POST_QUIT, on_event=on_post_quit_event, observer_name="name of the subscriber for debugging", order=0)
sub2 = get_eventdispatcher().observe_event(event_name=omni.kit.app.GLOBAL_EVENT_PRE_SHUTDOWN, on_event=on_pre_shutdown_event, observer_name="name of the subscriber for debugging", order=0)

