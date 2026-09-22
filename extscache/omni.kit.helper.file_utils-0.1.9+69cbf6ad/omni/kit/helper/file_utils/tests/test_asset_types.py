## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test

from .. import asset_types


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
            ("test.usd", asset_types.ASSET_TYPE_USD),
            ("test.usda", asset_types.ASSET_TYPE_USD),
            ("test.usdc", asset_types.ASSET_TYPE_USD),
            ("test.usdz", asset_types.ASSET_TYPE_USD),
            ("test.live", asset_types.ASSET_TYPE_USD),
        ]

    async def tearDown(self):
        pass

    async def test_is_asset_type(self):
        """Testing asset_types.is_asset_type returns expected result"""
        for test_filename in self.test_filenames:
            filename, expected = test_filename
            self.assertTrue(asset_types.is_asset_type(filename, expected))

    async def test_get_asset_type(self):
        """Testing asset_types.get_asset_type returns expected result"""
        for test_filename in self.test_filenames:
            filename, expected = test_filename
            self.assertEqual(asset_types.get_asset_type(filename), expected)
        # Test unknown file type
        self.assertEqual(asset_types.get_asset_type("test.unknown"), asset_types.ASSET_TYPE_UNKNOWN)

    async def test_get_icon(self):
        """Testing asset_types.get_icon returns expected icon for asset type"""
        for test_filename in self.test_filenames:
            filename, asset_type = test_filename
            if asset_type not in [asset_types.ASSET_TYPE_ICON, asset_types.ASSET_TYPE_HIDDEN]:
                expected = asset_types._known_asset_types[asset_type].glyph
                self.assertEqual(asset_types.get_icon(filename), expected)
    
    async def test_get_thumbnail(self):
        """Testing FilePickerModel.get_thumbnail returns correct thumbnail for asset type"""
        for test_filename in self.test_filenames:
            filename, asset_type = test_filename
            if asset_type not in [asset_types.ASSET_TYPE_ICON, asset_types.ASSET_TYPE_HIDDEN]:
                expected = asset_types._known_asset_types[asset_type].thumbnail
                self.assertEqual(asset_types.get_thumbnail(filename), expected)

    async def test_register_file_extensions(self):
        """Testing FilePickerModel.register_file_extensions"""
        # Add to existing type
        asset_types.register_file_extensions("usd", [".test", "testz"])
        self.assertTrue(asset_types.is_asset_type("file.testz", "usd"))

        # Register new type
        test_type = "test"
        asset_types.register_file_extensions(test_type, [".test", "testz"])
        self.assertTrue(asset_types.is_asset_type("file.test", test_type))
        self.assertTrue(asset_types.is_asset_type("file.testz", test_type))
