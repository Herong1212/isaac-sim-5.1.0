import argparse
import struct

import matplotlib.pyplot as plt
import numpy as np
from omni.sensors.nv.radar.scripts.radar_detection import MAX_NUM_DETS, RadarDetection, RadarPointCloud  # noqa: E402


# Generator function for easy access of raw point clouds (used in fidelity test).
def get_radar_pc_gen(bin_file_path, append_empty_dets=True):
    with open(bin_file_path, "rb") as dump_file:
        file_size = dump_file.seek(0, 2)
        offset = dump_file.seek(0)
        size_scan = 64 + MAX_NUM_DETS * 32
        while (offset + size_scan) < file_size:  # 64 + NUM_DETS*32
            scan = RadarPointCloud()
            scan.sync_data = struct.unpack("L", dump_file.read(8))[0]
            scan.tasking_counter = struct.unpack("L", dump_file.read(8))[0]
            scan.sensor_id = struct.unpack("B", dump_file.read(1))[0]
            scan.scan_idx = struct.unpack("B", dump_file.read(1))[0]
            scan.timestamp_ns = struct.unpack("L", dump_file.read(8))[0]
            scan.cycle_cnt = struct.unpack("L", dump_file.read(8))[0]
            scan.max_range_m = struct.unpack("f", dump_file.read(4))[0]
            scan.min_vel_mps = struct.unpack("f", dump_file.read(4))[0]
            scan.max_vel_mps = struct.unpack("f", dump_file.read(4))[0]
            scan.min_az_rad = struct.unpack("f", dump_file.read(4))[0]
            scan.max_az_rad = struct.unpack("f", dump_file.read(4))[0]
            scan.min_el_rad = struct.unpack("f", dump_file.read(4))[0]
            scan.max_el_rad = struct.unpack("f", dump_file.read(4))[0]
            scan.num_detections = struct.unpack("H", dump_file.read(2))[0]
            scan.detections = []
            for i in range(0, MAX_NUM_DETS):
                detection = RadarDetection()
                detection.r_m = struct.unpack("f", dump_file.read(4))[0]
                detection.rv_ms = struct.unpack("f", dump_file.read(4))[0]
                detection.az_ang_rad = struct.unpack("f", dump_file.read(4))[0]
                detection.elev_ang_rad = struct.unpack("f", dump_file.read(4))[0]
                detection.rcs_dbsm = struct.unpack("f", dump_file.read(4))[0]
                detection.sem_id = struct.unpack("I", dump_file.read(4))[0]
                detection.mat_id = struct.unpack("I", dump_file.read(4))[0]
                detection.obj_id = struct.unpack("I", dump_file.read(4))[0]
                if i < scan.num_detections or append_empty_dets:
                    scan.detections.append(detection)
            yield scan
            offset = dump_file.tell()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="Generic binfile to parse")
    parser.add_argument("--out", type=str, required=True, help="Path to place generated point clouds")
    args = parser.parse_args()
    for i, scan in enumerate(get_radar_pc_gen(args.file)):
        plt.figure()
        ax = plt.gca()
        ax.set_xlim([-75, 75.0])
        ax.set_ylim([0, 100.0])
        x = [
            -detection.r_m * np.cos(detection.elev_ang_rad) * np.sin(detection.az_ang_rad)
            for detection in scan.detections
        ]
        x = x[: scan.num_detections]
        y = [
            detection.r_m * np.cos(detection.elev_ang_rad) * np.cos(detection.az_ang_rad)
            for detection in scan.detections
        ]
        y = y[: scan.num_detections]
        print("ts: " + str(scan.timestamp_ns), " num_dets: " + str(scan.num_detections))
        plt.scatter(x, y, s=1)
        plt.savefig(args.out + "scan" + str(i) + ".png")
        plt.close()
