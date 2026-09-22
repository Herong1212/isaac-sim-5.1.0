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

import colorsys
import hashlib
import itertools
import math
import random
from typing import Union

import numpy as np
import warp as wp
from PIL import Image, ImageDraw

EPS = 1e-5


def data_to_colour(data):
    if isinstance(data, str):
        data = bytes(data, "utf-8")
    else:
        data = bytes(data)
    m = hashlib.sha256()
    m.update(data)
    key = int(m.hexdigest()[:8], 16)
    r = ((((key >> 0) & 0xFF) + 1) * 33) % 255
    g = ((((key >> 8) & 0xFF) + 1) * 33) % 255
    b = ((((key >> 16) & 0xFF) + 1) * 33) % 255

    # illumination normalization to 128
    inv_norm_i = 128 * (3.0 / (r + g + b))

    return (int(r * inv_norm_i), int(g * inv_norm_i), int(b * inv_norm_i))


def colorize_distance(distance_data: Union[wp.array, np.ndarray], near: float = 1e-5, far: float = 100.0):
    """Convert distance in meters to grayscale image.

    Args:
        distance_data (wp.array, numpy.array): data returned by the annotator.
        near (float): near value to clip the distance_data.
            Set value to None to autofit data to ``min()``
        far (float): far value to clip the distance_data.
            Set value to None to autofit data to ``max()`` (disregarding np.inf)

    Return:
        (numpy.ndarray): Data converted to uint8 from (0, 255)
    """
    if isinstance(distance_data, wp.array):
        distance_data = distance_data.numpy()

    if near is None:
        # Disregard INF values
        near = np.nanmin(distance_data[distance_data != -np.inf])
    if far is None:
        # Disregard INF values
        far = np.nanmax(distance_data[distance_data != np.inf])
    clipped_data = np.clip(distance_data, near, far) + 1e-5
    clipped_data = (np.log(clipped_data) - np.log(near)) / (np.log(far) - np.log(near))
    clipped_data = 1.0 - clipped_data

    # Scaled to 255 for PNG output
    return (clipped_data * 255).astype(np.uint8)


def binary_mask_to_rle(binary_mask):
    """
    Convert a Binary Mask to RLE format neeeded by Pycocotools:
    Args:
    binary_mask - numpy.array of 0's and 1's representing current segmentation
    returns - data in RLE format to be used by pycocotools.
    """
    rle = {"counts": [], "size": list(binary_mask.shape)}
    counts = rle.get("counts")
    for i, (value, elements) in enumerate(itertools.groupby(binary_mask.ravel(order="F"))):
        if i == 0 and value == 1:
            counts.append(0)
        counts.append(len(list(elements)))
    return rle


def colorize_segmentation(data, labels, mapping=None):
    """Convert segmentation data into colored image.

    Args:
        data (numpy.array): data returned by the annotator.
        labels dict: label data mapping semantic IDs to semantic labels -
            {"0": {"class":"cube"}, "1": {"class", "sphere"}}
        mapping (dict): mapping from ids to labels used for retrieving color
            {(255, 0, 0): {"class":"cube"}, (0, 255, 0)}: {"class":"sphere"}}
    Return:
        Tuple[np.array, dict]: Data coverted to uint8 RGBA image and remapped labels
    """
    is_legacy_string_key = isinstance(next(iter(labels.keys())), str)
    if mapping:
        unique_ids = np.unique(data)
        # lut is a color look-up-table to match the segmentation ID to color
        lut = np.array([unique_ids, list(range(len(unique_ids)))])
        lut_array = lut[1, np.searchsorted(lut[0, :], data)]
        if is_legacy_string_key:
            colours = np.array(
                [mapping.get([*labels[str(_id)].values()][0].lower(), [0, 0, 0, 0]) for _id in unique_ids]
            )
        else:
            colours = np.array([mapping.get([*labels[_id].values()][0].lower(), [0, 0, 0, 0]) for _id in unique_ids])
        colored_segmentation = np.array(colours[lut_array], dtype=np.uint8)
        return colored_segmentation
    else:
        unique_ids = np.unique(data)
        # lut is a color look-up-table to match the segmentation ID to color
        lut = np.array([unique_ids, list(range(len(unique_ids)))])
        lut_array = lut[1, np.searchsorted(lut[0, :], data)]
        palette = {}
        color_2_labels = {}
        colors = random_colours(unique_ids.shape[0], enable_random=False)
        ### Setting background color ##
        colors[0] = [0, 0, 0, 0]
        colored_segmentation = np.array(colors[lut_array], dtype=np.uint8)
        for i, _id in enumerate(unique_ids):
            if is_legacy_string_key:
                _id = str(_id)
            if _id in labels:
                palette[tuple(colors[i])] = labels[_id]
                color_2_labels[tuple(colors[i])] = _id
            else:
                palette[tuple(colors[i])] = "UNLABELLED"
                color_2_labels[tuple(colors[i])] = _id
        return colored_segmentation, palette, color_2_labels


def colorize_motion_vector(data):
    """Convert motion vector into colored image. The conversion is done by mapping
    3D direction vector to HLS space, then converted to RGB.

    Args:
        data (numpy.array): data returned by the annotator of shape (H, W, 4).

    Return:
        (numpy.ndarray): Data converted to uint8 RGBA image.
    """
    r, theta, phi = _cartesian_to_spherical(data[:, :, :3])
    phi += np.pi

    theta_degree = theta * 180 / np.pi
    phi_degree = phi * 180 / np.pi

    h = phi_degree / 360
    l = theta_degree / 180

    colours = np.zeros((data.shape[0], data.shape[1], 3), dtype=np.uint8)

    # TODO: Optimize, vectorize
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            color = colorsys.hls_to_rgb(h[i, j], l[i, j], 1.0)
            colours[i, j] = (np.array(color) * 255).astype(np.uint8)

    A_channel = np.ones((data.shape[0], data.shape[1], 1), dtype=np.uint8) * 255
    colours = np.concatenate((colours, A_channel), axis=-1)

    return colours


def _cartesian_to_spherical(xyz):
    h, w = xyz.shape[0], xyz.shape[1]
    xyz = xyz.reshape(-1, 3)
    xy = xyz[:, 0] ** 2 + xyz[:, 1] ** 2
    r = np.sqrt(xy + xyz[:, 2] ** 2)
    theta = np.arctan2(np.sqrt(xy), xyz[:, 2])  # for elevation angle defined from Z-axis down
    phi = np.arctan2(xyz[:, 1], xyz[:, 0])  # for elevation angle defined from XY-plane up
    return r.reshape(h, w), theta.reshape(h, w), phi.reshape(h, w)


def colorize_bbox_2d(
    image: np.ndarray, data: np.ndarray, xform: np.ndarray = None, draw_rotated_boxes: bool = False
) -> np.ndarray:
    """Colorizes 2D bounding box data for visualization.

    Args:
        image: RGBA Image that bounding boxes are drawn onto.
        data: 2D bounding box data from the annotator.
        xform: Optional 3x3 transform matrix to apply to the points. The Xform expects `height, width` ordering.
        draw_rotated_boxes: If ``True``, draw bounding boxes with orientation using four corners when transformed using
            ``xform``. Ignored if ``xform`` is ``None``. Defaults to ``False``.

    Return:
        (numpy.ndarray): Data converted to uint8 RGB image, which the outline of the bounding box is colored.
    """
    rgb_img = Image.fromarray(image)
    rgb_img_draw = ImageDraw.Draw(rgb_img)

    colors = [data_to_colour(bbox["semanticId"]) for bbox in data]

    x_min = data["x_min"]
    y_min = data["y_min"]
    x_max = data["x_max"]
    y_max = data["y_max"]

    if xform is not None:
        if xform.shape == (9,):
            xform = xform.reshape(3, 3)
        if xform.shape != (3, 3):
            raise ValueError(f"Invalid `xform` shape, xform must be a 3x3 matrix, got {xform.shape}.")

        y_min_x_max = [y_min, x_max]
        y_max_x_min = [y_max, x_min]
        corners = np.stack((y_min_x_min, y_min_x_max, y_max_x_min, y_max_x_max), 0)
        corners_h = np.pad(corners, ((0, 0), (0, 1), (0, 0)), constant_values=1.0)

        corners_xformed = np.einsum("jki,kl->jil", corners_h, xform)[..., :2]

        if not draw_rotated_boxes:
            y_min_x_min = np.min(corners_xformed, 0)
            y_max_x_max = np.max(corners_xformed, 0)

            for bbox_min, bbox_max, color in zip(y_min_x_min, y_max_x_max, colors):
                rgb_img_draw.rectangle(xy=[bbox_min[1], bbox_min[0], bbox_max[1], bbox_max[0]], outline=color, width=2)
        else:
            for idx, color in enumerate(colors):
                rgb_img_draw.polygon(
                    xy=[
                        corners_xformed[0][idx][1],
                        corners_xformed[0][idx][0],
                        corners_xformed[1][idx][1],
                        corners_xformed[1][idx][0],
                        corners_xformed[3][idx][1],
                        corners_xformed[3][idx][0],
                        corners_xformed[2][idx][1],
                        corners_xformed[2][idx][0],
                    ],
                    outline=color,
                    width=2,
                )
    else:
        for bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, color in zip(x_min, y_min, x_max, y_max, colors):
            rgb_img_draw.rectangle(xy=[bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max], outline=color, width=2)
    bbox_2d_rgb = np.array(rgb_img)
    return bbox_2d_rgb


def colorize_normals(data):
    """Convert normals data into colored image.

    Args:
        data (numpy.ndarray): data returned by the annotator.

    Return:
        (numpy.ndarray): Data converted to uint8 RGB image.
    """

    colored_data = ((data * 0.5 + 0.5) * 255).astype(np.uint8)
    return colored_data


# Golden ratio for maximum spread in hue space
GOLDEN_RATIO = 1.618033988749895
GOLDEN_RATIO_INV = 1.0 / GOLDEN_RATIO


def color_hash(seed: int) -> int:
    """Simple hash function for better distribution. Used for colorization."""
    h = seed
    h ^= h >> 16
    h *= 0x85EBCA6B
    h ^= h >> 13
    h *= 0xC2B2AE35
    h ^= h >> 16
    return h


def random_colours_id(input_id: int, num_channels=4) -> tuple:
    """
    Generate random colors given single id.
    Generate visually distinct colours by linearly spacing the hue
    channel in HSV space and then convert to RGB space.

    Args:
        input_id (int): id to generate color for
        num_channels (int): number of channels in the color

    Return:
        (tuple): Color in r, g, b, a format
    """

    hash_val = color_hash(input_id)

    # Use golden ratio spacing for maximum hue spread
    hue = math.fmod(input_id * GOLDEN_RATIO_INV, 1.0)

    # Add hash-based perturbation for better distribution
    hue_perturbation = (hash_val & 0xFFFF) / 65536.0
    hue = math.fmod(hue + hue_perturbation * 0.1, 1.0)

    # Use hash to determine saturation and value for maximum spread
    sat_hash = hash_val >> 16
    val_hash = hash_val >> 8

    # Saturation: 0.7 to 1.0 for vibrant colors
    saturation = 0.7 + 0.3 * ((sat_hash & 0xFF) / 255.0)

    # Value: 0.8 to 1.0 for bright colors
    value = 0.8 + 0.2 * ((val_hash & 0xFF) / 255.0)

    # HSV to RGB conversion
    i = int(hue * 6.0)
    f = (hue * 6.0) - i
    p = value * (1.0 - saturation)
    q = value * (1.0 - saturation * f)
    t = value * (1.0 - saturation * (1.0 - f))
    i = i % 6

    if i == 0:
        r, g, b = value, t, p
    elif i == 1:
        r, g, b = q, value, p
    elif i == 2:
        r, g, b = p, value, t
    elif i == 3:
        r, g, b = p, q, value
    elif i == 4:
        r, g, b = t, p, q
    elif i == 5:
        r, g, b = value, p, q
    else:
        r, g, b = 0, 0, 0

    if num_channels == 4:
        return tuple([int(r * 255), int(g * 255), int(b * 255), 255])  # Alpha channel
    else:
        return tuple([int(r * 255), int(g * 255), int(b * 255)])


def random_colours(N, enable_random=True, num_channels=4, start=0):
    """
    Generate N random colors.
    Generate visually distinct colours by linearly spacing the hue
    channel in HSV space and then convert to RGB space.

    Args:
        N (int): number of colors to generate
        enable_random (bool): if True, shuffle the colors
        num_channels (int): number of channels in the color
        start (int): starting index for the colors

    Return:
        (np.ndarray): Colors in uint8 format
    """
    if enable_random:
        random.seed(10)
        start = random.random()
    hues = [(start + i / N) % 1.0 for i in range(N)]
    colours = [random_colours_id(i, num_channels) for i in range(start, start + N)]

    if enable_random:
        random.shuffle(colours)

    colours = (np.array(colours)).astype(np.uint8)
    return colours
