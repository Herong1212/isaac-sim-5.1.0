import omni.kit.usd.layers as layers
import omni.usd

from omni.kit.collaboration.presence_layer import LAYER_SUBSCRIPTION_ORDER
from .session_state import SessionState
from .timeline_session import TimelineSession
from .timeline_session_role import TimelineSessionRoleType


class SessionWatcher:
    def __init__(self, usd_context_name: str = ""):
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._live_syncing = layers.get_live_syncing(self._usd_context)
        self._layers = layers.get_layers(self._usd_context)

    def start(self):
        order = LAYER_SUBSCRIPTION_ORDER + 1
        self._layers_event_subscription = None
        self._layers_event_subscription = self._layers.get_event_stream().create_subscription_to_pop(
            self._on_layers_event, name="omni.timeline.live_session", order=order
        )
        self._session_state = SessionState()

    def stop(self):
        if self._session_state.timeline_session is not None:
            self._session_state.timeline_session.stop_session()
            self._session_state.timeline_session = None
        self._layers_event_subscription = None
        self._session_state = None

    def get_timeline_session(self) -> TimelineSession:
        return self._session_state.timeline_session

    def get_session_state(self) -> SessionState:
        return self._session_state

    def _on_layers_event(self, event):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        # Only events from root layer session are handled.
        if payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if not payload.is_layer_influenced(self._usd_context.get_stage_url()):
                return

            self._on_session_state_changed()
        elif payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_JOINED:
            if not payload.is_layer_influenced(self._usd_context.get_stage_url()):
                return

            self._on_user_joined(payload.user_id)
        elif payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT:
            if not payload.is_layer_influenced(self._usd_context.get_stage_url()):
                return

            self._on_user_left(payload.user_id)

    def _on_session_state_changed(self):
        if not self._live_syncing.is_in_live_session():
            if self._session_state.timeline_session is not None:
                self._session_state.timeline_session.stop_session()
            self._session_state.clear_users()
            from .live_session_extension import get_session_window
            window = get_session_window()
            if window:
                window.hide()
        else:
            self._session = self._get_current_session()
            role = TimelineSessionRoleType.LISTENER
            if self._is_owner(self._session):
                role = TimelineSessionRoleType.PRESENTER
            timeline_session = TimelineSession(
                usd_context_name=self._usd_context.get_name(),
                session_user=self._session.logged_user,
                session_state=self._session_state,
                role=role
            )
            self._session_state.add_users([self._session.logged_user])
            self._session_state.timeline_session = timeline_session
            timeline_session.start_session()
            # This needs to happen after we have a session
            if self._is_owner(self._session):
                timeline_session.owner = self._session.logged_user
                timeline_session.presenter = self._session.logged_user

    def _on_user_joined(self, user_id):
        user = self._session.get_peer_user_info(user_id)
        if user is not None:
            self._session_state.add_users([user])
            timeline_session = self._session_state.timeline_session
            if timeline_session is not None:
                if timeline_session.owner_id == user_id:
                    timeline_session.owner = user

    def _on_user_left(self, user_id):
        self._session_state.remove_user(user_id)

    def _get_current_session(self):  # -> LiveSession, TODO: export it in omni.kit.usd.layers
        return self._live_syncing.get_current_live_session()

    def _is_owner(self, session) -> bool:
       return session.merge_permission