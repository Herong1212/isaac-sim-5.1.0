__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import pathlib
import platform
import re
import subprocess

import omni.kit.test
from omni.scene.optimizer.core.scripts import standalone


# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of module will make it
# auto-discoverable by omni.kit.test
class TestStandalone(omni.kit.test.AsyncTestCase):
    """Assert that commands are exposed in omni.scene.optimizer.core.standalone as intended"""

    def _test_standalone_command(self, args, testfile):
        """Execute a standalone sceneOptimizer command and return the before/after stats"""

        bin_name = "sceneOptimizer"
        if platform.system().lower() != "linux":
            bin_name = "sceneOptimizer.bat"

        extension_path = pathlib.Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        )

        binary_path = extension_path.joinpath("bin")
        binary = binary_path.joinpath(bin_name)
        test_data_path = extension_path.joinpath("data")
        test_file = test_data_path.joinpath(testfile)

        # sceneOptimizer [args] [testFilename]
        command = [str(binary.absolute())]
        command.extend(args)
        command.append(str(test_file.absolute()))

        result = subprocess.run(command, stdout=subprocess.PIPE)

        # Assert the command executed successfully (it was found, opened the stage, did something)
        self.assertEqual(result.returncode, 0)

        if "-s" not in args and "--stats" not in args:
            return None, None

        resultStr = result.stdout.decode("utf-8")
        lines = resultStr.split("\n")

        # Grep the prim type counts out
        regexPrimCount = re.compile("^\|\s(\w+)\s+(\d+)")

        before = True
        result_before = {}
        result_after = {}

        for line in lines:
            match = regexPrimCount.search(line)
            if match:
                if before:
                    result_before[match.group(1)] = int(match.group(2))
                else:
                    result_after[match.group(1)] = int(match.group(2))

            elif line.startswith("Stats before"):
                # "Stats before" is printed with a time after the "before" stats are printed.
                # At this point the regex will match the "after" stats.
                before = False

        return result_before, result_after

    async def test_functions(self):
        # Assert presence of all the exposed functions
        self.assertTrue(hasattr(standalone, "execute_commands_from_json"))

    async def test_standalone_binary(self):
        """Test the sceneOptimizer standalone binary is found and executes"""

        stats_before, _ = self._test_standalone_command(["--stats"], "groupingScene.usd")

        self.assertEqual(stats_before["Material"], 2)
        self.assertEqual(stats_before["Mesh"], 18)
        self.assertEqual(stats_before["Scope"], 1)
        self.assertEqual(stats_before["Shader"], 4)
        self.assertEqual(stats_before["Xform"], 16)
        self.assertEqual(stats_before["Total"], 41)

    async def test_standalone_binary_merge(self):
        """Test a simple merge"""

        stats_before, stats_after = self._test_standalone_command(["--stats", "--merge"], "primvarMerge.usda")

        # Assert before count
        self.assertEqual(stats_before["Mesh"], 13)
        self.assertEqual(stats_before["Xform"], 1)

        # Assert after count to check the merge happened
        self.assertEqual(stats_after["Mesh"], 1)
        self.assertEqual(stats_after["Xform"], 1)
