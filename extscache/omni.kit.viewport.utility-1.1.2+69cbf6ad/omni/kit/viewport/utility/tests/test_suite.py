## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestViewportUtility']

import carb

import omni.kit.test
from omni.kit.test import AsyncTestCase

import omni.kit.viewport.utility
import omni.kit.renderer_capture
import omni.kit.app
import omni.usd
import omni.ui as ui
from pathlib import Path
from pxr import Gf, UsdGeom, Sdf, Usd


TEST_OUTPUT = Path(omni.kit.test.get_test_output_path()).resolve().absolute()
TEST_WIDTH, TEST_HEIGHT = (500, 500)


class TestViewportUtility(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        super().setUp()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        super().tearDown()

    # Legacy Viewport needs some time to adopt the resolution changes
    async def wait_for_resolution_change(self, viewport_api):
        await omni.kit.viewport.utility.next_viewport_frame_async(viewport_api)
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

    async def test_get_viewport_from_window_name(self):
        '''Test getting a default Viewport from a Window without a name'''
        viewport_window = omni.kit.viewport.utility.get_viewport_from_window_name()
        self.assertIsNotNone(viewport_window)

    async def test_get_viewport_from_window_name_with_name(self):
        '''Test getting a default Viewport from a Window name'''
        viewport_window = omni.kit.viewport.utility.get_viewport_from_window_name(window_name='Viewport')
        self.assertIsNotNone(viewport_window)

    async def test_get_active_viewport(self):
        '''Test getting a default Viewport'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        viewport_api = omni.kit.viewport.utility.get_active_viewport(usd_context_name='')
        self.assertIsNotNone(viewport_api)

    async def test_get_viewport_from_non_existant_window_name_with_name(self):
        '''Test getting a non-existent Viewport via Window name'''
        viewport_window = omni.kit.viewport.utility.get_viewport_from_window_name(window_name='NotExisting')
        self.assertIsNone(viewport_window)

    async def test_get_non_existant_viewport(self):
        '''Test getting a non-existent Viewport via UsdContext name'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport(usd_context_name='NotExisting')
        self.assertIsNone(viewport_api)

    async def test_get_camera_path_api(self):
        '''Test camera access API'''
        # Test camera-path as an Sdf.Path
        cam_path = omni.kit.viewport.utility.get_viewport_window_camera_path()
        self.assertTrue(bool(cam_path))
        self.assertTrue(isinstance(cam_path, Sdf.Path))

        cam_path = omni.kit.viewport.utility.get_viewport_window_camera_path(window_name='Viewport')
        self.assertTrue(bool(cam_path))
        self.assertTrue(isinstance(cam_path, Sdf.Path))

        cam_path = omni.kit.viewport.utility.get_viewport_window_camera_path(window_name='NO_Viewport')
        self.assertIsNone(cam_path)

        cam_path = omni.kit.viewport.utility.get_active_viewport_camera_path()
        self.assertTrue(bool(cam_path))
        self.assertTrue(isinstance(cam_path, Sdf.Path))

        cam_path = omni.kit.viewport.utility.get_active_viewport_camera_path(usd_context_name='')
        self.assertTrue(bool(cam_path))
        self.assertTrue(isinstance(cam_path, Sdf.Path))

        cam_path = omni.kit.viewport.utility.get_active_viewport_camera_path(usd_context_name='DoesntExist')
        self.assertIsNone(cam_path)

        # Test camera-path as a string
        cam_path_str = omni.kit.viewport.utility.get_viewport_window_camera_string()
        self.assertTrue(bool(cam_path_str))
        self.assertTrue(isinstance(cam_path_str, str))

        cam_path_str = omni.kit.viewport.utility.get_viewport_window_camera_string(window_name='Viewport')
        self.assertTrue(bool(cam_path_str))
        self.assertTrue(isinstance(cam_path_str, str))

        cam_path_str = omni.kit.viewport.utility.get_viewport_window_camera_string(window_name='NO_Viewport')
        self.assertIsNone(cam_path_str)

        cam_path_str = omni.kit.viewport.utility.get_active_viewport_camera_string()
        self.assertTrue(bool(cam_path_str))
        self.assertTrue(isinstance(cam_path_str, str))

        cam_path_str = omni.kit.viewport.utility.get_active_viewport_camera_string(usd_context_name='')
        self.assertTrue(bool(cam_path_str))
        self.assertTrue(isinstance(cam_path_str, str))

        cam_path_str = omni.kit.viewport.utility.get_active_viewport_camera_string(usd_context_name='DoesntExist')
        self.assertIsNone(cam_path_str)

        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        # Test property and method accessors are equal
        self.assertEqual(viewport_api.get_active_camera(), viewport_api.camera_path)

    async def test_setup_viewport_test_window(self):
        '''Test the test-suite utility setup_viewport_test_window'''
        from omni.kit.viewport.utility.tests import setup_viewport_test_window
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)
        resolution = viewport_api.resolution
        # Test the keywords arguments for the function
        await setup_viewport_test_window(resolution_x=128, resolution_y=128, position_x=10, position_y=10)
        # Test the arguments for the function and restore Viewport resolution
        await setup_viewport_test_window(resolution[0], resolution[1], 0, 0)

    async def test_viewport_resolution(self):
        '''Test the test-suite utility setup_viewport_test_window'''
        from omni.kit.viewport.utility.tests import setup_viewport_test_window
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        # Legacy Viewport needs some time to adopt the resolution changes
        try:
            resolution = viewport_api.resolution
            self.assertIsNotNone(resolution)

            full_resolution = viewport_api.full_resolution
            self.assertEqual(resolution, full_resolution)

            resolution_scale = viewport_api.resolution_scale
            # Resolution scale factor should be 1 by default
            self.assertEqual(resolution_scale, 1.0)

            viewport_api.resolution_scale = 0.5
            await self.wait_for_resolution_change(viewport_api)

            # Resolution scale factor should stick
            self.assertEqual(viewport_api.resolution_scale, 0.5)
            # Full resolution should still be the same
            self.assertEqual(viewport_api.full_resolution, full_resolution)
            # New resolution should now be half of the original
            self.assertEqual(viewport_api.resolution, (resolution[0] * 0.5, resolution[1] * 0.5))
        finally:
            viewport_api.resolution_scale = 1.0
            self.assertEqual(viewport_api.resolution_scale, 1.0)

    async def test_testsuite_capture_helpers(self):
        '''Test the API exposed to assist other extensions testing/capturing Viewport'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        from omni.kit.viewport.utility.tests.capture import viewport_capture, capture_viewport_and_wait
        # Test keyword arguments with an explicit Viewport
        await capture_viewport_and_wait(image_name='test_testsuite_capture_helper_01', output_img_dir=str(TEST_OUTPUT), viewport = viewport_api)

        # Test arguments with an implicit Viewport
        await capture_viewport_and_wait('test_testsuite_capture_helper_02', str(TEST_OUTPUT))

    async def test_legacy_as_new_api(self):
        '''Test the new API against a new or legacy Viewport'''

        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        self.assertEqual(viewport_api.camera_path.pathString, '/OmniverseKit_Persp')

        # Test camera property setter
        viewport_api.camera_path = '/OmniverseKit_Top'
        self.assertEqual(viewport_api.camera_path.pathString, '/OmniverseKit_Top')

        # Test camera method setter
        viewport_api.set_active_camera('/OmniverseKit_Persp')

        resolution = viewport_api.resolution
        self.assertIsNotNone(resolution)

        # Test access via legacy method-name
        self.assertEqual(resolution, viewport_api.get_texture_resolution())

        # Test setting via property
        viewport_api.resolution = (128, 128)
        await self.wait_for_resolution_change(viewport_api)
        self.assertEqual(viewport_api.resolution, (128, 128))

        # Test setting via method
        viewport_api.set_texture_resolution((256, 256))
        await self.wait_for_resolution_change(viewport_api)
        self.assertEqual(viewport_api.get_texture_resolution(), (256, 256))

        # Test matrix access
        self.assertIsNotNone(viewport_api.projection)
        self.assertIsNotNone(viewport_api.transform)
        self.assertIsNotNone(viewport_api.view)
        # Test world-NDC matrix convertor access
        self.assertIsNotNone(viewport_api.world_to_ndc)
        self.assertIsNotNone(viewport_api.ndc_to_world)

        # Test UsdContext and Stage access
        self.assertIsNotNone(viewport_api.usd_context_name)
        self.assertIsNotNone(viewport_api.usd_context)
        self.assertIsNotNone(viewport_api.stage)

        render_product_path = viewport_api.render_product_path
        self.assertIsNotNone(render_product_path)

        # Test access via legacy method-name
        self.assertEqual(render_product_path, viewport_api.get_render_product_path())

        # Test setting via property
        viewport_api.render_product_path = render_product_path

        # Test setting via method
        viewport_api.set_render_product_path(render_product_path)

        # Should have an id property
        self.assertIsNotNone(viewport_api.id)

        # Should have a frame_info dictionary
        self.assertIsNotNone(viewport_api.frame_info)

        # Test the NDC to texture-uv mapping API
        uv, valid = viewport_api.map_ndc_to_texture((0, 0))
        self.assertTrue(bool(valid))
        self.assertEqual(uv, (0.5, 0.5))

        # Test the NDC to texture-pixel mapping API
        pixel, valid = viewport_api.map_ndc_to_texture_pixel((0, 0))
        self.assertTrue(bool(valid))

        # Test API to set fill-frame resolution
        self.assertFalse(viewport_api.fill_frame)

        viewport_api.fill_frame = True
        await self.wait_for_resolution_change(viewport_api)
        self.assertTrue(viewport_api.fill_frame)

        viewport_api.fill_frame = False
        await self.wait_for_resolution_change(viewport_api)
        self.assertFalse(viewport_api.fill_frame)

    async def test_viewport_window_api(self):
        '''Test the legacy API exposure into the omni.ui window wrapper'''
        viewport_window = omni.kit.viewport.utility.get_active_viewport_window()
        self.assertIsNotNone(viewport_window)

        # Test the get_frame API
        frame_1 = viewport_window.get_frame('omni.kit.viewport.utility.test_frame_1')
        self.assertIsNotNone(frame_1)
        frame_2 = viewport_window.get_frame('omni.kit.viewport.utility.test_frame_1')
        self.assertEqual(frame_1, frame_2)

        frame_3 = viewport_window.get_frame('omni.kit.viewport.utility.test_frame_3')
        self.assertNotEqual(frame_1, frame_3)

        # Test setting visible attribute on Window
        viewport_window.visible = True
        self.assertTrue(viewport_window.visible)

    async def test_toggle_global_visibility(self):
        """Test the expected setting change for omni.kit.viewport.utility.toggle_global_visibility"""

        def collect_settings(settings):
            setting_keys = [
                "/persistent/app/viewport/Viewport/Viewport0/guide/grid/visible",
                "/persistent/app/viewport/Viewport/Viewport0/hud/deviceMemory/visible",
                "/persistent/app/viewport/Viewport/Viewport0/hud/hostMemory/visible",
                "/persistent/app/viewport/Viewport/Viewport0/hud/renderFPS/visible",
                "/persistent/app/viewport/Viewport/Viewport0/hud/renderProgress/visible",
                "/persistent/app/viewport/Viewport/Viewport0/hud/renderResolution/visible",
                "/persistent/app/viewport/Viewport/Viewport0/scene/cameras/visible",
                "/persistent/app/viewport/Viewport/Viewport0/scene/lights/visible",
                "/persistent/app/viewport/Viewport/Viewport0/scene/skeletons/visible",
            ]
            return {k: settings.get(k) for k in setting_keys}

        settings = carb.settings.get_settings()

        omni.kit.viewport.utility.toggle_global_visibility()
        options_1 = collect_settings(settings)

        omni.kit.viewport.utility.toggle_global_visibility()
        options_2 = collect_settings(settings)

        self.assertNotEqual(options_1, options_2)

        omni.kit.viewport.utility.toggle_global_visibility()
        options_3 = collect_settings(settings)
        self.assertEqual(options_1, options_3)

        omni.kit.viewport.utility.toggle_global_visibility()
        options_4 = collect_settings(settings)
        self.assertEqual(options_2, options_4)

    async def test_ui_scene_view_model_sync(self):
        '''Test API to autmoatically set view and projection on a SceneView model'''

        class ModelPoser:
            def __init__(model_self):
                model_self.set_items = set()

            def get_item(model_self, name: str):
                if name == 'view' or name == 'projection':
                    return name
                self.assertTrue(False)

            def set_floats(model_self, item, floats):
                self.assertEqual(len(floats), 16)
                self.assertTrue(item == model_self.get_item(item))
                model_self.set_items.add(item)

        class SceneViewPoser:
            def __init__(model_self):
                model_self.model = ModelPoser()

        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        scene_view = SceneViewPoser()
        # Test add_scene_view API
        viewport_api.add_scene_view(scene_view)
        # Test both view and projection have been set into
        self.assertTrue('view' in scene_view.model.set_items)
        self.assertTrue('projection' in scene_view.model.set_items)
        # Test remove_scene_view API
        viewport_api.remove_scene_view(scene_view)

    async def test_legacy_drag_drop_helper(self):
        pickable = False
        add_outline = False

        def on_drop_accepted_fn(url):
            pass

        def on_drop_fn(url, prim_path, unused_viewport_name, usd_context_name):
            pass

        def on_pick_fn(payload, prim_path, usd_context_name):
            pass

        dd_from_args = omni.kit.viewport.utility.create_drop_helper(
            pickable, add_outline, on_drop_accepted_fn, on_drop_fn, on_pick_fn
        )
        self.assertIsNotNone(dd_from_args)

        dd_from_kw = omni.kit.viewport.utility.create_drop_helper(
            pickable=pickable, add_outline=add_outline, on_drop_accepted_fn=on_drop_accepted_fn, on_drop_fn=on_drop_fn, on_pick_fn=on_pick_fn
        )
        self.assertIsNotNone(dd_from_kw)

    async def test_capture_file(self):
        '''Test the capture_viewport_to_file capture to a file'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertTrue(bool(viewport_api))

        # Make sure renderer is rendering images (also a good place to up the coverage %)
        await omni.kit.viewport.utility.next_viewport_frame_async(viewport_api)

        file = TEST_OUTPUT.joinpath('capture_01.png')
        cap_obj = omni.kit.viewport.utility.capture_viewport_to_file(viewport_api, file_path=str(file))
        # API should return an object we can await on
        self.assertIsNotNone(cap_obj)

        # Test that we can in fact wait on that object
        result = await cap_obj.wait_for_result(completion_frames=30)
        self.assertTrue(result)

        # File should exists by now
        omni.kit.renderer_capture.acquire_renderer_capture_interface().wait_async_capture()
        self.assertTrue(file.exists())

    async def test_capture_file_with_exr_compression(self):
        '''Test the capture_viewport_to_file capture to a file'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertTrue(bool(viewport_api))

        # Make sure renderer is rendering images (also a good place to up the coverage %)
        await omni.kit.viewport.utility.next_viewport_frame_async(viewport_api)

        format_desc = {}
        format_desc["format"] = "exr"
        format_desc["compression"] = "b44"

        file = TEST_OUTPUT.joinpath(f'capture_{format_desc["compression"]}.{format_desc["format"]}')
        cap_obj = omni.kit.viewport.utility.capture_viewport_to_file(viewport_api, file_path=str(file), format_desc=format_desc)
        # API should return an object we can await on
        self.assertIsNotNone(cap_obj)

        # Test that we can in fact wait on that object
        result = await cap_obj.wait_for_result(completion_frames=30)
        self.assertTrue(result)

        # File should exists by now
        omni.kit.renderer_capture.acquire_renderer_capture_interface().wait_async_capture()
        self.assertTrue(file.exists())

    async def test_capture_file_str_convert(self):
        '''Test the capture_viewport_to_file capture to a file when passed an path-like object'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertTrue(bool(viewport_api))

        # Make sure renderer is rendering images (also a good place to up the coverage %)
        await omni.kit.viewport.utility.next_viewport_frame_async(viewport_api)

        file = TEST_OUTPUT.joinpath('capture_02.png')
        cap_obj = omni.kit.viewport.utility.capture_viewport_to_file(viewport_api, file_path=file)
        # API should return an object we can await on
        self.assertIsNotNone(cap_obj)

        # Test that we can in fact wait on that object
        result = await cap_obj.wait_for_result(completion_frames=15)
        self.assertTrue(result)

        # File should exists by now
        # self.assertTrue(file.exists())

    async def test_capture_to_buffer(self):
        '''Test the capture_viewport_to_file capture to a callback function'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertTrue(bool(viewport_api))

        # Make sure renderer is rendering images (also a good place to up the coverage %)
        await omni.kit.viewport.utility.next_viewport_frame_async(viewport_api)

        callback_called = False
        def capture_callback(*args, **kwargs):
            nonlocal callback_called
            callback_called = True

        cap_obj = omni.kit.viewport.utility.capture_viewport_to_buffer(viewport_api, capture_callback)
        # API should return an object we can await on
        self.assertIsNotNone(cap_obj)

        # Test that we can in fact wait on that object
        result = await cap_obj.wait_for_result()
        self.assertTrue(result)

        # Callback should have been called
        self.assertTrue(callback_called)

    async def test_new_viewport_api(self):
        '''Test the ability to create a new Viewport and retrieve the number of Viewports open'''
        num_vp_1 = omni.kit.viewport.utility.get_num_viewports()
        self.assertEqual(num_vp_1, 1)

        # Test Window creation, but that would require a renderer other than Storm which can only be created once
        # Which would make the tests run slower and in L2

        # new_window = omni.kit.viewport.utility.create_viewport_window('TEST WINDOW', width=128, height=128, camera_path='/OmniverseKit_Top')
        # self.assertEqual(new_window.viewport_api.camera_path.pathString, '/OmniverseKit_Top')

        # num_vp_2 = omni.kit.viewport.utility.get_num_viewports()
        # self.assertEqual(num_vp_2, 2)

    async def test_post_toast_api(self):
        # Post a message with a Viewport only
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        omni.kit.viewport.utility.post_viewport_message(viewport_api, "Message from ViewportAPI")

        # Post a message with the same API, but a Window
        viewport_window = omni.kit.viewport.utility.get_active_viewport_window()
        omni.kit.viewport.utility.post_viewport_message(viewport_window, "Message from ViewportWindow")

        # Post a message with the same API, but with a method
        viewport_window._post_toast_message("Message from ViewportWindow method")

    async def test_disable_picking(self):
        '''Test ability to disable picking on a Viewport or ViewportWindow'''
        from omni.kit import ui_test

        viewport_window = omni.kit.viewport.utility.get_active_viewport_window()
        self.assertIsNotNone(viewport_window)

        # viewport_window.position_x = 0
        # viewport_window.position_y = 0
        # viewport_window.width = TEST_WIDTH
        # viewport_window.height = TEST_HEIGHT

        viewport_api = viewport_window.viewport_api
        self.assertIsNotNone(viewport_api)

        usd_cube = UsdGeom.Cube.Define(viewport_window.viewport_api.stage, "/cube")
        usd_cube.GetSizeAttr().Set(100)

        await omni.kit.viewport.utility.next_viewport_frame_async(viewport_api)

        async def test_selection_rect(wait_frames: int = 5):
            selection = viewport_api.usd_context.get_selection()
            self.assertIsNotNone(selection)

            selection.set_selected_prim_paths([], False)
            selected_prims = selection.get_selected_prim_paths()
            self.assertFalse(bool(selected_prims))

            for _ in range(wait_frames):
                await omni.kit.app.get_app().next_update_async()

            await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(100, 100), ui_test.Vec2(400, 400))

            for _ in range(wait_frames):
                await omni.kit.app.get_app().next_update_async()

            return selection.get_selected_prim_paths()

        # Test initial selection works as expected
        selection = await test_selection_rect()
        self.assertTrue(len(selection) == 1)
        self.assertTrue(selection[0] == '/cube')

        # Test disabling selection on the Window leads to no selection
        picking_disabled = omni.kit.viewport.utility.disable_selection(viewport_window)
        selection = await test_selection_rect()
        self.assertTrue(len(selection) == 0)
        del picking_disabled

        # Test restore of selection works as expected
        selection = await test_selection_rect()
        self.assertTrue(len(selection) == 1)
        self.assertTrue(selection[0] == '/cube')

        # Test disabling selection on the Viewport leads to no selection
        picking_disabled = omni.kit.viewport.utility.disable_selection(viewport_api)
        selection = await test_selection_rect()
        self.assertTrue(len(selection) == 0)
        del picking_disabled

    async def test_frame_viewport(self):

        time = Usd.TimeCode.Default()

        def set_camera(cam_path: str, camera_pos=None, target_pos=None):
            from omni.kit.viewport.utility.camera_state import ViewportCameraState
            camera_state = ViewportCameraState(cam_path)
            camera_state.set_position_world(camera_pos, True)
            camera_state.set_target_world(target_pos, True)

        def test_camera_position(cam_path: str, expected_pos: Gf.Vec3d):
            prim = viewport_api.stage.GetPrimAtPath(cam_path)
            camera = UsdGeom.Camera(prim) if prim else None
            world_xform = camera.ComputeLocalToWorldTransform(time)
            world_pos = world_xform.Transform(Gf.Vec3d(0, 0, 0))
            for w_pos, ex_pos in zip(world_pos, expected_pos):
                self.assertAlmostEqual(float(w_pos), float(ex_pos), 4)

        viewport_window = omni.kit.viewport.utility.get_active_viewport_window()
        self.assertIsNotNone(viewport_window)
        viewport_api = viewport_window.viewport_api

        usd_cube1 = UsdGeom.Cube.Define(viewport_window.viewport_api.stage, "/cube1")
        #usd_cube1.GetSizeAttr().Set(10)
        usd_cube1_xformable = UsdGeom.Xformable(usd_cube1.GetPrim())
        usd_cube1_xformable.AddTranslateOp()
        attr = usd_cube1.GetPrim().GetAttribute("xformOp:translate")
        attr.Set((200, 800, 4))

        usd_cube2 = UsdGeom.Cube.Define(viewport_window.viewport_api.stage, "/cube2")
        #usd_cube2.GetSizeAttr().Set(100)

        await omni.kit.viewport.utility.next_viewport_frame_async(viewport_api)

        selection = viewport_api.usd_context.get_selection()
        self.assertIsNotNone(selection)

        camera_path = '/OmniverseKit_Persp'
        test_camera_position(camera_path, Gf.Vec3d(500, 500, 500))

        # select cube1
        selection.set_selected_prim_paths(["/cube1"], True)
        # frame to the selection
        omni.kit.viewport.utility.frame_viewport_selection(viewport_api=viewport_api)
        # test
        test_camera_position(camera_path, Gf.Vec3d(202.49306, 802.49306, 6.49306))

        # select cube2
        selection.set_selected_prim_paths(["/cube2"], True)
        # frame to the selection
        omni.kit.viewport.utility.frame_viewport_selection(viewport_api=viewport_api)
        # test
        test_camera_position(camera_path, Gf.Vec3d(2.49306, 2.49306, 2.49306))
        # unselect
        selection.set_selected_prim_paths([], True)
        # reset camera position
        set_camera(camera_path, (500, 500, 500), (0, 0, 0))
        test_camera_position(camera_path, Gf.Vec3d(500, 500, 500))
        # frame. Because nothing is selected, it should frame to all.
        omni.kit.viewport.utility.frame_viewport_selection(viewport_api=viewport_api)
        test_camera_position(camera_path, Gf.Vec3d(522.65586, 822.65585, 424.65586))
        # unselect
        selection.set_selected_prim_paths([], True)
        # reset camera position
        set_camera(camera_path, (500, 500, 500), (0, 0, 0))
        test_camera_position(camera_path, Gf.Vec3d(500, 500, 500))
        # no frame on cube2 without to select it
        omni.kit.viewport.utility.frame_viewport_prims(viewport_api=viewport_api, prims=["/cube2"])
        # should be the same as when we select
        test_camera_position(camera_path, Gf.Vec3d(2.49306, 2.49306, 2.49306))
        # reset camera position
        set_camera(camera_path, (500, 500, 500), (0, 0, 0))
        test_camera_position(camera_path, Gf.Vec3d(500, 500, 500))
        # try on cube1
        omni.kit.viewport.utility.frame_viewport_prims(viewport_api=viewport_api, prims=["/cube1"])
        test_camera_position(camera_path, Gf.Vec3d(202.49306, 802.49306, 6.49306))
        # call frame on prims with no list given
        omni.kit.viewport.utility.frame_viewport_prims(viewport_api=viewport_api)
        # camera should not move
        test_camera_position(camera_path, Gf.Vec3d(202.49306, 802.49306, 6.49306))

    async def test_disable_context_menu(self):
        '''Test ability to disable context-menu on a Viewport or ViewportWindow'''
        from omni.kit import ui_test
        ctx_menu_wait = 50

        #
        # Initial checks about assumption that objects are reachable and that no context manu is visible
        #
        ui_viewport = ui_test.find("Viewport")
        self.assertIsNotNone(ui_viewport)
        self.assertIsNone(ui.Menu.get_current())

        #
        # Test context-menu is working by default
        #
        await ui_viewport.right_click(human_delay_speed=ctx_menu_wait)
        self.assertIsNotNone(ui.Menu.get_current())

        #
        # Test disabling context-menu with a ViewportWindow
        #
        viewport_window = omni.kit.viewport.utility.get_active_viewport_window()
        self.assertIsNotNone(viewport_window)

        context_menu_disabled = omni.kit.viewport.utility.disable_context_menu(viewport_window)
        await ui_viewport.right_click(human_delay_speed=ctx_menu_wait)
        self.assertIsNone(ui.Menu.get_current())
        del context_menu_disabled

        # Context menu should work again
        await ui_viewport.right_click(human_delay_speed=ctx_menu_wait)
        self.assertIsNotNone(ui.Menu.get_current())

        #
        # Test disabling context-menu with a Viewport instance
        #
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        context_menu_disabled = omni.kit.viewport.utility.disable_context_menu(viewport_api)
        await ui_viewport.right_click(human_delay_speed=ctx_menu_wait)
        self.assertIsNone(ui.Menu.get_current())
        del context_menu_disabled

        # Context menu should work again
        await ui_viewport.right_click(human_delay_speed=ctx_menu_wait)
        self.assertIsNotNone(ui.Menu.get_current())

        #
        # Test disabling context-menu globally
        #
        context_menu_disabled = omni.kit.viewport.utility.disable_context_menu()
        await ui_viewport.right_click(human_delay_speed=ctx_menu_wait)
        self.assertIsNone(ui.Menu.get_current())
        del context_menu_disabled

        # Context menu should work again
        await ui_viewport.right_click(human_delay_speed=ctx_menu_wait)
        self.assertIsNotNone(ui.Menu.get_current())

    async def testget_ground_plane_info(self):
        '''Test results from get_ground_plane_info'''
        viewport_api = omni.kit.viewport.utility.get_active_viewport()
        self.assertIsNotNone(viewport_api)

        async def get_camera_ground_plane(path: str, ortho_special: bool = True, wait_frames: int = 3):
            app = omni.kit.app.get_app()
            viewport_api.camera_path = path
            for _ in range(wait_frames):
                await omni.kit.app.get_app().next_update_async()
            return omni.kit.viewport.utility.get_ground_plane_info(viewport_api, ortho_special)

        def test_results(results, normal, planes):
            self.assertTrue(Gf.IsClose(results[0], normal, 1e-5))
            self.assertEqual(results[1], planes)

        # Test ground plane info against Y-up stage
        UsdGeom.SetStageUpAxis(viewport_api.stage, UsdGeom.Tokens.y)
        persp_info = await get_camera_ground_plane('/OmniverseKit_Persp')
        front_info = await get_camera_ground_plane('/OmniverseKit_Front')
        top_info = await get_camera_ground_plane('/OmniverseKit_Top')
        right_info = await get_camera_ground_plane('/OmniverseKit_Right')
        right_info_world = await get_camera_ground_plane('/OmniverseKit_Right', False)

        test_results(persp_info, Gf.Vec3d(0, 1, 0), ['x', 'z'])
        test_results(front_info, Gf.Vec3d(0, 0, 1), ['x', 'y'])
        test_results(top_info, Gf.Vec3d(0, 1, 0), ['x', 'z'])
        test_results(right_info, Gf.Vec3d(1, 0, 0), ['y', 'z'])
        test_results(right_info_world, Gf.Vec3d(0, 1, 0), ['x', 'z'])

        # Test ground plane info against Z-up stage
        UsdGeom.SetStageUpAxis(viewport_api.stage, UsdGeom.Tokens.z)
        persp_info = await get_camera_ground_plane('/OmniverseKit_Persp')
        front_info = await get_camera_ground_plane('/OmniverseKit_Front')
        top_info = await get_camera_ground_plane('/OmniverseKit_Top')
        right_info = await get_camera_ground_plane('/OmniverseKit_Right')
        right_info_world = await get_camera_ground_plane('/OmniverseKit_Right', False)

        test_results(persp_info, Gf.Vec3d(0, 0, 1), ['x', 'y'])
        test_results(front_info, Gf.Vec3d(1, 0, 0), ['y', 'z'])
        test_results(top_info, Gf.Vec3d(0, 0, 1), ['x', 'y'])
        test_results(right_info, Gf.Vec3d(0, 1, 0), ['x', 'z'])
        test_results(right_info_world, Gf.Vec3d(0, 0, 1), ['x', 'y'])
