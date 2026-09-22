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

"""OmniGraph node for background randomization"""


# ======================================================================


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.kernel
def rgb_to_grey_and_blur(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array2d(dtype=wp.uint8)):
    i, j = wp.tid()
    height = data_in.shape[0]
    width = data_in.shape[1]

    # Only process non-border pixels for the blur
    if i > 0 and i < height - 1 and j > 0 and j < width - 1:
        # Gaussian kernel 3x3
        kernel = wp.mat33f(1.0, 2.0, 1.0, 2.0, 4.0, 2.0, 1.0, 2.0, 1.0) / 16.0

        sum = 0.0
        # Apply convolution with RGB to grayscale conversion in a single pass
        for ki in range(-1, 2):
            for kj in range(-1, 2):
                # Convert RGB to grayscale using standard weights
                gray_val = (
                    wp.float(data_in[i + ki, j + kj, 0]) * 0.299  # Red
                    + wp.float(data_in[i + ki, j + kj, 1]) * 0.587  # Green
                    + wp.float(data_in[i + ki, j + kj, 2]) * 0.114  # Blue
                )
                sum += gray_val * kernel[ki + 1, kj + 1]

        data_out[i, j] = wp.uint8(wp.clamp(sum, 0.0, 255.0))
    else:
        # For border pixels, just convert to grayscale without blur
        data_out[i, j] = wp.uint8(
            wp.float(data_in[i, j, 0]) * 0.299 + wp.float(data_in[i, j, 1]) * 0.587 + wp.float(data_in[i, j, 2]) * 0.114
        )


@wp.kernel
def sobel_and_suppress(
    data_in: wp.array2d(dtype=wp.uint8),
    data_out: wp.array2d(dtype=wp.uint8),
    low_threshold: float,
    high_threshold: float,
):
    i, j = wp.tid()
    height = data_in.shape[0]
    width = data_in.shape[1]

    if i > 0 and i < height - 1 and j > 0 and j < width - 1:
        # Compute Sobel gradients with proper kernel weights
        gx = (
            -1.0 * wp.float(data_in[i - 1, j - 1])
            + -2.0 * wp.float(data_in[i, j - 1])
            + -1.0 * wp.float(data_in[i + 1, j - 1])
            + 1.0 * wp.float(data_in[i - 1, j + 1])
            + 2.0 * wp.float(data_in[i, j + 1])
            + 1.0 * wp.float(data_in[i + 1, j + 1])
        )

        gy = (
            -1.0 * wp.float(data_in[i - 1, j - 1])
            + -2.0 * wp.float(data_in[i - 1, j])
            + -1.0 * wp.float(data_in[i - 1, j + 1])
            + 1.0 * wp.float(data_in[i + 1, j - 1])
            + 2.0 * wp.float(data_in[i + 1, j])
            + 1.0 * wp.float(data_in[i + 1, j + 1])
        )

        # Compute gradient magnitude
        magnitude = wp.sqrt(gx * gx + gy * gy)

        # Calculate gradient direction and handle edge cases
        angle = wp.atan2(gy, gx) * 180.0 / 3.14159
        if angle < 0:
            angle += 180.0

        # Get interpolated magnitudes along gradient direction
        g00 = wp.float(0.0)  # First interpolated point
        g01 = wp.float(0.0)  # Second interpolated point
        xstep = wp.float(0.0)
        ystep = wp.float(0.0)

        # Determine interpolation direction based on angle
        if angle <= 22.5 or angle > 157.5:  # ~0 degrees
            xstep = wp.float(1.0)
            ystep = wp.float(0.0)
        elif angle > 22.5 and angle <= 67.5:  # ~45 degrees
            xstep = wp.float(1.0)
            ystep = wp.float(1.0)
        elif angle > 67.5 and angle <= 112.5:  # ~90 degrees
            xstep = wp.float(0.0)
            ystep = wp.float(1.0)
        else:  # ~135 degrees
            xstep = wp.float(-1.0)
            ystep = wp.float(1.0)

        # Interpolate gradient magnitudes
        # Forward direction
        x1_floor = wp.int32(wp.float(j) + xstep)
        y1_floor = wp.int32(wp.float(i) + ystep)
        if x1_floor > 0 and x1_floor < width - 1 and y1_floor > 0 and y1_floor < height - 1:
            gx1 = (
                -1.0 * wp.float(data_in[y1_floor - 1, x1_floor - 1])
                + -2.0 * wp.float(data_in[y1_floor, x1_floor - 1])
                + -1.0 * wp.float(data_in[y1_floor + 1, x1_floor - 1])
                + 1.0 * wp.float(data_in[y1_floor - 1, x1_floor + 1])
                + 2.0 * wp.float(data_in[y1_floor, x1_floor + 1])
                + 1.0 * wp.float(data_in[y1_floor + 1, x1_floor + 1])
            )
            gy1 = (
                -1.0 * wp.float(data_in[y1_floor - 1, x1_floor - 1])
                + -2.0 * wp.float(data_in[y1_floor - 1, x1_floor])
                + -1.0 * wp.float(data_in[y1_floor - 1, x1_floor + 1])
                + 1.0 * wp.float(data_in[y1_floor + 1, x1_floor - 1])
                + 2.0 * wp.float(data_in[y1_floor + 1, x1_floor])
                + 1.0 * wp.float(data_in[y1_floor + 1, x1_floor + 1])
            )
            g00 = wp.sqrt(gx1 * gx1 + gy1 * gy1)

        # Backward direction
        x2_floor = wp.int32(wp.float(j) - xstep)
        y2_floor = wp.int32(wp.float(i) - ystep)
        if x2_floor > 0 and x2_floor < width - 1 and y2_floor > 0 and y2_floor < height - 1:
            gx2 = (
                -1.0 * wp.float(data_in[y2_floor - 1, x2_floor - 1])
                + -2.0 * wp.float(data_in[y2_floor, x2_floor - 1])
                + -1.0 * wp.float(data_in[y2_floor + 1, x2_floor - 1])
                + 1.0 * wp.float(data_in[y2_floor - 1, x2_floor + 1])
                + 2.0 * wp.float(data_in[y2_floor, x2_floor + 1])
                + 1.0 * wp.float(data_in[y2_floor + 1, x2_floor + 1])
            )
            gy2 = (
                -1.0 * wp.float(data_in[y2_floor - 1, x2_floor - 1])
                + -2.0 * wp.float(data_in[y2_floor - 1, x2_floor])
                + -1.0 * wp.float(data_in[y2_floor - 1, x2_floor + 1])
                + 1.0 * wp.float(data_in[y2_floor + 1, x2_floor - 1])
                + 2.0 * wp.float(data_in[y2_floor + 1, x2_floor])
                + 1.0 * wp.float(data_in[y2_floor + 1, x2_floor + 1])
            )
            g01 = wp.sqrt(gx2 * gx2 + gy2 * gy2)

        # Strict non-maximum suppression with interpolation
        if magnitude > g00 and magnitude > g01:
            # Scale magnitude to match OpenCV's scaling
            scaled_magnitude = magnitude * 3.0

            if scaled_magnitude >= high_threshold:
                data_out[i, j] = wp.uint8(255)  # Strong edge
            elif scaled_magnitude >= low_threshold:
                data_out[i, j] = wp.uint8(127)  # Weak edge
            else:
                data_out[i, j] = wp.uint8(0)  # Non-edge
        else:
            data_out[i, j] = wp.uint8(0)
    else:
        data_out[i, j] = wp.uint8(0)


@wp.kernel
def hysteresis_thresholding(data_inout: wp.array2d(dtype=wp.uint8)):
    i, j = wp.tid()
    height = data_inout.shape[0]
    width = data_inout.shape[1]

    if i > 0 and i < height - 1 and j > 0 and j < width - 1:
        # Only process weak edges
        if data_inout[i, j] == 127:
            # Check 8-connected neighbors
            has_strong_neighbor = float(0.0)

            for di in range(-1, 2):
                if i + di < 0 or i + di >= height:
                    continue
                for dj in range(-1, 2):
                    if j + dj < 0 or j + dj >= width:
                        continue
                    if di == 0 and dj == 0:
                        continue
                    if data_inout[i + di, j + dj] == 255:
                        has_strong_neighbor += 1.0
                        break
                if has_strong_neighbor >= 1.0:
                    break

            # Convert weak edge to strong if connected to strong edge, otherwise suppress
            if has_strong_neighbor >= 1.0:
                data_inout[i, j] = wp.uint8(255)
            else:
                data_inout[i, j] = wp.uint8(0)


class OgnAugCannyInternalState:
    def __init__(self):
        self.greyscale = None
        self.edges = None


class OgnAugCanny:
    @staticmethod
    def internal_state():
        return OgnAugCannyInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

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
        )

        if state.greyscale is None or state.greyscale.shape != (height, width):
            state.greyscale = wp.empty(
                dtype=wp.uint8,
                shape=(height, width),
                device=device,
                requires_grad=False,
            )

        if state.edges is None or state.edges.shape != (height, width):
            state.edges = wp.empty(
                dtype=wp.uint8,
                shape=(height, width),
                device=device,
                requires_grad=False,
            )

        # Get threshold values from inputs
        low_threshold = db.inputs.thresholdLow
        high_threshold = db.inputs.thresholdHigh

        wp.launch(
            kernel=rgb_to_grey_and_blur,
            dim=(height, width),
            inputs=[rgb_data_gpu, state.greyscale],
            device=device,
        )
        wp.launch(
            kernel=sobel_and_suppress,
            dim=(height, width),
            inputs=[state.greyscale, state.edges, low_threshold, high_threshold],
            device=device,
        )

        # Multiple passes of hysteresis to propagate strong edges
        for _ in range(3):  # Usually 2-3 passes are sufficient
            wp.launch(
                kernel=hysteresis_thresholding,
                dim=(height, width),
                inputs=[state.edges],
                device=device,
            )

        db.outputs.exec = 1
        db.outputs.bufferSize = db.inputs.bufferSize
        db.outputs.height = db.inputs.height
        db.outputs.width = db.inputs.width
        db.outputs.cudaDeviceIndex = device_idx
        db.outputs.dataPtr = state.edges.ptr
        db.outputs.strides = state.edges.strides[1], state.edges.strides[0]

        return True
