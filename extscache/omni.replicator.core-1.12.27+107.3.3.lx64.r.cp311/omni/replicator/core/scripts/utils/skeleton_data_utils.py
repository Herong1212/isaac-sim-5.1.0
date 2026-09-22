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


import numpy as np


def _reconstruct_translations(num_skels, data, sizes):
    if num_skels == 0 or not data.any():
        return
    begin = 0
    end = sizes[0]
    reconstructed_arr = []
    for i in range(num_skels):
        inner = data[begin:end]
        reconstructed_arr.append(inner.reshape(sizes[i], 3))
        begin = end
        if i != len(sizes) - 1:
            end = end + (sizes[i + 1])
    return reconstructed_arr


def _reconstruct_rotations(num_skels, data, sizes):
    if num_skels == 0 or not data.any():
        return
    begin = 0
    end = sizes[0]
    reconstructed_arr = []
    for i in range(num_skels):
        inner = data[begin:end]
        reconstructed_arr.append(inner.reshape(sizes[i], 4))
        begin = end
        if i != len(sizes) - 1:
            end = end + (sizes[i + 1])
    return reconstructed_arr


def _reconstruct_single_point(num_skels, data, sizes):
    if num_skels == 0 or not data.any():
        return
    begin = 0
    end = sizes[0]
    reconstructed_arr = []
    for i in range(num_skels):
        reconstructed_arr.append(data[begin:end])
        begin = end
        if i != len(sizes) - 1:
            end = end + sizes[i + 1]
    return reconstructed_arr


def get_skeleton_parents(num_skels, data, sizes):
    return _reconstruct_single_point(num_skels, data, sizes)


def get_rest_global_translations(num_skels, data, sizes):
    return _reconstruct_translations(num_skels, data, sizes)


def get_rest_local_rotations(num_skels, data, sizes):
    return _reconstruct_rotations(num_skels, data, sizes)


def get_rest_local_translations(num_skels, data, sizes):
    return _reconstruct_translations(num_skels, data, sizes)


def get_global_translations(num_skels, data, sizes):
    return _reconstruct_translations(num_skels, data, sizes)


def get_local_rotations(num_skels, data, sizes):
    return _reconstruct_rotations(num_skels, data, sizes)


def get_skeleton_joints(data):
    if not data:
        return
    return [s.replace("[", "").replace("]", "").replace("'", "").replace(" ", "").split(",") for s in data]


def get_translations_2d(num_skels, data, sizes):
    if num_skels == 0:
        return
    begin = 0
    end = sizes[0]
    reconstructed_arr = []
    for i in range(num_skels):
        inner = data[begin:end]
        reconstructed_arr.append(inner.reshape(sizes[i], 2))
        begin = end
        if i != len(sizes) - 1:
            end = end + (sizes[i + 1])
    return reconstructed_arr


def get_joint_occlusions(num_skels, data, sizes):
    if num_skels == 0:
        return
    return _reconstruct_single_point(num_skels, data, sizes)


def get_occlusion_types(num_skels, data, sizes):
    if num_skels == 0:
        return
    return [s.replace("[", "").replace("]", "").replace("'", "").replace(" ", "").split(",") for s in data]
