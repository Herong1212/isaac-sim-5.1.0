## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import omni.kit.test
import omni.client

from omni.kit.helper.file_utils import asset_types
from omni.kit.widget.filebrowser import FileBrowserItem, FileBrowserItemFactory
from ..model import FilePickerModel
from .test_utils import time_logger


@time_logger
class TestAssetTypes(omni.kit.test.AsyncTestCase):
    """Testing FilePickerModel.*asset_type"""
    async def setUp(self):
        self.test_filenames = [
            ("test.settings.usd", asset_types.ASSET_TYPE_USD_SETTINGS),
            ("test.settings.usda", asset_types.ASSET_TYPE_USD_SETTINGS),
            ("test.settings.usdc", asset_types.ASSET_TYPE_USD_SETTINGS),
            ("test.settings.usdz", asset_types.ASSET_TYPE_USD_SETTINGS),
            ("test.fbx", asset_types.ASSET_TYPE_FBX),
            ("test.obj", asset_types.ASSET_TYPE_OBJ),
            ("test.mdl", asset_types.ASSET_TYPE_MATERIAL),
            ("test.mtlx", asset_types.ASSET_TYPE_MATERIAL),
            ("test.bmp", asset_types.ASSET_TYPE_IMAGE),
            ("test.gif", asset_types.ASSET_TYPE_IMAGE),
            ("test.jpg", asset_types.ASSET_TYPE_IMAGE),
            ("test.jpeg", asset_types.ASSET_TYPE_IMAGE),
            ("test.png", asset_types.ASSET_TYPE_IMAGE),
            ("test.tga", asset_types.ASSET_TYPE_IMAGE),
            ("test.tif", asset_types.ASSET_TYPE_IMAGE),
            ("test.tiff", asset_types.ASSET_TYPE_IMAGE),
            ("test.hdr", asset_types.ASSET_TYPE_IMAGE),
            ("test.dds", asset_types.ASSET_TYPE_IMAGE),
            ("test.exr", asset_types.ASSET_TYPE_IMAGE),
            ("test.psd", asset_types.ASSET_TYPE_IMAGE),
            ("test.ies", asset_types.ASSET_TYPE_IMAGE),
            ("test.wav", asset_types.ASSET_TYPE_SOUND),
            ("test.wav", asset_types.ASSET_TYPE_SOUND),
            ("test.wave", asset_types.ASSET_TYPE_SOUND),
            ("test.ogg", asset_types.ASSET_TYPE_SOUND),
            ("test.oga", asset_types.ASSET_TYPE_SOUND),
            ("test.flac", asset_types.ASSET_TYPE_SOUND),
            ("test.fla", asset_types.ASSET_TYPE_SOUND),
            ("test.mp3", asset_types.ASSET_TYPE_SOUND),
            ("test.m4a", asset_types.ASSET_TYPE_SOUND),
            ("test.spx", asset_types.ASSET_TYPE_SOUND),
            ("test.opus", asset_types.ASSET_TYPE_SOUND),
            ("test.adpcm", asset_types.ASSET_TYPE_SOUND),
            ("test.py", asset_types.ASSET_TYPE_SCRIPT),
            ("test.nvdb", asset_types.ASSET_TYPE_VOLUME),
            ("test.vdb", asset_types.ASSET_TYPE_VOLUME),
            ("test.svg", asset_types.ASSET_TYPE_ICON),
            (".thumbs", asset_types.ASSET_TYPE_HIDDEN),
        ]
        try:
            # test USD only when available
            import omni.usd
        except ImportError:
            pass
        else:
            self.test_filenames.extend([
                ("test.usd", asset_types.ASSET_TYPE_USD),
                ("test.usda", asset_types.ASSET_TYPE_USD),
                ("test.usdc", asset_types.ASSET_TYPE_USD),
                ("test.usdz", asset_types.ASSET_TYPE_USD),
            ])

    async def tearDown(self):
        pass

    def _create_folder_item(self, path: str) -> FileBrowserItem:
        item = FileBrowserItemFactory.create_group_item(path, path)
        return item

    def _create_file_item(self, path: str) -> FileBrowserItem:
        item = FileBrowserItemFactory.create_group_item(path, path)
        item._is_folder = False
        return item

    async def test_get_icon(self):
        """Testing FilePickerModel.get_icon returns expected icon for asset type"""
        under_test = FilePickerModel()
        for test_filename in self.test_filenames:
            filename, asset_type = test_filename
            if asset_type not in [asset_types.ASSET_TYPE_ICON, asset_types.ASSET_TYPE_HIDDEN]:
                expected = asset_types._known_asset_types[asset_type].glyph
                result = under_test.get_icon(self._create_file_item(filename), False)
                self.assertEqual(result, expected,
                    "Expected icon of {filename} to be {expected} - got {result}")

        # Test folder type
        self.assertEqual(under_test.get_icon(self._create_folder_item("folder"), False), None)

        # Test unknown file type
        self.assertEqual(under_test.get_icon(self._create_file_item("test.unknown"), False), None)

    async def test_get_thumbnail(self):
        """Testing FilePickerModel.get_thumbnail returns correct thumbnail for asset type"""
        under_test = FilePickerModel()
        for test_filename in self.test_filenames:
            filename, asset_type = test_filename
            if asset_type not in [asset_types.ASSET_TYPE_ICON, asset_types.ASSET_TYPE_HIDDEN]:
                expected = asset_types._known_asset_types[asset_type].thumbnail
                result = under_test.get_thumbnail(self._create_file_item(filename))
                self.assertEqual(result, expected,
                    "Expected thumbnail of {filename} to be {expected} - got {result}")

        # Test folder type
        result = under_test.get_thumbnail(self._create_folder_item("folder"))
        self.assertEqual(os.path.basename(result), "folder_256.png")

        # Test unknown file type
        result = under_test.get_thumbnail(self._create_file_item("test.unknown"))
        self.assertEqual(os.path.basename(result), "unknown_file_256.png")
