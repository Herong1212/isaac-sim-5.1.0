__copyright__ = "Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


from omni.scene.optimizer.core.operation import Operation


class BadVersion1PythonOperation(Operation):
    def __init__(self):
        super().__init__(
            "badVersion1PythonOperation",
            "Bad Version 1 Python Operation",
            "This is a Python Operation that returns a non-tuple from the version property for testing purposes.",
        )

    @property
    def author(self):
        return "Scene Optimizer Unit Test"

    @property
    def version(self):
        return 1

    def execute(self, args):
        return True


#####################################
# Register Scene Optimizer Plugin
#####################################


def sceneOptimizerPluginInit():
    return BadVersion1PythonOperation()
