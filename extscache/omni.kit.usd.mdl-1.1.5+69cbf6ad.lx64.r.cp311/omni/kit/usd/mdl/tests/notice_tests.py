import asyncio
import os
import shutil
from pathlib import Path

import carb
import omni.UsdMdl as UsdMdl
from pxr import Sdf, Sdr, Tf, UsdShade

from .lib.base import UsdMdlTestBase


class Notice_Tests(UsdMdlTestBase):
    async def test_notice_mdl_module_load(self):
        def _on_mdl_module_load(notice, sender):
            nonlocal resolved_path
            resolved_path = notice.GetResolvedPath()

        mdl_module = "load.mdl"
        subidentifier = "test_int"
        module_path = self.get_module_path(mdl_module)

        resolved_path = None

        listener = Tf.Notice.Register(UsdMdl.Notice.ModuleLoaded, _on_mdl_module_load, None)

        sdr_node = self.validate_node(mdl_module, subidentifier)
        await self.wait()

        self.assertIsNotNone(resolved_path)
        self.assertTrue(resolved_path == module_path.resolvedPath)

    async def test_notice_mdl_module_reload(self):
        def _on_mdl_module_reload(notice, sender):
            nonlocal reloaded_resolved_path
            reloaded_resolved_path = str(Path(notice.GetResolvedPath()))

        def _copyFile(src, dest):
            shutil.copyfile(src, dest)
            self.assertTrue(os.path.exists(dest))

        listener = Tf.Notice.Register(UsdMdl.Notice.ModuleReloaded, _on_mdl_module_reload, None)

        mdl_module = "test.mdl"
        subidentifier = "test_int"

        temp_dir = self.createTempDir()
        module_path = str(Path(temp_dir).joinpath(mdl_module))

        int_module_path = self.get_module_path("int.mdl")
        source_asset_path = Sdf.AssetPath(module_path, module_path)
        _copyFile(int_module_path.resolvedPath, source_asset_path.resolvedPath)

        usdshade_shader = self.create_usdshade_shader()

        res = usdshade_shader.SetSourceAsset(source_asset_path, UsdMdl.Tokens.Mdl)
        self.assertTrue(res)

        res = usdshade_shader.SetSourceAssetSubIdentifier(subidentifier, UsdMdl.Tokens.Mdl)
        self.assertTrue(res)

        prim = usdshade_shader.GetPrim()
        self.assertIsNotNone(prim)

        api = UsdShade.NodeDefAPI(prim)
        sdr_node = UsdMdl.RegistryUtils.GetShaderNodeForPrim(prim)

        self.assertIsNotNone(sdr_node)
        usdshade_shader.SetSdrMetadata(sdr_node.GetMetadata())

        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 1

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
        }

        self.validate_property("param", sdr_node, value_type_name, True, metadata, default_value)

        reloaded_resolved_path = None

        reloaded_module_path = self.get_module_path("int_reloaded.mdl")
        _copyFile(reloaded_module_path.resolvedPath, source_asset_path.resolvedPath)

        await self.wait()

        self.assertIsNotNone(reloaded_resolved_path)
        reloaded_resolved_path = str(reloaded_resolved_path).lower()
        module_path = str(module_path).lower()
        self.assertTrue(reloaded_resolved_path.endswith(module_path))

        sdr_node = UsdMdl.RegistryUtils.GetShaderNodeForPrim(prim)
        self.assertIsNotNone(sdr_node)

        default_value = 2
        self.validate_property("updated", sdr_node, value_type_name, True, metadata, default_value)
