# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pathlib import Path
from unittest.mock import Mock

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
import usdrt
from omni.kit import ui_test
from omni.kit.property.adapter.fabric import convert_usdrt_to_usd
from omni.ui.tests.test_base import OmniUiTest
from pxr import Gf, Kind, Sdf, UsdGeom, UsdShade

from ..usd_attribute_model import GfVecAttributeSingleChannelModel


class TestWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        from omni.kit.test_suite.helpers import arrange_windows, get_test_data_path, open_stage

        await super().setUp()

        await arrange_windows("Stage", 200)

        self._golden_img_dir = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests/golden_img"
        )
        self._usd_path = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests/usd"
        )

        import omni.kit.window.property as p
        from omni.kit.property.usd.usd_attribute_widget import UsdPropertiesWidget

        self._w = p.get_window()

        INT32_MIN = -2147483648
        INT32_MAX = 2147483647

        INT64_MIN = -9223372036854775808
        INT64_MAX = 9223372036854775807

        HALF_LOWEST = -65504.0
        HALF_MAX = 65504.0

        # In double precision
        FLT_LOWEST = -3.4028234663852886e38
        FLT_MIN = 1.1754943508222875e-38
        FLT_MAX = 3.4028234663852886e38
        FLT_EPS = 1.1920928955078125e-07

        DBL_LOWEST = -1.7976931348623158e308
        DBL_MIN = 2.2250738585072014e-308
        DBL_MAX = 1.7976931348623158e308
        DBL_EPS = 2.2204460492503131e-016

        # (attr_name, attr_type, value_0, value_1, value_2, expected_model_count)
        self._test_data = [
            ("bool_attr", Sdf.ValueTypeNames.Bool, True, False, True, 1),
            ("uchar_attr", Sdf.ValueTypeNames.UChar, ord("o"), ord("v"), ord("k"), 1),
            ("int_attr", Sdf.ValueTypeNames.Int, -1, 0, 1, 1),
            ("uint_attr", Sdf.ValueTypeNames.UInt, 1, 2, 3, 1),
            ("int64_attr", Sdf.ValueTypeNames.Int64, INT64_MIN, 0, INT64_MAX, 1),
            (
                "uint64_attr",
                Sdf.ValueTypeNames.UInt64,
                0,
                2,
                INT64_MAX,
                1,
            ),  # omni.ui only supports int64 range, thus uint max won't work
            (
                "half_attr",
                Sdf.ValueTypeNames.Half,
                HALF_LOWEST,
                0.333251953125,
                HALF_MAX,
                1,
            ),  # half is stored as double in model
            (
                "float_attr",
                Sdf.ValueTypeNames.Float,
                FLT_MIN,
                FLT_MAX,
                FLT_EPS,
                1,
            ),  # Float is stored as double in model
            ("double_attr", Sdf.ValueTypeNames.Double, DBL_MIN, DBL_MAX, DBL_EPS, 1),
            ("timdcode_attr", Sdf.ValueTypeNames.TimeCode, Sdf.TimeCode(10), Sdf.TimeCode(20), Sdf.TimeCode(30), 1),
            ("string_attr", Sdf.ValueTypeNames.String, "This", "is a", "string", 1),
            (
                "token_attr",
                Sdf.ValueTypeNames.Token,
                Kind.Tokens.subcomponent,
                Kind.Tokens.component,
                Kind.Tokens.group,
                1,
            ),
            ("asset_attr", Sdf.ValueTypeNames.Asset, "/This", "/is/an", "/asset", 1),
            ("asset_attr_noedit", Sdf.ValueTypeNames.Asset, "/This", "/is/an", "/asset", 1),
            (
                "int2_attr",
                Sdf.ValueTypeNames.Int2,
                Gf.Vec2i(INT32_MIN, INT32_MAX),
                Gf.Vec2i(INT32_MAX, INT32_MIN),
                Gf.Vec2i(INT32_MIN, INT32_MAX),
                2 + 1,  # Vector has one additional model for label context menu
            ),
            (
                "int3_attr",
                Sdf.ValueTypeNames.Int3,
                Gf.Vec3i(INT32_MIN, INT32_MAX, INT32_MIN),
                Gf.Vec3i(INT32_MAX, INT32_MIN, INT32_MAX),
                Gf.Vec3i(INT32_MIN, INT32_MAX, INT32_MIN),
                3 + 1,
            ),
            (
                "int4_attr",
                Sdf.ValueTypeNames.Int4,
                Gf.Vec4i(INT32_MIN, INT32_MAX, INT32_MIN, INT32_MAX),
                Gf.Vec4i(INT32_MAX, INT32_MIN, INT32_MAX, INT32_MIN),
                Gf.Vec4i(INT32_MIN, INT32_MAX, INT32_MIN, INT32_MAX),
                4 + 1,
            ),
            (
                "half2_attr",
                Sdf.ValueTypeNames.Half2,
                Gf.Vec2h(HALF_LOWEST, HALF_MAX),
                Gf.Vec2h(HALF_MAX, HALF_LOWEST),
                Gf.Vec2h(HALF_LOWEST, HALF_MAX),
                2 + 1,
            ),
            (
                "half3_attr",
                Sdf.ValueTypeNames.Half3,
                Gf.Vec3h(HALF_LOWEST, HALF_MAX, HALF_LOWEST),
                Gf.Vec3h(HALF_MAX, HALF_LOWEST, HALF_MAX),
                Gf.Vec3h(HALF_LOWEST, HALF_MAX, HALF_LOWEST),
                3 + 1,
            ),
            (
                "half4_attr",
                Sdf.ValueTypeNames.Half4,
                Gf.Vec4h(HALF_LOWEST, HALF_MAX, HALF_LOWEST, HALF_MAX),
                Gf.Vec4h(HALF_MAX, HALF_LOWEST, HALF_LOWEST, HALF_MAX),
                Gf.Vec4h(HALF_LOWEST, HALF_MAX, HALF_LOWEST, HALF_MAX),
                4 + 1,
            ),
            (
                "float2_attr",
                Sdf.ValueTypeNames.Float2,
                Gf.Vec2f(FLT_LOWEST, FLT_MAX),
                Gf.Vec2f(FLT_MAX, FLT_LOWEST),
                Gf.Vec2f(FLT_MAX, FLT_MAX),
                2 + 1,
            ),
            (
                "float3_attr",
                Sdf.ValueTypeNames.Float3,
                Gf.Vec3f(FLT_LOWEST, FLT_MAX, FLT_LOWEST),
                Gf.Vec3f(FLT_MAX, FLT_LOWEST, FLT_MAX),
                Gf.Vec3f(FLT_MAX, FLT_MAX, FLT_MAX),
                3 + 1,
            ),
            (
                "float4_attr",
                Sdf.ValueTypeNames.Float4,
                Gf.Vec4f(FLT_LOWEST, FLT_MAX, FLT_LOWEST, FLT_MAX),
                Gf.Vec4f(FLT_MAX, FLT_LOWEST, FLT_MAX, FLT_LOWEST),
                Gf.Vec4f(FLT_MAX, FLT_MAX, FLT_MAX, FLT_MAX),
                4 + 1,
            ),
            (
                "double2_attr",
                Sdf.ValueTypeNames.Double2,
                Gf.Vec2d(DBL_LOWEST, DBL_MAX),
                Gf.Vec2d(DBL_MAX, DBL_LOWEST),
                Gf.Vec2d(DBL_MAX, DBL_MAX),
                2 + 1,
            ),
            (
                "double3_attr",
                Sdf.ValueTypeNames.Double3,
                Gf.Vec3d(DBL_LOWEST, DBL_MAX, DBL_LOWEST),
                Gf.Vec3d(DBL_MAX, DBL_LOWEST, DBL_MAX),
                Gf.Vec3d(DBL_MAX, DBL_MAX, DBL_MAX),
                3 + 1,
            ),
            (
                "double4_attr",
                Sdf.ValueTypeNames.Double4,
                Gf.Vec4d(DBL_LOWEST, DBL_MAX, DBL_LOWEST, DBL_MAX),
                Gf.Vec4d(DBL_MAX, DBL_LOWEST, DBL_MAX, DBL_LOWEST),
                Gf.Vec4d(DBL_MAX, DBL_MAX, DBL_MAX, DBL_MAX),
                4 + 1,
            ),
            (
                "point3h_attr",
                Sdf.ValueTypeNames.Point3h,
                Gf.Vec3h(HALF_LOWEST, HALF_MAX, HALF_LOWEST),
                Gf.Vec3h(HALF_MAX, HALF_LOWEST, HALF_MAX),
                Gf.Vec3h(HALF_LOWEST, HALF_MAX, HALF_LOWEST),
                3 + 1,
            ),
            (
                "point3f_attr",
                Sdf.ValueTypeNames.Point3f,
                Gf.Vec3f(FLT_LOWEST, FLT_MAX, FLT_LOWEST),
                Gf.Vec3f(FLT_MAX, FLT_LOWEST, FLT_MAX),
                Gf.Vec3f(FLT_MAX, FLT_MAX, FLT_MAX),
                3 + 1,
            ),
            (
                "point3d_attr",
                Sdf.ValueTypeNames.Point3d,
                Gf.Vec3d(DBL_LOWEST, DBL_MAX, DBL_LOWEST),
                Gf.Vec3d(DBL_MAX, DBL_LOWEST, DBL_MAX),
                Gf.Vec3d(DBL_MAX, DBL_MAX, DBL_MAX),
                3 + 1,
            ),
            (
                "vector3h_attr",
                Sdf.ValueTypeNames.Vector3h,
                Gf.Vec3h(HALF_LOWEST, HALF_MAX, HALF_LOWEST),
                Gf.Vec3h(HALF_MAX, HALF_LOWEST, HALF_MAX),
                Gf.Vec3h(HALF_LOWEST, HALF_MAX, HALF_LOWEST),
                3 + 1,
            ),
            (
                "vector3f_attr",
                Sdf.ValueTypeNames.Vector3f,
                Gf.Vec3f(FLT_LOWEST, FLT_MAX, FLT_LOWEST),
                Gf.Vec3f(FLT_MAX, FLT_LOWEST, FLT_MAX),
                Gf.Vec3f(FLT_MAX, FLT_MAX, FLT_MAX),
                3 + 1,
            ),
            (
                "vector3d_attr",
                Sdf.ValueTypeNames.Vector3d,
                Gf.Vec3d(DBL_LOWEST, DBL_MAX, DBL_LOWEST),
                Gf.Vec3d(DBL_MAX, DBL_LOWEST, DBL_MAX),
                Gf.Vec3d(DBL_MAX, DBL_MAX, DBL_MAX),
                3 + 1,
            ),
            (
                "normal3h_attr",
                Sdf.ValueTypeNames.Normal3h,
                Gf.Vec3h(1.0, 0.0, 0.0),
                Gf.Vec3h(0.0, 1.0, 0.0),
                Gf.Vec3h(0.0, 0.0, 1.0),
                3 + 1,
            ),
            (
                "normal3f_attr",
                Sdf.ValueTypeNames.Normal3f,
                Gf.Vec3f(1.0, 0.0, 0.0),
                Gf.Vec3f(0.0, 1.0, 0.0),
                Gf.Vec3f(0.0, 0.0, 1.0),
                3 + 1,
            ),
            (
                "normal3d_attr",
                Sdf.ValueTypeNames.Normal3d,
                Gf.Vec3d(1.0, 0.0, 0.0),
                Gf.Vec3d(0.0, 1.0, 0.0),
                Gf.Vec3d(0.0, 0.0, 1.0),
                3 + 1,
            ),
            (
                "color3h_attr",
                Sdf.ValueTypeNames.Color3h,
                Gf.Vec3h(1.0, 0.0, 0.0),
                Gf.Vec3h(0.0, 1.0, 0.0),
                Gf.Vec3h(0.0, 0.0, 1.0),
                3 + 1,  # Color attr has one model per channel + one model for the color picker
            ),
            (
                "color3f_attr",
                Sdf.ValueTypeNames.Color3f,
                Gf.Vec3f(1.0, 0.0, 0.0),
                Gf.Vec3f(0.0, 1.0, 0.0),
                Gf.Vec3f(0.0, 0.0, 1.0),
                3 + 1,
            ),
            (
                "color3d_attr",
                Sdf.ValueTypeNames.Color3d,
                Gf.Vec3d(1.0, 0.0, 0.0),
                Gf.Vec3d(0.0, 1.0, 0.0),
                Gf.Vec3d(0.0, 0.0, 1.0),
                3 + 1,
            ),
            (
                "color4h_attr",
                Sdf.ValueTypeNames.Color4h,
                Gf.Vec4h(1.0, 0.0, 0.0, 1.0),
                Gf.Vec4h(0.0, 1.0, 0.0, 1.0),
                Gf.Vec4h(0.0, 0.0, 1.0, 1.0),
                4 + 1,
            ),
            (
                "color4f_attr",
                Sdf.ValueTypeNames.Color4f,
                Gf.Vec4f(1.0, 0.0, 0.0, 1.0),
                Gf.Vec4f(0.0, 1.0, 0.0, 1.0),
                Gf.Vec4f(0.0, 0.0, 1.0, 1.0),
                4 + 1,
            ),
            (
                "color4d_attr",
                Sdf.ValueTypeNames.Color4d,
                Gf.Vec4d(1.0, 0.0, 0.0, 1.0),
                Gf.Vec4d(0.0, 1.0, 0.0, 1.0),
                Gf.Vec4d(0.0, 0.0, 1.0, 1.0),
                4 + 1,
            ),
            ("quath_attr", Sdf.ValueTypeNames.Quath, Gf.Quath(-1), Gf.Quath(0), Gf.Quath(1), 1),
            ("quatf_attr", Sdf.ValueTypeNames.Quatf, Gf.Quatf(-1), Gf.Quatf(0), Gf.Quatf(1), 1),
            ("quatd_attr", Sdf.ValueTypeNames.Quatd, Gf.Quatd(-1), Gf.Quatd(0), Gf.Quatd(1), 1),
            ("matrix2d_attr", Sdf.ValueTypeNames.Matrix2d, Gf.Matrix2d(-1), Gf.Matrix2d(0), Gf.Matrix2d(1), 1),
            ("matrix3d_attr", Sdf.ValueTypeNames.Matrix3d, Gf.Matrix3d(-1), Gf.Matrix3d(0), Gf.Matrix3d(1), 1),
            ("matrix4d_attr", Sdf.ValueTypeNames.Matrix4d, Gf.Matrix4d(-1), Gf.Matrix4d(0), Gf.Matrix4d(1), 1),
            ("frame4d_attr", Sdf.ValueTypeNames.Frame4d, Gf.Matrix4d(-1), Gf.Matrix4d(0), Gf.Matrix4d(1), 1),
            (
                "texCoord2f_attr",
                Sdf.ValueTypeNames.TexCoord2f,
                Gf.Vec2f(1.0, 0.0),
                Gf.Vec2f(0.0, 1.0),
                Gf.Vec2f(1.0, 1.0),
                2 + 1,
            ),
            (
                "texCoord2d_attr",
                Sdf.ValueTypeNames.TexCoord2d,
                Gf.Vec2d(1.0, 0.0),
                Gf.Vec2d(0.0, 1.0),
                Gf.Vec2d(1.0, 1.0),
                2 + 1,
            ),
            (
                "texCoord2h_attr",
                Sdf.ValueTypeNames.TexCoord2h,
                Gf.Vec2h(1.0, 0.0),
                Gf.Vec2h(0.0, 1.0),
                Gf.Vec2h(1.0, 1.0),
                2 + 1,
            ),
            (
                "texCoord3f_attr",
                Sdf.ValueTypeNames.TexCoord3f,
                Gf.Vec3f(1.0, 0.0, 1.0),
                Gf.Vec3f(0.0, 1.0, 0.0),
                Gf.Vec3f(1.0, 1.0, 1.0),
                3 + 1,
            ),
            (
                "texCoord3d_attr",
                Sdf.ValueTypeNames.TexCoord3d,
                Gf.Vec3d(1.0, 0.0, 1.0),
                Gf.Vec3d(0.0, 1.0, 0.0),
                Gf.Vec3d(1.0, 1.0, 1.0),
                3 + 1,
            ),
            (
                "texCoord3h_attr",
                Sdf.ValueTypeNames.TexCoord3h,
                Gf.Vec3h(1.0, 0.0, 1.0),
                Gf.Vec3h(0.0, 1.0, 0.0),
                Gf.Vec3h(1.0, 1.0, 1.0),
                3 + 1,
            ),
            # Add array types
            (
                "asset_array_attr",
                Sdf.ValueTypeNames.AssetArray,
                Sdf.AssetPathArray(2, [Sdf.AssetPath("foo.ext"), Sdf.AssetPath("textures/granite_a_mask.png")]),
                Sdf.AssetPathArray(),
                Sdf.AssetPathArray(3, [Sdf.AssetPath("foo.ext"), Sdf.AssetPath("bar.ext"), Sdf.AssetPath("baz.ext")]),
                1,
            ),
            (
                "asset_array_attr_noedit",
                Sdf.ValueTypeNames.AssetArray,
                Sdf.AssetPathArray(2, [Sdf.AssetPath("foo.ext"), Sdf.AssetPath("textures/granite_a_mask.png")]),
                Sdf.AssetPathArray(),
                Sdf.AssetPathArray(3, [Sdf.AssetPath("foo.ext"), Sdf.AssetPath("bar.ext"), Sdf.AssetPath("baz.ext")]),
                1,
            ),
        ]

        from omni.kit.property.usd.usd_property_widget_builder import SdfAssetPathDelegate

        class SpecialAssetPathDelegate(SdfAssetPathDelegate):
            pass

        class EditButtonTestWidget(UsdPropertiesWidget):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.edit_path = None

            def get_additional_kwargs(self, ui_attr):

                if ui_attr.prop_name in ["asset_array_attr", "asset_attr"]:

                    def edit_entry(sdfpath):
                        self.edit_path = sdfpath

                    return None, {"on_edit_fn": edit_entry, "delegate_cls": SpecialAssetPathDelegate}
                return None, None

        self._test_widget = EditButtonTestWidget(title="Test USD Properties", collapsed=False, enable_adapter=True)

        self._w.register_widget("prim", "test_raw_attribute", self._test_widget)
        self._usd_context = omni.usd.get_context()

        # open an actual scene instead of creating a new one so we can test
        # path widgets referencing files using relative paths.
        await open_stage(get_test_data_path(__name__, "usd/empty.usda"))

        self._stage = self._usd_context.get_stage()
        self._test_prim = self._stage.DefinePrim("/TestPrim")
        self._usd_context.get_selection().set_selected_prim_paths(["/TestPrim"], True)

        await ui_test.human_delay(10)

    # After running each test
    async def tearDown(self):
        self._usd_context.get_selection().set_selected_prim_paths([], False)
        await ui_test.human_delay()
        await self._usd_context.close_stage_async()

        self._w.unregister_widget("prim", "test_raw_attribute")
        self._test_widget = None
        self._test_prim = None
        self._stage = None

        await super().tearDown()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    # This tests read/write between USD attribute model and USD data
    async def test_attribute_model(self):

        usdrt_classes = (
            usdrt.Sdf.AssetPath,
            usdrt.Gf.Vec2i,
            usdrt.Gf.Vec2h,
            usdrt.Gf.Vec2f,
            usdrt.Gf.Vec2d,
            usdrt.Gf.Vec3i,
            usdrt.Gf.Vec3h,
            usdrt.Gf.Vec3f,
            usdrt.Gf.Vec3d,
            usdrt.Gf.Vec4i,
            usdrt.Gf.Vec4h,
            usdrt.Gf.Vec4f,
            usdrt.Gf.Vec4d,
            usdrt.Gf.Quath,
            usdrt.Gf.Quatf,
            usdrt.Gf.Quatd,
            usdrt.Gf.Matrix2f,
            usdrt.Gf.Matrix2d,
            usdrt.Gf.Matrix3f,
            usdrt.Gf.Matrix3d,
            usdrt.Gf.Matrix4f,
            usdrt.Gf.Matrix4d,
        )

        def verify_model_value(value_idx: int):
            models = self._test_widget._models
            for attr_data in self._test_data:
                attr_path = prim_path.AppendProperty(attr_data[0])
                attr_model_list = models.get(attr_path, None)
                self.assertNotEqual(attr_model_list, None, msg=attr_data[0])
                self.assertEqual(len(attr_model_list), attr_data[5], msg=attr_data[0])
                for model in attr_model_list:
                    if isinstance(model.get_value(), usdrt_classes):
                        usd_value = convert_usdrt_to_usd(model.get_value())
                        self.assertEqual(usd_value, attr_data[value_idx], msg=attr_data[0])
                    elif isinstance(model.get_value(), usdrt.Vt.AssetArray):
                        usd_value = convert_usdrt_to_usd(model.get_value())
                        self.assertEqual(str(usd_value), str(attr_data[value_idx]), msg=attr_data[0])
                    elif isinstance(attr_data[value_idx], Sdf.AssetPathArray):
                        # Comparison doesn't work when model.get_value() has a resolvable path
                        # as the AssetPath.resolvedPath member variable gets filled in (and is
                        # just an empty string in attr_data[value_idx]), so we're comparing
                        # after converting to a string intead:
                        self.assertEqual(str(model.get_value()), str(attr_data[value_idx]), msg=attr_data[0])
                    else:
                        self.assertEqual(model.get_value(), attr_data[value_idx], msg=attr_data[0])

        # Test Resync event
        for attr_data in self._test_data:
            attr = self._test_prim.CreateAttribute(attr_data[0], attr_data[1])
            self.assertTrue(attr is not None)
            attr.Set(attr_data[2])

        # Wait for a frame for widget to process all pending changes
        await omni.kit.app.get_app().next_update_async()

        # Need to wait for an additional frame for omni.ui rebuild to take effect
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        prim_path = self._test_prim.GetPrimPath()

        # Verify the model has fetched the correct data
        verify_model_value(2)

        # Test info changed only event
        for attr_data in self._test_data:
            attr = self._test_prim.GetAttribute(attr_data[0])
            self.assertTrue(attr is not None)
            attr.Set(attr_data[3])

        # Wait for a frame for widget to process all pending changes
        await omni.kit.app.get_app().next_update_async()

        # Verify the model has fetched the correct data
        verify_model_value(3)

        # Test set value to model
        # TODO ideally new value should be set via UI, and have UI update the model instead of setting model directly,
        # it is less useful of a test to write to model directly from user-interaction perspective.
        # Update the test once we can locate UI element and emulate input.
        models = self._test_widget._models
        mock_item_changed_callback = Mock()
        for attr_data in self._test_data:
            attr_path = prim_path.AppendProperty(attr_data[0])
            attr_model_list = models.get(attr_path, None)
            for i, model in enumerate(attr_model_list):
                if isinstance(model, ui.AbstractItemModel):
                    model.add_item_changed_fn(mock_item_changed_callback)
                if isinstance(model, GfVecAttributeSingleChannelModel):
                    model.set_value(attr_data[4][i])
                    # Wait for a frame for the rest of the channel model to sync the change
                    await omni.kit.app.get_app().next_update_async()
                else:
                    model.set_value(attr_data[4])
                await omni.kit.app.get_app().next_update_async()
                if isinstance(model, ui.AbstractItemModel):
                    mock_item_changed_callback.assert_called()
                    mock_item_changed_callback.reset()

        # verify value updated in USD
        for attr_data in self._test_data:
            attr = self._test_prim.GetAttribute(attr_data[0])
            self.assertNotEqual(attr, None)
            self.assertEqual(attr.Get(), attr_data[4], msg=attr_data[0])

    async def _test_attribute_ui_base(self, start, end, filter_name="", block_devices=True):
        await self.docked_test_window(
            window=self._w._window,
            width=800,
            height=1050,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
            block_devices=block_devices,
        )

        # Populate USD attributes
        for attr_data in self._test_data[start:end]:
            attr = self._test_prim.CreateAttribute(attr_data[0], attr_data[1])
            self.assertTrue(attr is not None)
            attr.Set(attr_data[2])

        if filter_name:
            self._w._searchfield._search_field.model.as_string = filter_name
            self._w._searchfield._set_in_searching(True)

        # Wait for a frame for widget to process all pending changes
        await omni.kit.app.get_app().next_update_async()

        # Need to wait for an additional frame for omni.ui rebuild to take effect
        await omni.kit.app.get_app().next_update_async()

    async def test_fabric_attribute_ui(self):
        await self.docked_test_window(
            window=self._w._window,
            width=800,
            height=1050,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        from omni.kit import ui_test

        omni.usd.get_context().get_selection().set_selected_prim_paths([], True)
        await ui_test.human_delay(2)

        # Create Fabric attributes
        stage_id = omni.usd.get_context().get_stage_id()
        stage_rt = usdrt.Usd.Stage.Attach(stage_id) if stage_id >= 0 else None
        self.assertTrue(stage_rt is not None)
        prim_fabric = stage_rt.GetPrimAtPath("/TestPrim")
        attr = prim_fabric.CreateAttribute("test_fabric", usdrt.Sdf.ValueTypeNames.Bool, True)
        self.assertTrue(attr is not None)
        attr.Set(False)

        omni.usd.get_context().get_selection().set_selected_prim_paths(["/TestPrim"], True)
        await ui_test.human_delay(10)

        fabric_widget = ui_test.find("Property//Frame/**/.identifier=='bool_test_fabric'")
        self.assertIsNotNone(fabric_widget)

        self.assertEqual(fabric_widget.model.get_value_as_bool(), False)

        # Change Fabric value
        attr.Set(True)
        await ui_test.human_delay(10)
        self.assertEqual(fabric_widget.model.get_value_as_bool(), True)

        await self.finalize_test_no_image()

    async def test_mixed_adapter_attribute_ui(self):
        await self.docked_test_window(
            window=self._w._window,
            width=800,
            height=1050,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
            block_devices=False,
        )

        from omni.kit import ui_test

        omni.usd.get_context().get_selection().set_selected_prim_paths([], True)
        await ui_test.human_delay(2)

        # Create Usd attribute
        stage_usd = omni.usd.get_context().get_stage()
        self.assertTrue(stage_usd is not None)

        value_1 = 1
        prim_usd = stage_usd.GetPrimAtPath("/TestPrim")
        attr_usd = prim_usd.CreateAttribute("test_mixed", Sdf.ValueTypeNames.Int)
        self.assertTrue(attr_usd is not None)
        attr_usd.Set(value_1)

        # Get Fabric attributes
        stage_id = omni.usd.get_context().get_stage_id()
        stage_rt = usdrt.Usd.Stage.Attach(stage_id) if stage_id >= 0 else None
        self.assertTrue(stage_rt is not None)

        prim_fabric = stage_rt.GetPrimAtPath("/TestPrim")
        attr_fabric = prim_fabric.GetAttribute("test_mixed")
        self.assertTrue(attr_fabric is not None)

        omni.usd.get_context().get_selection().set_selected_prim_paths(["/TestPrim"], True)
        await ui_test.human_delay(10)

        test_widget = ui_test.find("Property//Frame/**/.identifier=='integer_slider_test_mixed'")
        self.assertIsNotNone(test_widget)
        self.assertEqual(test_widget.model.get_value_as_int(), value_1)
        await ui_test.human_delay(10)

        # click default checkbox
        await ui_test.find("Property//Frame/**/.identifier=='control_state_test_mixed'").click()
        await ui_test.human_delay(10)
        self.assertEqual(attr_fabric.Get(), 0)
        self.assertEqual(attr_usd.Get(), 0)

        await self.finalize_test_no_image()

    # Capture screenshot of property window and compare with golden image (1/3)
    # The property list is too long and Window limits max window size base on primary monitor height,
    # the test has to be split into 3, each tests 1/3 of the attributes.
    async def test_attribute_ui_1(self):
        sublist_length = len(self._test_data) // 3
        await self._test_attribute_ui_base(0, sublist_length)

        allowed_tokens = ["a", "b", "c"]
        attr_a = self._test_prim.CreateAttribute("token_attr_allowedTokens", Sdf.ValueTypeNames.Token)
        attr_a.SetMetadata("allowedTokens", allowed_tokens)
        attr_a.Set(allowed_tokens[1])

        options = "x:0|y:1|z:2"
        attr_b = self._test_prim.CreateAttribute("int_attr_options", Sdf.ValueTypeNames.Int)
        attr_b.SetMetadata("sdrMetadata", {"options": options})
        attr_b.Set(2)

        # finalize needs to be called here to get proper test name
        await ui_test.human_delay(50)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_attribute_ui_1.png", zero_mouse=True
        )

    # Capture screenshot of property window and compare with golden image (2/3)
    # The property list is too long and Window limits max window size base on primary monitor height,
    # the test has to be split into 3, each tests 1/3 of the attributes.
    async def test_attribute_ui_2(self):
        sublist_length = len(self._test_data) // 3

        await self._test_attribute_ui_base(sublist_length, 2 * sublist_length)

        # finalize needs to be called here to get proper test name
        await ui_test.human_delay(50)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_attribute_ui_2.png", zero_mouse=True
        )

    # Capture screenshot of property window and compare with golden image (3/3)
    # The property list is too long and Window limits max window size base on primary monitor height,
    # the test has to be split into 3, each tests 1/3 of the attributes.
    async def test_attribute_ui_3(self):
        sublist_length = len(self._test_data) // 3

        await self._test_attribute_ui_base(sublist_length * 2, len(self._test_data))

        # finalize needs to be called here to get proper test name
        await ui_test.human_delay(50)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_attribute_ui_3.png", zero_mouse=True
        )

    # test property filter
    async def test_property_filter(self):
        await self._test_attribute_ui_base(0, len(self._test_data), "color")
        await ui_test.human_delay(50)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_property_filter.png", zero_mouse=True
        )
        self._w._searchfield._search_field.model.as_string = ""
        self._w._searchfield._set_in_searching(False)

    # test property filter out everything
    async def test_property_filter_everything(self):
        await self._test_attribute_ui_base(0, len(self._test_data), "nothing")
        await ui_test.human_delay(50)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_property_filter_everything.png", zero_mouse=True
        )
        self._w._searchfield._search_field.model.as_string = ""
        self._w._searchfield._set_in_searching(False)

    # Tests the relationship UI
    async def test_relationship_ui(self):
        await self.docked_test_window(
            window=self._w._window,
            width=800,
            height=950,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        target_prim_paths = ["/Target1", "/Target2", "/Target3"]

        for prim_path in target_prim_paths:
            self._stage.DefinePrim(prim_path)

        rel = self._test_prim.CreateRelationship("TestRelationship")
        for prim_path in target_prim_paths:
            omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=prim_path)

        # Wait for a frame for widget to process all pending changes
        await omni.kit.app.get_app().next_update_async()

        omni.kit.commands.execute("RemoveRelationshipTarget", relationship=rel, target=target_prim_paths[-1])

        # Need to wait for an additional frame for omni.ui rebuild to take effect
        await omni.kit.app.get_app().next_update_async()

        await ui_test.human_delay(50)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_relationship_ui.png", zero_mouse=True
        )

    # Tests SdfReferences UI
    async def test_references_ui(self):
        await self.docked_test_window(
            window=self._w._window,
            width=800,
            height=420,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        usd_context = omni.usd.get_context()

        test_file_path = self._usd_path.joinpath("ref_test.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))

        self._stage = usd_context.get_stage()

        ref = Sdf.Reference(primPath="/Xform")
        omni.kit.commands.execute(
            "AddReference",
            stage=self._stage,
            prim_path="/World",
            reference=ref,
        )

        ref = Sdf.Reference(assetPath="cube.usda", primPath="/Xform")
        omni.kit.commands.execute(
            "AddReference",
            stage=self._stage,
            prim_path="/World",
            reference=ref,
        )

        ref = Sdf.Reference(assetPath="sphere.usda")
        omni.kit.commands.execute(
            "AddReference",
            stage=self._stage,
            prim_path="/World",
            reference=ref,
        )

        ref = Sdf.Reference(primPath="/Xform2")
        omni.kit.commands.execute(
            "AddReference",
            stage=self._stage,
            prim_path="/World",
            reference=ref,
        )

        await omni.kit.app.get_app().next_update_async()

        # Select the prim after references are created because the widget hide itself when there's no reference
        # Property window does not refresh itself when new ref is added. This is a limitation to property window that
        # needs to be fixed.
        usd_context.get_selection().set_selected_prim_paths(["/World"], True)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        ref = Sdf.Reference(primPath="/Xform2")
        omni.kit.commands.execute(
            "RemoveReference",
            stage=self._stage,
            prim_path="/World",
            reference=ref,
        )

        await omni.kit.app.get_app().next_update_async()

        # Need to wait for an additional frame for omni.ui rebuild to take effect
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await ui_test.human_delay(50)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_references_ui.png", zero_mouse=True
        )

    # Tests mixed TfToken (with allowedTokens) and MDL enum that when one changes
    # The bug was when selecting 2+ prims with TfToken(or MDL enum) that results in a mixed state,
    # changing last selected prim's value from USD API will overwrite the value for other untouched attributes.
    async def test_mixed_combobox_attributes(self):
        shader_a = UsdShade.Shader.Define(self._stage, "/PrimA")
        shader_b = UsdShade.Shader.Define(self._stage, "/PrimB")

        enum_options = "a:0|b:1|c:2"

        input_a = shader_a.CreateInput("mdl_enum", Sdf.ValueTypeNames.Int)
        input_a.SetSdrMetadataByKey("options", enum_options)
        input_a.SetRenderType("::dummy::enum")
        input_a.Set(0)

        input_b = shader_b.CreateInput("mdl_enum", Sdf.ValueTypeNames.Int)
        input_b.SetSdrMetadataByKey("options", enum_options)
        input_b.SetRenderType("::dummy::enum")
        input_b.Set(1)

        prim_a = shader_a.GetPrim()
        prim_b = shader_b.GetPrim()

        allowed_tokens = ["a", "b", "c"]

        attr_a = prim_a.CreateAttribute("token", Sdf.ValueTypeNames.Token)
        attr_a.SetMetadata("allowedTokens", allowed_tokens)
        attr_a.Set(allowed_tokens[0])

        attr_b = prim_b.CreateAttribute("token", Sdf.ValueTypeNames.Token)
        attr_b.SetMetadata("allowedTokens", allowed_tokens)
        attr_b.Set(allowed_tokens[1])

        omni.usd.get_context().get_selection().set_selected_prim_paths(["/PrimA", "/PrimB"], True)

        # took 5 frames to trigger the bug
        for _i in range(5):
            await omni.kit.app.get_app().next_update_async()

        input_b.Set(2)
        attr_b.Set(allowed_tokens[2])

        await omni.kit.app.get_app().next_update_async()

        # if bug happens, input_a's value will be set to 2
        self.assertEqual(input_a.Get(), 0)
        # if bug happens, attr_a's value will be set to "c"
        self.assertEqual(attr_a.Get(), allowed_tokens[0])

    async def test_sdf_path_delegate(self):

        await self._test_attribute_ui_base(0, int(len(self._test_data)), block_devices=False)

        treeview = ui_test.find("Property//Frame/**/.identifier=='sdf_asset_array_asset_array_attr'")

        self.assertTrue("SpecialAssetPathDelegate" in treeview.widget.model._delegate.__class__.__name__)
        await self.finalize_test_no_image()

    async def test_sdf_path_edit(self):

        await self._test_attribute_ui_base(0, int(len(self._test_data)), block_devices=False)

        edit_button_standalone = ui_test.find("Property//Frame/**/.identifier=='sdf_edit_asset_asset_attr'")
        edit_button_0 = ui_test.find("Property//Frame/**/.identifier=='sdf_edit_asset_asset_array_attr[0]'")
        edit_button_1 = ui_test.find("Property//Frame/**/.identifier=='sdf_edit_asset_asset_array_attr[1]'")

        # the first two clicks won't do anyting because the path is invalid and
        # the edit button is disabled...
        await edit_button_standalone.click()
        self.assertEqual(self._test_widget.edit_path, None)

        await edit_button_0.click()
        self.assertEqual(self._test_widget.edit_path, None)

        # this should do something because the path's valid
        await edit_button_1.click()
        self.assertEqual(self._test_widget.edit_path.path, "textures/granite_a_mask.png")

        await self.finalize_test_no_image()

    async def test_sdf_path_change(self):

        await self._test_attribute_ui_base(0, int(len(self._test_data)), block_devices=False)

        edit_button_standalone = ui_test.find("Property//Frame/**/.identifier=='sdf_edit_asset_asset_attr'")
        edit_button_0 = ui_test.find("Property//Frame/**/.identifier=='sdf_edit_asset_asset_array_attr[0]'")
        edit_button_1 = ui_test.find("Property//Frame/**/.identifier=='sdf_edit_asset_asset_array_attr[1]'")

        locate_button_standalone = ui_test.find("Property//Frame/**/.identifier=='sdf_locate_asset_asset_attr'")
        locate_button_0 = ui_test.find("Property//Frame/**/.identifier=='sdf_locate_asset_asset_array_attr[0]'")
        locate_button_1 = ui_test.find("Property//Frame/**/.identifier=='sdf_locate_asset_asset_array_attr[1]'")

        string_field_standalone = ui_test.find("Property//Frame/**/.identifier=='sdf_asset_asset_attr'")
        string_field_0 = ui_test.find("Property//Frame/**/.identifier=='sdf_asset_asset_array_attr[0]'")
        string_field_1 = ui_test.find("Property//Frame/**/.identifier=='sdf_asset_asset_array_attr[1]'")

        # first two locate/edit buttons should be disabled as they reference invalid
        # paths, but the third should be enabled:
        self.assertEqual(locate_button_standalone.widget.enabled, False)
        self.assertEqual(locate_button_0.widget.enabled, False)
        self.assertEqual(locate_button_1.widget.enabled, True)

        self.assertEqual(edit_button_standalone.widget.enabled, False)
        self.assertEqual(edit_button_0.widget.enabled, False)
        self.assertEqual(edit_button_1.widget.enabled, True)

        # Change by emulating keyboard input and make sure the widget states update:
        await string_field_standalone.input("textures/granite_a_mask.png")
        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(locate_button_standalone.widget.enabled, True)
        self.assertEqual(edit_button_standalone.widget.enabled, True)

        await string_field_0.input("textures/granite_a_mask.png")
        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(locate_button_0.widget.enabled, True)
        self.assertEqual(edit_button_0.widget.enabled, True)

        await string_field_1.input("nonsense")
        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(locate_button_1.widget.enabled, False)
        self.assertEqual(edit_button_1.widget.enabled, False)

        # Change by modifying the usd and make sure the widget states update:
        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=Sdf.Path("/TestPrim.asset_attr"),
            value="nonsense",
            prev=None,
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(locate_button_standalone.widget.enabled, False)
        self.assertEqual(edit_button_standalone.widget.enabled, False)

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=Sdf.Path("/TestPrim.asset_array_attr"),
            value=["nonsense", "textures/granite_a_mask.png"],
            prev=None,
        )
        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(locate_button_0.widget.enabled, False)
        self.assertEqual(edit_button_0.widget.enabled, False)
        self.assertEqual(locate_button_1.widget.enabled, True)
        self.assertEqual(edit_button_1.widget.enabled, True)

        await self.finalize_test_no_image()

    async def test_asset_path_convert(self):
        """Test asset path is converted correctly."""
        import carb
        from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder

        _orig_path_method = carb.settings.get_settings().get("/persistent/app/material/dragDropMaterialPath")

        # for material path, if path method is set to relative, should convert to relative path
        carb.settings.get_settings().set("/persistent/app/material/dragDropMaterialPath", "Relative")

        asset_paths = ("omniverse://dummy/foo.bar", "./dummy.xxx", f"{self._usd_path}/dummy.xxx")
        expected_results = ("omniverse://dummy/foo.bar", "./dummy.xxx", "./dummy.xxx")
        for asset, result in zip(asset_paths, expected_results):
            self.assertEqual(UsdPropertiesWidgetBuilder.convert_asset_path(asset), result)

        # for material path, if path method is set to absolute, should not convert path
        carb.settings.get_settings().set("/persistent/app/material/dragDropMaterialPath", "Absolute")
        asset_paths = ("omniverse://dummy/foo.bar", "./dummy.xxx", f"{self._usd_path}/dummy.xxx")
        expected_results = asset_paths
        for asset, result in zip(asset_paths, expected_results):
            self.assertEqual(UsdPropertiesWidgetBuilder.convert_asset_path(asset), result)

        carb.settings.get_settings().set("/persistent/app/material/dragDropMaterialPath", _orig_path_method)
        await self.finalize_test_no_image()

    async def test_labels(self):
        import omni.kit.window.property as property_window_ext
        from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget
        from omni.kit.test_suite.helpers import select_prims

        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Materials on selected models", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Test USD Properties", True)

        await self.docked_test_window(
            window=self._w._window,
            width=500,
            height=500,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
            block_devices=False,
        )

        class ExampleAttributeWidget(UsdPropertiesWidget):
            def __init__(self):
                super().__init__(title="Example Properties", collapsed=False)

            def on_new_payload(self, payload):
                if not payload or len(payload) == 0:
                    return False

                if not super().on_new_payload(payload):
                    return False

                used = []
                for prim_path in self._payload:
                    prim = self._get_prim(prim_path)
                    if not prim or not (prim.IsA(UsdGeom.Xform) or prim.IsA(UsdGeom.Mesh)):
                        return False
                    if self.is_custom_schema_attribute_used(prim):
                        used.append(None)
                    used.append(prim)

                return used is not None

            def _customize_props_layout(self, props):
                from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutProperty
                from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
                from omni.kit.window.property.templates import HORIZONTAL_SPACING

                frame = CustomLayoutFrame(hide_extra=False)
                with frame:

                    def build_fn(
                        stage,
                        attr_name,
                        metadata,
                        property_type,
                        prim_paths,
                        additional_label_kwargs=None,
                        additional_widget_kwarg=None,
                    ):
                        additional_kwargs = {
                            "word_wrap": False,
                            "elided_text": True,
                            "alignment": omni.ui.Alignment.LEFT,
                        }
                        with ui.HStack(spacing=HORIZONTAL_SPACING):
                            UsdPropertiesWidgetBuilder.create_label(
                                "It had been sixteen days since the last zombie attack",
                                additional_label_kwargs=additional_kwargs,
                            )
                            ui.Button("Phew")

                        with ui.HStack(spacing=HORIZONTAL_SPACING):
                            UsdPropertiesWidgetBuilder.create_label(
                                "The gruff old man sat in the back of the bait shop grumbling to himself as he scooped out a handful of worms",
                                additional_label_kwargs=additional_kwargs,
                            )
                            ui.Button("Slowly head for the door")

                    CustomLayoutProperty(None, None, build_fn=build_fn)

                return frame.apply(props)

        property_window = property_window_ext.get_window()
        if property_window:
            property_window.register_widget("prim", "example_properties", ExampleAttributeWidget())

        try:
            await ui_test.human_delay(10)
            await select_prims(["/Xform"])

            await ui_test.human_delay(50)
            await self.finalize_test(
                threshold=0.25,
                golden_img_dir=self._golden_img_dir,
                golden_img_name="test_label_elided_text.png",
                zero_mouse=True,
            )
            await ui_test.human_delay(50)
        finally:
            # remove...
            property_window = property_window_ext.get_window()
            if property_window:
                # remove ExampleAttributeWidget class with property window
                property_window.unregister_widget("prim", "example_properties")
