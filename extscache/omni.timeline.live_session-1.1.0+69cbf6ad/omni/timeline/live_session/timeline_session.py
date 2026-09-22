from carb import log_error
import omni.kit.usd.layers as layers
from typing import Callable, List
from .timeline_director import TimelineDirector
from .timeline_listener import TimelineListener
from .timeline_session_role import TimelineSessionRoleType, TimelineSessionRole
from .timeline_serializer import TimelinePrimSerializer
import omni.kit.notification_manager as nm


class TimelineSession:
    def __init__(
        self,
        usd_context_name: str,
        session_user: layers.LiveSessionUser,
        session_state,
        role: TimelineSessionRoleType = None
    ):
        self._usd_context_name = usd_context_name
        self._serializer = TimelinePrimSerializer()
        self._session_user = session_user
        self._is_running: bool = False
        from .session_state import SessionState
        self._session_state: SessionState = session_state

        role_type = role
        if role_type is None:
            role_type = TimelineSessionRoleType.LISTENER
        self._role: TimelineSessionRole = None
        self._role_type: TimelineSessionRoleType = None
        self._change_role(role_type)

        self._owner: layers.LiveSessionUser = None
        # We may not have the user when we can query the ID already
        self._owner_id: str = None
        self._presenter: layers.LiveSessionUser = None
        self._control_requests: List[str] = []  # List of user IDs

        self._presenter_changed_callbacks = []
        self._request_control_callbacks = []
        self._enable_sync_callbacks = []

    def __del__(self):
        self.destroy()

    def destroy(self):
        # TODO: role, is_running, serializer, etc.
        self._presenter_changed_callbacks = []
        self._control_requests = []
        self._request_control_callbacks = []
        self._enable_sync_callbacks = []

    @property
    def live_session_user(self) -> layers.LiveSessionUser:
        return self._session_user

    @property
    def role_type(self) -> TimelineSessionRoleType:
        return self._role_type

    @property
    def role(self) -> TimelineSessionRole:
        return self._role

    def start_session(self):
        if self._role is None:
            return
        self._is_running = True
        success = self._role.start_session()
        self._control_requests = []

        if success:
            self._owner_id = self._serializer.receiveOwnerUpdate()

    def stop_session(self):
        if self._role is None:
            return
        self._is_running = False
        self._role.stop_session()
        self._control_requests = []

    def is_running(self) -> bool:
        return self._is_running

    def enable_sync(self, enabled: bool):
        if self._role is not None:
            self._role.enable_sync(enabled)

    def is_sync_enabled(self) -> bool:
        return self._role is not None and self._role.is_sync_enabled()

    @property
    def owner_id(self) -> str:
        if self.owner is not None:
            return self.owner.user_id
        elif self._owner_id is not None:
            return self._owner_id
        return None


    @property
    def owner(self) -> layers.LiveSessionUser:
        return self._owner

    @owner.setter
    def owner(self, user: layers.LiveSessionUser):
        if not self._is_running:
            log_error(f'Session must be running to set the owner')
            return
        if user is not None:
            self._owner_id = user.user_id
        if (self._owner is None and user is None) or\
            self._owner is not None and user is not None and\
            self._owner.user_id == user.user_id:
            # No change
            return
        self._owner = user
        self._serializer.sendOwnerUpdate(user)

        # clear all requests
        if self.am_i_owner():
            requests = self._serializer.receiveControlRequests()
            for request in requests:
                self._serializer.sendControlRequest(
                    user_id=request[0],
                    want_control=False,
                    from_owner=True
                )

    @property
    def presenter(self) -> layers.LiveSessionUser:
        return self._presenter

    @presenter.setter
    def presenter(self, user: layers.LiveSessionUser):
        if not self._is_running:
            log_error(f'Session must be running to set the presenter')
            return
        if (self._presenter is None and user is None) or\
            self._presenter is not None and user is not None and\
            self._presenter.user_id == user.user_id:
            # No change
            return
        if not self.am_i_owner():
            log_error(f'Only the session owner is allowed to set the presenter')
            return
        # Remove user from control requests
        if user.user_id in self._control_requests:
            self._on_control_request_received(user.user_id, False)
            self._serializer.sendControlRequest(user.user_id, False, self.am_i_owner())
        if user is not None:
            self._on_presenter_changed(user.user_id)
        self._serializer.sendPresenterUpdate(user)

    def request_control(self, want_control: bool = True):
        if not self._is_running:
            log_error(f'Session must be running to request timeline control')
            return
        user = self._session_user
        if user is not None:
            if (want_control and user.user_id not in self._control_requests) or \
                (not want_control and user.user_id in self._control_requests):
                self._on_control_request_received(user.user_id, want_control)
                self._serializer.sendControlRequest(user.user_id, want_control, self.am_i_owner())

    def get_request_controls(self) -> List[layers.LiveSessionUser]:
        users = []
        for user_id in self._control_requests:
            user = self._session_state.find_user(user_id)
            if user is not None:
                users.append(user)
        return users

    def get_request_control_ids(self) -> List[str]:
        return self._control_requests

    def add_presenter_changed_fn(self, callback: Callable[[layers.LiveSessionUser], None]):
        if callback not in self._presenter_changed_callbacks:
            self._presenter_changed_callbacks.append(callback)

    def remove_presenter_changed_fn(self, callback: Callable[[layers.LiveSessionUser], None]):
        if callback in self._presenter_changed_callbacks:
            self._presenter_changed_callbacks.remove(callback)

    def add_control_request_changed_fn(self, callback: Callable[[layers.LiveSessionUser, bool], None]):
        if callback not in self._request_control_callbacks:
            self._request_control_callbacks.append(callback)

    def remove_control_request_changed_fn(self, callback: Callable[[layers.LiveSessionUser, bool], None]):
        if callback in self._request_control_callbacks:
            self._request_control_callbacks.remove(callback)

    def add_enable_sync_changed_fn(self, callback: Callable[[bool], None]):
        if callback not in self._enable_sync_callbacks:
            self._enable_sync_callbacks.append(callback)

    def remove_enable_sync_changed_fn(self, callback: Callable[[bool], None]):
        if callback in self._enable_sync_callbacks:
            self._enable_sync_callbacks.remove(callback)

    def is_owner(self, user: layers.LiveSessionUser) -> bool:
        return user is not None and self._owner is not None and\
            user.user_id == self._owner.user_id

    def is_presenter(self, user: layers.LiveSessionUser) -> bool:
        return user is not None and self._presenter is not None and\
            user.user_id == self._presenter.user_id

    def is_logged_user(self, user: layers.LiveSessionUser) -> bool:
        return user is not None and self._session_user is not None and\
            user.user_id == self._session_user.user_id

    def am_i_owner(self) -> bool:
        return self.is_owner(self._session_user)

    def am_i_presenter(self) -> bool:
        return self.is_presenter(self._session_user)

    def _do_change_role(self, role_type: TimelineSessionRoleType):
        # TODO: we don't really need the user change listener at the owner client
        #       (the owner sets it)
        if self._role_type == TimelineSessionRoleType.LISTENER:
            self._role = TimelineListener(self._usd_context_name, self._serializer, self)
        elif self._role_type == TimelineSessionRoleType.PRESENTER:
            self._role = TimelineDirector(self._usd_context_name, self._serializer, self)

    def _change_role(self, role_type: TimelineSessionRoleType):
        if self._role_type is not None and self._role_type == role_type:
            return
        self._role_type = role_type

        if self._role is not None:
            if self._is_running:
                self._role.stop_session()

        self._do_change_role(role_type)

        if self._is_running:
            # This also calls self._role.start_session()
            self.start_session()

    def _on_presenter_changed(self, user_id: str):
        user = self._session_state.find_user(user_id)
        if user is None:
            # TODO: if None and we are Presenters, become listener?
            return

        was_current_user_presenter = self.am_i_presenter()
        self._presenter = user

        if user_id is not None and self._session_user is not None and\
            user_id == self._session_user.user_id:
            self._change_role(TimelineSessionRoleType.PRESENTER)
            nm.post_notification(
                "You are now the timeline presenter.",
                status=nm.NotificationStatus.INFO
            )

        else:
            if was_current_user_presenter:
                nm.post_notification(
                    "You are no longer the timeline presenter.",
                    status=nm.NotificationStatus.INFO
                )
            self._change_role(TimelineSessionRoleType.LISTENER)

        for callback in self._presenter_changed_callbacks:
            callback(self._presenter)

    def _on_control_request_received(self, user_id: str, want_control: bool):
        user = self._session_state.find_user(user_id)
        if user is None:
            return

        if self.am_i_owner() and want_control:
            nm.post_notification(
                    f"User {user.user_name} requested to control the timeline.",
                    status=nm.NotificationStatus.INFO
                )

        # NOTE: checks are done on the caller side
        if want_control:
            self._control_requests.append(user_id)
        else:
            self._control_requests.remove(user_id)

        for callback in self._request_control_callbacks:
            callback(user, want_control)

    def _on_enable_sync(self, is_sync_enabled: bool):
        for callback in self._enable_sync_callbacks:
            callback(is_sync_enabled)
