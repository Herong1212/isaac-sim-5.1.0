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
from functools import reduce

import omni.replicator.core as rep
import warp as wp
from omni.gpu_foundation_factory import TextureFormat

"""OmniGraph node for shaded segmentation"""


# ======================================================================


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.kernel
def shade_segmentation(
    segmentation: wp.array2d(dtype=wp.uint32),
    normals: wp.array3d(dtype=wp.float32),
    shading_out: wp.array3d(dtype=wp.uint8),
    light_source: wp.array(dtype=wp.vec3f),
    use_candy_colours: bool,
):
    """Apply pastel-like colorization to segmentation using surface normals.

    Args:
        segmentation: Input segmentation image with instance IDs (H,W)
        normals: Surface normal vectors (H,W,3)
        shading_out: Output colorized segmentation image (H,W,3)
        light_source: Position of light source
        use_candy_colours: If true, replace segmentation colours with random candy colours
    """
    i, j = wp.tid()
    instance_id = segmentation[i, j]

    # Check if this is background (index 0)
    if instance_id == 0:
        # Set background to black
        shading_out[i, j, 0] = wp.uint8(0)
        shading_out[i, j, 1] = wp.uint8(0)
        shading_out[i, j, 2] = wp.uint8(0)
        return

    normal = normals[i, j]
    normals_normalized = wp.normalize(wp.vec3f(normal[0], normal[1], normal[2]))
    light_source_vec = wp.normalize(light_source[0])

    # Calculate base shading from dot product (ranges from -1 to 1)
    base_shade = wp.dot(normals_normalized, light_source_vec)
    # Remap from [-1, 1] to desired shading range [min_shade, 1.0]
    min_shade = 0.5  # Adjusted for pastel effect
    shade = wp.clamp(wp.lerp(min_shade, 1.0, (base_shade + 1.0) * 0.5), 0.0, 1.0)

    if use_candy_colours:
        # Convert instance_id to color using HSV with pastel parameters
        state_h = wp.rand_init(wp.int32(instance_id))
        state_s = wp.rand_init(wp.int32(instance_id), 1)
        state_v = wp.rand_init(wp.int32(instance_id), 2)

        # Pastel colors have moderate saturation and high value/brightness
        h = wp.randf(state_h)
        s = 0.3 + wp.randf(state_s) * 0.3  # Lower saturation (0.3-0.6) for pastel effect
        v = 0.9 + wp.randf(state_v) * 0.1  # High value/brightness (0.9-1.0)

        # HSV to RGB conversion
        K = wp.vec4f(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0)
        p = wp.vec3f(
            wp.abs(wp.frac(h + K.x) * 6.0 - K.w),
            wp.abs(wp.frac(h + K.y) * 6.0 - K.w),
            wp.abs(wp.frac(h + K.z) * 6.0 - K.w),
        )
        clamped = wp.vec3f(
            wp.clamp(p[0] - K.x, 0.0, 1.0), wp.clamp(p[1] - K.x, 0.0, 1.0), wp.clamp(p[2] - K.x, 0.0, 1.0)
        )
        rgb = v * wp.lerp(wp.vec3f(K.x), clamped, s) * 255.0
    else:
        r = wp.float32(instance_id & wp.uint32(0xFF))
        g = wp.float32((instance_id >> wp.uint32(8)) & wp.uint32(0xFF))
        b = wp.float32((instance_id >> wp.uint32(16)) & wp.uint32(0xFF))
        rgb = wp.vec3f(r, g, b)

    # Apply shading and convert to uint8
    shading_out[i, j, 0] = wp.uint8(rgb[0] * shade)
    shading_out[i, j, 1] = wp.uint8(rgb[1] * shade)
    shading_out[i, j, 2] = wp.uint8(rgb[2] * shade)


class AugShadeSegmentationInternalState:
    def __init__(self):
        self.output_array = None


class OgnAugShadeSegmentation:
    @staticmethod
    def internal_state():
        return AugShadeSegmentationInternalState()

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
        normal_dtype = wp.float32
        normal_device_idx = db.inputs.normalCudaDeviceIndex
        normal_data_ptr = db.inputs.normalDataPtr
        if normal_device_idx < 0:
            normal_device = "cpu"
        else:
            normal_device = f"cuda:{normal_device_idx}"
        normal_strides_raw = db.inputs.normalStrides
        normal_strides = (normal_strides_raw[1], normal_strides_raw[0], wp.types.type_size_in_bytes(normal_dtype))

        normal_data_gpu = wp.types.array(
            dtype=normal_dtype,
            shape=orig_shape,  # number of elements
            ptr=normal_data_ptr,
            device=normal_device,
            strides=normal_strides,
            requires_grad=False,
        )

        segmentation_dtype = wp.uint32
        segmentation_device_idx = db.inputs.segmentationCudaDeviceIndex
        segmentation_data_ptr = db.inputs.segmentationDataPtr
        if segmentation_device_idx < 0:
            segmentation_device = "cpu"
        else:
            segmentation_device = f"cuda:{segmentation_device_idx}"
        segmentation_strides_raw = db.inputs.segmentationStrides

        segmentation_dtype = wp.uint32
        segmentation_shape = (height, width)
        segmentation_strides = (
            segmentation_strides_raw[1],
            segmentation_strides_raw[0],
            wp.types.type_size_in_bytes(segmentation_dtype),
        )

        segmentation_data_gpu = wp.types.array(
            dtype=segmentation_dtype,
            shape=segmentation_shape,  # number of elements
            ptr=segmentation_data_ptr,
            device=segmentation_device,
            strides=segmentation_strides,
            requires_grad=False,
        ).to(normal_device)

        output_dtype = wp.uint8
        if state.output_array is None or tuple(orig_shape) != state.output_array.shape:
            state.output_array = wp.empty(
                dtype=output_dtype,
                shape=(orig_shape[0], orig_shape[1], 3),
                device=normal_device,
                requires_grad=False,
            )
        elif normal_device != state.output_array.device:
            state.output_array = state.output_array.to(normal_device)

        light_source = wp.array([*db.inputs.lightSource], dtype=wp.vec3f, device=normal_device)
        wp.launch(
            kernel=shade_segmentation,
            dim=(height, width),
            inputs=[
                segmentation_data_gpu,
                normal_data_gpu,
                state.output_array,
                light_source,
                db.inputs.useCandyColours,
            ],
            device=normal_device,
        )

        db.outputs.exec = 1
        data_size_out = reduce(lambda x, y: x * y, state.output_array.shape) * wp.types.type_size_in_bytes(
            state.output_array.dtype
        )
        db.outputs.width = width
        db.outputs.height = height
        db.outputs.bufferSize = data_size_out
        db.outputs.cudaDeviceIndex = normal_device_idx
        db.outputs.dataPtr = state.output_array.ptr
        db.outputs.strides = state.output_array.strides[1], state.output_array.strides[0]
        return True
