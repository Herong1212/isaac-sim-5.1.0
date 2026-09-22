# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["EnvironmentCapabilityTests"]

from omni.asset_validator.simready import EnvironmentCapabilityChecker
from pxr import Sdf

from .simready_common import AsyncValidationRuleTestCase, IsAFailure, IsAWarning, get_url


class EnvironmentCapabilityTests(AsyncValidationRuleTestCase):
    async def test_environment_success(self):
        await self.assertRuleAsync(
            asset=get_url("environment/environment_success.usda"),
            rule=EnvironmentCapabilityChecker,
            asserts=[
                IsAWarning(
                    "Number of traffic signals in the USD Environment (2) and associated XODR file (4) do not match.",
                    at=f"Stage <{get_url('environment/environment_success.usda')}>",
                ),
            ],
        )

    async def test_environment_no_xodr(self):
        await self.assertRuleAsync(
            asset=get_url("environment/environment_no_xodr.usda"),
            rule=EnvironmentCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid Environment: OpenDrive map file '@./non_existent.xodr@' not found.",
                    at=Sdf.Path("/RootNode.omni:simready:openDrive"),
                ),
            ],
        )

    async def test_environment_no_opendrive_attribute(self):
        await self.assertRuleAsync(
            asset=get_url("environment/environment_no_opendrive_attribute.usda"),
            rule=EnvironmentCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid Environment: missing attribute 'omni:simready:openDrive'.",
                    at=Sdf.Path("/RootNode"),
                ),
            ],
        )

    async def test_environment_not_xml_xodr(self):
        environment_not_xml_xodr_usda_file = get_url("environment/environment_not_xml_xodr.usda")
        not_xml_xodr_file = get_url("environment/not_xml.xodr")
        await self.assertRuleAsync(
            asset=get_url("environment/environment_not_xml_xodr.usda"),
            rule=EnvironmentCapabilityChecker,
            asserts=[
                IsAFailure(
                    f"Invalid Environment: OpenDrive map file {not_xml_xodr_file} cannot be parsed. Error: syntax error: line 1, column 0",
                    at=f"Stage <{environment_not_xml_xodr_usda_file}>",
                ),
            ],
        )

    async def test_environment_incorrect_opendrive_attribute_type(self):
        await self.assertRuleAsync(
            asset=get_url("environment/environment_incorrect_opendrive_attribute_type.usda"),
            rule=EnvironmentCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid Environment: incorrect attribute type 'string' found. Expected 'asset'.",
                    at=Sdf.Path("/RootNode.omni:simready:openDrive"),
                ),
            ],
        )

    async def test_environment_opendrive_attribute_time_varying(self):
        await self.assertRuleAsync(
            asset=get_url("environment/environment_opendrive_attribute_time_varying.usda"),
            rule=EnvironmentCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid Environment: attribute is time-varrying.",
                    at=Sdf.Path("/RootNode.omni:simready:openDrive"),
                ),
            ],
        )

    async def test_environment_invalid_traffic_signal_ids(self):
        await self.assertRuleAsync(
            asset=get_url("environment/environment_invalid_traffic_signal_ids.usda"),
            rule=EnvironmentCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid signal ID value -1. Signal IDs must be positive.",
                    at=Sdf.Path("/RootNode/traffic_signal_invalid_id.omni:simready:signalID"),
                ),
                IsAFailure(
                    "Duplicate signal ID 3050 found.",
                    at=Sdf.Path("/RootNode/traffic_signal_3050_duplicate_id.omni:simready:signalID"),
                ),
                IsAFailure(
                    "Attribute has no value.",
                    at=Sdf.Path("/RootNode/traffic_signal_no_id.omni:simready:signalID"),
                ),
                IsAFailure(
                    "Attribute has incorrect type 'float'. Expected 'int64'.",
                    at=Sdf.Path("/RootNode/traffic_signal_wrong_type.omni:simready:signalID"),
                ),
                IsAFailure(
                    "Attribute is time-varrying.",
                    at=Sdf.Path("/RootNode/traffic_signal_time_varying.omni:simready:signalID"),
                ),
                IsAWarning(
                    "Number of traffic signals in the USD Environment (2) and associated XODR file (4) do not match.",
                    at=f"Stage <{get_url('environment/environment_invalid_traffic_signal_ids.usda')}>",
                ),
                IsAFailure(
                    "Signal 9999 found in USD Environment not found in XODR file.",
                    at=f"Stage <{get_url('environment/environment_invalid_traffic_signal_ids.usda')}>",
                ),
            ],
        )
