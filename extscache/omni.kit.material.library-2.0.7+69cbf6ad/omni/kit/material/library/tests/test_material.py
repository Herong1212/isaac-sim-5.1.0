import weakref
import unittest
import pathlib
import omni.kit.test
import omni.ui as ui
import carb
from omni.kit import ui_test
from pxr import Usd, Sdf, UsdGeom, UsdShade
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.test_suite.helpers import wait_stage_loading, arrange_windows

SDF_PATH_INVALID = "$NONE$"

class TestMaterialWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage")

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        await wait_stage_loading()

    async def test_material_widget_API(self):
        cache_updates = 0

        def prim_cache_changed():
            nonlocal cache_updates

            cache_updates += 1

        def get_material_strength(prim):
            strength = None
            material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            if relationship:
                strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(relationship)
            return strength

        # wait for material to be preloaded so create menu is complete & menus don't rebuild during tests
        await omni.kit.material.library.get_mdl_list_async()
        await ui_test.human_delay()

        await omni.usd.get_context().new_stage_async()
        material_prims, bound_prims = omni.kit.material.library.tests.create_test_stage()

        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        stage = usd_context.get_stage()
        weak_stage = weakref.ref(omni.usd.get_context().get_stage())

        # wait for material loads...
        carb.log_verbose("loading materials")
        await wait_stage_loading()
        await ui_test.human_delay(50)

        try:
            # initalize material.library after materials have loaded to prevent false updates
            await ui_test.human_delay(2)
            omni.kit.material.library.add_cache_changed_fn(prim_cache_changed)

            materials = omni.kit.material.library.get_materials_from_stage(SDF_PATH_INVALID)
            self.assertListEqual([SDF_PATH_INVALID] + sorted(material_prims), materials)

            for prim_path, bound_strength in bound_prims:
                prim = stage.GetPrimAtPath(prim_path)
                strength = get_material_strength(prim)
                self.assertTrue(bound_strength == strength)

            # change selection should not effect cache
            all_prims = []
            for prim in stage.TraverseAll():
                all_prims.append(prim.GetPath().pathString)
            selection.set_selected_prim_paths(all_prims, True)
            await ui_test.human_delay(10)
            self.assertTrue(cache_updates == 0)

            selection.set_selected_prim_paths([], True)
            await ui_test.human_delay(10)
            self.assertTrue(cache_updates == 0)

            # create prim should not effect cache
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/CubeTest1",
                prim_type="Cube",
                select_new_prim=False,
                attributes={UsdGeom.Tokens.size: 100},
            )
            await ui_test.human_delay(10)
            self.assertTrue(cache_updates == 0)

            # delete prim should does effect cache
            omni.kit.commands.execute("DeletePrims", paths=["/CubeTest1"])
            await ui_test.human_delay(10)
            self.assertTrue(cache_updates == 1)

        finally:
            omni.kit.material.library.remove_cache_changed_fn(prim_cache_changed)
