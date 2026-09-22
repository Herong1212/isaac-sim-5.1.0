import asyncio
from pathlib import Path

import omni.UsdMdl as UsdMdl
from pxr import Ndr, Sdf, Sdr

from .lib.base import UsdMdlTestBase


class Discovery_Preview_Surface_Tests(UsdMdlTestBase):
    async def test_omni_usd_mdl_discover_preview_surface_on_startup(self):
        # This test serves two purposes:
        # 1. To verify that the UsdPreviewSurface module loads and that it contains the expected material and shaders
        # 2. For each material and shader, we validate the parameter names and types against the glslfx implementation.
        #  The glslfx implementation ships with OpenUsd and should serve as a ground truth.

        def get_property_type(ndr_type_indicator):
            type_name = ndr_type_indicator[1]

            if type_name:
                if type_name == "terminal":
                    type_name = "token"

                type_name = Sdf.ValueTypeNames.Find(type_name)
            else:
                type_name = ndr_type_indicator[0]

            return type_name

        sdr = Sdr.Registry()

        preview_surface_identifiers = ["UsdPreviewSurface", "UsdTransform2d", "UsdUVTexture"]
        for data_type in ["float", "float2", "float3", "int", "matrix", "normal", "point", "string", "vector"]:
            preview_surface_identifiers.append(f"UsdPrimvarReader_{data_type}")

        for sdr_node_id in preview_surface_identifiers:
            # Verify module loaded and the expected materials and shaders exist in it.
            mdl_sdr_node = sdr.GetShaderNodeByIdentifierAndType(sdr_node_id, UsdMdl.Tokens.Mdl)
            self.assertTrue(mdl_sdr_node)
            file_name = Path(mdl_sdr_node.GetResolvedImplementationURI()).name
            self.assertTrue(file_name, "UsdPreviewSurface.mdl")

            # validate shader properties and types
            glslfx_sdr_node = sdr.GetShaderNodeByIdentifierAndType(sdr_node_id, "glslfx")
            self.assertTrue(glslfx_sdr_node)

            for name in glslfx_sdr_node.GetInputNames():
               glslfx_property = glslfx_sdr_node.GetInput(name)
               self.assertTrue(glslfx_property)

               mdl_property = mdl_sdr_node.GetInput(name)
               self.assertTrue(mdl_property)

               glslfx_property_type = get_property_type(glslfx_property.GetTypeAsSdfType())
               mdl_property_type = get_property_type(mdl_property.GetTypeAsSdfType())
               self.assertTrue(glslfx_property_type == mdl_property_type)

            for name in glslfx_sdr_node.GetOutputNames():
               glslfx_property = glslfx_sdr_node.GetOutput(name)
               self.assertTrue(glslfx_property)

               mdl_property = mdl_sdr_node.GetOutput(name)
               self.assertTrue(mdl_property)

               glslfx_property_type = get_property_type(glslfx_property.GetTypeAsSdfType())
               mdl_property_type = get_property_type(mdl_property.GetTypeAsSdfType())
               self.assertTrue(glslfx_property_type == mdl_property_type)
