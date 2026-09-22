# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core import XRCore, XRCoreEventType
from omni.kit.xr.core.test_utils import TestVRProfile, XRTestVR


class TestXRCoreEvent(XRTestVR):
    @test_utils.opened_usd_stage()
    async def test_unit_xrcore_events(self):
        """Launch VR and load a scene"""

        # Create a test profile
        async with TestVRProfile(self):

            self._test_pre_sync_triggered = False
            self._test_post_sync_triggered = False
            self._test_pre_render_triggered = False

            def on_pre_sync(ev):
                self._test_pre_sync_triggered = True

            def on_post_sync(ev):
                self._test_post_sync_triggered = True

            await self.wait_post_sync_async()

            subs = []
            subs.append(
                XRCore.get_singleton()
                .get_message_bus()
                .create_subscription_to_pop_by_type(XRCoreEventType.pre_sync_update, on_pre_sync, name="Pre Sync")
            )

            subs.append(
                XRCore.get_singleton()
                .get_message_bus()
                .create_subscription_to_pop_by_type(XRCoreEventType.post_sync_update, on_post_sync, name="Post Sync")
            )

            await self.wait_post_sync_async(2)

            self.assertEqual(self._test_pre_sync_triggered, True)
            self.assertEqual(self._test_post_sync_triggered, True)

            subs = []
