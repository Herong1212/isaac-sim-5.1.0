# Copyright (c) 2020-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from omni.services.core import main

from . import base


class SchemaTest(base.BaseServiceTest):

    async def test_controlport_status_hidden_in_schema(self):
        app = main.get_app()
        # schema = app.openapi()
        # paths = schema["paths"]

        # self.assertNotIn("/controlport/status", paths)

    async def test_status_in_schema(self):
        app = main.get_app()
        # schema = app.openapi()
        # paths = schema["paths"]

        # self.assertIn("/status", paths)
