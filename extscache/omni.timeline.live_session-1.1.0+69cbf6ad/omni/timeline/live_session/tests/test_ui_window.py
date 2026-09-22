# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.ui_test as ui_test
import omni.kit.usd.layers as layers
import omni.ui
import omni.usd
from omni.timeline.live_session.session_state import SessionState
from omni.timeline.live_session.timeline_session import TimelineSession
from omni.timeline.live_session.timeline_session_role import TimelineSessionRoleType
from omni.timeline.live_session.ui_user_window import UserWindow
from omni.ui.tests.test_base import OmniUiTest

# for clean up state
from ..live_session_extension import _session_watcher as g_session_watcher


class TestUiWindow(OmniUiTest):
    fail_on_log_error = False

    async def setUp(self):
        await super().setUp()
        self._window: UserWindow = None
        self._usd_context = None
        self._layers = None
        self._live_syncing = None

        g_session_watcher.start()

    async def tearDown(self):
        g_session_watcher.stop()

        if self._window is not None:
            self._window.hide()
            self._window.destroy()

        self._destroy_stage()
        await super().tearDown()

    async def _setup_stage(self):
        self._usd_context = omni.usd.get_context()
        self._layers = layers.get_layers(self._usd_context)
        self._live_syncing = layers.get_live_syncing(self._usd_context)

        await self._usd_context.new_stage_async()

    def _destroy_stage(self):
        self._usd_context = None
        self._layers = None
        self._live_syncing = None

    async def test_show_hide_window(self):
        self._window = UserWindow(SessionState())
        self._window._window.title = "Timeline Session Test"
        window_ref = ui_test.find("Timeline Session Test")

        self.assertIsNotNone(window_ref)
        self.assertFalse(window_ref.window.visible)

        self._window.show()
        self.assertTrue(window_ref.window.visible)

        self._window.hide()
        self.assertFalse(window_ref.window.visible)

    async def test_no_session(self):
        self._window = UserWindow(SessionState())
        self._window._window.title = "Timeline Session Test"

        window_ref = ui_test.find("Timeline Session Test")
        label = window_ref.find_all("**/Label[*]")
        self.assertEqual(len(label), 1)
        self.assertTrue(label[0].widget.text == "Timeline session is not available")

    async def test_display_user(self):
        session_state = SessionState()
        owner = layers.LiveSessionUser("owner", "owner_id", "test")
        user1 = layers.LiveSessionUser("user1", "user1_id", "test")
        user2 = layers.LiveSessionUser("user2", "user2_id", "test")

        timeline_session = TimelineSession("", owner, session_state, TimelineSessionRoleType.PRESENTER)
        session_state.timeline_session = timeline_session

        self._window = UserWindow(session_state)
        self._window._window.title = "Timeline Session Test"
        # register ui building callback
        self._window.show()

        window_ref = ui_test.find("Timeline Session Test")
        labels = window_ref.find_all("**/Label[*]")

        # without users
        field_texts = ["Session Users", "Timeline Control Requests", "Allowed time difference from Presenter (sec): "]
        for index, label in enumerate(labels):
            self.assertTrue(label.widget.text, field_texts[index])

        # add users
        session_state.add_users([owner, user1])
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")
        self.assertEqual(len(users), 2)
        current_users = ["owner (test) [Current user]", "user1 (test)"]
        for index, user in enumerate(users):
            self.assertTrue(user.widget.text, current_users[index])
        session_state.add_users([user2])
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")
        self.assertEqual(len(users), 3)
        self.assertTrue(users[2].widget.text, "user2 (test)")

        # remove user
        session_state.remove_user("user2_id")
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")
        self.assertEqual(len(users), 2)
        for index, user in enumerate(users):
            self.assertTrue(user.widget.text, current_users[index])

    async def test_requst_control_list(self):
        session_state = SessionState()
        owner = layers.LiveSessionUser("owner", "owner_id", "test")
        user1 = layers.LiveSessionUser("user1", "user1_id", "test")

        timeline_session = TimelineSession("", owner, session_state, TimelineSessionRoleType.PRESENTER)
        session_state.timeline_session = timeline_session

        self._window = UserWindow(session_state)
        self._window._window.title = "Timeline Session Test"
        # register ui building callback
        self._window.show()

        window_ref = ui_test.find("Timeline Session Test")
        session_state.add_users([owner, user1])
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")

        # workaround to request timeline control for UI tests
        timeline_session._is_running = True

        request_control_btn = window_ref.find('**/Button[*].text == "Request Timeline Control"')
        self.assertIsNotNone(request_control_btn)

        await request_control_btn.click()
        self.assertIsNotNone(
            window_ref.find(f'**/ScrollingFrame[1]/VStack[0]/Label[0].text == "{users[0].widget.text}"')
        )
        revoke_btn = window_ref.find('**/Button[*].text == "Revoke Request"')
        self.assertIsNotNone(revoke_btn)

        await revoke_btn.click()
        self.assertEqual(len(window_ref.find_all(f"**/ScrollingFrame[1]/VStack[0]/Label[*]")), 0)

        # click user
        await users[0].click()
        self.assertIsNone(window_ref.find('**/Button[*].text == "Set as Timeline Presenter"'))

        ## request control list user click
        request_ids = ["owner_id", "user1_id"]
        timeline_session._control_requests.extend(request_ids)
        ## force rebuild ui
        self._window.show()
        request_control_users = window_ref.find_all("**/ScrollingFrame[1]/VStack[0]/Label[*]")
        await request_control_users[0].click()
        self.assertIsNone(window_ref.find('**/Button[*].text == "Set as Timeline Presenter"'))

    async def test_btns(self):
        session_state = SessionState()
        owner = layers.LiveSessionUser("owner", "owner_id", "test")
        user1 = layers.LiveSessionUser("user1", "user1_id", "test")

        timeline_session = TimelineSession("", owner, session_state, TimelineSessionRoleType.PRESENTER)
        session_state.timeline_session = timeline_session

        self._window = UserWindow(session_state)
        self._window._window.title = "Timeline Session Test"
        # register ui building callback
        self._window.show()

        window_ref = ui_test.find("Timeline Session Test")
        session_state.add_users([owner, user1])
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")

        # non-owner buttons
        self.assertIsNone(window_ref.find('**/Button[*].text == "Set as Timeline Presenter"'))

        # set owner
        # workaround to set owner for UI tests
        timeline_session._is_running = True
        timeline_session.owner = owner

        ## force rebuild ui
        self._window.show()
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")

        owner = window_ref.find("**/ScrollingFrame[0]/VStack[0]/Label[0]")
        self.assertIsNotNone(owner)
        self.assertTrue(users[0].widget.text, "owner (test) [Owner][Current user]")

        presenter_btn = window_ref.find('**/Button[*].text == "Set as Timeline Presenter"')
        self.assertIsNotNone(presenter_btn)
        self.assertFalse(presenter_btn.widget.visible)
        self.assertIsNone(window_ref.find('**/Button[*].text == "Request Timeline Control"'))

        # click user as a onwer
        ## make myself as a presenter
        await users[0].click()
        self.assertTrue(presenter_btn.widget.visible)
        await presenter_btn.click()
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")

        owner = window_ref.find("**/ScrollingFrame[0]/VStack[0]/Label[0]")
        self.assertIsNotNone(owner)
        self.assertTrue(users[0].widget.text, "owner (test) [Owner][Presenter][Current user]")
        self.assertIsNone(window_ref.find('**/Label[*].text == "Allowed time difference from Presenter (sec): "'))
        presenter_btn = window_ref.find('**/Button[*].text == "Set as Timeline Presenter"')
        self.assertFalse(presenter_btn.widget.visible)
        await users[0].click()
        self.assertFalse(presenter_btn.widget.visible)

        ## make user1 as a presenter from control request list
        request_ids = ["owner_id", "user1_id"]
        timeline_session._control_requests = request_ids
        ## force rebuild ui
        self._window.show()
        await window_ref.find('**/ScrollingFrame[1]/**/Label[*].text == "user1 (test) "').click()
        presenter_btn = window_ref.find('**/Button[*].text == "Set as Timeline Presenter"')
        self.assertTrue(presenter_btn.widget.visible)

        # workaround for being a listener to test UI
        timeline_session._role_type = TimelineSessionRoleType.LISTENER

        await presenter_btn.click()
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")
        self.assertIsNotNone(
            window_ref.find('**/ScrollingFrame[0]/VStack[0]/Label[*].text == "user1 (test) [Presenter]"')
        )
        self.assertIsNone(window_ref.find('**/ScrollingFrame[1]/VStack[0]/Label[*].text == "user1 (test) "'))
        self.assertIsNone(window_ref.find('**/ScrollingFrame[1]/VStack[0]/Label[*].text == "user1 (test) [Presenter]"'))

        ## make myself as a presenter from control request list
        request_control_users = window_ref.find_all("**/ScrollingFrame[1]/VStack[0]/Label[*]")
        await request_control_users[0].click()
        self.assertTrue(presenter_btn.widget.visible)

        # workaround for being a presenter to test UI
        timeline_session._role_type = TimelineSessionRoleType.PRESENTER

        await presenter_btn.click()
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")
        self.assertIsNotNone(
            window_ref.find(
                '**/ScrollingFrame[0]/VStack[0]/Label[*].text == "owner (test) [Owner][Presenter][Current user]"'
            )
        )
        self.assertIsNone(
            window_ref.find('**/ScrollingFrame[1]/VStack[0]/Label[*].text == "owner (test) [Owner][Current user]"')
        )
        self.assertIsNone(
            window_ref.find(
                '**/ScrollingFrame[1]/VStack[0]/Label[*].text == "owner (test) [Owner][Presenter][Current user]"'
            )
        )

        ## make user1 as a presenter
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")
        await users[1].click()
        self.assertTrue(presenter_btn.widget.visible)

        ### workaround for not printing error log of timeline_session_role
        ### since we do not care the functionalities timeline_session_role in this test
        timeline_session._role_type = TimelineSessionRoleType.LISTENER

        await presenter_btn.click()
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")
        self.assertIsNotNone(
            window_ref.find('**/ScrollingFrame[0]/VStack[0]/Label[*].text == "user1 (test) [Presenter]"')
        )

    async def test_time_difference_slider(self):
        session_state = SessionState()
        owner = layers.LiveSessionUser("owner", "owner_id", "test")
        user1 = layers.LiveSessionUser("user1", "user1_id", "test")

        timeline_session = TimelineSession("", owner, session_state, TimelineSessionRoleType.LISTENER)
        session_state.timeline_session = timeline_session

        self._window = UserWindow(session_state)
        self._window._window.title = "Timeline Session Test"
        # register ui building callback
        self._window.show()

        window_ref = ui_test.find("Timeline Session Test")
        session_state.add_users([owner, user1])
        users = window_ref.find_all("**/ScrollingFrame[0]/VStack[0]/Label[*]")

        slider = window_ref.find('**/FloatSlider[*].name == "tsync_maxdiff_slider"')
        self.assertIsNotNone(slider)

        await slider.input("0")
        self.assertEqual(timeline_session.role.sync_strategy.strategy_desc.max_time_diff_sec, 0)

        await slider.input("1")
        self.assertEqual(timeline_session.role.sync_strategy.strategy_desc.max_time_diff_sec, 1.0)

        await slider.input("1.7")
        self.assertEqual(timeline_session.role.sync_strategy.strategy_desc.max_time_diff_sec, 1.7)

        await slider.input("2")
        self.assertEqual(timeline_session.role.sync_strategy.strategy_desc.max_time_diff_sec, 2.0)
