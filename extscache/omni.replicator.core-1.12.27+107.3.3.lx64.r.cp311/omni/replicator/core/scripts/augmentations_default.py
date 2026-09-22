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

# pylint: disable=too-many-lines, invalid-name

import warp as wp

from .annotators import Augmentation, register_augmentation


@wp.kernel
def rgba_to_rgb(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
    i, j = wp.tid()
    data_out[i, j, 0] = data_in[i, j, 0]
    data_out[i, j, 1] = data_in[i, j, 1]
    data_out[i, j, 2] = data_in[i, j, 2]


@wp.kernel
def aug_adjust_sigmoid(
    data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), cutoff: float, gain: float
):
    i, j = wp.tid()

    r = 1.0 / (1.0 + wp.exp(gain * (cutoff - wp.float(data_in[i, j, 0]) / 255.0)))
    g = 1.0 / (1.0 + wp.exp(gain * (cutoff - wp.float(data_in[i, j, 1]) / 255.0)))
    b = 1.0 / (1.0 + wp.exp(gain * (cutoff - wp.float(data_in[i, j, 2]) / 255.0)))

    data_out[i, j, 0] = wp.clamp(wp.uint8(r * 255.0), wp.uint8(0), wp.uint8(255))
    data_out[i, j, 1] = wp.clamp(wp.uint8(g * 255.0), wp.uint8(0), wp.uint8(255))
    data_out[i, j, 2] = wp.clamp(wp.uint8(b * 255.0), wp.uint8(0), wp.uint8(255))
    data_out[i, j, 3] = data_in[i, j, 3]


@wp.kernel
def aug_brightness(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), brightness_factor: float):

    i, j = wp.tid()

    r = wp.float(data_in[i, j, 0]) * brightness_factor
    g = wp.float(data_in[i, j, 1]) * brightness_factor
    b = wp.float(data_in[i, j, 2]) * brightness_factor

    data_out[i, j, 0] = wp.uint8(wp.clamp(r, 0.0, 255.0))
    data_out[i, j, 1] = wp.uint8(wp.clamp(g, 0.0, 255.0))
    data_out[i, j, 2] = wp.uint8(wp.clamp(b, 0.0, 255.0))
    data_out[i, j, 3] = data_in[i, j, 3]


@wp.kernel
def aug_speckle_noise(
    data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), seed: int, sigma: float
):

    i, j = wp.tid()

    dim_i = data_in.shape[0]
    dim_j = data_in.shape[1]

    pixel_id = i * dim_i + j
    state_r = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 0))
    state_g = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 1))
    state_b = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 2))

    r = wp.float(data_in[i, j, 0]) * 1.0 / 255.0
    g = wp.float(data_in[i, j, 1]) * 1.0 / 255.0
    b = wp.float(data_in[i, j, 2]) * 1.0 / 255.0

    noise_r = sigma * wp.randn(state_r) * r
    noise_g = sigma * wp.randn(state_g) * g
    noise_b = sigma * wp.randn(state_b) * b

    r = r + noise_r
    g = g + noise_g
    b = b + noise_b

    data_out[i, j, 0] = wp.uint8(wp.clamp(r * 255.0, 0.0, 255.0))
    data_out[i, j, 1] = wp.uint8(wp.clamp(g * 255.0, 0.0, 255.0))
    data_out[i, j, 2] = wp.uint8(wp.clamp(b * 255.0, 0.0, 255.0))
    data_out[i, j, 3] = data_in[i, j, 3]


@wp.kernel
def aug_shot_noise(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), seed: int, sigma: float):
    i, j = wp.tid()

    dim_i = data_in.shape[0]
    dim_j = data_in.shape[1]

    pixel_id = i * dim_i + j
    state_r = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 0))
    state_g = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 1))
    state_b = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 2))

    r = wp.float(data_in[i, j, 0]) * 1.0 / 255.0
    g = wp.float(data_in[i, j, 1]) * 1.0 / 255.0
    b = wp.float(data_in[i, j, 2]) * 1.0 / 255.0

    noise_r = wp.sqrt(sigma * r) * wp.randn(state_r) + r * sigma
    noise_g = wp.sqrt(sigma * b) * wp.randn(state_g) + g * sigma
    noise_b = wp.sqrt(sigma * g) * wp.randn(state_b) + b * sigma

    r = noise_r / sigma
    g = noise_g / sigma
    b = noise_b / sigma

    r = wp.clamp(r, 0.0, 1.0)
    g = wp.clamp(g, 0.0, 1.0)
    b = wp.clamp(b, 0.0, 1.0)

    data_out[i, j, 0] = wp.uint8(r * 255.0)
    data_out[i, j, 1] = wp.uint8(g * 255.0)
    data_out[i, j, 2] = wp.uint8(b * 255.0)
    data_out[i, j, 3] = data_in[i, j, 3]


@wp.kernel
def aug_rgb_to_hsv(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
    """Converts an integer RGB tuple (value range from 0 to 255) to an HSV tuple"""

    i, j = wp.tid()

    r = int(data_in[i, j, 0])
    g = int(data_in[i, j, 1])
    b = int(data_in[i, j, 2])

    # Compute the H value by finding the maximum of the RGB values
    rgb_max = max(max(r, g), b)
    rgb_min = min(min(r, g), b)

    # Compute the value
    v = rgb_max

    if v == 0:
        h = int(0)
        s = int(0)

    # Compute the saturation value
    s = 255 * int(rgb_max - rgb_min) // v

    if s == 0:
        h = 0

    # Compute the Hue
    if rgb_max == r:
        h = 0 + 43 * (g - b) // (rgb_max - rgb_min)
    elif rgb_max == g:
        h = 85 + 43 * (b - r) // (rgb_max - rgb_min)
    else:  # rgb_max == B
        h = 171 + 43 * (r - g) // (rgb_max - rgb_min)

    data_out[i, j, 0] = wp.uint8(h)
    data_out[i, j, 1] = wp.uint8(s)
    data_out[i, j, 2] = wp.uint8(v)
    data_out[i, j, 3] = data_in[i, j, 3]


@wp.kernel
def aug_hsv_to_rgb(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
    i, j = wp.tid()

    h = int(data_in[i, j, 0])
    s = int(data_in[i, j, 1])
    v = int(data_in[i, j, 2])

    # Check if the color is Grayscale
    if s == 0:
        r = v
        g = v
        b = v

    # Make hue 0-5
    region = h // 43

    # Find remainder part, make it from 0-255
    remainder = (h - (region * 43)) * 6

    # Calculate temp vars, doing integer multiplication
    p = (v * (255 - s)) // 256  # >> 8
    q = (v * (255 - ((s * remainder) // 256))) // 256
    t = (v * (255 - ((s * (255 - remainder)) // 256))) // 256

    # Assign temp vars based on color cone region
    if region == 0:
        r = v
        g = t
        b = p

    elif region == 1:
        r = q
        g = v
        b = p

    elif region == 2:
        r = p
        g = v
        b = t

    elif region == 3:
        r = p
        g = q
        b = v

    elif region == 4:
        r = t
        g = p
        b = v

    else:
        r = v
        g = p
        b = q

    data_out[i, j, 0] = wp.uint8(r)
    data_out[i, j, 1] = wp.uint8(g)
    data_out[i, j, 2] = wp.uint8(b)
    data_out[i, j, 3] = data_in[i, j, 3]


@wp.kernel
def aug_glass_blur(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), seed: int, delta: int):

    i, j = wp.tid()
    height = data_in.shape[0]
    width = data_in.shape[1]

    pixel_id = i * height + j

    state_x = wp.rand_init(seed, pixel_id)
    state_y = wp.rand_init(seed, pixel_id + (height * width))
    dx = wp.randi(state_x, -delta, delta)
    dy = wp.randi(state_y, -delta, delta)

    i_new = min(max(i + dx, 0), height - 1)
    j_new = min(max(j + dy, 0), width - 1)

    data_out[i, j, 0] = data_in[i_new, j_new, 0]
    data_out[i, j, 1] = data_in[i_new, j_new, 1]
    data_out[i, j, 2] = data_in[i_new, j_new, 2]
    data_out[i, j, 3] = data_in[i, j, 3]


@wp.kernel
def colorize_depth(
    data_in: wp.array2d(dtype=wp.float32), data_out: wp.array3d(dtype=wp.uint8), near: float, far: float
):
    """Apply colorization to depth data.

    Args:
        distance_data: Input depth data (H,W)
        output: Output colorized depth image (H,W,3)
        near: Minimum depth value to consider
        far: Maximum depth value to consider
    """
    i, j = wp.tid()

    # Get the depth value
    depth = data_in[i, j]

    # Skip invalid values
    if depth != wp.inf and depth != -wp.inf:  # noqa: PLR1714
        # Clip depth to range [near, far]
        clipped_depth = wp.clamp(depth, near, far) + 1e-5

        # Apply log normalization
        normalized = (wp.log(clipped_depth) - wp.log(near)) / (wp.log(far) - wp.log(near))

        # Invert and scale to 0-255 range
        color_value = wp.uint8((1.0 - normalized) * 255.0)

        # Set RGB channels to the same value (grayscale)
        data_out[i, j, 0] = color_value
        data_out[i, j, 1] = color_value
        data_out[i, j, 2] = color_value
    else:
        # For invalid depth values, set to black
        data_out[i, j, 0] = wp.uint8(0)
        data_out[i, j, 1] = wp.uint8(0)
        data_out[i, j, 2] = wp.uint8(0)
    # Set alpha channel to 0
    data_out[i, j, 3] = wp.uint8(255)


@wp.kernel
def colorize_normals(data_in: wp.array3d(dtype=wp.float32), data_out: wp.array3d(dtype=wp.uint8)):
    i, j = wp.tid()
    normal = data_in[i, j]
    if normal[0] == 0.0 and normal[1] == 0.0 and normal[2] == 0.0:
        data_out[i, j, 0] = wp.uint8(0)
        data_out[i, j, 1] = wp.uint8(0)
        data_out[i, j, 2] = wp.uint8(0)
    else:
        data_out[i, j, 0] = wp.uint8((0.5 + normal[0] * 0.5) * 255.0)
        data_out[i, j, 1] = wp.uint8((0.5 + normal[1] * 0.5) * 255.0)
        data_out[i, j, 2] = wp.uint8((0.5 + normal[2] * 0.5) * 255.0)
    data_out[i, j, 3] = wp.uint8(255)


@wp.kernel
def sobel_edges(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
    """Apply Sobel edge detection to an image.

    The Sobel operator calculates the gradient of the image intensity at each pixel,
    giving the direction of the largest increase from light to dark and the rate of
    change in that direction.

    Args:
        data_in: Input RGBA image
        data_out: Output RGBA image with detected edges
    """
    i, j = wp.tid()
    height = data_in.shape[0]
    width = data_in.shape[1]

    # Skip border pixels
    if 0 < i < height - 1 and 0 < j < width - 1:
        # Horizontal Sobel filter [-1, 0, 1; -2, 0, 2; -1, 0, 1]
        gx = 0.0
        # Vertical Sobel filter [-1, -2, -1; 0, 0, 0; 1, 2, 1]
        gy = 0.0

        # Apply filters to grayscale values
        for c in range(3):  # Process RGB channels
            # Horizontal gradient
            gx += (
                wp.float(data_in[i - 1, j - 1, c]) * -1.0
                + wp.float(data_in[i - 1, j + 1, c]) * 1.0
                + wp.float(data_in[i, j - 1, c]) * -2.0
                + wp.float(data_in[i, j + 1, c]) * 2.0
                + wp.float(data_in[i + 1, j - 1, c]) * -1.0
                + wp.float(data_in[i + 1, j + 1, c]) * 1.0
            )

            # Vertical gradient
            gy += (
                wp.float(data_in[i - 1, j - 1, c]) * -1.0
                + wp.float(data_in[i - 1, j, c]) * -2.0
                + wp.float(data_in[i - 1, j + 1, c]) * -1.0
                + wp.float(data_in[i + 1, j - 1, c]) * 1.0
                + wp.float(data_in[i + 1, j, c]) * 2.0
                + wp.float(data_in[i + 1, j + 1, c]) * 1.0
            )

        # Average the gradients across channels
        gx /= 3.0
        gy /= 3.0

        # Calculate gradient magnitude
        magnitude = wp.sqrt(gx * gx + gy * gy)

        # Normalize and threshold
        edge_val = wp.uint8(wp.clamp(magnitude / 4.0, 0.0, 255.0))

        data_out[i, j, 0] = edge_val
        data_out[i, j, 1] = edge_val
        data_out[i, j, 2] = edge_val
    else:
        # Set border pixels to black
        data_out[i, j, 0] = wp.uint8(0)
        data_out[i, j, 1] = wp.uint8(0)
        data_out[i, j, 2] = wp.uint8(0)
    data_out[i, j, 3] = wp.uint8(255)  # Set alpha to opaque


augmentation_descriptions = [
    {"name": "rgba_to_rgb", "augmentation": Augmentation.from_function(rgba_to_rgb)},  # backwards compatibility
    {
        "name": "RgbaToRgb",
        "augmentation": Augmentation.from_function(
            rgba_to_rgb,
            documentation="""Remove the alpha (last) channel from an RGBA image

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 3): RGB image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_rgba_to_rgb():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment("RgbaToRgb")
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_rgba_to_rgb())
                """,
        ),
    },
    {
        "name": "ColorizeDepth",
        "augmentation": Augmentation.from_function(
            colorize_depth,
            near=0.1,
            far=100.0,
            data_out_shape=(-1, -1, 4),
            documentation="""Colorize depth data.

                Distance to camera is inverted and normalized to the range [0, 255] in greyscale RGB.

                **Input Format**
                - (height, width): Depth data

                **Output Format**
                - (height, width, 3): RGB image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_colorize_depth():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("distance_to_camera", device="cuda").augment(
                            "ColorizeDepth",
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 3)

                    asyncio.ensure_future(test_colorize_depth())
                """,
        ),
    },
    {
        "name": "ColorizeNormals",
        "augmentation": Augmentation.from_function(
            colorize_normals,
            data_out_shape=(-1, -1, 4),
            documentation="""Colorize normal data.

                **Input Format**
                - (height, width, 3): Normal data

                **Output Format**
                - (height, width, 3): RGB image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_colorize_normals():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("normals", device="cuda").augment("ColorizeNormals")
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 3)

                    asyncio.ensure_future(test_colorize_normals())
                """,
        ),
    },
    {
        "name": "Sobel",
        "augmentation": Augmentation.from_function(
            sobel_edges,
            data_out_shape=(-1, -1, 4),
            documentation="""Apply Sobel edge detection to an image.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image with detected edges

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_sobel_edges():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment("Sobel")
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_sobel_edges())
                """,
        ),
    },
    {
        "name": "AdjustSigmoid",
        "augmentation": Augmentation.from_function(
            aug_adjust_sigmoid,
            cutoff=0.5,
            gain=1.0,
            documentation=r"""Perform sigmoid correction on an image

            A form of contrast adjustment, transforms each pixel (normalized to be between 0 and 1) of an image
            according to the equation :math:`Out = ({1 + e^{gain \cdot (cutoff - In)}})^{-1}` [1]_ [2]_.

                **Initialization Parameters**

                * cutoff (float): Shifts the characteristic sigmoid curve horizontally
                * gain (float): Multiplier in the exponent's power of sigmoid function.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_adjust_sigmoid():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "AdjustSigmoid", cutoff=0.2, gain=20.0
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_adjust_sigmoid())

                **References**

                .. [1] Gustav J. Braun, "Image Lightness Rescaling Using Sigmoidal Contrast
                    Enhancement Functions",
                    http://markfairchild.org/PDFs/PAP07.pdf
                .. [2] Stéfan van der Walt, Johannes L. Schönberger, Juan Nunez-Iglesias, François Boulogne,
                    Joshua D. Warner, Neil Yager, Emmanuelle Gouillart, Tony Yu and the scikit-image contributors.
                    scikit-image: Image processing in Python. PeerJ 2:e453 (2014),
                    https://doi.org/10.7717/peerj.453
                """,
        ),
    },
    {
        "name": "Brightness",
        "augmentation": Augmentation.from_function(
            aug_brightness,
            brightness_factor=2.0,
            documentation="""Modify the brightness of an image.

                **Initialization Parameters**

                * brightness_factor (float): value between ``[-100, 100]`` that determines the brightness modification.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_brightness():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "Brightness",
                            brightness_factor=5.0
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_brightness())
                """,
        ),
    },
    {
        "name": "SpeckleNoise",
        "augmentation": Augmentation.from_function(
            aug_speckle_noise,
            sigma=0.5,
            documentation="""Add speckle noise to an RGBA image

                Provided a noise scaling factor ``sigma``, add speckle noise to each pixel of the image.

                **Initialization Parameters**

                * sigma (float): determines the amount of noise to add. A larger value produces a noisier image.
                * seed (int): Seed to use as initialization for the pseudo-random number generator. Seed is expected to
                  be a non-negative integer.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_speckle_noise():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get(
                            "LdrColor",
                            device="cuda"
                        ).augment("SpeckleNoise", sigma=0.2)
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_speckle_noise())
                """,
        ),
    },
    {
        "name": "ShotNoise",
        "augmentation": Augmentation.from_function(
            aug_shot_noise,
            sigma=0.5,
            documentation="""Add shot noise to an RGBA image

                Provided a noise scaling factor ``sigma``, add shot noise to each pixel of the image.

                **Initialization Parameters**

                * sigma (float): Determines the amount of noise to add. A larger value produces a noisier image.
                * seed (int): Seed to use as initialization for the pseudo-random number generator. Seed is expected to
                  be a non-negative integer.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_shot_noise():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment("ShotNoise", sigma=0.2)
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_shot_noise())
                """,
        ),
    },
    {
        "name": "RgbToHsv",
        "augmentation": Augmentation.from_function(
            aug_rgb_to_hsv,
            documentation="""Modifies an RGB image to HSV

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_rgb_to_hsv():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment("HsvToRgb")
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_rgb_to_hsv())
                """,
        ),
    },
    {
        "name": "HsvToRgb",
        "augmentation": Augmentation.from_function(
            aug_hsv_to_rgb,
            documentation="""Modifies an HSV image to RGB

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_hsv_to_rgb():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment_compose(
                            ["RgbToHsv", "HsvToRgb"]
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_hsv_to_rgb())
                """,
        ),
    },
    {
        "name": "GlassBlur",
        "augmentation": Augmentation.from_function(
            aug_glass_blur,
            delta=4,
            documentation="""Applies a Glass Blur augmentation to an RGBA image.

                To simulate glass blur, each pixel is swapped with another sampled from within a window whose size is
                determined by the ``delta`` parameter.

                **Initialization Parameters**

                * delta (int): determines the maximum window size from which to sample a pixel. A larger value produces
                  a blurrier effect.
                * seed (int): Seed to use as initialization for the pseudo-random number generator. Seed is expected to
                  be a non-negative integer.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_glass_blur():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment("GlassBlur", delta=5)
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data.shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_glass_blur())
            """,
        ),
    },
    # Register node based augmentation
    {
        "name": "BackgroundRand",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugBgRandExp",
            documentation="""Randomize and apply a background image.

                Given a folder path, valid images are randomly selected and applied as the background to the current
                image.

                **Initialization Parameters**

                * folderpath (str): Path to directory containing images to be used as backgrounds.
                * seed (int): Seed to use as initialization for the pseudo-random number generator for the sampler
                  controlling image selection. Seed is expected to be a non-negative integer.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_background_rand():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "BackgroundRand",
                            folderpath=rep.example.TEXTURES_DIR
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([1., 0., 0., 0., 1., 0., 0., 0., 1.])}

                    asyncio.ensure_future(test_background_rand())
            """,
        ),
    },
    {
        "name": "Contrast",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugContrastExp",
            contrastFactor=0.5,
            documentation="""Adjust the contrast of an image.

                **Initialization Parameters**

                * contrastFactor (float): Positive float value specifying how much to adjust the contrast. A value of
                  ``0.0`` produces a solid grey image, ``1.0`` results in the original input image and ``2.0`` increases
                  the contrast by a factor of ``2.0``.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_adjust_contrast():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "Contrast",
                            contrastFactor=1.5
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([1., 0., 0., 0., 1., 0., 0., 0., 1.])}

                    asyncio.ensure_future(test_adjust_contrast())
            """,
        ),
    },
    {
        "name": "Conv2d",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugConv2dExp",
            alpha=0.7,
            documentation="""Apply a 2D convolution to an image

                **Initialization Parameters**

                * kernel (float[]): The kernel to convolve with an image. Kernel is provided as a flattened array of
                  size ``[N * N]`` where ``N`` is the kernel size.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import numpy as np
                    import omni.replicator.core as rep

                    async def test_conv2d():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))

                        # Create a gaussian blur kernel
                        gaussian_blur = np.array([
                            [0.0625, 0.1250, 0.0625],
                            [0.1250, 0.2500, 0.1250],
                            [0.0625, 0.1250, 0.0625],
                        ])

                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "Conv2d", kernel=gaussian_blur
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([1., 0., 0., 0., 1., 0., 0., 0., 1.])}

                    asyncio.ensure_future(test_conv2d())
            """,
        ),
    },
    {
        "name": "CropResize",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugCropResizeExp",
            cropFactor=0.5,
            offsetFactor=(0.0, 0.0),
            documentation="""Crop, resize and translate an image.

                **Initialization Parameters**

                * cropFactor (float): Value between >0.0 and 1.0 specifying the amount of the image to crop. A value of
                  ``1.0`` indicates no crop and a value of `0.5` will crop the image by half.
                * offsetFactor (float[2]): Value between `(-1.0 and 1.0)` indicating the translation offset factor in
                  ``(vertical, horizontal)`` directions. A value of ``(-1.0, -1.0)`` will translate the cropped image to
                  the bottom-most and left-most, and a value of ``(1.0, 1.0)`` to the top-most and right-most. Note that
                  if ``cropFactor`` is set to ``1.0``, no translation is possible.
                * seed (int): Seed to use as initialization for the pseudo-random number generator for the sampler
                  controlling image selection. Seed is expected to be a non-negative integer.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_crop_resize():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "CropResize",
                            cropFactor=0.5,
                            offset_factor=(-0.2, 0.2)
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([   2.,    0.,  320.,    0.,    2., -720.,    0.,    0.,    1.])}

                    asyncio.ensure_future(test_crop_resize())
            """,
        ),
    },
    {
        "name": "CutMix",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugCutMixExp",
            documentation="""Randomly apply a rectangular patch from another image onto the input image.

                The augmentation takes in a random rectangular patch from another image and superimposes it on the input
                image. The rectangular patch is encoded in a binary mask where the pixels belonging to the rectangle
                have a mask value of 1 and 0 otherwise.

                **Initialization Parameters**

                * folderpath (str): Path to directory containing images to be used as patches.
                * seed (int): Seed to use as initialization for the pseudo-random number generator for the sampler
                  controlling image selection. Seed is expected to be a non-negative integer.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_cut_mix():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "CutMix",
                            folderpath=rep.example.TEXTURES_DIR
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([1., 0., 0., 0., 1., 0., 0., 0., 1.])}

                    asyncio.ensure_future(test_cut_mix())
            """,
        ),
    },
    {
        "name": "ImageBlend",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugImgBlendExp",
            blendFactor=0.5,
            documentation="""Blend an input image with a sampled blend image.

                **Initialization Parameters**

                * blendFactor (float): Blend amount. A value of ``0.0`` will return the original image and a value of
                  ``1.0`` will return the blend image.
                * folderpath (str): Path to directory containing images to be used as patches.
                * seed (int): Seed to use as initialization for the pseudo-random number generator for the sampler
                  controlling image selection. Seed is expected to be a non-negative integer.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_image_blend():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "ImageBlend",
                            blendFactor=0.2,
                            folderpath=rep.example.TEXTURES_DIR
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([1., 0., 0., 0., 1., 0., 0., 0., 1.])}

                    asyncio.ensure_future(test_image_blend())
            """,
        ),
    },
    {
        "name": "MotionBlur",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugMotionBlurExp",
            motionAngle=45.0,
            strength=0.7,
            kernelSize=11,
            documentation="""Apply a motion blur effect to an input image.

                **Initialization Parameters**

                * motionAngle (float): Angle in degrees where ``0`` indicates motion towards the left, ``90`` towards
                  the bottom, and ``270`` towards the top.
                * strength (float): Motion Blur strength from ``-1`` to ``1``.
                * kernelSize (int): Size of the conv kernel which controls the size of blur that will be produced.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_motion_blur():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "MotionBlur",
                            motionAngle=45.0,
                            strength=0.8,
                            kernelSize=25
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([1., 0., 0., 0., 1., 0., 0., 0., 1.])}

                    asyncio.ensure_future(test_motion_blur())
            """,
        ),
    },
    {
        "name": "Pixellate",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugPixellateExp",
            kernelSize=8,
            documentation="""Pixellate an input image.

                **Initialization Parameters**

                * kernelSize (int): Size of the conv kernel which controls how many original pixels get consolidated
                  into a single larger pixel.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_pixellate():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "Pixellate",
                            kernelSize=25
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([1., 0., 0., 0., 1., 0., 0., 0., 1.])}

                    asyncio.ensure_future(test_pixellate())
            """,
        ),
    },
    {
        "name": "Rotate",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugRotateExp",
            rotation=45.0,
            documentation="""Rotate an input image.

                **Initialization Parameters**

                * rotation (float): Clockwise image rotation in degrees. A value of ``0.0`` corresponds to no rotation.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep


                    async def test_rotate():
                        camera = rep.create.camera()
                        rp = rep.create.render_product(camera, (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment("Rotate", rotation=90)
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)
                        print(data["info"])
                        # {'xform': array([ 0.0,  1.0,  80.0, -1.0, 0.0,  559.0,  0.0,  0.0, 1.0])}

                        # Test bounding box transform based on rotation xform
                        # Add a labelled sphere
                        with rep.create.sphere(semantics=[("class", "sphere")]):
                            rep.modify.pose_camera_relative(
                                camera=camera,
                                render_product=rp,
                                distance=700,
                                horizontal_location=0.2,
                                vertical_location=0.4
                            )

                        # Add a labelled cone
                        with rep.create.cone(semantics=[("class", "cone")]):
                            rep.modify.pose_camera_relative(
                                camera=camera,
                                render_product=rp,
                                distance=500,
                                horizontal_location=-0.2,
                                vertical_location=0.1,
                            )

                        # Add bounding box annotator
                        bbox_2d = rep.annotators.get("bounding_box_2d_tight_fast")
                        bbox_2d.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        xform = data["info"]["xform"]
                        bbox_data = bbox_2d.get_data()["data"]

                        visualization = rep.tools.colorize_bbox_2d(
                            data["data"].numpy(),
                            bbox_data,
                            xform,
                            draw_rotated_boxes=True,
                        )
                        from PIL import Image
                        Image.fromarray(visualization).save("rotated_bbox.png")

                    asyncio.ensure_future(test_rotate())
            """,
        ),
    },
    {
        "name": "Canny",
        "augmentation": Augmentation.from_node(
            "omni.replicator.core.AugCanny",
            thresholdLow=50,
            thresholdHigh=100,
            documentation="""Apply the Canny edge detection algorithm to an input image.

                **Initialization Parameters**
                * thresholdLow (float): Low threshold for the hysteresis procedure.
                * thresholdHigh (float): High threshold for the hysteresis procedure.

                **Input Format**
                - (height, width, 4): RGBA image

                **Output Format**
                - (height, width, 4): RGBA image with detected edges

                **Example**

                .. code:: python

                    import asyncio
                    import omni.replicator.core as rep

                    async def test_canny():
                        rp = rep.create.render_product(rep.create.camera(), (640, 480))
                        augmented_anno = rep.annotators.get("LdrColor", device="cuda").augment(
                            "Canny",
                            thresholdLow=100,
                            thresholdHigh=200
                        )
                        augmented_anno.attach(rp)

                        await rep.orchestrator.step_async()

                        data = augmented_anno.get_data()
                        print(data["data"].shape)
                        # (480, 640, 4)

                    asyncio.ensure_future(test_canny())
            """,
        ),
    },
]


def register_augmentations():
    for augmentation_description in augmentation_descriptions:
        register_augmentation(**augmentation_description)
