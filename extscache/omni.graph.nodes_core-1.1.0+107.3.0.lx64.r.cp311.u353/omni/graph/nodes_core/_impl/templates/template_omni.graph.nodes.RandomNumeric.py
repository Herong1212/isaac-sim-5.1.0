# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.graph.ui as ogui


class CustomLayout(ogui.RandomNodeCustomLayoutBase):
    """Custom layout for RandomNumeric node"""

    def __init__(self, compute_node_widget):
        super().__init__(
            compute_node_widget,
            {
                "inputs": {
                    "min": {"display_name": "Minimum", "default_ui": True},
                    "max": {"display_name": "Maximum", "default_ui": True},
                }
            },
        )
