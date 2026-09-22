import omni.kit.test
import omni.kit.ui_test as ui_test
from omni.kit.window.usddebug import DebugFlagsExtension
from pxr import Tf


class Test(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        """
        Search UI tree for important refs
        """
        self.ext = DebugFlagsExtension()
        # Resize window to avoid scrollbar difference
        window = ui_test.find("Debug Flags").window
        window.height = 600
        scrollframes = ui_test.find_all("Debug Flags//Frame/*/ScrollingFrame[*]")
        self.prefix_stacks = scrollframes[0].find_all("*/VStack[0]/TreeView[0]/VStack[*]")
        self.flags_treeview = scrollframes[1].find("TreeView[0]")

    async def tearDown(self):
        pass

    async def test_all_prefixes(self):
        """
        Clicks all the prefixes in left menu and calls check helper
        """
        for stack in self.prefix_stacks:
            await ui_test.emulate_mouse_move_and_click(stack.center)
            await ui_test.human_delay(30)
            prefix = stack.find("Label[0]").widget.text
            await self.check_single_prefix(prefix)

    async def check_single_prefix(self, prefix):
        """
        Clicks all entries in table given a prefix,
        then calls helpers to check functionality
        """
        items = self.flags_treeview.find_all("*/*/HStack[0]")
        labels = [item.find("Label[0]") for item in items]
        checkboxes = [item.find("CheckBox[0]") for item in items]
        for i in range(len(labels)):
            flag = labels[i].widget.text.replace(" ", "_")
            cb = checkboxes[i]
            self.assertEqual(True, flag.startswith(prefix))

            # Try toggling the clickbox, stop if we cannot
            if not await self.check_widget_functionality(cb, flag):
                break
            await self.check_widget_functionality(cb, flag)

            # Check clicks for first two items
            if i < 2:
                await self.check_widget_click(cb, flag)
                await self.check_widget_click(cb, flag)

    async def check_widget_click(self, cb, flag):
        """
        Clicks checkbox to make sure it works
        Assumes the checkbox is visible
        """
        pre_val = cb.widget.model.get_value_as_bool()

        await ui_test.emulate_mouse_move_and_click(cb.center + ui_test.Vec2(5, 5))
        await ui_test.human_delay(10)

        self.assertEqual(pre_val, not cb.widget.model.get_value_as_bool())

    async def check_widget_functionality(self, cb, flag):
        """
        Clicks flag and checks app internal state change
        Returns: if the functionality was actually checked
        """
        pre_val = cb.widget.model.get_value_as_bool()
        pre_actual_val = Tf.Debug.IsDebugSymbolNameEnabled(flag)
        self.assertEqual(pre_val, pre_actual_val)

        await ui_test.emulate_mouse_move_and_click(cb.center + ui_test.Vec2(5, 5))
        await ui_test.human_delay(10)

        # Only check in this function if the clickbox was clickable
        post_val = cb.widget.model.get_value_as_bool()
        if pre_val != post_val:
            post_actual_val = Tf.Debug.IsDebugSymbolNameEnabled(flag)
            self.assertEqual(post_val, post_actual_val)
        else:
            return False
        return True
