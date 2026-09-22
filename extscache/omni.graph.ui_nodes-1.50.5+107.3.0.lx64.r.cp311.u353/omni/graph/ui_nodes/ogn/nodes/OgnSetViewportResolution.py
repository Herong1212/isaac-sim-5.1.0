# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.graph.core as og
from omni.kit.viewport.utility import get_viewport_from_window_name


class OgnSetViewportResolution:
    """
    Sets the resolution of the target viewport.
    """

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""
        try:
            viewport = db.inputs.viewport
            viewport_api = get_viewport_from_window_name(viewport)

            if viewport_api is not None:
                resolution = db.inputs.resolution
                if resolution[0] > 0 and resolution[1] > 0:
                    viewport_api.resolution = resolution
                else:
                    db.log_error(f"Invalid resolution {resolution[0]}x{resolution[1]}.")
            else:
                db.log_error(f"Unknown viewport window '{viewport}'")

            db.outputs.exec = og.ExecutionAttributeState.ENABLED

        except Exception as error:  # noqa: PLW0703
            db.log_error(str(error))
            return False

        return True
