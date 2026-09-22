## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.client
import omni.kit.app
import omni.ui as ui

from unittest.mock import  patch
from ..model import FileBrowserModel, FileBrowserItemFactory, FileBrowserItem
from ..grid_view import FileBrowserGridView, FileBrowserGridViewDelegate


class TestUpdateGridView(omni.kit.test.AsyncTestCase):
    """Testing FileBrowserGridViewDelegate.update_grid"""
    async def setUp(self):
        self._throttle_frames = 2

    async def tearDown(self):
        pass

    async def _after_redraw_async(self):
        for _ in range(self._throttle_frames + 1):
            await omni.kit.app.get_app().next_update_async()

    async def _mock_refresh_thumbnails_async(self, model: FileBrowserModel):
        pass

    def _get_badges(self, item: FileBrowserItem):
        return []

    async def test_update_grid_adds_new_items(self):
        """Testing FileBrowserGridView.update_grid updates the grid view successfully"""
        with patch.object(FileBrowserGridViewDelegate, "refresh_thumbnails_async", side_effect=self._mock_refresh_thumbnails_async):
            model = FileBrowserModel("ov-test", "omniverse://ov-test")
            test_items = ["foo.usd", "bar.usd"]
            test_items_path = []
            for name in test_items:
                model.root.add_child(FileBrowserItemFactory.create_dummy_item(name, f"{model.root.path}/{name}"))
                test_items_path.append(f"{model.root.path}/{name}")
            # Assert grid initially empty
            under_test = FileBrowserGridView(model, testing=True)
            # OMPE-5500: Wait for another redraw since we now delay building ui after grid view model changed
            await self._after_redraw_async()
            delegate = under_test._delegate
            self.assertTrue(delegate._grid is not None)
            self.assertEqual(0, len(ui.Inspector.get_children(delegate._grid)))
            self.assertEqual(0, len(delegate._cards))

            # Grid is populated after redraw
            under_test.refresh_ui()
            await self._after_redraw_async()
            test_card = delegate._cards[test_items_path[0]]
            test_card._get_badges_fn = self._get_badges
            thumbnail = test_card._get_thumbnail(test_card._item)
            self.assertIsNotNone(thumbnail)
            test_card._item.alert = (1, "Info")
            test_card.draw_badges()
            self.assertEqual(len(test_items), len(ui.Inspector.get_children(delegate._grid)))
            self.assertEqual(len(test_items), len(delegate._cards))

            # Adding a file updates the grid
            model.root.add_child(FileBrowserItemFactory.create_dummy_item("baz.usd", f"{model.root.path}/baz.usd"))
            under_test.refresh_ui()
            await self._after_redraw_async()
            self.assertEqual(len(test_items)+1, len(ui.Inspector.get_children(delegate._grid)))
            self.assertEqual(len(test_items)+1, len(delegate._cards))

            # Assert deleting orignal files leaves only the added file in place
            for name in test_items:
                model.root.del_child(name)

            under_test.refresh_ui()
            await self._after_redraw_async()
            self.assertEqual(1, len(ui.Inspector.get_children(delegate._grid)))
            self.assertEqual(1, len(delegate._cards))
            self.assertTrue(f"{model.root.path}/baz.usd" in delegate._cards)
            under_test.destroy()

    async def test_cut_items_style_reflected(self):
        """Testing that items in cut clipboard are applied cut style."""
        from ..clipboard import save_items_to_clipboard, is_path_cut
        with patch.object(FileBrowserGridViewDelegate, "refresh_thumbnails_async", side_effect=self._mock_refresh_thumbnails_async):
            model = FileBrowserModel("ov-test", "omniverse://ov-test")
            test_names = ["foo.usd", "bar.usd", "baz.usd"]

            for name in test_names:
                model.root.add_child(FileBrowserItemFactory.create_dummy_item(name, f"{model.root.path}/{name}"))

            # Assert grid initially empty
            under_test = FileBrowserGridView(model, testing=True)
            delegate = under_test._delegate
            under_test.refresh_ui()
            await self._after_redraw_async()

            # with empty clipboard every item should be with normal name
            for path, item in delegate._cards.items():
                self.assertFalse(is_path_cut(path))
                self.assertEqual(item._back_buffer_thumbnail.name, "")
                item.draw_badges()

            # put item in clipboard
            items = model.get_item_children(model.root)
            cut_path = items[0].path
            save_items_to_clipboard(items[0], is_cut=True)
            await self._after_redraw_async()
            under_test.refresh_ui()

            # item in clipboard should be applied Cut style name
            for path, item in delegate._cards.items():
                if path == cut_path:
                    self.assertTrue(is_path_cut(path))
                    self.assertEqual(item._back_buffer_thumbnail.name, "Cut")
                else:
                    self.assertFalse(is_path_cut(path))
                    self.assertEqual(item._back_buffer_thumbnail.name, "")
            under_test.destroy()
