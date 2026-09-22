# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from fastapi import FastAPI

from ._route import CompressedRoute


class OmniverseService(FastAPI):
    """ 
    An Omniverse Service
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router.route_class = CompressedRoute
        
        # Monkey-patch the FastAPI application in order to address potential discrepancies in the version of
        # `starlette`, where `self._debug` was renamed to `self.debug` in some version:
        self.debug = False

__all__ = ["OmniverseService"]
