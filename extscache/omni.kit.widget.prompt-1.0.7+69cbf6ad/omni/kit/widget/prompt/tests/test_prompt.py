import omni.kit.test

import omni.kit.ui_test as ui_test

from functools import partial
from omni.kit.widget.prompt import Prompt, PromptManager, PromptButtonInfo


class TestPrompt(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        PromptManager.on_shutdown()

    async def _wait(self, frames=5):
        for i in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_show_prompt_and_button_clicks(self):
        value = ""

        def f(text):
            nonlocal value
            value = text

        button_names = ["left", "right", "middle", "middle_2"]
        prompt = Prompt(
            "title", "information text", *button_names,
            ok_button_fn=partial(f, button_names[0]), cancel_button_fn=partial(f, button_names[1]),
            middle_button_fn=partial(f, button_names[2]), middle_2_button_fn=partial(f, button_names[3])
        )

        for button_name in button_names:
            prompt.show()
            self.assertTrue(prompt.visible)
            await ui_test.find("title").focus()
            label = ui_test.find("title//Frame/**/Label[*].text=='information text'")
            self.assertTrue(label)
            button = ui_test.find(f"title//Frame/**/Button[*].text=='{button_name}'")
            self.assertTrue(button)
            await button.click()
            self.assertEqual(value, button_name)
            self.assertFalse(prompt.visible)
            self.assertFalse(prompt.is_visible())
        prompt.destroy()

    async def test_set_buttons_fn(self):
        value = ""

        def f(text):
            nonlocal value
            value = text

        button_names = ["left", "right", "middle", "middle_2"]
        prompt = Prompt("title", "test", *button_names)
        prompt.set_confirm_fn(partial(f, button_names[0]))
        prompt.set_cancel_fn(partial(f, button_names[1]))
        prompt.set_middle_button_fn(partial(f, button_names[2]))
        prompt.set_middle_2_button_fn(partial(f, button_names[3]))
        prompt.set_on_closed_fn(partial(f, "closed"))
        for button_name in button_names:
            prompt.show()
            self.assertTrue(prompt.visible)
            await ui_test.find("title").focus()
            label = ui_test.find("title//Frame/**/Label[*].text=='test'")
            self.assertTrue(label)
            button = ui_test.find(f"title//Frame/**/Button[*].text=='{button_name}'")
            self.assertTrue(button)
            await button.click()
            self.assertEqual(value, button_name)
            self.assertFalse(prompt.visible)
            self.assertFalse(prompt.is_visible())
            prompt.show()
            prompt.hide()
            self.assertEqual(value, "closed")
        prompt.destroy()

    async def test_hide_prompt(self):
        value = ""

        def f(text):
            nonlocal value
            value = text

        prompt = Prompt("title", "hide dialog", on_closed_fn=partial(f, "closed"))
        prompt.show()
        self.assertTrue(prompt.visible)
        prompt.hide()
        self.assertEqual(value, "closed")
        self.assertFalse(prompt.visible)
        prompt.show()
        self.assertTrue(prompt.visible)
        prompt.visible = False
        self.assertFalse(prompt.visible)

    async def test_set_text(self):
        prompt = Prompt("test", "test")
        prompt.show()
        prompt.set_text("set text")
        await ui_test.find("test").focus()
        label = ui_test.find("test//Frame/**/Label[*].text=='set text'")
        self.assertTrue(label)

    async def test_prompt_manager(self):
        value = ""

        def f(text):
            nonlocal value
            value = text

        n = ["1left", "1right", "1middle", "1middle_2"]
        prompt = PromptManager.post_simple_prompt(
            "title", "test",
            ok_button_info=PromptButtonInfo(n[0], partial(f, n[0])),
            cancel_button_info=PromptButtonInfo(n[1], partial(f, n[1])),
            middle_button_info=PromptButtonInfo(n[2], partial(f, n[2])),
            middle_2_button_info=PromptButtonInfo(n[3], partial(f, n[3])),
            on_window_closed_fn=partial(f, "closed")
        )

        for button_name in n:
            prompt.show()
            self.assertTrue(prompt.visible)
            await ui_test.find("title").focus()
            label = ui_test.find("title//Frame/**/Label[*].text=='test'")
            self.assertTrue(label)
            button = ui_test.find(f"title//Frame/**/Button[*].text=='{button_name}'")
            self.assertTrue(button)
            await button.click()
            self.assertEqual(value, button_name)
            self.assertFalse(prompt.visible)
            self.assertFalse(prompt.is_visible())
            prompt.show()
            prompt.hide()
            self.assertEqual(value, "closed")
        prompt.destroy()
