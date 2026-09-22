# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited

import omni.ext

import omni.services.client as _client

from . import consumer


class HTTPAsyncClient(omni.ext.IExt):
    """HTTP asynchronous Client Consumer."""

    def on_startup(self):
        _client.register("http", consumer.HttpAsyncConsumer, is_async=True)
        _client.register("https", consumer.HttpsAsyncConsumer, is_async=True)

    def on_shutdown(self):
        try:
            _client.unregister("http", is_async=True)
        except KeyError:
            pass

        try:
            _client.unregister("https", is_async=True)
        except KeyError:
            pass
