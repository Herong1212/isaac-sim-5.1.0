import carb
import omni.kit.usd.layers as layers
import omni.timeline
from pxr import Sdf, Usd
from typing import List, Tuple
from .global_time import get_global_time_s
from .timeline_event import TimelineEvent
from .timeline_state import (
    get_timeline_state,
    get_timeline_next_events,
    get_timeline_next_state,
    PlayState,
    TimelineState
)


TIMELINE_PRIM_PATH = '/__session_shared_data__/Omni_Timeline_Live_Sync'
TIME_ATTR_NAME = 'timeline:time'
CONTROL_ID_PREF = 'timeline:control:ID_'
LOOPING_ATTR_NAME = 'timeline:looping'
OWNER_ID_ATTR_NAME = 'timeline:owner:id'
PLAYSTATE_ATTR_NAME = 'timeline:playstate'
OWNER_NAME_ATTR_NAME = 'timeline:owner:name'
PRESENTER_ID_ATTR_NAME = 'timeline:presenter:id'
GLB_TIMESTAMP_ATTR_NAME = 'timeline:timestamp'
PRESENTER_NAME_ATTR_NAME = 'timeline:presenter:name'
ZOOM_RANGE_END_ATTR_NAME  = 'timeline:zoom_end'
ZOOM_RANGE_START_ATTR_NAME = 'timeline:zoom_start'


def prop_path(prop_name: str) -> str:
    return TIMELINE_PRIM_PATH + '.' + prop_name


class TimelineStateSerializer:
    def __init__(self):
        self._timeline = None
        self._stage = None

    def initialize(self, timeline, synced_stage: Usd.Stage, sending: bool):
        self._timeline = timeline
        self._stage = synced_stage
        self._timeline_state = TimelineState(timeline)

    def finalize(self):
        pass

    def sendTimelineUpdate(self, e: TimelineEvent):
        pass

    def receiveTimelineUpdate(self) -> List[TimelineEvent]:
        return []

    def receiveTimestamp(self) -> float:
        return 0

    def sendOwnerUpdate(self, user: layers.LiveSessionUser):
        pass

    def receiveOwnerUpdate(self) -> str:
        """
        Returns user ID
        """
        pass

    def sendPresenterUpdate(self, user: layers.LiveSessionUser):
        pass

    def receivePresenterUpdate(self) -> str:
        """
        Returns user ID
        """
        pass

    def sendControlRequest(self, user_id: str, want_control: bool, from_owner: bool):
        pass

    def receiveControlRequests(self) -> List[Tuple[str, bool]]:
        pass


class TimelinePrimSerializer(TimelineStateSerializer):
    """
    Communicates timeline messages via attributes of a single shared prim.
    It transforms events to state and vice versa.
    """
    def __init__(self):
        super().__init__()
        self._layer = None

    def initialize(self, timeline, synced_stage: Usd.Stage, sending: bool):
        super().initialize(timeline, synced_stage, sending)
        self._layer = self._stage.GetRootLayer() if self._stage is not None else None

        self._timeline_prim_path = TIMELINE_PRIM_PATH

        if sending:
            self._setup_timeline_prim()
        else:
            self._timeline_prim = self._stage.GetPrimAtPath(self._timeline_prim_path)
            if not self._timeline_prim.IsValid():
                carb.log_warn(f'{self.__class__}: Could not find timeline prim')

    def sendTimelineUpdate(self, e: TimelineEvent):
        super().sendTimelineUpdate(e)

        if self._stage is None or self._layer is None:
            return

        if not self._timeline_prim.IsValid():
            self._setup_timeline_prim()

        attr_names = []
        values = []
        if e.type == int(omni.timeline.TimelineEventType.PLAY) or\
            e.type == int(omni.timeline.TimelineEventType.PAUSE) or\
            e.type == int(omni.timeline.TimelineEventType.STOP):
            next_state = get_timeline_next_state(self._timeline_state.state, e.type)
            if next_state != self._timeline_state.state:
                # TODO: omni.timeline should send a time changed event instead when stopped
                if e.type == int(omni.timeline.TimelineEventType.STOP):
                    self._timeline_state.current_time = self._timeline.get_start_time()
                self._timeline_state.state = next_state
                attr_names.append(PLAYSTATE_ATTR_NAME)
                values.append(next_state.value)
                attr_names.append(TIME_ATTR_NAME)
                values.append(self._timeline_state.current_time)
        elif e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            self._timeline_state.current_time = e.payload['currentTime']
            attr_names.append(TIME_ATTR_NAME)
            values.append(self._timeline_state.current_time)
        elif e.type == int(omni.timeline.TimelineEventType.LOOP_MODE_CHANGED):
            self._timeline_state.looping = e.payload['looping']
            attr_names.append(LOOPING_ATTR_NAME)
            values.append(self._timeline_state.looping)
        elif e.type == int(omni.timeline.TimelineEventType.ZOOM_CHANGED):
            self._timeline_state.set_zoom_range(e.payload['startTime'], e.payload['endTime'])
            attr_names.append(ZOOM_RANGE_START_ATTR_NAME)
            values.append(self._timeline_state.zoom_range[0])
            attr_names.append(ZOOM_RANGE_END_ATTR_NAME)
            values.append(self._timeline_state.zoom_range[1])

        with Sdf.ChangeBlock():
            for attr_name, value in zip(attr_names, values):
                self._layer.GetAttributeAtPath(prop_path(attr_name)).default = value
            if len(attr_names) > 0 or \
                e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT):
                self._layer.GetAttributeAtPath(prop_path(GLB_TIMESTAMP_ATTR_NAME)).default = e.timestamp

    def receiveTimelineUpdate(self) -> List[TimelineEvent]:
        if self._stage is None or self._layer is None:
            return []
        if not self._timeline_prim.IsValid():
            return []

        events = []
        play_state = self._layer.GetAttributeAtPath(prop_path(PLAYSTATE_ATTR_NAME)).default
        try:
            play_state = PlayState(play_state)
        except:
            carb.log_error(
                f'Invalid invalid playstate in timeline event serialization: {play_state}')
            play_state = self._timeline_state.state
        current_time = self._layer.GetAttributeAtPath(prop_path(TIME_ATTR_NAME)).default
        timestamp = self._layer.GetAttributeAtPath(prop_path(GLB_TIMESTAMP_ATTR_NAME)).default
        looping = self._layer.GetAttributeAtPath(prop_path(LOOPING_ATTR_NAME)).default
        zoom_start = self._layer.GetAttributeAtPath(prop_path(ZOOM_RANGE_START_ATTR_NAME)).default
        zoom_end = self._layer.GetAttributeAtPath(prop_path(ZOOM_RANGE_END_ATTR_NAME)).default

        if looping != self._timeline_state.looping:
            self._timeline_state.looping = looping
            event = TimelineEvent(
                type=omni.timeline.TimelineEventType.LOOP_MODE_CHANGED,
                payload={'looping' : looping},
                timestamp=timestamp
            )
            events.append(event)

        if play_state != self._timeline_state.state:
            timeline_events = get_timeline_next_events(self._timeline_state.state, play_state)
            self._timeline_state.state = play_state
            for timeline_event in timeline_events:
                event = TimelineEvent(
                    timeline_event,
                    payload={'currentTime' : current_time},  # for better sync strategies
                    timestamp=timestamp
                )
                events.append(event)

        if current_time != self._timeline_state.current_time:
            self._timeline_state.current_time = current_time
            event = TimelineEvent(
                type=omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
                payload={'currentTime' : current_time},
                timestamp=timestamp
            )
            events.append(event)

        if zoom_start != self._timeline_state.zoom_range[0] or zoom_end != self._timeline_state.zoom_range[1]:
            self._timeline_state.set_zoom_range(zoom_start, zoom_end)
            event = TimelineEvent(
                type=omni.timeline.TimelineEventType.ZOOM_CHANGED,
                payload={'startTime' : zoom_start, 'endTime' : zoom_end},
                timestamp=timestamp
            )
            events.append(event)

        return events

    def receiveTimestamp(self) -> float:
        if self._stage is None or self._layer is None:
            return 0
        if not self._timeline_prim.IsValid():
            return 0
        return self._layer.GetAttributeAtPath(prop_path(GLB_TIMESTAMP_ATTR_NAME)).default

    def sendOwnerUpdate(self, user: layers.LiveSessionUser):
        super().sendOwnerUpdate(user)
        if self._stage is None or self._layer is None:
            return

        if not self._timeline_prim.IsValid():
            self._setup_timeline_prim()
        self._layer.GetAttributeAtPath(prop_path(OWNER_ID_ATTR_NAME)).default = user.user_id
        self._layer.GetAttributeAtPath(prop_path(OWNER_NAME_ATTR_NAME)).default = user.user_name

    def receiveOwnerUpdate(self) -> str:
        if self._stage is None or self._layer is None:
            return None
        if not self._timeline_prim.IsValid():
            return None

        return self._layer.GetAttributeAtPath(prop_path(OWNER_ID_ATTR_NAME)).default

    def sendPresenterUpdate(self, user: layers.LiveSessionUser):
        super().sendPresenterUpdate(user)
        if self._stage is None or self._layer is None:
            return

        if not self._timeline_prim.IsValid():
            self._setup_timeline_prim()
        self._layer.GetAttributeAtPath(prop_path(PRESENTER_ID_ATTR_NAME)).default = user.user_id
        self._layer.GetAttributeAtPath(prop_path(PRESENTER_NAME_ATTR_NAME)).default = user.user_name

    def receivePresenterUpdate(self) -> str:
        if self._stage is None or self._layer is None:
            return None
        if not self._timeline_prim.IsValid():
            return None

        return self._layer.GetAttributeAtPath(prop_path(PRESENTER_ID_ATTR_NAME)).default

    def sendControlRequest(self, user_id: str, want_control: bool, from_owner: bool):
        super().sendControlRequest(user_id, want_control, from_owner)
        if self._stage is None or self._layer is None:
            return

        if not self._timeline_prim.IsValid():
            if from_owner:
                self._setup_timeline_prim()
            else:
                return
        prim = self._timeline_prim

        prefix = CONTROL_ID_PREF
        attr_name = f'{prefix}{user_id}'
        if want_control:
            if not prim.HasAttribute(attr_name):
                prim.CreateAttribute(attr_name, Sdf.ValueTypeNames.Int)
            prim.GetAttribute(attr_name).Set(1)
        elif prim.HasAttribute(attr_name):  # Nothing to do if the attribute does not exist
            if from_owner:
                prim.RemoveProperty(attr_name)
            else:
                prim.GetAttribute(attr_name).Set(0)

    def receiveControlRequests(self) -> List[Tuple[str, bool]]:
        if self._stage is None or self._layer is None:
            return []
        if not self._timeline_prim.IsValid():
            return []

        requests = []
        prim_spec = self._layer.GetPrimAtPath(self._timeline_prim_path)
        for property in prim_spec.properties:
            attr_name: str = property.name
            prefix = CONTROL_ID_PREF
            if attr_name.startswith(prefix):
                user_id = attr_name.removeprefix(prefix)
                want_control = property.default
                requests.append([user_id, want_control != 0])
        return requests

    def _setup_timeline_prim(self):
        self._stage.DefinePrim(self._timeline_prim_path)
        self._timeline_prim = self._stage.GetPrimAtPath(self._timeline_prim_path)
        prim = self._timeline_prim
        prim.SetMetadata("hide_in_stage_window", True)
        if not prim.IsValid():
            carb.log_error("Coding error in TimelinePrimSerializer: trying to create attributes of an invalid prim")
            return
        if not prim.HasAttribute(PLAYSTATE_ATTR_NAME):
            prim.CreateAttribute(PLAYSTATE_ATTR_NAME, Sdf.ValueTypeNames.Int)
        if not prim.HasAttribute(TIME_ATTR_NAME):
            prim.CreateAttribute(TIME_ATTR_NAME, Sdf.ValueTypeNames.Double)
        if not prim.HasAttribute(LOOPING_ATTR_NAME):
            prim.CreateAttribute(LOOPING_ATTR_NAME, Sdf.ValueTypeNames.Bool)
        if not prim.HasAttribute(ZOOM_RANGE_START_ATTR_NAME):
            prim.CreateAttribute(ZOOM_RANGE_START_ATTR_NAME, Sdf.ValueTypeNames.Double)
        if not prim.HasAttribute(ZOOM_RANGE_END_ATTR_NAME):
            prim.CreateAttribute(ZOOM_RANGE_END_ATTR_NAME, Sdf.ValueTypeNames.Double)
        if not prim.HasAttribute(GLB_TIMESTAMP_ATTR_NAME):
            prim.CreateAttribute(GLB_TIMESTAMP_ATTR_NAME, Sdf.ValueTypeNames.Double)
        if not prim.HasAttribute(OWNER_ID_ATTR_NAME):
            prim.CreateAttribute(OWNER_ID_ATTR_NAME, Sdf.ValueTypeNames.String)
        if not prim.HasAttribute(OWNER_NAME_ATTR_NAME):
            prim.CreateAttribute(OWNER_NAME_ATTR_NAME, Sdf.ValueTypeNames.String)
        if not prim.HasAttribute(PRESENTER_ID_ATTR_NAME):
            prim.CreateAttribute(PRESENTER_ID_ATTR_NAME, Sdf.ValueTypeNames.String)
        if not prim.HasAttribute(PRESENTER_NAME_ATTR_NAME):
            prim.CreateAttribute(PRESENTER_NAME_ATTR_NAME, Sdf.ValueTypeNames.String)
        prim.GetAttribute(PLAYSTATE_ATTR_NAME).Set(get_timeline_state(self._timeline).value)
        prim.GetAttribute(TIME_ATTR_NAME).Set(self._timeline.get_current_time())
        prim.GetAttribute(LOOPING_ATTR_NAME).Set(self._timeline.is_looping())
        prim.GetAttribute(ZOOM_RANGE_START_ATTR_NAME).Set(self._timeline.get_zoom_start_time())
        prim.GetAttribute(ZOOM_RANGE_END_ATTR_NAME).Set(self._timeline.get_zoom_end_time())
        prim.GetAttribute(GLB_TIMESTAMP_ATTR_NAME).Set(get_global_time_s())
