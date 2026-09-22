import omni.ui as ui
from .session_state import SessionState
from .sync_strategy import SyncStrategyType
from .timeline_listener import TimelineListener
from .timeline_session import TimelineSession
from .timeline_session_role import TimelineSessionRoleType
from functools import partial


scrollingframe_style = {
    "background_color": 0xFF23211F,
    "Label:selected": {"color": 0xFFFFFF00}
}


class UserWindow:
    def __init__(self, session_state: SessionState):
        self._session_state: SessionState = session_state

        self._window = ui.Window(
            "Timeline Session",
            width=400,
            height=500,
            visible=False,
            flags=0,
            visibility_changed_fn=self.on_window_visibility_changed,
        )

        with self._window.frame:
            self._ui_container = ui.Frame(build_fn=self._build_ui)

        self._labels = []
        self._selected_user = None
        self._presenter_button = None
        self._diff_slider = None

    def show(self):
        self._window.visible = True
        self._ui_container.rebuild()

    def hide(self):
        self._window.visible = False
        self._selected_user = None

    def on_window_visibility_changed(self, visible):
        if self._session_state is None:
            return
        if visible:
            self._session_state.add_users_changed_fn(self._on_user_changed)
        else:
            self._session_state.remove_users_changed_fn(self._on_user_changed)
        timeline_session = self._session_state.timeline_session
        if timeline_session is not None:
            if visible:
                timeline_session.add_presenter_changed_fn(self._on_user_changed)
                timeline_session.add_control_request_changed_fn(self._on_user_changed)
            else:
                timeline_session.remove_presenter_changed_fn(self._on_user_changed)
                timeline_session.remove_control_request_changed_fn(self._on_user_changed)

    def destroy(self):
        self._presenter_button = None
        self._diff_slider = None
        self._ui_container.destroy()
        self._ui_container = None
        self._window.set_visibility_changed_fn(None)
        self._window.destroy()
        self._window = None
        self._session_state = None
        self._labels = []
        self._selected_user = None

    def _build_ui(self):
        users = self._session_state.users
        self._selected_user = None
        timeline_session = self._session_state.timeline_session
        if timeline_session is None:
            with ui.HStack():
                ui.Label("Timeline session is not available")
                return
        with ui.VStack():
            ui.Label("Session Users", height=30)
            self._labels = []
            with ui.ScrollingFrame(width=390, height=200, style=scrollingframe_style):
                with ui.VStack():
                    for user in users:
                        self._create_user_label(timeline_session, user)
            ui.Label("Timeline Control Requests", height=30)
            with ui.ScrollingFrame(width=390, height=100, style=scrollingframe_style):
                with ui.VStack():
                    for user in timeline_session.get_request_controls():
                        self._create_user_label(timeline_session, user)
            if timeline_session.am_i_owner():
                with ui.HStack(height=50):
                    self._presenter_button = ui.Button("Set as Timeline Presenter",
                                                       clicked_fn=self._on_make_presenter_clicked,
                                                       visible=False)
            elif not timeline_session.am_i_presenter():
                with ui.HStack(height=50):
                    title = "Request Timeline Control"
                    if timeline_session.live_session_user in timeline_session.get_request_controls():
                        title = "Revoke Request"
                    self._presenter_button = ui.Button(title,
                                                       clicked_fn=self._on_request_control_clicked)
                    
            if not timeline_session.am_i_presenter():
                with ui.VStack(height=50):
                    ui.Spacer()
                    with ui.HStack():
                        ui.Label('Allowed time difference from Presenter (sec): ')
                        self._diff_slider = ui.FloatSlider(name='tsync_maxdiff_slider', min=0, max=2)
                        if timeline_session.role is not None and\
                            hasattr(timeline_session.role, 'sync_strategy'):
                            listener: TimelineListener = timeline_session.role
                            strategy_desc = listener.sync_strategy.strategy_desc
                            self._diff_slider.model.set_value(strategy_desc.max_time_diff_sec)
                        self._diff_slider.model.add_value_changed_fn(self._on_diff_slider_changed)
                    ui.Spacer()

    def _create_user_label(self, timeline_session: TimelineSession, user):
        logged_str = f"[Current user]" if timeline_session.is_logged_user(user) else ""
        owner_str = "[Owner]" if timeline_session.is_owner(user) else ""
        presenter_str = "[Presenter]" if timeline_session.is_presenter(user) else ""
        label = ui.Label(f'{user.user_name} ({user.from_app}) {owner_str}{presenter_str}{logged_str}',
                            height=0)
        label.set_mouse_pressed_fn(partial(self._on_user_pressed, label, user))
        self._labels.append(label)

    def _on_user_pressed(self, label, user, x, y, a, b):
        for l in self._labels:
            l.selected = False
        label.selected = True
        self._selected_user = user
        timeline_session = self._session_state.timeline_session
        if self._presenter_button is not None and timeline_session is not None:
            if timeline_session.am_i_owner():
                self._presenter_button.visible = not timeline_session.is_presenter(user)

    def _on_make_presenter_clicked(self):
        if self._selected_user is not None and self._session_state.timeline_session is not None:
            self._session_state.timeline_session.presenter = self._selected_user

    def _on_request_control_clicked(self):
        timeline_session = self._session_state.timeline_session
        if timeline_session is not None:
            current_user = timeline_session.live_session_user
            want_control = current_user not in timeline_session.get_request_controls()
            timeline_session.request_control(want_control)

    def _on_user_changed(self, *_):
        self._ui_container.rebuild()

    def _on_diff_slider_changed(self, value):
        timeline_session = self._session_state.timeline_session
        if timeline_session is not None and timeline_session.role is not None and\
            timeline_session.role_type == TimelineSessionRoleType.LISTENER and \
            hasattr(timeline_session.role, 'sync_strategy'):
            listener: TimelineListener = timeline_session.role
        
            max_diff = value.as_float
            strategy_desc = listener.sync_strategy.strategy_desc
            strategy_desc.max_time_diff_sec = max_diff
            strategy_desc.strategy_type = SyncStrategyType.DIFFERENCE_LIMITED
            listener.sync_strategy.strategy_desc = strategy_desc
            strategy_desc = listener.sync_strategy.strategy_desc
