# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import unittest

import omni.kit.app
import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core.test_utils import XRTestVR

from .utils import (
    TestLogErrorChecker,
    VrTestProfile,
    check_whether_extension_is_disabled,
    check_whether_extension_is_enabled,
    get_all_profile_extensions,
    get_extension_id,
    set_extension_enabled_and_wait_few_frames,
)


class TestProfileExtensionsEnabled(omni.kit.test.AsyncTestCase):

    @unittest.skipIf(
        os.getenv("ETM_ACTIVE"), "OMPE-30890: We can't get expected number of profile extensions from extension manager"
    )
    async def test_amount_of_profiles(self):
        """
        Tests whether there is at least the same amount of KIT XR profile extensions
        """
        profiles_amount = len(get_all_profile_extensions())

        # There should be at least 2 KIT XR profile extensions (common and derived profile)
        minimum_expected_amount_of_profile_extensions = 2
        self.assertGreaterEqual(
            profiles_amount,
            minimum_expected_amount_of_profile_extensions,
            f"There is less KIT XR profile extensions than {minimum_expected_amount_of_profile_extensions}! That is no expected!",
        )

    async def test_profile_common_is_enabled(self):
        """
        As a default omni.kit.xr.profile.common is enable KIT extension.
        """
        manager = omni.kit.app.get_app().get_extension_manager()
        self.assertTrue(manager.is_extension_enabled("omni.kit.xr.profile.common"))

    @unittest.skipIf(
        os.getenv("ETM_ACTIVE"), "OMPE-30890: We can't get expected number of profile extensions from extension manager"
    )
    async def test_profile_default_enabled_status(self):
        """
        Test default state of whether KIT XR profiles are enabled or disabled
        """
        manager = omni.kit.app.get_app().get_extension_manager()
        profiles = get_all_profile_extensions()
        enabled_profiles = 0
        disabled_profiles = 0
        for profile in profiles:
            ext_id = get_extension_id(profile)

            # only should happen for 'omni.kit.xr.profile.common' extension
            if manager.is_extension_enabled(ext_id):
                enabled_profiles = enabled_profiles + 1
            else:
                disabled_profiles = disabled_profiles + 1

        self.assertEqual(
            enabled_profiles,
            1,
            "There should be only one KIT profile extension enabled ('omni.kit.xr.profile.common') as a default",
        )
        self.assertGreater(disabled_profiles, 1, "There should be more than 1 disabled profiles as a default")

    async def test_enabling_profile_extensions_multiple_times(self):
        """
        Tests enabling each disable profile extension multiple times
        """
        manager = omni.kit.app.get_app().get_extension_manager()
        profiles = get_all_profile_extensions()
        amount_of_times_to_reenable_extension = 3
        for _ in range(amount_of_times_to_reenable_extension):
            for profile in profiles:
                ext_id = get_extension_id(profile)

                # only should happen for 'omni.kit.xr.profile.common' extension
                if manager.is_extension_enabled(ext_id):
                    continue

                print(f"test_load_extensions: Enabling {ext_id}")
                with TestLogErrorChecker(self, ext_id):
                    await set_extension_enabled_and_wait_few_frames(manager, ext_id, True)
                    check_whether_extension_is_enabled(self, ext_id)
                    await set_extension_enabled_and_wait_few_frames(manager, ext_id, False)
                    check_whether_extension_is_disabled(self, ext_id)


class TestProfileExtensionsIntegratedWithOtherComponents(XRTestVR):
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 0.5  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def test_profile_extensions_with_vr_profile_and_loaded_scene(self):
        """
        Tests enabling given KIT XR profile with already loaded USD scene. Then start vr test profile and then comparing golden images.
        """

        manager = omni.kit.app.get_app().get_extension_manager()
        profiles = get_all_profile_extensions()
        for profile in profiles:

            ext_id = get_extension_id(profile)

            # only should happen for 'omni.kit.xr.profile.common' extension
            if manager.is_extension_enabled(ext_id):
                continue

            # Loading scene
            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

            await self.wait_post_sync_async(5)

            print(f"test_load_extensions: Enabling {ext_id}")
            with TestLogErrorChecker(self, ext_id):

                # Enable profile extension
                await set_extension_enabled_and_wait_few_frames(manager, ext_id, True)
                check_whether_extension_is_enabled(self, ext_id)

                # Start VR profile
                async with VrTestProfile(self):
                    # Capture the screen and compare golden images
                    await self.capture_and_compare_viewport_output_async("load_while_in_vr_test", 0.001, __name__)

                    # Disable profile extension
                    await set_extension_enabled_and_wait_few_frames(manager, ext_id, False)
                    check_whether_extension_is_disabled(self, ext_id)
