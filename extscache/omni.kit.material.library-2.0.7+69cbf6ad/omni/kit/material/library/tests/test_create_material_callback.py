import weakref
import unittest
import pathlib
import asyncio
import omni.kit.test
import omni.ui as ui
import carb
from omni.kit import ui_test
from pxr import Usd, Sdf, UsdGeom, UsdShade
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.test_suite.helpers import open_stage, get_test_data_path, select_prims, wait_stage_loading


class TestCreateMaterialCallback(OmniUiTest):

    # Before running each test
    async def setUp(self):
        await open_stage(get_test_data_path(__name__, "usd/color_map_types.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_create_material_callback(self):
        usd_context = omni.usd.get_context()

        prim_path = "/World/Plane"
        prim_name ="testplane"

        #Get the stage
        stage = omni.usd.get_context().get_stage()

        #Create a Plane Prim
        omni.kit.commands.execute('CreatePrimWithDefaultXform',prim_type='Plane', prim_path=prim_path )

        #Select the Plane
        omni.kit.commands.execute('SelectPrims',old_selected_paths=[''],new_selected_paths=[prim_path],expand_in_stage=True)

        future_test = asyncio.Future()
        prim = None

        async def on_created(shader_prim: Usd.Prim):
            nonlocal future_test
            nonlocal prim

            for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
                w.widget.collapsed = False
            await self.wait_n_updates(3)

            widget_ref = ui_test.find("Property//Frame/**/StringField[*].identifier=='sdf_asset_inputs:diffuse_texture'")
            self.assertIsNotNone(widget_ref)
            model = widget_ref.widget.model
            self.assertIsNotNone(model)

            model.set_value("./test.png")
            await self.wait_n_updates(3)

            prim = shader_prim
            await ui_test.human_delay(10)
            future_test.set_result(True)

        async def wait_for_event():
            nonlocal future_test

            await future_test

        #Create a Shader
        omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
                                  mdl_name='OmniPBR.mdl',
                                  mtl_name='OmniPBR',
                                  prim_name=prim_name,
                                  mtl_created_list=None,
                                  bind_selected_prims=True,
                                  on_created_fn=lambda p: asyncio.ensure_future(on_created(p))
        )

        try:
            await asyncio.wait_for(wait_for_event(), timeout=30.0)
        except asyncio.TimeoutError: # pragma: no cover
            carb.log_error(f"timeout waiting for on_created to be called")

        future_test = None
        asset_path = prim.GetAttribute('inputs:diffuse_texture').Get()
        self.assertEqual(asset_path.path, "./test.png")
