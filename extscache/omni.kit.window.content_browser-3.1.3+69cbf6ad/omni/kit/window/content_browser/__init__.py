# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""A window extension for browsing filesystem, including Nucleus, content"""
__all__ = ["ContentBrowserExtension", "get_content_window", "ContentBrowser", "ContentBrowserWidget"]

FILE_TYPE_USD = 1
FILE_TYPE_IMAGE = 2
FILE_TYPE_SOUND = 3
FILE_TYPE_TEXT = 4
FILE_TYPE_VOLUME = 5

SETTING_ROOT = "/exts/omni.kit.window.content_browser/"
SETTING_PERSISTENT_ROOT = "/persistent" + SETTING_ROOT
SETTING_PERSISTENT_CURRENT_DIRECTORY = SETTING_PERSISTENT_ROOT + "current_directory"

from .extension import ContentBrowserExtension, ContentBrowser, get_instance, get_content_instance
from .window import ContentBrowserWindow
from .widget import ContentBrowserWidget


def get_content_window() -> ContentBrowser:
    """Returns the singleton instance of the content browser.

    Returns:
        ContentBrowser: The instance of the content browser  that allows browsing
        of the filesystem, including Nucleus content."""
    return get_content_instance()
