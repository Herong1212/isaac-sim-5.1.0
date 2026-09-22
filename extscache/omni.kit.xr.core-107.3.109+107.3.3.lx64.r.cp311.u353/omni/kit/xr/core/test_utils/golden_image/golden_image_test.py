# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import asyncio
import os
import shutil
from typing import List, Optional, Sequence, Tuple

import carb
import omni.kit.app
import omni.kit.test
import omni.kit.xr.core.imagecomparison
import omni.usd
from omni.kit.xr.core import XRCore, XRCoreEventType

from ..tests_directories import (
    ensure_directory_exist,
    get_golden_image_source_directory,
    get_test_ext_output_directory,
    get_test_output_directory,
)
from ..utils import get_ext_id_by_file_name, get_test_name_and_file_name

SUFFIX_GOLDEN = ".golden"
SUFFIX_GENERATED = ".generated"
SUFFIX_DIFF = ".diff"


def compare_test_image(
    output_image_name: str, threshold: float, golden_image_source_extension: Optional[str] = None
) -> bool:
    """
    Compare set of images
    """

    carb.log_info(f"[XR] Comparing golden image: '{output_image_name}'")

    def remove_file_if_exist(file_path: str) -> None:
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception as exception:
                carb.log_error(f"Failed to remove file '{file_path}'  exception: {str(exception)}")

    carb_settings = carb.settings.get_settings()
    golden_directory = str(get_golden_image_source_directory(golden_image_source_extension))
    test_output_directory = str(get_test_output_directory())
    out_generated_image_path = test_output_directory + "/" + output_image_name + SUFFIX_GENERATED + ".png"
    out_diff_image_path = test_output_directory + "/" + output_image_name + SUFFIX_DIFF + ".png"
    in_golden_image_path = golden_directory + "/" + output_image_name + SUFFIX_GOLDEN + ".png"

    desc = omni.kit.xr.core.imagecomparison.XRImageComparisonDesc(
        out_generated_image_path, in_golden_image_path, out_diff_image_path
    )

    result = omni.kit.xr.core.imagecomparison.xr_compare_output_image_to_golden_image(desc, threshold)

    if not result.images_equal:
        carb.log_warn(
            f"[XR] Comparison result: {output_image_name} error: {result.result_value} threshold: {result.threshold}"
        )
        carb.log_warn(f"[XR] Comparison message: {result.message}")
    else:
        carb.log_info(
            f"[XR] Comparison result: {output_image_name} error: {result.result_value} threshold: {result.threshold}"
        )

    # Always include the golden image in test outputs to make comparison from Gitlab artifacts easier
    try:
        out_golden_image_path = test_output_directory + "/" + output_image_name + SUFFIX_GOLDEN + ".png"
        shutil.copyfile(in_golden_image_path, out_golden_image_path)
    except Exception as exception:
        carb.log_warn(
            f"[XR] Could not copy golden image to outputs, from path '{in_golden_image_path}' to '{out_golden_image_path}'. Exception: {exception}"
        )

    ext_output_dir = get_test_ext_output_directory()
    failed_tests_directory = os.path.join(str(ext_output_dir), "failed_golden_images", "current_run")
    failed_generated_image_path = failed_tests_directory + "/" + output_image_name + SUFFIX_GENERATED + ".png"
    failed_golden_image_path = failed_tests_directory + "/" + output_image_name + SUFFIX_GOLDEN + ".png"
    failed_diff_image_path = failed_tests_directory + "/" + output_image_name + SUFFIX_DIFF + ".png"

    if result.images_equal:
        # Deal with images from previous runs (keep them or remove them)
        do_not_delete_prev_failures = carb_settings.get("/xr/test/doNotDeletePrevFailures")
        if do_not_delete_prev_failures is not True:
            remove_file_if_exist(failed_generated_image_path)
            remove_file_if_exist(failed_golden_image_path)
            remove_file_if_exist(failed_diff_image_path)
    else:
        # Copy the failed images to "{omni_data}/_testoutput/failed_golden_images/current_run" directory
        # This is useful for comparing images after multiple runs
        ensure_directory_exist(failed_tests_directory)
        shutil.copyfile(in_golden_image_path, failed_golden_image_path)
        shutil.copyfile(out_generated_image_path, failed_generated_image_path)
        shutil.copyfile(out_diff_image_path, failed_diff_image_path)

        carb.log_warn(f"[XR] Image comparision failed: {result.message}")

    return result.images_equal


class GoldenImageTest:
    def __init__(self, disable_comparison) -> None:
        self._disable_comparison = disable_comparison

        if not self._image_capturer:  # type: ignore[attr-defined]
            carb.log_error("[XR] Image capturer cannot be None")
            return

    def get_frames_to_wait(self) -> int:
        if self._disable_comparison:
            return 30
        else:
            return 8

    def prepare_paths(self, golden_image_name: str, module_name: Optional[str]) -> Tuple[List[str], List[str]]:
        output_path = str(get_test_output_directory())
        file_names = []
        file_paths = []

        image_suffix = SUFFIX_GENERATED
        if self._disable_comparison:
            image_suffix = SUFFIX_GOLDEN

        for image_type in self.image_types:  # type: ignore[attr-defined]
            file_path = get_test_name_and_file_name(golden_image_name, module_name, image_type)
            file_names.append(file_path)
            file_paths.append(output_path + "/" + file_path + image_suffix)

        return (file_paths, file_names)

    def capture_images(self, golden_image_name: str, file_paths: List[str]) -> None:
        self._image_capturer.capture_images(golden_image_name, file_paths)  # type: ignore[attr-defined]

    async def capture_and_compare_output_async(
        self, golden_image_name: str, threshold: float, module_name: Optional[str]
    ) -> bool:

        carb.log_info(
            f"[XR] Capturing golden image: '{golden_image_name}', comparison disabled: '{self._disable_comparison}'"
        )

        file_paths, file_names = self.prepare_paths(golden_image_name, module_name)
        if asyncio.iscoroutinefunction(self._image_capturer.capture_images):  # type: ignore[attr-defined]
            await self._image_capturer.capture_images(file_paths)  # type: ignore[attr-defined]
        else:
            self.capture_images(golden_image_name, file_paths)

        await self.wait_for_images_async(file_paths)

        return self.compare_all_test_images(file_names, threshold, module_name)

    def compare_all_test_images(self, file_names: List[str], threshold: float, module_name: Optional[str]) -> bool:
        result = True
        if not self._disable_comparison:
            golden_image_source_extension = get_ext_id_by_file_name(module_name)
            for file_name in file_names:
                local_result = compare_test_image(file_name, threshold, golden_image_source_extension)
                result = result and local_result

        return result

    async def wait_for_images_async(self, paths: Sequence[str]) -> bool:
        number_of_captures = len(paths)
        found = []

        for idx in range(number_of_captures):
            full_path = paths[idx] + ".png"
            carb.log_info(f"[XR] Waiting for golden image: '{full_path}'")

        for idx in range(number_of_captures):
            found.append(False)

        max_wait = 50
        wait_count = 0
        found_all = False

        while not found_all and wait_count < max_wait:
            await self.wait_pre_sync_async()

            found_all = True
            for idx in range(number_of_captures):
                full_path = paths[idx] + ".png"
                if found[idx] is False:
                    if os.path.isfile(full_path):
                        found[idx] = True
                        carb.log_info(f"[XR] Found golden image: '{full_path}'")
                    else:
                        found_all = False

            wait_count = wait_count + 1

        if not found_all:
            carb.log_error("[XR] Failed to find all the captured images in the allotted time window")
            for idx in range(number_of_captures):
                if not found[idx]:
                    full_path = paths[idx] + ".png"
                    carb.log_error(f"[XR] Failed to generate golden image: {full_path}")

        return found_all

    async def wait_pre_sync_async(self, count: int = 1) -> None:
        """
        Wait for the pre_sync callback in XRCore

        Args:
            count: number of frames to wait
        """

        future: asyncio.Future = asyncio.Future()
        cur_count = 0
        target_count = count

        def on_pre_sync(ev: carb.events.IEvent):
            nonlocal cur_count
            cur_count = cur_count + 1
            if cur_count == target_count:
                future.set_result(True)

        sub_pre_sync = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.pre_sync_update, on_pre_sync, name="Pre Sync", order=-1)
        )

        await future
        sub_pre_sync = None  # noqa: F841

        return
