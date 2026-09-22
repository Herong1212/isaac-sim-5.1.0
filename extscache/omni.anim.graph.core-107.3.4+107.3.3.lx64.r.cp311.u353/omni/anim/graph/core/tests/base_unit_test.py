import carb
import omni.kit
import omni.kit.commands
import omni.kit.undo
import omni.timeline
import omni.usd
from omni.kit.test_suite.helpers import wait_stage_loading
from pathlib import Path
import os


class BaseUnitTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._context = omni.usd.get_context()
        self._selection = self._context.get_selection()
        self._ext_dir = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
        self._golden_data_dir = self._ext_dir.joinpath("data/tests/golden")
        self._usd_data_dir = self._ext_dir.joinpath("data/tests/usd")
        self._xml_data_dir = self._ext_dir.joinpath("data/tests/xml")
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()
        self._timeline.set_current_time(0.0)
        self._timeline.set_auto_update(False)
        self._timeline.set_fast_mode(True)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        self._golden_data_dir = None
        self._usd_data_dir = None
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await self._context.new_stage_async()

    @property
    def ext_dir(self):
        return self._ext_dir

    @property
    def golden_data_dir(self):
        return self._golden_data_dir

    @property
    def usd_data_dir(self):
        return self._usd_data_dir

    async def load_stage(self, base_url, stage_name):
        stage_name = os.path.join(base_url, stage_name)
        result = None
        (result, err) = await self._context.open_stage_async(stage_name, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
        await wait_stage_loading()
        self.assertTrue(result)
        return result

    async def play(self):
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

    async def step_frames(self, n):
        for i in range(n):
            self._timeline.forward_one_frame()
            self._timeline.get_current_time()
            await omni.kit.app.get_app().next_update_async()

    async def stop(self):
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()

    def assertFloat3Equals(self, a: carb.Float3, b: carb.Float3):
        self.assertTrue(a.x == b.x and a.y == b.y and a.z == b.z)

    def assertFloat4Equals(self, a: carb.Float4, b: carb.Float4):
        self.assertTrue(a.x == b.x and a.y == b.y and a.z == b.z and a.w == b.w)
