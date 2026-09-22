## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test

import omni.activity.profiler

import carb.profiler


class TestActivityProfiler(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._activity_profiler = omni.activity.profiler.get_activity_profiler()
        self._carb_profiler = carb.profiler.acquire_profiler_interface(plugin_name="omni.activity.profiler.plugin")

    async def tearDown(self):
        self._carb_profiler = None
        self._activity_profiler = None

    async def test_activity_profiler_masks(self):
        # Verify the initial value of the activity profiler capture mask.
        self.assertEqual(self._carb_profiler.get_capture_mask(), 0)

        # Set the base activity profiler capture mask directly through the carb profiler API.
        self._carb_profiler.set_capture_mask(omni.activity.profiler.CAPTURE_MASK_STARTUP)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP)

        # Enable an activity profiler capture mask through the activity profiler API.
        uid1 = self._activity_profiler.enable_capture_mask(omni.activity.profiler.CAPTURE_MASK_LATENCY)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP |
                                                                 omni.activity.profiler.CAPTURE_MASK_LATENCY)

        # Enable another activity profiler capture mask through the activity profiler API.
        uid2 = self._activity_profiler.enable_capture_mask(omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP |
                                                                 omni.activity.profiler.CAPTURE_MASK_LATENCY |
                                                                 omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)

        # Enable an activity profiler capture mask for the second time through the activity profiler API.
        uid3 = self._activity_profiler.enable_capture_mask(omni.activity.profiler.CAPTURE_MASK_LATENCY)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP |
                                                                 omni.activity.profiler.CAPTURE_MASK_LATENCY |
                                                                 omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)

        # Disable the activity profiler capture mask that was set a second time through the activity profiler API.
        self._activity_profiler.disable_capture_mask(uid3)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP |
                                                                 omni.activity.profiler.CAPTURE_MASK_LATENCY |
                                                                 omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)

        # Disable the first activity profiler capture mask that was set through the activity profiler API.
        self._activity_profiler.disable_capture_mask(uid1)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP |
                                                                 omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)

        # Enable the same base activity profiler capture mask through the activity profiler API.
        uid4 = self._activity_profiler.enable_capture_mask(omni.activity.profiler.CAPTURE_MASK_STARTUP)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP |
                                                                 omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)

        # Disable the same base activity profiler capture mask that was set through the activity profiler API.
        self._activity_profiler.disable_capture_mask(uid4)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_STARTUP |
                                                                 omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)

        # Set the base activity profiler capture mask directly through the carb profiler API.
        self._carb_profiler.set_capture_mask(0)
        self.assertEqual(self._carb_profiler.get_capture_mask(), omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING)

        # Disable the second activity profiler capture mask that was set through the activity profiler API.
        self._activity_profiler.disable_capture_mask(uid2)
        self.assertEqual(self._carb_profiler.get_capture_mask(), 0)

        # Set the base activity profiler capture mask to something that is not an activity mask.
        self._activity_profiler.disable_capture_mask(1)
        self.assertEqual(self._carb_profiler.get_capture_mask(), 0)

        # Enable an activity profiler capture mask that is not an activity mask.
        uid5 = self._activity_profiler.enable_capture_mask(1)
        self.assertEqual(self._carb_profiler.get_capture_mask(), 0)

        # Disable the activity profiler capture mask that is not an activity mask.
        self._activity_profiler.disable_capture_mask(uid5)
        self.assertEqual(self._carb_profiler.get_capture_mask(), 0)
