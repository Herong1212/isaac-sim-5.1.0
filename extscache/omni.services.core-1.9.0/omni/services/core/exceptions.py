# Copyright (c) 2020-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from fastapi import HTTPException as _HTTPException


class KitServicesBaseException(_HTTPException):
    """ Base exception for kit micro services
    """


class ServiceUnavailableError(Exception):
    """ Error raised if a service is unavailable (503)
    """
