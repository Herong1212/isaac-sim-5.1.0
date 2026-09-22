# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['TestModels']

import carb
import omni.kit.test
from omni.kit.test import AsyncTestCase
import omni.kit.undo
import omni.ui as ui
import omni.usd
from pxr import UsdGeom

from ..model.setting_model import SettingModel
from ..model.usd_attribute_model import USDAttributeModel, USDBoolAttributeModel, USDIntAttributeModel, USDFloatAttributeModel, USDStringAttributeModel
from ..model.usd_metadata_model import USDMetadataModel
from ..model.reset_button import ResetHelper, ResetButton
from ..model.combobox_model import ComboBoxModel, SettingComboBoxModel
from ..model.list_model import ColorModel, SimpleListModel
from ..model.category_model import SimpleCategoryModel, CategoryStateItem, CategoryCustomItem, CategoryStatus


class TestModels(AsyncTestCase):
    async def setUp(self):
        self.usd_context_name = ''
        self.usd_context = omni.usd.get_context(self.usd_context_name)
        await self.usd_context.new_stage_async()
        self.stage = self.usd_context.get_stage()

        self.stage.SetDefaultPrim(UsdGeom.Xform.Define(self.stage, '/World').GetPrim())

    async def tearDown(self):
        self.usd_context = None
        self.stage = None

    def get_setting_path(self, setting):
        return f'/app/test/omni.kit.viewport.menubar.core/test_root/{setting}'

    async def test_setting_model_bool(self):
        setting = self.get_setting_path('bool_value')
        settings = carb.settings.get_settings()
        model = SettingModel(setting)

        self.assertEqual(model.path, setting)

        # Should start as None and False
        self.assertEqual(model.get_value_as_bool(), bool(settings.get(setting)))

        # Test model -> carb.setting
        model.set_value(True)
        self.assertEqual(model.get_value_as_bool(), settings.get(setting))

        model.set_value(False)
        self.assertEqual(model.get_value_as_bool(), settings.get(setting))

        # Test carb.setting -> model
        settings.set(setting, True)
        self.assertEqual(model.get_value_as_bool(), settings.get(setting))

        settings.set(setting, False)
        self.assertEqual(model.get_value_as_bool(), settings.get(setting))

        model.begin_edit()
        self.assertTrue(model._editing)  # noqa: PLW0212
        model.end_edit()
        self.assertFalse(model._editing)  # noqa: PLW0212

        model.destroy()

    async def test_setting_model_int(self):
        setting = self.get_setting_path('int_value')
        settings = carb.settings.get_settings()
        model = SettingModel(setting)

        # Test model -> carb.setting
        model.set_value(1)
        self.assertEqual(model.get_value_as_int(), settings.get(setting))

        model.set_value(2)
        self.assertEqual(model.get_value_as_int(), settings.get(setting))

        # Test carb.setting -> model
        settings.set(setting, 3)
        self.assertEqual(model.get_value_as_int(), settings.get(setting))

        settings.set(setting, 4)
        self.assertEqual(model.get_value_as_int(), settings.get(setting))

        model.destroy()

    async def test_setting_model_float(self):
        setting = self.get_setting_path('float_value')
        settings = carb.settings.get_settings()
        model = SettingModel(setting)

        # Test model -> carb.setting
        model.set_value(123.0)
        self.assertEqual(model.get_value_as_float(), settings.get(setting))

        model.set_value(456.0)
        self.assertEqual(model.get_value_as_float(), settings.get(setting))

        # Test carb.setting -> model
        settings.set(setting, 789.0)
        self.assertEqual(model.get_value_as_float(), settings.get(setting))

        settings.set(setting, 101112.0)
        self.assertEqual(model.get_value_as_float(), settings.get(setting))

        model.destroy()

    async def test_setting_model_string(self):
        setting = self.get_setting_path('string_value')
        settings = carb.settings.get_settings()
        model = SettingModel(setting)

        # Test model -> carb.setting
        model.set_value('A')
        self.assertEqual(model.get_value_as_string(), settings.get(setting))

        model.set_value('B')
        self.assertEqual(model.get_value_as_string(), settings.get(setting))

        # Test carb.setting -> model
        settings.set(setting, 'C')
        self.assertEqual(model.get_value_as_string(), settings.get(setting))

        settings.set(setting, 'D')
        self.assertEqual(model.get_value_as_string(), settings.get(setting))

        model.destroy()

    async def test_implicit_bool_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDAttributeModel(self.stage, prim.GetPath(), 'implicicit_bool')
        model.set_value(True)
        prop = prim.GetProperty('implicicit_bool')
        self.assertEqual(prop.Get(), True)

        model.set_value(False)
        self.assertEqual(prop.Get(), False)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

        prop.Set(True)
        self.assertEqual(model.get_value_as_bool(), True)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

        prop.Set(False)
        self.assertEqual(model.get_value_as_bool(), False)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

    async def test_implicit_int_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDAttributeModel(self.stage, prim.GetPath(), 'implicicit_int')
        model.set_value(1)
        prop = prim.GetProperty('implicicit_int')
        self.assertEqual(prop.Get(), 1)

        model.set_value(2)
        self.assertEqual(prop.Get(), 2)
        self.assertEqual(prop.Get(), model.get_value_as_int())

        prop.Set(3)
        self.assertEqual(model.get_value_as_int(), 3)
        self.assertEqual(prop.Get(), model.get_value_as_int())

        prop.Set(4)
        self.assertEqual(model.get_value_as_int(), 4)
        self.assertEqual(prop.Get(), model.get_value_as_int())

    async def test_implicit_float_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDAttributeModel(self.stage, prim.GetPath(), 'implicicit_float')
        model.set_value(123.4)
        prop = prim.GetProperty('implicicit_float')
        self.assertAlmostEqual(prop.Get(), 123.4, 2)

        model.set_value(234.5)
        self.assertAlmostEqual(prop.Get(), 234.5, 1)
        self.assertAlmostEqual(prop.Get(), model.get_value_as_float(), 2)

        prop.Set(345.6)
        self.assertAlmostEqual(model.get_value_as_float(), 345.6, 2)
        self.assertAlmostEqual(prop.Get(), model.get_value_as_float(), 2)

        prop.Set(456.7)
        self.assertAlmostEqual(model.get_value_as_float(), 456.7, 2)
        self.assertAlmostEqual(prop.Get(), model.get_value_as_float(), 2)

    async def test_implicit_string_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDAttributeModel(self.stage, prim.GetPath(), 'implicicit_string')
        model.set_value('A')
        prop = prim.GetProperty('implicicit_string')
        self.assertEqual(prop.Get(), 'A')

        model.set_value('B')
        self.assertEqual(prop.Get(), 'B')
        self.assertEqual(prop.Get(), model.get_value_as_string())

        prop.Set('C')
        self.assertEqual(model.get_value_as_string(), 'C')
        self.assertEqual(prop.Get(), model.get_value_as_string())

        prop.Set('D')
        self.assertEqual(model.get_value_as_string(), 'D')
        self.assertEqual(prop.Get(), model.get_value_as_string())

    async def test_explicit_bool_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDBoolAttributeModel(self.stage, prim.GetPath(), 'explicit_bool')
        model.set_value(True)
        prop = prim.GetProperty('explicit_bool')
        self.assertEqual(prop.Get(), True)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

        model.set_value(False)
        self.assertEqual(prop.Get(), False)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

        prop.Set(True)
        self.assertEqual(model.get_value_as_bool(), True)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

        prop.Set(False)
        self.assertEqual(model.get_value_as_bool(), False)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

        # Test undo works and collapses back to original value
        omni.kit.undo.undo()
        self.assertEqual(prop.Get(), True)
        self.assertEqual(prop.Get(), model.get_value_as_bool())

    async def test_explicit_int_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDIntAttributeModel(self.stage, prim.GetPath(), 'explicit_int')
        model.set_value(1)
        prop = prim.GetProperty('explicit_int')
        self.assertEqual(prop.Get(), 1)
        self.assertEqual(prop.Get(), model.get_value_as_int())

        model.set_value(2)
        self.assertEqual(prop.Get(), 2)
        self.assertEqual(prop.Get(), model.get_value_as_int())

        prop.Set(3)
        self.assertEqual(model.get_value_as_int(), 3)
        self.assertEqual(prop.Get(), model.get_value_as_int())

        prop.Set(4)
        self.assertEqual(model.get_value_as_int(), 4)
        self.assertEqual(prop.Get(), model.get_value_as_int())

        # Test undo works and collapses back to original value
        omni.kit.undo.undo()
        self.assertEqual(prop.Get(), 1)
        self.assertEqual(prop.Get(), model.get_value_as_int())

    async def test_explicit_float_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDFloatAttributeModel(self.stage, prim.GetPath(), 'explicit_float')
        model.set_value(123.4)
        prop = prim.GetProperty('explicit_float')
        self.assertAlmostEqual(prop.Get(), 123.4, 2)
        self.assertAlmostEqual(prop.Get(), model.get_value_as_float(), 2)

        model.set_value(234.5)
        self.assertAlmostEqual(prop.Get(), 234.5, 1)
        self.assertAlmostEqual(prop.Get(), model.get_value_as_float(), 2)

        prop.Set(345.6)
        self.assertAlmostEqual(model.get_value_as_float(), 345.6, 2)
        self.assertAlmostEqual(prop.Get(), model.get_value_as_float(), 2)

        prop.Set(456.7)
        self.assertAlmostEqual(model.get_value_as_float(), 456.7, 2)
        self.assertAlmostEqual(prop.Get(), model.get_value_as_float(), 2)

        # Test undo works and collapses back to original value
        omni.kit.undo.undo()
        self.assertAlmostEqual(prop.Get(), 123.4, 2)
        self.assertEqual(prop.Get(), model.get_value_as_float())

    async def test_explicit_string_attribute_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDStringAttributeModel(self.stage, prim.GetPath(), 'explicit_string')
        model.set_value('A')
        prop = prim.GetProperty('explicit_string')
        self.assertEqual(prop.Get(), 'A')
        self.assertEqual(prop.Get(), model.get_value_as_string())

        model.set_value('B')
        self.assertEqual(prop.Get(), 'B')
        self.assertEqual(prop.Get(), model.get_value_as_string())

        prop.Set('C')
        self.assertEqual(model.get_value_as_string(), 'C')
        self.assertEqual(prop.Get(), model.get_value_as_string())

        prop.Set('D')
        self.assertEqual(model.get_value_as_string(), 'D')
        self.assertEqual(prop.Get(), model.get_value_as_string())

        # Test undo works and collapses back to original value
        omni.kit.undo.undo()
        self.assertEqual(model.get_value_as_string(), 'A')
        self.assertEqual(prop.Get(), model.get_value_as_string())

    async def test_prim_metadata_model(self):
        prim = self.stage.GetPrimAtPath('/World')
        model = USDMetadataModel(self.stage, prim.GetPath(), 'active')

        model.set_value(True)
        self.assertEqual(prim.GetMetadata('active'), True)
        self.assertEqual(prim.GetMetadata('active'), model.get_value_as_bool())

        model = USDMetadataModel(self.stage, prim.GetPath(), 'instanceable')
        model.set_value(False)
        self.assertEqual(prim.GetMetadata('instanceable'), False)
        self.assertEqual(prim.GetMetadata('instanceable'), model.get_value_as_bool())

    async def test_reset_button(self):
        class SimpleResetHelper(ResetHelper):
            def __init__(self, default: bool) -> None:
                self.value = default
                self._default = default
                super().__init__()

            def get_default(self):
                return self._default

            def restore_default(self):
                self.value = self.get_default()

            def get_value(self):
                return self.value

        def on_reset():
            nonlocal reset
            reset = True

        reset = False
        true_helper = SimpleResetHelper(True)
        false_helper = SimpleResetHelper(False)
        reset_btn = ResetButton([true_helper], on_reset_fn=on_reset)
        reset_btn.add_setting_model(false_helper)
        self.assertFalse(reset_btn._reset_button.visible)  # noqa: PLW0212
        true_helper.value = False
        reset_btn.refresh()
        self.assertTrue(reset_btn._reset_button.visible)  # noqa: PLW0212
        reset_btn._restore_defaults()  # noqa: PLW0212
        self.assertFalse(reset_btn._reset_button.visible)  # noqa: PLW0212
        self.assertTrue(true_helper.value)
        self.assertTrue(reset)

    async def test_combobox_model(self):
        model = ComboBoxModel(["First", "Second"], current_value="First")
        self.assertEqual(model.current_index.as_int, 0)

        combobox_changed = False

        def on_model_changed(model):
            nonlocal combobox_changed
            combobox_changed = True

        sub = model.current_index.subscribe_value_changed_fn(on_model_changed)  # noqa: PLW0612
        model.current_index.set_value(1)
        try:
            self.assertTrue(combobox_changed)
            self.assertEqual(model.current_index.as_int, 1)
        finally:
            sub = None  # noqa: F841

    async def test_setting_combobox_model(self):
        setting_path = self.get_setting_path('combobox_value')
        settings = carb.settings.get_settings()
        settings.set(setting_path, "Second")
        model = SettingComboBoxModel(setting_path, ["First", "Second"])
        self.assertEqual(model.current_index.as_int, 1)

        model.current_index.set_value(0)
        self.assertEqual(settings.get(setting_path), "First")

        model.destroy()

    async def test_list_model(self):
        values = [ui.SimpleStringModel("model"), 0.5, 1, "text"]
        texts = ["model", "float", "int", "string"]
        model = SimpleListModel(values, texts=texts)

        self.assertEqual(model.get_item_value_model_count(), 1)
        items = model.get_item_children()
        self.assertEqual(len(items), 4)
        self.assertEqual(model.get_item_value_model(items[0], 0), values[0])
        self.assertEqual(model.get_item_value_model(items[1], 0).as_float, values[1])
        self.assertEqual(model.get_item_value_model(items[2], 0).as_int, values[2])
        self.assertEqual(model.get_item_value_model(items[3], 0).as_string, values[3])
        for i in range(4):
            self.assertEqual(items[i].model.as_string, texts[i])

        model.destroy()

    async def test_color_model(self):
        new_color = None

        def _on_color_changed(color):
            nonlocal new_color
            new_color = color

        colors = [0.1, 0.2, 0.3]
        default = [0, 0, 0]
        model = ColorModel(colors, default=default, on_color_changed_fn=_on_color_changed)
        self.assertEqual(model.colors, colors)

        colors.reverse()
        model.colors = colors
        self.assertEqual(model.colors, colors)
        self.assertEqual(new_color, colors)

        self.assertEqual(model.get_default(), default)
        self.assertEqual(model.get_value(), model.colors)
        model.restore_default()
        self.assertEqual(model.colors, default)

        model.destroy()

    async def test_category_model(self):
        setting_path = self.get_setting_path("category_state")
        settings = carb.settings.get_settings()
        settings.set(setting_path, True)
        model = SimpleCategoryModel(
            "Category Model Test",
            [
                CategoryStateItem("State Setting", setting_path=setting_path),
                CategoryStateItem("State Model", value_model=ui.SimpleBoolModel(True)),
                CategoryStateItem("State Empty"),
            ]
        )

        def _build_fn():
            pass  # pragma: no cover

        model.add_item(CategoryCustomItem("Custom", build_fn=_build_fn))

        collection_items = model.get_item_children(None)
        self.assertEqual(len(collection_items), 1)

        children = model.get_item_children(collection_items[0])
        self.assertEqual(len(children), 4)

        empty = model.get_item_children(children[0])
        self.assertEqual(len(empty), 0)

        empty = model.get_item_children(children[3])
        self.assertEqual(len(empty), 0)

        # Status
        root = model._root  # noqa: PLW0212
        self.assertTrue(children[0].checked)
        self.assertTrue(children[1].checked)
        self.assertFalse(children[2].checked)
        self.assertEqual(root.status, CategoryStatus.MIXED)

        children[2].checked = True
        self.assertEqual(root.status, CategoryStatus.ALL)

        root.status = CategoryStatus.EMPTY
        self.assertFalse(children[0].checked)
        self.assertFalse(children[1].checked)
        self.assertFalse(children[2].checked)

        root.status = CategoryStatus.ALL
        self.assertTrue(children[0].checked)
        self.assertTrue(children[1].checked)
        self.assertTrue(children[2].checked)

        model.destroy()
