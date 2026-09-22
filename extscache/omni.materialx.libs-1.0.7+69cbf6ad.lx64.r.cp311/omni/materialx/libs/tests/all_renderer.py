from .common import MtlxRenderTest

# This class is auto-discoverable by omni.kit.test
class MtlxRenderTestAll(MtlxRenderTest):
    # ==============================================================================================
    # The tests
    # ==============================================================================================

    # StandardSurface presets that ship with the MaterialX SDK
    # ----------------------------------------------------------------------------------------------
    async def test_standardsurface_composition(self):
        await self.run_image_test('StandardSurface/Composition.usda', 'mtlx_standardsurface_composition')

    # A selection of the materials published by AMD on https://matlib.gpuopen.com
    # ----------------------------------------------------------------------------------------------
    async def test_amd_composition(self):
        await self.run_image_test('AMD/Composition.usda', 'mtlx_amd_composition')

    # Open Chess Set as released by the USD Work Group
    # ----------------------------------------------------------------------------------------------
    async def test_open_chess_set(self):
        await self.run_image_test('OpenChessSet/chess_set_light_camera.usda', 'mtlx_open_chess_set')

    # MaterialX tests published in the USD workgroup on https://github.com/usd-wg/assets
    # Added a single root prim to each test scene and recomposed them into one test case.
    # ----------------------------------------------------------------------------------------------
    async def test_usd_wg_assets_composition(self):
        try:
            # replace the token by an absolute file path in order to test absolute paths
            sceneDir = self.USD_DIR.joinpath('usd-wg-assets')
            tempSceneFile = sceneDir.joinpath('basicTextured_flatten.usda')
            self.prepare_temp_file(
                srcFilename = sceneDir.joinpath('basicTextured_flatten_template.usda'),
                destFilename = tempSceneFile,
                replacementMap = {"${USD_DIR}":f"{sceneDir}"})
            tempMtlxFile = sceneDir.joinpath('standard_surface_brass_tiled_absolute_paths.mtlx')
            self.prepare_temp_file(
                srcFilename = sceneDir.joinpath('standard_surface_brass_tiled_absolute_paths_template.mtlx'),
                destFilename = tempMtlxFile,
                replacementMap = {"${USD_DIR}":f"{sceneDir}"})
            # run the test
            await self.run_image_test('usd-wg-assets/Composition.usda', 'mtlx_usd-wg-assets_composition')
        finally:
            # remove the temp files
            if tempSceneFile.exists():
                tempSceneFile.unlink()
            if tempMtlxFile.exists():
                tempMtlxFile.unlink()

    # Tests the following:
    # 1. prim var reading
    # 2. a UsdShade network with node graphs
    # 3. a UsdShade network with a terminal inside a node graph
    # ----------------------------------------------------------------------------------------------
    async def test_general(self):
        await self.run_image_test('GeneralTests/general.usda', 'mtlx_general')

    # OpenPbr
    # ----------------------------------------------------------------------------------------------
    async def test_openpbr(self):
        await self.run_image_test('OpenPbr/scene.usda', 'mtlx_openpbr')

    async def test_python_bindings(self):
        """Tests that the MaterialX bindings are available"""
        import MaterialX
        self.assertIsNotNone(MaterialX)
