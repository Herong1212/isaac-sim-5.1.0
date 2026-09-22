## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestSelectionModel']


import omni.kit.test
from ..model import SelectionShapeModel


class TestSelectionModel(omni.kit.test.AsyncTestCase):
    async def test_ortho_selection(self):
        model = SelectionShapeModel()

        # Standard item should exist
        ndc_start_item = model.get_item('ndc_start')
        self.assertIsNotNone(ndc_start_item)

        # Standard item should exist
        ndc_current_item = model.get_item('ndc_current')
        self.assertIsNotNone(ndc_current_item)

        # Standard item should exist
        ndc_rect_item = model.get_item('ndc_rect')
        self.assertIsNotNone(ndc_rect_item)

        # Test setting only a start result in no rect
        model.set_floats(ndc_start_item, [1, 2])
        ndc_rect = model.get_as_floats(ndc_rect_item)
        self.assertEqual(ndc_rect, [1, 2, 1, 2])

        # Test setting a start and current results in a rect
        model.set_floats(ndc_start_item, [1, 2])
        model.set_floats(ndc_current_item, [3, 4])
        ndc_rect = model.get_as_floats(ndc_rect_item)
        self.assertEqual(ndc_rect, [1, 2, 3, 4])

        # Changing the order should result in the same sorted top-left, bottom-right rect
        model.set_floats(ndc_start_item, [3, 4])
        model.set_floats(ndc_current_item, [1, 2])
        ndc_rect = model.get_as_floats(ndc_rect_item)
        self.assertEqual(ndc_rect, [1, 2, 3, 4])
