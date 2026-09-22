# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from omni.kit.viewport.utility import get_viewport_from_window_name


class OgnGetViewportResolution:
    """
    Gets the resolution of the target viewport.
    """

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""
        try:
            viewport = db.inputs.viewport
            viewport_api = get_viewport_from_window_name(viewport)

            if viewport_api is not None:
                db.outputs.resolution = viewport_api.resolution
            else:
                db.outputs.resolution = (0, 0)
                db.log_error(f"Unknown viewport window '{viewport}'")

        except Exception as error:  # noqa: PLW0703
            db.log_error(str(error))
            return False

        return True
