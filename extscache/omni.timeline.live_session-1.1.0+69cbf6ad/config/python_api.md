# Public API for module omni.timeline.live_session:

## Classes

- class TimelineSession
  - def __init__(self, usd_context_name: str, session_user: layers.LiveSessionUser, session_state, role: TimelineSessionRoleType = None)
  - def destroy(self)
  - [property] def live_session_user(self) -> layers.LiveSessionUser
  - [property] def role_type(self) -> TimelineSessionRoleType
  - [property] def role(self) -> TimelineSessionRole
  - def start_session(self)
  - def stop_session(self)
  - def is_running(self) -> bool
  - def enable_sync(self, enabled: bool)
  - def is_sync_enabled(self) -> bool
  - [property] def owner_id(self) -> str
  - [property] def owner(self) -> layers.LiveSessionUser
  - [owner.setter] def owner(self, user: layers.LiveSessionUser)
  - [property] def presenter(self) -> layers.LiveSessionUser
  - [presenter.setter] def presenter(self, user: layers.LiveSessionUser)
  - def request_control(self, want_control: bool = True)
  - def get_request_controls(self) -> List[layers.LiveSessionUser]
  - def get_request_control_ids(self) -> List[str]
  - def add_presenter_changed_fn(self, callback: Callable[[layers.LiveSessionUser], None])
  - def remove_presenter_changed_fn(self, callback: Callable[[layers.LiveSessionUser], None])
  - def add_control_request_changed_fn(self, callback: Callable[[layers.LiveSessionUser, bool], None])
  - def remove_control_request_changed_fn(self, callback: Callable[[layers.LiveSessionUser, bool], None])
  - def add_enable_sync_changed_fn(self, callback: Callable[[bool], None])
  - def remove_enable_sync_changed_fn(self, callback: Callable[[bool], None])
  - def is_owner(self, user: layers.LiveSessionUser) -> bool
  - def is_presenter(self, user: layers.LiveSessionUser) -> bool
  - def is_logged_user(self, user: layers.LiveSessionUser) -> bool
  - def am_i_owner(self) -> bool
  - def am_i_presenter(self) -> bool

- class TimelineSessionRoleType(enum.Enum)
  - LISTENER: Tuple
  - PRESENTER: Tuple

- class SessionState
  - def __init__(self)
  - def add_users(self, users: List[User])
  - def remove_user(self, user_id: str)
  - def destroy(self)
  - def clear_users(self)
  - def find_user(self, user_id: str) -> User
  - [property] def users(self) -> List[User]
  - [property] def timeline_session(self) -> TimelineSession
  - [timeline_session.setter] def timeline_session(self, session: TimelineSession)
  - def add_users_changed_fn(self, callback: Callable[[List[User]], None])
  - def remove_users_changed_fn(self, callback: Callable[[List[User]], None])

## Functions

- def get_session_state() -> SessionState
- def get_session_window() -> UserWindow
- def get_timeline_session() -> TimelineSession
