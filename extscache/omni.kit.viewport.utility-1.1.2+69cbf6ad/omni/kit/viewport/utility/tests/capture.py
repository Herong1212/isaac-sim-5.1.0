## Copyright (c) 2022-2025, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = [
    'DEFAULT_THRESHOLD',
    'capture_viewport_and_compare'
]

import carb
import omni.kit.app
import omni.renderer_capture

from omni.kit.test_helpers_gfx import compare, CompareError
from omni.kit.test.teamcity import teamcity_log_fail, teamcity_publish_image_artifact

import pathlib
import traceback

DEFAULT_THRESHOLD = 10.0


def viewport_capture(image_name: str, output_img_dir: str, viewport=None, use_log: bool = True,
    frame_to_capture: int = None
):
    """
    Captures a Viewport texture into a file.

    Args:
        image_name: the image name of the image and golden image.
        output_img_dir: the directory path that the capture will be saved to.
        golden_img_dir: the directory path that stores the golden image. Leave it to None to use default dir.
        use_log: whether to log the comparison image path
        frame_to_capture: The SWH frame number to capture. If not provided the next published frame will be captured.
    """
    from omni.kit.viewport.utility import get_active_viewport, capture_viewport_to_file

    image1 = str(pathlib.Path(output_img_dir).joinpath(image_name))
    if use_log:
        carb.log_info(f"[tests.compare] Capturing {image1}")

    if viewport is None:
        viewport = get_active_viewport()

    return capture_viewport_to_file(viewport, file_path=image1, frame_to_capture=frame_to_capture)


def finalize_capture_and_compare(image_name: str, output_img_dir: str, golden_img_dir: str, threshold: float = DEFAULT_THRESHOLD):
    """
    Finalizes capture and compares it with the golden image.

    Args:
        image_name: the image name of the image and golden image.
        threshold: the max threshold to collect TC artifacts.
        output_img_dir: the directory path that the capture will be saved to.
        golden_img_dir: the directory path that stores the golden image. Leave it to None to use default dir.

    Returns:
        A value that indicates the maximum difference between pixels. 0 is no difference
        in the range [0-255].
    """
    image1 = pathlib.Path(output_img_dir).joinpath(image_name)
    image2 = pathlib.Path(golden_img_dir).joinpath(image_name)
    image_diffmap_name = f"{pathlib.Path(image_name).stem}.diffmap.png"

    image_diffmap = pathlib.Path(output_img_dir).joinpath(image_diffmap_name)

    carb.log_info(f"[tests.compare] Comparing {image1} to {image2}")

    try:
        diff = compare(image1, image2, image_diffmap)
        if diff >= threshold:
            # TODO pass specific test name here instead of omni.rtx.tests
            teamcity_log_fail("omni.rtx.tests", f"Reference image {image_name} differ from golden.")
            teamcity_publish_image_artifact(image2, "golden", "Reference")
            teamcity_publish_image_artifact(image1, "results", "Generated")
            teamcity_publish_image_artifact(image_diffmap, "results", "Diff")

        return diff
    except CompareError as e:
        carb.log_error(f"[tests.compare] Failed to compare images for {image_name}. Error: {e}")
        exc = traceback.format_exc()
        carb.log_error(f"[tests.compare] Traceback:\n{exc}")


async def capture_viewport_and_wait(image_name: str, output_img_dir: str, viewport = None, frame_to_capture: int = None):
    await viewport_capture(image_name, output_img_dir, viewport, frame_to_capture=frame_to_capture).wait_for_result(0)

    app = omni.kit.app.get_app()
    capure_iface = omni.renderer_capture.acquire_renderer_capture_interface()
    for i in range(3):
        capure_iface.wait_async_capture()
        await app.next_update_async()


async def capture_viewport_and_compare(
    image_name: str,
    output_img_dir: str,
    golden_img_dir: str,
    threshold: float = DEFAULT_THRESHOLD,
    viewport = None,
    test_caller: str = None,
    frame_to_capture: int = None
):
    """
    Captures frame and compares it with the golden image.

    Args:
        image_name: the image name of the image and golden image.
        golden_img_dir: the directory path that stores the golden image. Leave it to None to use default dir.
        threshold: the max threshold to collect TC artifacts.
        viewport: the viewport to capture or None for the active Viewport
        frame_to_capture: The SWH frame number to capture. If not provided the next published frame will be captured.

    Returns:
        A value that indicates the maximum difference between pixels. 0 is no difference
        in the range [0-255].
    """

    await capture_viewport_and_wait(image_name=image_name, output_img_dir=output_img_dir, viewport=viewport, frame_to_capture=frame_to_capture)

    diff = finalize_capture_and_compare(image_name=image_name, output_img_dir=output_img_dir, golden_img_dir=golden_img_dir, threshold=threshold)

    if diff is not None and diff < DEFAULT_THRESHOLD:
        return True, ''

    carb.log_warn(f"[{image_name}] the generated image has difference {diff}")

    if test_caller is None:
        import os.path
        test_caller = os.path.splitext(image_name)[0]

    return False, f"The image for test '{test_caller}' doesn't match the golden one. Difference of {diff} is is not less than threshold of {threshold}."
