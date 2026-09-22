## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestExtension']

import omni.kit.actions.core
from omni.kit.test import AsyncTestCase


class TestExtension(AsyncTestCase):
    async def setUp(self):
        self.extension_id = "omni.kit.viewport.actions"

    async def wait_n_updates(self, n_frames: int = 3):
        app = omni.kit.app.get_app()
        for _ in range(n_frames):
            await app.next_update_async()

    async def test_extension_start_stop(self):
        manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = self.extension_id
        self.assertTrue(ext_id)
        self.assertTrue(manager.is_extension_enabled(ext_id))

        manager.set_extension_enabled(ext_id, False)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(not manager.is_extension_enabled(ext_id))

        manager.set_extension_enabled(ext_id, True)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(manager.is_extension_enabled(ext_id))
