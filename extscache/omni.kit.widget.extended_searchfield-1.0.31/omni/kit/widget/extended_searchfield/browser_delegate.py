# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb


class BrowserDelegate:
    @property
    def current_directory(self) -> str:
        pass

    @current_directory.setter
    def current_directory(self, path: str):
        pass


class ContentBrowserDelegate(BrowserDelegate):
    @property
    def current_directory(self) -> str:
        try:
            from omni.kit.window.content_browser import get_content_window

            return get_content_window().get_current_directory()
        except ImportError:
            carb.log_warn("Unable to get content window.")
            return None

    @current_directory.setter
    def current_directory(self, path: str):
        try:
            from omni.kit.window.content_browser import get_content_window

            get_content_window().navigate_to(path)
        except ImportError:
            carb.log_warn("Unable to get content window.")
