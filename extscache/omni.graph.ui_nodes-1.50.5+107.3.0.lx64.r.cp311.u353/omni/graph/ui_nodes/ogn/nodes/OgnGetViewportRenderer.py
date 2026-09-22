# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from omni.kit.viewport.utility import get_viewport_from_window_name


class OgnGetViewportRenderer:
    """
    Gets the renderer being used by the specified viewport.
    """

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""
        try:
            viewport = db.inputs.viewport
            viewport_api = get_viewport_from_window_name(viewport)

            renderer = ""

            if viewport_api is not None:
                engine_name = viewport_api.hydra_engine
                render_mode = viewport_api.render_mode

                if engine_name == "rtx":
                    if render_mode == "RaytracedLighting":
                        renderer = "RTX: Realtime"
                    elif render_mode == "PathTracing":
                        renderer = "RTX: Path Tracing"
                elif engine_name == "iray":
                    if render_mode == "iray":
                        renderer = "RTX: Iray"
                elif engine_name == "pxr":
                    renderer = "Pixar Storm"

                if renderer == "":
                    db.log_error(f"Unknown Hydra engine '{engine_name}' and render mode '{render_mode}'")

            else:
                db.log_error(f"Unknown viewport window '{viewport}'")

            db.outputs.renderer = renderer

        except Exception as error:  # noqa: PLW0703
            db.log_error(str(error))
            return False

        return True
