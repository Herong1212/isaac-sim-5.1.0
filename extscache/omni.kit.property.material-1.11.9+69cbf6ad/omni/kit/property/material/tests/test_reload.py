import asyncio
import os
import shutil
import tempfile

import carb
import omni.kit.undo
import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, get_test_data_path
from pxr import Sdf

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialReload(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Property")

    async def test_reload_material(self):
        import omni.UsdMdl as UsdMdl
        from pxr import Tf

        await self._dock_test_window(450, 250)
        await ui_test.human_delay(10)

        omni.kit.window.property.managed_frame.set_collapsed_state("Shader/Info", False)

        scene_file_path = self._get_scene_path("reload.usda")
        await self._load_scene(scene_file_path)

        future_test = asyncio.Future()
        material_reloaded = False

        # NOTE: This is called during test but doesn't register in code coverage
        def on_mdl_module_reload(notice, sender) -> None:  # pragma: no cover
            nonlocal future_test, material_reloaded

            if future_test and not future_test.done():
                future_test.set_result(True)
                material_reloaded = True

        async def wait_for_event():
            nonlocal future_test

            await future_test

        mdl_module_reload_sub = Tf.Notice.Register(UsdMdl.Notice.ModuleReloaded, on_mdl_module_reload, None)

        with tempfile.TemporaryDirectory() as tempdir:
            # copy reload_test.mdl to temp
            src_mdl = get_test_data_path(__name__, "mdl/reload_test.mdl")
            new_mdl = os.path.join(tempdir, "reload_test.mdl")
            shutil.copyfile(src_mdl, new_mdl)

            prim_path = "/World/Looks/mtl_test/construct_float"

            # select shader
            await self._select_prims([prim_path])
            await ui_test.human_delay(10)

            # changing the source asset clears the subidentifier, so we get its value and restore it below.
            attribute_path = Sdf.Path(prim_path).AppendProperty("info:mdl:sourceAsset:subIdentifier")
            attribute = self._get_attribute_at_path(attribute_path)
            subidentifier = attribute.Get()

            # change sourceAsset
            source_asset_widget = ui_test.find_first(
                "Property//Frame/**/StringField[*].identifier=='sdf_asset_info:mdl:sourceAsset'"
            )
            self.assertTrue(source_asset_widget)
            source_asset_widget.model.set_value(new_mdl)
            await ui_test.human_delay(10)

            attribute.Set(subidentifier)
            await ui_test.human_delay(10)

            # copy reload_test_2.mdl to temp triggering on_mdl_module_reload
            src_mdl = get_test_data_path(__name__, "mdl/reload_test_2.mdl")
            shutil.copyfile(src_mdl, new_mdl)

            # wait for material reload
            try:
                await asyncio.wait_for(wait_for_event(), timeout=1000)
            except asyncio.TimeoutError:  # pragma: no cover
                carb.log_error("test_reload_material: timeout waiting for UsdMdl.Notice.ModuleReloaded")
            finally:
                # reloading has started, give it time to finish
                await ui_test.human_delay(100)

        self.assertTrue(material_reloaded)
        await self._golden_image_compare("test_reload.png")

        future_test = None
        if mdl_module_reload_sub:
            mdl_module_reload_sub.Revoke()
            mdl_module_reload_sub = None
