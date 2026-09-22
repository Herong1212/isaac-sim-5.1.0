# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""Keeps a history of file events that is made available via an API to other extensions"""
__all__ = [
    "FileEventModel",
    "get_latest_urls_from_event_queue",
    "get_last_url_visited",
    "get_last_url_opened",
    "get_last_url_saved",
    "reset_file_event_queue",
    "asset_types",
    "FILE_OPENED_GLOBAL_EVENT",
    "FILE_OPENED_EVENT",
    "FILE_SAVED_GLOBAL_EVENT",
    "FILE_SAVED_EVENT",
    "FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT",
    "FILE_EVENT_QUEUE_UPDATED",
]

import carb.events
from omni.kit.app import register_event_alias

FILE_OPENED_GLOBAL_EVENT: str = "omni.kit.helper.file_utils.FILE_OPENED"
FILE_OPENED_EVENT: int = carb.events.type_from_string(FILE_OPENED_GLOBAL_EVENT)
register_event_alias(FILE_OPENED_EVENT, FILE_OPENED_GLOBAL_EVENT)

FILE_SAVED_GLOBAL_EVENT: str = "omni.kit.helper.file_utils.FILE_SAVED"
FILE_SAVED_EVENT: int = carb.events.type_from_string(FILE_SAVED_GLOBAL_EVENT)
register_event_alias(FILE_SAVED_EVENT, FILE_SAVED_GLOBAL_EVENT)

FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT: str = "omni.kit.helper.file_utils.FILE_EVENT_QUEUE_UPDATED"
FILE_EVENT_QUEUE_UPDATED: int = carb.events.type_from_string(FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT)
register_event_alias(FILE_EVENT_QUEUE_UPDATED, FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT)

from typing import List
from .extension import get_instance, FileEventHistoryExtension, FileEventModel
from . import asset_types


def get_latest_urls_from_event_queue(
    num_latest: int = 1, asset_type: str = None, event_type: int = 0, event_name: str = None, tag: str = None
) -> List[str]:
    """Retrieves the urls visited based on asset type, event type and tag.

    Args:
        asset_type (str, optional): The type of asset to filter URLs by.
        event_type (int, optional): The type of event to filter URLs by.
        tag (str, optional): The tag to further filter URLs.

    Returns:
        List[str]: The visited URLs matching the criteria, or empty list if no URLs found."""
    ext = get_instance()
    if ext:
        return ext.get_latest_urls_from_event_queue(
            num_latest=num_latest, asset_type=asset_type, event_type=event_type, event_name=event_name, tag=tag
        )
    return []


def get_last_url_visited(asset_type: str = None, tag: str = None) -> str:
    """Retrieves the last URL visited based on asset type and tag.

    Args:
        asset_type (str, optional): The type of asset to filter URLs by.
        tag (str, optional): The tag to further filter URLs.

    Returns:
        str: The last visited URL matching the criteria, or None if no URLs found."""
    urls = get_latest_urls_from_event_queue(num_latest=1, asset_type=asset_type, tag=tag)
    if urls:
        return urls[0]
    else:
        return None


def get_last_url_opened(asset_type: str = None, tag: str = None) -> str:
    """Retrieves the last URL opened based on asset type and tag.

    Args:
        asset_type (str, optional): The type of asset to filter URLs by.
        tag (str, optional): Additional tag to filter the URLs.

    Returns:
        str: The last opened URL matching the specified criteria or None if no match found."""
    urls = get_latest_urls_from_event_queue(num_latest=1, asset_type=asset_type, event_name=FILE_OPENED_GLOBAL_EVENT, tag=tag)
    if urls:
        return urls[0]
    else:
        return None


def get_last_url_saved(asset_type: str = None, tag: str = None) -> str:
    """Retrieves the last URL that was saved for a given asset type and tag.

    Args:
        asset_type (str): The type of asset to filter the URL by.
        tag (str): An additional filter to apply based on a tag."""
    urls = get_latest_urls_from_event_queue(num_latest=1, asset_type=asset_type, event_name=FILE_SAVED_GLOBAL_EVENT, tag=tag)
    if urls:
        return urls[0]
    else:
        return None


def reset_file_event_queue():
    """Clear the event queue maintained by this extension."""
    ext = get_instance()
    if ext:
        return ext.clear_event_queue()
