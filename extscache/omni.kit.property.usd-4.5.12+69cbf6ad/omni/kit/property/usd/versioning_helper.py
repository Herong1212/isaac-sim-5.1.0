## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["VersioningHelper"]

import asyncio

import omni.client


class VersioningHelper:
    """
    A class to represent the versioning helper.
    """

    server_cache = {}

    @staticmethod
    def is_versioning_enabled():
        """
        Checks if versioning is enabled.

        Returns:
            True if versioning is enabled, False otherwise.
        """
        try:
            import omni.kit.widget.versioning  # noqa: F401  # pylint: disable=unused-import

            enable_versioning = True
        except ModuleNotFoundError:  # pragma: no cover
            enable_versioning = False

        return enable_versioning

    @staticmethod
    def extract_server_from_url(url):
        """
        Extracts the server from a URL.

        Args:
            url: The URL.

        Returns:
            The server URL.
        """
        client_url = omni.client.break_url(url)
        server_url = omni.client.make_url(scheme=client_url.scheme, host=client_url.host, port=client_url.port)
        return server_url

    @staticmethod
    def check_server_checkpoint_support(server: str, on_complete: callable):  # pragma: no cover
        """
        Checks the server checkpoint support.

        Args:
            server: The server.
            on_complete: The on complete callback.
        """
        if not server:
            on_complete(server, False)
            return

        if server in VersioningHelper.server_cache:
            on_complete(server, VersioningHelper.server_cache[server])
            return

        async def update_server_can_save_checkpoint():
            result, server_info = await omni.client.get_server_info_async(server)
            support_checkpoint = result and server_info and server_info.checkpoints_enabled
            on_complete(server, support_checkpoint)
            VersioningHelper.server_cache[server] = support_checkpoint

        asyncio.ensure_future(update_server_can_save_checkpoint())
