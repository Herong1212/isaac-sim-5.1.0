# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Collection of functions to manage thumbnails."""
__all__ = ["MissingThumbnailError", "find_thumbnails_for_files_async", "list_thumbnails_for_folder_async", "generate_missing_thumbnails_async"]
import os
import asyncio
import omni.client
import omni.kit.app

from typing import List, Dict, Set
from carb import log_warn
from omni.kit.helper.file_utils import asset_types
from . import MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT

# Module globals
_thumbnails_dir: str = ".thumbs/256x256"
_missing_thumbnails_cache: Set = set()


class MissingThumbnailError(Exception):
    """ Raised when Moebius server error
    """
    def __init__(self, msg: str = '', url: str = None):
        super().__init__(msg)
        self.url = url


async def find_thumbnails_for_files_async(urls: List[str], generate_missing: bool = True) -> Dict:
    """
    Return a dictionary of thumbnails for the given files.

    Args:
        urls (List[str]): List of file Urls.
        generate_missing (bool): When True, emits a carb event for the missing thumbnails. Set to False to
            disable this behavior.

    Returns:
        Dict: Dict of all found thumbnails, with file Url as key, and thumbnail Url as value.

    """
    tasks = [_find_thumbnail_async(url, auto=False) for url in urls if url]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    thumbnail_dict = {}
    missing_thumbnails = []
    for result in results:
        if result is None:
            # Result could be None if url is empty or url represents a thumbnail
            # It may happen when fetching search results
            continue
        if isinstance(result, MissingThumbnailError):
            missing_thumbnails.append(result.url)
        else:
            url, thumbnail_url = result
            if url and thumbnail_url:
                thumbnail_dict[url] = thumbnail_url

    # Generate any missing thumbnails
    if missing_thumbnails and generate_missing:
        await generate_missing_thumbnails_async(missing_thumbnails)

    return thumbnail_dict


async def _find_thumbnail_async(url: str, auto=False):
    if not url:
        return None

    broken_url = omni.client.break_url(url)
    if _thumbnails_dir in broken_url.path:
        return None

    parent_path = os.path.dirname(broken_url.path)
    filename = os.path.basename(broken_url.path)
    thumbnail_path = f"{parent_path.rstrip('/')}/{_thumbnails_dir}/{filename}" + (".auto.png" if auto else ".png")
    thumbnail_url = omni.client.make_url(scheme=broken_url.scheme, host=broken_url.host, port=broken_url.port, path=thumbnail_path)
    result = None
    try:
        result, stats = await omni.client.stat_async(thumbnail_url)
    except (Exception, asyncio.CancelledError, asyncio.TimeoutError) as e:
        result = omni.client.Result.ERROR_NOT_FOUND

    if result == omni.client.Result.OK:
        return (url, thumbnail_url)
    elif not auto:
        return await _find_thumbnail_async(url, auto=True)
    else:
        raise MissingThumbnailError(url=url)


async def list_thumbnails_for_folder_async(url: str, timeout: float = 30.0, generate_missing: bool = True) -> Dict:
    """
    Return a dictionary of thumbnails for the files in the given folder.

    Args:
        url (str): Folder Url.
        generate_missing (bool): When True, emits a carb event for the missing thumbnails. Set to False to
            disable this behavior.

    Returns:
        Dict: Dict of all found thumbnails, with file Url as key, and thumbnail Url as value.

    """
    thumbnail_dict = {}

    if not url or _thumbnails_dir in url:
        return {}

    url = url.rstrip('/')
    # TODO: collection name, don't need to change here
    if url in ["omniverse:", "my-computer:", "bookmark:"]:
        return {}
    try:
        result, stats = await omni.client.stat_async(url)
    except (Exception, asyncio.CancelledError, asyncio.TimeoutError) as e:
        result = omni.client.Result.ERROR_NOT_FOUND
    else:
        if stats and result == omni.client.Result.OK:
            if not (stats.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN):
                # Not a folder
                return await find_thumbnails_for_files_async([url])
        else:
            log_warn(f"Failed to stat url {url}")
            return {}

    # 1. List the given folder and populate keys of thumbnail_dict
    result, entries = None, {}
    try:
        result, entries = await asyncio.wait_for(omni.client.list_async(url), timeout=timeout)
    except asyncio.CancelledError as e:
        # Do not show a warning if the coroutine is cancelled from the outside as this has
        # nothing to do with omni.client.list_async failing.
        return {}
    except (Exception, asyncio.TimeoutError) as e:
        log_warn(f"Failed to list the folder at {url}: {str(e)}")
        return {}

    if result == omni.client.Result.OK:
        for entry in entries:
            thumbnail_dict[f"{url}/{entry.relative_path}"] = None

    # 2. List thumbnail folder and match up thumbnail Url's
    thumbnail_folder_url = f"{url}/{_thumbnails_dir}"
    result = entries = None, {}
    try:
        result, entries = await asyncio.wait_for(omni.client.list_async(thumbnail_folder_url), timeout=timeout)
    except (Exception, asyncio.CancelledError, asyncio.TimeoutError) as e:
        result = omni.client.Result.ERROR_NOT_FOUND

    if result == omni.client.Result.OK:
        for entry in entries:
            if entry.relative_path.endswith(".auto.png"):
                asset_name = entry.relative_path[:-len(".auto.png")]
                auto = True
            elif entry.relative_path.endswith(".png"):
                asset_name = entry.relative_path[:-len(".png")]
                auto = False
            else:
                continue

            asset_url = f"{url}/{asset_name}"
            if not auto or (auto and thumbnail_dict.get(asset_url) is None):
                # Take manual thumbnails over auto thumbnails
                thumbnail_dict[asset_url] = f"{thumbnail_folder_url}/{entry.relative_path}"

    # 3. Separate haves and have nots.  Missing thumbnails have thumbnail Url == None
    missing_thumbnails = [k for k, v in thumbnail_dict.items() if v == None]
    thumbnail_dict = {k: v for k, v in thumbnail_dict.items() if v != None}

    # 4. Generate any missing thumbnails
    if missing_thumbnails and generate_missing:
        asyncio.ensure_future(generate_missing_thumbnails_async(missing_thumbnails))

    return thumbnail_dict


async def generate_missing_thumbnails_async(missing_thumbnails: List[str]):
    """
    When missing thumbnails are discovered, send an event to have them generated.  The generator
    service is a separate process.  Once generated, a reciprocal event is sent to update the UI.
    The flow is diagramed below::

        +-------------------------------+                        +------------------------------+
        |         Filebrowser           |                        |                              |
        |  +-------------------------+  |   Missing thumbnails   |                              |
        |  |                         |  |        event           |                              |
        |  |       update_grid       +--------------------------->     Thumbnail generator      |
        |  |                         |  |                        |          service             |
        |  +-------------------------+  |                        |                              |
        |  +-------------------------+  |      Thumbnails        |                              |
        |  |                         |  |   generated event      |                              |
        |  |    update_cards_on      <---------------------------+                              |
        |  |  thumbnails_generated   |  |                        |                              |
        |  +-------------------------+  |                        |                              |
        |                               |                        |                              |
        +-------------------------------+                        +------------------------------+

    """
    image_urls = []
    for url in missing_thumbnails:
        if asset_types.is_asset_type(url, asset_types.ASSET_TYPE_IMAGE) and (url not in _missing_thumbnails_cache):
            # Check that this file is an image type and not already submitted
            image_urls.append(url)

    if image_urls:
        omni.kit.app.queue_event(MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT, {"urls": image_urls})
        _missing_thumbnails_cache.update(set(image_urls))
