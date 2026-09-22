## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test

import omni.kit.livestream.bind


def qos_status_callback(qos_status):
    # Will never actually be called in the context of this test.
    self.assertIsNotNone(qos_status)

class TestLivestreamWebRtc(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._kit_livestream = omni.kit.livestream.bind.acquire_livestream_interface()

    async def tearDown(self):
        self._kit_livestream = None

    async def test_qos_status_callback(self):
        # Register a callback.
        qos_status_callback_id = self._kit_livestream.register_qos_status_callback(qos_status_callback)
        self.assertIsNotNone(qos_status_callback_id)
        self.assertNotEqual(qos_status_callback_id, 0)

        # Register the same callback again.
        qos_status_callback_id_2 = self._kit_livestream.register_qos_status_callback(qos_status_callback)
        self.assertIsNotNone(qos_status_callback_id_2)
        self.assertNotEqual(qos_status_callback_id, qos_status_callback_id_2)

        # Deregister a callback id that was never registered.
        result = self._kit_livestream.deregister_qos_status_callback(999)
        self.assertFalse(result)

        # Deregister the second callback id that was registered.
        result = self._kit_livestream.deregister_qos_status_callback(qos_status_callback_id_2)
        self.assertTrue(result)

        # Deregister the second callback id that was already deregistered.
        result = self._kit_livestream.deregister_qos_status_callback(qos_status_callback_id_2)
        self.assertFalse(result)

        # Deregister the first callback id that was registered.
        result = self._kit_livestream.deregister_qos_status_callback(qos_status_callback_id)
        self.assertTrue(result)
