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
import os
from functools import reduce

import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import warp as wp
from omni.replicator.core.utils import rng

"""OmniGraph node for 2D convolution"""


# ======================================================================


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.kernel
def conv2d(
    rgb_data_in: wp.array3d(dtype=wp.uint8),
    rgb_data_out: wp.array3d(dtype=wp.uint8),
    kernel: wp.array2d(dtype=float),
    alpha: float,
):

    height = rgb_data_in.shape[0]
    width = rgb_data_in.shape[1]
    kernel_hf_size = kernel.shape[0] / 2

    # thread index
    i, j = wp.tid()

    sum_r = float(0)
    sum_g = float(0)
    sum_b = float(0)

    for ki in range(-kernel_hf_size, kernel_hf_size + 1):
        for kj in range(-kernel_hf_size, kernel_hf_size + 1):

            i_idx = wp.clamp(i + ki, 0, height - 1)
            j_idx = wp.clamp(j + kj, 0, width - 1)

            ki_idx = ki + kernel_hf_size
            kj_idx = kj + kernel_hf_size

            sum_r = sum_r + float(rgb_data_in[i_idx, j_idx, 0]) * kernel[ki_idx, kj_idx]
            sum_g = sum_g + float(rgb_data_in[i_idx, j_idx, 1]) * kernel[ki_idx, kj_idx]
            sum_b = sum_b + float(rgb_data_in[i_idx, j_idx, 2]) * kernel[ki_idx, kj_idx]

    rgb_data_out[i, j, 0] = wp.uint8(
        alpha * wp.clamp(sum_r, 0.0, 255.0) + (1.0 - alpha) * wp.float(rgb_data_in[i, j, 0])
    )
    rgb_data_out[i, j, 1] = wp.uint8(
        alpha * wp.clamp(sum_g, 0.0, 255.0) + (1.0 - alpha) * wp.float(rgb_data_in[i, j, 1])
    )
    rgb_data_out[i, j, 2] = wp.uint8(
        alpha * wp.clamp(sum_b, 0.0, 255.0) + (1.0 - alpha) * wp.float(rgb_data_in[i, j, 2])
    )
    rgb_data_out[i, j, 3] = rgb_data_in[i, j, 3]


class OgnAugConv2dExpInternalState:
    def __init__(self):
        np.random.seed(rng.get_global_seed())
        self.output_array = None


class OgnAugConv2dExp:
    @staticmethod
    def internal_state():
        return OgnAugConv2dExpInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

        state = db.shared_state
        alpha = db.inputs.alpha
        kernel = db.inputs.kernel
        kernel_size = math.sqrt(len(kernel))
        if not kernel_size.is_integer():
            db.log_error(f"Kernel {kernel} of length {len(kernel)} has invalid size {kernel_size}")
        kernel_size = int(kernel_size)
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
            conv_kernel_wp = wp.array2d(kernel.reshape(kernel_size, kernel_size), dtype=float)

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
                kernel=conv2d,
                dim=(height, width),
                inputs=[
                    rgb_data_gpu,
                    state.output_array,
                    conv_kernel_wp,
                    alpha,
                ],
                device=device,
            )

            db.outputs.exec = 1
            db.outputs.xform = db.inputs.xform
            db.outputs.bufferSize = db.inputs.bufferSize
            db.outputs.height = db.inputs.height
            db.outputs.width = db.inputs.width
            db.outputs.format = array_format
            db.outputs.cudaDeviceIndex = device_idx
            db.outputs.dataPtr = state.output_array.ptr
            db.outputs.strides = state.output_array.strides[1], state.output_array.strides[0]

            return True
