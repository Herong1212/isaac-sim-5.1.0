## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
"""The utilities for image comparison"""
from pathlib import Path
import os
import platform
import carb
import carb.tokens
import sys
import traceback

import omni.kit.test
from omni.kit.test.teamcity import teamcity_publish_image_artifact


OUTPUTS_DIR = Path(omni.kit.test.get_test_output_path())
KIT_ROOT = Path(carb.tokens.get_tokens_interface().resolve("${kit}")).parent.parent.parent
GOLDEN_DIR = KIT_ROOT.joinpath("data/tests/omni.ui.tests")


def Singleton(class_):
    """
    A singleton decorator.

    TODO: It's also available in omni.kit.widget.stage. Do we have a utility extension where we can put the utilities
    like this?
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


class CompareError(Exception):
    pass


class CompareMetric:
    MEAN_ERROR = "mean_error"
    MEAN_ERROR_SQUARED = "mean_error_squared"
    PIXEL_COUNT = "pixel_count"


def compare(image1: Path, image2: Path, image_diffmap: Path, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR):
    """
    Compares two images and return a value that indicates the difference based on the metric used.
    Types of comparison: mean error (default), mean error squared, and pixel count.

    Mean Error (mean absolute error):
        Average pixel level for each channel in the image, return a number between [0, 255]
        This is the default method in UI compare tests - it gives a nice range of numbers.

    Mean Error Squared (mean squared error):
        Measures the average of the squares of the errors, return a number between [0, 1]
        This is the default method used in Kit Rendering, see `meanErrorSquaredMetric`

    Pixel Count:
        Return the number of pixels that are different

    It uses Pillow for image read.

    Args:
        image1, image2: images to compare
        image_diffmap: the difference map image will be saved if there is any difference between given images
        threshold: the threshold value (int or float)
        cmp_metric: comparison method
    """
    if not image1.exists():
        raise CompareError(f"File image1 {image1} does not exist")
    if not image2.exists():
        raise CompareError(f"File image2 {image2} does not exist")

    # OMFP-1891: Cease use of pip install
    if "PIL" not in sys.modules.keys():
        raise CompareError("Cannot import PIL from Pillow, image comparison failed.")

    from PIL import Image, ImageChops, ImageStat

    original = Image.open(str(image1))
    contrast = Image.open(str(image2))

    if original.size != contrast.size:
        raise CompareError(
            f"[omni.ui.test] Can't compare different resolutions\n\n"
            f"{image1} {original.size[0]}x{original.size[1]}\n"
            f"{image2} {contrast.size[0]}x{contrast.size[1]}\n\n"
            f"It's possible that your monitor DPI is not 100%.\n\n"
        )

    if original.mode != contrast.mode:
        raise CompareError(
            f"[omni.ui.test] Can't compare images with different mode (channels).\n\n"
            f"{image1} {original.mode}\n"
            f"{image2} {contrast.mode}\n\n"
        )

    img_diff = ImageChops.difference(original, contrast)
    stat = ImageStat.Stat(img_diff)

    if cmp_metric == CompareMetric.MEAN_ERROR:
        # Calculate average difference between two images
        diff = sum(stat.mean) / len(stat.mean)
    elif cmp_metric == CompareMetric.MEAN_ERROR_SQUARED:
        # Measure the average of the squares of the errors between two images
        # Errors are calculated from 0 to 255 (squared), divide by 255^2 to have a range between [0, 1]
        errors = [x / stat.count[i] for i, x in enumerate(stat.sum2)]
        diff = sum(errors) / len(stat.sum2) / 255**2
    elif cmp_metric == CompareMetric.PIXEL_COUNT:
        # Count of different pixels - on single channel image the value of getpixel is an int instead of a tuple
        if isinstance(img_diff.getpixel((0, 0)), int):
            diff = sum([img_diff.getpixel((j, i)) > 0 for i in range(img_diff.height) for j in range(img_diff.width)])
        else:
            diff = sum(
                [sum(img_diff.getpixel((j, i))) > 0 for i in range(img_diff.height) for j in range(img_diff.width)]
            )

    # only save image diff if needed (2 order of magnitude near threshold)
    if diff > 0 and threshold and diff > threshold / 100:
        # Images are different
        # Multiply image by 255
        img_diff = img_diff.convert("RGB").point(lambda i: min(i * 255, 255))
        img_diff.save(str(image_diffmap))

    return diff


async def capture_and_compare(
    image_name: str,
    threshold,
    golden_img_dir: Path = None,
    use_log: bool = True,
    cmp_metric=CompareMetric.MEAN_ERROR,
):
    """
    Captures frame and compares it with the golden image.

    Args:
        image_name: the image name of the image and golden image.
        threshold: the max threshold to collect TC artifacts.
        golden_img_dir: the directory path that stores the golden image. Leave it to None to use default dir.
        cmp_metric: comparison metric (mean error, mean error squared, pixel count)

    Returns:
        A diff value based on the comparison metric used.
    """

    if not golden_img_dir:
        golden_img_dir = GOLDEN_DIR

    image1 = OUTPUTS_DIR.joinpath(image_name)
    image2 = golden_img_dir.joinpath(image_name)
    image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image_name).stem}.diffmap.png")
    alt_image2 = golden_img_dir.joinpath(f"{platform.system().lower()}/{image_name}")
    if os.path.exists(alt_image2):
        image2 = alt_image2

    if use_log:
        carb.log_info(f"[omni.ui.tests.compare] Capturing {image1} and comparing with {image2}.")

    import omni.renderer_capture

    capture_next_frame = omni.renderer_capture.acquire_renderer_capture_interface().capture_next_frame_swapchain
    wait_async_capture = omni.renderer_capture.acquire_renderer_capture_interface().wait_async_capture

    try:
        os.remove(str(image1))
    except OSError:
        pass

    capture_next_frame(str(image1))

    tries = 10
    while tries > 0:
        await omni.kit.app.get_app().next_update_async()

        wait_async_capture()

        if os.path.isfile(str(image1)):
            break

        tries -= 1

    try:
        diff = compare(image1, image2, image_diffmap, threshold, cmp_metric)
        if diff >= threshold:
            golden_path = Path("golden").joinpath(OUTPUTS_DIR.name)
            results_path = Path("results").joinpath(OUTPUTS_DIR.name)
            teamcity_publish_image_artifact(image2, golden_path, "Reference")
            teamcity_publish_image_artifact(image1, results_path, "Generated")
            teamcity_publish_image_artifact(image_diffmap, results_path, "Diff")
        return diff
    except CompareError as e:
        carb.log_error(f"[omni.ui.tests.compare] Failed to compare images for {image_name}. Error: {e}")
        carb.log_error(f"[omni.ui.tests.compare] Traceback:\n{traceback.format_exc()}")
