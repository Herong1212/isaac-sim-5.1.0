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

import numpy as np
import omni.replicator.core as rep
import warp as wp
from omni.replicator.core.utils import rng

"""OmniGraph node for crop and resize augmentation"""


# ======================================================================


def sample_crop(dim_orig, crop_factor, offset_factor):
    offset_factor_rel = offset_factor * (1 - crop_factor) / 2

    x_size = int(crop_factor * dim_orig[0])
    x_adj = int(offset_factor_rel[0] * dim_orig[0] + (dim_orig[0] - x_size) / 2)
    x1x2 = [x_adj, x_size + x_adj]

    y_size = int(crop_factor * dim_orig[1])
    y_adj = int(-offset_factor_rel[1] * dim_orig[1] + (dim_orig[1] - y_size) / 2)
    y1y2 = [y_adj, y_size + y_adj]

    cut_l = [x1x2[0], y1y2[0]]
    cut_h = [x1x2[1], y1y2[1]]

    return cut_l, cut_h


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.func
def lookup_float(f: wp.array3d(dtype=wp.uint8), axis: wp.int32, dim: wp.vec2, x: int, y: int):

    x = wp.clamp(x, 0, int(dim[0]) - 1)
    y = wp.clamp(y, 0, int(dim[1]) - 1)

    return float(f[x, y, axis])


@wp.func
def sample_float(f: wp.array3d(dtype=wp.uint8), axis: wp.int32, dim: wp.vec2, x: float, y: float):

    lx = int(wp.floor(x))
    ly = int(wp.floor(y))

    tx = x - float(lx)
    ty = y - float(ly)

    s0 = wp.lerp(lookup_float(f, axis, dim, lx, ly), lookup_float(f, axis, dim, lx + 1, ly), tx)

    s1 = wp.lerp(lookup_float(f, axis, dim, lx, ly + 1), lookup_float(f, axis, dim, lx + 1, ly + 1), tx)
    s = wp.lerp(s0, s1, ty)
    return wp.uint8(s)


@wp.kernel
def crop_resize(
    cut_l: wp.vec2,
    cut_h: wp.vec2,
    dim_orig: wp.vec2,
    wp_orig: wp.array3d(dtype=wp.uint8),
    wp_new: wp.array3d(dtype=wp.uint8),
):

    i, j = wp.tid()

    # trace backward
    p = wp.vec2(
        float(i) * (cut_h[0] - cut_l[0] - float(1)) / (dim_orig[0] - float(1)) + cut_l[0],
        float(j) * (cut_h[1] - cut_l[1] - float(1)) / (dim_orig[1] - float(1)) + cut_l[1],
    )

    wp_new[i, j, 0] = sample_float(wp_orig, 0, dim_orig, p[0], p[1])
    wp_new[i, j, 1] = sample_float(wp_orig, 1, dim_orig, p[0], p[1])
    wp_new[i, j, 2] = sample_float(wp_orig, 2, dim_orig, p[0], p[1])
    wp_new[i, j, 3] = sample_float(wp_orig, 3, dim_orig, p[0], p[1])


def getPerspectiveTransform(cut_l, cut_h, height, width):
    """
    Calculates the 3x3 matrix to transform the four source points to the four destination points
    """

    sourcePoints = np.array(
        [[cut_l[0], cut_l[1]], [cut_h[0], cut_l[1]], [cut_l[0], cut_h[1]], [cut_h[0], cut_h[1]]]
    ).astype(np.float32)
    destinationPoints = np.array([[0, 0], [height, 0], [0, width], [height, width]]).astype(np.float32)

    a = np.zeros((8, 8))
    b = np.zeros((8))
    for i in range(4):
        a[i][0] = a[i + 4][3] = sourcePoints[i][0]
        a[i][1] = a[i + 4][4] = sourcePoints[i][1]
        a[i][2] = a[i + 4][5] = 1
        a[i][3] = a[i][4] = a[i][5] = 0
        a[i + 4][0] = a[i + 4][1] = a[i + 4][2] = 0
        a[i][6] = -sourcePoints[i][0] * destinationPoints[i][0]
        a[i][7] = -sourcePoints[i][1] * destinationPoints[i][0]
        a[i + 4][6] = -sourcePoints[i][0] * destinationPoints[i][1]
        a[i + 4][7] = -sourcePoints[i][1] * destinationPoints[i][1]
        b[i] = destinationPoints[i][0]
        b[i + 4] = destinationPoints[i][1]

    x = np.linalg.solve(a, b)
    x.resize((9,), refcheck=False)
    x[8] = 1  # Set c22 to 1 as indicated in comment above
    return np.transpose(x.reshape((3, 3)))


class OgnAugCropResizeExpInternalState:
    def __init__(self):
        self.output_array = None


class OgnAugCropResizeExp:
    @staticmethod
    def internal_state():
        return OgnAugCropResizeExpInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

        state = db.shared_state
        crop_factor = db.inputs.cropFactor
        offset_factor = db.inputs.offsetFactor
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
        ).to(device)

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

            cut_l, cut_h = sample_crop(dim_orig=orig_shape[:2], crop_factor=crop_factor, offset_factor=offset_factor)
            # cut_l, cut_h = [300, 50], [600, 1150]  #should be in h, w

            xform_curr = getPerspectiveTransform(cut_l, cut_h, height, width)

            wp_cut_l = wp.vec2(float(cut_l[0]), float(cut_l[1]))
            wp_cut_h = wp.vec2(float(cut_h[0]), float(cut_h[1]))

            wp.launch(
                kernel=crop_resize,
                dim=(height, width),
                inputs=[wp_cut_l, wp_cut_h, orig_shape[:2], rgb_data_gpu, state.output_array],
                device=device,
            )

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
