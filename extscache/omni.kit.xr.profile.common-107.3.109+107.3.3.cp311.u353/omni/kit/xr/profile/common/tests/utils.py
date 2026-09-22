# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import List, Optional

import carb
import omni.kit.app
from omni.kit.xr.core.test_utils import XRTestVR


class TestLogErrorChecker(XRTestVR):
    """
    Helper class wrapping LogErrorChecker into control-flow structure. It tests whether LogErrorChecker logged any errors on 'exit'.
    Initialize the class with instance of unittest class (to be able to invoke assert on exit)
    """

    def __init__(self, test_class_instance, ext_id):
        self.log_checker = LogErrorChecker()
        self.test_class_instance = test_class_instance
        self.ext_id = ext_id

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        error_count = self.log_checker.get_error_count()
        self.test_class_instance.assertEqual(
            error_count, 0, f"There are '{error_count}' produced  errors! Current extension id is '{self.ext_id}'"
        )


class LogErrorChecker:
    """Automatically subscribes to logging events and monitors if error were produced during the test."""

    def __init__(self):
        # Setup this test case to fail if any error is produced
        self._error_count = 0

        def on_log_event(e):
            if e.payload["level"] >= carb.logging.LEVEL_ERROR:
                self._error_count = self._error_count + 1

        self._log_stream = omni.kit.app.get_app().get_log_event_stream()
        self._log_sub = self._log_stream.create_subscription_to_pop(on_log_event, name="test log event")

    def shutdown(self):
        self._log_stream = None
        self._log_sub = None

    def get_error_count(self):
        self._log_stream.pump()
        return self._error_count


def get_all_profile_extensions() -> List[dict]:
    """
    Returns list of all KIT extensions which starts with "omni.kit.xr.profile".
    Each record in a list is a dictionary of extension properties (like id, name etc.)
    """
    manager = omni.kit.app.get_app().get_extension_manager()
    all_extensions = manager.get_extensions()
    profile_extensions = [
        kit_extension for kit_extension in all_extensions if kit_extension["id"].startswith("omni.kit.xr.profile")
    ]
    return profile_extensions


def get_extension_id(kit_extension_record) -> Optional[str]:
    """
    Return KIT extension Id (ext_id). If it doesn't exist, return None
    """
    if "id" not in kit_extension_record:
        print(f"There is no 'id' in KIT extension '{kit_extension_record}'")
        return None

    ext_id = kit_extension_record["id"]
    return ext_id


async def set_extension_enabled_and_wait_few_frames(manager, ext_id: str, enabled: bool):
    """
    Use extension manager to set extension enabled/disabled, and wait few updates.
    """
    manager.set_extension_enabled_immediate(ext_id, enabled)
    for _ in range(5):
        await omni.kit.app.get_app().next_update_async()


def check_whether_extension_is_enabled(test_instance, ext_id):
    manager = omni.kit.app.get_app().get_extension_manager()
    test_instance.assertTrue(manager.is_extension_enabled(ext_id), f"Extension failed to load: {ext_id}")


def check_whether_extension_is_disabled(test_instance, ext_id):
    manager = omni.kit.app.get_app().get_extension_manager()
    test_instance.assertFalse(manager.is_extension_enabled(ext_id), f"Extension failed to unload: {ext_id}")


class VrTestProfile:
    """
    Helper class invoking starting/stopping vr_test_profile frm XRTestVR instance.
    """

    def __init__(self, test_class_instance: XRTestVR):
        self.test_class_instance = test_class_instance

    async def __aenter__(self):
        await self.test_class_instance.start_vr_test_profile()
        await self.test_class_instance.wait_post_sync_async(3)

    async def __aexit__(self, type, value, traceback):
        # That clears vr_test_profile. Maybe it should be polished in future to do
        # only necessary clean up instead of the whole tearDown.
        await self.test_class_instance.tearDown()
