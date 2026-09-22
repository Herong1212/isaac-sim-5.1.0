## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import asyncio
import omni.client

from typing import Callable


class CheckpointHelper:
    """A helper class for checkpoint functionality.

    This class provides static operations for processing server URLs and verifying whether checkpoints are enabled. It extracts standardized server information from a provided URL and determines if the checkpoint feature is active on the server. An internal cache is used to remember responses and reduce redundant queries, thereby improving performance when the same server is queried multiple times.

    The class supports both asynchronous operations and callback mechanisms. Use asynchronous functions when integrating within an async workflow, or provide a callback function to receive the checkpoint status once the operation completes.
    """

    server_cache = {}

    @staticmethod
    def extract_server_from_url(url: str) -> str:
        """Extracts the server components from the provided URL.

        Args:
            url (str): The URL to extract the server components from.

        Returns:
            str: The server URL extracted from the input URL. Returns an empty string if URL is invalid.
        """
        server_url = ""
        if url:
            client_url = omni.client.break_url(url)
            server_url = omni.client.make_url(scheme=client_url.scheme, host=client_url.host, port=client_url.port)
        return server_url

    @staticmethod
    async def is_checkpoint_enabled_async(url: str) -> bool:
        """Asynchronously checks if checkpoint is enabled for the provided URL.

        Args:
            url (str): The URL to verify for checkpoint enablement.

        Returns:
            bool: True if checkpoint is enabled, otherwise False.
        """
        server_url = CheckpointHelper.extract_server_from_url(url)
        if not server_url:
            enabled = False
        elif server_url in CheckpointHelper.server_cache:
            enabled = CheckpointHelper.server_cache[server_url]
        else:
            result, server_info = await omni.client.get_server_info_async(server_url)
            supports_checkpoint = result and server_info and server_info.checkpoints_enabled
            CheckpointHelper.server_cache[server_url] = supports_checkpoint
            enabled = supports_checkpoint
        return enabled

    @staticmethod
    def is_checkpoint_enabled_with_callback(url: str, callback: Callable):
        """Checks if checkpoint is enabled for the given URL and uses a callback to return the result.

        Args:
            url (str): The URL to check for checkpoint enablement.
            callback (Callable): A function that receives the extracted server and checkpoint status.
        """

        async def is_checkpoint_enabled_async(url: str, callback: Callable):
            """Asynchronously checks if checkpoint is enabled for the provided URL.

            Args:
                url (str): The URL to verify for checkpoint enablement.

            Returns:
                bool: True if checkpoint is enabled, otherwise False.
            """
            enabled = await CheckpointHelper.is_checkpoint_enabled_async(url)
            if callback:
                callback(CheckpointHelper.extract_server_from_url(url), enabled)

        asyncio.ensure_future(is_checkpoint_enabled_async(url, callback))
