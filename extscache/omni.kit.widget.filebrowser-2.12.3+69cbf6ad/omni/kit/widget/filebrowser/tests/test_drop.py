## Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
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

from unittest.mock import Mock
from ..model import FileBrowserModel, FileBrowserItemFactory


class TestDrop(omni.kit.test.AsyncTestCase):
    """Testing FileSystemItem.content_changed_async"""
    async def setUp(self):
        pass

    async def tearDown(self):
        pass
    
    async def test_drop_handler(self):
        """Test drop handler behaves as expected."""
        from .. import TREEVIEW_PANE
        mock_drop = Mock()
        model = FileBrowserModel("C:", "C:", drop_fn=mock_drop)

        src_paths = []
        for i in range(100):
            src_paths.append("C://foo_" + str(i  +1))
        src_items = []
        for src in src_paths:
            src_items.append(FileBrowserItemFactory.create_group_item(src.lstrip("C://"), src))
        dst_item = FileBrowserItemFactory.create_group_item("dst", "C://dst")
        
        # test drop_fn only called once when multiple items are triggering drop handler at the same time
        for src_item in src_items:
            model.drop(dst_item, src_item)

        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        mock_drop.assert_called_once_with(dst_item, "\n".join(src_paths))
        mock_drop.reset_mock()

        # test drop_fn called correctly when passing in string as source
        src_paths_str = "C://foo\nC://bar\nC://baz"
        model.drop(dst_item, src_paths_str)
        mock_drop.assert_called_once_with(dst_item, src_paths_str)