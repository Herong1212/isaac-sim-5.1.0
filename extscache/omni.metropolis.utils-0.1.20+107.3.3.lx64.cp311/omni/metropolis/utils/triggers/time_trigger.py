from typing import ClassVar

import omni, carb
import omni.timeline


from .core import *

from pxr import Usd


@dataclass
class TimeTrigger(TriggerBase):
    type_name: ClassVar[str] = "time"
    time: float = 5.0

    def __post_init__(self):
        # Register timeline callback
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            lambda e, s=self: s._timeline_callback(e)
        )
        # Flag to mark if callbacks have been called during a play
        self._has_called = True

    def destroy(self):
        if self._timeline_sub:
            self._timeline_sub.unsubscribe()
            self._timeline_sub = None
        super().destroy()

    def _timeline_callback(self, e: carb.events.IEvent):

        # Refresh at begining of play
        if e.type == omni.timeline.TimelineEventType.PLAY.value:
            self._has_called = False
        elif e.type == omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value:
            if self._has_called:
                return
            if not self._timeline.is_playing():
                return
            # Caculate current frame number
            subframe_number = (
                self._timeline.time_to_time_code(self._timeline.get_current_time())
                * self._timeline.get_ticks_per_frame()
            )
            subframe_number_nearest_int = round(subframe_number)

            target_subframe_number = round(
                self._timeline.time_to_time_code(self.time) * self._timeline.get_ticks_per_frame()
            )
            if subframe_number_nearest_int == target_subframe_number:
                self._has_called = True
                self.trigger()
                carb.log_info(
                    "[TimeTrigger]: Triggering event: "
                    + self.type_name
                    + " at time: "
                    + str(self._timeline.get_current_time())
                )


# class TimeTriggers:
#     """
#     This class is responsible for triggering events at specified times.
#     It listens to the timeline events and triggers the events when the time comes.
#     """

#     def __init__(self, name: str):
#         # a dict of trigger_id to frame_number
#         self.trigger_id_to_frame_number = {}

#         # a dict of frame_number to a dict of trigger_id to trigger callback
#         self.triggers_by_frame_number = {}

#         # a dict of trigger_id to name
#         self.trigger_id_to_name = {}

#         self._timeline = omni.timeline.get_timeline_interface()

#         self.update_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
#             lambda e, s=self: s.on_update(e), name=name
#         )

#         self.current_max_id = 0

#         self.name = name

#     def __del__(self):
#         self.update_sub = None

#     def on_update(self, e: carb.events.IEvent):
#         # print("TimeLine Event", e.type, int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED), e.payload)
#         if e.type == omni.timeline.TimelineEventType.PLAY.value:
#             return
#         elif e.type == omni.timeline.TimelineEventType.START_TIME_CHANGED.value:
#             # TODO: handle start time changed
#             return
#         elif e.type == omni.timeline.TimelineEventType.STOP.value:
#             return
#         elif not e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED.value):
#             return
#         frame_number = self._timeline.time_to_time_code(self._timeline.get_current_time())
#         frame_number_nearest_int = round(frame_number)
#         ticks_per_frame = self._timeline.get_ticks_per_frame()
#         threshold = 1.0 / (2.0 * ticks_per_frame)
#         # only trigger near the main time codes
#         if abs(frame_number - frame_number_nearest_int) < threshold:
#             frame_number = frame_number_nearest_int
#         else:
#             return

#         # print("[TimeTriggers]: on_update time: ", self.current_frame_count)
#         # print(self.triggers)
#         for trigger_id, callback in self.triggers_by_frame_number.get(frame_number, {}).items():
#             # print("Triggering topple event: ", name)
#             carb.log_info("Triggering event: " + self.trigger_id_to_name[trigger_id] + " from " + self.name)
#             callback()

#     def _remove_time_trigger(self, trigger_id: int):
#         del self.trigger_id_to_name[trigger_id]
#         frame_number = self.trigger_id_to_frame_number[trigger_id]
#         del self.trigger_id_to_frame_number[trigger_id]
#         del self.triggers_by_frame_number[frame_number][trigger_id]

#     def add_time_trigger(self, name: str, time: float, callback) -> TriggerSub:
#         timeline = omni.timeline.get_timeline_interface()

#         frame_number = round(timeline.time_to_time_code(time))
#         carb.log_info("Adding time trigger: " + name + " at frame: " + str(frame_number))

#         trigger_id = self.current_max_id
#         self.current_max_id += 1

#         self.trigger_id_to_name[trigger_id] = name

#         def on_destroy_callback():
#             self._remove_time_trigger(trigger_id)

#         self.trigger_id_to_frame_number[trigger_id] = frame_number
#         self.triggers_by_frame_number.setdefault(frame_number, {})[trigger_id] = callback

#         return TriggerSub(trigger_id, name, on_destroy_callback)
