# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

class BaseServiceError(Exception):
    """Base Service Client exception."""


class ServiceNotFoundError(BaseServiceError):
    """Raised when a Service cannot be found (HTTP: 404)."""


class HTTPServerError(BaseServiceError):
    """Raised when a 500 error is returned."""
