import os
from copy import deepcopy
from math import radians
from pathlib import Path
from typing import List

import carb
import generic_model_output as gpc
from omni.sensors.nv.radar.scripts.radar_data_integrity import run_radar_data_integrity_tests  # noqa: E402

# from radar_detection import *
from omni.sensors.nv.radar.scripts.radar_detection import *  # noqa: E402


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


def gen_gmo_frame_to_radar_scan(frames: List[GmoRadarFrame]):

    scans = []

    for frame in frames:
        scan = RadarPointCloud()
        scan.frameId = frame.frameId
        scan.timestamp_ns = frame.timestampNs
        scan.sensor_id = frame.sensorID
        scan.scan_idx = frame.scanIdx
        scan.cycle_cnt = frame.cycleCnt
        scan.max_range_m = frame.maxRangeM
        scan.min_vel_mps = frame.minVelMps
        scan.max_vel_mps = frame.maxVelMps
        scan.min_az_rad = frame.minAzRad
        scan.max_az_rad = frame.maxAzRad
        scan.min_el_rad = frame.minElRad
        scan.max_el_rad = frame.maxElRad

        scan.detections = []
        az_ang_rad, elev_ang_rad, r_m = frame.get_az_el_range()

        for i in range(0, frame.numElements):
            detection = RadarDetection()
            detection.az_ang_rad = az_ang_rad[i]
            detection.elev_ang_rad = elev_ang_rad[i]
            detection.r_m = r_m[i]
            detection.rv_ms = frame.rv_ms[i]
            detection.rcs_dbsm = frame.scalar[i]

            scan.detections.append(detection)

        scan.num_detections = frame.numElements
        scans.append(scan)

    for scan in scans:
        yield scan


_gmo_parser_used_client_names = []


# Parses a GMO file and returns a list of GmoRadarFrame objects.
def parse_gmo_radar_file(h5_path, client_name="radar_front_corner_right", group_name="Radar"):

    global _gmo_parser_used_client_names

    if client_name in _gmo_parser_used_client_names:
        print(
            "ERROR: Client name already used. For the h5 GMO parser to not mix up files and create ugly errors, the same client name must not be used twice."
        )
        return None
    _gmo_parser_used_client_names.append(client_name)

    # For debugging, save a file called ref-wpm_radar_2.h5 in the reference
    # folder and uncomment the following two lines.  Moreover, do not execute kit in
    # test_compute_stability_regressions(..) in test_sensors.py.
    # if "_test" in h5_path:
    #     h5_path = "/home/mmontebaur/Documents/kit-mmontebaur/kit/source/tests/test.pytest/sensors/compute_stability/ref-wpm_radar_2.h5"

    print("Radar parser: Reading GMO file {0}".format(h5_path))
    cfg = gpc.GMOIOConfig()
    cfg.accessType = gpc.AccessType.READ
    cfg.maxPoints = MAX_NUM_DETS
    cfg.onlyValid = True
    cfg.loop = False
    cfg.groupName = group_name
    cfg.clientName = client_name
    cfg.fileName = h5_path
    io = gpc.IGenericModelOutputIO()
    io.init(cfg)
    last_frame_id = None
    frames = []

    # Note: counter needs to be used and setting it to -1 is not sufficient!
    # Otherwise, the internal state of the gmo io parser is used and it does not
    # reset between runs, meaning that once file 1 with 800 frames is parsed and
    # this function here is called again for file 2, it will continue with frame
    # 801 in file 2.
    counter = 0

    while True:
        f = io.readModelOutput(group_name, counter)
        # from_readModelOutput returns a GmoRadarFrame object that allows for type completion and stuff
        frame: GmoRadarFrame = GmoRadarFrame.from_readModelOutput(f)
        if frame.frameId == last_frame_id:
            break
        last_frame_id = frame.frameId

        counter += 1
        # deepcopy is important, otherwise parts of the frame object are freed by the python bindings
        frames.append(deepcopy(frame))

    del io
    del cfg

    if not run_radar_data_integrity_tests(frames):
        return None

    print("-> Radar parser: Finished reading {0} GMO frames from file: {1}".format(len(frames), h5_path))

    return frames
