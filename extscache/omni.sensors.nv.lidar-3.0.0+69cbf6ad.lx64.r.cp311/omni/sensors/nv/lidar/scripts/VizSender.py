# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import struct
from enum import Enum

import carb
import generic_model_output as gmo_bindings  # noqa: N813, E402
import numpy as np
from omni.sensors.net import *

# imports not needed for every use case
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp


def to_cartesian(gmo):
    x = gmo.z * np.cos(np.deg2rad(gmo.x)) * np.cos(np.deg2rad(gmo.y))
    y = gmo.z * np.sin(np.deg2rad(gmo.x)) * np.cos(np.deg2rad(gmo.y))
    z = gmo.z * np.sin(np.deg2rad(gmo.y))
    return x, y, z


def lerp(a, b, t):
    return (1 - t) * a + t * b


def motion_compensate(gmo):
    x, y, z = to_cartesian(gmo)
    timed_points = np.asarray([x, y, z, gmo.timeOffSetNs + gmo.timestampNs]).T
    rot_start_end = R.from_quat(
        np.asarray(
            [
                [
                    gmo.frameStart.orientation[0],
                    gmo.frameStart.orientation[1],
                    gmo.frameStart.orientation[2],
                    gmo.frameStart.orientation[3],
                ],
                [
                    gmo.frameEnd.orientation[0],
                    gmo.frameEnd.orientation[1],
                    gmo.frameEnd.orientation[2],
                    gmo.frameEnd.orientation[3],
                ],
            ]
        )
    )
    rot_end = R.from_quat(
        [
            gmo.frameEnd.orientation[0],
            gmo.frameEnd.orientation[1],
            gmo.frameEnd.orientation[2],
            gmo.frameEnd.orientation[3],
        ]
    )
    pos_start = np.asarray([gmo.frameStart.posM[0], gmo.frameStart.posM[1], gmo.frameStart.posM[2]])
    pos_end = np.asarray([gmo.frameEnd.posM[0], gmo.frameEnd.posM[1], gmo.frameEnd.posM[2]])
    slerp = Slerp([gmo.frameStart.timestampNs, gmo.frameEnd.timestampNs], rot_start_end)
    rots = slerp(timed_points[:, 3])
    # poses = lerp(pos_start,pos_end,timed_points[:,3])
    # motion compensate points with interpolated rots and poses
    compensated_points = np.asarray(
        [
            rots[i].apply(point[:3])
            + lerp(
                pos_start,
                pos_end,
                (point[3] - gmo.timestampNs) / (gmo.frameEnd.timestampNs - gmo.frameStart.timestampNs),
            )
            for i, point in enumerate(timed_points)
        ]
    )
    # trafo back to sensor in tend
    # compensated_points = rot_end.inv().apply((compensated_points - pos_end))
    return compensated_points


class BBox:
    def __init__(self, corners, value):
        self.corners = corners
        self.value = value


class VizSenderColorAttr(Enum):
    CONSTANT = 0
    INTENSITY = 1
    HEIGHT = 2
    RANGE = 3
    ECHO = 4
    MATERIAL = 5
    OBJECT = 6


class VizSender:
    def __init__(self, channel_spec, data_id):
        factory = INetworkFactory()
        self.channel = factory.make_channel(channel_spec)
        self.data_id = data_id
        self.color_attr = VizSenderColorAttr.INTENSITY
        self.color_map_types = {
            VizSenderColorAttr.CONSTANT: 0,
            VizSenderColorAttr.INTENSITY: 0,
            VizSenderColorAttr.HEIGHT: 0,
            VizSenderColorAttr.RANGE: 0,
            VizSenderColorAttr.ECHO: 1,
            VizSenderColorAttr.MATERIAL: 1,
            VizSenderColorAttr.OBJECT: 1,
        }

    def set_color_attribute(self, color_attr):
        self.color_attr = color_attr

    def convert_and_send_bbox(self, bboxes, timestamp, max_bboxes=1000):
        out = [np.float32(x) for box in bboxes for x in list(box.corners.flatten()) + [box.value]]
        buf = bytes()
        buf += struct.pack("I", np.uint32(len(bboxes)))
        buf += struct.pack("B", 2)
        buf += struct.pack("B", 1)
        buf += struct.pack("B", self.data_id)
        buf += struct.pack("f", np.float32(100))
        buf += struct.pack("I", np.uint32(max_bboxes))
        buf += struct.pack("Q", np.uint64(timestamp))
        # buf += struct.pack('Q',np.uint64(pc.getPoint(pc.numElements-1).timeStampNs))
        buf += struct.pack(str(len(out)) + "f", *out)
        self.channel.send(buf)

    def convert_and_send_pc(self, pc, max_points=500000, motion_compensated=False):
        def get_color_attr(pc):
            # return pc.scalar.astype(np.float32)
            # res = 1.0
            if self.color_attr is VizSenderColorAttr.CONSTANT:
                return np.constant((pc.numElements, 1), 1, dtype=np.float32)
            elif self.color_attr is VizSenderColorAttr.INTENSITY:
                return pc.scalar.astype(np.float32)
            elif self.color_attr is VizSenderColorAttr.HEIGHT:
                return pc.z.astype(np.float32)
            elif self.color_attr is VizSenderColorAttr.RANGE:
                return [np.float32(np.hypot(pc.x[i], pc.y[i], pc.z[i])) for i in range(0, pc.numElements)]
            elif self.color_attr is VizSenderColorAttr.ECHO:
                return pc.echoId.astype(np.float32)
            elif self.color_attr is VizSenderColorAttr.MATERIAL:
                return pc.matId.astype(np.float32)
            elif self.color_attr is VizSenderColorAttr.OBJECT:
                return np.sum(np.asarray(pc.objId).reshape(-1, 16).astype(np.float32), axis=1)
                # return np.asarray([np.sum( pc.objId[j*16:(j+1)*16]) for j in range(0,pc.numElements)]).astype(np.float32)

        def get_color_map_id():
            return self.color_map_types[self.color_attr]

        if pc.numElements > 0:
            out = np.empty((pc.numElements * 4,), dtype=np.float32)
            if motion_compensated:
                points = motion_compensate(pc)
                out[0::4] = points[:, 0]
                out[1::4] = points[:, 1]
                out[2::4] = points[:, 2]
            elif pc.elementsCoordsType == gmo_bindings.CoordsType.CARTESIAN:
                out[0::4] = pc.x
                out[1::4] = pc.y
                out[2::4] = pc.z
            else:
                out[0::4] = pc.z * np.cos(np.deg2rad(pc.x)) * np.cos(np.deg2rad(pc.y))
                out[1::4] = pc.z * np.sin(np.deg2rad(pc.x)) * np.cos(np.deg2rad(pc.y))
                out[2::4] = pc.z * np.sin(np.deg2rad(pc.y))
            out[3::4] = get_color_attr(pc)

            # temp = np.asarray(out).reshape(-1, 4)
            # temp[:, 3] = np.asarray(pc.timeOffSetNs).astype(np.float32)
            # np.savetxt("pc"+str(pc.timestampNs)+".txt", temp, delimiter=',')

            buf = bytes()
            buf += struct.pack("I", np.uint32(len(out) / 4))
            buf += struct.pack("B", 0)
            buf += struct.pack("B", get_color_map_id())
            buf += struct.pack("B", self.data_id)
            buf += struct.pack("f", np.float32(1.0))
            buf += struct.pack("I", np.uint32(max_points))
            buf += struct.pack("Q", np.uint64(pc.timestampNs))
            # buf += struct.pack('Q',np.uint64(pc.getPoint(pc.numElements-1).timeStampNs))
            buf += struct.pack(str(len(out)) + "f", *out)
            self.channel.send(buf)

    def send_viz_points(self, pc, max_points=500000):
        def get_color_map_id():
            return self.color_map_types[self.color_attr]

        if pc.numElements > 0:
            out = [
                x
                for p in pc
                if p.value >= 0.0
                for x in (np.float32(p.pos.x), np.float32(p.pos.y), np.float32(p.pos.z), p.value)
            ]
            buf = bytes()
            buf += struct.pack("I", np.uint32(len(out) / 4))
            buf += struct.pack("B", 0)
            buf += struct.pack("B", get_color_map_id())
            buf += struct.pack("B", self.data_id)
            buf += struct.pack("f", np.float32(1.0))
            buf += struct.pack("I", np.uint32(max_points))
            buf += struct.pack("Q", np.uint64(0))
            # buf += struct.pack('Q',np.uint64(pc.getPoint(pc.numElements-1).timeStampNs))
            buf += struct.pack(str(len(out)) + "f", *out)
            self.channel.send(buf)

    def send_numpy_points(self, pc1, pc2):
        def get_color_map_id():
            return self.color_map_types[self.color_attr]

        out1 = [x for row in pc1 for x in (np.float32(row[0]), np.float32(row[1]), np.float32(row[2]), 0.0)]
        print(len(out1))
        out2 = [x for row in pc2 for x in (np.float32(row[0]), np.float32(row[1]), np.float32(row[2]), 1.0)]

        out = out1 + out2
        print(len(out))

        buf = bytes()
        buf += struct.pack("I", np.uint32(len(out) / 4))
        buf += struct.pack("B", 0)
        buf += struct.pack("B", get_color_map_id())
        buf += struct.pack("B", self.data_id)
        buf += struct.pack("f", np.float32(1.0))
        buf += struct.pack("I", np.uint32(1000000))
        buf += struct.pack("Q", np.uint64(0))
        # buf += struct.pack('Q',np.uint64(pc.getPoint(pc.numElements-1).timeStampNs))
        buf += struct.pack(str(len(out)) + "f", *out)
        self.channel.send(buf)
