import carb
import omni.kit.test
import omni.usd
import omni.client
import unittest
import omni.kit.app

import carb
import omni.kit.test
import omni.usd
import omni.client
import unittest
import omni.kit.app
import omni.kit.widget.live_session_management as lsm

from .base import TestLayerUIBase
from omni.kit.usd.layers.tests.mock_utils import (
    MockLiveSyncingApi, join_new_simulated_user, quit_simulated_user,
    quit_all_simulated_users
)
from omni.kit.usd.layers import get_layers, get_layer_event_payload, LayerEventType, LayerUtils
from pxr import Usd, Sdf


class TestLiveSession(TestLayerUIBase):

    # Before running each test
    async def setUp(self):
        await super().setUp()
        layers = get_layers()
        self.live_syncing = layers.get_live_syncing()

    async def tearDown(self):
        await super().tearDown()

    async def wait(self, frames=10):
        for i in range(frames):
            await self.app.next_update_async()

    async def test_non_omniverse_stage(self):
        import omni.kit.ui_test as ui_test
        # For non-omniverse stage, it cannot start live session.
        await self.usd_context.new_stage_async()
        await ui_test.find("Layer").focus()
        await ui_test.human_delay(10)

        window = ui_test.find("Live Session")
        self.assertFalse(window)

    async def __create_fake_stage(self):
        format = Sdf.FileFormat.FindByExtension(".usd")
        # Sdf.Layer.New will not save layer so it won't fail.
        # This can be used to test layer identifier with omniverse sheme without
        # touching real server.
        layer = Sdf.Layer.New(format, "omniverse://__fake_omniverse_server__/test/test.usd")
        stage = self.usd_context.get_stage()
        stage.GetRootLayer().subLayerPaths.append(layer.identifier)

        return stage, layer

    @MockLiveSyncingApi
    async def test_session_management(self):
        _, layer = await self.__create_fake_stage()

        import omni.kit.ui_test as ui_test
        await ui_test.find("Layer").focus()
        await ui_test.human_delay(10)
        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        await ui_test.select_context_menu("Create Session")
        await ui_test.human_delay(10)
        window = ui_test.find("Live Session")
        self.assertTrue(window)

        create_session_button = ui_test.find("Live Session//Frame/**/RadioButton[*].name=='create_session_radio_button'")
        join_session_button = ui_test.find("Live Session//Frame/**/RadioButton[*].name=='join_session_radio_button'")
        self.assertTrue(create_session_button)
        self.assertTrue(join_session_button)

        session_name_field = ui_test.find("Live Session//Frame/**/StringField[*].name=='new_session_name_field'")
        self.assertTrue(session_name_field)

        confirm_button = ui_test.find("Live Session//Frame/**/Button[*].name=='confirm_button'")
        self.assertTrue(confirm_button)
        await self.wait()

        session_name_field.model.set_value("")
        # Empty session name is not valid
        await confirm_button.click()
        await ui_test.human_delay(10)

        # Invalid session name will fail to join
        await ui_test.human_delay(10)
        session_name_field.model.set_value("11111test_session")
        await confirm_button.click()
        await ui_test.human_delay(10)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())

        session_name_field.model.set_value("")
        await ui_test.human_delay(10)
        await session_name_field.input("test_session.,m,mn,m")
        await confirm_button.click()
        await ui_test.human_delay(10)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())

        # Valid session name
        session_name_field.model.set_value("")
        await ui_test.human_delay(10)
        await session_name_field.input("test_session")
        await confirm_button.click()
        await ui_test.human_delay(10)

        self.assertTrue(self.live_syncing.is_stage_in_live_session())
        current_live_session = self.live_syncing.get_current_live_session(layer.identifier)
        self.assertEqual(current_live_session.name, "test_session")

        layer_model = self.layers_instance.get_layer_model()
        self.assertTrue(layer_model.get_layer_item_by_identifier(current_live_session.root))

        join_new_simulated_user("user0", "user0", layer_identifier=layer.identifier)
        await self.wait(20)

        user_layout = ui_test.find("Layer//Frame/**/ZStack[*].identifier=='user0'")
        self.assertTrue(user_layout)

        # Creates another user
        join_new_simulated_user("user1", "user1", layer_identifier=layer.identifier)
        await self.wait(20)

        user_layout = ui_test.find("Layer//Frame/**/ZStack[*].identifier=='user1'")
        self.assertTrue(user_layout)

        # Quits user should remove its icon
        quit_simulated_user("user1", layer_identifier=layer.identifier)
        await self.wait(20)
        user_layout = ui_test.find("Layer//Frame/**/ZStack[*].identifier=='user1'")
        self.assertFalse(user_layout)

        # Joins another 10 users will show ellipsis since maximum count is 3.
        all_user_ids = []
        for i in range(10):
            index = i + 10
            user_id = f"user{index}"
            all_user_ids.append(user_id)
            join_new_simulated_user(user_id, user_id, layer_identifier=layer.identifier)
            await self.wait(20)

        user_layout = ui_test.find("Layer//Frame/**/Label[*].text=='...'")
        self.assertTrue(user_layout)

        # initialize mouse outside of list, so it doesn't accidentally hover on the wrong thing at the start
        await ui_test.emulate_mouse_move(ui_test.Vec2(0,0))
        await ui_test.emulate_mouse_move(user_layout.center)
        await self.wait(100)

        # Disable the check at this moment but only shows the dialog for coverage
        # and ensure there is are no scripting errors since ui_test cannot find
        # tooltip frame.
        # for user_id in all_user_ids:
        #    user_layout = ui_test.find(f"Layer//Frame/**/HStack[*].identifier=='{user_id}'")
        #    self.assertTrue(user_layout)

        quit_all_simulated_users(layer_identifier=layer.identifier)
        await self.wait()
        user_layout = ui_test.find("Layer//Frame/**/Label[*].text=='...'")
        self.assertFalse(user_layout)

        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Leave Session")
        await ui_test.human_delay(10)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())

        # Open session dialog again
        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Join Session")
        await ui_test.human_delay(10)
        window = ui_test.find("Live Session")
        self.assertTrue(window)

        create_session_button = ui_test.find("Live Session//Frame/**/RadioButton[*].name=='create_session_radio_button'")
        join_session_button = ui_test.find("Live Session//Frame/**/RadioButton[*].name=='join_session_radio_button'")
        self.assertTrue(create_session_button)
        self.assertTrue(join_session_button)

        # Click on join button will immediately join into the session.
        confirm_button = ui_test.find("Live Session//Frame/**/Button[*].name=='confirm_button'")
        self.assertTrue(confirm_button)
        await confirm_button.click()
        await ui_test.human_delay(10)
        self.assertTrue(self.live_syncing.is_stage_in_live_session())
        self.assertEqual(current_live_session.name, "test_session")

        # Quit session
        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        await ui_test.select_context_menu("Leave Session")
        await ui_test.human_delay(10)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())

        # Cancel button test
        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Join Session")
        cancel_button = ui_test.find("Live Session//Frame/**/Button[*].name=='cancel_button'")
        self.assertTrue(cancel_button)
        await cancel_button.click()
        self.assertFalse(self.live_syncing.is_stage_in_live_session())

        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Join Session")
        confirm_button = ui_test.find("Live Session//Frame/**/Button[*].name=='confirm_button'")
        self.assertTrue(confirm_button)
        await confirm_button.click()
        self.assertTrue(self.live_syncing.is_stage_in_live_session())

        # Test leave session menu
        await ui_test.human_delay(10)
        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        # Select leave session will notify you if you want to leave
        await ui_test.select_context_menu("Leave Session")
        await ui_test.human_delay(10)

        await confirm_button.click()
        self.assertFalse(self.live_syncing.is_stage_in_live_session())

        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Join Session")
        confirm_button = ui_test.find("Live Session//Frame/**/Button[*].name=='confirm_button'")
        self.assertTrue(confirm_button)
        await confirm_button.click()
        self.assertTrue(self.live_syncing.is_stage_in_live_session())

        carb.settings.get_settings().set(lsm.VIEWER_ONLY_MODE_SETTING, True)
        self.assertTrue(lsm.is_viewer_only_mode())
        await ui_test.human_delay(10)
        live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
        self.assertTrue(live_update_button)
        await live_update_button.right_click()
        # Select leave session will notify you if you want to leave
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("End and Merge")
        carb.settings.get_settings().set(lsm.VIEWER_ONLY_MODE_SETTING, False)
        self.assertFalse(lsm.is_viewer_only_mode())

        # Join session and make some changes to test end session dialog
        for confirm_or_cancel in [False, True]:
            await self.wait()
            live_update_button = ui_test.find("Layer//Frame/**/ToolButton[*].name=='live_update'")
            self.assertTrue(live_update_button)
            await live_update_button.right_click()
            # Select leave session will notify you if you want to leave
            await ui_test.select_context_menu("End and Merge")
            await self.wait()
            confirm_button = ui_test.find("Merge Options//Frame/**/Button[*].name=='confirm_button'")
            cancel_button = ui_test.find("Merge Options//Frame/**/Button[*].name=='cancel_button'")
            self.assertTrue(confirm_button)
            self.assertTrue(cancel_button)

            if confirm_or_cancel:
                await confirm_button.click()
                await self.wait()
                self.assertFalse(self.live_syncing.is_stage_in_live_session())
            else:
                await cancel_button.click()
                self.assertTrue(self.live_syncing.is_stage_in_live_session())

        self.live_syncing.stop_all_live_sessions()
        await self.wait()
