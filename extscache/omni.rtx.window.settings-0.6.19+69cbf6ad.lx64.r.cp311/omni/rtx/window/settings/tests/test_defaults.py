import omni.kit.test
import carb.settings
import omni.kit.commands
from omni.rtx.window.settings.rendersettingsdefaults import RenderSettingsDefaults
from omni.rtx.window.settings import commands
from omni.kit.test_suite.helpers import wait_for_viewport_ready, arrange_windows


class TestDefaults(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        from omni.kit.test_suite.helpers import wait_stage_loading

        super().setUp()
        await omni.usd.get_context().new_stage_async()
        await wait_for_viewport_ready()
        await wait_stage_loading()

        settings = carb.settings.get_settings()

        # Am not sure what sets the default normally..
        settings.set("/rtx-defaults/pathtracing/maxBounces", 4)

    async def test_rtx_setting(self):
        """
        Test single item /rtx/pathtracing/maxBounces
        """
        settings = carb.settings.get_settings()
        blah = RenderSettingsDefaults()
        blah.reset_setting_to_default("/rtx/pathtracing/maxBounces")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)
        settings.set("/rtx/pathtracing/maxBounces", 12)
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 12)
        blah.reset_setting_to_default("/rtx/pathtracing/maxBounces")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)

    async def test_rtx_setting_section(self):
        """
        Test section /rtx/pathtracing
        """
        settings = carb.settings.get_settings()
        blah = RenderSettingsDefaults()
        blah.reset_setting_to_default("/rtx/pathtracing")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)
        settings.set("/rtx/pathtracing/maxBounces", 12)
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 12)
        blah.reset_setting_to_default("/rtx/pathtracing")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)

    async def test_rtx_settings_all(self):
        """
        Test entire section /rtx
        """
        settings = carb.settings.get_settings()
        blah = RenderSettingsDefaults()
        blah.reset_setting_to_default("/rtx")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)
        settings.set("/rtx/pathtracing/maxBounces", 12)
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 12)
        blah.reset_setting_to_default("/rtx")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)

    async def test_commands(self):
        settings = carb.settings.get_settings()
        settings.set("/rtx/pathtracing/maxBounces", 15)
        omni.kit.commands.execute("RestoreDefaultRenderSetting", path="/rtx/pathtracing/maxBounces")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)

        settings.set("/rtx/pathtracing/maxBounces", 16)
        omni.kit.commands.execute("RestoreDefaultRenderSettingSection", path="/rtx/pathtracing/maxBounces")
        currVal = settings.get("/rtx/pathtracing/maxBounces")
        self.assertEqual(currVal, 4)
