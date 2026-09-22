# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import os
import sys
import threading
import time

import carb
import carb.settings
import generic_model_output as gmo_utils
import omni.sensors.nv.common._common as common  # noqa: N813, E402
import omni.sensors.nv.lidar._lidar as lidar  # noqa: F401, E402

from .scripts.LidarFWLoader import LidarFWLoader  # noqa: E402
from .scripts.LidarUtilities import PCGeneratorConfig, generate_pc_from_file  # noqa: N813, E402
from .scripts.VizSender import VizSender  # noqa: E402


def convert_pc_and_send_pc(cfg, viz=True, sleep_time=0.08):
    viz_sender = None
    if viz:
        channelspec = {
            "backend": "net_realm",
            "type": "REALM",
            "key": "viz",
            "sending": True,
            "remoteProcessIdx": 0,
        }
        viz_sender = VizSender(channelspec, 1)

    def thread_fun():
        for i, pc in enumerate(generate_pc_from_file(cfg)):
            print(i)
            print(pc.numElements)
            if viz:
                viz_sender.convert_and_send_pc(pc)
            time.sleep(sleep_time)
            # break

    thread = threading.Thread(target=thread_fun)
    thread.start()


def start_dwpackets(bin_file, profile_name, viz=False):
    cfg = PCGeneratorConfig(bin_file, profile_name)
    cfg.cfg.mode = lidar.LidarPCConverterMode.PACKETS
    # cfg.cfg.runMode = lidar.LidarPCConverterRunMode.CPU
    # cfg.cfg.desiredCoordsType = gmo_utils.CoordsType.CARTESIAN
    # cfg.cfg.maxPoints = 1000000
    # cfg.cfg.rightHanded = True
    # cfg.cfg.scanFrequencyHz = 10
    convert_pc_and_send_pc(cfg, viz)


def start_hdf5(bin_file, viz=False, sensor_name="hesai_left"):
    cfg = PCGeneratorConfig(bin_file, "", sensor_name)
    cfg.cfg.mode = lidar.LidarPCConverterMode.GENERIC_FILE
    cfg.cfg.runMode = lidar.LidarPCConverterRunMode.CPU
    cfg.cfg.desiredCoordsType = gmo_utils.CoordsType.CARTESIAN
    cfg.cfg.maxPoints = 921600
    # cfg.pos = [1.0,0.0,0.0]
    # cfg.roll_pitch_yaw = [0.0,0.0,0.0]
    # cfg.cfg.scanFrequencyHz = 10
    convert_pc_and_send_pc(cfg, viz, 0.08)


def start_packets(bin_file, profile_name, viz=False):
    cfg = PCGeneratorConfig(bin_file, profile_name)
    cfg.cfg.mode = lidar.LidarPCConverterMode.PACKETS
    cfg.cfg.runMode = lidar.LidarPCConverterRunMode.CPU
    cfg.cfg.desiredCoordsType = gmo_utils.CoordsType.CARTESIAN
    cfg.cfg.maxPoints = 921600
    convert_pc_and_send_pc(cfg, viz)


def test():
    dumpfilename = ""
    start_hdf5(dumpfilename, True, "lidar1")
    # carb.settings.get_settings().set_string_array("/app/sensors/nv/lidar/profileBaseFolder",[profilefolder])
    # dumpfilename = ""
    # start_packets(dumpfilename, "Hesai_P128_V4P5_HR10", False)


if __name__ == "__main__":

    loader = LidarFWLoader()
    test()
