# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityModel"]

from dataclasses import dataclass
from functools import lru_cache
from omni.ui import color as cl
from typing import Dict, List, Optional, Set
from .style import get_shade_from_name

import asyncio
import carb
import contextlib
import functools
import omni.activity.core
import omni.ui as ui
import traceback
import weakref


TIMELINE_EXTEND_DELAY_SEC = 5.0
SECOND_MULTIPLIER = 10000000

SMALL_ACTIVITY_THRESHOLD = 0.001

time_begin = 0
time_end = 0


@lru_cache()
def get_color_from_name(name: str):
    return get_shade_from_name(name)


def get_default_metadata(name):
    return {"name": name, "color": int(get_color_from_name(name))}


def handle_exception(func):
    """
    Decorator to print exception in async functions

    TODO: The alternative way would be better, but we want to use traceback.format_exc for better error message.
        result = await asyncio.gather(*[func(*args)], return_exceptions=True)
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            # We always cancel the task. It's not a problem.
            pass
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


async def event_wait(evt, timeout):
    # Suppress TimeoutError because we'll return False in case of timeout
    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(evt.wait(), timeout)
    return evt.is_set()


@handle_exception
async def loop_forever_async(refresh_rate: float, stop_event: asyncio.Event, callback):
    """Forever loop with the ability to stop"""

    while not await event_wait(stop_event, refresh_rate):
        # Do something
        callback()


@dataclass
class ActivityModelEvent:
    """Atomic event"""

    type: omni.activity.core.EventType
    time: int
    payload: dict


@dataclass
class TimeRange:
    """Values or a timerange"""

    item: ui.AbstractItem
    begin: int
    end: int
    metadata: dict


class ActivityModelItem(ui.AbstractItem):
    def __init__(self, name: str, parent):
        super().__init__()

        self.parent = parent
        self.name_model = ui.SimpleStringModel(name)
        self.events: List[ActivityModelEvent] = []

        self.children: List[ActivityModelItem] = []
        self.child_to_id: Dict[str, int] = {}

        # We need it for hash
        parent_path = parent.path if parent else ""
        self.path = parent_path + "->" + name

        if parent_path == "->Root->Textures->Load" or parent_path == "->Root->Textures->Queue":
            self.icon_name = "texture"
        elif parent_path == "->Root->Materials":
            self.icon_name = "material"
        elif parent_path == "->Root->USD->Read" or parent_path == "->Root->USD->Resolve":
            self.icon_name = "USD"
        else:
            self.icon_name = "undefined"

        self.max_time_cached = None

        # True when ended
        self.ended = True
        # Time range when the item is active
        self.__child_timerange_dirty = True
        self.__dirty_event_id: Optional[int] = None
        self.__timerange_cache: List[TimeRange] = []
        self.__total_time: int = 0
        self.__size = 0
        self.__children_size = 0

        self._packItem = None

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __repr__(self):
        return "<ActivityModelItem '" + self.name_model.as_string + "'>"

    @property
    def loaded_children_num(self):
        res = 0
        for c in self.children:
            if c.ended:
                res += 1
        return res

    @property
    def time_range(self) -> List[TimeRange]:
        """Return the time ranges when the item  was active"""

        if self.events:
            # Check if it's not dirty and is not read from the json
            if self.__dirty_event_id is None and self.__timerange_cache:
                return self.__timerange_cache
            dirty_event_id = self.__dirty_event_id
            self.__dirty_event_id = None

            if self.__timerange_cache:
                time_range = self.__timerange_cache.pop(-1)
            else:
                time_range = None

            # Iterate the new added events
            for event in self.events[dirty_event_id:]:
                if event.type == omni.activity.core.EventType.ENDED or event.type == omni.activity.core.EventType.UPDATED:
                    if time_range is None:
                        # Can't end or update if it's not started
                        continue

                    time_range.end = event.time
                else:
                    if time_range and event.type == omni.activity.core.EventType.BEGAN and time_range.end != 0:
                        # The latest event is ended. We can add it to the cache.
                        self.__timerange_cache.append(time_range)
                        time_range = None

                    if time_range is None:
                        global time_begin
                        time_range = TimeRange(self, 0, 0, get_default_metadata(self.name_model.as_string))
                        time_range.begin = max(event.time, time_begin)

                if "size" in event.payload:
                    prev_size = self.__size
                    self.__size = event.payload["size"]
                    loaded_size = self.__size - prev_size
                    if loaded_size > 0:
                        self.parent.__children_size += loaded_size

            if time_range:
                if time_range.end == 0:
                    # Range did not end, set to the end of the capture.
                    global time_end
                    time_range.end = max(time_end, time_range.begin)
                if time_range.end < time_range.begin:
                    # Bad data, range ended before it began.
                    time_range.end = time_range.begin

                self.__timerange_cache.append(time_range)

        elif self.children:
            # Check if it's not dirty
            if not self.__child_timerange_dirty:
                return self.__timerange_cache
            self.__child_timerange_dirty = False

            # Create ranges out of children
            min_begin = None
            max_end = None
            for child in self.children:
                time_range = child.time_range
                if time_range:
                    if min_begin is None:
                        min_begin = time_range[0].begin
                    else:
                        min_begin = min(min_begin, time_range[0].begin)
                    if max_end is None:
                        max_end = time_range[-1].end
                    else:
                        max_end = max(max_end, time_range[-1].end)

            if min_begin is not None and max_end is not None:
                if self.__timerange_cache:
                    time_range_cache = self.__timerange_cache[0]
                    time_range_cache.begin = min_begin
                    time_range_cache.end = max_end
                else:
                    time_range_cache = TimeRange(
                        self, min_begin, max_end, get_default_metadata(self.name_model.as_string)
                    )
                if not self.__timerange_cache:
                    self.__timerange_cache.append(time_range_cache)

        # TODO: optimize
        self.__total_time = 0
        for timerange in self.__timerange_cache:
            self.__total_time += timerange.end - timerange.begin

        return self.__timerange_cache

    @property
    def total_time(self):
        """Return the time ranges when the item was active"""
        if self.__dirty_event_id is not None:
            # Recache
            _ = self.time_range

        return self.__total_time

    @property
    def size(self):
        """Return the size of the item"""
        return self.__size

    @size.setter
    def size(self, val):
        self.__size = val

    @property
    def children_size(self):
        return self.__children_size

    @children_size.setter
    def children_size(self, val):
        self.__children_size = val

    def find_or_create_child(self, node):
        """Return the child if it's exists, or creates one"""
        name = node.name
        child_id = self.child_to_id.get(name, None)
        if child_id is None:
            created = True

            # Create a new item
            child_item = ActivityModelItem(name, self)
            child_id = len(self.children)
            self.child_to_id[name] = child_id
            self.children.append(child_item)
        else:
            created = False

        child_item = self.children[child_id]
        child_item._update_events(node)

        return child_item, created

    def _update_events(self, node: omni.activity.core.IEvent):
        """Returns true if the item is ended"""
        if not node.event_count:
            return

        activity_events_count = node.event_count

        if activity_events_count > 512:
            # We have a problem with the following activities:
            #
            # IEventStream(RunLoop.update)::push() Event:0
            # IEventStream(RunLoop.update)::push() Event:0
            # IEventStream(RunLoop.update)::dispatch() Event:0
            # IEventStream(RunLoop.update)::dispatch() Event:0
            # IEventStream(RunLoop.postUpdate)::push() Event:0
            # IEventStream(RunLoop.postUpdate)::push() Event:0
            # IEventStream(RunLoop.postUpdate)::dispatch() Event:0
            # IEventStream(RunLoop.postUpdate)::dispatch() Event:0
            # IEventListener(omni.kit.renderer.plugin.dll!carb::events::LambdaEventListener::onEvent+0x0 at include\carb\events\EventsUtils.h:57)::onEvent
            # IEventListener(omni.kit.renderer.plugin.dll!carb::events::LambdaEventListener::onEvent+0x0 at include\carb\events\EventsUtils.h:57)::onEvent
            # IEventStream(RunLoop.preUpdate)::push() Event:0
            # IEventStream(RunLoop.preUpdate)::push() Event:0
            # IEventStream(RunLoop.preUpdate)::dispatch() Event:0
            # IEventStream(RunLoop.preUpdate)::dispatch() Event:0
            #
            # Each of them has 300k events on Factory Explorer startup. (pairs
            # of Begin-End with 0 duration). When trying to visualize 300k
            # events at once on Python side it fails to do it in adequate time.
            # Ignoring such activities saves 15s of startup time.
            #
            # TODO: But the best would be to not report such activities at all.
            activity_events = [node.get_event(0), node.get_event(activity_events_count - 1)]
            activity_events_count = 2
        else:
            activity_events = [node.get_event(e) for e in range(activity_events_count)]
        activity_events_filtered = []

        # TODO: Temporary. We need to do in in the core
        # Filter out BEGAN+ENDED events with the same timestamp
        i = 0
        # The threshold is 1 ms
        threshold = SECOND_MULTIPLIER * SMALL_ACTIVITY_THRESHOLD
        while i < activity_events_count:
            if (
                i + 1 < activity_events_count
                and activity_events[i].event_type == omni.activity.core.EventType.BEGAN
                and activity_events[i + 1].event_type == omni.activity.core.EventType.ENDED
                and activity_events[i + 1].event_timestamp - activity_events[i].event_timestamp < threshold
            ):
                # Skip them
                i += 2
            elif (
                i + 2 < activity_events_count
                and activity_events[i].event_type == omni.activity.core.EventType.BEGAN
                and activity_events[i + 1].event_type == omni.activity.core.EventType.UPDATED
                and activity_events[i + 2].event_type == omni.activity.core.EventType.ENDED
                and activity_events[i + 2].event_timestamp - activity_events[i].event_timestamp < threshold
            ):
                # Skip them
                i += 3
            else:
                activity_events_filtered.append(activity_events[i])
                i += 1

        if self.__dirty_event_id is None:
            self.__dirty_event_id = len(self.events)

        for activity_event in activity_events_filtered:
            self.events.append(
                ActivityModelEvent(activity_event.event_type, activity_event.event_timestamp, activity_event.payload)
            )

    def update_flags(self):
        self.ended = not self.events or self.events[-1].type == omni.activity.core.EventType.ENDED
        for c in self.children:
            self.ended = self.ended and c.ended

            if c.__child_timerange_dirty or self.__dirty_event_id is not None:
                self.__child_timerange_dirty = True

    def update_size(self):
        if self.events:
            for event in self.events:
                if "size" in event.payload:
                    self.size = event.payload["size"]

    def get_data(self):
        children = []
        for c in self.children:
            children.append(c.get_data())

        # Events
        events = []
        for e in self.events:
            event = {"time": e.time, "type": e.type.name}
            if "size" in e.payload:
                event["size"] = self.size
            events.append(event)

        return {"name": self.name_model.as_string, "children": children, "events": events}

    def get_report_data(self):
        children = []
        for c in self.children:
            children.append(c.get_report_data())

        data = {
            "name": self.name_model.as_string,
            "children": children,
            "duration": self.total_time / SECOND_MULTIPLIER,
        }

        for e in self.events:
            if "size" in e.payload:
                data["size"] = self.size

        return data

    def set_data(self, data):
        """Recreate the item from the data"""
        self.name_model = ui.SimpleStringModel(data["name"])
        self.events: List[ActivityModelEvent] = []

        for e in data["events"]:
            event_type_str = e["type"]
            if event_type_str == "BEGAN":
                event_type = omni.activity.core.EventType.BEGAN
            elif event_type_str == "ENDED":
                event_type = omni.activity.core.EventType.ENDED
            else:  # event_type_str == "UPDATED":
                event_type = omni.activity.core.EventType.UPDATED
            payload = {}
            if "size" in e:
                self.size = e["size"]
                payload["size"] = e["size"]
            self.events.append(ActivityModelEvent(event_type, e["time"], payload))

        self.children: List[ActivityModelItem] = []
        self.child_to_id: Dict[str, int] = {}

        for i, c in enumerate(data["children"]):
            child = ActivityModelItem(c["name"], self)
            child.set_data(c)
            self.children.append(child)
            self.child_to_id[c["name"]] = i


class ActivityModel(ui.AbstractItemModel):
    """Empty Activity model"""

    class _Event(set):
        """
        A list of callable objects. Calling an instance of this will cause a
        call to each item in the list in ascending order by index.
        """

        def __call__(self, *args, **kwargs):
            """Called when the instance is “called” as a function"""
            # Call all the saved functions
            for f in list(self):
                f(*args, **kwargs)

        def __repr__(self):
            """
            Called by the repr() built-in function to compute the “official”
            string representation of an object.
            """
            return f"Event({set.__repr__(self)})"

    class _EventSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, event, fn):
            """
            Save the function, the event, and add the function to the event.
            """
            self._fn = fn
            self._event = event
            event.add(self._fn)

        def __del__(self):
            """Called by GC."""
            self._event.remove(self._fn)

    def __init__(self, **kwargs):
        super().__init__()
        self._stage_path = ""
        self._root = ActivityModelItem("Root", None)

        self.__selection = None
        self._on_selection_changed = ActivityModel._Event()
        self.__on_selection_changed_sub = self.subscribe_selection_changed(kwargs.pop("on_selection_changed", None))

        self._on_timeline_changed = ActivityModel._Event()
        self.__on_timeline_changed_sub = self.subscribe_timeline_changed(kwargs.pop("on_timeline_changed", None))

    def destroy(self):
        self._on_timeline_changed = None
        self.__on_timeline_changed_sub = None

        self.__selection = None
        self._on_selection_changed = None
        self.__on_selection_changed_sub = None

    def subscribe_timeline_changed(self, fn):
        if fn:
            return ActivityModel._EventSubscription(self._on_timeline_changed, fn)

    def subscribe_selection_changed(self, fn):
        if fn:
            return ActivityModel._EventSubscription(self._on_selection_changed, fn)

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is None:
            return self._root.children

        return item.children

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 5

    def get_item_value_model(self, item, column_id):
        """
        Return value model. It's the object that tracks the specific value.
        """
        return item.name_model

    def get_data(self):
        return {"stage": self._stage_path, "root": self._root.get_data(), "begin": self._time_begin, "end": self._time_end}

    def get_report_data(self):
        return {"root": self._root.get_report_data()}

    @property
    def selection(self):
        return self.__selection

    @selection.setter
    def selection(self, value):
        if not self.__selection or self.__selection != value:
            self.__selection = value
            self._on_selection_changed()


class ActivityModelDump(ActivityModel):
    """Activity model with pre-defined data"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._data = kwargs.pop("data", [])

        self._time_begin = self._data["begin"]
        self._time_end = self._data["end"]

        # So we can fixup time spans that started early or didn't end.
        global time_begin
        global time_end
        time_begin = self._time_begin
        time_end = self._time_end

        self._root.set_data(self._data["root"])

    def destroy(self):
        super().destroy()


class ActivityModelDumpForProgress(ActivityModelDump):
    """Activity model for loaded data with 3 columns"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 3


class ActivityModelRealtime(ActivityModel):
    """The model that accumulates all the activities"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        activity = omni.activity.core.get_instance()
        self._subscription = activity.create_callback_to_pop(self._activity)

        self._timeline_stop_event = asyncio.Event()
        self._timeline_extend_task = asyncio.ensure_future(
            loop_forever_async(
                TIMELINE_EXTEND_DELAY_SEC,
                self._timeline_stop_event,
                functools.partial(ActivityModelRealtime.__update_timeline, weakref.proxy(self)),
            )
        )

        self._time_begin = activity.current_timestamp
        self._time_end = self._time_begin + int(TIMELINE_EXTEND_DELAY_SEC * SECOND_MULTIPLIER)
        self._activity_pump = False

        # So we can fixup time spans that started early or didn't end.
        global time_begin
        global time_end
        time_begin = self._time_begin
        time_end = self._time_end

    def start(self):
        self._activity_pump = True

    def end(self):
        self._activity_pump = False
        activity = omni.activity.core.get_instance()
        activity.remove_callback(self._subscription)

        self._timeline_stop_event.set()
        if self._timeline_extend_task:
            self._timeline_extend_task.cancel()
            self._timeline_extend_task = None

    def destroy(self):
        super().destroy()
        self.end()

    def _activity(self, node):
        """Called when the activity happened"""
        if self._activity_pump:
            self._update_item(self._root, node)

    def __update_timeline(self):
        """
        Called once a minute to extend the timeline.
        """
        activity = omni.activity.core.get_instance()
        self._time_end = activity.current_timestamp + int(TIMELINE_EXTEND_DELAY_SEC * SECOND_MULTIPLIER)

        # So we can fixup time spans that don't end.
        global time_end
        time_end = self._time_end

        if self._on_timeline_changed:
            self._on_timeline_changed()

    def _update_item(self, parent, node, depth=0):
        """
        Recursively update the item with the activity. Called when the activity
        passed to the UI.
        """
        item, created = parent.find_or_create_child(node)

        events = node.event_count

        for node_id in range(node.child_count):
            child_events = self._update_item(item, node.get_child(node_id), depth + 1)

            # Cascading
            events += child_events

        item.update_flags()

        # If child is created, we need to update the parent
        if created:
            if parent == self._root:
                self._item_changed(None)
            else:
                self._item_changed(parent)

        # If the time/size is changed, we need to update the item
        if events:
            self._item_changed(item)

        return events


class ActivityModelStageOpen(ActivityModelRealtime):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_path(self, path):
        self._stage_path = path
        self.start()

    def destroy(self):
        super().destroy()


class ActivityModelStageOpenForProgress(ActivityModelStageOpen):
    def __init__(self, **kwargs):
        self._flattened_children = []
        super().__init__(**kwargs)

    def destroy(self):
        super().destroy()
        self._flattened_children = []

    def _update_item(self, parent, node, depth=0):
        """
        Recursively update the item with the activity. Called when the activity
        passed to the UI.
        """
        item, created = parent.find_or_create_child(node)

        for node_id in range(node.child_count):
            self._update_item(item, node.get_child(node_id), depth + 1)

        item.update_flags()

        if parent.name_model.as_string in ["Read", "Load", "Materials"]: # Should check for "USD|Read" and "Textures|Load" if possible
            if not created and item in self._flattened_children:
                self._flattened_children.pop(self._flattened_children.index(item))

            self._flattened_children.insert(0, item)
            # make sure the list only keeps the latest items, so else insert won't be too expensive
            if len(self._flattened_children) > 50:
                self._flattened_children.pop()

            # update the item size and parent's children_size
            prev_size = item.size
            item.update_size()
            loaded_size = item.size - prev_size
            if loaded_size > 0:
                parent.children_size += loaded_size

            # if there is newly created items or new updated size, we update the item
            if created or loaded_size > 0:
                self._item_changed(parent)

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 3
