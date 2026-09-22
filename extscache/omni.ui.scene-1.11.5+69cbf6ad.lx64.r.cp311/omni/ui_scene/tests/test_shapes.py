## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##


from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
from omni.ui_scene import scene as sc
from omni.ui import color as cl
import omni.ui as ui
import math
import carb
import omni.kit
from omni.kit import ui_test
from .gesture_manager_utils import Manager
from functools import partial
from numpy import pi, cos, sin, arccos
import random

import asyncio


KIT_ROOT = Path(carb.tokens.get_tokens_interface().resolve("${kit}")).parent.parent.parent
CURRENT_PATH = Path(__file__).parent.joinpath("../../../data")


class TestShapes(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = KIT_ROOT.joinpath("data/tests/omni.ui.tests")
        random.seed(10)

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def test_general(self):
        window = await self.create_test_window(width=512, height=256)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
            with scene_view.scene:
                # line
                sc.Line([-2.5, -1.0, 0], [-1.5, -1.0, 0], color=cl.red, thickness=5)
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(1, 0.2, 0)):
                    # Rectangle
                    sc.Rectangle(color=cl.blue)
                    # wireframe rectangle
                    sc.Rectangle(2, 1.3, thickness=5, wireframe=True)
                # arc
                sc.Arc(3, begin=math.pi, end=4, thickness=5, wireframe=True, color=cl.yellow)
                # label
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(1, -2, 0)):
                    sc.Label("NVIDIA Omniverse", alignment=ui.Alignment.CENTER, color=cl.green, size=50)

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_image(self):
        window = await self.create_test_window(width=512, height=256)
        sc_image = None
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
            with scene_view.scene:
                # image
                filename = f"{CURRENT_PATH}/main_ov_logo_square.png"
                sc_image = sc.Image(filename)

        # removing this wait leads to an error of png unload wait time exceeded limit of 20000 ms!
        for _ in range(50):
            image_ready = sc_image.image_provider.is_reference_valid
            if image_ready:
                break
            await asyncio.sleep(0.1)
            await self.wait_n_updates(1)

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_distant_shape(self):
        window = await self.create_test_window(width=256, height=256)
        # Projection matrix
        proj = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]

        # Move camera
        transl = sc.Matrix44.get_translation_matrix(100000000000, 100000000000, 119999998)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, transl), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )

            with scene_view.scene:
                with sc.Transform(
                    transform=sc.Matrix44.get_translation_matrix(-100000000000, -100000000000, -119999995)
                ):
                    sc.Line([-1, -1, -1], [1, -1, -1])
                    sc.Line([-1, 1, -1], [1, 1, -1])
                    sc.Line([-1, -1, 1], [1, -1, 1])
                    sc.Line([-1, 1, 1], [1, 1, 1])

                    sc.Line([-1, -1, -1], [-1, 1, -1])
                    sc.Line([1, -1, -1], [1, 1, -1])
                    sc.Line([-1, -1, 1], [-1, 1, 1])
                    sc.Line([1, -1, 1], [1, 1, 1])

                    sc.Line([-1, -1, -1], [-1, -1, 1])
                    sc.Line([-1, 1, -1], [-1, 1, 1])
                    sc.Line([1, -1, -1], [1, -1, 1])
                    sc.Line([1, 1, -1], [1, 1, 1])

        await self.wait_n_updates(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_points(self):
        window = await self.create_test_window(width=512, height=200)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
            with scene_view.scene:
                point_count = 36
                points = []
                sizes = []
                colors = []
                for i in range(point_count):
                    weight = i / point_count
                    angle = 2.0 * math.pi * weight
                    points.append([math.cos(angle), math.sin(angle), 0])
                    colors.append([weight, 1 - weight, 1, 1])
                    sizes.append(6 * (weight + 1.0 / point_count))
                sc.Points(points, colors=colors, sizes=sizes)

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_polygon_mesh(self):
        window = await self.create_test_window(width=512, height=200)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
            with scene_view.scene:
                point_count = 36

                # Form the mesh data
                points = []
                vertex_indices = []
                sizes = []
                colors = []
                for i in range(point_count):
                    weight = i / point_count
                    angle = 2.0 * math.pi * weight
                    vertex_indices.append(i)
                    points.append([math.cos(angle) * weight, -math.sin(angle) * weight, 0])
                    colors.append([weight, 1 - weight, 1, 1])
                    sizes.append(6 * (weight + 1.0 / point_count))

                # Draw the mesh
                sc.PolygonMesh(points, colors, [point_count], vertex_indices)

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_polygon_mesh_intersection(self):
        """Click on the different polygon mesh to get the s and t"""
        await self.create_test_area(width=1440, height=900, block_devices=False)
        self.intersection = False
        self.face_id = -1
        self.s = -1.0
        self.t = -1.0

        def _on_shape_clicked(shape):
            """Called when the user clicks the point"""
            self.intersection = True
            self.face_id = shape.gesture_payload.face_id
            self.s = shape.gesture_payload.s
            self.t = shape.gesture_payload.t

        window = ui.Window("test_polygon_mesh_intersection", width=700, height=500)
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )
            with scene_view.scene:
                select = sc.ClickGesture(_on_shape_clicked)
                # two triangles
                point_count = 3
                points = [[-1, -1, 0], [2, -1, 0], [3, 1, 0], [2, -1, 0], [4, 0, -1], [3, 1, 0]]
                vertex_indices = [0, 1, 2, 3, 4, 5]
                colors = [[1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1]]
                sc.PolygonMesh(points, colors, [point_count, point_count], vertex_indices, gesture=select)

        await ui_test.wait_n_updates(10)
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(850, 300))
        await ui_test.wait_n_updates(10)
        self.assertEqual(self.intersection, True)
        self.assertEqual(self.face_id, 0)
        self.assertAlmostEqual(self.s, 0.18666667622178545)
        self.assertAlmostEqual(self.t, 0.7600000000000001)

        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(870, 300))
        await ui_test.wait_n_updates(10)
        self.assertEqual(self.intersection, True)
        self.assertEqual(self.face_id, 1)
        self.assertAlmostEqual(self.s, 0.16000002187854384)
        self.assertAlmostEqual(self.t, 0.6799999891122469)

    async def test_polygon_mesh_not_intersection(self):
        """Click on a polygon mesh to see shape is not clicked"""
        await self.create_test_area(width=1440, height=900, block_devices=False)
        self.intersection = False

        def _on_shape_clicked(shape):
            """Called when the user clicks the point"""
            self.intersection = True

        window = ui.Window("test_polygon_mesh_not_intersection", width=700, height=500)
        proj = [1.7, 0, 0, 0, 0, 3, 0, 0, 0, 0, -1, -1, 0, 0, -2, 0]
        view = sc.Matrix44.get_translation_matrix(0, 0, -6)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )

            with scene_view.scene:
                select = sc.ClickGesture(_on_shape_clicked)
                # a concave quadrangle
                point_count = 4
                points = [[-1, -1, 0], [1, -1, 0], [0, -0.5, 0], [1, 1, 0]]
                vertex_indices = [0, 1, 2, 3]
                colors = [[1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1]]
                sc.PolygonMesh(points, colors, [point_count], vertex_indices, gesture=select)

        await ui_test.wait_n_updates(10)
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(740, 350))
        await ui_test.wait_n_updates(10)
        self.assertEqual(self.intersection, False)
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(700, 350))
        await ui_test.wait_n_updates(10)
        self.assertEqual(self.intersection, True)

    async def __test_textured_mesh(self, golden_img_name: str, **kwargs):
        """Test polygon mesh with texture"""
        window = await self.create_test_window(width=512, height=200)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
            with scene_view.scene:
                point_count = 4
                # Form the mesh data
                vertex_indices = [0, 2, 3, 1]
                points = [(-1, -1, 0), (1, -1, 0), (-1, 1, 0), (1, 1, 0)]
                colors = [[0, 1, 0, 1], [0, 1, 0, 1], [0, 1, 0, 1], [0, 1, 0, 1]]
                # UVs specified in USD coordinate system
                uvs = [(0, 0), (0, 1), (1, 1), (1, 0)]
                # Flip V coordinate is requested
                if kwargs.get("legacy_flipped_v") is None:
                    uvs = [(uv[0], 1.0 - uv[1]) for uv in uvs]
                # Draw the mesh
                filename = f"{CURRENT_PATH}/main_ov_logo_square.png"
                tm = sc.TexturedMesh(filename, uvs, points, colors, [point_count], vertex_indices, **kwargs)
                # Test that get of uv property is equal to input in both cases
                self.assertTrue(tm.uvs, uvs)

        # removing this wait leads to an error of png unload wait time exceeded limit of 20000 ms!
        for _ in range(50):
            await asyncio.sleep(0.1)
            await self.wait_n_updates(1)

        await self.finalize_test(golden_img_name=golden_img_name, golden_img_dir=self._golden_img_dir)

    async def test_textured_mesh_legacy(self):
        """Test legacy polygon mesh with texture (flipped V)"""
        await self.__test_textured_mesh(golden_img_name="test_textured_mesh_legacy.png")

    async def test_textured_mesh(self):
        """Test polygon mesh with texture (USD coordinates)"""
        await self.__test_textured_mesh(golden_img_name="test_textured_mesh.png", legacy_flipped_v=False)

    async def test_textured_mesh_intersection(self):
        """Click on the different polygon mesh to get the s and t"""
        await self.create_test_area(width=1440, height=900, block_devices=False)
        self.intersection = False
        self.face_id = -1
        self.u = -1.0
        self.v = -1.0
        self.s = -1.0
        self.t = -1.0

        def _on_shape_clicked(shape):
            """Called when the user clicks the point"""
            self.intersection = True
            self.face_id = shape.gesture_payload.face_id
            self.u = shape.gesture_payload.u
            self.v = shape.gesture_payload.v
            self.s = shape.gesture_payload.s
            self.t = shape.gesture_payload.t

        window = ui.Window("test_textured_mesh_intersection", width=700, height=700)
        proj = [1.7, 0, 0, 0, 0, 3, 0, 0, 0, 0, -1, -1, 0, 0, -2, 0]
        view = sc.Matrix44.get_translation_matrix(0, 0, -6)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )

            with scene_view.scene:
                select = sc.ClickGesture(_on_shape_clicked)
                # Form the mesh data
                point_count = 4
                points = [
                    [-3, -3, 0],
                    [3, -3, 0],
                    [3, 3, 0],
                    [-3, 3, 0],
                    [-3, -6, 0],
                    [3, -6, 0],
                    [3, -3, 0],
                    [-3, -3, 0],
                ]
                vertex_indices = [0, 1, 2, 3, 4, 5, 6, 7]
                colors = [
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                ]
                filename = f"{CURRENT_PATH}/main_ov_logo_square.png"
                uvs = [[0, 1], [1, 1], [1, 0], [0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]
                sc.TexturedMesh(
                    filename, uvs, points, colors, [point_count, point_count], vertex_indices, gesture=select
                )

        await ui_test.wait_n_updates(10)
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(580, 130))
        await ui_test.wait_n_updates(10)
        self.assertEqual(self.face_id, 0)
        self.assertAlmostEqual(self.u, 0.03333332762122154)
        self.assertAlmostEqual(self.v, 0.18000000715255737)
        self.assertAlmostEqual(self.s, 0.03333332818826966)
        self.assertAlmostEqual(self.t, 0.8200000000000001)

    async def test_linear_curve(self):
        window = await self.create_test_window(width=512, height=512)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
            with scene_view.scene:
                sc.Curve(
                    [[-2.5, -1.0, 0], [-1.5, -1.0, 0], [-1.5, -2.0, 0], [1.0, 0.5, 0]],
                    curve_type=sc.Curve.CurveType.LINEAR,
                    colors=[cl.yellow, cl.blue, cl.yellow, cl.green],
                    thicknesses=[3.0, 1.5, 3.0, 3],
                )

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_curve_properties(self):
        """test with different colors and thicknesses"""
        window = await self.create_test_window(width=600, height=800)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
        with scene_view.scene:
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-4, 0, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    thicknesses=[1.0, 2.0, 3.0, 4.0],
                    curve_type=sc.Curve.CurveType.LINEAR,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-4, -2, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red],
                    thicknesses=[1.0, 2.0, 3.0],
                    curve_type=sc.Curve.CurveType.LINEAR,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-4, -4, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red, cl.blue],
                    thicknesses=[1.0, 2.0],
                    curve_type=sc.Curve.CurveType.LINEAR,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-4, -6, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red, [0, 1, 0, 1], cl.blue],
                    thicknesses=[1.5],
                    tessellation=7,
                    curve_type=sc.Curve.CurveType.LINEAR,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-4, -8, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red, [0, 1, 0, 1], cl.blue, cl.yellow],
                    tessellation=7,
                    curve_type=sc.Curve.CurveType.LINEAR,
                )

            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    thicknesses=[1.0, 2.0, 3.0, 4.0],
                    tessellation=4,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, -2, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red],
                    thicknesses=[1.0, 2.0, 3.0],
                    tessellation=4,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, -4, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red, cl.blue],
                    thicknesses=[1.0, 2.0],
                    tessellation=4,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, -6, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red, [0, 1, 0, 1], cl.blue],
                    thicknesses=[1.5],
                    tessellation=4,
                )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, -8, 0)):
                sc.Curve(
                    [[0.5, -1, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -1, 0]],
                    colors=[cl.red, [0, 1, 0, 1], cl.blue, cl.yellow],
                    tessellation=4,
                )

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_curve_intersection_linear(self):
        """Click different segments of the curve sets the curve to different colors"""

        def _on_shape_clicked(shape):
            """Called when the user clicks the point"""
            shape.colors = [cl.yellow]

        window = await self.create_test_window(width=512, height=256)
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )

            with scene_view.scene:
                select = sc.ClickGesture(_on_shape_clicked)
                mouse_action_sequence = [(0, 0, 0), (1, 1, 0)] + [(0, 1, 0)] * 10 + [(0, 0, 1), (0, 0, 0)]
                mouse_position_sequence = [(-0.023809523809523836, -0.19333333333333336)] * 14
                select.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
                sc.Curve(
                    [[-2.5, -1.0, 0], [-1.5, -1.0, 0], [-0.5, 0, 0], [0.5, -1, 0], [1.5, -1, 0]],
                    curve_type=sc.Curve.CurveType.LINEAR,
                    gesture=select,
                )

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_curve_intersection_distance(self):
        """Click different segments of the curve sets the curve to different colors"""
        self.curve_distance = 0.0

        def _on_shape_clicked(shape):
            """Called when the user clicks the point"""
            shape.colors = [cl.red]
            self.curve_distance = shape.gesture_payload.curve_distance

        window = await self.create_test_window(width=512, height=256)
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )

            with scene_view.scene:
                select = sc.ClickGesture(_on_shape_clicked)
                mouse_action_sequence = [(0, 0, 0), (1, 1, 0)] + [(0, 1, 0)] * 5 + [(0, 0, 1)] + [(0, 0, 0)] * 100
                mouse_position_sequence = [(0.0978835978835979, 0.04)] * 108
                select.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
                sc.Curve(
                    [[-1, 1.0, 0], [1, 0.2, 0], [1, -0.2, 0], [-1, -1, 0]],
                    thicknesses=[5.0],
                    colors=[cl.blue],
                    gesture=select,
                )

        await self.wait_n_updates(30)
        self.assertAlmostEqual(self.curve_distance, 0.4788618615426895)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_bezier_curve(self):
        window = await self.create_test_window(width=600, height=450)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=150)
        with scene_view.scene:
            sc.Curve(
                [
                    [-2.5, -1.0, 0],
                    [-1.5, 0, 0],
                    [-0.5, -1, 0],
                    [0.5, -1, 0],
                    [0.1, 0.6, 0],
                    [2.0, 0.6, 0],
                    [3.5, -1, 0],
                ],
                colors=[cl.red],
                thicknesses=[3.0],
                curve_type=sc.Curve.CurveType.LINEAR,
            )
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, -2, 0)):
                sc.Curve(
                    [
                        [-2.5, -1.0, 0],
                        [-1.5, 0, 0],
                        [-0.5, -1, 0],
                        [0.5, -1, 0],
                        [0.1, 0.6, 0],
                        [2.0, 0.6, 0],
                        [3.5, -1, 0],
                    ],
                    colors=[cl.red],
                    thicknesses=[3.0],
                    tessellation=9,
                )

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_bezier_curve_move(self):
        def move(transform: sc.Transform, shape: sc.AbstractShape):
            """Called by the gesture"""
            translate = shape.gesture_payload.moved
            # Move transform to the direction mouse moved
            current = sc.Matrix44.get_translation_matrix(*translate)
            transform.transform *= current

        window = await self.create_test_window(width=600, height=256)
        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )
            with scene_view.scene:
                transform = sc.Transform()
                with transform:
                    mouse_action_sequence = [
                        (0, 0, 0),
                        (1, 1, 0),
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 0, 1),
                        (0, 0, 0),
                    ]
                    mouse_position_sequence = [
                        (0.009, 0.22667),
                        (0.009, 0.22667),
                        (0.009, 0.22667),
                        (0.01126, 0.22667),
                        (0.2207, 0.2),
                        (0.5157, 0.186667),
                        (0.5157, 0.186667),
                        (0.5157, 0.186667),
                    ]
                    mrg = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
                    drag = sc.DragGesture(manager=mrg, on_changed_fn=partial(move, transform))
                    sc.Curve(
                        [[-1.5, -1.0, 0], [-0.5, 1, 0], [0.5, 0.8, 0], [1.5, -1, 0]],
                        colors=[cl.yellow],
                        thicknesses=[5.0, 1.5],
                        gesture=drag,
                    )

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    def _curves_on_sphere(self, num_curves, num_segs):
        """generate curves points on a sphere"""
        curves = []
        for i in range(0, num_curves):
            phi = arccos(1 - 2 * i / num_curves)
            theta = pi * (1 + 5**0.5) * i
            x, y, z = cos(theta) * sin(phi) + 0.5, sin(theta) * sin(phi) + 0.5, cos(phi) + 0.5
            curve = []
            curve.append([x, y, z])
            for j in range(0, num_segs):
                rx = (random.random() - 0.5) * 0.2
                ry = (random.random() - 0.5) * 0.2
                rz = (random.random() - 0.5) * 0.2
                curve.append([x + rx, y + ry, z + rz])
            curves.append(curve)
        return curves

    async def test_linear_curve_scalability(self):
        """we can have maximum 21 segments per curve with 10000 linear
        10000 curves
        21 segments per curve
        which has 22 vertices per curve
        """
        num_curves = 10000
        num_segs = 21
        curves = self._curves_on_sphere(num_curves, num_segs)

        window = await self.create_test_window(width=600, height=600)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=300)
            with scene_view.scene:
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-0.5, -1, 0)):
                    for curve in curves:
                        sc.Curve(
                            curve,
                            colors=[[curve[0][0], curve[0][1], curve[0][2], 1.0]],
                            curve_type=sc.Curve.CurveType.LINEAR,
                        )

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_bezier_curve_scalability(self):
        """we can have maximum 8920 curves with 3 segments per bezier curve and default 9 tessellation
        8920 curves
        3 segments per curve
        9 tessellation per curve
        which has 25 vertices per curve
        """
        num_curves = 8920
        num_segs = 3
        curves = self._curves_on_sphere(num_curves, num_segs)

        window = await self.create_test_window(width=600, height=600)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=300)
            with scene_view.scene:
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-0.5, -1, 0)):
                    for curve in curves:
                        sc.Curve(
                            curve,
                            colors=[[curve[0][0], curve[0][1], curve[0][2], 1.0]],
                            thicknesses=[1.0],
                        )

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_bezier_segment_scalability(self):
        """we can have maximum 27 curves per bezier curve with 999 segments and default 9 tessellation
        27 curves
        999 segments per curve
        9 tessellation per curve
        which has 7993 vertices per curve
        """
        num_curves = 27
        num_segs = 999  # the number has to be dividable by 3

        curves = []
        for i in range(0, num_curves):
            x = i % 6
            y = int(i / 6)
            z = random.random()
            curve = []
            curve.append([x, y, z])
            for j in range(0, num_segs):
                curve.append([x + random.random(), y + random.random(), z + random.random()])
            curves.append(curve)

        window = await self.create_test_window(width=1000, height=800)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=300)
            with scene_view.scene:
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-3, -4, 0)):
                    for curve in curves:
                        sc.Curve(
                            curve,
                            colors=[[1, 1, 0, 1.0]],
                            thicknesses=[1.0],
                        )

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_intersection_scalability(self):
        """for intersection workable, we can have maximum 3000 curves with 9 segments and 9 tessellation per curve
        3000 curves
        9 segments per curve
        9 tessellation per curve
        which has 73 vertices per curve
        """

        def move(transform: sc.Transform, shape: sc.AbstractShape):
            """Called by the gesture"""
            translate = shape.gesture_payload.moved
            # Move transform to the direction mouse moved
            current = sc.Matrix44.get_translation_matrix(*translate)
            transform.transform *= current

        num_curves = 3000
        num_segs = 9
        curves = self._curves_on_sphere(num_curves, num_segs)

        mouse_action_sequence = [(0, 0, 0), (1, 1, 0)] + [(0, 1, 0)] * 40 + [(0, 0, 1)] * 20 + [(0, 0, 0)] * 10
        mouse_position_sequence = (
            [(0.06981981981981988, -0.7333333333333334)] * 22
            + [(0.12387387387387383, -0.8844444444444444)] * 10
            + [(0.2635135135135136, -1.511111111111111)] * 10
            + [(0.6265765765765767, -1.98844444444444444)] * 10
            + [(1.84009009009009006, -2.9977777777777776)] * 20
        )

        window = await self.create_test_window(width=600, height=600)
        with window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=300)
            mgr = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
            with scene_view.scene:
                for curve in curves:
                    transform = sc.Transform(transform=sc.Matrix44.get_translation_matrix(-0.5, -1, 0))
                    with transform:
                        drag = sc.DragGesture(on_changed_fn=partial(move, transform), manager=mgr)
                        sc.Curve(curve, colors=[[random.random(), random.random(), random.random(), 1.0]], gesture=drag)

        await self.wait_n_updates(100)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_transparency(self):
        window = await self.create_test_window()
        with window.frame:
            with ui.ZStack():
                # Background
                ui.Rectangle(style={"background_color": ui.color(0.5, 0.5, 0.5)})

                scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT)
                with scene_view.scene:
                    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0.25, 0.25, -0.1)):
                        sc.Rectangle(1, 1, color=ui.color(1.0, 1.0, 0.0, 0.5))
                    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0)):
                        sc.Rectangle(1, 1, color=ui.color(1.0, 1.0, 1.0, 0.5))
                    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-0.25, -0.25, 0.1)):
                        sc.Rectangle(1, 1, color=ui.color(1.0, 0.0, 1.0, 0.5))

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_vertexindices(self):
        window = await self.create_test_window(500, 250)
        with window.frame:
            proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -10)
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )
            with scene_view.scene:
                # two triangles, the first one is red and second one is blue
                point_count = 3
                points = [[-1, -1, 0], [2, -1, 0], [3, 1, 0], [4, 0, -1], [3, 1, 0]]
                vertex_indices = [0, 1, 2, 1, 3, 2]
                colors = [[1, 0, 0, 1]] * 3 + [[0, 0, 1, 1]] * 3
                sc.PolygonMesh(points, colors, [point_count, point_count], vertex_indices)

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_polygon_mesh_wireframe(self):
        window = await self.create_test_window(500, 250)
        with window.frame:
            proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, -10)
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT, height=200
            )
            with scene_view.scene:
                # two triangles, the first one is red and second one is blue
                point_count = 3
                points = [[-1, -1, 0], [2, -1, 0], [3, 1, 0], [4, 0, -1], [3, 1, 0]]
                vertex_indices = [0, 1, 2, 1, 3, 2]
                colors = [[1, 0, 0, 1]] * 3 + [[0, 0, 1, 1]] * 3
                thicknesses = [3] * 6
                sc.PolygonMesh(
                    points, colors, [point_count, point_count], vertex_indices, thicknesses=thicknesses, wireframe=True
                )

        await self.wait_n_updates()
        await self.finalize_test(golden_img_dir=self._golden_img_dir)
