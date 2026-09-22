# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from typing import Optional
import carb.settings

import omni.kit.test
from omni.services.client import AsyncClient
from omni.services.transport.client.base.exceptions import BaseServiceError


class APIServiceTestCase(omni.kit.test.AsyncTestCase):

    async def setUp(self) -> None:
        super().setUp()
        frontend_port = carb.settings.get_settings().get_as_int("exts/omni.services.transport.server.http/port")
        frontend_prefix = f"http://localhost:{frontend_port}"
        self._post_streaming_credentials_path = f"{frontend_prefix}/v1/streaming/creds"
        self._get_streaming_ready_path = f"{frontend_prefix}/v1/streaming/ready"
        self._client: Optional[AsyncClient] = None

    async def tearDown(self) -> None:
        super().tearDown()
        if self._client:
            await self._client.stop_async()
            self._client = None

    async def test_post_streaming_credentials(self) -> None:
        stunIp = "999.999.999"
        stunPort = "9"
        username = "TestUsername"
        password = "TestPassword"
        self._client = AsyncClient(uri=self._post_streaming_credentials_path)
        result = await self._client.post(stunIp=stunIp, stunPort=stunPort, username=username, password=password)
        self.assertTrue(
            expr="success" in result,
            msg="Expected to find a \"success\" key in the JSON response."
        )
        self.assertTrue(result["success"], "Expected the response to return a successful message.")

    async def test_get_streaming_ready(self) -> None:
        self._client = AsyncClient(uri=self._get_streaming_ready_path)
        with self.assertRaises(
            expected_exception=BaseServiceError,
            msg="Exception Failed"
        ) as ctx:
            result = await self._client.get()

        self.assertTrue(
            expr="503" in str(ctx.exception),
            msg="Expected to find HTTP status code '503' in exception message",
        )
