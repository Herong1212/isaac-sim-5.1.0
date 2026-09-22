import os
import shutil
import tempfile

import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.window.extensions

from .utils import open_window_and_sync

# pylint: disable=protected-access


def build_dir(path):
    os.makedirs(path, exist_ok=True)
    return path.replace("\\", "/")


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_extension(exts_dir: str, ext_id: str, deps: dict):
    ext_path = build_dir(f"{exts_dir}/{ext_id}")
    ext_config_dir = build_dir(f"{ext_path}/config")
    config_content = "[dependencies]\n"
    for dep, version in deps.items():
        config_content += f'"{dep}" = {{ version = "{version}" }}\n'
    write_file(f"{ext_config_dir}/extension.toml", config_content)
    return ext_path


async def toggle_extension(ext_id, enable):
    omni.kit.app.get_app().get_extension_manager().set_extension_enabled(ext_id, enable)
    await omni.kit.app.get_app().next_update_async()


class TestExtensionToggling(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._temp_folder = tempfile.mkdtemp()
        self._exts_dir = build_dir(f"{self._temp_folder}/exts")

        # build 2 sets of 2 extensions, one depends on the other
        build_extension(self._exts_dir, "aaa.blob-1.0.0", {})
        build_extension(self._exts_dir, "aaa.blob-1.2.3", {})
        build_extension(self._exts_dir, "aaa.bundle-1.0.0", {"aaa.blob": "=1.0.0"})
        build_extension(self._exts_dir, "aaa.bundle-1.2.3", {"aaa.blob": "=1.2.3"})

        # add this path to the extension manager
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.add_path(self._exts_dir)

        # open the window to force sync
        await open_window_and_sync(False)

        # check aaa. extensions are added to the extension manager
        ext_added = [
            ext["id"] for ext in manager.get_extensions() if "aaa.blob" in ext["name"] or "aaa.bundle" in ext["name"]
        ]
        self.assertEqual(ext_added, ["aaa.blob-1.0.0", "aaa.blob-1.2.3", "aaa.bundle-1.0.0", "aaa.bundle-1.2.3"])

    async def tearDown(self):
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate("omni.kit.window.extensions", True)

        # remove this path from the extension manager
        manager.remove_path(self._exts_dir)

        # reopen the window to force sync
        await open_window_and_sync(False)

        if manager.is_extension_enabled("omni.kit.window.extensions"):
            instance = omni.kit.window.extensions.get_instance()()
            instance.show_window(False)

        # remove the temp folder
        shutil.rmtree(self._temp_folder)

        # check aaa. extensions are removed from the extension manager
        ext_added = [
            ext["id"] for ext in manager.get_extensions() if "aaa.blob" in ext["name"] or "aaa.bundle" in ext["name"]
        ]
        self.assertEqual(ext_added, [])

    async def select_extension_by_name(self, ext_name):
        instance = omni.kit.window.extensions.get_instance()()
        ext_list_widget_model = instance._window._exts_list_widget._model
        ext_list_widget_model.filter_by_text([ext_name])
        await ui_test.human_delay(50)

        # click on ext_name
        for w in ui_test.find_all("Extensions//Frame/**/Label[*].identifier=='Title'"):
            await w.click()
            await ui_test.human_delay(10)
            break

    async def __wait_for_widget(self, root_widget, widget_id):
        count = 0
        while count < 50:
            if root_widget:
                item = root_widget.find(widget_id)
            else:
                item = ui_test.find(widget_id)
            await omni.kit.app.get_app().next_update_async()
            if item:
                return item
            count += 1
        return None

    async def test_update_button(self):
        manager = omni.kit.app.get_app().get_extension_manager()

        async def find_update_button(ext_name):
            await self.select_extension_by_name(ext_name)
            return await self.__wait_for_widget(None, "Extensions//Frame/**/Button[*].identifier=='update_button'")

        # enable lower level extension, update button is available
        await toggle_extension("aaa.blob-1.0.0", True)
        update_button = await find_update_button("aaa.blob")
        self.assertIsNotNone(update_button, "Update button not found")

        # click on it
        await update_button.click()
        await ui_test.human_delay(50)
        self.assertEqual(manager.get_enabled_extension_id("aaa.blob"), "aaa.blob-1.2.3")
        await toggle_extension("aaa.blob-1.2.3", False)

        # now enable bundle, update button is not available because "aaa.bundle" locked the version of "aaa.blob":
        await toggle_extension("aaa.bundle-1.0.0", True)
        update_button = await find_update_button("aaa.blob")
        self.assertIsNone(update_button, "Update button found")

        # disable all
        await toggle_extension("aaa.blob-1.0.0", False)
        await toggle_extension("aaa.bundle-1.0.0", False)

    async def test_toggle_with_one_click(self):
        manager = omni.kit.app.get_app().get_extension_manager()

        await toggle_extension("aaa.blob-1.0.0", True)

        await self.select_extension_by_name("aaa.blob")

        # find top_row HStack:
        ext_info_widget = await self.__wait_for_widget(
            None, "Extensions//Frame/**/VStack[*].identifier=='ext_info_widget'"
        )

        # 1.0.0 should be chosen by default because it is enabled (while 1.2.3 is latest):
        label = await self.__wait_for_widget(ext_info_widget, "**/Label[*].identifier=='ext_card_label'")
        self.assertIn("v1.0.0", label.widget.text)

        # find version selector to choose 1.2.3 now
        top_row = await self.__wait_for_widget(None, "Extensions//Frame/**/HStack[*].identifier=='top_row'")
        await top_row.find("**/Button[*].identifier=='version_selector'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("1.2.3", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay(10)

        # find toggle button and press. That should swtich from 1.0.0 to 1.2.3
        top_row = await self.__wait_for_widget(None, "Extensions//Frame/**/HStack[*].identifier=='top_row'")
        await top_row.find("**/ToolButton[*].identifier=='toggle_button'").click()

        await ui_test.human_delay(50)
        self.assertEqual(manager.get_enabled_extension_id("aaa.blob"), "aaa.blob-1.2.3")  # can fail

        # disable all
        await toggle_extension("aaa.blob-1.2.3", False)
