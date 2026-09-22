__copyright__ = "Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

__all__ = [
    "get_operation_info_for_execution_context",
]

import omni.kit.commands


def get_operation_info_for_execution_context():
    """Get the operation info for Context Options"""
    info = {
        "name": "executionContext",
        "displayName": "Configure",
        "arguments": [
            {
                "name": "verbose",
                "displayName": "Verbose",
                "description": "Log extended information (may result in slower performance)",
                "displayType": "bool",
                "defaultValue": False,
                "metadata": {},
            },
            {
                "name": "generateReport",
                "displayName": "Generate Report",
                "description": "Create a report with information/timing about the various operations and what they did",
                "displayType": "bool",
                "defaultValue": True,
                "metadata": {},
            },
            {
                "name": "captureStats",
                "displayName": "Capture Before/After Stats",
                "description": "Capture and report on the contents of the stage before and after the operations run",
                "displayType": "bool",
                "defaultValue": True,
                "metadata": {},
            },
        ],
    }
    return info
