# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from omni.kit.hotkeys.core import KeyCombination
import carb.input


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestKeyCombination(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    # Actual test, notice it is "async" function, so "await" can be used if needed
    async def test_key_define_function(self):
        key_comb = KeyCombination(carb.input.KeyboardInput.D)
        self.assertEqual(key_comb.as_string, "D")
        self.assertEqual(key_comb.trigger_press, True)

        key_comb = KeyCombination(carb.input.KeyboardInput.D, trigger_press=False)
        self.assertEqual(key_comb.as_string, "D")
        self.assertEqual(key_comb.trigger_press, False)

        key_comb = KeyCombination(carb.input.KeyboardInput.D, modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        self.assertEqual(key_comb.as_string, "CTRL + D")

        key_comb = KeyCombination(carb.input.KeyboardInput.D, modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT)
        self.assertEqual(key_comb.as_string, "SHIFT + D")

        key_comb = KeyCombination(carb.input.KeyboardInput.D, modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_ALT)
        self.assertEqual(key_comb.as_string, "ALT + D")

        key_comb = KeyCombination(carb.input.KeyboardInput.A, modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL + carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT)
        self.assertEqual(key_comb.as_string, "SHIFT + CTRL + A")

        key_comb = KeyCombination(carb.input.KeyboardInput.A, modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL + carb.input.KEYBOARD_MODIFIER_FLAG_ALT)
        self.assertEqual(key_comb.as_string, "CTRL + ALT + A")

        key_comb = KeyCombination(carb.input.KeyboardInput.A, modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_ALT + carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT)
        self.assertEqual(key_comb.as_string, "SHIFT + ALT + A")

        key_comb = KeyCombination(carb.input.KeyboardInput.B, modifiers=carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL + carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT + carb.input.KEYBOARD_MODIFIER_FLAG_ALT)
        self.assertEqual(key_comb.as_string, "SHIFT + CTRL + ALT + B")

    async def test_key_string_function(self):
        key_comb = KeyCombination("d")
        self.assertEqual(key_comb.as_string, "D")
        key_comb = KeyCombination("D")
        self.assertEqual(key_comb.as_string, "D")
        self.assertTrue(key_comb.trigger_press)
        key_comb = KeyCombination("D", trigger_press=False)
        self.assertEqual(key_comb.as_string, "D")
        self.assertFalse(key_comb.trigger_press)

        key_comb = KeyCombination("ctrl+d")
        self.assertEqual(key_comb.as_string, "CTRL + D")
        key_comb = KeyCombination("ctl+d")
        self.assertEqual(key_comb.as_string, "CTRL + D")
        key_comb = KeyCombination("control+d")
        self.assertEqual(key_comb.as_string, "CTRL + D")

        key_comb = KeyCombination("shift+d")
        self.assertEqual(key_comb.as_string, "SHIFT + D")

        key_comb = KeyCombination("alt+d")
        self.assertEqual(key_comb.as_string, "ALT + D")

        key_comb = KeyCombination("ctrl+shift+a")
        self.assertEqual(key_comb.as_string, "SHIFT + CTRL + A")
        key_comb = KeyCombination("shift+ctrl+A")
        self.assertEqual(key_comb.as_string, "SHIFT + CTRL + A")

        key_comb = KeyCombination("ctrl+ALT+a")
        self.assertEqual(key_comb.as_string, "CTRL + ALT + A")
        key_comb = KeyCombination("alt+CTRL+a")
        self.assertEqual(key_comb.as_string, "CTRL + ALT + A")

        key_comb = KeyCombination("ALT+shift+a")
        self.assertEqual(key_comb.as_string, "SHIFT + ALT + A")
        key_comb = KeyCombination("SHIFT+alt+a")
        self.assertEqual(key_comb.as_string, "SHIFT + ALT + A")

        key_comb = KeyCombination("Ctrl+shift+alt+b")
        self.assertEqual(key_comb.as_string, "SHIFT + CTRL + ALT + B")
        key_comb = KeyCombination("Ctrl+alt+shift+b")
        self.assertEqual(key_comb.as_string, "SHIFT + CTRL + ALT + B")
