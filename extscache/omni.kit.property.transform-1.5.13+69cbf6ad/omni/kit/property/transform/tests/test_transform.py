## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path

import carb
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.undo
import omni.timeline
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest
from pxr import Gf, UsdGeom

from ..scripts.transform_builder import USDXformOpRotateWidget


class TestTransformWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        extension_root_folder = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        )

        self._golden_img_dir = extension_root_folder.joinpath("data/test_data/golden_img")
        self._usd_path = extension_root_folder.joinpath("data/test_data/test_map")

        import omni.kit.window.property as p

        self._w = p.get_window()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_transform_property_srt(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=250,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_transform_property_srt.png")

    async def test_transform_property_srt_filter(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=250,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)

        try:
            self._w._searchfield._search_field.model.as_string = "tr"
            self._w._searchfield._set_in_searching(True)

            # Need to wait for an additional frames for omni.ui rebuild to take effect
            await ui_test.human_delay(10)

            await self.finalize_test(
                golden_img_dir=self._golden_img_dir, golden_img_name="test_transform_property_srt_filter.png"
            )
        finally:
            self._w._searchfield._search_field.model.as_string = ""
            self._w._searchfield._set_in_searching(False)

    async def test_transform_property_sqt(self):
        usd_context = omni.usd.get_context()

        # golden image expects the UI to be switched to "orient as rotate"
        settings = carb.settings.get_settings()
        doar_path = "/persistent/app/uiSettings/DisplayOrientAsRotate"
        doar_val = settings.get_as_bool(doar_path)
        settings.set(doar_path, True)

        try:
            await self.docked_test_window(
                window=self._w._window,
                width=450,
                height=250,
                restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
                restore_position=ui.DockPosition.BOTTOM,
            )

            test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
            await usd_context.open_stage_async(str(test_file_path))
            await wait_stage_loading()

            # Select the prim.
            usd_context.get_selection().set_selected_prim_paths(["/World/Capsule"], True)

            # Need to wait for an additional frames for omni.ui rebuild to take effect
            await ui_test.human_delay(10)
        finally:
            carb.settings.get_settings().set(doar_path, doar_val)
            await self.finalize_test(
                golden_img_dir=self._golden_img_dir, golden_img_name="test_transform_property_sqt.png"
            )

    async def test_transform_property_matrix(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=250,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cylinder"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_transform_property_matrix.png"
        )

    async def test_transform_property_pivot(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=280,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cone"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_transform_property_pivot.png"
        )

    async def test_transform_property_disabled_translate_op(self):
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=260,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Sphere"], True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_transform_property_disabled_translate_op.png"
        )

    async def test_transform_property_euler_to_quat_sync(self):
        usd_context = omni.usd.get_context()
        usd_context.new_stage()

        settings = carb.settings.get_settings()
        doar_path = "/persistent/app/uiSettings/DisplayOrientAsRotate"
        doar_val = settings.get_as_bool(doar_path)
        carb.settings.get_settings().set(doar_path, True)

        try:
            await self.docked_test_window(
                window=self._w._window,
                width=640,
                height=480,
                restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
                restore_position=ui.DockPosition.BOTTOM,
            )

            # we actually want mouse and keyboard to be active
            omni.appwindow.get_default_app_window().set_input_blocking_state(carb.input.DeviceType.MOUSE, False)
            omni.appwindow.get_default_app_window().set_input_blocking_state(carb.input.DeviceType.KEYBOARD, False)

            await ui_test.wait_n_updates(10)

            path = "/Cube"
            cube_geom = UsdGeom.Cube.Define(usd_context.get_stage(), path)
            cube_geom.AddOrientOp().Set(Gf.Quatf(1.0))

            usd_context.get_selection().set_selected_prim_paths([path], False)
            await ui_test.find("Property").focus()

            transform_euler = ui_test.find("Property//Frame/**/*.identifier=='euler_xformOp:orient'")

            # change Y axis to 180 digit by digit as a user would do
            await transform_euler.double_click(human_delay_speed=10)
            for s in "180":
                await ui_test.emulate_char_press(s)
                await ui_test.wait_n_updates(10)
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        finally:
            await self.finalize_test_no_image()
            carb.settings.get_settings().set(doar_path, doar_val)

        orient = Gf.Quatf(1.0)
        for op in cube_geom.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeOrient:
                orient = op.Get()
        self.assertTrue(orient.imaginary[1] != 0)

    async def test_transform_property_scale_default(self):
        """
        OMPRW-901: check data type for scale default value
        """
        usd_context = omni.usd.get_context()

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay()

        # Set xformOp:scale default
        stage = usd_context.get_stage()
        prim = stage.GetPrimAtPath("/World/Cube")
        attr = prim.GetAttribute("xformOp:scale")
        attr.ClearDefault()

        scale_value_field_widget = ui_test.find("Property//Frame/**/*.identifier=='scale_stack'").find(
            "**/HStack[0]/ZStack[1]/FloatDrag[0]"
        )

        # No error when change the first component
        scale_value_field_widget.model.set_value(2.0)

    async def test_transform_rotate_order_dropdown(self):
        usd_context = omni.usd.get_context()

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay()

        # Set xformOp:scale default
        stage = usd_context.get_stage()
        prim = stage.GetPrimAtPath("/World/Cube")
        attr = prim.GetAttribute("xformOp:scale")
        attr.ClearDefault()

        # click on all rotate-order drop down manipulators
        for _, rotate_order in enumerate(USDXformOpRotateWidget.ROTATE_ORDERS):
            frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Transform'")
            await frame.find("**/.identifier=='rotation dropdown button'").click()
            await ui_test.human_delay()

            await ui_test.find(f"RotationOrder//Frame/**/.identifier=='button {rotate_order}'").click()
            await ui_test.human_delay()

    async def test_transform_add_transforms(self):
        usd_context = omni.usd.get_context()

        test_file_path = self._usd_path.joinpath("test_transform_property.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World"], True)
        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay()

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath("/World")
        self.assertFalse(prim.HasAttribute("xformOp:translate"))

        frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Transform'")
        for w in frame.find_all("/**/Button[*]"):
            if "Add Transforms" in w.widget.text:
                await w.click()
                await ui_test.human_delay()
                self.assertTrue(prim.HasAttribute("xformOp:translate"))
                omni.kit.undo.undo()
                await ui_test.human_delay()
                self.assertFalse(prim.HasAttribute("xformOp:translate"))
                return

        carb.log_error('"Add Transforms" Button not found on /World')

    async def test_transform_time_samples(self):
        usd_context = omni.usd.get_context()
        timeline = omni.timeline.get_timeline_interface()

        test_file_path = self._usd_path.joinpath("time_samples.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay()

        frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Transform'")
        self.assertIsNotNone(frame)

        widgets = frame.find_all("Property//Frame/**/.identifier=='value'")
        model = widgets[1].model
        start_time = timeline.get_current_time()
        self.assertEqual(start_time, 0)
        self.assertEqual(model.get_value(), [0, 0, 0])

        tps = timeline.get_time_codes_per_seconds()
        timeline.set_current_time(1.0 / tps)
        await ui_test.human_delay()
        self.assertEqual(model.get_value(), [0, 10, 0])

        timeline.set_current_time(5.0 / tps)
        await ui_test.human_delay()
        self.assertEqual(model.get_value(), [0, 50, 0])
