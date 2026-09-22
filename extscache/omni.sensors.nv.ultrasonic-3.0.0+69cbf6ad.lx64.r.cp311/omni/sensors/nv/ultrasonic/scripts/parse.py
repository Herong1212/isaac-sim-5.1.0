import json
import os
import struct
from pathlib import Path

import carb
import carb.settings as set
import generic_model_output as gpc
import numpy as np


class SignalWay:
    num_samples = -1
    samples = np.zeros(0)
    timestamp_ns = -1
    tx_sensor_id = -1
    rx_sensor_id = -1
    channel = -1


class ProviderCycle:
    num_signalways = -1
    signalways = []
    timestamp_ns = -1
    cycle_idx = -1


def init(build_config="release", build_os="linux-x86_64", sensor_map=None, is_internal=False):
    framework = carb.get_framework()
    common_ext_path = "extsbuild/omni.sensors.nv.common/bin"

    if is_internal:
        common_ext_path = (
            str(Path(__file__).resolve().parents[4])
            + f"/_build/{build_os}/{build_config}/exts/omni.sensors.nv.common/bin"
        )

    # override extension search path if SENSOR_DEV_EXT_PATH is set
    if "SENSOR_DEV_EXT_PATH" in os.environ and os.environ["SENSOR_DEV_EXT_PATH"] is not None:
        common_ext_path = os.environ["SENSOR_DEV_EXT_PATH"] + "/omni.sensors.nv.common/bin"

    plugin_dirs = [common_ext_path]

    if "DRIVESIM_APP_PATH" in os.environ:
        plugin_dirs = [os.path.join(os.getenv("DRIVESIM_APP_PATH"), dirc) for dirc in plugin_dirs]
    if os.getenv("CARB_APP_PATH"):
        plugin_dirs.append(os.getenv("CARB_APP_PATH"))

    config_str = """
    pluginsLoaded = [
        "generic_mo_io.plugin"
    ]
    pluginSearchPaths = {}
    /log/level = "verbose"

    """.format(
        plugin_dirs
    )

    framework.startup([], config_str)
    framework.load_plugins(["generic_mo_io.plugin"], plugin_dirs)


def parse_dump_file(path, client_name="uss_front", group_name="Ultrasonic"):
    cfg = gpc.GMOIOConfig()
    cfg.accessType = gpc.AccessType.READ
    cfg.maxPoints = 16 * 320
    cfg.onlyValid = False
    cfg.loop = False
    cfg.clientName = client_name
    cfg.groupName = group_name
    cfg.fileName = path

    io = gpc.IGenericModelOutputIO()
    io.init(cfg)

    cycles = []
    counter = 40
    frame = io.readModelOutput(group_name, counter)
    while frame and frame.numElements != 0:
        cycle = ProviderCycle()
        cycle.signalways = []
        cycle.num_signalways = frame.numSgws
        for i in range(0, cycle.num_signalways):
            if frame.flags[i] == 1:
                signalway = SignalWay()
                signalway.samples = np.array(frame.scalar)
                signalway.timestamp_ns = np.uint64(frame.timeOffSetNs[i])
                signalway.tx_sensor_id = np.uint32(frame.x[i])
                signalway.rx_sensor_id = np.uint32(frame.y[i])
                signalway.channel = np.uint32(frame.z[i])
                cycle.signalways.append(signalway)

        cycle.timestamp_ns = frame.timestampNs
        cycle.cycle_idx = frame.frameId
        cycles.append(cycle)
        frame = io.readModelOutput(sensor_name, counter)
        counter += 1

    signalways = {}

    for cycle in cycles:
        for signalway in cycle.signalways:
            key = str(signalway.tx_sensor_id) + "-" + str(signalway.rx_sensor_id) + "-" + str(signalway.channel)
            if key not in signalways:
                signalways[key] = []

            signalways[key].append(signalway.samples)

    return signalways
