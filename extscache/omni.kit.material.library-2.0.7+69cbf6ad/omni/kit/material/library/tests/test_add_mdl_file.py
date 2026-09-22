import unittest
import omni.kit.test

from pxr import UsdShade
from unittest.mock import patch
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, wait_stage_loading, get_test_data_path
from .. import MaterialLibraryExtension
from ..test_helper import MaterialLibraryTestHelper


class TestMaterialMenuAddMDLFile(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_material_context_menu(self):
        """Testing context menu item to add material from mdl file."""
        with patch.object(MaterialLibraryExtension, "_on_create_custom_mdl_material") as mock_create_material:
            for info in omni.kit.material.library.get_material_list():
                if info.name == "Add MDL File":
                    callback = info.create_fn
                    self.assertTrue(callable(callback))
                    callback()
        # Confirm that action was triggered
        mock_create_material.assert_called_once()

    async def test_add_material_from_mdl(self):
        """Testing addition of material from mdl file."""
        # new stage
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()

        # Load material from mdl file
        async with MaterialLibraryTestHelper() as test_helper:
            await test_helper.add_material(get_test_data_path(__name__, "mtl/TESTEXPORT.mdl"), bind_selected_prims=True)

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # verify
        # NOTE: TESTEXPORT.mdl material is named "Material" so that is the prim created
        shader = UsdShade.Shader(stage.GetPrimAtPath("/Looks/Material/Shader"))
        identifier = shader.GetSourceAssetSubIdentifier("mdl")
        self.assertTrue(identifier == "Material")
