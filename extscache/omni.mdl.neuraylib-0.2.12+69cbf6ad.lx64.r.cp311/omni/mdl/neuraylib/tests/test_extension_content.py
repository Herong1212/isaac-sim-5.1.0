from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

import os
from pathlib import Path
from unittest import skipIf
from .utils import *

import omni.mdl.neuraylib as neuraylib  # interface the OV material backend
import omni.mdl.pymdlsdk as pymdlsdk    # low-level MDL python binding that matches the native SDK

class ExtensionContentTest(AsyncTestCase):


    # Before running each test
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetDefaultPrim(stage.DefinePrim("/World"))
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()
        await omni.usd.get_context().close_stage_async()
        await wait_stage_loading()

    #-------------------------------------------------------------------------------------------------------------------
    # Register Extension Content

    async def base_extension_content(self):
        # usually constant data for common extensions
        ext_id = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(__name__)
        ext_dir = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id))
        ext_name = omni.ext.get_extension_name(ext_id)
        ext_content_dir: Path = ext_dir.joinpath('data', 'example_content')
        ext_content_mdl_dir: Path = ext_content_dir.joinpath('mdl')

        # selecting this folder yields the following modules in the search path addressable as USD source asset:
        #   -   nvidia/ProjectABC/main.mdl
        #   -   nvidia/ProjectABC/sub1/A.mdl
        #   -   nvidia/ProjectABC/sub1/sub3/C.mdl
        #   -   nvidia/ProjectABC/sub2/B.mdl
        # and the corresponding MDL qualified module names:
        #   -   ::nvidia::ProjectABC::main.mdl
        #   -   ::nvidia::ProjectABC::sub1::A.mdl
        #   -   ::nvidia::ProjectABC::sub1::sub3::C.mdl
        #   -   ::nvidia::ProjectABC::sub2::B.mdl

        # NOTE always put your content into proper packages to avoid collisions with other modules
        # the MDL module space is similar to package names in python and java. they have to be unique.
        # a common pattern is to put the company in front, followed by a project or product name.

        # allow extension content to be found via search path, done when loading the extension
        # NOTE keep the returned links in order to unregister on shutdown
        linkedContentPaths: list[str] = neuraylib.register_extension_content(ext_name, str(ext_content_mdl_dir))
        self.assertNotEqual(len(linkedContentPaths), 0)

        # acquire neuray instance from OV
        ov_neuraylib: neuraylib.NeurayLib = neuraylib.get_neuraylib()
        ov_neuraylib_handle = ov_neuraylib.getNeurayAPI()

        # feed the neuray instance into the python binding
        neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ov_neuraylib_handle)
        self.assertIsNotNone(neuray)

        # load a module using the extension search path
        dbgModule = ov_neuraylib.createMdlModule('nvidia/ProjectABC/sub1/sub3/C.mdl')
        self.assertIsNotNone(dbgModule)
        self.assertTrue(dbgModule.valid())
        ov_neuraylib.destroyMdlModule(dbgModule)

        # use the search path in USD
        # Note, this is independent of the module loading right above
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path(ext_content_dir.joinpath('extension_content.usda')))
        await wait_stage_loading()
        # access a USD shader nodes MDL representation
        usd_prim_path: str = "/World/Looks/DebugMaterial/Shader"
        ov_entity = ov_neuraylib.createMdlEntity(usd_prim_path) # using the default scope name
        self.assertIsNotNone(ov_entity)
        self.assertTrue(ov_entity.valid()) # scene is loaded, material should be valid
        ov_neuraylib.destroyMdlEntity(ov_entity)

        # remove the extension content, usually done when unloading the extension
        removed: bool = neuraylib.deregister_extension_content(ext_name, linkedContentPaths)
        self.assertTrue(removed)

        # test error cases
        ext_content_mdl_dir = ext_content_dir.joinpath('NOT-EXISTING')
        absPaths: list[str] = neuraylib.register_extension_content(ext_name, str(ext_content_mdl_dir))
        self.assertEqual(len(absPaths), 0)

    # regular test
    async def test_extension_content(self):
        await self.base_extension_content()

    # test symlinks on windows works only with admin rights
    async def manual_test_extension_content_symlink(self):
        carb.settings.get_settings().set('/exts/omni.mdl.neuraylib/extSearchPath/forceSymlinks', True)
        await self.base_extension_content()
        carb.settings.get_settings().set('/exts/neuraylib/extSearchPath/forceSymlinks', False)
