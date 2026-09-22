# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.test
import omni.kit.app
import omni.usd
import omni.client.utils as clientutils

from unittest.mock import Mock
from pxr import Usd, UsdGeom, Gf, Sdf


class TestUsdWatcher(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        self.usd_watcher = omni.usd.get_watcher()
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        if omni.usd.get_context().get_stage():
            await omni.usd.get_context().close_stage_async()

    async def wait(self, frames=3):
        for i in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_usd_watcher(self):
        # Loop 3 times to ensure stage switch will not influence USD subscription.
        for _ in range(2):
            await omni.usd.get_context().new_stage_async()
            self.stage = omni.usd.get_context().get_stage()

            for i in range(20):
                await self.wait()
                mocked_prim_cb = Mock()
                sub = self.usd_watcher.subscribe_to_resync_path("/Cube", mocked_prim_cb)
                prim = self.stage.DefinePrim("/Cube", "Cube")
                await self.wait()
                mocked_prim_cb.assert_called_once()

                # Property resync
                mocked_property_cb = Mock()
                sub = self.usd_watcher.subscribe_to_resync_path("/Cube.custom", mocked_property_cb)
                attr = prim.CreateAttribute("custom", Sdf.ValueTypeNames.Float)
                await self.wait()
                mocked_property_cb.assert_called_once()

                self.stage.RemovePrim("/Cube")

            prim = self.stage.DefinePrim("/Cube", "Cube")
            attr = prim.CreateAttribute("custom", Sdf.ValueTypeNames.Float)
            await self.wait()

            for i in range(20):
                # Property changed
                mocked_property_cb = Mock()
                sub = self.usd_watcher.subscribe_to_change_info_path("/Cube.custom", mocked_property_cb)
                attr.Set(i)
                await self.wait()
                mocked_property_cb.assert_called_once()

        mocked_prim_cb = Mock()
        sub = self.usd_watcher.subscribe_to_resync_path("/Cube", mocked_prim_cb)
        # Subscribes changes beforehand and swtiches stage will not influence subscription
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()
        prim = self.stage.DefinePrim("/Cube", "Cube")
        await self.wait()
        mocked_prim_cb.assert_called_once()

        mocked_prim_cb = Mock()
        sub = self.usd_watcher.subscribe_to_resync_path("/Cube", mocked_prim_cb)
        # Clear sub to see if mock is called
        sub = None
        self.stage.RemovePrim("/Cube")
        await self.wait()
        mocked_prim_cb.assert_not_called()

        # Only stage in default context can influence subscriptions.
        mocked_prim_cb = Mock()
        sub = self.usd_watcher.subscribe_to_resync_path("/Cube", mocked_prim_cb)
        new_stage = Usd.Stage.CreateInMemory()
        new_stage.DefinePrim("/Cube", "Cube")
        await self.wait()
        mocked_prim_cb.assert_not_called()
