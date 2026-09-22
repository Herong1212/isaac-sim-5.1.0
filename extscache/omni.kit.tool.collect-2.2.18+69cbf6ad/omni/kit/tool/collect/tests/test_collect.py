import os
import carb
import omni.kit.test
import omni.usd
import omni.client
import omni.kit.commands

from pathlib import Path
from omni.kit.tool.collect import get_instance
from omni.kit.usd.collect import COLLECT_MAPPING_FILE_NAME
from omni.kit.usd.collect.utils import Utils
from omni.kit.window.file_exporter import get_file_exporter
from pxr import Sdf, Usd


# NOTE: those tests belong to omni.kit.tool.collect extension.
class TestCollect(omni.kit.test.AsyncTestCase):
    def list_folder(self, folder_path):
        all_file_names = []
        all_file_paths = []
        result, entry = omni.client.stat(folder_path)
        if result == omni.client.Result.OK and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
            is_folder = True
        else:
            is_folder = False

        if not is_folder:
            all_file_names = [os.path.basename(folder_path)]
        else:
            folder_queue = [folder_path]
            while len(folder_queue) > 0:
                folder = folder_queue.pop(0)
                (result, entries) = omni.client.list(folder)
                if result != omni.client.Result.OK:
                    break
                folders = set((e.relative_path for e in entries if e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN))
                for f in folders:
                    folder_queue.append(f"{folder}/{f}")
                files = set((e.relative_path for e in entries if not e.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN))
                for file in files:
                    all_file_names.append(os.path.basename(file))
                    all_file_paths.append(f"{folder}/{file}")
        return all_file_names, all_file_paths

    def get_test_dir(self):
        token = carb.tokens.get_tokens_interface()
        data_dir = token.resolve("${data}")
        if not data_dir.endswith("/"):
            data_dir += "/"

        data_dir = Utils.normalize_path(data_dir)

        return f"{data_dir}collect_tool_tests"

    def get_test_data_path(self):
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        extension_path = Path(extension_path)

        return extension_path.joinpath("data")

    async def setUp(self):
        self._done = False
        self._get_files_done = False

    async def tearDown(self):
        await omni.client.delete_async(self.get_test_dir())

    async def __wait(self, frames=2):
        for _ in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def __test_folder_ui_internal(self, folder_name, usd_only, material_only, flat_collection):
        test_data_path = self.get_test_data_path()
        test_stage_dir = str(test_data_path.joinpath("test_stages").joinpath(folder_name))
        collected_stage_dir = self.get_test_dir() + f"/collected_{folder_name}"

        self._done = False

        def on_collect_finish():
            self._done = True

        self._get_files_done = False
        
        def on_get_files_finish():
            self._get_files_done = True

        collect_extension = get_instance()
        collect_extension.collect_multiple_in_folder(test_stage_dir, folder_name, self.get_test_dir(), on_get_files_finish, on_collect_finish)
        await self.__wait()
        await self.__test_select_window_internal()
        await self.__test_collect_window_internal(collected_stage_dir, usd_only, material_only, flat_collection)
        await self.__test_progress_and_result_internal(test_stage_dir, collected_stage_dir, usd_only, material_only, flat_collection)


    async def __test_multiple_ui_internal(self, stage_name, root_usds, usd_only, material_only, flat_collection):
        test_data_path = self.get_test_data_path()
        test_stage_dir = str(test_data_path.joinpath("test_stages").joinpath(stage_name))
        test_root_usds = [test_stage_dir + "/" + root_usd for root_usd in root_usds]
        collected_stage_dir = self.get_test_dir() + f"/collected_{stage_name}"

        self._done = False

        def on_finish():
            self._done = True

        collect_extension = get_instance()
        collect_extension.collect_multiple(test_root_usds, stage_name, self.get_test_dir(), on_finish)
        await self.__wait()
        await self.__test_collect_window_internal(collected_stage_dir, usd_only, material_only, flat_collection)
        await self.__test_progress_and_result_internal(test_stage_dir, collected_stage_dir, usd_only, material_only, flat_collection)

    async def __test_ui_internal(
        self, stage_name, root_usd, usd_only,
        material_only, flat_collection,
        default_prim_only=False, usda_to_usdc=False
    ):
        test_data_path = self.get_test_data_path()
        test_stage_dir = str(test_data_path.joinpath("test_stages").joinpath(stage_name))
        test_root_usd = test_stage_dir + "/" + root_usd
        collected_stage_dir = self.get_test_dir() + f"/collected_{stage_name}"

        self._done = False

        def on_finish():
            self._done = True

        collect_extension = get_instance()
        collect_extension.collect(test_root_usd, on_finish)
        await self.__wait()
        await self.__test_collect_window_internal(
            collected_stage_dir, usd_only, material_only,
            flat_collection, default_prim_only,
            usda_to_usdc
        )
        await self.__test_progress_and_result_internal(
            test_stage_dir, collected_stage_dir, usd_only,
            material_only, flat_collection,
            default_prim_only, usda_to_usdc
        )

    async def __test_select_window_internal(self):
        from omni.kit import ui_test

        progress_window = ui_test.find("Collecting")
        self.assertTrue(progress_window)
        while not self._get_files_done:
            await self.__wait()

        self.assertFalse(progress_window.window.visible)

        select_window = ui_test.find("Select Files to Collect")
        await select_window.focus()

        select_all_checkbox = select_window.find("**/CheckBox[*].identifier=='select_all'")
        start_collect_button = select_window.find("**/Button[*].text=='Collect Selected'")
        cancel_button = select_window.find("**/Button[*].text=='Cancel'")
        self.assertTrue(select_all_checkbox)
        self.assertTrue(start_collect_button)
        self.assertTrue(cancel_button)

        select_all_checkbox.model.set_value(False)
        await self.__wait()
        select_all_checkbox.model.set_value(True)

        await start_collect_button.click()

        await self.__wait()

        collect_window = ui_test.find("Collection Options")
        self.assertTrue(collect_window)

    async def __test_collect_window_internal(
        self, collected_stage_dir, usd_only,
        material_only, flat_collection,
        default_prim_only=False,
        usda_to_usdc=False
    ):
        from omni.kit import ui_test

        collect_window = ui_test.find("Collection Options")
        await collect_window.focus()

        usd_only_checkbox = collect_window.find("**/CheckBox[*].identifier=='usd_only_checkbox'")
        material_only_checkbox = collect_window.find("**/CheckBox[*].identifier=='material_only_checkbox'")
        flat_collection_checkbox = collect_window.find("**/CheckBox[*].identifier=='flat_collection_checkbox'")
        folder_button = collect_window.find("**/Button[*].identifier=='folder_button'")
        path_field = collect_window.find("**/StringField[*].identifier=='collect_path'")
        start_button = collect_window.find("**/Button[*].text=='Start'")
        cancel_button = collect_window.find("**/Button[*].text=='Cancel'")
        option_combo = collect_window.find("**/ComboBox[*].identifier=='texture_option_combo'")
        default_prim_only_checkbox = collect_window.find("**/CheckBox[*].identifier=='default_prim_only_checkbox'")
        default_prim_option_combo = collect_window.find("**/ComboBox[*].identifier=='default_prim_option_combo'")
        usda_to_usdc_checkbox = collect_window.find("**/CheckBox[*].identifier=='usda_to_usdc_checkbox'")
        self.assertTrue(usd_only_checkbox)
        self.assertTrue(material_only_checkbox)
        self.assertTrue(flat_collection_checkbox)
        self.assertTrue(folder_button)
        self.assertTrue(path_field)
        self.assertTrue(start_button)
        self.assertTrue(cancel_button)
        self.assertTrue(option_combo)
        self.assertTrue(default_prim_only_checkbox)
        self.assertTrue(default_prim_option_combo)
        self.assertTrue(usda_to_usdc_checkbox)

        usd_only_checkbox.model.set_value(False)
        material_only_checkbox.model.set_value(False)
        flat_collection_checkbox.model.set_value(False)
        default_prim_only_checkbox.model.set_value(False)
        usda_to_usdc_checkbox.model.set_value(False)

        if usd_only:
            await usd_only_checkbox.click()

        if material_only:
            await material_only_checkbox.click()

        if flat_collection:
            self.assertFalse(option_combo.widget.visible)
            await flat_collection_checkbox.click()

            # should show texture options combo here
            self.assertTrue(option_combo.widget.visible)

        if default_prim_only:
            self.assertFalse(default_prim_option_combo.widget.visible)
            await default_prim_only_checkbox.click()
            self.assertTrue(default_prim_option_combo.widget.visible)

        if usda_to_usdc:
            await usda_to_usdc_checkbox.click()

        await folder_button.click()

        file_picker = get_file_exporter()
        self.assertTrue(file_picker)

        file_picker.click_apply(filename_url=collected_stage_dir)
        path_field.model.set_value(collected_stage_dir)
        await start_button.click()

        await self.__wait()

        progress_window = ui_test.find("Collecting")
        self.assertTrue(progress_window)
        while not self._done:
            await self.__wait()

        self.assertFalse(progress_window.window.visible)

    async def __test_progress_and_result_internal(
        self, test_stage_dir, collected_stage_dir,
        usd_only, material_only, flat_collection,
        default_prim_only=False, usda_to_usdc=False
    ):
        before, _ = self.list_folder(test_stage_dir)
        after, after_abs = self.list_folder(collected_stage_dir)
        self.assertTrue(len(after) > 0)

        if usd_only:
            before_filtered = []
            for f in before:
                if omni.usd.is_usd_writable_filetype(f):
                    before_filtered.append(f)
            before = before_filtered

        if material_only:
            before_filtered = []
            for f in before:
                if not omni.usd.is_usd_writable_filetype(f):
                    before_filtered.append(f)
            before = before_filtered

        # for this test file, it should only collect the usd file
        # when default prim only is true
        if default_prim_only:
            before_filtered = []
            for f in before:
                if omni.usd.is_usd_writable_filetype(f):
                    before_filtered.append(f)

            before = before_filtered

        if usda_to_usdc:
            for file_path in after_abs:
                if omni.usd.is_usd_writable_filetype(file_path):
                    layer = Sdf.Layer.FindOrOpen(file_path)
                    file_format = Usd.UsdFileFormat.GetUnderlyingFormatForLayer(layer)
                    self.assertEqual(file_format, "usdc")

                    _, ext = os.path.splitext(file_path)
                    self.assertEqual(ext, ".usd")

                    layer = None

            before_filtered = []
            for f in before:
                base, ext = os.path.splitext(f)
                if ext == ".usda":
                    base += ".usd"
                else:
                    base = f
                before_filtered.append(base)

            before = before_filtered

        self.assertTrue(COLLECT_MAPPING_FILE_NAME in after)
        after.remove(COLLECT_MAPPING_FILE_NAME)
        self.assertEqual(set(before), set(after))
        self.assertTrue(self._done)

    async def test_ui_collect_with_usd_and_material(self):
        await self.__test_ui_internal("normal", "FullScene.usd", False, False, False)

    async def test_ui_collect_without_material(self):
        await self.__test_ui_internal("normal", "FullScene.usd", False, True, False)

    async def test_ui_collect_without_usd(self):
        await self.__test_ui_internal("normal", "FullScene.usd", True, False, False)

    async def test_om_55150(self):
        await self.__test_ui_internal("OM_55150", "collect_donut.usd", False, False, False)

    async def test_ui_flatten_collection(self):
        await self.__test_ui_internal("normal", "FullScene.usd", False, False, True)

    async def test_ui_default_prim_only(self):
        await self.__test_ui_internal("default_prim", "has_enviroment.usd", False, False, False, True)

    async def test_ui_usda_to_usdc(self):
        await self.__test_ui_internal("usda_to_usdc", "main.usda", False, False, False, True, True)

    async def test_ui_collect_multiple_with_usd_and_material(self):
        await self.__test_multiple_ui_internal("normal", ["FullScene.usd","Contour1_Surface.usd"], False, False, False)

    async def test_ui_collect_multiple_without_material(self):
        await self.__test_multiple_ui_internal("normal", ["FullScene.usd","Contour1_Surface.usd"], False, True, False)

    async def test_ui_collect_multiple_without_usd(self):
        await self.__test_multiple_ui_internal("normal", ["FullScene.usd","Contour1_Surface.usd"], True, False, False)

    async def test_ui_flatten_multiple_collection(self):
        await self.__test_multiple_ui_internal("normal", ["FullScene.usd","Contour1_Surface.usd"], False, False, True)

    async def test_file_menu(self):
        await omni.usd.get_context().new_stage_async()

        from omni.kit import ui_test

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        extension_path = Path(extension_path)
        test_data_path = extension_path.joinpath("data")
        test_stage_dir = str(test_data_path.joinpath("test_stages").joinpath("udim"))
        test_root_usd = test_stage_dir + "/SM_Hood_A1_1.usd"

        success, _ = await omni.usd.get_context().open_stage_async(test_root_usd)
        self.assertTrue(success)
        await self.__wait(100)
        await ui_test.menu_click("File/Collect As...")
        await self.__wait(10)

        collect_window = ui_test.find("Collection Options")
        self.assertTrue(collect_window)
        self.assertTrue(collect_window.widget.visible)

    async def test_ui_folder_multiple_collection(self):
        await self.__test_folder_ui_internal("usda_to_usdc", False, False, True)