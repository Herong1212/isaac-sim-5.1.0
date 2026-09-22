

import carb.settings
from omni.kit.test import AsyncTestCase

from ..renderer_menu_container import BoolStringModel, FlashLightModel, LIGHTING_MODE, DisableMaterialModel, MATERIAL_MODE, ShadingModeModel, SHADING_MODE


class TestModel(AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.get_settings()
        super().setUp()

    async def test_bool_string_model(self):
        setting_path = "/app/test/boolStringModel"
        self._settings.set(setting_path, "default")
        model = BoolStringModel(setting_path)
        self.assertFalse(model.as_bool)
        self.assertEqual(model.as_string, "default")
        model.set_value(True)
        self.assertTrue(model.as_bool)
        self.assertEqual(model.as_bool, model.get_value())
        self.assertEqual(model.as_string, "disabled")
        self.assertTrue(self._settings.get(setting_path), model.as_string)

    async def test_flash_light_model(self):
        model = FlashLightModel(LIGHTING_MODE)
        try:
            model.set_value(True)
            self.assertTrue(self._settings.get("/rtx/useViewLightingMode"))
            model.set_value(False)
            self.assertFalse(self._settings.get("/rtx/useViewLightingMode"))
        finally:
            model.set_value(False)

    async def test_disable_material_model(self):
        model = DisableMaterialModel(MATERIAL_MODE)
        setting_path_wireframe_mode = "/rtx/wireframe/mode"
        saved_wireframe_mode = self._settings.get(setting_path_wireframe_mode)
        try:
            self._settings.set(setting_path_wireframe_mode, 1)
            model.set_value(True)
            self.assertEqual(self._settings.get("/rtx/debugMaterialType"), 0)
            self.assertEqual(self._settings.get(setting_path_wireframe_mode), 2)
            model.set_value(False)
            self.assertEqual(self._settings.get("/rtx/debugMaterialType"), -1)
            self.assertEqual(self._settings.get("/rtx/wireframe/mode"), 1)
        finally:
            model.set_value(False)
            self._settings.set(setting_path_wireframe_mode, saved_wireframe_mode)

    async def test_shading_mode_model(self):
        model = ShadingModeModel(SHADING_MODE, value_map=("default", "wireframe"))
        setting_path_debug_maetrial_type = "/rtx/debugMaterialType"
        saved_debug_material_type = self._settings.get(setting_path_debug_maetrial_type)
        try:
            self._settings.set(setting_path_debug_maetrial_type, 0)
            model.set_value(True)
            self.assertEqual(self._settings.get("/rtx/debugView/target"), "")
            self.assertEqual(self._settings.get("/rtx/wireframe/mode"), 2)
            model.set_value(False)
            self.assertEqual(self._settings.get("/rtx/wireframe/mode"), 0)
        finally:
            model.set_value(False)
            self._settings.set(setting_path_debug_maetrial_type, saved_debug_material_type)
