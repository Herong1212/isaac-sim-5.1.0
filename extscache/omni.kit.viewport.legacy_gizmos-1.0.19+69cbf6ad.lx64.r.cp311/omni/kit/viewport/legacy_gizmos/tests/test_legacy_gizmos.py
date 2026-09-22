# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import pathlib
import asyncio

import carb

import omni.kit.app
import omni.kit.test

from omni.kit.hydra_texture import create_hydra_texture
import omni.renderer_capture
from omni.kit.test_helpers_gfx.compare_utils import finalize_capture_and_compare, ComparisonMetric

import omni.usd
from pxr import Usd, Gf

# FIXME: omni.ui.ImageProvider holds the carb.Format conversion routine
import omni.ui

EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TEST_DATA_DIR = EXTENSION_FOLDER_PATH.joinpath('data', 'tests')

KIT_ROOT = pathlib.Path(carb.tokens.acquire_tokens_interface().resolve('${kit}')).parent.parent.parent
OUTPUTS_DIR = pathlib.Path(omni.kit.test.get_test_output_path())

from sys import platform
if platform.find('linux') == 0:
  IMAGE_PLATFORM='linux'
elif platform == 'darwin':
  IMAGE_PLATFORM='macos'
elif platform == 'win32':
  IMAGE_PLATFORM='windows'

class TestLegacyGizmos(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.acquire_settings_interface()
        self._render_capture = omni.renderer_capture.acquire_renderer_capture_interface()

        self._usd_context_name = 'test_context'
        self._usd_context = omni.usd.create_context(self._usd_context_name)

    async def tearDown(self):
        omni.usd.release_all_hydra_engines(self._usd_context)
        omni.usd.destroy_context(self._usd_context_name)
        self._settings = None
        self._render_capture = None

    async def _create_hydra_texture_test(self, filename: str = None):
        wait_iterations = 15
        try:
            if 'rtx' not in self._usd_context.get_attached_hydra_engine_names():
                omni.usd.create_hydra_engine('rtx', self._usd_context)

            for i in range(wait_iterations):
                await omni.kit.app.get_app().next_update_async()

            if filename:
                test_usd_asset = TEST_DATA_DIR.joinpath(filename)
                self._usd_context.open_stage_with_callback(str(test_usd_asset), None)
            else:
                self._usd_context.new_stage_with_callback(None)

            hydra_texture = create_hydra_texture(
                'test_viewport',
                320,
                320,
                self._usd_context_name,
                '/OmniverseKit_Persp',
                'rtx',
                is_async=False
            )

            return hydra_texture
        finally:
            for i in range(wait_iterations):
                await omni.kit.app.get_app().next_update_async()

    async def _capture_hydra_texture(self, hydra_texture, test_name: str, converge: int = 5, platform_image: bool = False):
        drawable_result = asyncio.Future()
        if platform_image:
            global IMAGE_PLATFORM
            image_name = f'{test_name}_{IMAGE_PLATFORM}.png'
        else:
            image_name = f'{test_name}.png'
        filepath = OUTPUTS_DIR.joinpath(image_name).absolute()

        def on_drawable_changed(event: carb.events.IEvent):
            if event.type != omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED:
                carb.log_error('Wrong event captured for DRAWABLE_CHANGED')
                return

            result_handle = event.payload['result_handle']
            self.assertIsNotNone(result_handle)

            ldr_info = hydra_texture.get_aov_info(result_handle, 'LdrColor', include_texture=True)
            self.assertEqual(len(ldr_info), 1)
            self.assertEqual(ldr_info[0]['name'], 'LdrColor')
            ldr_tex = ldr_info[0]['texture']
            self.assertIsNotNone(ldr_tex)
            ldr_rsrc = ldr_tex['rp_resource']
            self.assertIsNotNone(ldr_rsrc)

            nonlocal converge
            converge = converge - 1
            if converge <= 0 and not drawable_result.done():
                self._render_capture.capture_next_frame_rp_resource(str(filepath), ldr_rsrc)
                drawable_result.set_result(True)

        drawable_change_sub = hydra_texture.get_event_stream().create_subscription_to_push_by_type(
            omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED,
            on_drawable_changed,
            name="_capture_hydra_texture",
        )

        result = await drawable_result
        drawable_change_sub = None
        self.assertTrue(result)
        return image_name

    async def capture_and_compare(self, image_name: str, threshold: float = 1e-4):
        # self._render_capture.wait_async_capture()
        diff = finalize_capture_and_compare(image_name, threshold=threshold, output_img_dir=OUTPUTS_DIR,
                                            golden_img_dir=TEST_DATA_DIR, metric=ComparisonMetric.MEAN_ERROR_SQUARED)
        if diff > threshold:
            carb.log_error(f'The generated image {image_name} has a difference of {diff}, but max difference is {threshold}')

    async def test_light_gizmos(self):
        hydra_texture = await self._create_hydra_texture_test('gizmos.usda')
        self.assertIsNotNone(hydra_texture)

        # >> test_sphere_light
        self._settings.set('/app/viewport/grid/enabled', False)
        self._settings.set('/persistent/app/viewport/gizmo/lineWidth', 1)
        self._settings.set('/persistent/app/viewport/gizmo/scale', 1)

        self._usd_context.get_selection().set_selected_prim_paths(['/World/SphereLight'], True)
        image = await self._capture_hydra_texture(hydra_texture, 'test_sphere_light', platform_image=True)
        await self.capture_and_compare(image)
        # << test_sphere_light


        # >> test_cylinder_light
        self._settings.set('/app/viewport/grid/enabled', False)
        self._settings.set('/persistent/app/viewport/gizmo/lineWidth', 2)
        self._settings.set('/persistent/app/viewport/gizmo/scale', 2)

        self._usd_context.get_selection().set_selected_prim_paths(['/World/CylinderLight'], True)
        image = await self._capture_hydra_texture(hydra_texture, 'test_cylinder_light', platform_image=True)
        await self.capture_and_compare(image)
        # << test_cylinder_light


        # >> test_disk_light
        self._settings.set('/app/viewport/grid/enabled', False)
        self._settings.set('/persistent/app/viewport/gizmo/lineWidth', 10)
        self._settings.set('/persistent/app/viewport/gizmo/scale', 10)

        self._usd_context.get_selection().set_selected_prim_paths(['/World/DiskLight'], True)
        image = await self._capture_hydra_texture(hydra_texture, 'test_disk_light', platform_image=True)
        await self.capture_and_compare(image)
        # << test_disk_light


        # >> test_rect_light
        self._settings.set('/app/viewport/grid/enabled', False)
        self._settings.set('/persistent/app/viewport/gizmo/lineWidth', 20)
        self._settings.set('/persistent/app/viewport/gizmo/scale', 20)

        self._usd_context.get_selection().set_selected_prim_paths(['/World/RectLight'], True)
        image = await self._capture_hydra_texture(hydra_texture, 'test_rect_light', platform_image=True)
        await self.capture_and_compare(image)
        # << test_rect_light

    async def test_grid_drawing(self):
        hydra_texture = await self._create_hydra_texture_test('empty.usda')
        self.assertIsNotNone(hydra_texture)

        # >> test_grid_drawing
        self._settings.set('/app/viewport/grid/enabled', True)
        self._settings.set('/persistent/app/viewport/grid/lineColor', carb.Float3(0.3, 0.3, 0.3))
        self._settings.set('/persistent/app/viewport/grid/lineWidth', 1)
        self._settings.set('/persistent/app/viewport/grid/scale', 100)
        # Need to wait for slightly more frames on Linux to avoid writing black imge / failure
        image = await self._capture_hydra_texture(hydra_texture, 'test_grid_drawing', converge=20)
        await self.capture_and_compare(image)
        # << test_grid_drawing


        # >> test_grid_drawing_yz
        self._settings.set('/app/viewport/grid/enabled', True)
        self._settings.set('/persistent/app/viewport/grid/lineColor', carb.Float3(0.3, 0.3, 0.3))
        self._settings.set('/app/viewport/grid/plane', 'YZ')
        self._settings.set('/persistent/app/viewport/grid/lineWidth', 10)
        self._settings.set('/persistent/app/viewport/grid/scale', 150)

        image = await self._capture_hydra_texture(hydra_texture, 'test_grid_drawing_yz')
        await self.capture_and_compare(image)
        # << test_grid_drawing_yz


        # >> test_grid_drawing_xy
        self._settings.set('/app/viewport/grid/enabled', True)
        self._settings.set('/persistent/app/viewport/grid/lineColor', carb.Float3(0.3, 0.3, 0.3))
        self._settings.set('/app/viewport/grid/plane', 'XY')
        self._settings.set('/persistent/app/viewport/grid/lineWidth', 4)
        self._settings.set('/persistent/app/viewport/grid/scale', 200)

        image = await self._capture_hydra_texture(hydra_texture, 'test_grid_drawing_xy')
        await self.capture_and_compare(image)
        # << test_grid_drawing_xy


        # >> test_grid_drawing_xz
        self._settings.set('/app/viewport/grid/enabled', True)
        self._settings.set('/persistent/app/viewport/grid/lineColor', carb.Float3(0.3, 0.3, 0.3))
        self._settings.set('/app/viewport/grid/plane', 'XZ')
        self._settings.set('/persistent/app/viewport/grid/lineWidth', 6)
        self._settings.set('/persistent/app/viewport/grid/scale', 250)

        image = await self._capture_hydra_texture(hydra_texture, 'test_grid_drawing_xz')
        await self.capture_and_compare(image)
        # << test_grid_drawing_xz

    async def test_camera_gizmos(self):
        hydra_texture = await self._create_hydra_texture_test('cameras.usda')
        self.assertIsNotNone(hydra_texture)
        wait_iterations = 5
        try:
            self._settings.set('/app/viewport/show/camera', True)
            self._settings.set('/persistent/app/viewport/gizmo/constantScaleCamera', False)
            self._settings.set('/persistent/app/viewport/gizmo/constantScaleEnabled', False)
            self._settings.set('/persistent/app/viewport/gizmo/constantScale', 10.0)
            self._settings.set('/persistent/app/viewport/gizmo/scale', 2.0)
            self._settings.set('/app/viewport/grid/enabled', False)

            for i in range(wait_iterations): await omni.kit.app.get_app().next_update_async();
            image = await self._capture_hydra_texture(hydra_texture, 'test_camera_drawing_0')
            await self.capture_and_compare(image)

            stage = self._usd_context.get_stage()
            camera_prim = stage.GetPrimAtPath('/World/Camera')
            camera_prim.GetAttribute('xformOp:translate').Set(Gf.Vec3d(0, 0, -250))

            for i in range(wait_iterations): await omni.kit.app.get_app().next_update_async();
            image = await self._capture_hydra_texture(hydra_texture, 'test_camera_drawing_1')
            await self.capture_and_compare(image)

            self._settings.set('/persistent/app/viewport/gizmo/constantScale', 50.0)
            self._settings.set('/persistent/app/viewport/gizmo/constantScaleEnabled', True)
            self._settings.set('/persistent/app/viewport/gizmo/constantScaleCamera', True)
            for i in range(wait_iterations): await omni.kit.app.get_app().next_update_async();
            image = await self._capture_hydra_texture(hydra_texture, 'test_camera_drawing_2')
            await self.capture_and_compare(image)

        finally:
            self._settings.set('/app/viewport/show/camera', False)
            self._settings.set('/persistent/app/viewport/gizmo/scale', 1.0)
            self._settings.set('/persistent/app/viewport/gizmo/constantScale', 10.0)
            self._settings.set('/persistent/app/viewport/gizmo/constantScaleEnabled', True)
            self._settings.set('/persistent/app/viewport/gizmo/constantScaleCamera', False)


    async def test_bounding_box_drawing(self):
        hydra_texture = await self._create_hydra_texture_test('bounding_box.usda')
        self.assertIsNotNone(hydra_texture)

        self._usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)

        self._settings.set('/app/viewport/grid/enabled', False)
        saved_pick_mode = self._settings.get("/persistent/app/viewport/pickingMode")

        try:
            # >> test_bounding_box_drawing in prim mode
            self._settings.set("/persistent/app/viewport/pickingMode", "type:ALL")
            self._settings.set('/app/viewport/boundingBoxes/enabled', True)
            self._settings.set('/app/viewport/boundingBoxes/lineColor', [0.886, 0.447, 0.447])
            # Need to wait for slightly more frames on Linux to avoid writing black image / failure
            image = await self._capture_hydra_texture(hydra_texture, 'test_bounding_box_drawing', converge=20)
            await self.capture_and_compare(image)
            # << test_bounding_box_drawing

            # >> test_bounding_box_hide in prim mode
            self._settings.set('/app/viewport/boundingBoxes/enabled', False)
            # Need to wait for slightly more frames on Linux to avoid writing black image / failure
            image = await self._capture_hydra_texture(hydra_texture, 'test_bounding_box_hide', converge=20)
            await self.capture_and_compare(image)
            # << test_bounding_box_hide

            # >> test bounding box always hide in model mode
            self._settings.set("/persistent/app/viewport/pickingMode", "kind:model.ALL")
            image = await self._capture_hydra_texture(hydra_texture, 'test_bounding_box_hide', converge=20)
            await self.capture_and_compare(image)

            self._settings.set('/app/viewport/boundingBoxes/enabled', True)
            image = await self._capture_hydra_texture(hydra_texture, 'test_bounding_box_hide', converge=20)
            await self.capture_and_compare(image)
        finally:
            self._settings.set("/persistent/app/viewport/pickingMode", saved_pick_mode)
