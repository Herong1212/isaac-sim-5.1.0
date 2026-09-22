## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.ui as ui
import omni.kit.app

from pathlib import Path
from omni.ui.tests.test_base import OmniUiTest
from unittest.mock import Mock
from ..form_dialog import FormDialog, FormWidget

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestFormDialog(OmniUiTest):
    """Testing FormDialog"""
    async def setUp(self):
        self._field_defs = [
            FormDialog.FieldDef("string", "String:  ", ui.StringField, "default"),
            FormDialog.FieldDef("int", "Integer:  ", ui.IntField, 1),
            FormDialog.FieldDef("float", "Float:  ", ui.FloatField, 2.0),
            FormDialog.FieldDef(
                "tuple", "Tuple:  ", lambda **kwargs: ui.MultiFloatField(column_count=3, h_spacing=2, **kwargs), None
            ),
            FormDialog.FieldDef("slider", "Slider:  ", lambda **kwargs: ui.FloatSlider(min=0, max=10, **kwargs), 3.5),
            FormDialog.FieldDef("bool", "Boolean:  ", ui.CheckBox, True),
        ]
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("images")

    async def tearDown(self):
        pass

    async def test_ui_layout(self):
        """Testing that the UI layout looks consistent"""
        window = await self.create_test_window()
        with window.frame:
            FormWidget(
                message="Test fields:",
                field_defs=self._field_defs,
            )

        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="form_dialog.png")
        window.destroy()
        # wait one frame so that widget is destroyed
        await omni.kit.app.get_app().next_update_async()

    async def test_okay_handler(self):
        """Test clicking okay button triggers the callback"""
        mock_okay_handler = Mock()
        under_test = FormDialog(
            message="Test fields:",
            field_defs=self._field_defs,
            ok_handler=mock_okay_handler,
        )
        under_test.show()
        under_test._on_okay()
        await omni.kit.app.get_app().next_update_async()
        mock_okay_handler.assert_called_once()
        under_test.destroy()

    async def test_get_field_value(self):
        """Test that get_value returns the value of the named field"""
        under_test = FormDialog(
            message="Test fields:",
            field_defs=self._field_defs,
        )
        for field in self._field_defs:
            name, label, _, default_value, focused = field
            self.assertEqual(default_value, under_test.get_value(name))
        under_test.destroy()

    async def test_reset_dialog_value(self):
        """Test reset dialog value"""
        under_test = FormDialog(
            message="Test fields:",
            field_defs=self._field_defs,
        )
        string_field = under_test.get_field("string")
        string_field.model.set_value("test")
        self.assertEqual(under_test.get_value("string"), "test")
        under_test.reset_values()
        self.assertEqual(under_test.get_value("string"), "default")
        under_test.destroy()