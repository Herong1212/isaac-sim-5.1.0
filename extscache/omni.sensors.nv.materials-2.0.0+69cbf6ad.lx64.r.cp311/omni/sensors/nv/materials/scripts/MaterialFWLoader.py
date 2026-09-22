# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import os
from pathlib import Path

import carb


class MaterialFWLoader:
    def __init__(self, is_internal=False):
        self.framework = carb.get_framework()
        lidar_ext_path = "extsbuild/omni.sensors.nv.lidar/bin"
        common_ext_path = "extsbuild/omni.sensors.nv.common/bin"
        materials_ext_path = "extsbuild/omni.sensors.nv.materials/bin"
        if is_internal:
            common_ext_path = (
                str(Path(__file__).resolve().parents[4])
                + f"/_build/linux-x86_64/release/exts/omni.sensors.nv.common/bin"
            )
            lidar_ext_path = (
                str(Path(__file__).resolve().parents[4])
                + f"/_build/linux-x86_64/release/exts/omni.sensors.nv.lidar/bin"
            )
            materials_ext_path = (
                str(Path(__file__).resolve().parents[4])
                + f"/_build/linux-x86_64/release/exts/omni.sensors.nv.materials/bin"
            )

        if "SENSOR_DEV_EXT_PATH" in os.environ and os.environ["SENSOR_DEV_EXT_PATH"] is not None:
            lidar_ext_path = os.environ["SENSOR_DEV_EXT_PATH"] + "/omni.sensors.nv.lidar/bin"
            common_ext_path = os.environ["SENSOR_DEV_EXT_PATH"] + "/omni.sensors.nv.common/bin"
            materials_ext_path = os.environ["SENSOR_DEV_EXT_PATH"] + "/omni.sensors.nv.materials/bin"

        plugin_dirs = [
            "plugins",
            lidar_ext_path,
            common_ext_path,
            materials_ext_path,
        ]

        if "DRIVESIM_APP_PATH" in os.environ:
            plugin_dirs = [os.path.join(os.getenv("DRIVESIM_APP_PATH"), dirc) for dirc in plugin_dirs]
        if os.getenv("CARB_APP_PATH"):
            plugin_dirs.append(os.getenv("CARB_APP_PATH"))

        config_str = """
        pluginsLoaded = [
            "omni.exec",
            "omni.sensors.nv.common.profile_reader.plugin",
            "material_profile_reader.plugin",
            "material_util_bsdf.plugin",
            "omni.sensors.nv.lidar.nvlidar_pc_converter.plugin",
        ]
        pluginSearchPaths = {}
            /log/level = "verbose"

        """.format(
            plugin_dirs
        )
        # for more info framework.startup(["--verbose-config"], config_str), also log line in toml above
        self.framework.startup([], config_str)
        self.framework.load_plugins(
            [
                "omni.sensors.nv.common.profile_reader.plugin",
                "omni.sensors.nv.lidar.nvlidar_pc_converter.plugin",
                "material_profile_reader.plugin",
                "material_util_bsdf.plugin",
            ],
            plugin_dirs,
        )
        # for plugin in self.framework.get_plugins():
        #     print(plugin.libPath)


if __name__ == "__main__":
    loader = MaterialFWLoader()
