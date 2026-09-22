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

import os
from typing import Sequence

import carb
from omni.kit.xr.core import XRCore


class ViewportImageCapturer:
    def __init__(self, viewport_indices: Sequence[str]) -> None:

        self.viewport_indices: Sequence = viewport_indices

        if not self.viewport_indices or len(self.viewport_indices) == 0:
            carb.log_error("ViewportImageCapturer needs to have viewport_indices not None and not empty")
            return

    def remove_images(self, paths: Sequence[str]):
        for path in paths:
            full_path = path + ".png"
            carb.log_info(f"[XR] Trying to remove file: '{full_path}'")
            # Check if the path is a file (not a directory)
            if os.path.isfile(full_path):
                try:
                    # Remove the file
                    os.remove(full_path)
                except Exception:
                    carb.log_error(f"[XR] There was an exception on removing file: '{full_path}'")

            if os.path.isfile(full_path):
                carb.log_error(f"[XR] Failed to remove file: '{full_path}'")

    def capture_images(self, golden_image_name: str, paths: Sequence[str]) -> None:
        self.capture_viewport_images(golden_image_name, paths, self.viewport_indices)

    def capture_viewport_images(self, golden_image_name: str, paths: Sequence[str], viewport_indices: Sequence[int]):

        self.remove_images(paths)
        carb.log_info(f"Generating golden image: '{golden_image_name}'")

        if not golden_image_name:
            carb.log_error("golden_image name cannot be None")
            return

        number_of_captures = len(paths)

        try:
            for idx in range(number_of_captures):
                XRCore.get_singleton().schedule_capture_viewport_frame(paths[idx], viewport_id=viewport_indices[idx])
        except Exception as exception:
            carb.log_error(f"Failed to capture golden image: '{golden_image_name}' exception: {str(exception)}")
