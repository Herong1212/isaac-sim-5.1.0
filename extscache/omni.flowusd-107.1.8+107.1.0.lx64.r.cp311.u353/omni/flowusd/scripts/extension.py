# Copyright (c) 2020-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ext

from .commands import register_all_flow_commands


class PublicExtension(omni.ext.IExt):
    """Object that tracks the lifetime of the Python part of the extension loading"""

    def __init__(self):
        super().__init__()

        # register commands for undo system
        register_all_flow_commands()

        try:
            import omni.kit.app

            app = omni.kit.app.get_app()
            manager = app.get_extension_manager()
            if manager.is_extension_enabled("omni.graph.ui"):
                import omni.graph.ui

                omni.graph.ui.ComputeNodeWidget.get_instance().add_template_path(__file__)
        except ImportError:
            # No templates necessary
            pass
