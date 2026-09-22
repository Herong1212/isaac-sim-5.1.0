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
import os

import carb.settings
import omni.replicator.core as rep
import warp as wp
from omni.replicator.core import rng
from omni.replicator.core.ogn.OgnAugBgRandExpDatabase import OgnAugBgRandExpDatabase
from omni.replicator.core.utils import wp_utils

"""OmniGraph node for background randomization"""


# ======================================================================


BGRAND_SETTINGS = {
    "/rtx/post/backgroundZeroAlpha/enabled": True,
    "/rtx/post/backgroundZeroAlpha/backgroundComposite": False,
    "/rtx/post/backgroundZeroAlpha/outputAlphaInComposite": True,
}
AA_SETTING = "/rtx/post/aa/op"


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


@wp.kernel
def fill_background(
    rgb_in: wp.array3d(dtype=wp.uint8), bg_in: wp.array3d(dtype=wp.uint8), rgb_out: wp.array3d(dtype=wp.uint8)
):
    i, j = wp.tid()

    rgb_out[i, j, 0] = wp.uint8(
        (int(rgb_in[i, j, 3]) * int(rgb_in[i, j, 0]) + (255 - int(rgb_in[i, j, 3])) * int(bg_in[i, j, 0])) / 255
    )
    rgb_out[i, j, 1] = wp.uint8(
        (int(rgb_in[i, j, 3]) * int(rgb_in[i, j, 1]) + (255 - int(rgb_in[i, j, 3])) * int(bg_in[i, j, 1])) / 255
    )
    rgb_out[i, j, 2] = wp.uint8(
        (int(rgb_in[i, j, 3]) * int(rgb_in[i, j, 2]) + (255 - int(rgb_in[i, j, 3])) * int(bg_in[i, j, 2])) / 255
    )
    rgb_out[i, j, 3] = wp.uint8(255)


class AugBgRandExpInternalState:
    def __init__(self):
        self._bg_ims = []
        self._last_width_height = [0, 0]
        self.rng = rep.rng.ReplicatorRNG()
        self.settings_cache = None
        self.output_array = None

    def initialize(self):
        self.cache_settings()
        self.set_settings(BGRAND_SETTINGS)
        carb.log_warn(
            f"AugBgRandExp requires specific render settings which have been automatically set as follows: {BGRAND_SETTINGS}"
        )

    def cache_settings(self):
        self.settings_cache = {}
        _settings = carb.settings.get_settings()
        for setting in BGRAND_SETTINGS:
            self.settings_cache[setting] = _settings.get(setting)
        # Cache AA setting in case it's changed
        self.settings_cache[AA_SETTING] = _settings.get(AA_SETTING)

    def set_settings(self, settings_dict):
        _settings = carb.settings.get_settings()
        if settings_dict:
            for setting, value in settings_dict.items():
                _settings.set(setting, value)
        if _settings.get(AA_SETTING) == 2:
            # Matte compositing does not work with FXAA
            carb.log_warn(
                "AugBgRandExp uses compositing which is incompatible with current Antialiasing mode: FXAA. Switching to DLAA"
            )
            _settings.set(AA_SETTING, 4)

    def restore_settings(self):
        self.set_settings(self.settings_cache)

    def release(self, node):
        self.restore_settings()
        rep.rng.release(node.get_prim_path())

    def get_random_background_im(self, folderpath, width, height, device):

        # currently we reload and zoom the background images from a folder if the incoming image (db.inputs.data)
        # height and width does not match what the heights and widths are in our cache of background images.
        # Thus, the first time the node is called with db.inputs.data of length greater than 0, it will load and zoom.
        reload_zoom_bgims_flag = [width, height] != self._last_width_height

        if reload_zoom_bgims_flag:
            if len(folderpath) == 0 or not os.path.exists(folderpath):
                raise RuntimeWarning("No valid folderpath provided for background randomization images.")

            self._bg_ims = wp_utils.get_zoomed_wp_ims_from_path(folderpath, height, width, device)

        self._last_width_height = [width, height]
        random_im_idx = self.rng.generator.integers(0, max(1, len(self._bg_ims)))
        bg_im_gpu = self._bg_ims[random_im_idx]
        return bg_im_gpu.reshape((height, width, bg_im_gpu.shape[-1]))


class OgnAugBgRandExp:
    @staticmethod
    def internal_state():
        return AugBgRandExpInternalState()

    @staticmethod
    def release(node):
        state = OgnAugBgRandExpDatabase.shared_internal_state(node)
        state.release(node)

    @staticmethod
    def initialize(graph_context, node):
        state = OgnAugBgRandExpDatabase.shared_internal_state(node)
        state.initialize()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.width == 0 or db.inputs.height == 0:
            return False

        state = db.shared_state
        seed = db.inputs.seed
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

        is_seed_valid = seed is not None
        is_seed_changed = state.rng is None or seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(seed, db.node, node_id)

        bg_data_gpu = state.get_random_background_im(db.inputs.folderpath, width, height, device)

        dtype = wp.uint8

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
            kernel=fill_background,
            dim=(height, width),
            inputs=[rgb_data_gpu, bg_data_gpu, state.output_array],
            device=device,
        )

        db.outputs.xform = db.inputs.xform
        db.outputs.exec = 1
        db.outputs.bufferSize = db.inputs.bufferSize
        db.outputs.height = db.inputs.height
        db.outputs.width = db.inputs.width
        db.outputs.format = array_format
        db.outputs.cudaDeviceIndex = device_idx
        db.outputs.dataPtr = state.output_array.ptr
        db.outputs.strides = state.output_array.strides[1], state.output_array.strides[0]

        return True
