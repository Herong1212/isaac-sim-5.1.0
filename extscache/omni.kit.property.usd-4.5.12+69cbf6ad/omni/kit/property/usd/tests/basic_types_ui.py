## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.window.property.managed_frame
from omni.ui.tests.test_base import OmniUiTest
from pxr import Gf, Sdf


class TestBasicTypesRange(OmniUiTest):  # pragma: no cover
    def __init__(self, tests=()):
        super().__init__(tests)
        self._widget_compare_table = {
            Sdf.ValueTypeNames.Half2.type: (Gf.Vec2h(0.12345, 0.12345), 3),
            Sdf.ValueTypeNames.Float2.type: (Gf.Vec2f(0.12345, 0.12345), 4),
            Sdf.ValueTypeNames.Double2.type: (Gf.Vec2d(0.12345, 0.12345), 4),
            Sdf.ValueTypeNames.Half3.type: (Gf.Vec3h(0.12345, 0.12345, 0.12345), 3),
            Sdf.ValueTypeNames.Float3.type: (Gf.Vec3f(0.12345, 0.12345, 0.12345), 4),
            Sdf.ValueTypeNames.Double3.type: (Gf.Vec3d(0.12345, 0.12345, 0.12345), 4),
            Sdf.ValueTypeNames.Half4.type: (Gf.Vec4h(0.12345, 0.12345, 0.12345, 0.12345), 3),
            Sdf.ValueTypeNames.Float4.type: (Gf.Vec4f(0.12345, 0.12345, 0.12345, 0.12345), 4),
            Sdf.ValueTypeNames.Double4.type: (Gf.Vec4d(0.12345, 0.12345, 0.12345, 0.12345), 4),
            Sdf.ValueTypeNames.Int2.type: Gf.Vec2i(9999, 9999),
            Sdf.ValueTypeNames.Int3.type: Gf.Vec3i(9999, 9999, 9999),
            Sdf.ValueTypeNames.Int4.type: Gf.Vec4i(9999, 9999, 9999, 9999),
            Sdf.ValueTypeNames.UChar.type: 99,
            Sdf.ValueTypeNames.UInt.type: 99,
            Sdf.ValueTypeNames.Int.type: 9999,
            Sdf.ValueTypeNames.Int64.type: 9999,
            Sdf.ValueTypeNames.UInt64.type: 9999,
        }

    def assertAlmostEqualVector(self, vec1, vec2, places=4):
        match type(vec1):
            case Gf.Vec2d | Gf.Vec2f | Gf.Vec2h:
                self.assertAlmostEqual(vec1[0], vec2[0], places=places)
                self.assertAlmostEqual(vec1[1], vec2[1], places=places)
            case Gf.Vec3d | Gf.Vec3f | Gf.Vec3h:
                self.assertAlmostEqual(vec1[0], vec2[0], places=places)
                self.assertAlmostEqual(vec1[1], vec2[1], places=places)
                self.assertAlmostEqual(vec1[2], vec2[2], places=places)
            case Gf.Vec4d | Gf.Vec4f | Gf.Vec4h:
                self.assertAlmostEqual(vec1[0], vec2[0], places=places)
                self.assertAlmostEqual(vec1[1], vec2[1], places=places)
                self.assertAlmostEqual(vec1[2], vec2[2], places=places)
                self.assertAlmostEqual(vec1[3], vec2[3], places=places)
            case _:
                if isinstance(vec1, float):
                    self.assertAlmostEqual(vec1, vec2, places=places)
                else:
                    raise ValueError(f"Unexpected type: {type(vec1)}")

    def assertEqualVector(self, vec1, vec2, places=4):
        match type(vec1):
            case Gf.Vec2i:
                self.assertEqual(vec1[0], vec2[0])
                self.assertEqual(vec1[1], vec2[1])
            case Gf.Vec3i:
                self.assertEqual(vec1[0], vec2[0])
                self.assertEqual(vec1[1], vec2[1])
                self.assertEqual(vec1[2], vec2[2])
            case Gf.Vec4i:
                self.assertEqual(vec1[0], vec2[0])
                self.assertEqual(vec1[1], vec2[1])
                self.assertEqual(vec1[2], vec2[2])
                self.assertEqual(vec1[3], vec2[3])
            case _:
                if isinstance(vec1, int):
                    self.assertEqual(vec1, vec2)
                else:
                    raise ValueError(f"Unexpected type: {type(vec1)}")

    # Before running each test
    async def setUp(self):
        from omni.kit.test_suite.helpers import arrange_windows, get_test_data_path, open_stage

        await arrange_windows(topleft_window="Property", topleft_height=64, topleft_width=800.0)
        await open_stage(get_test_data_path(__name__, "usd/types.usda"))
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)

    # After running each test
    async def tearDown(self):
        from omni.kit.test_suite.helpers import wait_stage_loading

        await wait_stage_loading()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    # assertEqualWithRetry is only in AsyncTestCase
    async def __assertEqualWithRetry(self, operation, expected, wait_frames: int = 2, max_retries: int = 50):
        for _ in range(max_retries):
            ret = operation()
            if ret == expected:
                break
            await self.wait_n_updates(wait_frames)
        self.assertEqualVector(
            ret,
            expected,
            f"operation failed to get the expected value after {max_retries} retries: {ret} != {expected}",
        )

    async def test_basic_type_coverage_ui(self):
        from omni.kit import ui_test
        from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
        from omni.kit.test_suite.helpers import select_prims, wait_stage_loading

        UsdPropertiesWidgetBuilder.reset_builder_coverage_table()

        stage = omni.usd.get_context().get_stage()

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        for prim_path in ["/defaultPrim/in_0", "/defaultPrim/in_1", "/defaultPrim/out_0"]:
            await select_prims([prim_path])

            # create attribute used table
            prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
            attr_list = {}
            for attr in prim.GetAttributes():
                attr_list[attr.GetPath().name] = attr.GetTypeName().type.typeName

            # remove all widgets from attribute used table
            for w in ui_test.find_all("Property//Frame/**/.identifier!=''"):
                wid = w.widget.identifier
                for wtype in [
                    "bool_",
                    "float_slider_",
                    "integer_slider_",
                    "drag_per_channel_",
                    "boolean_per_channel_",
                    "matrix_",
                    "token_",
                    "string_",
                    "timecode_",
                    "sdf_asset_array_",  # must before "sdf_asset_"
                    "sdf_asset_",
                    "fallback_",
                ]:
                    if wid.startswith(wtype):
                        attr_id = wid[len(wtype) :]
                        # ignore placeholder widgets
                        if attr_id in attr_list:
                            del attr_list[attr_id]
                        break

            # check attribute used table is empty
            self.assertFalse(attr_list, f"USD attribute {attr_list} have no widgets")

        widget_builder_coverage_table = UsdPropertiesWidgetBuilder.widget_builder_coverage_table
        for widget_type, builder_state in widget_builder_coverage_table.items():
            self.assertTrue(builder_state, f"Failed to test {widget_type}")

    async def test_float_rounding(self):
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import select_prims, wait_stage_loading

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()

        tested_list = {}
        for prim_path in ["/defaultPrim/in_0", "/defaultPrim/in_1", "/defaultPrim/out_0"]:
            await select_prims([prim_path])

            # test float types
            for w in ui_test.find_all("Property//Frame/**/.identifier!=''"):
                wid = w.widget.identifier
                if wid.startswith("float_slider_"):
                    if wid in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    await ui_test.human_delay()
                    await w.input("0.12345")
                    await ui_test.human_delay()
                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[13:])
                    self.assertAlmostEqualVector(attr.Get(), 0.12345, places=4)
                    tested_list[wid] = True
                elif wid.startswith("integer_slider_"):
                    if wid in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[15:])
                    metadata = attr.GetAllMetadata()
                    type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")).type
                    value = self._widget_compare_table[type_name]
                    await ui_test.human_delay()
                    await w.input(str(value))
                    await ui_test.human_delay()
                    self.assertEqualVector(attr.Get(), value)
                    tested_list[wid] = True
                elif wid.startswith("drag_per_channel_int"):
                    if wid in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    await ui_test.human_delay()
                    sub_widgets = w.find_all("**/IntSlider[*]")
                    if sub_widgets == []:
                        sub_widgets = w.find_all("**/IntDrag[*]")
                    self.assertNotEqual(sub_widgets, [])

                    for child in sub_widgets:
                        child.model.set_value(0)
                        await child.input("9999")
                        await ui_test.human_delay()

                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[17:])
                    metadata = attr.GetAllMetadata()
                    type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")).type
                    await self.__assertEqualWithRetry(attr.Get, self._widget_compare_table[type_name])
                    tested_list[wid] = True
                elif wid.startswith("drag_per_channel_"):
                    # colord normald pointd texcoordd vectord are the same
                    idc = wid
                    for count in [2, 3, 4]:
                        for fullsize, size in [("half", "h"), ("float", "f"), ("double", "d")]:
                            if wid in [
                                f"drag_per_channel_color{size}{count}_0",
                                f"drag_per_channel_normal{size}{count}_0",
                                f"drag_per_channel_point{size}{count}_0",
                                f"drag_per_channel_texcoord{size}{count}_0",
                                f"drag_per_channel_vector{size}{count}_0",
                            ]:
                                idc = f"drag_per_channel_{fullsize}{count}_0"

                    if idc in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    await ui_test.human_delay()
                    sub_widgets = w.find_all("**/FloatSlider[*]")
                    if sub_widgets == []:
                        sub_widgets = w.find_all("**/FloatDrag[*]")
                    self.assertNotEqual(sub_widgets, [])

                    for child in sub_widgets:
                        child.model.set_value(0)
                        await child.input("0.12345")
                        await ui_test.human_delay()

                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[17:])
                    metadata = attr.GetAllMetadata()
                    type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")).type
                    value, places = self._widget_compare_table[type_name]
                    self.assertAlmostEqualVector(attr.Get(), value, places=places)
                    tested_list[idc] = True

    async def test_float_rounding_tab(self):
        from carb.input import KeyboardInput
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import select_prims, wait_stage_loading

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()

        tested_list = {}
        for prim_path in ["/defaultPrim/in_0", "/defaultPrim/in_1", "/defaultPrim/out_0"]:
            await select_prims([prim_path])

            # test float types
            for w in ui_test.find_all("Property//Frame/**/.identifier!=''"):
                wid = w.widget.identifier
                if wid.startswith("float_slider_"):
                    if wid in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    await ui_test.human_delay()
                    await w.input("0.12345", end_key=KeyboardInput.TAB)
                    await ui_test.human_delay()
                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[13:])
                    self.assertAlmostEqualVector(attr.Get(), 0.12345, places=4)
                    tested_list[wid] = True
                elif wid.startswith("integer_slider_"):
                    if wid in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[15:])
                    metadata = attr.GetAllMetadata()
                    type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")).type
                    value = self._widget_compare_table[type_name]
                    await ui_test.human_delay()
                    await w.input(str(value))
                    await ui_test.human_delay()
                    self.assertEqualVector(attr.Get(), value)
                    tested_list[wid] = True
                elif wid.startswith("drag_per_channel_int"):
                    if wid in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    await ui_test.human_delay()
                    sub_widgets = w.find_all("**/IntSlider[*]")
                    if sub_widgets == []:
                        sub_widgets = w.find_all("**/IntDrag[*]")
                    self.assertNotEqual(sub_widgets, [])

                    for child in sub_widgets:
                        child.model.set_value(0)
                        await child.input("9999")
                        await ui_test.human_delay()

                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[17:])
                    metadata = attr.GetAllMetadata()
                    type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")).type
                    await self.__assertEqualWithRetry(attr.Get, self._widget_compare_table[type_name])
                    tested_list[wid] = True
                elif wid.startswith("drag_per_channel_"):
                    # colord normald pointd texcoordd vectord are the same
                    idc = wid
                    for count in [2, 3, 4]:
                        for fullsize, size in [("half", "h"), ("float", "f"), ("double", "d")]:
                            if wid in [
                                f"drag_per_channel_color{size}{count}_0",
                                f"drag_per_channel_normal{size}{count}_0",
                                f"drag_per_channel_point{size}{count}_0",
                                f"drag_per_channel_texcoord{size}{count}_0",
                                f"drag_per_channel_vector{size}{count}_0",
                            ]:
                                idc = f"drag_per_channel_{fullsize}{count}_0"

                    if idc in tested_list:
                        continue
                    w.widget.scroll_here_y(0.5)
                    await ui_test.human_delay()
                    sub_widgets = w.find_all("**/FloatSlider[*]")
                    if sub_widgets == []:
                        sub_widgets = w.find_all("**/FloatDrag[*]")
                    self.assertNotEqual(sub_widgets, [])

                    for child in sub_widgets:
                        child.model.set_value(0)
                        await child.input("0.12345", end_key=KeyboardInput.TAB)
                        await ui_test.human_delay()

                    attr = stage.GetPrimAtPath(prim_path).GetAttribute(wid[17:])
                    metadata = attr.GetAllMetadata()
                    type_name = Sdf.ValueTypeNames.Find(metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")).type
                    value, places = self._widget_compare_table[type_name]
                    self.assertAlmostEqualVector(attr.Get(), value, places=places)
                    tested_list[idc] = True

    async def test_mixed(self):
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import select_prims, wait_stage_loading

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        await select_prims(["/defaultPrim/in_0", "/defaultPrim/in_0_duplicate"])

        last_widget = None

        for w in ui_test.find_all("Property//Frame/**/.identifier!=''"):
            wid = w.widget.identifier
            if wid.endswith("_mixed_stack") and w.widget.visible:
                last_widget.widget.scroll_here_y(0.5)
                await ui_test.human_delay()
                await last_widget.double_click()
                await ui_test.human_delay(50)
                self.assertEqualVector(w.widget.visible, False)
                last_widget = None
            else:
                last_widget = w
