# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


from typing import List

import omni.kit.usd.layers as layers
import omni.timeline
import omni.ui
import omni.usd

from ..session_state import SessionState
from ..sync_strategy import SyncStrategyDescriptor, SyncStrategyType, TimelineSyncStrategyExecutor
from ..timeline_session import TimelineSession
from ..timeline_session_role import TimelineSessionRoleType
from ..ui_user_window import UserWindow


def print_widget_tree(widget: omni.ui.Widget, level: int = 0):
    # Prints the widget tree to the console
    print("  " * level + str(widget.__class__.__name__))
    for child in omni.ui.Inspector.get_children(widget):
        print_widget_tree(child, level + 1)


# making sure context and timeline are unique
_cnt = 0

# need to re-write this once we have mock live session joiner
# for now, it hacks timeline to simulate joiner
class MockTimelineSession(TimelineSession):
    def __init__(
        self,
        usd_context_name: str,
        session_user: layers.LiveSessionUser,
        session_state,
        role: TimelineSessionRoleType,
        hijack_timeline_fn,
    ):
        self._hijack_timeline_fn = hijack_timeline_fn
        super().__init__(usd_context_name, session_user, session_state, role)

    # hijack _do_change_role role inorder to hijack director timeline
    def _do_change_role(self, role_type: TimelineSessionRoleType):
        super()._do_change_role(role_type)
        self._hijack_timeline_fn(self)


class MockJoiner:
    def __init__(
        self,
        main_timeline: omni.timeline.Timeline,
        user: layers.LiveSessionUser,
        sync_strategy_type: SyncStrategyType = SyncStrategyType.DIFFERENCE_LIMITED,
    ):
        # hijack director timeline for making sure `mock_timeline_session` the timeline could achieve the same state as the main timeline
        self.joiner = user
        self.mock_timeline_usd_context = omni.usd.create_context(f"test_another_timeline_contex_{self.joiner.user_id}")
        self.mock_timeline_usd_context.set_timeline(f"mock timeline {self.joiner.user_id}")
        self.mock_timeline = self.mock_timeline_usd_context.get_timeline()
        self.mock_director_timeline_name = f"mock director timeline: {user.user_id}"
        self.mock_director_timeline = omni.timeline.get_timeline_interface(self.mock_director_timeline_name)
        self.has_copied_from_main_timeline = False

        def hijack_timeline_fn(mock_timeline_session: MockTimelineSession):
            if mock_timeline_session.role_type != TimelineSessionRoleType.LISTENER:
                return

            self._copy_from_main_timeline(self.mock_timeline, main_timeline)
            mock_timeline_session.role._director_timeline = None
            mock_timeline_session.role._timeline_sync_executor._timeline = None
            omni.timeline.destroy_timeline(mock_timeline_session.role._timeline_name)

            mock_timeline_session.role._timeline_name = self.mock_director_timeline_name
            mock_timeline_session.role._timeline_sync_executor = TimelineSyncStrategyExecutor(
                SyncStrategyDescriptor(sync_strategy_type), self.mock_director_timeline
            )

        # mock timeline session
        self.mock_session_state = SessionState()
        self.mock_timeline_session = MockTimelineSession(
            self.mock_timeline_usd_context.get_name(),
            self.joiner,
            self.mock_session_state,
            TimelineSessionRoleType.LISTENER,
            hijack_timeline_fn,
        )
        self.mock_session_state.timeline_session = self.mock_timeline_session
        self.mock_session_state.add_users([self.joiner])

        # mock window
        self.window = UserWindow(self.mock_session_state)
        self.window._window.title = f"Timeline Session Test {user.user_name}"

    def set_current_time(self, time: float) -> None:
        self.mock_timeline.set_current_time(time)

    def get_current_time(self) -> float:
        return self.mock_timeline.get_current_time()

    def get_time_codes_per_seconds(self) -> float:
        return self.mock_timeline.get_time_codes_per_seconds()

    def is_playing(self) -> bool:
        return self.mock_timeline.is_playing()

    def is_stopped(self) -> bool:
        return self.mock_timeline.is_stopped()

    def is_looping(self) -> bool:
        return self.mock_timeline.is_looping()

    def play(self) -> None:
        self.mock_timeline.play()

    def commit_received_update_timeline_events(self) -> None:
        self.mock_director_timeline.commit()

    def commit(self) -> None:
        self.mock_timeline.commit()

    def get_window_title(self) -> str:
        return self.window._window.title

    def destroy(self) -> None:
        self.window.destroy()
        self.mock_timeline_session.stop_session()
        self.mock_timeline.set_director(None)
        self.mock_timeline.stop()
        self.mock_timeline.commit()
        self.mock_timeline = None
        self.mock_director_timeline = None
        omni.timeline.destroy_timeline(self.mock_timeline_usd_context.get_timeline_name())
        omni.timeline.destroy_timeline(self.mock_director_timeline_name)
        omni.usd.destroy_context(self.mock_timeline_usd_context.get_name())
        self.mock_timeline_usd_context = None

    # simulate open main timeline from live layer
    def _copy_from_main_timeline(self, mock_timeline: omni.timeline.Timeline, main_timeline: omni.timeline.Timeline):
        if self.has_copied_from_main_timeline:
            return

        self.has_copied_from_main_timeline = True

        mock_timeline.set_end_time(main_timeline.get_end_time())
        mock_timeline.set_start_time(main_timeline.get_start_time())
        mock_timeline.set_time_codes_per_second(main_timeline.get_time_codes_per_seconds())

        mock_timeline.commit()
        return mock_timeline


# need to replace this session_watcher once we have mock live session joiner
class MockJoinerManager:
    def __init__(self):
        self._joiners: List[MockJoiner] = []

    def create_joiner(
        self,
        main_timeline: omni.timeline.Timeline,
        user_name: str,
        user_id: str,
        owner: layers.LiveSessionUser,
        sync_strategy_type: SyncStrategyType = SyncStrategyType.DIFFERENCE_LIMITED,
    ) -> MockJoiner:
        global _cnt
        cnt = _cnt
        _cnt += 1
        joiner_id = len(self._joiners)
        mock_joiner = MockJoiner(
            main_timeline,
            layers.LiveSessionUser(
                f"{user_name}_{joiner_id}", f"{user_id}_{joiner_id}_test_cnt_{cnt}", "timeline live_session test"
            ),
            sync_strategy_type,
        )

        # simulate session watcher
        mock_joiner.mock_session_state.add_users([owner])
        for joiner in self._joiners:
            joiner.mock_session_state.add_users([mock_joiner.joiner])
            mock_joiner.mock_session_state.add_users([joiner.joiner])

        self._joiners.append(mock_joiner)
        return mock_joiner

    def destroy_joiners(self):
        for mock_joiner in self._joiners:
            mock_joiner.destroy()

        self._joiners = []
