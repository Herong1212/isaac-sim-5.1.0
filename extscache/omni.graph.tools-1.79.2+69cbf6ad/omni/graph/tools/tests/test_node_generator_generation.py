"""Contains support for testing the generator calls individually"""

import argparse
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import omni.graph.tools.ogn as ogn
import omni.kit.test
from omni.graph.tools._impl.node_generator.main import main as ogn_main


class TestNodeGeneratorGeneration(omni.kit.test.AsyncTestCase):
    # --------------------------------------------------------------------------------------------------------------
    async def test_main(self):
        """Test accessing the OGN parser through the main script"""
        ogn_main([])
        ext_name = "omni.graph.tools"

        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()

            with open(tmp_dir / "CategoryConfiguration.json", "w", encoding="utf-8") as cat_fd:
                cat_fd.write(
                    """{
    "categoryDefinitions": {
        "test": "Node types used for testing"
    }
}
"""
                )

            with open(tmp_dir / "TypeDefinitions.json", "w", encoding="utf-8") as def_fd:
                def_fd.write(
                    """{
    "typeDefinitions": {
        "c++": {
            "any": []
        }
    }
}
"""
                )

            tmp_fd = NamedTemporaryFile(dir=tmp_dir, suffix=".ogn", delete=False)
            tmp_fd.close()
            with open(tmp_fd.name, "w", encoding="utf-8") as ogn_fd:
                ogn_fd.write(
                    """
{
    "TestNodeType": {
        "description": "This is a test node type",
        "version": 1,
        "categories": ["test"]
    }
}
"""
                )
            ogn_main(
                [
                    "--nodeFile",
                    tmp_fd.name,
                    "--icons",
                    str(tmp_dir),
                    "--cpp",
                    str(tmp_dir),
                    "--docs",
                    str(tmp_dir),
                    "--python",
                    str(tmp_dir),
                    "--extension",
                    ext_name,
                    "--module",
                    ext_name,
                    "--settings",
                    "pyOptimize",
                    "--configDirectory",
                    str(tmp_dir),
                    "--typeDefinitions",
                    str(def_fd.name),
                ]
            )
            ogn_main(
                [
                    "--nodeFile",
                    tmp_fd.name,
                    "--icons",
                    str(tmp_dir),
                    "--cpp",
                    str(tmp_dir),
                    "--docs",
                    str(tmp_dir),
                    "--python",
                    str(tmp_dir),
                    "--intermediate",
                    str(tmp_dir),
                    "--unwritable",
                    str(tmp_dir),
                    "--extension",
                    ext_name,
                    "--module",
                    ext_name,
                    "--settings",
                    "pyOptimize",
                    "--configDirectory",
                    str(tmp_dir),
                    "--typeDefinitions",
                    "TypeDefinitions.json",
                ]
            )

            # Check out a few error cases for more detailed coverage
            with self.assertRaises(ogn.ParseError):
                ogn_main(
                    [
                        "--settings",
                        "bork",
                    ]
                )
            with self.assertRaises(argparse.ArgumentTypeError):
                ogn_main(
                    [
                        "--configDirectory",
                        "/Not/A/Directory",
                    ]
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_test_data(self):
        """Test the configuration of test data within the ogn definition"""
        required = {
            "TestNodeType": {
                "description": "This is a test node type",
                "version": 1,
                "uiName": "Test Node Type",
                "inputs": {
                    "a": {"type": "double", "description": "An a"},
                    "b": {"type": "double", "description": "A b"},
                    "x": {"type": "double", "description": "An x"},
                },
                "outputs": {
                    "a": {"type": "double", "description": "An a"},
                    "c": {"type": "double", "description": "A c"},
                    "y": {"type": "double", "description": "A y"},
                },
                "state": {
                    "b": {"type": "double", "description": "A b"},
                    "c": {"type": "double", "description": "A c"},
                    "z": {"type": "double", "description": "A z"},
                },
            }
        }
        ext_name = "omni.graph.tools"

        bad_test_configurations = [
            {"a": 42},
            {"b": 42},
            {"c": 42},
            {"q": 42},
            {"inputs:d": 42},
            {"outputs:d": 42},
            {"state:d": 42},
            {"namespace:d": 42},
            {"gpu": 42},
        ]
        for bad_test_configuration in bad_test_configurations:
            configuration = required.copy()
            configuration["TestNodeType"]["tests"] = [bad_test_configuration]
            with self.assertRaises(ogn.ParseError):
                _ = ogn.NodeInterfaceWrapper(configuration, ext_name)

        configuration = required.copy()
        configuration["TestNodeType"]["tests"] = [
            {"inputs:a": 42, "outputs:c": 42, "state_set:b": 42, "state_get:c": 42}
        ]
        wrapper = ogn.NodeInterfaceWrapper(configuration, ext_name)
        with self.assertRaises(AttributeError):
            _ = wrapper.node_interface.attribute_by_name("b")

        configuration = required.copy()
        configuration["TestNodeType"]["tests"] = [{"x": 42, "y": 42, "z": 42}]
        wrapper = ogn.NodeInterfaceWrapper(configuration, ext_name)
