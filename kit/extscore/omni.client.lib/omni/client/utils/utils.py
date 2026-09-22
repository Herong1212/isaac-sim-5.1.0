"""
omni.client handles URLs only, while Kit, as an authoring tool, needs to support both URLs and raw file system paths.
Although omni.client can handle raw file system paths, it's still not ideal as what we want because of the following
issues:

    * It cannot handle anonymous layer identifier from USD. For example, calling omni.client.normalize_url on an
      anonymous layer identifier may encode the layer identifier, which is not what we want as it changes the
      identifier.
    * Kit supports both local filesystem and remote servers, and the source paths include both local raw filesystem
      paths, and standard URLs. Developers may feed in different URL or path style. For non-local filesystem URLs,
      it's not different as omni.client. While we want to handle local raw filesystem paths and URLs prefixed with "file:"
      uniformly and they could get consistent output, so that the local paths authored into USD could be consumed
      by non-Kit applications, like USDView.

To resolve the above two issues, omni.client.utils provides utilities built on top of omni.client. The APIs
defined here could consume 3 types of URLs or paths:

    * Raw filesystem path without scheme, like local system path `c:/test/path/xxxx`.
    * URLs with scheme, like `omniverse://xxx`.
    * USD anonymous identifier, like `anon:xxxx`.

The difference between omni.client API and the utils here is that they will always output raw filesystem paths if
the input paths or URLs are raw filesystem paths or URLs with scheme `file:`. For other URLs, they are handled
the same as omni.client. Also, it will skip handling to anonymous layer identifier from USD.
"""
import os
import re
import omni.client
import asyncio

from urllib.parse import unquote, urlparse


__all__ = [
    "make_file_url_if_possible",
    "make_relative_url_if_possible",
    "make_absolute_url_if_possible",
    "equal_urls",
    "is_local_url",
    "normalize_url",
    "is_omni_objects_enabled",
    "is_valid_url",
    "is_tagging_enabled",
]


def is_tagging_enabled(url: str) -> bool:
    """Checks if the url support tagging."""
    # TODO: udpate this when omni client has relate function
    return url.startswith("omniverse://")

def is_omni_objects_enabled(url: str) -> bool:
    """Checks if the url support omni objects enabled."""
    if url.startswith("omniverse://"):
        return True
    try:
        result, server_info = omni.client.get_server_info(url)
        if result != omni.client.Result.OK:
            return False
        return bool(server_info and server_info.omniojects_enabled)
    except Exception as e:
        return False

def is_valid_url(url: str) -> bool:
    """Checks if the url format is valid."""
    try:
        result = urlparse(url)
    except ValueError:
        return False
    return bool(result.scheme and result.netloc) or is_local_url(url)

def is_local_url(path_or_url: str) -> bool:
    """Checks if the url points to a raw path or with scheme `file`."""

    url = omni.client.break_url(path_or_url)
    return url.is_raw or url.scheme == "file"

def normalize_url(path_or_url: str) -> str:
    """
    Normalizes url to create uniform format of url, which can be used to compare
    with other normalized urls to check the equality between urls.

    The difference between this functon and omni.client.normalize_url is that
    this function will handle raw path without scheme, url with scheme, and
    also USD anonymous layer, and it will return raw filesystem paths if
    the URL scheme is "file" and not UNC paths.
    """

    url = omni.client.break_url(path_or_url)
    if url.scheme == "anon":
        return path_or_url

    if url.scheme == "file":
        url_path = url.path or ""

        if os.name == "nt":
            # If url.path is in format `/C:/xxxx`, strips the slash to return raw filesystem path.
            # Otherwise, keep the url untouched as it's UNC paths.
            if len(url_path) >= 3 and url_path[0] == '/' and url_path[2] == ':':
                path_or_url = url_path[1:]
        else:
            path_or_url = url.path
    elif url.is_raw:
        path_or_url = unquote(path_or_url)

    return omni.client.normalize_url(path_or_url)


def make_file_url_if_possible(absolute_local_path: str) -> str:
    """
    This function is a wrapper of omni.client.make_file_url to only convert path
    to file url when the followings satisfy:
        1. Path must be absolute local path.
        2. Path is not an URL.
    """

    url = omni.client.break_url(absolute_local_path)
    if not url.is_raw or not os.path.isabs(absolute_local_path):
        return absolute_local_path

    return omni.client.make_file_url(absolute_local_path)


def make_relative_url_if_possible(base_url: str, path_or_url: str) -> str:
    """
    This function is a wrapper of omni.client.make_relative_url
    to handle anonymous layer and convert returned URL to raw filesystem path
    if possible. Also, the final URL or path will be normalized.
    """

    base_client_url = omni.client.break_url(base_url)
    path_client_url = omni.client.break_url(path_or_url)
    if (
        not base_client_url.is_raw
        and base_client_url.scheme != "file"
        and path_client_url.is_raw
        and os.path.isabs(path_or_url)
    ):
        return normalize_url(path_or_url)

    # OM-122939
    base_url = normalize_url(base_url)
    path_or_url = normalize_url(path_or_url)

    relative_url = omni.client.make_relative_url(base_url, path_or_url)
    return normalize_url(relative_url)


def make_absolute_url_if_possible(base_url: str, path_or_url: str) -> str:
    """
    This function is a wrapper of omni.client.combine_urls
    to handle anonymous layer and convert returned URL to raw filesystem path
    if possible. Also, the final URL or path will be normalized.
    """

    base_client_url = omni.client.break_url(base_url)
    path_client_url = omni.client.break_url(path_or_url)
    if (
        base_client_url.scheme != "file"
        and path_client_url.is_raw
        and os.path.isabs(path_or_url)
    ):
        return normalize_url(path_or_url)

    url = omni.client.combine_urls(base_url, path_or_url)

    return normalize_url(url)


def equal_urls(
    url_a: str, url_b: str,
    ignore_port=True, ignore_user=True,
    ignore_query_string=True
):
    """
    Checks if two urls are equal. This function will simply compare URLs with string equality to
    different parts of URLs. When to compare a raw filesystem path towards an local file URL with scheme `file`,
    the URL will firstly be converted to a raw filesystem path, then doing comparison.
    """

    client_url_a = omni.client.break_url(normalize_url(url_a))
    client_url_b = omni.client.break_url(normalize_url(url_b))

    if client_url_a.scheme != client_url_b.scheme:
        return False

    if client_url_a.host != client_url_b.host:
        return False

    if client_url_a.path != client_url_b.path:
        return False

    if not ignore_port and client_url_a.port != client_url_b.port:
        return False

    if not ignore_user and client_url_a.user != client_url_b.user:
        return False

    if not ignore_query_string and client_url_a.query != client_url_b.query:
        return False

    return True
