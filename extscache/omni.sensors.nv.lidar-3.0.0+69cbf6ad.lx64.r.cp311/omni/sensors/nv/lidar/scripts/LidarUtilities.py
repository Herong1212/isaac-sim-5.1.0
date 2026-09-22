# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from enum import Enum

import generic_model_output as gmo_utils
import numpy as np
import omni.sensors.nv.common._common as common  # noqa: N813, E402
import omni.sensors.nv.lidar._lidar as lidar


class BinFileType(Enum):
    DWBIN = 0
    PCAP = 1
    DWPOD = 2


class PCGeneratorConfig:
    def __init__(self, file_name, profile_name="", group_name="Lidar", client_name="lidar_instance"):
        self.cfg = lidar.LidarPCConverterCfg()
        self.cfg.fileName = file_name
        self.cfg.runMode = lidar.LidarPCConverterRunMode.CPU
        self.cfg.syncMode = True
        self.cfg.desiredCoordsType = gmo_utils.CoordsType.CARTESIAN
        self.cfg.outputOnGPU = False
        self.cfg.groupName = group_name
        self.cfg.clientName = client_name
        self.cfg.profileName = profile_name
        self.cfg.maxPoints = 1000000
        self.pos = [0.0, 0.0, 0.0]
        self.roll_pitch_yaw = [0.0, 0.0, 0.0]  # in degrees
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.tell = 0
        self.bin_file_type = BinFileType.DWBIN
        self.frameOfReference = gmo_utils.FrameOfReference.SENSOR
        self.motionCompensationState = gmo_utils.MotionCompensationState.NONCOMPENSATED
        self.interpolation_factor = 1.0


def get_profile(profilfilename):
    profile = None
    dwId = None
    with open(profilfilename, "r") as file:
        data = file.read()
        profilefactory = common.acquire_profile_reader_interface()
        reader = profilefactory.createInstance()
        reader.init(data, common.ProfileType.LIDAR)
        data_size = reader.dataSizeProfile()
        byte_array = bytearray(data_size)
        reader.update(byte_array)
        profile = lidar.getLidarProfileFromBuffer(byte_array)
        ### REMOVE
        dwId = profile.dwId
    return profile, dwId


def get_vanilla_pc_converter():
    factory = lidar.acquire_pcconverter_interface()
    return factory.createInstance()


def get_pc_converter(cfg):
    converter = get_vanilla_pc_converter()
    if cfg.cfg.mode != lidar.LidarPCConverterMode.GENERIC_FILE and cfg.cfg.profileName == "":
        print(
            "Missing profile. Did you forget to set the profile path in the cfg? A sensor profile is needed for non-hdf5 file reading."  # noqa: E501
        )
    converter.init(cfg.cfg)
    return converter


def get_beam_angles_of_bin_file_header(file_path):
    with open(file_path, "rb") as f:
        size_header = lidar.getSizeOfLidarBinFileHeader()
        bin_file_header = f.read(size_header)
        return lidar.getChannelsOfBinFileHeader(bin_file_header)


def generate_pc_from_pod(converter, cfg, cb=None):
    pod_cfg = common.DWPodIOConfig()
    pod_cfg.accessType = common.DWPodAccessType.READ
    pod_cfg.fileName = cfg.cfg.fileName
    factory = common.acquire_dwpod_io_interface()
    dwpod_io = factory.createInstance()

    dwpod_io.init(pod_cfg)
    while True:
        timed_packet = dwpod_io.readNextPacket()
        if timed_packet.timestampNs == -1:
            break
        if timed_packet.timestampNs >= cfg.start_timestamp:
            if cb is not None:
                cb(converter, timed_packet.timestampNs, False)
            int_pod_cfg = dwpod_io.getCfg()
            track_header_data = int_pod_cfg.trackHeaderDataBuffer
            converter.convertPacket(
                timed_packet.dataBuffer.tobytes(),
                track_header_data.dataBuffer.tobytes(),
                track_header_data.getDataSize(),
            )
            opc = converter.getPointCloud()
            # print("PointC {0}".format(timed_packet.timestampNs))
            if opc is not None and opc.numElements > 0:
                yield opc
    print("Converted all packets of file.\n")
    dwpod_io = None


# cb updates the transformation of the converter.
# Either its setting it for the packet timestamp or for the whole new scan (if is_new_scan is True)
# It has to have the following signature:
#   cb(converter,packet_timestamp,is_new_scan)
def generate_pc_from_packets_bin(converter, cfg, cb=None):
    size_packet_header = lidar.getSizeOfBinPacketHeader()
    with open(cfg.cfg.fileName, "rb") as f:
        # init
        size_header = lidar.getSizeOfLidarBinFileHeader()
        bin_file_header = f.read(size_header)
        # old_num = 0
        idxx = 0
        tell = cfg.tell
        if tell != 0:
            f.seek(tell)
        timestamp = 0
        while timestamp <= cfg.end_timestamp or cfg.end_timestamp == 0:
            packet_header = f.read(size_packet_header)
            if len(packet_header) < size_packet_header:
                print("packet_header size: {0}".format(len(packet_header)))
                break
            size_packet = int(np.frombuffer((packet_header[0:4]), np.uint32))
            timestamp = np.frombuffer((packet_header[4:12]), np.uint64)

            buffer = f.read(size_packet)
            if timestamp >= cfg.start_timestamp:
                if tell == 0:
                    tell = f.tell()
                    print("file tell: {0}".format(tell))
                if len(buffer) < size_packet:
                    print("size buffer: {0}".format(len(buffer)))
                    break

                is_new_scan = converter.isPacketOfNewScan(bytes(buffer))
                if cb is not None:
                    cb(converter, timestamp, is_new_scan)
                # if is_new_scan or first_spin:
                #     opc = converter.getPointCloud()
                #     if opc.numElements > 0:
                #         first_spin = False
                #         yield opc
                #     if cb is not None:
                #         cb(converter, timestamp, is_new_scan)
                converter.convertPacket(bytes(buffer), bytes(bin_file_header))
                opc = converter.getPointCloud()
                if opc is not None and opc.numElements > 0:
                    yield opc
            elif idxx % 3600 == 0:
                print("current time: {0} min time: {1}".format(timestamp, cfg.start_timestamp))
            idxx += 1
        print("Converted all packets of file.\n")


def generate_pc_from_pcap(converter, cfg):
    import dpkt

    size_packet = converter.sizeOfVendorPacket(cfg.profile.dwId)
    tell = 0
    idxx = 0
    first_timestamp = 0
    with open(cfg.cfg.fileName, "rb") as f:
        pcap = dpkt.pcap.Reader(f)
        for _, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            buffer = eth.data.data.data
            idxx += 1
            if len(buffer) == size_packet:
                packet_time = converter.getPacketTime(buffer)

                if packet_time >= first_timestamp:
                    if tell == 0:
                        # print("current time: {0} min time: {1}".format(datatimestamp,cfg.start_timestamp))
                        print("min: {0} current: {1}, idxx {2}".format(first_timestamp, packet_time, idxx))
                        tell = f.tell()
                        print("file tell: {0}".format(tell))
                    if converter.isPacketOfNewScan(bytes(buffer)):
                        opc = converter.getPointCloud()
                        if opc.numElements > 0:
                            yield opc
                    converter.convertPcapPacket(bytes(buffer))
        print("Converted all packets of file.\n")


def generate_pc_from_h5(converter, _):
    pc_in_frame = True
    while pc_in_frame:
        pc_in_frame = converter.convertBuffer()
        pc = converter.getPointCloud()
        if pc_in_frame and pc is not None and pc.numElements > 0:
            yield pc


def generate_pc_from_file(cfg, cb=None):
    converter = get_pc_converter(cfg)
    if cfg.pos is not None and cfg.roll_pitch_yaw is not None:
        converter.setStaticTransformation(cfg.pos, cfg.roll_pitch_yaw)
    if cfg.frameOfReference is not gmo_utils.FrameOfReference.CUSTOM:
        converter.setTransformation(cfg.frameOfReference, cfg.motionCompensationState, cfg.interpolation_factor)
    if cfg.cfg.mode == lidar.LidarPCConverterMode.GENERIC_FILE:
        return generate_pc_from_h5(converter, cfg)
    elif cfg.cfg.mode == lidar.LidarPCConverterMode.PACKETS:
        if cfg.bin_file_type == BinFileType.PCAP:
            return generate_pc_from_pcap(converter, cfg)
        elif cfg.bin_file_type == BinFileType.DWBIN:
            return generate_pc_from_packets_bin(converter, cfg, cb)
        elif cfg.bin_file_type == BinFileType.DWPOD:
            return generate_pc_from_pod(converter, cfg, cb)
        else:
            print("Unknown bin file type.")
