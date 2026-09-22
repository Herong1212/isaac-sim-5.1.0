## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.kit.app

from unittest.mock import  patch
from ..widget import FileBrowserWidget
from ..grid_view import FileBrowserGridViewDelegate


class TestZoomBar(omni.kit.test.AsyncTestCase):
    """Testing FileBrowserGridViewDelegate.update_grid"""
    async def setUp(self):
        self._throttle_frames = 2

    async def tearDown(self):
        pass

    async def _after_redraw_async(self):
        for _ in range(self._throttle_frames + 1):
            await omni.kit.app.get_app().next_update_async()

    async def test_zoom_switches_to_table_view(self):
        """Testing FileBrowserWidget.scale_grid_view changes to treeview for small scale factors"""
        under_test = FileBrowserWidget("test", show_grid_view=True)
        self.assertFalse(under_test._table_view.visible)
        self.assertTrue(under_test._grid_view.visible)

        under_test.scale_grid_view(0.25)
        self.assertTrue(under_test._table_view.visible)
        self.assertFalse(under_test._grid_view.visible)

        under_test.scale_grid_view(0.5)
        self.assertFalse(under_test._table_view.visible)
        self.assertTrue(under_test._grid_view.visible)

        under_test.scale_grid_view(2.0)
        self.assertFalse(under_test._table_view.visible)
        self.assertTrue(under_test._grid_view.visible)

        under_test.destroy()
        under_test = None

    async def test_zoom_rebuilds_grid_view(self):
        """Testing FileBrowserWidget.scale_grid_view re-builds the grid view"""
        with patch.object(FileBrowserGridViewDelegate, "build_grid") as mock_build_grid,\
            patch.object(FileBrowserGridViewDelegate, "update_grid") as mock_update_grid:

            test_scale = 1.75
            under_test = FileBrowserWidget("test", show_grid_view=True)

            # OMPE-5500: Wait for another redraw since we now delay building ui after grid view model changed
            await self._after_redraw_async()
            mock_build_grid.reset_mock()
            mock_update_grid.reset_mock()
            under_test.scale_grid_view(test_scale)

            await self._after_redraw_async()
            self.assertEqual(under_test._grid_view._delegate.scale, test_scale)
            mock_build_grid.assert_called_once()
            mock_update_grid.assert_called_once()
            under_test.destroy()
