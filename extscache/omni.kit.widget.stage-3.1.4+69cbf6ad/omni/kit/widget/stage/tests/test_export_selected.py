## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import os
import omni.kit.app
import omni.usd

from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.test_suite.helpers import open_stage, get_test_data_path, select_prims, wait_stage_loading, arrange_windows
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
from omni.kit.window.file_exporter import get_instance as get_file_exporter


class TestExportSelected(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd/test_export_simple.usda"))
        stage_window = ui_test.find("Stage")
        await stage_window.focus()

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()


    async def test_l1_stage_menu_export_selected_single_prim(self):
        stage = omni.usd.get_context().get_stage()
        to_select = ["/World/Cone"]
        test_file = os.path.join(omni.kit.test.get_test_output_path(), "save_single_selected_prim.usd")

        # select prims
        await select_prims(to_select)

        # right click on Cube
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{to_select[0]}'").right_click()

        # click on context menu item & save
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Selected")
            await file_export_helper.wait_for_popup()
            await file_export_helper.click_apply_async(filename_url=test_file)
            await wait_stage_loading()

        # load created file
        await open_stage(test_file)
        await wait_stage_loading()

        # verify prims
        stage = omni.usd.get_context().get_stage()
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/Root', '/Root/Cone'])

        # close stage & delete file
        await omni.usd.get_context().new_stage_async()


    async def test_l1_stage_menu_export_selected_multiple_prims(self):
        stage = omni.usd.get_context().get_stage()
        to_select = ["/World/Cone", "/World/Cube"]
        test_file = os.path.join(omni.kit.test.get_test_output_path(), "save_multiple_selected_prim.usd")

        # select prims
        await select_prims(to_select)

        # right click on Cube
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{to_select[0]}'").right_click()

        # click on context menu item & save
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Selected")
            await file_export_helper.wait_for_popup()
            await file_export_helper.click_apply_async(filename_url=test_file)
            await wait_stage_loading()

        # load created file
        await open_stage(test_file)
        await wait_stage_loading()

        # verify prims
        stage = omni.usd.get_context().get_stage()
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(set(prims), set(['/Root', '/Root/Cone', '/Root/Cone/Cone', '/Root/Cube', '/Root/Cube/Cube']))

        # close stage & delete file
        await omni.usd.get_context().new_stage_async()


    async def test_l1_stage_menu_export_selected_single_material(self):
        stage = omni.usd.get_context().get_stage()
        to_select = ["/World/Looks/OmniPBR"]
        test_file = os.path.join(omni.kit.test.get_test_output_path(), "save_single_selected_material.usd")

        # select prims
        await select_prims(to_select)

        # right click on Cube
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{to_select[0]}'").right_click()

        # click on context menu item & save
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Selected")
            await file_export_helper.wait_for_popup()
            await file_export_helper.click_apply_async(filename_url=test_file)
            await wait_stage_loading()

        # load created file
        await open_stage(test_file)
        await wait_stage_loading()

        # verify prims
        stage = omni.usd.get_context().get_stage()
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/Root', '/Root/OmniPBR', '/Root/OmniPBR/Shader'])

        # close stage & delete file
        await omni.usd.get_context().new_stage_async()


    async def test_l1_stage_menu_export_selected_multiple_materials(self):
        stage = omni.usd.get_context().get_stage()
        to_select = ["/World/Looks/OmniPBR", "/World/Looks/OmniGlass"]
        test_file = os.path.join(omni.kit.test.get_test_output_path(), "save_multiple_selected_material.usd")

        # select prims
        await select_prims(to_select)

        # right click on Cube
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{to_select[0]}'").right_click()

        # click on context menu item & save
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Selected")
            await file_export_helper.wait_for_popup()
            await file_export_helper.click_apply_async(filename_url=test_file)
            await wait_stage_loading()

        # load created file
        await open_stage(test_file)
        await wait_stage_loading()

        # verify prims
        stage = omni.usd.get_context().get_stage()
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(set(prims), set(['/Root', '/Root/OmniPBR', '/Root/OmniPBR/Shader', '/Root/OmniGlass', '/Root/OmniGlass/Shader']))

        # close stage & delete file
        await omni.usd.get_context().new_stage_async()

    async def test_stage_menu_export_selected_prefill(self):
        """Test that export selected pre-fill prim name and save directory."""
        stage = omni.usd.get_context().get_stage()
        to_select = ["/World/Cone", "/World/Cube"]
        output_dir = omni.kit.test.get_test_output_path()
        test_file = os.path.join(output_dir, "test_prefill.usd")

        # select prims
        await select_prims(to_select)

        # right click on Cube
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{to_select[0]}'").right_click()

        # click on context menu item & save
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Selected")
            await file_export_helper.wait_for_popup()
            # check that prim name is pre-fill with the first prim name
            exporter = get_file_exporter()
            filename = exporter._dialog.get_filename()
            self.assertEqual(filename, "Cone")
            # check that current directory is the same as the stage directory
            dirname = exporter._dialog.get_current_directory()
            self.assertEqual(dirname.rstrip("/").lower(),
                os.path.dirname(stage.GetRootLayer().realPath).replace("\\", "/").lower())
            await file_export_helper.click_apply_async(filename_url=test_file)
            await wait_stage_loading()

        # right click again, now the default directory for save should update to the last save directory
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{to_select[0]}'").right_click()
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Selected")
            await file_export_helper.wait_for_popup()
            exporter = get_file_exporter()
            # check that current directory is the same as the stage directory
            dirname = exporter._dialog.get_current_directory()
            self.assertEqual(dirname.rstrip("/").lower(), output_dir.replace("\\", "/").lower())
            await file_export_helper.click_cancel_async()

        # load another file
        output_dir = get_test_data_path(__name__, "usd")
        await open_stage(os.path.join(output_dir, "cube.usda"))
        await wait_stage_loading()
        stage = omni.usd.get_context().get_stage()

        # check that current directory is the same as the stage directory
        to_select = ["/World/Cube"]
        await select_prims(to_select)

        # right click on Cube
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_widget.find(f"**/StringField[*].model.path=='{to_select[0]}'").right_click()

        # click on context menu item & save
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Selected")
            await file_export_helper.wait_for_popup()
            # check that prim name is pre-fill with the selected prim name
            exporter = get_file_exporter()
            filename = exporter._dialog.get_filename()
            self.assertEqual(filename, "Cube")
            # check that current directory is the same as the stage directory
            dirname = exporter._dialog.get_current_directory()
            self.assertEqual(dirname.rstrip("/").lower(),
                os.path.dirname(stage.GetRootLayer().realPath).replace("\\", "/").lower())
            await file_export_helper.click_cancel_async()

        # close stage & delete file
        await omni.usd.get_context().new_stage_async()


class TestExportUtils(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_export_prims_with_variant_sets(self):
        """Test exporting prims with variant sets correctly duplicates all variants setup."""
        from ..export_utils import export

        def _check_variant_result(prim, set_name, variant_names, current_variant):
            variant_set = prim.GetVariantSets().GetVariantSet(set_name)
            self.assertIsNotNone(variant_set)
            self.assertListEqual(variant_names, variant_set.GetVariantNames())
            self.assertEqual(prim.GetVariantSets().GetVariantSelection(set_name), current_variant)

        await open_stage(get_test_data_path(__name__, "usd/prim_with_variants.usda"))

        stage = omni.usd.get_context().get_stage()
        to_select = ["/World/Xform_no_varset", "/World/Cube_1_varset", "/World/Xform/Cone_2_varsets"]
        test_file = os.path.join(omni.kit.test.get_test_output_path(), "prim_with_variants_saved.usd")
        export(test_file, [stage.GetPrimAtPath(p) for p in to_select])

        # load created file
        await open_stage(test_file)
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()
        # check recursively look up all children and duplicate variants works
        prim = stage.GetPrimAtPath("/Root/Xform_no_varset/Xform_no_varset/Xform/Cylinder_1_varset")
        # variant set should be set to C with 3 variants
        _check_variant_result(prim, "Set", ["A", "B", "C"], "C")

        # check single variant set is correct
        prim = stage.GetPrimAtPath("/Root/Cube_1_varset/Cube_1_varset")
        # variant set should be set to B with 2 variants
        _check_variant_result(prim, "Set", ["A", "B"], "B")

        # check multiple variant sets duplication is correct
        prim = stage.GetPrimAtPath("/Root/Cone_2_varsets/Cone_2_varsets")
        # variant set1 should be set to A with 2 variants, variant set2 should be set to D with 3 variants
        _check_variant_result(prim, "Set1", ["A", "B"], "A")
        _check_variant_result(prim, "Set2", ["C", "D", "E"], "D")

        # close stage & delete file
        await omni.usd.get_context().new_stage_async()

    async def test_export_parent_and_child_prims(self):
        """Test exporting prims that are parent and descendants."""
        from ..export_utils import export

        await open_stage(get_test_data_path(__name__, "usd/test_export.usda"))
        stage = omni.usd.get_context().get_stage()

        # Select all parents of a child prim with other prim
        to_select = ["/World/Xform_Multi", "/World/Xform_Multi/Xform_nothing", "/World/Xform_Multi/Xform_Cube/Cube",
                     "/World/Xform_Multi/Xform/Xform_Child"]
        test_file_00 = os.path.join(omni.kit.test.get_test_output_path(), "export_selected_00.usd")
        export(test_file_00, [stage.GetPrimAtPath(p) for p in to_select])

        # Select prims that are leaf node and a middle level node
        to_select = ["/World/Xform_Multi/Xform/Xform_Child", "/World/Disk", "/World/Xform_Cone"]
        test_file_01 = os.path.join(omni.kit.test.get_test_output_path(), "export_selected_01.usd")
        export(test_file_01, [stage.GetPrimAtPath(p) for p in to_select])

        # load created file
        await open_stage(test_file_00)
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()
        # check that exported prims are as expected, we should only have one top level prim exported
        prim = stage.GetPrimAtPath("/Root/Xform_Multi")
        self.assertIsNotNone(prim)
        root_prim = stage.GetPrimAtPath("/Root")
        self.assertEqual(root_prim.GetAllChildrenNames(), ["Xform_Multi"])

        # load created file
        await open_stage(test_file_01)
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()
        # check that exported prims are as expected, we should only have one top level prim exported
        root_prim = stage.GetPrimAtPath("/Root")
        self.assertEqual(sorted(root_prim.GetAllChildrenNames()), ["Disk", "Xform_Child", "Xform_Cone"])

        # close stage & delete file
        await omni.usd.get_context().new_stage_async()
