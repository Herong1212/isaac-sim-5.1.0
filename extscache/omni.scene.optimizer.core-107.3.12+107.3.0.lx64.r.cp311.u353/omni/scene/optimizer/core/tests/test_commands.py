__copyright__ = "Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import omni.kit.test
from omni.scene.optimizer.core.scripts import commands, standalone


# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of module will make it
# auto-discoverable by omni.kit.test
class TestCommands(omni.kit.test.AsyncTestCase):
    """Generic Command tests"""

    async def test_list_operations(self):
        """Test listing plugins"""

        # Assert there are operations
        cmd = commands.SceneOptimizerListOperations()
        operations = cmd.do()
        self.assertGreater(len(operations), 0)

    async def test_list_operation_arguments(self):
        """Test listing the arguments of an operation"""

        cmd = commands.SceneOptimizerListOperationArguments("merge")
        args = cmd.do()
        self.assertGreater(len(args), 0)
