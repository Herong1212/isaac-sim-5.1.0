from omni.kit.commands.command import create
import omni.usd
import omni.kit.app
import omni.kit.test

from pxr import UsdShade, Sdf


class TestMaterialCommands(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._stage = omni.usd.get_context().get_stage()
        self._app = omni.kit.app.get_app()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()

    async def test_create_and_bind_material(self):
        async def create_material(mdl_name, mtl_name="", prim_name=""):
            created_materials = []
            omni.kit.commands.execute(
                "CreateAndBindMdlMaterialFromLibrary",
                mdl_name=mdl_name,
                mtl_name=mtl_name,
                mtl_created_list=created_materials,
                select_new_prim=True,
                prim_name=prim_name
            )
            # Delay some frames to populate material params
            await self._app.next_update_async()
            await self._app.next_update_async()

            if created_materials:
                return Sdf.Path(created_materials[0])
            else:
                return None # pragma: no cover

        def check(material_path, sub_identifier_name):
            self.assertTrue(material_path is not None)

            shader = UsdShade.Shader.Get(self._stage, material_path.AppendElementString("Shader"))
            self.assertTrue(not not shader)
            identifier = shader.GetSourceAssetSubIdentifier("mdl")
            self.assertEqual(identifier, sub_identifier_name)

        material_path = await create_material("OmniPBR.mdl", "OmniPBR")
        self.assertTrue(material_path.elementString, "OmniPBR")
        check(material_path, "OmniPBR")

        # Creates with empty mtl_name will use file name of mdl_name as subIdentifier by default.
        material_path = await create_material("OmniPBR.mdl")
        check(material_path, "OmniPBR")

        # Creates with specified other sub-identifier
        material_path = await create_material("OmniPBR.mdl", "TestIdentifier")
        check(material_path, "TestIdentifier")

        # Creates with specified prim name
        material_path = await create_material("OmniPBR.mdl", "", "test_prim")
        self.assertTrue(material_path.elementString, "test_prim")
        check(material_path, "OmniPBR")

    async def test_create_and_bind_mtlx_material(self):
        async def create_mtlx_material(mtlx_id, mtl_name):
            # create material
            created_materials = []
            omni.kit.commands.execute(
                "CreateAndBindMtlxSurfaceFromLibrary",
                mtlx_id=mtlx_id,
                mtl_name=mtl_name,
                mtl_created_list=created_materials,
                bind_selected_prims=False
            )

            # delay some frames to populate material params
            await self._app.next_update_async()
            await self._app.next_update_async()

            self.assertTrue(created_materials)

            return Sdf.Path(created_materials[0])

        def check_mtlx_material(mtl_path, mtlx_id, mtl_name):
            # check material prim name
            self.assertEqual(mtl_path.elementString, mtl_name)

            # check shader attr "info:id"
            shader = UsdShade.Shader.Get(self._stage, mtl_path.AppendElementString(mtlx_id))
            info_id = shader.GetShaderId()
            self.assertEqual(info_id, mtlx_id)


        # test OpenPBR
        mtlx_id = "ND_open_pbr_surface_surfaceshader"
        mtl_name = "OpenPBR"
        mtl_path = await create_mtlx_material(mtlx_id, mtl_name)
        check_mtlx_material(mtl_path, mtlx_id, mtl_name)

        # test StandardSurface
        mtlx_id = "ND_standard_surface_surfaceshader"
        mtl_name = "StandardSurface"
        mtl_path = await create_mtlx_material(mtlx_id, mtl_name)
        check_mtlx_material(mtl_path, mtlx_id, mtl_name)

    async def test_create_and_bind_usd_material(self):
        def check_usd_material(created_mtls, mtl_name, shader_name):
            # check created material
            self.assertEqual(len(created_mtls), 1)
            mtl_path = Sdf.Path(created_mtls[0])
            self.assertEqual(mtl_path, f"/Looks/{mtl_name}")

            # check shader attr "info:id"
            shader = UsdShade.Shader.Get(self._stage, mtl_path.AppendElementString(shader_name))
            info_id = shader.GetShaderId()
            self.assertTrue(info_id, "UsdPreviewSurface")


        # create PreviewSurface material
        created_materials = []
        omni.kit.commands.execute(
            "CreateAndBindPreviewSurfaceFromLibrary",
            mtl_created_list=created_materials,
            bind_selected_prims=False
        )

        # delay some frames to populate material params
        await self._app.next_update_async()
        await self._app.next_update_async()

        check_usd_material(created_materials, "PreviewSurface", "Shader")

        # create PreviewSurfaceTexture material
        created_materials = []
        omni.kit.commands.execute(
            "CreateAndBindPreviewSurfaceTextureFromLibrary",
            mtl_created_list=created_materials,
            bind_selected_prims=False
        )

        # delay some frames to populate material params
        await self._app.next_update_async()
        await self._app.next_update_async()

        check_usd_material(created_materials, "PreviewSurfaceTexture", "PreviewSurfaceTexture")
