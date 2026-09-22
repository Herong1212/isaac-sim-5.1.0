from carb import log_error
import omni.kit.usd.layers as layers
from .timeline_session import TimelineSession
from typing import List, Callable


User = layers.LiveSessionUser


class SessionState:
    def __init__(self):
        self._users: List[User] = []
        self._timeline_session: TimelineSession = None
        self._users_changed_callbacks = []

    def add_users(self, users: List[User]):
        self._users.extend(users)
        self._notify_users_changed(users)

    def remove_user(self, user_id: str):
        self._users = list(filter(lambda user: user.user_id != user_id, self._users))
        # TODO: pass the removed user
        self._notify_users_changed([])

    def destroy(self):
        self.clear_users()
        self._timeline_session = None
        self._users_changed_callbacks = []

    def clear_users(self):
        users = self._users
        self._users = []
        self._notify_users_changed(users)

    def find_user(self, user_id: str) -> User:
        for user in self._users:
            if user.user_id == user_id:
                return user
        return None

    @property
    def users(self) -> List[User]:
        return self._users
    
    @property 
    def timeline_session(self) -> TimelineSession:
        return self._timeline_session
    
    @timeline_session.setter
    def timeline_session(self, session: TimelineSession):
        self._timeline_session = session

    def add_users_changed_fn(self, callback: Callable[[List[User]], None]):
        if callback not in self._users_changed_callbacks:
            self._users_changed_callbacks.append(callback)

    def remove_users_changed_fn(self, callback: Callable[[List[User]], None]):
        if callback in self._users_changed_callbacks:
            self._users_changed_callbacks.remove(callback)

    def _notify_users_changed(self, users: List[User]):
        for callback in self._users_changed_callbacks:
            callback(users)
