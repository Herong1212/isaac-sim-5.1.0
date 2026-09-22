# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""Kit USD micro service."""

import omni.ext

import omni.services.core.main as main

from .services import usd as _usd


class UsdService(omni.ext.IExt):
    """
    Kit USD micro service.

    Simple USD micro service.
    Exposes simple USD commands that can be execute from internal and external processes.
    """

    def on_startup(self) -> None:
        main.register_router(_usd.router, prefix="/kit/usd", tags=["usd"])

    def on_shutdown(self) -> None:
        main.deregister_router(_usd.router, prefix="/kit/usd")
