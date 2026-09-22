## Copyright (c) top_left[0]22, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestSelectionManipulator']

import omni.kit.test
from ..manipulator import SelectionManipulator
from .test_scene_ui_base import TestOmniUiScene
from omni.ui import scene as sc


class TestSelectionManipulator(TestOmniUiScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ndc_rects = []
        self.__last_rect = None

    def on_item_changed(self, model, item):
        # ndc_rect should be part of the model, always
        ndc_rect_item = model.get_item('ndc_rect')
        self.assertIsNotNone(ndc_rect_item)

        # Ignore other signals
        if item != ndc_rect_item:
            return

        # Get the values
        ndc_rect = model.get_as_floats(ndc_rect_item)
        self.assertIsNotNone(ndc_rect)
        # NDC rect cannot be none, but it can be empty (on mouse-up)
        if ndc_rect != []:
            # ndc_rect should be totally ordered: top-left, bottom-right
            self.assertLess(ndc_rect[0], ndc_rect[2])
            self.assertLess(ndc_rect[1], ndc_rect[3])
            # Save the lat mouse for a test later
            self.__last_rect = ndc_rect

    def ndc_rects_match(self):
        self.assertIsNotNone(self.__last_rect)
        self.__ndc_rects.append(self.__last_rect)
        self.__last_rect = None
        if len(self.__ndc_rects) > 1:
            self.assertEqual(self.__ndc_rects[0], self.__ndc_rects[-1])

    async def test_ortho_selection(self):
        window, scene_view = await self.create_ortho_scene_view('test_ortho_selection')

        with scene_view.scene:
            manipulator = SelectionManipulator()
            sc.Arc(radius=25, wireframe=True, tesselation = 36 * 3, thickness = 2)

        manip_sub = manipulator.model.subscribe_item_changed_fn(self.on_item_changed)

        top_left = (20, 40)
        bottom_right = (window.width-top_left[0], window.height-60)

        # Test dragging top-left to bottom-right
        await self.wait_frames()
        await self.mouse_dragging_test('test_ortho_selection', (top_left[0], top_left[1]), (bottom_right[0], bottom_right[1]))
        await self.wait_frames()
        # Ortho and Perspective should stil have same selection box
        self.ndc_rects_match()

        # Test dragging bottom-right to top-left
        await self.wait_frames()
        await self.mouse_dragging_test('test_ortho_selection', (bottom_right[0], bottom_right[1]), (top_left[0], top_left[1]))
        await self.wait_frames()
        # Ortho and Perspective should stil have same selection box
        self.ndc_rects_match()


        # Test dragging top-right to bottom-left
        await self.wait_frames()
        await self.mouse_dragging_test('test_ortho_selection', (bottom_right[0], top_left[1]), (top_left[0], bottom_right[1]))
        await self.wait_frames()
        # Should stil have same selection box
        self.ndc_rects_match()

        # Test dragging bottom-left to top-right
        await self.wait_frames()
        await self.mouse_dragging_test('test_ortho_selection', (top_left[0], bottom_right[1]), (bottom_right[0], top_left[1]))
        await self.wait_frames()


    async def test_persepctive_selection(self):
        window, scene_view = await self.create_perspective_scene_view('test_persepctive_selection')

        with scene_view.scene:
            manipulator = SelectionManipulator({
                'thickness': 5.0,
                'color': (0.2, 0.2, 0.8, 0.8),
                'inner_color': (0.2, 0.6, 0.8, 0.4)
            })
            sc.Arc(radius=25, wireframe=True, tesselation = 36 * 3, thickness = 2)

        manip_sub = manipulator.model.subscribe_item_changed_fn(self.on_item_changed)

        top_left = (20, 40)
        bottom_right = (window.width-top_left[0], window.height-60)

        # Test dragging bottom-left to top-right
        await self.wait_frames()
        await self.mouse_dragging_test('test_persepctive_selection', (top_left[0], bottom_right[1]), (bottom_right[0], top_left[1]))
        await self.wait_frames()
        # Should stil have same selection box
        self.ndc_rects_match()

        # Test dragging top-right to bottom-left
        await self.wait_frames()
        await self.mouse_dragging_test('test_persepctive_selection', (bottom_right[0], top_left[1]), (top_left[0], bottom_right[1]))
        await self.wait_frames()
        # Should stil have same selection box
        self.ndc_rects_match()

        # Test dragging bottom-right to top-left
        await self.wait_frames()
        await self.mouse_dragging_test('test_persepctive_selection', (bottom_right[0], bottom_right[1]), (top_left[0], top_left[1]))
        await self.wait_frames()
        # Ortho and Perspective should stil have same selection box
        self.ndc_rects_match()

        # Test dragging top-left to bottom-right
        await self.wait_frames()
        await self.mouse_dragging_test('test_persepctive_selection', (top_left[0], top_left[1]), (bottom_right[0], bottom_right[1]))
        await self.wait_frames()
        # Ortho and Perspective should stil have same selection box
        self.ndc_rects_match()
