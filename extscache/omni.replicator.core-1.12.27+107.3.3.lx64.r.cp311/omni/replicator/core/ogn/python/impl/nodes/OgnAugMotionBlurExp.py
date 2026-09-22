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

"""OmniGraph node for Motion Blur"""


# ======================================================================


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


def angle_to_rotation_matrix(angle):
    ang_rad = np.deg2rad(angle)
    cos_a = np.cos(ang_rad)
    sin_a = np.sin(ang_rad)

    rot_mat = np.zeros((2, 2))
    rot_mat[0, 0] = cos_a
    rot_mat[0, 1] = sin_a
    rot_mat[1, 0] = -sin_a
    rot_mat[1, 1] = cos_a

    return rot_mat


def get_rotation_matrix2d(center, angle, scale):
    rotation_matrix = angle_to_rotation_matrix(angle)
    scaling_matrix = np.zeros((2, 2))
    np.fill_diagonal(scaling_matrix, 1.0)

    scaling_matrix = scaling_matrix * scale

    scaled_rotation = rotation_matrix @ scaling_matrix

    alpha = scaled_rotation[0, 0]
    beta = scaled_rotation[0, 1]
    x = center[0]
    y = center[1]

    M = np.eye(3)

    M[0:2, 0:2] = scaled_rotation
    M[0, 2] = (1 - alpha) * x - beta * y
    M[1, 2] = beta * x + (1 - alpha) * y

    return M


def rotate(kernel, angle):
    center = [(kernel.shape[1] - 1) / 2, (kernel.shape[0] - 1) / 2]

    scale = 1.0
    rot_matrix = get_rotation_matrix2d(center, angle, scale)

    x = np.linspace(0, kernel.shape[1] - 1, kernel.shape[1])
    y = np.linspace(0, kernel.shape[0] - 1, kernel.shape[0])

    xx, yy = np.meshgrid(x, y)

    XY = np.array([xx.flatten(), yy.flatten()])
    XY = np.vstack([XY, np.ones((1, XY.shape[-1]))])

    Rot_XY = np.matmul(np.linalg.inv(rot_matrix), XY)

    out_kernel = np.zeros_like(kernel)

    for idx in range(0, Rot_XY.shape[-1]):

        rotx, roty = Rot_XY[0][idx], Rot_XY[1][idx]

        rotx = max(min(int(rotx + 0.5), kernel.shape[1] - 1), 0)
        roty = max(min(int(roty + 0.5), kernel.shape[0] - 1), 0)

        interp_val = kernel[int(roty)][int(rotx)]

        x_org = XY[0][idx]
        y_org = XY[1][idx]

        out_kernel[int(y_org)][int(x_org)] = interp_val

    return out_kernel


def get_motion_blur_kernel2d(kernel_size, angle, strength):

    kernel_tuple = (kernel_size, kernel_size)

    # direction from [-1, 1] to [0, 1] range
    strength = (np.clip(strength, -1.0, 1.0) + 1.0) / 2.0
    kernel = np.zeros((1, kernel_tuple[0], kernel_tuple[1]))

    # # Element-wise linspace
    kernel[:, kernel_tuple[0] // 2, :] = np.stack(
        [(strength + ((1 - 2 * strength) / (kernel_size - 1)) * i) for i in range(kernel_size)], axis=-1
    )

    # rotate (counterclockwise) kernel by given angle
    kernel = rotate(kernel[0], angle)

    # kernel = kernel[:, 0]
    kernel = kernel / np.sum(kernel, axis=(0, 1))

    return kernel


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
            ki_idx = ki + kernel_hf_size
            kj_idx = kj + kernel_hf_size
            if kernel[ki_idx, kj_idx] != 0.0:
                i_idx = wp.clamp(i + ki, 0, height - 1)
                j_idx = wp.clamp(j + kj, 0, width - 1)

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
    # rgb_data_out[i, j, 0] = wp.uint8((1.0 - alpha) * wp.float(rgb_data_in[i, j, 0]))
    # rgb_data_out[i, j, 1] = wp.uint8((1.0 - alpha) * wp.float(rgb_data_in[i, j, 1]))
    # rgb_data_out[i, j, 2] = wp.uint8((1.0 - alpha) * wp.float(rgb_data_in[i, j, 2]))
    rgb_data_out[i, j, 3] = rgb_data_in[i, j, 3]


class OgnAugMotionBlurExpInternalState:
    def __init__(self):
        self.output_array = None


class OgnAugMotionBlurExp:
    @staticmethod
    def internal_state():
        return OgnAugMotionBlurExpInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

        state = db.shared_state
        alpha = db.inputs.alpha
        kernel_size = db.inputs.kernelSize
        motion_angle = db.inputs.motionAngle
        strength = db.inputs.strength
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
            # If using motion blur kernel
            out_kernel = get_motion_blur_kernel2d(kernel_size, motion_angle, strength)
            conv_kernel_wp = wp.array2d(out_kernel, dtype=float)

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
