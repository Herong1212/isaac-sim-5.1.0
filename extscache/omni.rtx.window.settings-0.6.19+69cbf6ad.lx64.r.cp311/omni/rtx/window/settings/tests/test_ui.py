import random
import omni.kit.test
import carb.settings
import omni.kit.commands
from omni.rtx.window.settings import RendererSettingsFactory
from omni.kit.test_suite.helpers import wait_for_viewport_ready, arrange_windows


class SettingsIterator(object):
    def __init__(self, output_dict):
        self._settings = carb.settings.get_settings()
        self._output_dict = output_dict

    def iterate(self, settings_dict, path_string=""):
        """
        iterate rtx settings and get a flat dictionary back we can work with
        """
        for k, v in settings_dict.items():
            key_string = path_string + "/" + str(k)
            if isinstance(v, dict):
                self.iterate(v, path_string=path_string + "/" + k)
            else:
                val = self._settings.get(key_string)
                self._output_dict[key_string] = val


class TestSetRenderSettings:
    @classmethod
    def generate_change_setting_command(cls, setting_path, current_value):
        if isinstance(current_value, bool):
            bool_choice = random.choice([True, False])
            omni.kit.commands.execute("ChangeSetting", path=setting_path, value=bool_choice)
        elif isinstance(current_value, float):
            float_choice = 0.0
            if abs(current_value) < 0.1:
                float_choice = random.uniform(0, 100)
            else:
                # TODO: We can make a better guess if we have more info about the range
                float_choice = random.uniform(current_value / 2, current_value * 2)
            omni.kit.commands.execute("ChangeSetting", path=setting_path, value=float_choice)
        elif isinstance(current_value, int):
            int_choice = 0
            if current_value == 0:
                int_choice = random.choice(range(0, 100))
            else:
                int_range = range(int(current_value / 2), int(current_value * 2))
                if len(int_range) > 1:
                    int_choice = random.choice(range(int(current_value / 2), int(current_value * 2)))
            omni.kit.commands.execute("ChangeSetting", path=setting_path, value=int_choice)
        elif isinstance(current_value, list):
            # TODO: add
            pass
        elif isinstance(current_value, str):
            # TODO: Without a bit more info (e.g from the "add_setting" calls in the UI)
            # it's hard to know what to do with strings - they could be filepaths/assets,
            # combo box elements etc. We should probably look at extracting that data
            pass
        else:
            print("this type is not supported")

    async def run_test_render_settings_ui(self, settings_path: str):
        """
        we're really not attempting to assert anything here, just
        cycle through a bunch of commands and hope it doesn't segfault
        """

        settings = carb.settings.get_settings()

        # if the renderers have initialised properly, this should have items
        settings_dict = settings.get_settings_dictionary(settings_path)
        output_dict = {}
        settingsIt = SettingsIterator(output_dict)
        settingsIt.iterate(settings_dict.get_dict(), settings_path)
        setting_list = list(output_dict)

        # TODO: add in ResetAllSettings and other commands

        # Set some settings, switch renderer, set stack, and do the same again several times
        for x in range(0, 20):
            for y in range(0, 10):
                key = random.choice(setting_list)
                self.generate_change_setting_command(key, output_dict[key])
                await omni.kit.app.get_app().next_update_async()

            renderers = RendererSettingsFactory.get_registered_renderers()
            if renderers:
                renderer_choice = random.choice(RendererSettingsFactory.get_registered_renderers())
                omni.kit.commands.execute("SetCurrentRenderer", renderer_name=renderer_choice)
                await omni.kit.app.get_app().next_update_async()

                for y in range(0, 10):
                    key = random.choice(setting_list)
                    self.generate_change_setting_command(key, output_dict[key])
                    await omni.kit.app.get_app().next_update_async()

                stacks = RendererSettingsFactory.get_renderer_stacks(renderer_choice)
                if stacks:
                    stack_choice = random.choice(stacks)
                    omni.kit.commands.execute("SetCurrentStack", stack_name=stack_choice)
                    await omni.kit.app.get_app().next_update_async()

        # If we have get a crash, we should be able to replay it outside the unit testing framework
        # with commands...
        history = omni.kit.undo.get_history().values()
        for cmd in history:
            continue
            # print (cmd)


class TestRTXCommandsDefaults(TestSetRenderSettings, omni.kit.test.AsyncTestCase):
    async def setUp(self):
        from omni.kit.test_suite.helpers import wait_stage_loading

        super().setUp()
        await omni.usd.get_context().new_stage_async()
        await wait_for_viewport_ready()
        await wait_stage_loading()

    async def test_rtx_settings_ui(self):
        return await self.run_test_render_settings_ui("/rtx")
