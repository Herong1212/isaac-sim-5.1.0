# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Collection of utility functions to manage the clipboard.
"""
from typing import List
from .model import FileBrowserItem

_clipboard_items: List = []
_is_clipboard_cut = False


def save_items_to_clipboard(items: List[FileBrowserItem], is_cut: bool = False):
    """
    Save browser items to clipboard.

    Args:
        items (List[:obj:`FileBrowserItem`]): List of browser items.
        is_cut (bool): Specify if items are cut from other items or clipboard, defaults to False.
    """
    global _clipboard_items
    _clipboard_items.clear()
    if isinstance(items, list):
        _clipboard_items = items
    elif isinstance(items, FileBrowserItem):
        _clipboard_items = [items]

    if _clipboard_items:
        global _is_clipboard_cut
        _is_clipboard_cut = is_cut


def get_clipboard_items() -> List[FileBrowserItem]:
    """
    Get browser items.
    """
    return _clipboard_items


def is_clipboard_cut() -> bool:
    """
    Return True if items in the clipboard are cut from other items.
    """
    return _is_clipboard_cut


def is_path_cut(path: str) -> bool:
    """
    Return True if the path are cut from other items or clipboard.

    Args:
        path (str): path to check.
    """
    if _is_clipboard_cut:
        return any(path == item.path for item in _clipboard_items)
    return False


def clear_clipboard():
    """
    Clear the clipboard.
    """
    # used when cut items are pasted, we need to clear the clipboard and cut status.
    global _clipboard_items
    _clipboard_items.clear()

    global _is_clipboard_cut
    _is_clipboard_cut = False
