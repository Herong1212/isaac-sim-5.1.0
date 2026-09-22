import numpy as np
import omni.sensors.nv.ultrasonic.scripts.parse as parse


def init(build_config="release", build_os="linux-x86_64"):
    parse.init(build_config, build_os)


def compare_bins(bin_file, ref_bin_file, sensor_name="uss_front"):
    signalways = parse.parse_dump_file(bin_file, sensor_name)
    ref_signalways = parse.parse_dump_file(ref_bin_file, sensor_name)

    error = 0.0

    for key in ref_signalways.keys():
        ref_sgw = np.array(ref_signalways[key])
        sgw = np.array(signalways[key])
        error = error + np.sqrt(
            np.sum(
                np.square(np.sum(ref_sgw, axis=0) / ref_sgw.shape[0] / 255 - np.sum(sgw, axis=0) / sgw.shape[0] / 255)
            )
            / ref_sgw.shape[1]
        )

    return error / len(ref_signalways.keys())
