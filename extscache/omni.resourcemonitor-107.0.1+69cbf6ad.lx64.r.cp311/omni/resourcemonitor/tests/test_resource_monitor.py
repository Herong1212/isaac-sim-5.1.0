# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import numpy as np

import carb.settings

import omni.kit.test

import omni.resourcemonitor as rm


class TestResourceSettings(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        self._savedSettings = {}
        self._rm_interface = rm.acquire_resource_monitor_interface()
        self._settings = carb.settings.get_settings()

        # Save current settings
        self._savedSettings[rm.timeBetweenQueriesSettingName] = \
            self._settings.get_as_float(rm.timeBetweenQueriesSettingName)

        self._savedSettings[rm.sendDeviceMemoryWarningSettingName] = \
            self._settings.get_as_bool(rm.sendDeviceMemoryWarningSettingName)

        self._savedSettings[rm.deviceMemoryWarnMBSettingName] = \
            self._settings.get_as_int(rm.deviceMemoryWarnMBSettingName)

        self._savedSettings[rm.deviceMemoryWarnFractionSettingName] = \
            self._settings.get_as_float(rm.deviceMemoryWarnFractionSettingName)

        self._savedSettings[rm.sendHostMemoryWarningSettingName] = \
            self._settings.get_as_bool(rm.sendHostMemoryWarningSettingName)

        self._savedSettings[rm.hostMemoryWarnMBSettingName] = \
            self._settings.get_as_int(rm.hostMemoryWarnMBSettingName)

        self._savedSettings[rm.hostMemoryWarnFractionSettingName] = \
            self._settings.get_as_float(rm.hostMemoryWarnFractionSettingName)

    # After running each test
    async def tearDown(self):
        # Restore settings
        self._settings.set_float(
            rm.timeBetweenQueriesSettingName,
            self._savedSettings[rm.timeBetweenQueriesSettingName])

        self._settings.set_bool(
            rm.sendDeviceMemoryWarningSettingName,
            self._savedSettings[rm.sendDeviceMemoryWarningSettingName])

        self._settings.set_int(
            rm.deviceMemoryWarnMBSettingName,
            self._savedSettings[rm.deviceMemoryWarnMBSettingName])

        self._settings.set_float(
            rm.deviceMemoryWarnFractionSettingName,
            self._savedSettings[rm.deviceMemoryWarnFractionSettingName])

        self._settings.set_bool(
            rm.sendHostMemoryWarningSettingName,
            self._savedSettings[rm.sendHostMemoryWarningSettingName])

        self._settings.set_int(
            rm.hostMemoryWarnMBSettingName,
            self._savedSettings[rm.hostMemoryWarnMBSettingName])

        self._settings.set_float(
            rm.hostMemoryWarnFractionSettingName,
            self._savedSettings[rm.hostMemoryWarnFractionSettingName])

    async def test_resource_monitor(self):
        """
        Test host memory warnings by setting the warning threshold to slightly
        less than 10 GB below current memory usage then allocating a 10 GB buffer
        """

        hostBytesAvail = self._rm_interface.get_available_host_memory()

        memoryToAlloc = 10 * 1024 * 1024 * 1024
        queryTime = 0.1

        fudge = 512 * 1024 * 1024 # make sure we go below the warning threshold
        warnHostThresholdBytes = hostBytesAvail - memoryToAlloc + fudge

        self._settings.set_float(
            rm.timeBetweenQueriesSettingName,
            queryTime)
        self._settings.set_bool(
            rm.sendHostMemoryWarningSettingName,
            True)
        self._settings.set_int(
            rm.hostMemoryWarnMBSettingName,
            warnHostThresholdBytes // (1024 * 1024)) # bytes to MB

        hostMemoryWarningOccurred = False

        def on_rm_update(event):
            nonlocal hostMemoryWarningOccurred
            hostBytesAvail = self._rm_interface.get_available_host_memory()
            if event.type == int(rm.ResourceMonitorEventType.LOW_HOST_MEMORY):
                hostMemoryWarningOccurred = True

        sub = self._rm_interface.get_event_stream().create_subscription_to_pop(on_rm_update, name='resource monitor update')
        self.assertIsNotNone(sub)

        # allocate something
        numElements = memoryToAlloc // np.dtype(np.int64).itemsize
        array = np.zeros(numElements, dtype=np.int64)
        array[:] = 1

        # give time for a resourcemonitor event to come through
        await self.assertTrueWithRetry(lambda: hostMemoryWarningOccurred, max_retries=100)