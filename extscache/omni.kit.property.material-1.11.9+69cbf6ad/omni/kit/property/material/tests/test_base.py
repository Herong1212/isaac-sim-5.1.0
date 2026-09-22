import os
from pathlib import Path
from typing import List

import carb
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.test_suite.helpers import get_test_data_path, open_stage, select_prims, wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf, Usd, UsdShade


class MaterialPropertiesTestBase(OmniUiTest):
    async def setUp(self) -> None:
        import omni.kit.window.property

        await super().setUp()

        self._settings = carb.settings.get_settings()

        self._usd_context = omni.usd.get_context()
        await self._usd_context.new_stage_async()
        self._stage = self._usd_context.get_stage()

        test_data_dir = Path(get_test_data_path(__name__))
        self._usd_dir = test_data_dir / "usd"
        self._golden_img_dir = test_data_dir / "golden_img"
        self._icons_dir = test_data_dir / "icons"
        self._mdl_dir = test_data_dir / "mdl"
        self._textures_dir = test_data_dir / "textures"

        omni.kit.window.property.managed_frame.reset_collapsed_state()

        self._window = omni.kit.window.property.get_window()._window

    async def tearDown(self):
        await super().tearDown()
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await wait_stage_loading()

    async def _load_scene(self, scene_file_path: str) -> None:

        await open_stage(scene_file_path, self._usd_context)
        await wait_stage_loading()
        self._stage = self._usd_context.get_stage()

    def _get_scene_path(self, file_name: str) -> str:

        path = str(self._usd_dir / file_name)
        self.assertTrue(os.path.exists(path))
        return path

    def _get_mdl_path(self, file_name: str) -> str:

        path = str(self._mdl_dir / file_name)
        self.assertTrue(os.path.exists(path))
        return path

    def _get_texture_path(self, file_name: str) -> str:

        path = str(self._textures_dir / file_name)
        self.assertTrue(os.path.exists(path))
        return path

    async def _dock_test_window(self, width: int = 256, height: int = 256) -> None:

        await self.docked_test_window(
            window=self._window,
            width=width,
            height=height,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

    async def _golden_image_compare(self, file_name: str, threshold=None) -> None:

        path = str(self._golden_img_dir / file_name)
        self.assertTrue(os.path.exists(path))

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name=file_name, threshold=threshold, zero_mouse=True
        )

    async def _select_prims(self, prim_paths: List[Sdf.Path]) -> None:
        await select_prims(prim_paths)
        await wait_stage_loading()
        await ui_test.human_delay(50)

    def _get_prim_at_path(self, path: Sdf.Path) -> Usd.Prim:
        prim = self._stage.GetPrimAtPath(path)
        self.assertTrue(isinstance(prim, Usd.Prim) and prim.IsValid())
        return prim

    def _get_attribute_at_path(self, path: Sdf.Path) -> Usd.Prim:
        attribute = self._stage.GetAttributeAtPath(path)
        self.assertTrue(isinstance(attribute, Usd.Attribute) and attribute.IsValid())
        return attribute

    def _get_bound_material(self, prim: Usd.Prim, expected_res: bool = True):
        self.assertTrue(isinstance(prim, Usd.Prim) and prim.IsValid())

        api = UsdShade.MaterialBindingAPI(prim)
        mat, rel = api.ComputeBoundMaterial()

        if expected_res:
            self.assertTrue(mat.GetPrim().IsValid())
        else:
            self.assertFalse(mat.GetPrim().IsValid())

        return (mat, rel)

    def _get_shader_from_material(self, prim: Usd.Prim) -> Usd.Prim:
        self.assertTrue(prim.IsA(UsdShade.Material))
        shader = omni.usd.get_shader_from_material(prim, False)
        self.assertTrue(bool(shader))
        return shader

    def _get_attribute_from_model(self, model: UsdAttributeModel) -> Usd.Attribute:
        """
        Get the underlying Usd.Attribute that drives the widget model.
        """
        attribute_paths = model.get_attribute_paths()
        self.assertTrue(len(attribute_paths) == 1)
        attribute_path = str(attribute_paths[0])
        attribute = self._get_attribute_at_path(attribute_path)
        return attribute
