## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import omni.kit.test
import re
from pathlib import Path

import omni.kit.app
import omni.kit.commands
import omni.kit.undo
from omni.kit.window.commands import Window
from omni.ui.tests.test_base import OmniUiTest

_result = []


class TestAppendCommand(omni.kit.commands.Command):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def do(self):
        global _result
        _result.append(self._x)
        _result.append(self._y)

    def undo(self):
        global _result
        del _result[-1]
        del _result[-1]


class TestCommandsWindow(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._golden_img_dir = Path(extension_path).joinpath("data").joinpath("tests").absolute()

        # make sure we are starting from a clean state
        omni.kit.undo.clear_stack()

        # Register all commands
        omni.kit.commands.register(TestAppendCommand)

    # After running each test
    async def tearDown(self):
        # Unregister all commands
        omni.kit.commands.unregister(TestAppendCommand)

        await super().tearDown()

    async def test_simple_command(self):
        window = await self.create_test_window(1000, 600)
        with window.frame:
            win = Window("Commands")
            win.show()

        global _result

        # Execute and undo
        _result = []
        omni.kit.commands.execute("TestAppend", x=1, y=2)
        self.assertListEqual(_result, [1, 2])
        omni.kit.undo.undo()
        self.assertListEqual(_result, [])

        script = """import omni.kit.commands
                    omni.kit.commands.execute('TestAppend',
                        x=1,
                        y=2)
                    omni.kit.commands.execute('Undo')"""

        result = win._generate_command_script(False)

        # strip all whitespaces to ease our comparison
        s = re.sub(r"[\s+]", "", script)
        r = re.sub(r"[\s+]", "", result)

        # test script
        self.assertEqual(s, r)

        for i in range(50):
            await omni.kit.app.get_app().next_update_async()

        # test image
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_simple_command.png", use_log=False
        )
