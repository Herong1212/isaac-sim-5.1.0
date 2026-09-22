## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["TestDragDrop"]


import omni.kit.test
from omni.kit.test import AsyncTestCase
import omni.usd
from pxr import Sdf, UsdGeom
from ..dragdrop.usd_file_drop_delegate import UsdFileDropDelegate
from ..dragdrop.material_file_drop_delegate import MaterialFileDropDelegate
from ..dragdrop.audio_file_drop_delegate import AudioFileDropDelegate


class TestDragDrop(AsyncTestCase):
    async def setUp(self):
        self.usd_context_name = ''
        self.usd_context = omni.usd.get_context(self.usd_context_name)
        await self.usd_context.new_stage_async()
        self.stage = self.usd_context.get_stage()

    async def tearDown(self):
        self.usd_context = None
        self.stage = None

    async def createNewStage(self, default_prim: str = None):
        self.usd_context_name = ''
        self.usd_context = omni.usd.get_context(self.usd_context_name)
        await self.usd_context.new_stage_async()
        self.stage = self.usd_context.get_stage()
        if default_prim is not None:
            self.stage.SetDefaultPrim(UsdGeom.Xform.Define(self.stage, f'/{default_prim}').GetPrim())

    def validate_sdf_path(self, file_drop: UsdFileDropDelegate, url: str):
        prim_path = file_drop.make_prim_path(self.stage, url)

        # Make sure the return value is a completely valid SdfPath
        self.assertIsNotNone(prim_path)
        self.assertTrue(Sdf.Path.IsValidPathString(prim_path.pathString))

        # If it was dropped onto a stage wit a defaultPrim, make sure it was dropped into that Prim
        default_prim = self.stage.GetDefaultPrim()
        if default_prim:
            default_prim_path = default_prim.GetPath()
            self.assertEqual(prim_path.GetCommonPrefix(default_prim_path), default_prim_path)

    async def test_prim_name_generation_in_world(self):
        """Test new prim is generated with a valid path under defaultPrim=World"""

        await self.createNewStage('World')
        usd_file_drop = UsdFileDropDelegate()

        # Test against a file path
        self.validate_sdf_path(usd_file_drop, '/fake/path.usda')
        self.validate_sdf_path(usd_file_drop, '/fake/path with spaces.usda')
        self.validate_sdf_path(usd_file_drop, '/fake/a_weird_name-off__-_that-is_ still odd.usda')

        # Test against an omni protocol
        self.validate_sdf_path(usd_file_drop, 'omni://fake/omnipath.usda')
        self.validate_sdf_path(usd_file_drop, 'omni://fake/1 omni path path with spaces.usda')
        self.validate_sdf_path(usd_file_drop, 'omni:///fake/a_weird_name-off__-_that-is_ still odd.usda')

        # Test a protocol other than omni, just use https
        self.validate_sdf_path(usd_file_drop, 'https://fake/protocolpath.usda')
        self.validate_sdf_path(usd_file_drop, 'https://fake/2 prot')
        self.validate_sdf_path(usd_file_drop, 'https:///fake/a_weird_name-off__-_that-is_ still odd.usda')

    async def test_prim_name_generation_in_another_world(self):
        """Test new prim is generated with a valid path under defaultPrim=AnotherNonStandardWorld"""

        await self.createNewStage('AnotherNonStandardWorld')
        usd_file_drop = UsdFileDropDelegate()

        # Test against a file path
        self.validate_sdf_path(usd_file_drop, '/fake/path.usda')
        self.validate_sdf_path(usd_file_drop, '/fake/path with spaces.usda')
        self.validate_sdf_path(usd_file_drop, '/fake/a_weird_name-off__-_that-is_ still odd.usda')

        # Test against an omni protocol
        self.validate_sdf_path(usd_file_drop, 'omni://fake/omnipath.usda')
        self.validate_sdf_path(usd_file_drop, 'omni://fake/1 omni path path with spaces.usda')
        self.validate_sdf_path(usd_file_drop, 'omni:///fake/a_weird_name-off__-_that-is_ still odd.usda')

        # Test a protocol other than omni, just use https
        self.validate_sdf_path(usd_file_drop, 'https://fake/protocolpath.usda')
        self.validate_sdf_path(usd_file_drop, 'https://fake/2 prot')
        self.validate_sdf_path(usd_file_drop, 'https:///fake/a_weird_name-off__-_that-is_ still odd.usda')

    async def test_prim_name_root_generation(self):
        """Test new prim is generated with a valid path"""

        await self.createNewStage()
        usd_file_drop = UsdFileDropDelegate()

        # Test against a file path
        self.validate_sdf_path(usd_file_drop, '/fake/path.usda')
        self.validate_sdf_path(usd_file_drop, '/fake/path with spaces.usda')
        self.validate_sdf_path(usd_file_drop, '/fake/a_weird_name-off__-_that-is_ still odd.usda')

        # Test against an omni protocol
        self.validate_sdf_path(usd_file_drop, 'omni://fake/omnipath.usda')
        self.validate_sdf_path(usd_file_drop, 'omni://fake/1 omni path path with spaces.usda')
        self.validate_sdf_path(usd_file_drop, 'omni:///fake/a_weird_name-off__-_that-is_ still odd.usda')

        # Test a protocol other than omni, just use https
        self.validate_sdf_path(usd_file_drop, 'https://fake/protocolpath.usda')
        self.validate_sdf_path(usd_file_drop, 'https://fake/2 prot')
        self.validate_sdf_path(usd_file_drop, 'https:///fake/a_weird_name-off__-_that-is_ still odd.usda')

    async def test_mdl_drop(self):
        """Test Material will be accepted by MDL handler and denied by USD handler"""

        await self.createNewStage('World')
        usd_file_drop = UsdFileDropDelegate()
        mtl_file_drop = MaterialFileDropDelegate(show_alert=False)

        def make_drop_object(url: str):
            return {'mime_data': url, 'usd_context_name': self.usd_context_name}

        self.assertFalse(usd_file_drop.accepted(make_drop_object('/fake/mdlfile.mdl')))
        self.assertFalse(usd_file_drop.accepted(make_drop_object('https://fake/mdlfile.mdl')))
        self.assertFalse(usd_file_drop.accepted(make_drop_object('material::https://fake/mdlfile.mdl')))

        self.assertTrue(mtl_file_drop.accepted(make_drop_object('/fake/mdlfile.mdl')))
        self.assertTrue(mtl_file_drop.accepted(make_drop_object('https://fake/mdlfile.mdl')))
        self.assertFalse(mtl_file_drop.accepted(make_drop_object('material::https://fake/mdlfile.mdl')))

        self.assertEqual(mtl_file_drop.accept_url('/fake/mdlfile.mdl'), '/fake/mdlfile.mdl')
        self.assertEqual(mtl_file_drop.accept_url('https://fake/mdlfile.mdl'), 'https://fake/mdlfile.mdl')
        self.assertFalse(mtl_file_drop.accept_url('material::https://fake/mdlfile.mdl'))

    async def test_mdl_drop_material_location(self):
        """Test Material will be created in proper Scope location"""

        mtl_file_drop = MaterialFileDropDelegate()

        await self.createNewStage('World')
        self.assertEqual(mtl_file_drop.get_material_prim_location(self.stage), Sdf.Path('/World/Looks'))

        await self.createNewStage()
        self.assertEqual(mtl_file_drop.get_material_prim_location(self.stage), Sdf.Path('/Looks'))

    async def test_audio_drop_delegate(self):
        """Test Audio will be created in proper location"""

        audio_drop = AudioFileDropDelegate()
        await self.createNewStage('World')

        def make_drop_object(url: str):
            return {'mime_data': url, 'usd_context_name': self.usd_context_name}

        self.validate_sdf_path(audio_drop, '/fake/path.wav')
        self.validate_sdf_path(audio_drop, '/fake/path.wave')
        self.validate_sdf_path(audio_drop, '/fake/path.ogg')
        self.validate_sdf_path(audio_drop, '/fake/path.mp3')

        self.assertFalse(audio_drop.accepted(make_drop_object('/fake/path.txt')))
        self.assertFalse(audio_drop.accepted(make_drop_object('/fake/path.usda')))
        self.assertFalse(audio_drop.accepted(make_drop_object('material::https://fake/mdlfile.mdl')))

    async def test_ignored_dragdrop_protocols(self):
        """Test DragDropDelegates to ensure registered protocols are ignored"""

        delegates = [UsdFileDropDelegate,
                     MaterialFileDropDelegate,
                     AudioFileDropDelegate]
        protocol = "test://"
        for delegate in delegates:
            self.assertFalse(delegate.is_ignored_protocol(protocol))
            delegate.add_ignored_protocol(protocol)
            self.assertTrue(delegate.is_ignored_protocol(protocol + "test.ext"))
            delegate.remove_ignored_protocol(protocol)
            self.assertFalse(delegate.is_ignored_protocol(protocol))

    async def test_ignored_dragdrop_extensions(self):
        """Test DragDropDelegates to ensure registered extensions are ignored"""

        delegates = [UsdFileDropDelegate,
                     MaterialFileDropDelegate,
                     AudioFileDropDelegate]
        extension = ".test"
        for delegate in delegates:
            self.assertFalse(delegate.is_ignored_extension(extension))
            delegate.add_ignored_extension(extension)
            self.assertTrue(delegate.is_ignored_extension("test" + extension))
            delegate.remove_ignored_extension(extension)
            self.assertFalse(delegate.is_ignored_extension(extension))
