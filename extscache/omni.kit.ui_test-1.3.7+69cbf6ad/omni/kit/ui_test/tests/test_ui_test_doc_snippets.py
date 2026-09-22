## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import builtins
import omni.kit.app
from omni.kit.test.async_unittest import AsyncTestCase

import omni.ui as ui
import omni.kit.ui_test as ui_test


class TestUITestDocSnippet(AsyncTestCase):
    async def test_doc_snippet(self):
        clicks = 0

        def on_click(*_):
            nonlocal clicks
            clicks += 1

        printed_text = ""

        def print(*args, **kwargs):
            nonlocal printed_text
            printed_text += str(args[0]) + "\n"
            return builtins.print(*args, **kwargs)

        # begin-doc-1

        # Demo:
        import omni.kit.ui_test as ui_test
        import omni.ui as ui

        # Build some UI
        window = ui.Window("Nice Window")
        with window.frame:  # the frame can only have 1 widget under it
            with ui.HStack():
                ui.Label("Test1")
                with ui.VStack(width=150):
                    ui.Label("Test2")
                    ui.Button("TestButton", clicked_fn=on_click)

        # Let UI build
        await ui_test.wait_n_updates(2)

        # Find a button
        button = ui_test.find("Nice Window//Frame/**/Button[*]")

        # Real / Unique path:
        print(button.realpath)  # Nice Window//Frame/HStack[0]/VStack[0]/Button[0]

        # button is a reference, actual omni.ui.Widget can be accessed:
        print(type(button.widget))  # <class 'omni.ui._ui.Button'>

        # Click on button
        await button.click()

        # Find can be nested
        same_button = ui_test.find("Nice Window").find("**/Button[*]")

        # Find multiple:
        labels = ui_test.find_all("Nice Window//Frame/**/Label[*]")
        print(labels[0].widget.text)  # Test 1
        print(labels[1].widget.text)  # Test 2

        # end-doc-1

        # Verify snippet operations:
        self.assertEqual(
            printed_text,
            """Nice Window//Frame/HStack[0]/VStack[0]/Button[0]
<class 'omni.ui._ui.Button'>
Test1
Test2
""",
        )
        self.assertEqual(button.widget, same_button.widget)
        self.assertEqual(clicks, 1)
        self.assertEqual(len(labels), 2)
