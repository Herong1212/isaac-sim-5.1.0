import os
import unittest
import carb
import omni.kit.test
from omni.kit.window.preferences.scripts.preferences_window import (
    PreferenceBuilder,
    PERSISTENT_SETTINGS_PREFIX,
)


class TestPreferencesWindow(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_new_preferences_window(self):
        called_init = False
        called_del = False

        class TestPreferences(PreferenceBuilder):
            def __init__(self):
                super().__init__("Test")

            def build(self):
                nonlocal called_init
                called_init = True

            def __del__(self):
                super().__del__()
                nonlocal called_del
                called_del = True

        self.assertFalse(called_init)
        self.assertFalse(called_del)
        called_init = False
        called_del = False

        page = omni.kit.window.preferences.register_page(TestPreferences())
        omni.kit.window.preferences.select_page(page)
        omni.kit.window.preferences.rebuild_pages()
        prefs = omni.kit.window.preferences.get_instance()

        self.assertTrue(called_init)
        self.assertFalse(called_del)
        called_init = False
        called_del = False

        omni.kit.window.preferences.unregister_page(page)
        del page

        self.assertFalse(called_init)
        self.assertTrue(called_del)
