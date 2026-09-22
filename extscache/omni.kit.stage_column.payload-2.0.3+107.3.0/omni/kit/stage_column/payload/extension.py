# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ext
from omni.kit.widget.stage import StageColumnDelegateRegistry

from .payload_column_delegate import PayloadColumnDelegate


class StagePayloadWidgetExtension(omni.ext.IExt):
    """The entry point for Stage Window"""

    def on_startup(self):
        # Register column delegates
        self._payload_column_sub = StageColumnDelegateRegistry().register_column_delegate(
            "Payload", PayloadColumnDelegate
        )

    def on_shutdown(self):
        self._payload_column_sub = None
