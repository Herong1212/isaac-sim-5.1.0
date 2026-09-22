import os
import carb
import omni.usd
import omni.kit.ui_test as ui_test
import omni.ui as ui
import omni.kit.usd.layers as layers
import omni.timeline.live_session
import omni.kit.collaboration.presence_layer as pl
import omni.kit.collaboration.presence_layer.utils as pl_utils
import unittest
import tempfile
import random
import uuid

from functools import partial
from omni.kit.test import AsyncTestCase
from omni.kit.window.preferences import register_page, unregister_page
from pxr import Sdf, Usd, UsdUtils
from omni.kit.usd.layers.tests.mock_utils import MockLiveSyncingApi, join_new_simulated_user, quit_simulated_user, forbid_session_merge
from omni.kit.widget.live_session_management_ui.live_session_start_window import LiveSessionStartWindow
from ..extension import LiveSessionWidgetExtension, stop_or_show_live_session_widget
from ..live_session_camera_follower_list import LiveSessionCameraFollowerList
from ..live_session_user_list import LiveSessionUserList
from ..live_session_preferences import LiveSessionPreferences
from ..reload_widget import build_reload_widget
from .mock_utils import (
    MockApiForLiveSessionManagement,
    append_outdated_layers,
    clear_outdated_layers,
    get_merge_and_stop_live_session_async_called
)

TEST_URL = "omniverse://__omni.kit.widget.live_session_management__/tests/"
LIVE_SESSION_CONFIRM_BUTTON_PATH = "Live Session//Frame/**/Button[*].name=='confirm_button'"
LIVE_SESSION_CANCEL_BUTTON_PATH = "Live Session//Frame/**/Button[*].name=='cancel_button'"
LEAVE_SESSION_CONFIRM_BUTTON_PATH = "Leave Session//Frame/**/Button[*].name=='confirm_button'"
JOIN_LIVE_SESSION_WITH_LINK_CANCEL_BUTTON_PATH = "JOIN LIVE SESSION WITH LINK//Frame/**/Button[*].name=='cancel_button'"
SHARE_LIVE_SESSION_LINK_COMBO_BOX_PATH = "SHARE LIVE SESSION LINK//Frame/**/ComboBox[0]"
SHARE_LIVE_SESSION_LINK_CONFIRM_BUTTON_PATH = "SHARE LIVE SESSION LINK//Frame/**/InvisibleButton[*].name=='confirm_button'"
MERGE_OPTIONS_CONFIRM_BUTTON_PATH = "Merge Options//Frame/**/Button[*].name=='confirm_button'"
MERGE_OPTIONS_COMBO_BOX_PATH = "Merge Options//Frame/**/ComboBox[0]"
MERGE_PROMPT_LEAVE_BUTTON_PATH = "Permission Denied//Frame/**/Button[*].name=='confirm_button'"

QUICK_JOIN_ENABLED = "/exts/omni.kit.widget.live_session_management/quick_join_enabled"

def _menu_items_as_string_list(items):
    return [i.text for i in items]

def _find_menu_item(items, text):
    for i in items:
        if i.text == text:
            return i
    return None

def enable_server_tests():
    settings = carb.settings.get_settings()
    return True or settings.get_as_bool("/exts/omni.kit.widget.live_session_management/enable_server_tests")

class TestLiveSessionManagement(AsyncTestCase):
    def get_live_syncing(self):
        usd_context = omni.usd.get_context()
        self.assertIsNotNone(layers.get_layers(usd_context))
        self.assertIsNotNone(layers.get_layers(usd_context).get_live_syncing())
        return layers.get_layers(usd_context).get_live_syncing()

    async def setUp(self):
        self._instance = LiveSessionWidgetExtension.get_instance()
        self.assertIsNotNone(self._instance)
        self.assertFalse(self.get_live_syncing().is_stage_in_live_session())
        self.__attached_stage = None

    async def _close_case(self):
        usd_context = omni.usd.get_context()
        if usd_context.get_stage():
            live_syncing = self.get_live_syncing()
            if live_syncing:
                if live_syncing.is_stage_in_live_session():
                    await self._leave_current_session()
                live_syncing.stop_all_live_sessions()
            await usd_context.close_stage_async()

        stage, self.__attached_stage = self.__attached_stage, None
        if stage:
            UsdUtils.StageCache.Get().Erase(stage)

        await ui_test.human_delay(6)


    async def _click_menu_item(self, item, right_click=False):
        offset = ui_test.Vec2(5, 5)
        pos = ui_test.Vec2(item.screen_position_x, item.screen_position_y) + offset
        await ui_test.emulate_mouse_move(pos, 4)
        await ui_test.human_delay(6)
        await ui_test.emulate_mouse_click(right_click=right_click)
        await ui_test.human_delay(6)

    async def _create_test_usd(self, filename = 'test'):
        await omni.client.delete_async(TEST_URL)
        stage_url = TEST_URL + f"{filename}.usd"
        layer = Sdf.Layer.CreateNew(stage_url)
        stage = Usd.Stage.Open(layer.identifier)
        self.assertIsNotNone(stage)

        await omni.usd.get_context().attach_stage_async(stage)
        self.__attached_stage = stage
        return stage

    async def _create_test_sublayer_usd(self, filename = 'sublayer'):
        layer_url = TEST_URL + f"{filename}.usd"
        layer = Sdf.Layer.CreateNew(layer_url)
        return layer

    async def _expand_live_session_menu(self,
                                        layer_identifier: str=None,
                                        quick_join: str=None):
        stop_or_show_live_session_widget(layer_identifier=layer_identifier, quick_join=quick_join)
        await ui_test.human_delay(6)
        menu = self._instance._live_session_menu
        self.assertIsNotNone(menu)
        items = ui.Inspector.get_children(menu)
        await ui_test.human_delay(6)
        return items

    def _get_current_menu_item_string_list(self):
        menu = ui.Menu.get_current()
        self.assertIsNotNone(menu)
        items = ui.Inspector.get_children(menu)
        return _menu_items_as_string_list(items)

    async def _click_on_current_menu(self, text: str):
        menu = ui.Menu.get_current()
        self.assertIsNotNone(menu)
        items = ui.Inspector.get_children(menu)
        item_str_list = self._get_current_menu_item_string_list()
        self.assertIn(text, item_str_list)
        item = _find_menu_item(items, text)
        self.assertIsNotNone(item)
        await self._click_menu_item(item)
        await ui_test.human_delay(6)

    async def _click_live_session_menu_item(self,
                                            text: str, layer_identifier = None,
                                            quick_join: str = None):
        items = await self._expand_live_session_menu(layer_identifier, quick_join)
        self.assertTrue(len(items) > 0)

        item_str_list = _menu_items_as_string_list(items)
        self.assertIn(text, item_str_list)
        item = _find_menu_item(items, text)
        self.assertIsNotNone(item)
        await self._click_menu_item(item)
        await ui_test.human_delay(6)

    @MockLiveSyncingApi
    async def test_create_session_dialog(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._click_live_session_menu_item("Create Session")

        frame = ui_test.find("Live Session")
        self.assertIsNotNone(frame)
        cancal_button = ui_test.find(LIVE_SESSION_CANCEL_BUTTON_PATH)
        self.assertIsNotNone(cancal_button)
        await cancal_button.click()

        await self._close_case()

    async def _create_session(self, session_name: str=None):
        await self._click_live_session_menu_item("Create Session")

        frame = ui_test.find("Live Session")
        self.assertIsNotNone(frame)

        if session_name:
            name_field = ui_test.find("Live Session//Frame/**/StringField[0]")
            self.assertIsNotNone(name_field)
            name_field.model.set_value(session_name)

        ok_button = ui_test.find(LIVE_SESSION_CONFIRM_BUTTON_PATH)
        self.assertIsNotNone(ok_button)
        await ok_button.click()
        await ui_test.human_delay(6)

    async def _create_session_then_leave(self, session_name: str):
        self.assertFalse(self.get_live_syncing().is_stage_in_live_session())
        await self._create_session(session_name)
        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())
        await self._leave_current_session()
        self.assertFalse(self.get_live_syncing().is_stage_in_live_session())

    async def _leave_current_session(self):
        await self._click_live_session_menu_item("Leave Session")
        if ui_test.find("Leave Session"):
            button = ui_test.find(LEAVE_SESSION_CONFIRM_BUTTON_PATH)
            self.assertIsNotNone(button)
            await button.click()
            await ui_test.human_delay(6)

    @MockLiveSyncingApi
    async def test_create_session(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session("test")

        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())
        self.get_live_syncing().stop_all_live_sessions()
        self.assertFalse(self.get_live_syncing().is_stage_in_live_session())

        await self._close_case()

    @MockLiveSyncingApi
    async def test_leave_session(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_join_session(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session_then_leave("test")

        await self._click_live_session_menu_item("Join Session")

        frame = ui_test.find("Live Session")
        self.assertIsNotNone(frame)

        ok_button = ui_test.find(LIVE_SESSION_CONFIRM_BUTTON_PATH)
        self.assertIsNotNone(ok_button)
        await ok_button.click()
        await ui_test.human_delay(6)

        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())

        await self._close_case()

    def _on_join_session(self, layers_interface: layers.Layers, current_session,
                         layer_identifier: str, prim_path) -> bool:
        from ..utils import join_live_session, is_viewer_only_mode
        return join_live_session(
            layers_interface, layer_identifier, current_session, prim_path, is_viewer_only_mode()
        )

    def _create_live_session(self, layers_interface: layers.Layers, layer_identifier: str, name: str):
        live_syncing = layers_interface.get_live_syncing()
        return live_syncing.create_live_session(name, layer_identifier)

    @MockLiveSyncingApi
    @MockApiForLiveSessionManagement
    async def test_join_session_participants(self):
        from ..live_session_model import LiveSessionModel

        stage = await self._create_test_usd("test")
        await omni.usd.get_context().attach_stage_async(stage)

        layers_interface = layers.get_layers()
        session_model = LiveSessionModel(layers_interface, stage.GetRootLayer().identifier)
        live_session_start_window = LiveSessionStartWindow(session_model,
            None, partial(self._on_join_session, layers_interface),
            partial(self._create_live_session, layers_interface))

        await self._create_session("test")

        live_session_start_window.visible = True
        live_session_start_window.set_focus(True)
        await ui_test.human_delay(6)
        live_session_start_window.visible = False

        await self._close_case()

    @MockLiveSyncingApi
    async def test_join_session_quick(self):
        settings = carb.settings.get_settings()
        before = settings.get_as_bool(QUICK_JOIN_ENABLED)
        settings.set(QUICK_JOIN_ENABLED, True)
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session_then_leave("test")

        await self._expand_live_session_menu(quick_join="test")
        self.assertEqual("test", self.get_live_syncing().get_current_live_session().name)

        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())
        settings.set(QUICK_JOIN_ENABLED, before)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_join_session_quick_create(self):
        settings = carb.settings.get_settings()
        before = settings.get_as_bool(QUICK_JOIN_ENABLED)
        settings.set(QUICK_JOIN_ENABLED, True)
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._expand_live_session_menu(quick_join="test")
        self.assertEqual("test", self.get_live_syncing().get_current_live_session().name)

        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())
        settings.set(QUICK_JOIN_ENABLED, before)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_join_session_options(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session_then_leave(None)
        await self._create_session_then_leave(None)
        for i in range(3):
            await self._create_session_then_leave(f"test_{i}")

        await self._click_live_session_menu_item("Join Session")

        frame = ui_test.find("Live Session")
        self.assertIsNotNone(frame)

        combo_box = ui_test.find("Live Session//Frame/**/ComboBox[0]")
        items = combo_box.model.get_item_children(None)
        names = [i.session.name for i in items]

        carb.log_warn(names)
        self.assertIn("Default", names)
        self.assertIn("simulated_user_name___01", names)
        for i in range(3):
            self.assertIn(f"test_{i}", names)

        index_of_second_test_usd = names.index('test_1')
        self.assertTrue(index_of_second_test_usd > -1)
        combo_box.model.get_item_value_model(None, 0).set_value(index_of_second_test_usd)
        await ui_test.human_delay(6)

        ok_button = ui_test.find(LIVE_SESSION_CONFIRM_BUTTON_PATH)
        self.assertIsNotNone(ok_button)
        await ok_button.click()
        await ui_test.human_delay(6)

        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())
        self.assertEqual("test_1", self.get_live_syncing().get_current_live_session().name)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_menu_item_join_with_session_link_without_stage(self):
        self.assertIsNone(stop_or_show_live_session_widget())
        await self._close_case()

    @MockLiveSyncingApi
    async def test_menu_item_join_with_session_link_dialog(self):
        await omni.usd.get_context().new_stage_async()
        await self._click_live_session_menu_item("Join With Session Link")

        frame = ui_test.find("JOIN LIVE SESSION WITH LINK")
        self.assertIsNotNone(frame)
        cancal_button = ui_test.find(JOIN_LIVE_SESSION_WITH_LINK_CANCEL_BUTTON_PATH)
        self.assertIsNotNone(cancal_button)
        await cancal_button.click()

        await self._close_case()

    @MockLiveSyncingApi
    async def test_menu_item_copy_session_link(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session("test")

        layer = stage.GetRootLayer()
        await self._click_live_session_menu_item("Copy Session Link", layer.identifier)

        current_session = self.get_live_syncing().get_current_live_session()
        live_session_link = omni.kit.clipboard.paste()
        self.assertEqual(live_session_link, current_session.shared_link)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_menu_item_share_session_link(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        for i in range(3):
            await self._create_session_then_leave(f"test_{i}")

        await self._click_live_session_menu_item("Share Session Link")

        frame = ui_test.find("SHARE LIVE SESSION LINK")
        self.assertIsNotNone(frame)

        combo_box = ui_test.find(SHARE_LIVE_SESSION_LINK_COMBO_BOX_PATH)
        items = combo_box.model.get_item_children(None)
        names = [i.session.name for i in items]

        index_of_second_test_usd = -1
        for i in range(3):
            self.assertIn(f"test_{i}", names)
            if names[i] == "test_1":
                index_of_second_test_usd = i
        self.assertTrue(index_of_second_test_usd > -1)
        combo_box.model.get_item_value_model(None, 0).set_value(index_of_second_test_usd)
        await ui_test.human_delay(6)

        confirm_button = ui_test.find(SHARE_LIVE_SESSION_LINK_CONFIRM_BUTTON_PATH)
        await confirm_button.click()

        live_session_link = omni.kit.clipboard.paste()
        self.assertEqual(live_session_link, items[index_of_second_test_usd].session.shared_link)

        await self._close_case()

    def _create_test_camera(self, name: str='camera'):
        camera_path = f"/{name}"
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Camera", prim_path=camera_path)
        return Sdf.Path(camera_path)

    async def _setup_camera_follower_list(self, camera_path, maximum_users=3):
        camera = omni.usd.get_context().get_stage().GetPrimAtPath(camera_path)
        self.assertIsNotNone(camera)
        return LiveSessionCameraFollowerList(omni.usd.get_context(), camera_path, maximum_users=maximum_users)

    @MockLiveSyncingApi
    async def test_live_session_camera_follower_list(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        camera_path = self._create_test_camera()
        camera_follower_list = await self._setup_camera_follower_list(camera_path)

        await self._close_case()

    async def _bound_camera(self, shared_stage: Usd.Stage, user_id: str, camera_path: Sdf.Path):
        if not camera_path:
            camera_path = Sdf.Path.emptyPath

        camera_path = Sdf.Path(camera_path)
        bound_camera_property_path = pl_utils.get_bound_camera_property_path(user_id)
        property_spec = pl_utils.get_or_create_property_spec(
            shared_stage.GetRootLayer(), bound_camera_property_path,
            Sdf.ValueTypeNames.String
        )

        builtin_camera_name = pl_utils.is_local_builtin_camera(camera_path)
        if not builtin_camera_name:
            property_spec.default = str(camera_path)
        else:
            property_spec.default = builtin_camera_name

        if builtin_camera_name:
            persp_camera = pl_utils.get_user_shared_root_path(user_id).AppendChild(builtin_camera_name)
            camera_prim = shared_stage.DefinePrim(persp_camera, "Camera")

        await ui_test.human_delay(12)

    def _get_shared_stage(self, current_session: layers.LiveSession):
        shared_data_stage_url = current_session.url + "/shared_data/users.live"
        layer = Sdf.Layer.FindOrOpen(shared_data_stage_url)
        if not layer:
            layer = Sdf.Layer.CreateNew(shared_data_stage_url)

        return Usd.Stage.Open(layer)

    async def _follow_user(
        self, shared_stage: Usd.Stage, user_id: str, following_user_id: str
    ):
        following_user_property_path = pl_utils.get_following_user_property_path(user_id)
        property_spec = pl_utils.get_or_create_property_spec(
            shared_stage.GetRootLayer(), following_user_property_path,
            Sdf.ValueTypeNames.String
        )
        property_spec.default = following_user_id

        await ui_test.human_delay(6)

    def _create_shared_stage(self):
        current_session = self.get_live_syncing().get_current_live_session()
        self.assertIsNotNone(current_session)

        shared_stage = self._get_shared_stage(current_session)
        self.assertIsNotNone(shared_stage)
        return shared_stage

    def _create_users(self, count):
        return [f"user_{i}" for i in range(count)]

    @MockLiveSyncingApi
    async def test_live_session_camera_follower_list_user_join(self):
        stage = await self._create_test_usd("test_camera")
        usd_context = omni.usd.get_context()
        presence_layer = pl.get_presence_layer_interface(usd_context)
        await omni.usd.get_context().attach_stage_async(stage)
        await self._create_session("test_camera")

        stage_url = usd_context.get_stage_url()
        presence_layer = pl.get_presence_layer_interface(usd_context)
        shared_stage = self._create_shared_stage()

        camera_path = self._create_test_camera()
        camera_follower_list = await self._setup_camera_follower_list(camera_path)
        user_list = LiveSessionUserList(usd_context, stage_url)

        users = self._create_users(3)

        await self._bound_camera(shared_stage, users[0], camera_path)

        for user_id in users:
            join_new_simulated_user(user_id, user_id)
            await ui_test.human_delay(6)

        self.assertIsNotNone(presence_layer.get_bound_camera_prim(users[0]))
        user_0 = self._get_user_in_session(users[0])
        user_list._LiveSessionUserList__on_follow_user(
            0.0,
            0.0,
            int(carb.input.MouseInput.LEFT_BUTTON),
            None,
            user_0
        )
        await ui_test.human_delay(6)

        async def right_click_on(user):
            user_list._LiveSessionUserList__on_mouse_clicked(
                0.0,
                0.0,
                int(carb.input.MouseInput.RIGHT_BUTTON),
                None,
                user
            )
            await ui_test.human_delay(6)

        timeline_session = omni.timeline.live_session.get_timeline_session()

        self.assertFalse(timeline_session.is_presenter(user_0))
        await right_click_on(user_0)
        await self._click_on_current_menu("Set as Timeline Presenter")
        self.assertTrue(timeline_session.is_presenter(user_0))

        await right_click_on(user_0)
        await self._click_on_current_menu("Withdraw Timeline Presenter")
        self.assertFalse(timeline_session.is_presenter(user_0))

        self.assertEqual(users[0], presence_layer.get_following_user_id())
        await ui_test.human_delay(600)

        for user_id in users:
            quit_simulated_user(user_id)
            await ui_test.human_delay(6)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_live_session_camera_follower_list_bound_change(self):
        stage = await self._create_test_usd("test_camera")
        usd_context = omni.usd.get_context()
        presence_layer = pl.get_presence_layer_interface(usd_context)
        await omni.usd.get_context().attach_stage_async(stage)
        await self._create_session("test_camera")

        stage_url = usd_context.get_stage_url()
        presence_layer = pl.get_presence_layer_interface(usd_context)
        shared_stage = self._create_shared_stage()

        camera_path_1 = self._create_test_camera("camera1")
        camera_path_2 = self._create_test_camera("camera2")
        camera_follower_list = await self._setup_camera_follower_list(camera_path_1)
        user_list = LiveSessionUserList(usd_context, stage_url)

        users = self._create_users(2)
        for user_id in users:
            join_new_simulated_user(user_id, user_id)
            await ui_test.human_delay(6)

        await self._bound_camera(shared_stage, users[0], camera_path_1)
        await self._bound_camera(shared_stage, users[1], camera_path_2)
        await self._bound_camera(shared_stage, users[0], camera_path_2)
        await self._bound_camera(shared_stage, users[1], camera_path_1)

        for user_id in users:
            quit_simulated_user(user_id)
            await ui_test.human_delay(6)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_live_session_camera_follower_list_user_join_exceed_maximum(self):
        stage = await self._create_test_usd("test_camera")
        usd_context = omni.usd.get_context()
        presence_layer = pl.get_presence_layer_interface(usd_context)
        await omni.usd.get_context().attach_stage_async(stage)
        await self._create_session("test_camera")
        UI_MAXIMUM_USERS = 3

        stage_url = usd_context.get_stage_url()
        presence_layer = pl.get_presence_layer_interface(usd_context)
        shared_stage = self._create_shared_stage()

        camera_path = self._create_test_camera()
        camera_follower_list = await self._setup_camera_follower_list(camera_path, maximum_users=UI_MAXIMUM_USERS)
        user_list = LiveSessionUserList(usd_context, stage_url)

        users = self._create_users(UI_MAXIMUM_USERS + 1)

        for user in users:
            await self._bound_camera(shared_stage, user, camera_path)

        for user_id in users:
            join_new_simulated_user(user_id, user_id)
            await ui_test.human_delay(6)

        for user_id in users:
            quit_simulated_user(user_id)
            await ui_test.human_delay(6)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_end_and_merge(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session("test")

        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())

        await self._click_live_session_menu_item("End and Merge")

        frame = ui_test.find("Merge Options")
        self.assertIsNotNone(frame)

        combo = ui_test.find(MERGE_OPTIONS_COMBO_BOX_PATH)
        combo.model.get_item_value_model(None, 0).set_value(0)

        ok_button = ui_test.find(MERGE_OPTIONS_CONFIRM_BUTTON_PATH)
        self.assertIsNotNone(ok_button)
        await ok_button.click()
        await ui_test.human_delay(6)

        await self._close_case()

    @MockLiveSyncingApi
    @MockApiForLiveSessionManagement
    async def test_end_and_merge_save_file(self):
        self.assertFalse(get_merge_and_stop_live_session_async_called())
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session("test")

        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())

        await self._click_live_session_menu_item("End and Merge")

        frame = ui_test.find("Merge Options")
        self.assertIsNotNone(frame)

        combo = ui_test.find(MERGE_OPTIONS_COMBO_BOX_PATH)
        combo.model.get_item_value_model(None, 0).set_value(1)

        ok_button = ui_test.find(MERGE_OPTIONS_CONFIRM_BUTTON_PATH)
        self.assertIsNotNone(ok_button)
        await ok_button.click()
        await ui_test.human_delay(6)
        self.assertTrue(get_merge_and_stop_live_session_async_called())

        await self._close_case()

    @MockLiveSyncingApi
    async def test_end_and_merge_without_permission(self):
        stage = await self._create_test_usd()
        await omni.usd.get_context().attach_stage_async(stage)

        await self._create_session("test")

        current_session = self.get_live_syncing().get_current_live_session()
        forbid_session_merge(current_session)
        self.assertTrue(self.get_live_syncing().is_stage_in_live_session())

        await self._click_live_session_menu_item("End and Merge")

        frame = ui_test.find("Permission Denied")
        self.assertIsNotNone(frame)

        ok_button = ui_test.find(MERGE_PROMPT_LEAVE_BUTTON_PATH)
        self.assertIsNotNone(ok_button)
        await ok_button.click()
        await ui_test.human_delay(6)

        await self._close_case()

    @MockLiveSyncingApi
    async def test_reload_widget_on_layer(self):
        stage = await self._create_test_usd("test")
        usd_context = omni.usd.get_context()
        await usd_context.attach_stage_async(stage)
        await self._create_session("test")

        layer = stage.GetSessionLayer()
        window = omni.ui.Window(title='test_reload')
        with window.frame:
            reload_widget = build_reload_widget(layer.identifier, usd_context, True, True, False)
            self.assertIsNotNone(reload_widget)
            reload_widget.visible = True
            await ui_test.human_delay(10)
        window.width, window.height = 50, 50

        reload_button = ui_test.find("test_reload//Frame/**/InvisibleButton[0]")
        self.assertIsNotNone(reload_button)

        await reload_button.click(right_click=True)
        await ui_test.human_delay(6)

        item_str_list = self._get_current_menu_item_string_list()
        self.assertIn("Auto Reload", item_str_list)
        self.assertIn("Reload Layer", item_str_list)

        self.assertFalse(layers.get_layers_state(usd_context).is_auto_reload_layer(layer.identifier))
        await self._click_on_current_menu("Auto Reload")
        self.assertTrue(layers.get_layers_state(usd_context).is_auto_reload_layer(layer.identifier))

        await reload_button.click(right_click=True)
        await ui_test.human_delay(6)
        await self._click_on_current_menu("Auto Reload")
        self.assertFalse(layers.get_layers_state(usd_context).is_auto_reload_layer(layer.identifier))

        await reload_button.click()
        await ui_test.human_delay(6)

        await self._close_case()

    @MockLiveSyncingApi
    @MockApiForLiveSessionManagement
    async def test_reload_widget_on_outdated_layer(self):
        stage = await self._create_test_usd("test")
        usd_context = omni.usd.get_context()
        await usd_context.attach_stage_async(stage)
        await self._create_session("test")

        all_layers = []
        for i in range(3):
            layer = await self._create_test_sublayer_usd(f"layer_{i}")
            self.assertIsNotNone(layer)
            all_layers.append(layer)
            stage.GetRootLayer().subLayerPaths.append(layer.identifier)

        window = omni.ui.Window(title='test_reload')
        with window.frame:
            reload_widget = build_reload_widget(all_layers[0].identifier, usd_context, True, True, False)
            self.assertIsNotNone(reload_widget)
            reload_widget.visible = True
            await ui_test.human_delay(10)
        window.width, window.height = 50, 50

        reload_button = ui_test.find("test_reload//Frame/**/InvisibleButton[0]")
        self.assertIsNotNone(reload_button)

        layer = all_layers[0]
        custom_data = layer.customLayerData
        custom_data['test'] = random.randint(0, 10000000)
        layer.customLayerData = custom_data
        layer.Save(True)
        await ui_test.human_delay(6)

        append_outdated_layers(all_layers[0].identifier)

        await reload_button.click()
        await ui_test.human_delay(6)

        clear_outdated_layers()

        await self._close_case()

    async def test_live_session_preferences(self):
        preferences = register_page(LiveSessionPreferences())
        omni.kit.window.preferences.show_preferences_window()

        await ui_test.human_delay(6)
        label = ui_test.find("Preferences//Frame/**/ScrollingFrame[0]/TreeView[0]/Label[*].text=='Live'")
        await label.click()
        await ui_test.human_delay(6)
        self.assertIsNotNone(preferences._checkbox_quick_join_enabled)
        self.assertIsNotNone(preferences._combobox_session_list_select)
        await ui_test.human_delay(6)
        omni.kit.window.preferences.hide_preferences_window()
        unregister_page(preferences)

    def _get_user_in_session(self, user_id):
        current_session = self.get_live_syncing().get_current_live_session()
        session_channel = current_session._session_channel()
        return session_channel._peer_users.get(user_id, None)
