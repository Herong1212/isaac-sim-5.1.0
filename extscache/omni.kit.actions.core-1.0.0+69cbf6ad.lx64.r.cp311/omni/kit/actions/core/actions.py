# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ext
from ._kit_actions_core import *

# Put interface object publicly to use in our API.
_action_registry = None

# public API
def get_action_registry() -> IActionRegistry:
    """
    Get the action registry.

    Return:
        ActionRegistry object which implements the IActionRegistry interface.
    """
    return _action_registry


def execute_action(extension_id: str, action_id: str, *args, **kwargs):
    """
    Find and execute an action.

    Args:
        extension_id: The id of the source extension that registered the action.
        action_id: Id of the action, unique to the extension that registered it.
        *args: Variable length argument list which will be forwarded to execute.
        **kwargs: Arbitrary keyword arguments that will be forwarded to execute.

    Return:
        The result of executing the action, which is an arbitrary Python object
        that could be None (will also return None if the action was not found).
    """
    return get_action_registry().execute_action(extension_id, action_id, *args, **kwargs)


# Use extension entry points to acquire and release the interface.
class ActionsExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        global _action_registry
        _action_registry = acquire_action_registry()

        # Is this a test run? Add extra test for the tested extension.
        try:
            import omni.kit.test
            from .test_extension_actions_api import TestExtensionActionsAPI
            if not omni.kit.test.is_etm_run():
                omni.kit.test.add_test_case_to_tested_extension(TestExtensionActionsAPI)
        except ImportError:
            pass

    def on_shutdown(self):
        global _action_registry

        release_action_registry(_action_registry)
        _action_registry = None
