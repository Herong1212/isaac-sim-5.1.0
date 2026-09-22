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

from .golden_image_test import GoldenImageTest
from .viewport_image_capture import ViewportImageCapturer


class ViewportGoldenImageTest(GoldenImageTest):
    def __init__(self, disable_comparison) -> None:
        self.image_types = ["viewport"]
        self.viewport_indices: list = [0]
        self._image_capturer = ViewportImageCapturer(self.viewport_indices)

        super().__init__(disable_comparison)
