import os
import tempfile

import omni.kit.app
import omni.kit.test
import omni.kit.window.extensions

from .utils import open_window_and_sync

# pylint: disable=protected-access


class TestPaths(omni.kit.test.AsyncTestCase):
    async def tearDown(self):
        instance = omni.kit.window.extensions.get_instance()()
        instance.show_window(False)

    async def test_add_remove_user_path(self):
        manager = omni.kit.app.get_app().get_extension_manager()

        def get_paths():
            return {p["path"] for p in manager.get_folders()}

        async def wait():
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        def get_model():
            omni.kit.window.extensions.get_instance()()
            return instance._window._exts_properties._paths_widget._model

        await open_window_and_sync(True)
        instance = omni.kit.window.extensions.get_instance()()
        instance._window._show_properties()
        await wait()

        paths_before = get_paths()

        with tempfile.TemporaryDirectory() as tmp_dir:
            p0 = f"{tmp_dir}/0"
            p1 = f"{tmp_dir}/1"

            # Add new path using model
            get_model().add_empty()
            last = get_model()._children[-1]
            last.path_model.as_string = p0
            get_model().save()

            # Ext manager creates it automatically
            self.assertTrue(os.path.exists(p0))
            self.assertEqual(len(get_paths()) - len(paths_before), 1)

            # Add new path using model
            get_model().add_empty()
            last = get_model()._children[-1]
            last.path_model.as_string = p1
            get_model().save()
            await wait()

            # Ext manager creates it automatically
            self.assertTrue(os.path.exists(p1))
            self.assertEqual(len(get_paths()) - len(paths_before), 2)

            # Remove!
            get_model().remove_item(get_model()._children[-1])
            await wait()
            self.assertEqual(len(get_paths()) - len(paths_before), 1)

            # Remove!
            get_model().remove_item(get_model()._children[-1])
            await wait()
            self.assertEqual(get_paths(), paths_before)
