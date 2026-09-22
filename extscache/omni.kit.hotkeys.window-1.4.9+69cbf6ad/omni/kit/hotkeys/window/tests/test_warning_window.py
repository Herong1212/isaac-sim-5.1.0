from pathlib import Path
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.kit.test
import omni.ui as ui

from ..window.warning_window import WarningWindow, WarningMessage

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")


class TestWarningWindow(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self.__window = None

        # Hide hotkeys window
        window = ui.Workspace.get_window("Hotkeys")
        window.visible = False
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        self.__window.visible = False
        self.__window = None
        await super().tearDown()

    async def test_simple(self):
        self.__window = WarningWindow("Test", messages=["This is a simple test menssage."])
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(window=self.__window, width=self.__window.width + 10, height=100, block_devices=False)

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="warning_simple.png")

    async def test_advanced(self):
        self.__window = WarningWindow(
            "Test",
            messages=[
                WarningMessage("'CTRL + O (On Press_'", highlight=True),
                WarningMessage(" is already assigned to "),
                WarningMessage("'Open'", highlight=True),
                "\n",
                "Do you want to replace this existing hotkey with your new one?"
            ],
            buttons=[
                ("Replace", lambda: print("Replace")),
                ("Cancel", lambda: print("Cancel"))
            ]
        )
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(window=self.__window, width=self.__window.width + 10, height=160, block_devices=False)

        # Because it takes time to load the icon in the warning window
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="warning_advanced.png")
