# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from omni.asset_validator.core import registerRule

from ._component_ground_truth_capability import GroundTruthCapabilityChecker
from ._component_non_visual_sensor_capability import NonVisualSensorCapabilityChecker
from ._component_visual_sensor_capability import VisualSensorCapabilityChecker
from ._environment_capability import EnvironmentCapabilityChecker
from ._environment_light_capability import EnvironmentLightCapabilityChecker
from ._geometry_capability import ContainsMeshChecker
from ._pedestrian_capability import PedestrianCapabilityChecker
from ._traffic_light_capability import TrafficLightCapabilityChecker
from ._units_capability import MetersPerUnit1Checker, UpAxisZChecker
from ._vehicle_capability import VehicleCapabilityChecker

__all__ = [
    "EnvironmentCapabilityChecker",
    "EnvironmentLightCapabilityChecker",
    "GroundTruthCapabilityChecker",
    "NonVisualSensorCapabilityChecker",
    "PedestrianCapabilityChecker",
    "TrafficLightCapabilityChecker",
    "VehicleCapabilityChecker",
    "VisualSensorCapabilityChecker",
    "UpAxisZChecker",
    "MetersPerUnit1Checker",
    "ContainsMeshChecker",
]


registerRule("Omni:SimReady")(GroundTruthCapabilityChecker)
registerRule("Omni:SimReady")(NonVisualSensorCapabilityChecker)
registerRule("Omni:SimReady")(VisualSensorCapabilityChecker)
registerRule("Omni:SimReady")(EnvironmentCapabilityChecker)
registerRule("Omni:SimReady")(EnvironmentLightCapabilityChecker)
registerRule("Omni:SimReady")(PedestrianCapabilityChecker)
registerRule("Omni:SimReady")(TrafficLightCapabilityChecker)
registerRule("Omni:SimReady")(VehicleCapabilityChecker)
registerRule("Omni:SimReady")(UpAxisZChecker)
registerRule("Omni:SimReady")(MetersPerUnit1Checker)
registerRule("Omni:SimReady")(ContainsMeshChecker)
