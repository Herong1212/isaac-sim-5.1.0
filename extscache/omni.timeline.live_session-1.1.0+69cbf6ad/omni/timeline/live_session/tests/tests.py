# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import unittest
import asyncio
from typing import List

import carb
import omni.kit.collaboration.presence_layer as pl
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.usd.layers as layers
import omni.timeline
import omni.timeline.live_session as ls
from omni.kit.usd.layers.tests.mock_utils import MockLiveSyncingApi
from pxr import Sdf, Usd

# for clean up state
from ..live_session_extension import _session_watcher as g_session_watcher
from ..sync_strategy import SyncStrategyType
from ..timeline_serializer import LOOPING_ATTR_NAME, PLAYSTATE_ATTR_NAME, TIME_ATTR_NAME, TIMELINE_PRIM_PATH
from ..timeline_session import TimelineSession
from ..ui_user_window import UserWindow
from .mock_utils import MockJoiner, MockJoinerManager

_fake_layer = None


class TestTimeline(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._app = omni.kit.app.get_app()
        self._usd_context = omni.usd.get_context()
        self._layers = layers.get_layers(self._usd_context)
        self._live_syncing = layers.get_live_syncing(self._usd_context)
        self._timeline = self._usd_context.get_timeline()
        self._end_time = 94874897

        self._simulated_user_name = "test"
        self._simulated_user_id = "abcde"

        self._users = None
        self._presenter = None
        self._control_request = None
        self._want_control = False

        g_session_watcher.start()

        self._mock_joiner_manager = MockJoinerManager()

        # need to create new window for every test case
        self._window = UserWindow(ls.get_session_state())
        self._window_title = "Timeline Session Test Owner"
        self._window._window.title = self._window_title

    async def tearDown(self):
        self._window.destroy()
        self._window = None
        self._mock_joiner_manager.destroy_joiners()
        self._mock_joiner_manager = None
        g_session_watcher.stop()

        if self._usd_context.get_stage():
            await self._usd_context.close_stage_async()
        self._stage = None
        self._fake_layer.Clear()

        await self._reset_timeline()

        self._live_syncing.stop_all_live_sessions()
        self._layers.get_event_stream().pump()

        await self.wait(50)

    async def wait(self, frames=10):
        for _ in range(frames):
            await self._app.next_update_async()

    async def _reset_timeline(self):
        self._timeline.stop()
        self._timeline.clear_zoom()
        self._timeline.set_current_time(0.0)
        self._timeline.set_end_time(self._end_time)
        self._timeline.set_start_time(0.0)
        self._timeline.set_director(None)
        self._timeline.commit()

    async def _create_session(self):

        self._stage_url = "omniverse://__faked_omniverse_server__/test/test.usd"
        global _fake_layer
        if _fake_layer is None:
            _fake_layer = Sdf.Layer.New(Sdf.FileFormat.FindByExtension(".usd"), self._stage_url)

        self._fake_layer = _fake_layer
        self._stage = Usd.Stage.Open(self._fake_layer)
        await self._usd_context.attach_stage_async(self._stage)

        session = self._live_syncing.find_live_session_by_name(self._stage_url, "test")
        if not session:
            session = self._live_syncing.create_live_session("test", self._stage_url)

        self.assertTrue(session, "Failed to create live session.")

        await self._reset_timeline()
        self.assertTrue(self._live_syncing.join_live_session(session))
        await self.wait()
        self.assertTrue(self._live_syncing.is_in_live_session())

        presence_layer = pl.get_presence_layer_interface(self._usd_context)
        self.assertIsNotNone(presence_layer)
        self._presence_stage: Usd.Stage = presence_layer.get_shared_data_stage()
        self.assertIsNotNone(self._presence_stage)

    async def _simulate_user_join(self, user_name, user_id) -> layers.LiveSessionUser:
        user = layers.LiveSessionUser(user_name, user_id, "Create")
        await self._simulate_user_join_with_user_object(user)

        return user

    async def _simulate_user_join_with_user_object(self, user: layers.LiveSessionUser):
        # Access private variable to simulate user login.
        current_session = self._live_syncing.get_current_live_session()
        session_channel = current_session._session_channel()
        session_channel._peer_users[user.user_id] = user
        session_channel._send_layer_event(
            layers.LayerEventType.LIVE_SESSION_USER_JOINED, {"user_name": user.user_name, "user_id": user.user_id}
        )

        await self.wait()

    @MockLiveSyncingApi
    async def test_state(self):
        state = ls.get_session_state()

        # Initial state, no live session
        session = ls.get_timeline_session()
        self.assertIsNone(session)
        self.assertIsNotNone(state)
        self.assertEqual(len(state.users), 0)

        # Create live session, test TimelineSession
        state.add_users_changed_fn(self._on_users_changed)

        await self._create_session()

        session = ls.get_timeline_session()
        self.assertTrue(session.is_running())
        self.assertIsNotNone(session.live_session_user)
        self.assertIsNotNone(session.owner)
        self.assertIsNotNone(session.presenter)
        self.assertTrue(session.am_i_owner())
        self.assertTrue(session.am_i_presenter())
        self.assertEqual(session.owner_id, session.live_session_user.user_id)
        self.assertTrue(session.is_logged_user(session.live_session_user))
        self.assertTrue(session.is_owner(session.live_session_user))
        self.assertTrue(session.is_presenter(session.live_session_user))
        self.assertEqual(len(session.get_request_controls()), 0)
        self.assertEqual(len(session.get_request_control_ids()), 0)
        self.assertTrue(session.is_sync_enabled())
        self.assertIsNotNone(session.role)
        self.assertEqual(session.role_type, ls.TimelineSessionRoleType.PRESENTER)

        self.assertEqual(len(state.users), 1)
        self.assertEqual(state.users[0], session.live_session_user)

        self._assert_users_and_clear(1, session.live_session_user)

        # Join a new user
        new_user = await self._simulate_user_join(self._simulated_user_name, self._simulated_user_id)

        users_with_new_id = [user for user in state.users if user.user_id == self._simulated_user_id]
        self.assertEqual(len(users_with_new_id), 1)
        new_user_from_session = users_with_new_id[0]
        self._assert_users_and_clear(1, new_user_from_session)

        self.assertTrue(session.am_i_owner())
        self.assertTrue(session.am_i_presenter())
        self.assertFalse(session.is_owner(new_user_from_session))
        self.assertFalse(session.is_presenter(new_user_from_session))
        self.assertEqual(len(session.get_request_controls()), 0)

        # Timeline state is sent properly
        await self._test_timeline_send(session, state)

        # Make the new user a presenter
        session.add_presenter_changed_fn(self._on_presenter_changed)

        session.presenter = new_user_from_session
        await self.wait()  # for timeline changes to become active

        self.assertEqual(self._presenter, new_user_from_session)  # callback
        self.assertTrue(session.am_i_owner())
        self.assertFalse(session.am_i_presenter())
        self.assertFalse(session.is_owner(new_user_from_session))
        self.assertTrue(session.is_presenter(new_user_from_session))
        self.assertEqual(session.role_type, ls.TimelineSessionRoleType.LISTENER)

        # We are listeners, cannot change the timeline
        self.assertTrue(self._timeline.is_stopped())  # make sure synchronization does not interfere with the test
        self._timeline.set_current_time(50)
        self._timeline.play()
        self._timeline.commit()
        self.assertAlmostEqual(self._timeline.get_current_time(), 0)
        self.assertTrue(self._timeline.is_stopped())

        # Control request
        session.add_control_request_changed_fn(self._on_control_request)

        session.request_control(True)
        await self.wait()

        self.assertEqual(self._control_request, session.live_session_user)  # callback
        self.assertEqual(self._want_control, True)  # callback
        self.assertEqual(len(session.get_request_controls()), 1)
        self.assertEqual(len(session.get_request_control_ids()), 1)
        self.assertTrue(session.live_session_user in session.get_request_controls())
        self.assertTrue(session.live_session_user.user_id in session.get_request_control_ids())

        session.request_control(True)  # send another control request, test that it is not duplicated
        await self.wait()

        self.assertEqual(len(session.get_request_controls()), 1)
        self.assertEqual(len(session.get_request_control_ids()), 1)

        session.request_control(False)
        await self.wait()

        self.assertEqual(self._control_request, session.live_session_user)  # callback
        self.assertEqual(self._want_control, False)  # callback
        self.assertEqual(len(session.get_request_controls()), 0)
        self.assertEqual(len(session.get_request_control_ids()), 0)

        self._control_request = None
        session.request_control(False)  # test that we don't crash when we remove the request twice
        await self.wait()
        self.assertIsNone(self._control_request)
        self.assertEqual(len(session.get_request_controls()), 0)
        self.assertEqual(len(session.get_request_control_ids()), 0)

        # Timeline state is read properly
        await self._test_timeline_receive(session, state)

        # Stop session
        session.stop_session()
        self.assertFalse(session.is_running())

        state.remove_users_changed_fn(self._on_users_changed)
        session.remove_presenter_changed_fn(self._on_presenter_changed)
        session.remove_control_request_changed_fn(self._on_control_request)

    # This is implementation specific, used in the function below.
    def _get_timeline_playstate(self) -> int:
        if self._timeline.is_playing():
            return 0
        if self._timeline.is_stopped():
            return 2
        return 1

    # As we don't have two clients, we test that the serializer changes the synchronization prim
    #   when the timeline is changed.
    # This needs to be rewritten when the transmission protocol is changed.
    async def _test_timeline_send(self, session, state):
        timeline_prim: Usd.Prim = self._presence_stage.GetPrimAtPath(TIMELINE_PRIM_PATH)
        self.assertTrue(timeline_prim.IsValid(), "Timeline prim needs to be created")

        time = self._timeline.get_current_time()
        looping = self._timeline.is_looping()
        playstate = self._get_timeline_playstate()

        time_attr = timeline_prim.GetAttribute(TIME_ATTR_NAME)
        looping_attr = timeline_prim.GetAttribute(LOOPING_ATTR_NAME)
        playstate_attr = timeline_prim.GetAttribute(PLAYSTATE_ATTR_NAME)
        self.assertTrue(time_attr.IsValid())
        self.assertTrue(looping_attr.IsValid())
        self.assertTrue(playstate_attr.IsValid())

        self.assertEqual(time_attr.Get(), time)
        self.assertEqual(looping_attr.Get(), looping)
        self.assertEqual(playstate_attr.Get(), playstate)

        # change timeline values
        time = time + 1
        looping = not looping
        self._timeline.set_current_time(time)
        self._timeline.set_looping(looping)
        self.assertFalse(self._timeline.is_playing())  # make sure time is not changed automatically
        await self.wait()

        self.assertEqual(time_attr.Get(), time)
        self.assertEqual(looping_attr.Get(), looping)

        self._timeline.play()
        await self.wait()
        self.assertEqual(playstate_attr.Get(), self._get_timeline_playstate())

        # restore
        self._timeline.stop()
        self._timeline.set_current_time(0)
        self._timeline.commit()

    # As we don't have two clients, we test that the serializer reads the result
    #   when the synchronization prim is changed and applies it to the timeline.
    # This needs to be rewritten when the transmission protocol is changed.
    async def _test_timeline_receive(self, sesssion, state):
        timeline_prim: Usd.Prim = self._presence_stage.GetPrimAtPath(TIMELINE_PRIM_PATH)
        self.assertTrue(timeline_prim.IsValid(), "Timeline prim needs to be created")

        time = self._timeline.get_current_time()
        looping = self._timeline.is_looping()
        self.assertFalse(self._timeline.is_playing())
        playstate = self._get_timeline_playstate()

        time_attr = timeline_prim.GetAttribute(TIME_ATTR_NAME)
        looping_attr = timeline_prim.GetAttribute(LOOPING_ATTR_NAME)
        playstate_attr = timeline_prim.GetAttribute(PLAYSTATE_ATTR_NAME)
        self.assertTrue(time_attr.IsValid())
        self.assertTrue(looping_attr.IsValid())
        self.assertTrue(playstate_attr.IsValid())
        self.assertEqual(time_attr.Get(), time)
        self.assertEqual(looping_attr.Get(), looping)
        self.assertEqual(playstate_attr.Get(), playstate)

        # change prim values
        time = time + 1
        looping = not looping
        time_attr.Set(time)
        looping_attr.Set(looping)
        await self.wait()

        self.assertEqual(self._timeline.get_current_time(), time)
        self.assertEqual(self._timeline.is_looping(), looping)

        playstate_attr.Set(0)
        await self.wait()
        self.assertFalse(self._timeline.is_stopped())  # sync strategies may set to paused but not stopped

        # restore
        self._timeline.stop()
        self._timeline.set_current_time(0)
        self._timeline.commit()

    def _on_users_changed(self, user_list):
        self._users = user_list

    def _assert_users_and_clear(self, expected_size, must_have_user):
        self.assertIsNotNone(self._users)
        self.assertEqual(len(self._users), expected_size)
        if must_have_user is not None:
            self.assertTrue(must_have_user in self._users)
        self._users = None

    def _on_presenter_changed(self, user):
        self._presenter = user

    def _on_control_request(self, user, want_control):
        self._control_request = user
        self._want_control = want_control

    async def _mock_join_session(
        self, sync_strategy_type: SyncStrategyType = SyncStrategyType.DIFFERENCE_LIMITED
    ) -> MockJoiner:
        mock_joiner = self._mock_joiner_manager.create_joiner(
            self._timeline,
            self._simulated_user_name,
            self._simulated_user_id,
            ls.get_timeline_session().live_session_user,
            sync_strategy_type,
        )

        mock_joiner.mock_timeline_session.start_session()
        await self._simulate_user_join_with_user_object(mock_joiner.joiner)

        return mock_joiner

    async def _sync_received_update_events_from_presenter(
        self, mock_joiners: List[MockJoiner], wait_frame: int = 4
    ) -> None:
        await self.wait(wait_frame)
        for mock_joiner in mock_joiners:
            mock_joiner.commit_received_update_timeline_events()

    # The following tests are written based on
    # this doc: https://docs.google.com/document/d/1vx2OBSDVKa1GgKwswSY7qmqgpQq46Qnha8L92GCPQNs/edit?pli=1#heading=h.5tno0u5x49br

    ## 1. User (owner) creates a new session and joins it
    ### a. Expected: User becomes timeline presenter immediately
    @MockLiveSyncingApi
    async def test_create_and_join_session(self):
        await self._create_session()

        session = ls.get_timeline_session()
        self.assertTrue(session.is_running())
        self.assertIsNotNone(session.live_session_user)
        self.assertIsNotNone(session.presenter)
        self.assertTrue(session.am_i_presenter())
        self.assertTrue(session.is_presenter(session.live_session_user))

    ## 2. Set state (e.g. time) to non-default for the presenter. Other users join.
    ### a Expected:
    #### i. joining users become listeners, owner stays presenter
    #### ii. joining users should pick up the synced state immediately
    #### (test that this is also happening when the timeline is not playing!)
    async def _test_change_state_before_other_joining(self, playing: bool):
        await self._create_session()

        # update timeline
        modified_time = self._timeline.get_current_time() + 10
        self._timeline.set_current_time(modified_time)
        if playing:
            # enable playing
            self._timeline.play()

        self._timeline.commit()

        mock_joiner = await self._mock_join_session()

        await self._sync_received_update_events_from_presenter([mock_joiner])

        # make sure presenter does not change
        origin_session = ls.get_timeline_session()
        self.assertTrue(origin_session.is_presenter(origin_session.live_session_user))
        self.assertEqual(len(ls.get_session_state().users), 2)
        self.assertFalse(
            mock_joiner.mock_timeline_session.is_presenter(mock_joiner.mock_timeline_session.live_session_user)
        )
        self.assertTrue(mock_joiner.mock_timeline_session.is_presenter(origin_session.live_session_user))

        ## joining users should pick up the synced state immediately
        self.assertEqual(mock_joiner.get_time_codes_per_seconds(), self._timeline.get_time_codes_per_seconds())
        self.assertEqual(mock_joiner.is_looping(), self._timeline.is_looping())
        self.assertEqual(mock_joiner.is_playing(), self._timeline.is_playing())
        self.assertEqual(mock_joiner.is_playing(), playing)

        if not playing:
            self.assertEqual(mock_joiner.get_current_time(), modified_time)
            self.assertEqual(mock_joiner.get_current_time(), self._timeline.get_current_time())
        else:
            # By default, listeners employ interpolation to synchronize with the presenter's state.
            # Therefore, we must introduce a delay to ensure smooth synchronization.
            self.assertLessEqual(mock_joiner.get_current_time(), modified_time)

            await self._sync_received_update_events_from_presenter([mock_joiner], 100)
            self.assertGreaterEqual(mock_joiner.get_current_time(), modified_time)
            self.assertAlmostEqual(mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1)

    @MockLiveSyncingApi
    async def test_change_state_before_other_joining_in_play_mode(self):
        await self._test_change_state_before_other_joining(True)

    @MockLiveSyncingApi
    async def test_change_state_before_other_joining_in_stop_mode(self):
        await self._test_change_state_before_other_joining(False)

    ## 3. Change time for the presenter
    ## 4. Same with playing, pause, stop
    ### i Expected: time should change for all listeners accordingly
    async def _test_change_time_and_timeline_state(
        self, presenter_timeline: omni.timeline.Timeline, listener_timelines: [omni.timeline.Timeline]
    ):

        # change time
        modified_time = presenter_timeline.get_current_time() + 10
        presenter_timeline.set_current_time(modified_time)
        presenter_timeline.commit()
        self.assertEqual(presenter_timeline.get_current_time(), modified_time)

        await self.wait()
        for timeline in listener_timelines:
            timeline.commit()
            self.assertEqual(timeline.get_current_time(), modified_time)
            self.assertEqual(timeline.get_current_time(), presenter_timeline.get_current_time())

        # play
        presenter_timeline.play()
        presenter_timeline.commit()
        self.assertTrue(presenter_timeline.is_playing())

        await self.wait()
        for timeline in listener_timelines:
            timeline.commit()
            self.assertAlmostEqual(timeline.get_current_time(), self._timeline.get_current_time(), delta=1)
            self.assertEqual(timeline.is_playing(), self._timeline.is_playing())
            self.assertEqual(timeline.is_playing(), True)

        # pause
        presenter_timeline.pause()
        presenter_timeline.commit()
        self.assertFalse(presenter_timeline.is_playing())
        self.assertFalse(presenter_timeline.is_stopped())

        await self.wait()
        for timeline in listener_timelines:
            timeline.commit()
            self.assertAlmostEqual(timeline.get_current_time(), presenter_timeline.get_current_time(), delta=1)
            self.assertEqual(timeline.is_playing(), presenter_timeline.is_playing())
            self.assertEqual(timeline.is_playing(), False)
            self.assertEqual(timeline.is_stopped(), presenter_timeline.is_stopped())
            self.assertEqual(timeline.is_stopped(), False)

        # stop
        presenter_timeline.stop()
        presenter_timeline.commit()
        self.assertFalse(presenter_timeline.is_playing())
        self.assertTrue(presenter_timeline.is_stopped())

        await self.wait()
        for timeline in listener_timelines:
            timeline.commit()
            self.assertEqual(timeline.get_current_time(), presenter_timeline.get_current_time())
            self.assertEqual(timeline.is_playing(), presenter_timeline.is_playing())
            self.assertEqual(timeline.is_playing(), False)
            self.assertEqual(timeline.is_stopped(), presenter_timeline.is_stopped())
            self.assertEqual(timeline.is_stopped(), True)

    @MockLiveSyncingApi
    async def test_change_time_and_timeline_state_for_presenter(self):
        await self._create_session()

        mock_joiner = await self._mock_join_session()

        for _ in range(3):
            await self._test_change_time_and_timeline_state(self._timeline, [mock_joiner.mock_timeline])

    # 5. Turn timeline sync off for presenter, start changing time, playing, etc.
    ## a. Expected:
    ### i. time is unchanged for all listeners
    ### ii. UI that shows sync state at the presenter's Kit instance should show sync is off (`is_sync_enabled()` should be false)
    ### iii. UI at listeners shows they are still receiving updates (`is_sync_enabled()` should be true)
    ### and they still cannot control their own timeline (in fact we might change this design)
    # 6. Turn back timeline sync for presenter.
    ## a. Expected: changes that are made for the presenter are synced at listeners;
    ## presenter's UI shows sync is on again (`is_sync_enabled()` should be true)
    @MockLiveSyncingApi
    async def test_presenter_turn_sync_off(self):
        await self._create_session()

        mock_joiner = await self._mock_join_session()

        # sync up state
        await self._sync_received_update_events_from_presenter([mock_joiner])
        old_time = mock_joiner.get_current_time()
        playing = mock_joiner.is_playing()

        # turn off sync
        def expect_false(enabled: bool) -> None:
            return self.assertFalse(enabled)

        ls.get_timeline_session().add_enable_sync_changed_fn(expect_false)
        ls.get_timeline_session().enable_sync(False)
        self.assertFalse(ls.get_timeline_session().is_sync_enabled())

        # change time
        modified_time = self._timeline.get_current_time() + 10
        self._timeline.set_current_time(modified_time)
        self._timeline.commit()

        await self._sync_received_update_events_from_presenter([mock_joiner])
        # listener is still in sync mode
        self.assertTrue(mock_joiner.mock_timeline_session.is_sync_enabled())
        self.assertEqual(mock_joiner.get_current_time(), old_time)
        self.assertNotEqual(mock_joiner.get_current_time(), modified_time)

        # play
        self._timeline.play()
        self._timeline.commit()

        # play for a while
        await self._sync_received_update_events_from_presenter([mock_joiner], 30)
        self.assertEqual(mock_joiner.get_current_time(), old_time)
        self.assertNotAlmostEqual(mock_joiner.get_current_time(), self._timeline.get_current_time())
        self.assertNotEqual(mock_joiner.is_playing(), self._timeline.is_playing())
        self.assertEqual(mock_joiner.is_playing(), playing)

        # listenr try to modify timeline but fail
        mock_joiner.set_current_time(modified_time)
        mock_joiner.commit()
        self.assertNotEqual(mock_joiner.get_current_time(), modified_time)
        self.assertEqual(mock_joiner.get_current_time(), old_time)

        mock_joiner.play()
        await self._sync_received_update_events_from_presenter([mock_joiner])
        self.assertEqual(mock_joiner.is_playing(), playing)

        # make sure this callback is removed
        ls.get_timeline_session().remove_enable_sync_changed_fn(expect_false)
        ls.get_timeline_session().enable_sync(True)
        self.assertTrue(ls.get_timeline_session().is_sync_enabled())

        # listener should pick up the state from the presenter
        await self._sync_received_update_events_from_presenter([mock_joiner])
        self.assertEqual(mock_joiner.is_playing(), self._timeline.is_playing())

        # By default, listeners employ interpolation to synchronize with the presenter's state.
        # Therefore, we must introduce a delay to ensure smooth synchronization.
        self.assertLessEqual(mock_joiner.get_current_time(), self._timeline.get_current_time())

        await self._sync_received_update_events_from_presenter([mock_joiner], 80)
        self.assertAlmostEqual(mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1)

    # 7. Similar to the previous one,
    # but testing allowed time difference: turn on and off timeline sync during playback.
    ## a. Expected:
    ### i. when sync is turned off during playback,
    ### listeners should pause after a while
    ### (which is determined by the allowed time difference setting,
    ### 0 = immediately, 1 sec = listeners should be 1 sec ahead when they pause).
    ### Test this carefully with looping, playing/pausing/stopping several times.
    ### ii. when sync is turned off and then on very rapidly,
    ### there should be minimal lag at listeners (which depends on the allowed time difference setting)
    @MockLiveSyncingApi
    async def test_presenter_turn_sync_on_and_off_during_playback(self):
        # rounding to 1e-5
        STRICT_MODE_EPS = 1e-5
        await self._create_session()

        default_mode_mock_joiner = await self._mock_join_session()
        strict_mode_mock_joiner = await self._mock_join_session(SyncStrategyType.STRICT)
        loose_mode_mock_joiner = await self._mock_join_session(SyncStrategyType.LOOSE)

        async def play() -> None:
            self._timeline.play()
            self._timeline.commit()
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner]
            )

            self.assertTrue(default_mode_mock_joiner.is_playing())
            # In strict mode, the system adheres strictly to the presenter's timeline.
            # Thus, we validate that the mock joiner isn't playing in this mode.
            self.assertFalse(strict_mode_mock_joiner.is_playing())
            self.assertTrue(loose_mode_mock_joiner.is_playing())

        async def disable_sync_during_playing_and_wait_for_a_while():
            ls.get_timeline_session().enable_sync(False)
            self.assertFalse(ls.get_timeline_session().is_sync_enabled())
            last_seen_time_from_presenter = self._timeline.get_current_time()

            # wait for a while
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner], 80
            )
            self.assertTrue(default_mode_mock_joiner.mock_timeline_session.is_sync_enabled())
            self.assertTrue(strict_mode_mock_joiner.mock_timeline_session.is_sync_enabled())
            self.assertTrue(loose_mode_mock_joiner.mock_timeline_session.is_sync_enabled())

            self.assertFalse(default_mode_mock_joiner.is_playing())
            self.assertFalse(strict_mode_mock_joiner.is_playing())
            self.assertTrue(loose_mode_mock_joiner.is_playing())

            # only follow the presenter
            self.assertAlmostEqual(
                last_seen_time_from_presenter, strict_mode_mock_joiner.get_current_time(), delta=STRICT_MODE_EPS
            )
            self.assertLess(last_seen_time_from_presenter, default_mode_mock_joiner.get_current_time())
            # stop after listener's time is 1 + some eps ahead the last seen presenter time
            self.assertAlmostEqual(
                last_seen_time_from_presenter, default_mode_mock_joiner.get_current_time(), delta=1.5
            )
            # keep playing
            self.assertLess(last_seen_time_from_presenter, loose_mode_mock_joiner.get_current_time())

        async def enable_sync_during_playing() -> None:
            # sync back
            ls.get_timeline_session().enable_sync(True)
            self.assertTrue(ls.get_timeline_session().is_sync_enabled())
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner]
            )

            self.assertTrue(default_mode_mock_joiner.is_playing())
            self.assertFalse(strict_mode_mock_joiner.is_playing())
            self.assertTrue(loose_mode_mock_joiner.is_playing())

            # in default mode, listeners employ interpolation to synchronize with the presenter's state.
            # So it will not catch up immediately
            self.assertLessEqual(default_mode_mock_joiner.get_current_time(), self._timeline.get_current_time())
            # in strict mode, time should be synced with the presenter immediately
            self.assertAlmostEqual(
                strict_mode_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1
            )

            # in default mode, listeners employ interpolation to synchronize with the presenter's state.
            # Therefore, we must introduce a delay to ensure smooth synchronization.
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner], 100
            )
            self.assertAlmostEqual(
                default_mode_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1
            )
            self.assertAlmostEqual(
                strict_mode_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1
            )

        async def pause() -> None:
            self._timeline.pause()
            self._timeline.commit()
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner]
            )

            self.assertFalse(default_mode_mock_joiner.is_playing())
            self.assertFalse(strict_mode_mock_joiner.is_playing())
            self.assertFalse(loose_mode_mock_joiner.is_playing())

            self.assertAlmostEqual(
                default_mode_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1
            )
            self.assertAlmostEqual(
                strict_mode_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=STRICT_MODE_EPS
            )

        async def trigger_loop() -> None:
            # trigger loop
            self._timeline.set_current_time(self._end_time - 1)
            self._timeline.commit()
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner]
            )
            self.assertEqual(default_mode_mock_joiner.get_current_time(), self._timeline.get_current_time())
            self.assertEqual(strict_mode_mock_joiner.get_current_time(), self._timeline.get_current_time())
            self.assertEqual(loose_mode_mock_joiner.get_current_time(), self._timeline.get_current_time())

            # play for a while to start from the begining
            self._timeline.play()
            self._timeline.commit()
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner], 100
            )
            self.assertTrue(default_mode_mock_joiner.is_playing())
            self.assertFalse(strict_mode_mock_joiner.is_playing())
            self.assertTrue(loose_mode_mock_joiner.is_playing())

            self.assertGreaterEqual(default_mode_mock_joiner.get_current_time(), 0)
            self.assertGreaterEqual(strict_mode_mock_joiner.get_current_time(), 0)
            self.assertGreaterEqual(loose_mode_mock_joiner.get_current_time(), 0)

        async def stop() -> None:
            self._timeline.stop()
            self._timeline.commit()
            await self._sync_received_update_events_from_presenter(
                [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner]
            )

            self.assertFalse(default_mode_mock_joiner.is_playing())
            self.assertFalse(strict_mode_mock_joiner.is_playing())
            self.assertFalse(loose_mode_mock_joiner.is_playing())

            self.assertEqual(default_mode_mock_joiner.get_current_time(), 0)
            self.assertEqual(strict_mode_mock_joiner.get_current_time(), 0)
            self.assertEqual(loose_mode_mock_joiner.get_current_time(), 0)

        # for joiners to sync up
        await self._sync_received_update_events_from_presenter(
            [default_mode_mock_joiner, strict_mode_mock_joiner, loose_mode_mock_joiner]
        )

        for _ in range(2):
            for _ in range(2):
                await play()
                await disable_sync_during_playing_and_wait_for_a_while()
                await enable_sync_during_playing()

                # pause
                await pause()
                await play()
                await disable_sync_during_playing_and_wait_for_a_while()
                await enable_sync_during_playing()
                await pause()

            # loop
            await trigger_loop()
            await disable_sync_during_playing_and_wait_for_a_while()
            await enable_sync_during_playing()

            # stop
            await stop()
            await play()
            await disable_sync_during_playing_and_wait_for_a_while()
            await enable_sync_during_playing()

            await stop()

        # turn on and off very rapidly
        await play()

        # making sure default_mode_listener never pause
        for _ in range(20):
            ls.get_timeline_session().enable_sync(False)
            ls.get_timeline_session().enable_sync(True)
            self.assertTrue(default_mode_mock_joiner.is_playing())
            await self.wait(1)

    # 8. Leave timeline sync on for presenter, turn it off for some of the listeners
    ## a. Expected: these listeners can control their own timeline
    ## and receive nothing from the synced state; corresponding UI shows sync is off (`is_sync_enabled()` is the state of the UI)
    # 9. Turn sync back for listeners
    ## a. Expected:
    ### i. If the synced (the presenter's) timeline is playing, it should start playing for the listeners again
    ### ii. If the synced (the presenter's) timeline is not playing,
    ### the time at the listeners should jump to the synced time.
    ### This is a bit different than the previous case,
    ### as we want to make sure that listeners pick up the synced state
    ### even if it has not changed since they re-enabled timeline sync. (In the previous case, if the timeline is playing they keep getting new time updates)
    @MockLiveSyncingApi
    async def test_listeners_turn_sync_off_and_on(self):
        await self._create_session()

        disable_sync_mock_joiner = await self._mock_join_session()
        enable_sync_mock_joiner = await self._mock_join_session()

        disable_sync_mock_joiner.mock_timeline_session.enable_sync(False)
        self.assertFalse(disable_sync_mock_joiner.mock_timeline_session.is_sync_enabled())
        old_time = disable_sync_mock_joiner.get_current_time()

        # change time
        modified_time = self._timeline.get_current_time() + 10
        self._timeline.set_current_time(modified_time)
        self._timeline.commit()

        await self._sync_received_update_events_from_presenter([disable_sync_mock_joiner, enable_sync_mock_joiner])

        self.assertEqual(disable_sync_mock_joiner.get_current_time(), old_time)
        self.assertNotEqual(disable_sync_mock_joiner.get_current_time(), self._timeline.get_current_time())

        self.assertEqual(enable_sync_mock_joiner.get_current_time(), modified_time)
        self.assertEqual(enable_sync_mock_joiner.get_current_time(), self._timeline.get_current_time())

        # manipluate time
        new_time = old_time + 3
        disable_sync_mock_joiner.set_current_time(new_time)
        disable_sync_mock_joiner.commit()

        self.assertEqual(disable_sync_mock_joiner.get_current_time(), new_time)
        self.assertNotEqual(disable_sync_mock_joiner.get_current_time(), self._timeline.get_current_time())

        # should pick up state after enable_sync
        disable_sync_mock_joiner.mock_timeline_session.enable_sync(True)
        self.assertTrue(disable_sync_mock_joiner.mock_timeline_session.is_sync_enabled())
        await self._sync_received_update_events_from_presenter([disable_sync_mock_joiner])
        self.assertEqual(disable_sync_mock_joiner.get_current_time(), modified_time)
        self.assertEqual(disable_sync_mock_joiner.is_playing(), self._timeline.is_playing())

        # disbale again and make presenter playing
        disable_sync_mock_joiner.mock_timeline_session.enable_sync(False)
        self.assertFalse(disable_sync_mock_joiner.mock_timeline_session.is_sync_enabled())
        old_time = disable_sync_mock_joiner.get_current_time()

        self._timeline.play()
        self._timeline.commit()

        # play for a while
        await self._sync_received_update_events_from_presenter([disable_sync_mock_joiner, enable_sync_mock_joiner], 50)
        self.assertNotEqual(disable_sync_mock_joiner.is_playing(), self._timeline.is_playing())
        self.assertEqual(enable_sync_mock_joiner.is_playing(), self._timeline.is_playing())
        self.assertFalse(disable_sync_mock_joiner.is_playing())
        self.assertTrue(enable_sync_mock_joiner.is_playing())
        self.assertAlmostEqual(enable_sync_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1)
        self.assertLess(disable_sync_mock_joiner.get_current_time(), self._timeline.get_current_time())

        # should pick up state after enable_sync
        disable_sync_mock_joiner.mock_timeline_session.enable_sync(True)
        self.assertTrue(disable_sync_mock_joiner.mock_timeline_session.is_sync_enabled())
        await self._sync_received_update_events_from_presenter([disable_sync_mock_joiner, enable_sync_mock_joiner])
        self.assertEqual(disable_sync_mock_joiner.is_playing(), self._timeline.is_playing())
        self.assertEqual(enable_sync_mock_joiner.is_playing(), self._timeline.is_playing())
        self.assertTrue(disable_sync_mock_joiner.is_playing())
        self.assertTrue(enable_sync_mock_joiner.is_playing())
        self.assertGreater(disable_sync_mock_joiner.get_current_time(), modified_time)
        self.assertAlmostEqual(disable_sync_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1)
        self.assertAlmostEqual(enable_sync_mock_joiner.get_current_time(), self._timeline.get_current_time(), delta=1)

    # 10. Owner passes the presenter role (timeline control) to another user.
    # The new presenter changes its (and thus the synced) timeline, set time, play/pause/stop etc.
    ## a. Expected:
    ### i. Owner (previous presenter) is no longer able to control its own timeline
    ### ii. Everything that the new presenter is doing is synced to all listeners (including the previous presenter!)
    ### iii. Owner is not allowed to pass the presenter role to the same user again (UI: "give control"-like messages turn to "withdraw control" or something similar)
    ### iv. All UI that somehow marks/shows who the presenter is should show the new presenter (user icons, timeline window etc.)
    # 11. Owner passes the presenter role to a new user.
    # Essentially the same as the previous case,
    # except that presenter role passed from a non-owner user to another non-owner.
    # Repeat this several times for several (or all) users.
    # 12. Owner returns the presenter role to him/herself (edge case).
    # Everything should be the same as in the cases above.
    async def _set_as_presenter(self, new_presenter_timeline_session: TimelineSession) -> None:
        owner_session = ls.get_timeline_session()
        owner_session.presenter = new_presenter_timeline_session.live_session_user
        await self.wait()

    async def _validate_presenter_state(
        self,
        old_presenter_timeline: omni.timeline.Timeline,
        new_presenter_timeline: omni.timeline.Timeline,
        new_presenter_timeline_session: TimelineSession,
        new_presenter_window: UserWindow,
        non_presenter_mock_joiners: List[MockJoiner],
        pass_to_owner: bool,
    ) -> None:
        owner_session = ls.get_timeline_session()
        # i. previous presenter could not change timeline
        old_time = old_presenter_timeline.get_current_time()
        new_time = old_time + self._end_time / 10
        old_presenter_timeline.set_current_time(new_time)
        old_presenter_timeline.commit()
        self.assertEqual(old_presenter_timeline.get_current_time(), old_time)
        self.assertNotEqual(old_presenter_timeline.get_current_time(), new_time)

        old_presenter_timeline.play()
        old_presenter_timeline.commit()
        self.assertFalse(old_presenter_timeline.is_playing())

        # ii. new presenter manipulate
        listener_timelines: List[omni.timeline.Timeline] = [old_presenter_timeline]
        for mock_joiner in non_presenter_mock_joiners:
            listener_timelines.append(mock_joiner.mock_timeline)

        for _ in range(3):
            await self._test_change_time_and_timeline_state(new_presenter_timeline, listener_timelines)

        # iv. new presenter
        self.assertEqual(
            new_presenter_timeline_session.is_presenter(owner_session.live_session_user), pass_to_owner, ""
        )
        self.assertEqual(owner_session.is_presenter(owner_session.live_session_user), pass_to_owner, "")
        self.assertEqual(owner_session.am_i_presenter(), pass_to_owner, "")

        self.assertTrue(owner_session.is_presenter(new_presenter_timeline_session.live_session_user))
        self.assertTrue(new_presenter_timeline_session.is_presenter(new_presenter_timeline_session.live_session_user))
        self.assertTrue(new_presenter_timeline_session.am_i_presenter())

        for mock_joiner in non_presenter_mock_joiners:
            self.assertEqual(
                mock_joiner.mock_timeline_session.is_presenter(owner_session.live_session_user), pass_to_owner
            )
            self.assertFalse(new_presenter_timeline_session.is_presenter(mock_joiner.joiner))
            self.assertFalse(
                new_presenter_timeline_session.is_presenter(mock_joiner.mock_timeline_session.live_session_user)
            )

            self.assertFalse(owner_session.is_presenter(mock_joiner.joiner))
            self.assertFalse(owner_session.is_presenter(mock_joiner.mock_timeline_session.live_session_user))

            self.assertFalse(mock_joiner.mock_timeline_session.is_presenter(mock_joiner.joiner))
            self.assertFalse(
                mock_joiner.mock_timeline_session.is_presenter(mock_joiner.mock_timeline_session.live_session_user)
            )
            self.assertTrue(
                mock_joiner.mock_timeline_session.is_presenter(new_presenter_timeline_session.live_session_user)
            )
            self.assertFalse(mock_joiner.mock_timeline_session.am_i_presenter())

        # iii and iv. UI
        owner_window = ui_test.find(self._window_title)
        new_presenter_window_ref = ui_test.find(new_presenter_window._window.title)

        self._window.show()
        new_presenter_window.show()
        await self.wait()

        new_presenter = new_presenter_timeline_session.live_session_user
        search_text = f'**/ScrollingFrame[0]/VStack[0]/Label[*].text == "{new_presenter.user_name} ({new_presenter.from_app}) [Presenter]"'
        if pass_to_owner:
            new_presenter_in_owner_window = owner_window.find_first(
                f'**/ScrollingFrame[0]/VStack[0]/Label[*].text == "{new_presenter.user_name} ({new_presenter.from_app}) [Owner][Presenter][Current user]"'
            )
        else:
            new_presenter_in_owner_window = owner_window.find_first(search_text)
            self.assertIsNotNone(new_presenter_window_ref.find_first(f'{search_text[:-1]}[Current user]"'))

        self.assertIsNotNone(new_presenter_in_owner_window)

        await new_presenter_in_owner_window.click()
        btn = owner_window.find_first('**/Button[*].text == "Set as Timeline Presenter"')
        self.assertIsNotNone(btn)
        self.assertFalse(btn.widget.visible)

        for mock_joiner in non_presenter_mock_joiners:
            mock_joiner_window = ui_test.find(mock_joiner.get_window_title())
            mock_joiner.window.show()
            await self.wait()

            self.assertIsNotNone(mock_joiner_window.find_first(search_text))

            non_presenter = mock_joiner.mock_timeline_session.live_session_user
            non_presenter_text = f'**/ScrollingFrame[0]/VStack[0]/Label[*].text == "{non_presenter.user_name} ({non_presenter.from_app}) "'
            non_presenter_in_owner_window = owner_window.find_first(non_presenter_text)
            self.assertIsNotNone(non_presenter_in_owner_window)
            await non_presenter_in_owner_window.click()
            btn = owner_window.find_first('**/Button[*].text == "Set as Timeline Presenter"')
            self.assertIsNotNone(btn)
            self.assertTrue(btn.widget.visible)

    @MockLiveSyncingApi
    async def test_pass_presenter(self):
        await self._create_session()

        mock_joiners: List[MockJoiner] = []
        for _ in range(2):
            mock_joiners.append(await self._mock_join_session())

        for _ in range(2):
            # 10, 11
            previous_presenter_timeline = self._timeline
            for _ in range(2):
                for mock_joiner in mock_joiners:
                    non_presenters = filter(
                        lambda other: other.joiner.user_id != mock_joiner.joiner.user_id, mock_joiners
                    )
                    await self._set_as_presenter(mock_joiner.mock_timeline_session)
                    await self._validate_presenter_state(
                        previous_presenter_timeline,
                        mock_joiner.mock_timeline,
                        mock_joiner.mock_timeline_session,
                        mock_joiner.window,
                        list(non_presenters),
                        False,
                    )

                    previous_presenter_timeline = mock_joiner.mock_timeline
            # 12
            await self._set_as_presenter(ls.get_timeline_session())
            await self._validate_presenter_state(
                previous_presenter_timeline,
                self._timeline,
                ls.get_timeline_session(),
                self._window,
                mock_joiners,
                True,
            )

    # 13. A listener sends a request to become presenter.
    # Potentially do this with multiple listeners at the same time.
    ## a. Expected: The UI for the listener changes and he can no longer send a request,
    ## instead, he can withdraw it
    # 14. The owner receives a notification about the request and the user(s) that sent the request appear(s) on the "requests" list.
    # The owner is able to select it and has the option to pass the presenter role.
    # 15. A listener revokes its request
    ## a. Expected: the owner no longer sees this user among the requests.
    # 16. Pass presenter role to a user that requested it. 1) listener sends a request, 2) owner gives timeline control
    ## a. Expected, once timeline control is passed:
    ### i. the requester should disappear from the request list at the owner
    ### ii. everything else should be the same (and tested similarly) as when the owner passes the presenter role to another user
    async def _list_check(self, control_requesters: List[MockJoiner]) -> None:
        self.assertEqual(len(ls.get_timeline_session().get_request_control_ids()), len(control_requesters))
        owner_window = ui_test.find(self._window_title)
        for mock_joiner in control_requesters:
            user = mock_joiner.joiner
            control_req_in_owner_window = owner_window.find_first(
                f'**/ScrollingFrame[1]/VStack[0]/Label[*].text == "{user.user_name} ({user.from_app}) "'
            )
            self.assertIsNotNone(control_req_in_owner_window)
            await control_req_in_owner_window.click()
            self.assertTrue(control_req_in_owner_window.widget.selected)
            self.assertIsNotNone(owner_window.find_first('**/Button[*].text == "Set as Timeline Presenter"'))

            mock_joiner_window_ref = ui_test.find_first(mock_joiner.get_window_title())
            self.assertIsNone(mock_joiner_window_ref.find_first('**/Button[*].text == "Request Timeline Control"'))
            self.assertIsNotNone(mock_joiner_window_ref.find_first('**/Button[*].text == "Revoke Request"'))
            self.assertTrue(
                any(
                    user_id == mock_joiner.joiner.user_id
                    for user_id in ls.get_timeline_session().get_request_control_ids()
                )
            )

            for other in filter(lambda other: other.joiner.user_id != mock_joiner.joiner.user_id, control_requesters):
                other_user = other.joiner
                self.assertIsNotNone(
                    mock_joiner_window_ref.find_first(
                        f'**/ScrollingFrame[1]/VStack[0]/Label[*].text == "{other_user.user_name} ({other_user.from_app}) "'
                    )
                )

    async def _remove_user_from_control_list(
        self, set_as_presenter: bool, control_requesters: List[MockJoiner], mock_joiners: List[MockJoiner]
    ) -> None:
        owner_window = ui_test.find(self._window_title)

        chosen_user = control_requesters.pop()
        if set_as_presenter:
            user = chosen_user.joiner
            control_req_in_owner_window = owner_window.find_first(
                f'**/ScrollingFrame[1]/VStack[0]/Label[*].text == "{user.user_name} ({user.from_app}) "'
            )
            self.assertIsNotNone(control_req_in_owner_window)
            await control_req_in_owner_window.click()
            self.assertTrue(control_req_in_owner_window.widget.selected)
            set_presenter_btn = owner_window.find_first('**/Button[*].text == "Set as Timeline Presenter"')
            self.assertIsNotNone(set_presenter_btn)
            await set_presenter_btn.click()
        else:
            # revoke
            chosen_user_window_ref = ui_test.find(chosen_user.get_window_title())
            revoke_btn = chosen_user_window_ref.find_first('**/Button[*].text == "Revoke Request"')
            self.assertIsNotNone(revoke_btn)
            await revoke_btn.click()

        chosen_user.window.show()

        for mock_joiner in mock_joiners:
            mock_joiner.window.show()

        self._window.show()
        await self.wait()

        self.assertIsNone(
            owner_window.find_first(
                f'**/ScrollingFrame[1]/VStack[0]/Label[*].text == "{chosen_user.joiner.user_name} ({chosen_user.joiner.from_app}) "'
            )
        )
        await self._list_check(control_requesters)
        for mock_joiner in mock_joiners:
            self.assertIsNone(
                owner_window.find_first(
                    f'**/ScrollingFrame[1]/VStack[0]/Label[*].text == "{chosen_user.joiner.user_name} ({chosen_user.joiner.from_app}) "'
                )
            )

        if not set_as_presenter:
            return

        await self._validate_presenter_state(
            self._timeline,
            chosen_user.mock_timeline,
            chosen_user.mock_timeline_session,
            chosen_user.window,
            list(filter(lambda other: other.joiner.user_id != chosen_user.joiner.user_id, mock_joiners)),
            False,
        )

    @MockLiveSyncingApi
    async def test_request_control(self):
        await self._create_session()

        mock_joiners: List[MockJoiner] = []
        for _ in range(5):
            mock_joiners.append(await self._mock_join_session())

        control_req_list = list(mock_joiners)

        # 13
        self.assertEqual(len(ls.get_timeline_session().get_request_control_ids()), 0)
        for mock_joiner in mock_joiners:
            mock_joiner_window_ref = ui_test.find(mock_joiner.get_window_title())
            self.assertIsNotNone(mock_joiner_window_ref.find_first('**/Button[*].text == "Request Timeline Control"'))
            self.assertIsNone(mock_joiner_window_ref.find_first('**/Button[*].text == "Revoke Request"'))
            mock_joiner.mock_timeline_session.request_control(True)

        for mock_joiner in mock_joiners:
            mock_joiner.window.show()

        self._window.show()
        await self.wait()

        # 14
        await self._list_check(control_req_list)

        # 15 revoke
        await self._remove_user_from_control_list(False, control_req_list, mock_joiners)

        # 16
        await self._remove_user_from_control_list(True, control_req_list, mock_joiners)

    # 17. Latency estimate: TBD
    ## a. So far I have tested that it returns zero for the presenter and something meaningful or everyone else.
    ## b. Latency for listeners should increase when there's a lag (e.g. artificially introduced sleep) at the presenter
    ## c. Turning timeline sync off for the presenter should not affect the latency
    @MockLiveSyncingApi
    async def test_latency_estimate(self):
        await self._create_session()

        self._timeline.play()
        self._timeline.commit()

        mock_joiners: List[MockJoiner] = []
        for _ in range(3):
            mock_joiners.append(await self._mock_join_session())

        await self._sync_received_update_events_from_presenter(mock_joiners)

        # latency estimate from presenter is 0
        self.assertEqual(ls.get_timeline_session().role.get_latency_estimate(), 0)

        avg_latency = 0.0
        cnt = 50
        for _ in range(cnt):
            await self.wait(1)
            for mock_joiner in mock_joiners:
                avg_latency += mock_joiner.mock_timeline_session.role.get_latency_estimate()

        avg_latency /= cnt

        # turn off sync does not affect latency
        ls.get_timeline_session().enable_sync(False)
        await self._sync_received_update_events_from_presenter(mock_joiners)

        avg_turn_off_sync_latency = 0.0
        cnt = 50
        for _ in range(cnt):
            await self.wait(1)
            for mock_joiner in mock_joiners:
                avg_turn_off_sync_latency += mock_joiner.mock_timeline_session.role.get_latency_estimate()

        avg_turn_off_sync_latency /= cnt

        self.assertAlmostEqual(avg_latency, avg_turn_off_sync_latency, delta=1)

        # simulate lag
        ls.get_timeline_session().stop_session()
        await asyncio.sleep(1.5)

        lag_latency = 0.0
        for _ in range(cnt):
            await self.wait(1)
            for mock_joiner in mock_joiners:
                lag_latency += mock_joiner.mock_timeline_session.role.get_latency_estimate()

        lag_latency /= cnt

        self.assertNotAlmostEqual(avg_latency, lag_latency, delta=1)

        ls.get_timeline_session().start_session()
        await self._sync_received_update_events_from_presenter(mock_joiners)

    # 18. Everyone leaves the session, then owner joins an existing session while there are no other users.
    # (There was a bug at some point when this didn't work.)
    ## a. Expected: owner should become the presenter
    @MockLiveSyncingApi
    @unittest.skip("Need to fix MockLiveSyncingApi to fully mock live session")
    async def test_new_owner(self):
        await self._create_session()
        mock_joiners: List[MockJoiner] = []
        for _ in range(3):
            mock_joiners.append(await self._mock_join_session())

        self._timeline.play()
        self._timeline.commit()
        await self._sync_received_update_events_from_presenter(mock_joiners)

        user_cnt = len(mock_joiners) + 1
        for mock_joiner in mock_joiners:
            user = mock_joiner.joiner
            current_session = self._live_syncing.get_current_live_session()
            session_channel = current_session._session_channel()
            del session_channel._peer_users[user.user_id]
            session_channel._send_layer_event(
                layers.LayerEventType.LIVE_SESSION_USER_LEFT, {"user_name": user.user_name, "user_id": user.user_id}
            )

            await self.wait()
            self.assertIsNone(ls.get_session_state().find_user(user.user_id))
            user_cnt -= 1
            self.assertEqual(len(ls.get_session_state().users), user_cnt)

        # leave
        self._live_syncing.stop_all_live_sessions()
        await self.wait()
        self.assertEqual(len(ls.get_session_state().users), 0)

        # rejoin
        session = self._live_syncing.find_live_session_by_name(self._stage_url, "test")
        self.assertTrue(session, "Failed to find live session.")
        self.assertTrue(self._live_syncing.join_live_session(session))
        await self.wait()
        self.assertTrue(self._live_syncing.is_in_live_session())

        # become presenter
        owner_timeline_session = ls.get_timeline_session()
        self.assertTrue(owner_timeline_session.am_i_presenter())
        self.assertTrue(owner_timeline_session.is_presenter(owner_timeline_session.live_session_user))
        self.assertEqual(owner_timeline_session.role_type, ls.TimelineSessionRoleType.PRESENTER)
