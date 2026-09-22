# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Omni Kit Actions Core
---------------------

Omni Kit Actions Core is a framework for creating, registering, and discovering actions.

Here is an example of registering an action that creates a new file when it is executed:

.. code-block::

    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "File Actions"

    action_registry.register_action(
        extension_id,
        "new",
        omni.kit.window.file.new,
        display_name="File->New",
        description="Create a new USD stage.",
        tag=actions_tag,
    )

For more examples, please consult the Python and C++ Usage Example pages.

For Python API documentation, please consult the following subpages.

For C++ API documentation, please consult the API(C++) page.
"""

__all__ = ["Action", "IActionRegistry", "get_action_registry", "execute_action"]
from .actions import *
