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

import os

import carb
import numpy as np
import warp as wp
from PIL import Image


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
def zoom(
    dim_orig: wp.vec2,
    dim_new: wp.vec2,
    wp_orig: wp.array3d(dtype=wp.uint8),  # must be 3D for the bilinear interpolation
    wp_new: wp.array2d(dtype=wp.uint8),  # perform ops in 2D so we don't have to reshape on the GPU with warp
):

    i, j = wp.tid()

    # trace backward
    p = wp.vec2(
        float(i) * (dim_orig[0] - float(1)) / (dim_new[0] - float(1)),
        float(j) * (dim_orig[1] - float(1)) / (dim_new[1] - float(1)),
    )

    idx = j + int(dim_new[1]) * i  # for writing the output in 2D rather than 3D.

    wp_new[idx, 0] = sample_float(wp_orig, 0, dim_orig, p[0], p[1])
    wp_new[idx, 1] = sample_float(wp_orig, 1, dim_orig, p[0], p[1])
    wp_new[idx, 2] = sample_float(wp_orig, 2, dim_orig, p[0], p[1])
    wp_new[idx, 3] = wp.uint8(255)


def get_zoomed_wp_ims_from_path(folderpath, height, width, device):
    """
    Provided a folderpath containing images of any size, returns a list of images as wp arrays of shape [H x W, C]
    """

    bg_ims = []
    with wp.ScopedDevice(device):
        for path, _, files in os.walk(folderpath):
            files.sort()
            for file in files:
                if os.name == "nt":  # If windows #NEED TO CHECK THIS AND FIX
                    curr_filepath = path + "/" + file
                    curr_filepath = curr_filepath.replace("/", "\\")
                else:  # else Linux
                    if path[-1] != "/":
                        path += "/"
                    curr_filepath = path + file
                try:
                    image = Image.open(curr_filepath)
                    image = image.convert("RGBA")
                    im_arr = np.array(image.getdata()).astype(np.uint8).reshape(image.size[1], image.size[0], 4)
                    # TODO:
                    # make a method to read from HDF5, which is much more efficient than PIL
                    # OR use joblib https://joblib.readthedocs.io/en/latest/generated/joblib.Memory.html

                    wp_orig = wp.array(im_arr, dtype=wp.uint8, device=device)
                    curr_bg_im_gpu = wp.zeros((height * width, 4), dtype=wp.uint8, device=device)
                    wp_dim_orig = wp.vec2(float(im_arr.shape[0]), float(im_arr.shape[1]))
                    wp_dim_new = wp.vec2(float(height), float(width))
                    wp.launch(
                        kernel=zoom,
                        dim=tuple((height, width)),
                        inputs=[wp_dim_orig, wp_dim_new, wp_orig, curr_bg_im_gpu],
                    )
                    bg_ims.append(curr_bg_im_gpu)
                except:
                    carb.log_warn(
                        f"get_zoomed_ims_from_path function is unable to load image at filepath {curr_filepath}"
                    )

    if len(bg_ims) == 0:
        dtype = wp.uint8
        black_bg = np.zeros((width * height, 4))
        black_bg[..., 3] = 255
        curr_bg_im_gpu = wp.array(black_bg, dtype=dtype, device=device)
        bg_ims.append(curr_bg_im_gpu)

    return bg_ims
