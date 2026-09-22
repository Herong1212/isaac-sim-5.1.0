import carb
import carb.eventdispatcher
import enum
import omni.timeline
import omni.usd
import omni.kit.app
import omni.kit.collaboration.presence_layer as pl
from typing import Callable
from .timeline_serializer import TimelineStateSerializer


class TimelineSessionRoleType(enum.Enum):
    LISTENER = 0,
    PRESENTER = 1,


class TimelineSessionRole:
    def __init__(self, usd_context_name: str, serializer: TimelineStateSerializer, session):
        self._main_timeline = omni.usd.get_context(usd_context_name).get_timeline()
        self._context = omni.usd.get_context()
        self._synced_stage = pl.get_presence_layer_interface(self._context).get_shared_data_stage()
        self._stage = self._context.get_stage()
        self._ed = carb.eventdispatcher.get_eventdispatcher()
        self._app_sub_user = None
        self._enable_sync = True
        self._serializer = serializer
        from .timeline_session import TimelineSession
        self._session: TimelineSession = session
        self._last_update_timestamp: float = 0

    def start_session(self) -> bool:
        if self._synced_stage is None:
            carb.log_error(f"{self.__class__}: could not find presence layer")
            return False
        self._app_sub_user = self._ed.observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._check_user_updates,
            observer_name="omni.timeline.live_session.timeline_session_role"
        )
        return True

    def stop_session(self):
        self._app_sub_user = None

    def enable_sync(self, enabled: bool):
        self._enable_sync = enabled
        self._session._on_enable_sync(enabled)

    def is_sync_enabled(self) -> bool:
        return self._enable_sync

    def get_latency_estimate(self) -> float:
        """
        Returns estimated latency in seconds.

        The accuracy depends on the error of synchronized global time.
        """
        return 0

    # TODO: consider moving _check methods to TimelineSession
    def _check_user_updates(self, _):
        self._check_presenter()
        self._check_control_requests()

    def _check_presenter(self):
        presenter_id = self._serializer.receivePresenterUpdate()
        if (self._session.presenter is None and presenter_id is None) or\
            (self._session.presenter is not None and self._session.presenter.user_id == presenter_id):
            return
        self._session._on_presenter_changed(presenter_id)

    def _check_control_requests(self):
        request_list = self._serializer.receiveControlRequests()
        users_want_control = self._session.get_request_control_ids()
        # current behavior of receiveControlRequests:
        # - returns _all_ positive requests (want_control=True)
        # - returns some of the negative requests but not necessarily all of them
        all_want_control = []
        for request in request_list:
            user_id = request[0]
            want_control = request[1]
            if want_control:
                all_want_control.append(user_id)
            if (want_control and user_id not in users_want_control) or\
                (not want_control and user_id in users_want_control):
                self._session._on_control_request_received(user_id, want_control)

        for user_id in self._session.get_request_control_ids():
            # Remove if not in the set of all users that want control
            if user_id not in all_want_control:
                self._session._on_control_request_received(user_id, False)
