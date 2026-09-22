__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

from pxr import UsdUtils

from ..bindings._omni_scene_optimizer_core import ExecutionContext, acquire_interface


def execute_commands_from_json(stage, filepath):
    """Execute a series of commands described in a Json file on the given Usd.Stage"""
    # acquire the interface and then release it after execution
    iface = acquire_interface()

    # Configure the execution context
    context = ExecutionContext()
    context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

    # Execute the Operation stack described withing the JSON Config
    result = iface.json_parser(context, filepath)

    # Note: we should not (currently) call release. If this is called from within the unit_tests
    #       where commands.py also has the interface, we end up releasing it behind the back of
    #       other things that want it.
    # release_interface(iface)
    return result


def get_output_paths(operation):
    """Return any output paths the operation may have set"""
    iface = acquire_interface()

    return iface.get_output_paths(operation)


def get_output_path_arrays(operation):
    """Return any output path arrays the operation may have set"""
    iface = acquire_interface()

    return iface.get_output_path_arrays(operation)
