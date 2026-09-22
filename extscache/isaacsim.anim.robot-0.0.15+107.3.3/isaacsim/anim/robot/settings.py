# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from dataclasses import dataclass


@dataclass
class SimulationSettings:
    dynamic_avoidance: str = "/exts/isaacsim.anim.robot/simulation_settings/dynamic_avoidance"


@dataclass
class CommandSettings:
    command_file_path: str = "/exts/isaacsim.anim.robot/command_settings/command_file_path"
