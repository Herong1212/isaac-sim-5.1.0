# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides the NucleusConnectorExtension for connecting to Nucleus servers and managing authentication flows."""

__all__=["NUCLEUS_CONNECTION_SUCCEEDED_EVENT", "NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT", "connect", "connect_with_dialog", "reconnect", "disconnect"]

import carb.events

NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT: str = "omni.kit.widget.nucleus_connector.CONNECTION_SUCCEEDED"
NUCLEUS_CONNECTION_SUCCEEDED_EVENT: int = carb.events.type_from_string(
    NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT
)
from omni.kit.app import register_event_alias
register_event_alias(NUCLEUS_CONNECTION_SUCCEEDED_EVENT, NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT)

from .extension import NucleusConnectorExtension, connect, connect_with_dialog, reconnect, disconnect
