import math
import os
import random
import string
import sys

import numpy as np

script_path = os.path.dirname(os.path.realpath(__file__)) + "/../../lidar/python/scripts"
sys.path.append(script_path)
import omni.sensors.nv.radar.scripts.gmo_radar_parser as gmo_radar_parser  # noqa: E402
from omni.sensors.nv.lidar.scripts.ComparePointClouds import calculate_metrics_for_npy_points  # noqa: E402
from omni.sensors.nv.radar.scripts.generic_radar_parser import get_radar_pc_gen  # noqa: E402


def init(build_config="r", build_os="l"):
    gmo_radar_parser.init(build_config, build_os)


def get_numpy_pc(pc):
    npc = np.empty((pc.num_detections, 3), dtype=float)
    npc[:, 0] = np.asarray([det.r_m * np.cos(det.elev_ang_rad) * np.cos(det.az_ang_rad) for det in pc.detections])
    npc[:, 1] = np.asarray([det.r_m * np.cos(det.elev_ang_rad) * np.sin(det.az_ang_rad) for det in pc.detections])
    npc[:, 2] = np.asarray([det.r_m * np.sin(det.az_ang_rad) for det in pc.detections])
    return npc


def get_uuid_str(n=20):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def get_scan_generator(file_path: str, client_name: str = None):
    if file_path.endswith(".bin"):
        return get_radar_pc_gen(file_path, False)
    elif file_path.endswith(".h5"):
        if client_name is None:
            client_name = get_uuid_str()

        # need a unique client name, otherwise the parser will introduce weird behavior
        frames = gmo_radar_parser.parse_gmo_radar_file(file_path, client_name=client_name, group_name="Radar")
        return gmo_radar_parser.gen_gmo_frame_to_radar_scan(frames)

    else:
        raise ValueError("Unknown file type: " + file_path)


def compare_radar_bin_files(bin_file, ref_file):

    gmo_radar_parser.init()

    gen_new = get_scan_generator(bin_file, client_name="radar_1")
    gen_ref = get_scan_generator(ref_file, client_name="radar_2")

    if not gen_new or not gen_ref:
        return 1000.0

    num_pcs = 0

    sum_distance_metric = 0.0
    sum_trafo_metric = 0.0
    sum_corr_metric = 0.0

    for _ in range(20):
        pc_new = next(gen_new, None)
        pc_ref = next(gen_ref, None)

    print("Starting comparison")
    print("frameId: new: ", pc_new.frameId, " ref: ", pc_ref.frameId)

    # Loading the world before the recording might take more or less time, so we need to align by frameId

    while pc_new is not None and pc_new.frameId < pc_ref.frameId:
        print("skipping new frameId: ", pc_new.frameId)
        pc_new = next(gen_new, None)
        # if pc_new is None or pc_ref is None:
        #     break

    while pc_ref is not None and pc_new.frameId > pc_ref.frameId:
        print("skipping ref frameId: ", pc_ref.frameId)
        pc_ref = next(gen_ref, None)
        # if pc_new is None or pc_ref is None:
        #     break

    # If timestamps are used for comparison, make sure that the same scan types are compared.
    # if abs(pc_new.max_range_m - pc_ref.max_range_m) > 0.1:
    #     # Advance another frames so that the same scan types are compared
    #     pc_new = next(gen_new, None)

    # print("Aligned timestamps: new: ", pc_new.timestamp_ns, " ref: ", pc_ref.timestamp_ns, "delta: ", (pc_new.timestamp_ns - pc_ref.timestamp_ns)/1e6)
    if pc_new is None or pc_ref is None:
        print("\nERROR: The difference in Frame IDs between new radar h5 file and the reference file is too large.")
        print(
            "  This usually happens if the duration of the scenario changed, e.g. because some sensor was added to or removed from the test."
        )
        print(
            "  This does not necessarily mean that the radar data is wrong, but it will make the comparison fail because no alignment between h5 files can be found.\n"
        )
        return 1000.0

    print("FrameIdx: new: ", pc_new.frameId, " ref: ", pc_ref.frameId)

    rm_deltas = []
    az_deltas = []
    el_deltas = []

    for i in range(0, 80):
        pc_new = next(gen_new, None)
        pc_ref = next(gen_ref, None)
        if pc_new is None or pc_ref is None:
            break

        # don't compare empty point clouds
        if pc_new.num_detections == 0 or pc_ref.num_detections == 0:
            continue

        npc_new = get_numpy_pc(pc_new)
        npc_ref = get_numpy_pc(pc_ref)

        # calculate deltas in pointcloud values
        if pc_new.num_detections != pc_ref.num_detections:
            print(f"Error: Number of detections not equal for frameId: {pc_new.frameId}")
            print(f"  ref: {pc_ref.num_detections} new: {pc_new.num_detections}")
            return 1000.0
        else:
            for j in range(pc_new.num_detections):
                delta_r_m = abs(pc_new.detections[j].r_m - pc_ref.detections[j].r_m)
                delta_az = math.degrees(abs(pc_new.detections[j].az_ang_rad - pc_ref.detections[j].az_ang_rad))
                delta_el = math.degrees(abs(pc_new.detections[j].elev_ang_rad - pc_ref.detections[j].elev_ang_rad))
                if delta_r_m > 0.01:
                    print(
                        "  frameId:",
                        pc_new.frameId,
                        "delta r_m:",
                        delta_r_m,
                        "delta az:",
                        delta_az,
                        "delta el:",
                        delta_el,
                    )
                rm_deltas.append(delta_r_m)
                az_deltas.append(delta_az)
                el_deltas.append(delta_el)

        num_pcs = i + 1
        distance_metric, trafo_metric, corr_metric = calculate_metrics_for_npy_points(npc_new, npc_ref)
        # add to sum
        sum_distance_metric += distance_metric
        # sum_normal_metric += normal_metric
        sum_trafo_metric += trafo_metric
        sum_corr_metric += corr_metric
    result = 1000.0

    # print("average deltas:")
    # print("  r_m: ", np.mean(rm_deltas))
    # print("  az: ", np.mean(az_deltas))
    # print("  el: ", np.mean(el_deltas))

    # print("biggest deltas:")
    # for i in range(10):
    #     print("  r_m: ", np.max(rm_deltas), " az: ", np.max(az_deltas), " el: ", np.max(el_deltas))
    #     rm_deltas.remove(np.max(rm_deltas))
    #     az_deltas.remove(np.max(az_deltas))
    #     el_deltas.remove(np.max(el_deltas))

    if num_pcs > 0:
        # build mean by dividing through num_pcs
        sum_distance_metric /= num_pcs
        # sum_normal_metric /= num_pcs
        sum_trafo_metric /= num_pcs
        sum_corr_metric /= num_pcs
        # build combined value of metrics
        result = (sum_distance_metric + sum_trafo_metric + sum_corr_metric) / 3.0
    return result  # noqa: R504


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python RadarFitnessFunction.py <bin_file> <ref_file>")
        sys.exit(1)

    bin_file = sys.argv[1]
    ref_file = sys.argv[2]
    result = compare_radar_bin_files(bin_file, ref_file)
    print(result)
    sys.exit(0)
