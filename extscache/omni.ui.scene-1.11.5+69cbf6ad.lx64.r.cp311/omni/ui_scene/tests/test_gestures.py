## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##


from .gesture_manager_utils import Manager
from functools import partial
from omni.ui import color as cl
from omni.ui_scene import scene as sc
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
from pathlib import Path
import carb
import omni.kit
import omni.ui as ui


KIT_ROOT = Path(carb.tokens.get_tokens_interface().resolve("${kit}")).parent.parent.parent


class TestGestures(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = KIT_ROOT.joinpath("data/tests/omni.ui.tests")

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def test_gesture_select(self):
        def _on_shape_clicked(shape):
            """Called when the user clicks the point"""
            shape.color = cl.red

        window = await self.create_test_window(width=512, height=256)
        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                height=200
            )

            with scene_view.scene:
                select = sc.ClickGesture(_on_shape_clicked)
                mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)]
                mouse_position_sequence = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
                select.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
                sc.Rectangle(color=cl.blue, gesture=select)

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_gesture_drag(self):
        class MyDragGesture(sc.DragGesture):
            def __init__(self):
                super().__init__()
                self.began_called = False
                self.changed_called = False
                self.ended_called = False

            def can_be_prevented(self, gesture):
                return True

            def on_began(self):
                self.began_called = True

            def on_changed(self):
                self.changed_called = True

            def on_ended(self):
                self.ended_called = True

        class PriorityManager(Manager):
            """
            Manager makes the gesture high priority
            """

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def can_be_prevented(self, gesture):
                return False

            def should_prevent(self, gesture, preventer):
                return gesture.state == sc.GestureState.CHANGED and (
                    preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED
                )

        window = await self.create_test_window()

        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
            )

            with scene_view.scene:
                # Click, move, release in the center
                drag = MyDragGesture()
                # Clicked, down, released
                mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)]
                mouse_position_sequence = [(0, 0), (0, 0), (0, 0), (0.1, 0), (0.1, 0), (0.1, 0)]
                drag.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
                rectangle = sc.Rectangle(color=cl.blue, gesture=drag)

        await self.wait_n_updates(30)

        self.assertTrue(drag.began_called)
        self.assertTrue(drag.changed_called)
        self.assertTrue(drag.ended_called)

        # Click, move, release on the side
        drag = MyDragGesture()
        mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)]
        mouse_position_sequence = [(0, 0.9), (0, 0.9), (0, 0.9), (0.1, 0.9), (0.1, 0.9), (0.1, 0.9)]
        drag.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
        rectangle.gestures = [drag]

        await self.wait_n_updates(30)

        self.assertFalse(drag.began_called)
        self.assertFalse(drag.changed_called)
        self.assertFalse(drag.ended_called)

        # Testing preventing
        drag = MyDragGesture()
        mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)]
        mouse_position_sequence = [(0, 0), (0, 0), (0, 0), (0.1, 0), (0.1, 0), (0.1, 0)]
        drag.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
        rectangle.gestures = [
            sc.DragGesture(manager=PriorityManager(mouse_action_sequence, mouse_position_sequence, scene_view)),
            drag,
        ]

        await self.wait_n_updates(30)

        self.assertTrue(drag.began_called)
        self.assertFalse(drag.changed_called)
        self.assertTrue(drag.ended_called)

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_gesture_callback(self):
        def move(transform: sc.Transform, shape: sc.AbstractShape):
            """Called by the gesture"""
            translate = shape.gesture_payload.moved
            # Move transform to the direction mouse moved
            current = sc.Matrix44.get_translation_matrix(*translate)
            transform.transform *= current

        window = await self.create_test_window(width=512, height=256)
        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                height=200
            )

            mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0),(0, 1, 0), (0, 0, 1), (0, 0, 0)]
            mouse_position_sequence = [(0, 0), (0, 0), (0.15, 0), (0.3, 0), (0.3, 0), (0.3, 0)]
            mgr = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
            with scene_view.scene:
                transform = sc.Transform()
                with transform:
                    sc.Line(
                        [-1, 0, 0],
                        [1, 0, 0],
                        color=cl.blue,
                        thickness=5,
                        gesture=sc.DragGesture(
                            manager = mgr,
                            on_changed_fn=partial(move, transform)
                        )
                    )

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_gesture_override(self):
        class Move(sc.DragGesture):
            def __init__(self, transform: sc.Transform):
                super().__init__()
                self.__transform = transform

            def on_began(self):
                self.sender.color = cl.red

            def on_changed(self):
                translate = self.sender.gesture_payload.moved
                # Move transform to the direction mouse moved
                current = sc.Matrix44.get_translation_matrix(*translate)
                self.__transform.transform *= current

            def on_ended(self):
                self.sender.color = cl.blue

        window = await self.create_test_window(width=512, height=256)
        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)

        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                height=200
            )
            with scene_view.scene:
                transform=sc.Transform()
                with transform:
                    move = Move(transform)
                    mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0),(0, 1, 0), (0, 0, 1), (0, 0, 0)]
                    mouse_position_sequence = [(0, 0), (0, 0), (-0.25, -0.07), (-0.6, -0.15), (-0.6, -0.15), (-0.6, -0.15)]
                    move.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
                    sc.Rectangle(color=cl.blue, gesture=move)

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_gesture_manager(self):
        class PrimeManager(Manager):
            def __init__(self, mouse_action_sequence, mouse_position_sequence, scene_view):
                super().__init__(mouse_action_sequence, mouse_position_sequence, scene_view)

            def should_prevent(self, gesture, preventer):
                # prime gesture always wins
                if preventer.name == "prime":
                    return True

        def move(transform: sc.Transform, shape: sc.AbstractShape):
            """Called by the gesture"""
            translate = shape.gesture_payload.moved
            current = sc.Matrix44.get_translation_matrix(*translate)
            transform.transform *= current

        window = await self.create_test_window(width=512, height=256)
        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                height=200
            )

            mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0),(0, 1, 0), (0, 0, 1), (0, 0, 0)]
            mouse_position_sequence = [(0, 0), (0, 0), (-0.25, -0.15), (-0.6, -0.3), (-0.6, -0.3), (-0.6, -0.3)]
            mgr = PrimeManager(mouse_action_sequence, mouse_position_sequence, scene_view)
            # create two cubes overlap with each other
            # since the red one has the name of prime, it wins the gesture of move
            with scene_view.scene:
                transform1 = sc.Transform()
                with transform1:
                    sc.Rectangle(
                        color=cl.blue,
                        gesture=sc.DragGesture(
                            manager=mgr,
                            on_changed_fn=partial(move, transform1)
                        )
                    )
                transform2 = sc.Transform()
                with transform2:
                    sc.Rectangle(
                        color=cl.red,
                        gesture=sc.DragGesture(
                            name="prime",
                            manager=mgr,
                            on_changed_fn=partial(move, transform2)
                        )
                    )

        await self.wait_n_updates(30)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_hover_gesture(self):
        class HoverGesture(sc.HoverGesture):
            def on_began(self):
                self.sender.color = cl.red

            def on_ended(self):
                self.sender.color = cl.blue

        window = await self.create_test_window()
        # Projection matrix
        proj = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -1)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT
            )

            mouse_action_sequence = [(0, 0, 0)] * 10
            # Move mouse close (2px) to the second line and after that on the
            # first line. The second line will be blue, the first one is the
            # red.
            mouse_position_sequence = [(-0, -1)] * 2 + [(0, 0.028)] * 3 + [(0, 0)] * 5
            mgr = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
            # create two cubes overlap with each other
            # since the red one has the name of prime, it wins the gesture of move
            with scene_view.scene:
                sc.Line([-1, -1, 0], [1, 1, 0], thickness=1, gesture=HoverGesture(manager=mgr))
                sc.Line([-1, 1, 0], [1, -0.9, 0], thickness=4, gesture=HoverGesture(manager=mgr))

        await self.wait_n_updates(9)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_intersection_thickness(self):
        class HoverGesture(sc.HoverGesture):
            def on_began(self):
                self.sender.color = cl.red

            def on_ended(self):
                self.sender.color = cl.blue

        window = await self.create_test_window()
        # Projection matrix
        proj = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -1)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT
            )

            mouse_action_sequence = [(0, 0, 0)] * 10
            # Move mouse close (about 4px) to the second line and after that on
            # the first line. The second line will be blue, the first one is the
            # red.
            mouse_position_sequence = [(-0, -1)] * 2 + [(0, 0.43)] * 3 + [(0, 0)] * 5
            mgr = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
            # create two cubes overlap with each other
            # since the red one has the name of prime, it wins the gesture of move
            with scene_view.scene:
                sc.Line([-1, -1, 0], [1, 1, 0], thickness=1, gesture=HoverGesture(manager=mgr))
                sc.Line(
                    [-1, 1, 0], [1, 0, 0], thickness=1, intersection_thickness=8, gesture=HoverGesture(manager=mgr)
                )

        await self.wait_n_updates(9)
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_hover_smallscale(self):
        # Flag that it was hovered
        hovered = [0, 0]

        class HoverGesture(sc.HoverGesture):
            def __init__(self, manager: sc.GestureManager):
                super().__init__(manager=manager)

            def on_began(self):
                if isinstance(self.sender, sc.Line):
                    hovered[0] = 1
                elif isinstance(self.sender, sc.Rectangle):
                    hovered[1] = 1
                self.sender.color = [0, 0, 1, 1]

            def on_ended(self):
                self.sender.color = [1, 1, 1, 1]

        class SmallScale(sc.Manipulator):
            def __init__(self, manager: sc.GestureManager):
                super().__init__()
                self.manager = manager

            def on_build(self):
                transform = sc.Matrix44.get_translation_matrix(-0.01, 0, 0)

                with sc.Transform(transform=transform):
                    sc.Line([0, 0.005, 0], [0, 0.01, 0], gestures=HoverGesture(manager=self.manager))
                    sc.Rectangle(0.01, 0.01, gestures=HoverGesture(manager=self.manager))

        window = await self.create_test_window()
        proj = [
            4.772131,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            7.987040,
            0.000000,
            0.000000,
            0.000000,
            0.000000,
            -1.002002,
            -1.000000,
            0.000000,
            0.000000,
            -0.200200,
            0.000000,
        ]
        view = [
            0.853374,
            -0.124604,
            0.506188,
            0.000000,
            -0.000000,
            0.971013,
            0.239026,
            0.000000,
            -0.521299,
            -0.203979,
            0.828638,
            0.000000,
            0.008796,
            -0.003659,
            -0.198528,
            1.000000,
        ]
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view), aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT
            )

            mouse_action_sequence = [(0, 0, 0)] * 10
            # Move mouse close (about 4px) to the second line and after that on
            # the first line. The second line will be blue, the first one is the
            # red.
            mouse_position_sequence = [(-0, -1)] * 2 + [(0, 0)] * 3 + [(0, 0.1)] * 5
            mgr = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)

            with scene_view.scene:
                SmallScale(mgr)

        await self.wait_n_updates(9)

        self.assertTrue(hovered[0])
        self.assertTrue(hovered[1])

        await self.finalize_test_no_image()

    async def test_gesture_click(self):
        single_click, double_click = False, False

        def _on_shape_clicked(shape):
            nonlocal single_click
            single_click = True

        def _on_shape_double_clicked(shape):
            nonlocal double_click
            double_click = True

        window = await self.create_test_window(width=1440, height=900, block_devices=False)
        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                height=200
            )

            with scene_view.scene:
                click_1 = sc.ClickGesture(_on_shape_clicked)
                click_2 = sc.DoubleClickGesture(_on_shape_double_clicked)
                sc.Rectangle(color=cl.blue, gestures=[click_1, click_2])

        await self.wait_n_updates(15)

        single_click, double_click = False, False
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(720, 100), double=False)

        await self.wait_n_updates(15)

        self.assertTrue(single_click)
        self.assertFalse(double_click)
        await self.wait_n_updates(15)

        single_click, double_click = False, False
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(720, 100), double=True)

        await self.wait_n_updates(15)
        self.assertTrue(double_click)
        self.assertFalse(single_click)
        await self.finalize_test_no_image()

    async def test_gesture_click_destroy_scene_view_no_crash(self):

        def _on_shape_clicked(shape):
            nonlocal scene_view
            scene_view.scene.clear()
            scene_view.destroy()
            scene_view = None

        class HoverGesture(sc.HoverGesture):
            def on_began(self):
                self.sender.color = cl.red

            def on_ended(self):
                self.sender.color = cl.blue

        window = await self.create_test_window(width=1440, height=900, block_devices=False)
        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                height=200
            )

            with scene_view.scene:
                click_1 = sc.ClickGesture(on_ended_fn=_on_shape_clicked)
                sc.Screen(gestures=[click_1])
                with sc.Transform() as t:
                    sc.Rectangle(color=cl.blue, gestures=[HoverGesture()])

        await self.wait_n_updates(5)
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(720, 100), double=False)
        # await self.wait_n_updates(15)

        self.assertIsNone(scene_view)
        await self.finalize_test_no_image()

    async def test_raw_input(self):
        class MyDragGesture(sc.DragGesture):
            def __init__(self):
                super().__init__()
                self.inputs = []

            def on_began(self):
                self.inputs.append(self.raw_input)

            def on_changed(self):
                self.inputs.append(self.raw_input)

            def on_ended(self):
                self.inputs.append(self.raw_input)

        window = await self.create_test_window()

        # Projection matrix
        proj = [0.5, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
            )

            with scene_view.scene:
                # Click, move, release in the center
                drag = MyDragGesture()
                # Clicked, down, released
                mouse_action_sequence = [(0, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)]
                mouse_position_sequence = [(0, 0), (0, 0), (0, 0), (0.1, 0), (0.1, 0), (0.1, 0)]
                drag.manager = Manager(mouse_action_sequence, mouse_position_sequence, scene_view)
                sc.Rectangle(color=cl.blue, gesture=drag)

        for _ in range(30):
            await omni.kit.app.get_app().next_update_async()

        self.assertEqual(len(drag.inputs), 3)
        self.assertEqual(drag.inputs[0].mouse_origin, drag.inputs[1].mouse_origin)
        self.assertEqual(drag.inputs[1].mouse_origin, drag.inputs[2].mouse_origin)
        for i in drag.inputs:
            self.assertEqual(i.mouse_direction, sc.Vector3(0, 0, 1))

        await self.finalize_test_no_image()

    async def test_check_mouse_moved_off(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        proj = [0.3, 0, 0, 0, 0, 0.3, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            with ui.ZStack():
                scene_view = sc.SceneView(
                    sc.CameraModel(proj, view),
                    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                )

        class Move(sc.DragGesture):
            def __init__(self, transform: sc.Transform):
                super().__init__(check_mouse_moved=False)
                self.__transform = transform

            def on_began(self):
                self.sender.color = cl.red

            def on_changed(self):
                translate = self.sender.gesture_payload.moved
                # Move transform to the direction mouse moved
                current = sc.Matrix44.get_translation_matrix(*translate)
                self.__transform.transform *= current

            def on_ended(self):
                self.sender.color = cl.blue

        with scene_view.scene:
            transform = sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, -1))
            with transform:
                sc.Rectangle(color=cl.blue, gesture=Move(transform))
            with sc.Transform(transform=sc.Matrix44.get_scale_matrix(3, 3, 3)):
                sc.Rectangle(color=cl.grey)

        scene_view_ref = ui_test.WidgetRef(scene_view, "")

        await ui_test.wait_n_updates()
        await ui_test.input.emulate_mouse(MouseEventType.MOVE, scene_view_ref.center)

        # Press mouse button
        await ui_test.wait_n_updates()
        await ui_test.input.emulate_mouse(MouseEventType.LEFT_BUTTON_DOWN)

        # Move camera
        await ui_test.wait_n_updates()
        view *= sc.Matrix44.get_translation_matrix(0, 1.0, 0)
        scene_view.model = sc.CameraModel(proj, view)

        # Release mouse button
        await ui_test.wait_n_updates()
        await ui_test.input.emulate_mouse(MouseEventType.LEFT_BUTTON_UP)

        await ui_test.wait_n_updates()
        await self.finalize_test()

    async def test_check_mouse_moved_on(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        proj = [0.3, 0, 0, 0, 0, 0.3, 0, 0, 0, 0, 2e-7, 0, 0, 0, 1, 1]
        view = sc.Matrix44.get_translation_matrix(0, 0, -10)
        with window.frame:
            with ui.ZStack():
                scene_view = sc.SceneView(
                    sc.CameraModel(proj, view),
                    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                )

        class Move(sc.DragGesture):
            def __init__(self, transform: sc.Transform):
                super().__init__(check_mouse_moved=True)
                self.__transform = transform

            def on_began(self):
                self.sender.color = cl.red

            def on_changed(self):
                translate = self.sender.gesture_payload.moved
                # Move transform to the direction mouse moved
                current = sc.Matrix44.get_translation_matrix(*translate)
                self.__transform.transform *= current

            def on_ended(self):
                self.sender.color = cl.blue

        with scene_view.scene:
            transform = sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, -1))
            with transform:
                sc.Rectangle(color=cl.blue, gesture=Move(transform))
            with sc.Transform(transform=sc.Matrix44.get_scale_matrix(3, 3, 3)):
                sc.Rectangle(color=cl.grey)

        scene_view_ref = ui_test.WidgetRef(scene_view, "")

        await ui_test.wait_n_updates()
        await ui_test.input.emulate_mouse(MouseEventType.MOVE, scene_view_ref.center)

        # Press mouse button
        await ui_test.wait_n_updates()
        await ui_test.input.emulate_mouse(MouseEventType.LEFT_BUTTON_DOWN)

        # Move camera
        await ui_test.wait_n_updates()
        view *= sc.Matrix44.get_translation_matrix(0, 1.0, 0)
        scene_view.model = sc.CameraModel(proj, view)

        # Release mouse button
        await ui_test.wait_n_updates()
        await ui_test.input.emulate_mouse(MouseEventType.LEFT_BUTTON_UP)

        await ui_test.wait_n_updates()
        await self.finalize_test()

    async def test_check_no_crash(self):
        class ClickGesture(sc.ClickGesture):
            def __init__(self, *args, **kwargs):
                # Passing `self` while using `super().__init__` is legal python, but not correct.
                # However, it shouldn't crash.
                super().__init__(self, *args, **kwargs)

        with self.assertRaises(TypeError) as cm:
            self.assertTrue(bool(ClickGesture()))
        await self.finalize_test_no_image()

    async def test_resize_no_drag(self):
        """OMPE-14095: Test resizing window doesn't trigger the drag gesture."""
        scene_window = await self.create_test_window(width=500, height=400, block_devices=False)
        # Projection matrix
        proj = [1.7, 0, 0, 0, 0, 3, 0, 0, 0, 0, -1, -1, 0, 0, -2, 0]

        # Move camera
        rotation = sc.Matrix44.get_rotation_matrix(30, 50, 0, True)
        transl = sc.Matrix44.get_translation_matrix(0, 0, -6)
        view = transl * rotation
        with scene_window.frame:
            scene_view = sc.SceneView(
                sc.CameraModel(proj, view),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
                height=400
            )

            dragged = False
            class _DragGesture(sc.DragGesture):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

                def on_began(self):
                    nonlocal dragged
                    dragged = True

            with scene_view.scene:
                sc.Screen(gesture=_DragGesture())

        await self.wait_n_updates(10)

        window_ref = ui_test.WindowRef(scene_window, "")
        pos = window_ref.position
        size = window_ref.size
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(pos.x, pos.y + size.y / 4))
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(pos.x, pos.y + size.y / 4), ui_test.Vec2(pos.x + size.x, pos.y + size.y / 4), human_delay_speed=8)
        self.assertFalse(dragged)

        ui.Workspace.clear()