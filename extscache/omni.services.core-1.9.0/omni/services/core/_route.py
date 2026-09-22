# Copyright (c) 2020-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

import carb

from . import _encoding


class _CompressedRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()

            for encoder_name in self.headers.getlist("Content-Encoding"):
                try:
                    encoder = _encoding.get_encoder(encoder_name)
                    body = encoder.decompress(body)
                    break
                except KeyError as exc:
                    carb.log_error(f"{encoder_name} is not a registered decoder")

            self._body = body
        return self._body


class CompressedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            request = _CompressedRequest(request.scope, request.receive)
            return await original_route_handler(request)
        return custom_route_handler
