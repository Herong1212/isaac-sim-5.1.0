import omni.kit.test
from pathlib import Path
import omni.usd
import omni.client
import omni.kit.app
import omni.kit.usd.layers as layers
import omni.kit.clipboard
from omni.ui.tests.test_base import OmniUiTest

from pxr import Sdf, Usd, UsdUtils

from omni.kit.usd.layers.tests.mock_utils import MockLiveSyncingApi, join_new_simulated_user, quit_simulated_user

CURRENT_PATH = Path(__file__).parent.joinpath("../../../../../data")

class TestLiveWidget(OmniUiTest):

    # Before running each test
    async def setUp(self):
        self.__external_stage = None
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.app = omni.kit.app.get_app()
        self.usd_context = omni.usd.get_context()
        self.layers = layers.get_layers(self.usd_context)
        self.live_syncing = self.layers.get_live_syncing()
        await omni.usd.get_context().new_stage_async()

        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")
        self.simulated_user_names = []
        self.simulated_user_ids = []
        self.test_session_name = "test"
        self.stage_url = "omniverse://__faked_omniverse_server__/test/live_session.usd"

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)
        external_stage, self.__external_stage = self.__external_stage, None
        if external_stage:
            UsdUtils.StageCache.Get().Erase(external_stage)

    async def wait(self, frames=10):
        for i in range(frames):
            await self.app.next_update_async()

    async def __create_simulated_users(self, count=2):
        for i in range(count):
            user_name = f"test{i}"
            user_id = user_name
            self.simulated_user_names.append(user_name)
            self.simulated_user_ids.append(user_id)

            join_new_simulated_user(user_name, user_id)
            await self.wait(2)

    async def test_menu_setup(self):
        import omni.kit.ui_test as ui_test
        await self.usd_context.new_stage_async()
        menu_widget = ui_test.get_menubar()
        menu = menu_widget.find_menu("Live State Widget")
        self.assertTrue(menu)

    async def __create_fake_stage(self, join_test_session=True):
        format = Sdf.FileFormat.FindByExtension(".usd")
        # Sdf.Layer.New will not save layer so it won't fail.
        # This can be used to test layer identifier with omniverse sheme without
        # touching real server.
        layer = Sdf.Layer.New(format, self.stage_url)
        stage = Usd.Stage.Open(layer.identifier)
        session = self.live_syncing.create_live_session(self.test_session_name, layer_identifier=layer.identifier)
        self.assertTrue(session)

        if join_test_session:
            await self.usd_context.attach_stage_async(stage)
            self.__external_stage = stage
            self.live_syncing.join_live_session(session)

        return stage, layer

    @MockLiveSyncingApi
    async def test_open_stage_with_live_session(self):
        import omni.kit.ui_test as ui_test
        await self.usd_context.new_stage_async()
        _, layer = await self.__create_fake_stage(False)

        menu_widget = ui_test.get_menubar()
        menu = menu_widget.find_menu("Live State Widget")
        self.assertTrue(menu)
        await menu.bring_to_front()
        await menu.click(menu.center + ui_test.Vec2(50, 0), False, 10)
        # hard code the position of click point, as the menu positon changes after running test_join_live_session_users
        # don't know why the menu positon changes after running test_join_live_session_users
        # await menu.click(ui_test.Vec2(1426, 5), False, 10)

        await ui_test.human_delay(100)

        await ui_test.select_context_menu("Join With Session Link")

        stage_url_with_session = f"{layer.identifier}?live_session_name=test"
        omni.kit.clipboard.copy(stage_url_with_session)

        window = ui_test.find("JOIN LIVE SESSION WITH LINK")
        self.assertTrue(window is not None)

        input_field = window.find("**/StringField[*].name=='new_session_link_field'")
        self.assertTrue(input_field)

        confirm_button = window.find("**/Button[*].name=='confirm_button'")
        self.assertTrue(confirm_button)

        cancel_button = window.find("**/Button[*].name=='cancel_button'")
        self.assertTrue(cancel_button)

        # Invalid session name will fail to join
        await ui_test.human_delay(100)
        input_field.model.set_value("111111")
        await confirm_button.click()
        await ui_test.human_delay(100)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())
        self.assertTrue(window.window.visible)

        input_field.model.set_value("")
        await confirm_button.click()
        await ui_test.human_delay(100)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())
        self.assertTrue(window.window.visible)

        await cancel_button.click()
        self.assertFalse(self.live_syncing.is_stage_in_live_session())
        self.assertFalse(window.window.visible)

        window.window.visible = True
        await self.wait()

        # Valid session link
        paste_button = window.find("**/ToolButton[*].name=='paste_button'")
        self.assertTrue(paste_button)
        await paste_button.click()

        self.assertEqual(input_field.model.get_value_as_string(), stage_url_with_session)
        await confirm_button.click()
        self.assertFalse(window.window.visible)

        await ui_test.human_delay(300)
        self.assertTrue(self.live_syncing.is_stage_in_live_session())

        await menu.click(menu.center + ui_test.Vec2(70, 0), False, 10)
        await ui_test.human_delay(100)

        # Copy session link
        omni.kit.clipboard.copy("unkonwn")
        await ui_test.select_context_menu("Share Session Link")

        window = ui_test.find("SHARE LIVE SESSION LINK")
        self.assertTrue(window is not None)

        confirm_button = window.find("**/InvisibleButton[*].name=='confirm_button'")
        self.assertTrue(confirm_button)

        await confirm_button.click()

        stage_url_with_session = f"{layer.identifier}?live_session_name=test"
        live_session_link = omni.kit.clipboard.paste()
        self.assertTrue(live_session_link, stage_url_with_session)
        self.assertFalse(window.window.visible)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    @MockLiveSyncingApi(user_name="test", user_id="test")
    async def test_join_live_session_users(self):
        await self.__create_fake_stage(join_test_session=True)
        await self.wait()
        await self.__create_simulated_users()

        await self.wait()

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            hide_menu_bar = False,
            threshold=1e-4
        )
        self.live_syncing.stop_all_live_sessions()
        await self.wait()

    @MockLiveSyncingApi(user_name="test", user_id="test")
    async def test_leave_live_session_users(self):
        await self.__create_fake_stage(join_test_session=True)
        await self.wait()

        await self.__create_simulated_users()
        await self.wait()

        quit_simulated_user(self.simulated_user_ids[0])
        await self.wait()

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            hide_menu_bar=False,
            threshold=1e-4
        )
        self.live_syncing.stop_all_live_sessions()
        await self.wait()

    @MockLiveSyncingApi(user_name="test", user_id="test")
    async def test_join_live_session_over_max_users(self):
        await self.__create_fake_stage(join_test_session=True)
        await self.wait()

        await self.__create_simulated_users(26)
        await self.wait()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, hide_menu_bar=False)
        self.live_syncing.stop_all_live_sessions()
        await self.wait()
