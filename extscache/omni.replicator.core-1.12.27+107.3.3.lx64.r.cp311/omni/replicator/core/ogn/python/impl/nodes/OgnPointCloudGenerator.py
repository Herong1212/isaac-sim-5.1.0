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

import carb
import numpy as np
import omni.graph.core as og
import warp as wp
from omni.replicator.core import annotators


def get_wp_array(ptr, shape, strides, dtype, source_device, target_device):
    wp_arr = wp.types.array(
        dtype=dtype,
        shape=shape,
        strides=strides,
        ptr=ptr,
        device=source_device,
        requires_grad=False,
    )
    if source_device != target_device:
        output_wp_arr = wp.empty_like(wp_arr, device=target_device)
        wp.copy(output_wp_arr, wp_arr)
        return output_wp_arr
    return wp_arr


@wp.kernel
def process_points(
    mat: wp.mat44f,
    mask: wp.array(dtype=wp.int32),
    points: wp.array2d(dtype=wp.float32),
    rgb: wp.array2d(dtype=wp.uint8),
    normals: wp.array2d(dtype=wp.float32),
    semantic_segmentation: wp.array(dtype=wp.uint32),
    instance_segmentation: wp.array(dtype=wp.uint32),
    points_out: wp.array2d(dtype=wp.float32),
    rgb_out: wp.array2d(dtype=wp.uint8),
    normals_out: wp.array2d(dtype=wp.float32),
    semantic_segmentation_out: wp.array(dtype=wp.uint32),
    instance_segmentation_out: wp.array(dtype=wp.uint32),
):
    tid = wp.tid()
    if mask[tid] >= 0:
        idx = int(mask[tid])

        # Compute point position
        output = wp.transform_point(mat, wp.vec3(points[tid][0], points[tid][1], points[tid][2]))
        points_out[idx][0] = output[0]
        points_out[idx][1] = output[1]
        points_out[idx][2] = output[2]

        # RGB
        rgb_out[idx][0] = rgb[tid][0]
        rgb_out[idx][1] = rgb[tid][1]
        rgb_out[idx][2] = rgb[tid][2]
        rgb_out[idx][3] = rgb[tid][3]

        # Normals
        normals_out[idx][0] = normals[tid][0]
        normals_out[idx][1] = normals[tid][1]
        normals_out[idx][2] = normals[tid][2]
        normals_out[idx][3] = normals[tid][3]

        # Semantic Segmentation
        semantic_segmentation_out[idx] = semantic_segmentation[tid]

        # Instance Segmentation
        instance_segmentation_out[idx] = instance_segmentation[tid]


@wp.kernel
def get_mask(
    camera_3d_positions: wp.array2d(dtype=wp.float32),
    semantic_segmentation: wp.array(dtype=wp.uint32),
    threshold: int,
    mask: wp.array(dtype=wp.int32),
    num_hits: wp.array(dtype=wp.uint32),
):
    tid = wp.tid()
    # wp.atomic_add(num_hits, int(0), wp.uint32(1))
    if camera_3d_positions[tid, 3] == 1 and semantic_segmentation[tid] > threshold:
        mask[tid] = wp.int32(wp.atomic_add(num_hits, int(0), wp.uint32(1)))
    else:
        mask[tid] = -1


def get_device(device_idx):
    if device_idx < 0:
        return "cpu"
    return f"cuda:{device_idx}"


class PointCloudAnnotatorState:
    def __init__(self):
        self.out_points = None
        self.out_rgb = None
        self.in_semantic_segmentation = None
        self.out_semantic_segmentation = None
        self.in_instance_segmentation = None
        self.out_instance_segmentation = None
        self.out_normals = None

    def get_semantic_segmentation_gpu(self, semantic_segmentation, target_device):
        if self.in_semantic_segmentation is None or self.in_semantic_segmentation.shape != semantic_segmentation.shape:
            self.in_semantic_segmentation = wp.empty(
                shape=semantic_segmentation.shape, dtype=wp.uint32, device=target_device
            )
        wp.copy(self.in_semantic_segmentation, semantic_segmentation)
        return self.in_semantic_segmentation

    def get_instance_segmentation_gpu(self, instance_segmentation, target_device):
        if self.in_instance_segmentation is None or self.in_instance_segmentation.shape != instance_segmentation.shape:
            self.in_instance_segmentation = wp.empty(
                shape=instance_segmentation.shape, dtype=wp.uint32, device=target_device
            )
        wp.copy(self.in_instance_segmentation, wp.array(instance_segmentation))
        return self.in_instance_segmentation

    def create_buffers(self, num_hits, device):
        self.out_points = wp.empty(
            dtype=wp.float32,
            shape=(num_hits, 3),
            device=device,
            requires_grad=False,
        )
        self.out_rgb = wp.empty(
            dtype=wp.uint8,
            shape=(num_hits, 4),
            device=device,
            requires_grad=False,
        )
        self.out_semantic_segmentation = wp.empty(
            dtype=wp.uint32,
            shape=(num_hits,),
            device=device,
            requires_grad=False,
        )
        self.out_instance_segmentation = wp.empty(
            dtype=wp.uint32,
            shape=(num_hits,),
            device=device,
            requires_grad=False,
        )
        self.out_normals = wp.empty(
            dtype=wp.float32,
            shape=(num_hits, 4),
            device=device,
            requires_grad=False,
        )


class OgnPointCloudGenerator:
    @staticmethod
    def internal_state():
        return PointCloudAnnotatorState()

    @staticmethod
    def compute(db) -> bool:
        carb.profiler.begin(1, "setup")
        state = db.shared_state
        width = db.inputs.width
        height = db.inputs.height

        # Will use rgb device index across kernels
        target_device = get_device(db.inputs.rgbCudaDeviceIndex)

        if width == 0 and height == 0:
            # Not initialized
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False
        elif width == 0 or height == 0:
            db.log_error("Height or width cannot have a dimension of 0!")
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        rgb_ptr = db.node.get_attribute("inputs:rgbPtr").get()
        rgb_strides = db.node.get_attribute("inputs:rgbStrides").get()
        rgb = get_wp_array(
            ptr=rgb_ptr,
            shape=(height, width, 4),
            strides=(rgb_strides[1], rgb_strides[0], wp.types.type_size_in_bytes(wp.uint8)),
            dtype=wp.uint8,
            source_device=get_device(db.inputs.rgbCudaDeviceIndex),
            target_device=target_device,
        ).reshape((-1, 4))

        normals_ptr = db.node.get_attribute("inputs:normalsPtr").get()
        normals_strides = db.node.get_attribute("inputs:normalsStrides").get()
        normals = get_wp_array(
            normals_ptr,
            (height, width, 4),
            (normals_strides[1], normals_strides[0], wp.types.type_size_in_bytes(wp.float32)),
            wp.float32,
            source_device=get_device(db.inputs.normalsCudaDeviceIndex),
            target_device=target_device,
        ).reshape((-1, 4))

        camera_3d_positions_ptr = db.node.get_attribute("inputs:camera3dPositionsPtr").get()
        camera_3d_position_strides = db.node.get_attribute("inputs:camera3dPositionsStrides").get()
        camera_3d_positions = get_wp_array(
            camera_3d_positions_ptr,
            (height, width, 4),
            (camera_3d_position_strides[1], camera_3d_position_strides[0], wp.types.type_size_in_bytes(wp.float32)),
            wp.float32,
            source_device=get_device(db.inputs.camera3dPositionsCudaDeviceIndex),
            target_device=target_device,
        ).reshape((-1, 4))

        carb.profiler.end(1)
        carb.profiler.begin(1, "segmentation")

        semantic_segmentation_ptr = db.node.get_attribute("inputs:semanticSegmentationPtr").get()
        semantic_segmentation_strides = db.node.get_attribute("inputs:semanticSegmentationStrides").get()
        semantic_segmentation_dtype = wp.uint32
        semantic_segmentation_shape = (height, width)
        semantic_segmentation_gpu = (
            get_wp_array(
                semantic_segmentation_ptr,
                semantic_segmentation_shape,
                dtype=semantic_segmentation_dtype,
                strides=(semantic_segmentation_strides[1], semantic_segmentation_strides[0]),
                source_device=get_device(db.inputs.semanticSegmentationCudaDeviceIndex),
                target_device=target_device,
            )
            .view(wp.uint32)
            .reshape((-1))
        )

        instance_segmentation_ptr = db.node.get_attribute("inputs:instanceSegmentationPtr").get()
        instance_segmentation_strides = db.node.get_attribute("inputs:instanceSegmentationStrides").get()
        instance_segmentation_dtype = wp.uint32
        instance_segmentation_shape = (height, width)
        instance_segmentation_gpu = (
            get_wp_array(
                instance_segmentation_ptr,
                instance_segmentation_shape,
                dtype=instance_segmentation_dtype,
                strides=(instance_segmentation_strides[1], instance_segmentation_strides[0]),
                source_device=get_device(db.inputs.instanceSegmentationCudaDeviceIndex),
                target_device=target_device,
            )
            .view(wp.uint32)
            .reshape((-1))
        )
        carb.profiler.end(1)
        carb.profiler.begin(1, "cam mats")

        cam_world_to_local = db.inputs.cameraViewTransform.reshape(4, 4)
        cam_local_to_world = np.linalg.inv(cam_world_to_local)

        carb.profiler.end(1)
        carb.profiler.begin(1, "mask")

        # Extract points that actually hit the prims
        threshold = 0 if db.inputs.includeUnlabelled else 1
        mask = wp.empty(shape=(len(camera_3d_positions)), dtype=wp.int32, device=target_device)
        num_hits = wp.zeros(shape=(1,), dtype=wp.uint32, device=target_device)
        wp.launch(
            get_mask,
            dim=len(camera_3d_positions),
            inputs=[
                camera_3d_positions,
                semantic_segmentation_gpu,
                threshold,
                mask,
                num_hits,
            ],
            device=target_device,
        )

        num_hits_int = num_hits.numpy()[0]

        state.create_buffers(num_hits_int, target_device)

        # Return empty array if the mask is all False
        if num_hits_int == 0:
            db.outputs.dataShape = (1, state.out_points.shape[0], 3)
            db.outputs.bufferSize = state.out_points.size
            db.outputs.cudaDeviceIndex = db.inputs.rgbCudaDeviceIndex
            db.outputs.dataType = "float32"

            db.outputs.pointRgbDataShape = (1, state.out_rgb.shape[0], 4)
            db.outputs.pointRgbBufferSize = state.out_rgb.size
            db.outputs.pointRgbCudaDeviceIndex = db.inputs.rgbCudaDeviceIndex
            db.outputs.pointRgbDataType = "uint8"

            db.outputs.pointNormalsDataShape = (1, state.out_normals.shape[0], 4)
            db.outputs.pointNormalsBufferSize = state.out_normals.size
            db.outputs.pointNormalsCudaDeviceIndex = db.inputs.rgbCudaDeviceIndex
            db.outputs.pointNormalsDataType = "float32"

            db.outputs.pointSemanticDataShape = (1, state.out_semantic_segmentation.shape[0])
            db.outputs.pointSemanticBufferSize = state.out_semantic_segmentation.size
            db.outputs.pointSemanticCudaDeviceIndex = db.inputs.rgbCudaDeviceIndex
            db.outputs.pointSemanticDataType = "uint32"

            db.outputs.pointInstanceDataShape = (1, state.out_instance_segmentation.shape[0])
            db.outputs.pointInstanceBufferSize = state.out_instance_segmentation.size
            db.outputs.pointInstanceCudaDeviceIndex = db.inputs.rgbCudaDeviceIndex
            db.outputs.pointInstanceDataType = "uint32"

            db.outputs.exec = og.ExecutionAttributeState.ENABLED
            carb.profiler.end(1)
            return True

        carb.profiler.end(1)
        carb.profiler.begin(1, "matmul CUDA")

        wp.launch(
            kernel=process_points,
            dim=len(camera_3d_positions),
            inputs=[
                cam_local_to_world.transpose(),
                mask,
                camera_3d_positions,
                rgb,
                normals,
                semantic_segmentation_gpu,
                instance_segmentation_gpu,
                state.out_points,
                state.out_rgb,
                state.out_normals,
                state.out_semantic_segmentation,
                state.out_instance_segmentation,
            ],
            device=target_device,
        )

        carb.profiler.end(1)
        carb.profiler.begin(1, "out assign")

        db.outputs.dataPtr = state.out_points.ptr
        db.outputs.dataShape = (1, state.out_points.shape[0], 3)
        db.outputs.bufferSize = state.out_points.size
        db.outputs.cudaDeviceIndex = state.out_points.device.ordinal
        db.outputs.dataType = "float32"

        db.outputs.pointRgbPtr = state.out_rgb.ptr
        db.outputs.pointRgbDataShape = (1, state.out_rgb.shape[0], 4)
        db.outputs.pointRgbBufferSize = state.out_rgb.size
        db.outputs.pointRgbCudaDeviceIndex = state.out_rgb.device.ordinal
        db.outputs.pointRgbDataType = "uint8"

        db.outputs.pointNormalsPtr = state.out_normals.ptr
        db.outputs.pointNormalsDataShape = (1, state.out_normals.shape[0], 4)
        db.outputs.pointNormalsBufferSize = state.out_normals.size
        db.outputs.pointNormalsCudaDeviceIndex = state.out_normals.device.ordinal
        db.outputs.pointNormalsDataType = "float32"

        db.outputs.pointSemanticPtr = state.out_semantic_segmentation.ptr
        db.outputs.pointSemanticDataShape = (1, state.out_semantic_segmentation.shape[0])
        db.outputs.pointSemanticBufferSize = state.out_semantic_segmentation.size
        db.outputs.pointSemanticCudaDeviceIndex = state.out_semantic_segmentation.device.ordinal
        db.outputs.pointSemanticDataType = "uint32"

        db.outputs.pointInstancePtr = state.out_instance_segmentation.ptr
        db.outputs.pointInstanceDataShape = (1, state.out_instance_segmentation.shape[0])
        db.outputs.pointInstanceBufferSize = state.out_instance_segmentation.size
        db.outputs.pointInstanceCudaDeviceIndex = state.out_instance_segmentation.device.ordinal
        db.outputs.pointInstanceDataType = "uint32"

        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        carb.profiler.end(1)
        return True
