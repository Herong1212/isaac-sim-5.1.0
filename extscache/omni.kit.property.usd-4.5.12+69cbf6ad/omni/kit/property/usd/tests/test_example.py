# pylint: disable=missing-function-docstring, missing-class-docstring
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.ui.tests.test_base import OmniUiTest


class TestExample(OmniUiTest):
    # Before running each test
    async def setUp(self):
        import omni.kit.window.property as p
        from omni.kit.property.usd import Examples

        await arrange_windows("Stage", 200)
        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))
        await wait_stage_loading()

        w = p.get_window()
        if w:
            self.__example = Examples(w)

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()
        del self.__example

    async def test_example(self):
        # coverage only...
        await select_prims(["/Xform/Cone"])
        await ui_test.human_delay(10)
