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

"""OmniGraph node for image pixallating augmentation"""


# ======================================================================


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.kernel
def resize_down(
    rgb_data_in: wp.array3d(dtype=wp.uint8),
    rgb_data_out: wp.array3d(dtype=wp.uint8),
):

    # thread index
    i, j = wp.tid()

    in_height = rgb_data_in.shape[0]
    in_width = rgb_data_in.shape[1]

    out_height = rgb_data_out.shape[0]
    out_width = rgb_data_out.shape[1]

    # start and end indices
    i_start = int(float(i) * float(in_height) / float(out_height))
    i_end = int(float(i + 1) * float(in_height) / float(out_height))

    j_start = int(float(j) * float(in_width) / float(out_width))
    j_end = int(float(j + 1) * float(in_width) / float(out_width))

    sum_r = int(0)
    sum_g = int(0)
    sum_b = int(0)
    sum_a = int(0)

    count = int(0)

    for i_idx in range(i_start, i_end):
        for j_idx in range(j_start, j_end):

            sum_r = sum_r + int(rgb_data_in[i_idx, j_idx, 0])
            sum_g = sum_g + int(rgb_data_in[i_idx, j_idx, 1])
            sum_b = sum_b + int(rgb_data_in[i_idx, j_idx, 2])
            sum_a = sum_a + int(rgb_data_in[i_idx, j_idx, 3])

            count = count + 1

    rgb_data_out[i, j, 0] = wp.uint8(sum_r / count)
    rgb_data_out[i, j, 1] = wp.uint8(sum_g / count)
    rgb_data_out[i, j, 2] = wp.uint8(sum_b / count)
    rgb_data_out[i, j, 3] = wp.uint8(sum_a / count)


@wp.kernel
def resize_up(
    rgb_data_in: wp.array3d(dtype=wp.uint8),
    rgb_data_out: wp.array3d(dtype=wp.uint8),
):

    # thread index
    i, j = wp.tid()
    in_height = rgb_data_in.shape[0]
    in_width = rgb_data_in.shape[1]

    out_height = rgb_data_out.shape[0]
    out_width = rgb_data_out.shape[1]

    # start and end indices
    i_down = int(float(i) * float(in_height) / float(out_height))
    j_down = int(float(j) * float(in_width) / float(out_width))

    rgb_data_out[i, j, 0] = rgb_data_in[i_down, j_down, 0]
    rgb_data_out[i, j, 1] = rgb_data_in[i_down, j_down, 1]
    rgb_data_out[i, j, 2] = rgb_data_in[i_down, j_down, 2]
    rgb_data_out[i, j, 3] = rgb_data_in[i_down, j_down, 3]


class OgnAugPixellateExpInternalState:
    def __init__(self):
        self.downsized_buffer = None
        self.shape = (0, 0)
        self.output_array = None

    def get_downsized_buffer(self, shape, device):
        if shape != self.shape:
            self.downsized_buffer = wp.zeros(shape=(*shape, 4), dtype=wp.uint8, device=device)
            self.shape = shape
        return self.downsized_buffer


class OgnAugPixellateExp:
    @staticmethod
    def internal_state():
        return OgnAugPixellateExpInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

        state = db.shared_state
        orig_shape = (db.inputs.height, db.inputs.width, 4)
        width = db.inputs.width
        height = db.inputs.height
        array_format = db.inputs.format
        if array_format:
            channels = rep.annotators.annotator_utils._format_to_elem_count(array_format)
            orig_shape = (height, width, channels)
        else:
            orig_shape = (height, width, 4)
        dtype = wp.uint8
        kernel_size = int(db.inputs.kernelSize)
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

        device = rgb_data_gpu.device
        with wp.ScopedDevice(device):
            out_width = width // kernel_size
            out_height = height // kernel_size
            rgb_data_downsample = state.get_downsized_buffer((out_height, out_width), device)

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
                kernel=resize_down,
                dim=(out_height, out_width),
                inputs=[rgb_data_gpu, rgb_data_downsample],
                device=device,
            )

            wp.launch(
                kernel=resize_up,
                dim=(height, width),
                inputs=[rgb_data_downsample, state.output_array],
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
