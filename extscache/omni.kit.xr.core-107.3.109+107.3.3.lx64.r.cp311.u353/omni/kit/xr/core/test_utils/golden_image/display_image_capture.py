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
from typing import Optional, Sequence, Tuple

import carb
from omni.kit.xr.core import XRCore


class DisplayImageCapturer:
    def __init__(
        self,
        display_names: Sequence[str],
        capture_source: Optional[str] = None,
        capture_output: str = "color",
        capture_depth_range: Tuple[float, float] = (0.1, 10.0),
    ) -> None:

        self.display_names = display_names
        self.capture_source = capture_source
        self.capture_output = capture_output
        self.capture_depth_range = capture_depth_range

        if not self.display_names:
            carb.log_error("[XR] DisplayImageCapturer needs to have display_names")
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

        carb.log_info(f"[XR] Generating golden image: '{golden_image_name}'")

        if not golden_image_name:
            carb.log_error("[XR] golden_image name cannot be None")
            return

        self.remove_images(paths)

        number_of_captures = len(paths)
        if len(self.display_names) != number_of_captures:
            carb.log_error("[XR] number paths, display_names needs to be the same")
            return

        try:
            for idx in range(number_of_captures):
                XRCore.get_singleton().schedule_capture_display_frame(
                    paths[idx],
                    display_name=self.display_names[idx],
                    capture_source=self.capture_source,
                    capture_output=self.capture_output,
                    capture_depth_range=self.capture_depth_range,
                )
        except Exception as exception:
            carb.log_error(f"[XR] Failed to capture golden image: '{golden_image_name}' exception: {str(exception)}")
