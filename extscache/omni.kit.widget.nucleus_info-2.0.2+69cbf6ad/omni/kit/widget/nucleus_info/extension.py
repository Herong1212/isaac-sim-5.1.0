# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext
import omni.kit.app
from .service_discovery import ServiceDiscovery

# Search Service is register name, it actually service name is NGSearch in server side
# See the start up in omni.kit.search.service
REGISTERED_NAME_TO_SERVCIE = {
    "Search Service": "NGSearch",
}


class NucleusInfoExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._discovery = None

    def on_startup(self, ext_id):
        self._discovery = ServiceDiscovery()

    def on_shutdown(self):
        if self._discovery:
            self._discovery.destory()


def is_service_available(service: str, nucleus_url: str):
    """Return True if the specified service is supported for the provided nucleus_url; False otherwise.

    Args:
        service (str): Service name to check for availability.
        nucleus_url (str): URL for the nucleus service.

    Returns:
        bool: True if the service is available; False otherwise.
    """
    discovery = ServiceDiscovery()

    if service in REGISTERED_NAME_TO_SERVCIE:
        return discovery.is_service_supported_for_nucleus(nucleus_url, REGISTERED_NAME_TO_SERVCIE[service])
    else:
        return discovery.is_service_supported_for_nucleus(nucleus_url, service)


def get_nucleus_services(nucleus_url: str):
    """Return the nucleus services available for the provided nucleus_url.

    Args:
        nucleus_url (str): URL for the nucleus service.

    Returns:
        object: The nucleus services returned by ServiceDiscovery.get_nucleus_services.
    """
    discovery = ServiceDiscovery()
    return discovery.get_nucleus_services(nucleus_url)


async def get_nucleus_services_async(nucleus_url: str):
    """Return the nucleus services asynchronously for the provided nucleus_url.

    Args:
        nucleus_url (str): URL for the nucleus service.

    Returns:
        object: The nucleus services returned by ServiceDiscovery.get_nucleus_services_async.
    """
    discovery = ServiceDiscovery()
    return await discovery.get_nucleus_services_async(nucleus_url)
