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

import omni.replicator.core as rep
import warp as wp
from omni.replicator.core.utils import rng

"""OmniGraph node for altering contrast of image"""


# ======================================================================


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.kernel
def sum_kernel(rgb_in: wp.array3d(dtype=wp.uint8), sum: wp.array(dtype=float)):
    i, j = wp.tid()
    rgb_mean = (wp.float(rgb_in[i, j, 0]) + wp.float(rgb_in[i, j, 1]) + wp.float(rgb_in[i, j, 2])) / 3.0
    wp.atomic_add(sum, 0, rgb_mean)


@wp.kernel
def add_contrast(
    rgb_in: wp.array3d(dtype=wp.uint8), rgb_out: wp.array3d(dtype=wp.uint8), mean: float, contrast_factor: float
):

    i, j = wp.tid()

    r = wp.float(rgb_in[i, j, 0]) * (contrast_factor) + (1.0 - contrast_factor) * mean
    g = wp.float(rgb_in[i, j, 1]) * (contrast_factor) + (1.0 - contrast_factor) * mean
    b = wp.float(rgb_in[i, j, 2]) * (contrast_factor) + (1.0 - contrast_factor) * mean

    rgb_out[i, j, 0] = wp.uint8(wp.clamp(r, 0.0, 255.0))
    rgb_out[i, j, 1] = wp.uint8(wp.clamp(g, 0.0, 255.0))
    rgb_out[i, j, 2] = wp.uint8(wp.clamp(b, 0.0, 255.0))
    rgb_out[i, j, 3] = rgb_in[i, j, 3]


@wp.kernel
def to_greyscale(rgb_in: wp.array3d(dtype=wp.uint8), greyscale: wp.array3d(dtype=wp.uint8)):
    i, j = wp.tid()

    r = wp.float(rgb_in[i, j, 0])
    g = wp.float(rgb_in[i, j, 1])
    b = wp.float(rgb_in[i, j, 2])

    greyscale[i, j, 0] = wp.uint8(0.2989 * r + 0.587 * g + 0.114 * b)


class OgnAugContrastExpInternalState:
    def __init__(self):
        self.greyscale_buffer = None
        self.shape = (0, 0)
        self.output_array = None

    def get_greyscale_buffer(self, shape, device):
        if shape != self.shape:
            self.greyscale_buffer = wp.zeros(shape=(*shape, 1), dtype=wp.uint8, device=device)
            self.shape = shape
        return self.greyscale_buffer


class OgnAugContrastExp:
    @staticmethod
    def internal_state():
        return OgnAugContrastExpInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

        contrast_factor = db.inputs.contrastFactor

        state = db.shared_state
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
            greyscale = state.get_greyscale_buffer((height, width), device)

            wp.launch(kernel=to_greyscale, dim=(height, width), inputs=[rgb_data_gpu, greyscale], device=device)

            luminance_sum = wp.zeros(1, dtype=float)

            wp.launch(kernel=sum_kernel, dim=(height, width), inputs=[greyscale, luminance_sum], device=device)

            sum_np = luminance_sum.to("cpu").numpy()
            if height * width == 0:
                mean = sum_np[0] * 0
            else:
                mean = sum_np[0] / (height * width)

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
                kernel=add_contrast,
                dim=(height, width),
                inputs=[rgb_data_gpu, state.output_array, mean, contrast_factor],
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
