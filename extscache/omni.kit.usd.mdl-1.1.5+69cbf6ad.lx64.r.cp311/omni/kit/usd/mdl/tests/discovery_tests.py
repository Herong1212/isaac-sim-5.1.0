import asyncio
from pathlib import Path

import omni.UsdMdl as UsdMdl
from pxr import Ndr, Sdf, Sdr

from .lib.base import UsdMdlTestBase


class Discovery_Tests(UsdMdlTestBase):
    async def test_omni_usd_mdl_discover_on_startup(self):
        # Note: this test is setup in the extension.toml to only load mdl modules from the data folder of the extension.
        # Check to see if these modules have been found by the discovery process.
        # The discovery process will find modules in the user directories, therefore the test is to verify the
        # modules in extension/mdl have been found and loaded.

        modules = [file.name for file in Path(self.mdl_path).glob("*.mdl")]

        sdr = Sdr.Registry()

        found = set()

        for sdr_node_id in sdr.GetNodeIdentifiers(filter=Ndr.VersionFilterAllVersions):
            sdr_node = sdr.GetShaderNodeByIdentifier(sdr_node_id)

            if (not sdr_node) or (sdr_node.GetSourceType() != UsdMdl.Tokens.Mdl):
                continue

            file_name = Path(sdr_node.GetResolvedImplementationURI()).name
            if file_name in modules:
                found.add(file_name)

        self.assertTrue(len(modules) == len(found))