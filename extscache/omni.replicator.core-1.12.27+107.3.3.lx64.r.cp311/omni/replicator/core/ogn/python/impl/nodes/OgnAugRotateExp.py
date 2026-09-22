# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes
import math

import numpy as np
import omni.replicator.core as rep
import warp as wp

"""OmniGraph node for rotating images"""


# ======================================================================


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.func
def lookup_float(f: wp.array3d(dtype=wp.uint8), axis: wp.int32, dim: wp.vec2, x: int, y: int):

    if x < 0 or x >= int(dim[0]):
        return float(0)
    if y < 0 or y >= int(dim[1]):
        return float(0)

    x = wp.clamp(x, 0, int(dim[0]) - 1)
    y = wp.clamp(y, 0, int(dim[1]) - 1)

    return float(f[x, y, axis])


@wp.func
def sample_float(f: wp.array3d(dtype=wp.uint8), axis: wp.int32, x: float, y: float):
    lx = int(wp.floor(x))
    ly = int(wp.floor(y))

    tx = x - float(lx)
    ty = y - float(ly)

    dim = wp.vec2(wp.float32(f.shape[0]), wp.float32(f.shape[1]))

    s0 = wp.lerp(lookup_float(f, axis, dim, lx, ly), lookup_float(f, axis, dim, lx + 1, ly), tx)

    s1 = wp.lerp(lookup_float(f, axis, dim, lx, ly + 1), lookup_float(f, axis, dim, lx + 1, ly + 1), tx)
    s = wp.lerp(s0, s1, ty)
    return wp.uint8(s)


@wp.kernel
def rotate(rotate: float, wp_orig: wp.array3d(dtype=wp.uint8), wp_new: wp.array3d(dtype=wp.uint8)):
    i, j = wp.tid()

    dim = wp.vec2(wp.float32(wp_orig.shape[0]), wp.float32(wp_orig.shape[1]))
    # trace backward
    rotate = float(rotate)
    cx = dim[0] / 2.0
    cy = dim[1] / 2.0
    p = wp.vec2(
        (float(i) - cx) * np.cos(rotate) + (float(j) - cy) * np.sin(rotate) + cx,
        -(float(i) - cx) * np.sin(rotate) + (float(j) - cy) * np.cos(rotate) + cy,
    )

    wp_new[i, j, 0] = sample_float(wp_orig, 0, p[0], p[1])
    wp_new[i, j, 1] = sample_float(wp_orig, 1, p[0], p[1])
    wp_new[i, j, 2] = sample_float(wp_orig, 2, p[0], p[1])
    wp_new[i, j, 3] = sample_float(wp_orig, 3, p[0], p[1])


class OgnAugRotateExpInternalState:
    def __init__(self):
        self.output_array = None


class OgnAugRotateExp:
    @staticmethod
    def internal_state():
        return OgnAugRotateExpInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

        state = db.shared_state
        rotation = math.radians(db.inputs.rotation)
        width = db.inputs.width
        height = db.inputs.height
        array_format = db.inputs.format
        if array_format:
            channels = rep.annotators.annotator_utils._format_to_elem_count(array_format)
            orig_shape = (height, width, channels)
        else:
            orig_shape = (height, width, 4)
        dtype = wp.uint8
        device_idx = db.inputs.cudaDeviceIndex
        data_ptr = db.inputs.dataPtr
        if device_idx < 0:
            device = "cpu"
        else:
            device = f"cuda:{device_idx}"

        strides_raw = db.inputs.strides
        strides = (strides_raw[1], strides_raw[0], wp.types.type_size_in_bytes(dtype))

        if not data_ptr:
            data_ptr = get_address(db.inputs.data)
            strides = None

        rgb_data_gpu = wp.types.array(
            dtype=dtype,
            shape=orig_shape,  # number of elements
            ptr=data_ptr,
            device=device,
            strides=strides,
            requires_grad=False,
        )

        with wp.ScopedDevice(device):
            if (
                state.output_array is None
                or tuple(orig_shape) != state.output_array.shape
                or dtype != state.output_array.dtype
            ):
                state.output_array = wp.empty(
                    dtype=dtype,
                    shape=tuple(orig_shape),
                    device=device,
                    requires_grad=False,
                )
            elif device != state.output_array.device:
                state.output_array = state.output_array.to(device)

            wp.launch(
                rotate,
                dim=(height, width),
                inputs=[rotation, rgb_data_gpu, state.output_array],
            )

            xform_curr = np.eye(3)
            xform_curr[0, 0] = np.cos(rotation)
            xform_curr[0, 1] = -np.sin(rotation)
            xform_curr[0, 2] = (
                np.sin(rotation) * (db.inputs.width - 1) / 2.0 + (1.0 - np.cos(rotation)) * (db.inputs.height - 1) / 2.0
            )
            xform_curr[1, 0] = np.sin(rotation)
            xform_curr[1, 1] = np.cos(rotation)
            xform_curr[1, 2] = (1.0 - np.cos(rotation)) * (db.inputs.width - 1) / 2.0 - np.sin(rotation) * (
                db.inputs.height - 1
            ) / 2.0
            xform_curr = np.transpose(xform_curr)

            db.outputs.exec = 1
            db.outputs.xform = np.matmul(db.inputs.xform.reshape(3, 3), xform_curr)
            db.outputs.bufferSize = db.inputs.bufferSize
            db.outputs.height = db.inputs.height
            db.outputs.width = db.inputs.width
            db.outputs.format = array_format
            db.outputs.cudaDeviceIndex = device_idx
            db.outputs.dataPtr = state.output_array.ptr
            db.outputs.strides = state.output_array.strides[1], state.output_array.strides[0]
            return True
