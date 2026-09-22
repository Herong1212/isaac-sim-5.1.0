import argparse

import matplotlib.pyplot as plt
import numpy as np
import parse as parse

NUM_SAMPLES = 320
CYCLE_SIGNALWAYS = 16
CYCLE_SIZE = 9065


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="Generic binfile to parse")

    parser.add_argument("--out", type=str, required=True, help="Path to place generated waveforms")
    args = parser.parse_args()

    parse.init()
    signalways = parse.parse_dump_file(args.file)

    for key in signalways.keys():
        plt.figure()
        ax = plt.gca()
        ax.set_ylim([0, 1.0])
        sgw = np.array(signalways[key])
        plt.plot(np.sum(sgw, axis=0) / sgw.shape[0] / 255)
        tokens = key.split("-")
        plt.title("TX: " + tokens[0] + " RX: " + tokens[1] + " channel: " + tokens[2])
        plt.savefig(args.out + "sgw_" + tokens[0] + "_" + tokens[1] + "_" + tokens[2] + ".png")
        plt.close()
