# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.graph.core as og
import omni.graph.tools.ogn as ogn
from omni.kit.viewport.utility import get_viewport_from_window_name


class OgnSetViewportRenderer:
    """
    Sets renderer for the target viewport.
    """

    # renderer: (hd_engine, render_mode)
    RENDERER_CONFIGS = {
        "RTX: Realtime": ("rtx", "RaytracedLighting"),
        "RTX: Path Tracing": ("rtx", "PathTracing"),
        "RTX: Iray": ("iray", "iray"),
    }

    @staticmethod
    def initialize(context, node):
        """Assign default value and allowed tokens for the inputs:renderer attribute"""
        renderers = []

        # Query which engines are enabled.
        setting = carb.settings.get_settings().get("/renderer/enabled")
        engines = setting.split(",") if setting else ["rtx", "iray"]

        # Third-party Hydra render delegates are ignored as requested by OM-75851, but they can be included if needed.
        for renderer, (engine, _) in OgnSetViewportRenderer.RENDERER_CONFIGS.items():
            if engine in engines:
                renderers.append(renderer)

        allowed_tokens = ",".join(renderers)

        attr = node.get_attribute("inputs:renderer")
        attr.set_metadata(ogn.MetadataKeys.ALLOWED_TOKENS, allowed_tokens)

        # If the attr is not authored, its default value will be the first enabled renderer.
        if attr.get() == "" and len(renderers) > 0:
            attr.set(renderers[0])

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""
        try:
            renderer = db.inputs.renderer
            if renderer != "":
                viewport = db.inputs.viewport
                viewport_api = get_viewport_from_window_name(viewport)

                if viewport_api is not None:

                    allowed_tokens = db.attributes.inputs.renderer.get_metadata(ogn.MetadataKeys.ALLOWED_TOKENS)
                    renderers = allowed_tokens.split(",")

                    if renderer in renderers and renderer in OgnSetViewportRenderer.RENDERER_CONFIGS:
                        hd_engine, render_mode = OgnSetViewportRenderer.RENDERER_CONFIGS[renderer]

                        # Update the legacy "/renderer/active" setting for anyone that may be watching for it
                        carb.settings.get_settings().set("/renderer/active", hd_engine)

                        viewport_api.set_hd_engine(hd_engine, render_mode)
                    else:
                        db.log_error(f"Unknown renderer '{renderer}'")
                else:
                    db.log_error(f"Unknown viewport window '{viewport}'")

            db.outputs.exec = og.ExecutionAttributeState.ENABLED

        except Exception as error:  # noqa: PLW0703
            db.log_error(str(error))
            return False

        return True
