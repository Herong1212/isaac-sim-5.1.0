import omni, carb
import omni.timeline
import omni.usd
import carb.eventdispatcher
from omni.kit.notification_manager import post_notification, NotificationStatus


class _TimelineEndExtender:
    def __init__(self):
        carb.log_info("[TimelineEndExtender]: initializing")
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            lambda e, s=self: s._timeline_callback(e)
        )

    def _timeline_callback(self, e: carb.events.IEvent):
        if e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            time = self._timeline.get_current_time()
            start_time = self._timeline.get_start_time()
            end_time = self._timeline.get_end_time()
            if time > 0.5 * (start_time + end_time):
                carb.log_info("[TimelineEndExtender]: extending timeline")
                post_notification(
                    """Timeline end is approaching, extending timeline.
                    Adjust the timeline end time to allow for longer simulations
                    without triggering this notification.""",
                    duration=4,
                    status=NotificationStatus.WARNING,
                )
                self._timeline.set_end_time(end_time + (end_time - start_time))
                self._timeline.commit()

    def destroy(self):
        carb.log_info("[TimelineEndExtender]: destroying")
        self._timeline_sub.unsubscribe()


class TimelineEndExtenderService:
    _instance = None
    _stage_sub = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimelineEndExtenderService, cls).__new__(cls)
            cls._instance._timeline_end_extender = None
            cls._stage_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSING),
                on_event=cls._on_stage_close_event,
                observer_name="omni/metropolis/utils/timeline_end_extender/ON_STAGE_EVENT",
            )

        return cls._instance

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def activate_timeline_end_extender(cls):
        if cls._get_instance()._timeline_end_extender is None:
            cls._get_instance()._timeline_end_extender = _TimelineEndExtender()

    @classmethod
    def deactivate_timeline_end_extender(cls):
        if cls._get_instance()._timeline_end_extender is not None:
            cls._get_instance()._timeline_end_extender.destroy()
            cls._get_instance()._timeline_end_extender = None

    @classmethod
    def _on_stage_close_event(cls, e):
        cls._get_instance().deactivate_timeline_end_extender()
