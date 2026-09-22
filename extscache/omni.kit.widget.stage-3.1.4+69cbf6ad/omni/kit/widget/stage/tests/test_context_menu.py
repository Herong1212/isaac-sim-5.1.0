import carb.settings
import omni
import omni.kit.test
import omni.usd
import omni.client
import omni.kit.widget.stage
import omni.kit.app
import omni.kit.ui_test as ui_test
import pathlib

from omni.kit.test_suite.helpers import arrange_windows
from pxr import Sdf, UsdShade, Usd



class TestContextMenu(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        await arrange_windows("Stage", 800, 600)

        self.app = omni.kit.app.get_app()
        self.usd_context = omni.usd.get_context()
        await self.usd_context.new_stage_async()
        self.stage = omni.usd.get_context().get_stage()
        self.layer = Sdf.Layer.CreateAnonymous()

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._test_path = pathlib.Path(extension_path).joinpath("data").joinpath("tests")
        self._cube_usd_path = str(self._test_path.joinpath("usd/cube.usda"))

        self.ref_prim = self.stage.DefinePrim("/reference0", "Xform")
        self.ref_prim.GetReferences().AddReference(self.layer.identifier)
        self.child_prim = self.stage.DefinePrim("/reference0/child0", "Xform")

        self.payload_prim = self.stage.DefinePrim("/payload0", "Xform")
        self.payload_prim.GetPayloads().AddPayload(self.layer.identifier)

        self.rf_prim = self.stage.DefinePrim("/reference_and_payload0", "Xform")
        self.rf_prim.GetReferences().AddReference(self.layer.identifier)
        self.rf_prim.GetPayloads().AddPayload(self.layer.identifier)
        await self.wait(frames=2)
        self.stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")

        settings = carb.settings.get_settings()
        self._original_setting_value = settings.get_as_string("/persistent/app/stage/unicodeNormalizationMethod")

    async def tearDown(self):
        settings = carb.settings.get_settings()
        settings.set("/persistent/app/stage/unicodeNormalizationMethod", self._original_setting_value)

    async def wait(self, frames=10):
        for _ in range(frames):
            await self.app.next_update_async()

    async def _find_all_prim_items(self):
        reference_widget = self.stage_tree.find("**/Label[*].text=='reference0'")
        payload_widget = self.stage_tree.find("**/Label[*].text=='payload0'")
        reference_and_payload_widget = self.stage_tree.find("**/Label[*].text=='reference_and_payload0'")

        return reference_widget, payload_widget, reference_and_payload_widget

    async def test_default_prim(self):
        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Clear Default Prim", human_delay_speed=1)

        await rf_widget.right_click()
        await ui_test.select_context_menu("Set as Default Prim", human_delay_speed=1)
        await self.wait(frames=2)

        ref_widget = self.stage_tree.find("**/Label[*].text=='reference0 (defaultPrim)'")
        self.assertTrue(ref_widget)

        ref_widget_old = self.stage_tree.find("**/Label[*].text=='reference0'")
        self.assertFalse(ref_widget_old)

        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Set as Default Prim", human_delay_speed=1)

        await rf_widget.right_click()
        await ui_test.select_context_menu("Clear Default Prim", human_delay_speed=1)
        await self.wait()

        ref_widget_old = self.stage_tree.find("**/Label[*].text=='reference0 (defaultPrim)'")
        self.assertFalse(ref_widget_old)

        ref_widget = self.stage_tree.find("**/Label[*].text=='reference0'")
        self.assertTrue(ref_widget)

    async def test_find_in_browser(self):
        self.usd_context.get_selection().set_selected_prim_paths(
            [str(self.ref_prim.GetPath())], True
        )
        await self.wait(frames=2)
        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        # If there are no on-disk references
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Find in Content Browser", human_delay_speed=1)

        # Adds a reference that's on disk.
        self.ref_prim.GetReferences().ClearReferences()
        self.ref_prim.GetReferences().AddReference(self._cube_usd_path)
        await self.wait(frames=2)

        await rf_widget.right_click()
        await ui_test.select_context_menu("Find in Content Browser", human_delay_speed=1)

    async def test_group_selected(self):
        self.usd_context.get_selection().set_selected_prim_paths(
            [str(self.ref_prim.GetPath()), str(self.payload_prim.GetPath())], True
        )
        await self.wait(frames=2)

        old_ref_path = self.ref_prim.GetPath()
        old_payload_path = self.payload_prim.GetPath()

        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        await ui_test.select_context_menu("Group Selected", human_delay_speed=1)
        await self.wait(frames=2)

        new_ref_path = Sdf.Path("/Group").AppendElementString(old_ref_path.name)
        new_payload_path = Sdf.Path("/Group").AppendElementString(old_payload_path.name)

        self.assertFalse(self.stage.GetPrimAtPath(old_ref_path))
        self.assertFalse(self.stage.GetPrimAtPath(old_payload_path))
        self.assertTrue(self.stage.GetPrimAtPath(new_ref_path))
        self.assertTrue(self.stage.GetPrimAtPath(new_payload_path))

        self.usd_context.get_selection().set_selected_prim_paths(
            [str(new_ref_path), str(new_payload_path)], True
        )
        await self.wait(frames=2)

        ref_widget = self.stage_tree.find("**/Label[*].text=='reference0'")
        self.assertTrue(ref_widget)
        await rf_widget.right_click()
        await ui_test.select_context_menu("Ungroup Selected", human_delay_speed=1)
        await self.wait(frames=2)

        self.assertTrue(self.stage.GetPrimAtPath(old_ref_path))
        self.assertTrue(self.stage.GetPrimAtPath(old_payload_path))
        self.assertFalse(self.stage.GetPrimAtPath(new_ref_path))
        self.assertFalse(self.stage.GetPrimAtPath(new_payload_path))

    async def test_duplicate_prim(self):
        self.usd_context.get_selection().set_selected_prim_paths(
            [str(self.ref_prim.GetPath()), str(self.payload_prim.GetPath())], True
        )
        await self.wait(frames=2)
        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        await ui_test.select_context_menu("Duplicate")
        self.assertTrue(self.stage.GetPrimAtPath("/reference0_01"))
        self.assertTrue(self.stage.GetPrimAtPath("/payload0_01"))

    async def test_delete_prim(self):
        self.usd_context.get_selection().set_selected_prim_paths(
            [str(self.ref_prim.GetPath()), str(self.payload_prim.GetPath())], True
        )
        await self.wait(frames=2)
        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        await ui_test.select_context_menu("Delete", human_delay_speed=1)
        self.assertFalse(self.ref_prim)
        self.assertFalse(self.payload_prim)

    async def test_refresh_reference_or_payload(self):
        self.usd_context.get_selection().set_selected_prim_paths(
            [str(self.ref_prim.GetPath())], True
        )
        await self.wait(frames=2)
        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        await ui_test.select_context_menu("Refresh Reference", human_delay_speed=1)

    async def test_convert_between_ref_and_payload(self):
        rf_widget, payload_widget, ref_and_payload_widget = await self._find_all_prim_items()
        await rf_widget.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Convert Payloads to References", human_delay_speed=1)

        await rf_widget.right_click()
        await ui_test.select_context_menu("Convert References to Payloads")
        ref_prim = self.stage.GetPrimAtPath("/reference0")
        ref_and_layers = omni.usd.get_composed_references_from_prim(ref_prim)
        payload_and_layers = omni.usd.get_composed_payloads_from_prim(ref_prim)
        self.assertTrue(len(ref_and_layers) == 0)
        self.assertTrue(len(payload_and_layers) == 1)

        await payload_widget.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Convert References to Payloads", human_delay_speed=1)
        await payload_widget.right_click()
        await ui_test.select_context_menu("Convert Payloads to References")
        payload_prim = self.stage.GetPrimAtPath("/payload0")
        ref_and_layers = omni.usd.get_composed_references_from_prim(payload_prim)
        payload_and_layers = omni.usd.get_composed_payloads_from_prim(payload_prim)
        self.assertTrue(len(ref_and_layers) == 1)
        self.assertTrue(len(payload_and_layers) == 0)

        await ref_and_payload_widget.right_click()
        await ui_test.select_context_menu("Convert References to Payloads")
        prim = self.stage.GetPrimAtPath("/reference_and_payload0")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        payload_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 0)
        self.assertEqual(len(payload_and_layers), 1)

        await ref_and_payload_widget.right_click()
        await ui_test.select_context_menu("Convert Payloads to References")
        prim = self.stage.GetPrimAtPath("/reference_and_payload0")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        payload_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertEqual(len(ref_and_layers), 1)
        self.assertEqual(len(payload_and_layers), 0)

    async def test_select_bound_objects(self):
        menu_name = "Select Bound Objects"
        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu(menu_name, human_delay_speed=1)

        material = UsdShade.Material.Define(self.stage, "/material0")
        UsdShade.MaterialBindingAPI(self.payload_prim).Bind(material)
        await self.wait()
        material_widget = self.stage_tree.find("**/Label[*].text=='material0'")

        await material_widget.right_click()
        await ui_test.select_context_menu(menu_name, human_delay_speed=1)
        await self.wait(frames=2)
        self.assertEqual(omni.usd.get_context().get_selection().get_selected_prim_paths(), [str(self.payload_prim.GetPath())])

    async def test_binding_material(self):
        menu_name = "Bind Material To Selected Objects"
        rf_widget, _, _ = await self._find_all_prim_items()
        await rf_widget.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu(menu_name, human_delay_speed=1)

        material = UsdShade.Material.Define(self.stage, "/material0")
        UsdShade.MaterialBindingAPI(self.payload_prim).Bind(material)
        await self.wait()
        material_widget = self.stage_tree.find("**/Label[*].text=='material0'")

        await material_widget.right_click()
        # No valid selection
        with self.assertRaises(Exception):
            await ui_test.select_context_menu(menu_name, human_delay_speed=1)

        self.usd_context.get_selection().set_selected_prim_paths(
            [str(self.payload_prim.GetPath())], True
        )
        await self.wait(frames=2)
        await material_widget.right_click()
        await ui_test.select_context_menu(menu_name, human_delay_speed=1)
        await self.wait(frames=5)

        selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        self.assertEqual(selected_paths, [str(self.payload_prim.GetPath())])

    async def test_set_kind(self):
        rf_widget, _, _ = await self._find_all_prim_items()
        self.usd_context.get_selection().set_selected_prim_paths(
            [str(self.ref_prim.GetPath())], True
        )
        await self.wait(frames=2)

        for name in ["Assembly", "Group", "Component", "Subcomponent"]:
            await rf_widget.right_click()
            await ui_test.select_context_menu(f"Set Kind/{name}", human_delay_speed=1)

    async def test_lock_specs(self):
        rf_widget, _, _ = await self._find_all_prim_items()
        for menu_name in ["Lock Selected", "Unlock Selected", "Lock Selected Hierarchy", "Unlock Selected Hierarchy"]:
            await rf_widget.right_click()
            await ui_test.select_context_menu(f"Locks/{menu_name}", human_delay_speed=1)

        await rf_widget.right_click()
        await ui_test.select_context_menu("Locks/Lock Selected Hierarchy", human_delay_speed=1)

        await rf_widget.right_click()
        await ui_test.select_context_menu("Locks/Select Locked Prims", human_delay_speed=1)
        await self.wait(frames=5)
        selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        self.assertEqual(set(selected_paths), set([str(self.ref_prim.GetPath()), str(self.child_prim.GetPath())]))

    async def test_assign_material(self):
        menu_name = "Assign Material"
        rf_widget, _, _ = await self._find_all_prim_items()

        material = UsdShade.Material.Define(self.stage, "/material0")
        UsdShade.MaterialBindingAPI(self.payload_prim).Bind(material)
        await self.wait()

        await rf_widget.right_click()
        await ui_test.select_context_menu(menu_name)

        dialog = ui_test.find("Bind material to reference0###context_menu_bind")
        self.assertTrue(dialog)
        button = dialog.find("**/Button[*].text=='Ok'")
        self.assertTrue(button)
        await button.click()

    async def test_rename_prim(self):
        await ui_test.find("Stage").focus()
        menu_name = "Rename"
        rf_widget, _, _ = await self._find_all_prim_items()

        await rf_widget.right_click(rf_widget.center)
        await ui_test.select_context_menu(menu_name, human_delay_speed=1)
        await self.wait(frames=5)
        string_fields = self.stage_tree.find_all("**/StringField[*].identifier=='rename_field'")
        self.assertTrue(len(string_fields) > 0)
        string_field = string_fields[0]
        # FIXME: Cannot make it visible in tests, but have to do it manually
        string_field.widget.visible = True
        await string_field.input("test测试★")
        self.assertTrue(self.stage.GetPrimAtPath("/reference0test测试_"))
        self.assertFalse(self.stage.GetPrimAtPath("/reference0"))

    async def test_rename_prim_unicode_NFC_normalization(self):
        import unicodedata

        await ui_test.find("Stage").focus()
        menu_name = "Rename"
        # Test NFC normalization
        # These 2 prim names are unique in NFD but same in NFC
        two_codepoints = '가'       # ᄀ + ᅡ
        single_codepoint = '가'     # 가
        prim0 = self.stage.DefinePrim(f"/prim_{two_codepoints}", "Xform")
        prim1 = self.stage.DefinePrim(f"/prim_{single_codepoint}", "Xform")

        self.assertNotEqual(prim0.GetName(), prim1.GetName())
        self.assertEqual(unicodedata.normalize("NFC", prim0.GetName()), unicodedata.normalize("NFC", prim1.GetName()))

        # Turn on NFC normalization option
        settings = carb.settings.get_settings()
        settings.set("/persistent/app/stage/unicodeNormalizationMethod", "NFC")

        # Try to rename prim0
        await self.wait(frames=5)
        prim0_widget = self.stage_tree.find(f"**/Label[*].text=='{prim0.GetName()}'")
        await prim0_widget.right_click(prim0_widget.center)
        await ui_test.select_context_menu(menu_name, human_delay_speed=1)
        await self.wait(frames=5)
        string_fields = self.stage_tree.find_all("**/StringField[*].identifier=='rename_field'")
        for f in string_fields:
            if f.position.y == prim0_widget.position.y:
                string_field = f
                break
        self.assertIsNotNone(string_field)
        string_field.widget.visible = True
        # If we don't do any edit, the prim name should automatically be applied NFC normalization, and since
        # there's already a prim with the same name, it will be renamed to prim_가_01
        string_field.widget.model.end_edit()
        await self.wait(frames=5)
        self.assertFalse(prim0.IsValid())
        renamed_prim = self.stage.GetPrimAtPath(f"/prim_{single_codepoint}_01")
        self.assertTrue(renamed_prim.IsValid())
        self.assertEqual(renamed_prim.GetName(), "prim_가_01")

    async def test_activate_prims(self):
        await ui_test.find("Stage").focus()
        rf_widget, _, _ = await self._find_all_prim_items()

        stage_model = self.stage_tree.model
        item0 = stage_model._get_stage_item_from_cache(self.ref_prim.GetPath(), True)
        item1 = stage_model._get_stage_item_from_cache(self.payload_prim.GetPath(), True)
        item2 = stage_model._get_stage_item_from_cache(self.rf_prim.GetPath(), True)
        stage_model.set_selected_stage_items([item0, item1, item2])
        await self.wait(frames=2)
        self.assertEqual(set(self.stage_tree.widget.selection), set([item0, item1, item2]))

        await rf_widget.right_click(rf_widget.center)
        await ui_test.select_context_menu("Deactivate", human_delay_speed=1)
        await self.wait(10)

        self.assertTrue(not self.ref_prim.IsActive())
        self.assertTrue(not self.payload_prim.IsActive())
        self.assertTrue(not self.rf_prim.IsActive())
        self.assertEqual(set(self.stage_tree.widget.selection), set([item0, item1, item2]))

        await rf_widget.right_click(rf_widget.center)
        await ui_test.select_context_menu("Activate", human_delay_speed=1)
        await self.wait(10)

        self.assertTrue(self.ref_prim.IsActive())
        self.assertTrue(self.payload_prim.IsActive())
        self.assertTrue(self.rf_prim.IsActive())
        self.assertEqual(set(self.stage_tree.widget.selection), set([item0, item1, item2]))
