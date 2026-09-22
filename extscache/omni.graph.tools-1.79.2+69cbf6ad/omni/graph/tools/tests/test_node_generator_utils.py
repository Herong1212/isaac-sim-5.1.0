"""Contains support for testing the general utilities used by the node generator."""

import argparse
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import carb
import omni.graph.tools as ogt
import omni.graph.tools._internal as ogi
import omni.graph.tools.ogn as ogn
import omni.kit.test
from omni.graph.tools._impl.node_generator.attributes.AnyAttributeManager import AnyAttributeManager
from omni.graph.tools._impl.node_generator.attributes.attribute_unions import get_attribute_union_configuration_file
from omni.graph.tools._impl.node_generator.attributes.BundleAttributeManager import BundleAttributeManager
from omni.graph.tools._impl.node_generator.attributes.DoubleAttributeManager import DoubleAttributeManager
from omni.graph.tools._impl.node_generator.attributes.inf_nan import NanInfValues, repr_value
from omni.graph.tools._impl.node_generator.attributes.management import (
    formatted_supported_attribute_type_names,
    split_attribute_list,
)
from omni.graph.tools._impl.node_generator.attributes.naming import split_attribute_name
from omni.graph.tools._impl.node_generator.attributes.parsing import is_type_or_list_of_types
from omni.graph.tools._impl.node_generator.attributes.UnionAttributeManager import UnionAttributeManager
from omni.graph.tools._impl.node_generator.nodes import NodeTestData, TestData, check_node_version
from omni.graph.tools._impl.node_generator.utils import (
    UNWRITABLE_TAG_FILE,
    NameManager,
    ReadableDirs,
    check_color,
    ensure_quoted,
    ensure_writable_directory,
    is_unwritable,
    rst_csv_table,
    rst_table,
    shorten_string_lines_to,
    to_python_comment,
    to_usd_docs,
    value_as_usd,
)


class TestNodeGeneratorUtils(omni.kit.test.AsyncTestCase):
    # --------------------------------------------------------------------------------------------------------------
    async def test_attribute_parsing(self):
        """Test the parsing.py utility functions that are not tested elsewhere."""
        full_list = [
            ("bundle", "inputs:bundle"),
            ("any", "inputs:any"),
            ("double", "inputs:bubble"),
            ("union['float', 'int']", "inputs:union"),
        ]

        self.assertTrue(isinstance(ogn.attributes_as_usd(full_list), list))
        self.assertFalse(is_type_or_list_of_types([1], "int", 3))

        self.assertEqual(ogn.separate_ogn_role_and_type("frame"), ("double", "frame"))
        self.assertEqual(ogn.separate_ogn_role_and_type("execution"), ("uint", "execution"))
        self.assertEqual(ogn.separate_ogn_role_and_type("string"), ("uchar", "text"))
        self.assertEqual(ogn.separate_ogn_role_and_type("path"), ("uchar", "path"))
        self.assertEqual(ogn.separate_ogn_role_and_type("normalh"), ("half", "normal"))
        self.assertEqual(ogn.separate_ogn_role_and_type("double"), ("double", "none"))

        self.assertEqual("double2", ogn.usd_type_name("double", 2, False))
        self.assertEqual("matrix2d[]", ogn.usd_type_name("matrixd", 2, True))
        self.assertEqual("quatd", ogn.usd_type_name("quatd", 4, False))
        self.assertEqual("float", ogn.usd_type_name("float", 1, False))

    # --------------------------------------------------------------------------------------------------------------
    async def test_attribute_management(self):
        """Test the management.py utility functions that are not tested elsewhere."""
        supported_names = formatted_supported_attribute_type_names()
        self.assertTrue(len(supported_names) > 20)
        self.assertTrue("double[2][]" in ",".join(supported_names))
        supported_names = ogn.supported_attribute_type_names()
        self.assertTrue(len(supported_names) > 20)
        self.assertTrue("double[2][]" in ",".join(supported_names))

        manager_sample = [
            DoubleAttributeManager("outputs:dbl", "double"),
            BundleAttributeManager("outputs:bundle1", "bundle"),
            BundleAttributeManager("outputs:bundle2", "bundle"),
            AnyAttributeManager("outputs:any1", "any"),
            AnyAttributeManager("outputs:any2", "any"),
            UnionAttributeManager("outputs:union", "union", {}),
            None,
        ]

        (single_attributes, bundle_attributes, runtime_attributes) = split_attribute_list(manager_sample)
        self.assertEqual(1, len(single_attributes))
        self.assertEqual(2, len(bundle_attributes))
        self.assertEqual(3, len(runtime_attributes))

        with self.assertRaises(ogn.ParseError):
            ogn.get_attribute_manager_type("double]")
        self.assertTrue(isinstance(ogn.split_attribute_type_name([["float", "int"]]), tuple))

        with self.assertRaises(ogn.ParseError):
            ogn.get_attribute_manager("name", "junk")
        with self.assertRaises(ogn.ParseError):
            ogn.get_attribute_manager("name", {"No": "description"})
        with self.assertRaises(ogn.ParseError):
            ogn.get_attribute_manager("name", {"type": "float"})
        with self.assertRaises(ogn.ParseError):
            ogn.get_attribute_manager_type("not a legal type")

        self.assertIsNotNone(get_attribute_union_configuration_file())
        self.assertEqual('float("NaN")', NanInfValues.as_repr("nan"))
        self.assertEqual('float("Inf")', NanInfValues.as_repr("inf"))
        self.assertEqual('float("-Inf")', NanInfValues.as_repr("-inf"))
        self.assertEqual('(float("NaN"), float("Inf"))', repr_value(("nan", "inf")))

    # --------------------------------------------------------------------------------------------------------------
    async def test_attribute_naming(self):
        """Test the naming.py utility functions that are not tested elsewhere."""
        with self.assertRaises(ogn.ParseError):
            ogn.namespace_of_group("unknown")
        with self.assertRaises(ogn.ParseError):
            ogn.check_attribute_name("name:spaced")
        with self.assertRaises(ogn.ParseError):
            ogn.check_attribute_ui_name("badly 'formatted' name")

        self.assertEqual("inputs:outputs:attr", ogn.attribute_name_in_namespace("outputs:attr", "inputs"))
        self.assertEqual(("inputs", "custom:attr"), split_attribute_name("inputs:custom:attr"))
        self.assertEqual("attr", ogn.attribute_name_without_port("inputs:attr"))
        self.assertEqual("inputs_attr", ogn.attribute_name_without_port("inputs_attr"))
        self.assertEqual("attr", ogn.attribute_name_as_python_property("inputs:attr"))
        self.assertEqual("attr", ogn.attribute_name_as_python_property("state:attr"))
        self.assertEqual("attr", ogn.attribute_name_as_python_property("attr"))
        self.assertEqual("custom_attr", ogn.attribute_name_as_python_property("outputs:custom:attr"))
        self.assertEqual(
            ["float", "int"], ogn.assemble_attribute_type_name("union", 1, 0, {"float": True, "int": True})
        )

        # Check name shortening. There might be others already so only the replacement pattern can be checked, not
        # the actual index, which is largely irrelevant anyway.
        mgr = NameManager()
        self.assertEqual("untouched", mgr.name("untouched"))
        old_value = mgr.SHORTEN_NAMES
        mgr.SHORTEN_NAMES = True
        self.assertTrue(mgr.name("Hello").startswith("__"))
        self.assertTrue(mgr.name("World").startswith("__"))
        mgr.SHORTEN_NAMES = old_value

    # --------------------------------------------------------------------------------------------------------------
    async def test_node_utilities(self):
        """Test the utilities found in the nodes.py file, and some edge cases."""
        with self.assertRaises(ogn.ParseError):
            ogn.check_node_ui_name("isn't allowed")
        self.assertEqual("okay", ogn.check_node_ui_name("okay"))
        with self.assertRaises(ogn.ParseError):
            check_node_version("not_a_legal_version")

        test_data = NodeTestData()
        test_data.add_set_state(DoubleAttributeManager("inputs:a", "double"), "aValue")
        test_data.add_get_state(DoubleAttributeManager("outputs:b", "double"), "bValue")
        test_data.set_gpu_outputs(["a", "b"])
        self.assertEqual(test_data.gpu_outputs, ["a", "b"])
        self.assertEqual(list(test_data.state_initial_values.values()), ["aValue"])
        self.assertEqual(list(test_data.state_final_values.values()), ["bValue"])

        test_data = TestData()
        test_data.set_file_path(__file__)
        self.assertEqual(test_data.file_path, __file__)

        with self.assertRaises(ogn.ParseError):
            _ = ogn.NodeInterface("bad", {}, "")

        # Empty descriptions are only warnings unless an environment variable turns then into errors
        _ = ogn.NodeInterface("questionable", {"description": ""}, "")
        with self.assertRaises(ogn.ParseError):
            old_value = os.environ.get("OGN_STRICT_DEBUG", None)
            try:
                os.environ["OGN_STRICT_DEBUG"] = "1"
                _ = ogn.NodeInterface("bad", {"description": ""}, "")
            except ogn.ParseError as error:
                raise error
            finally:
                if old_value is None:
                    os.environ.pop("OGN_STRICT_DEBUG")
                else:
                    os.environ["OGN_STRICT_DEBUG"] = old_value

        required = {"description": "This is required", "version": 1}
        bad_combinations = [
            {"singleton": "nope"},
            {"memoryType": "cuda", "language": "python"},
            {"tokens": 42},
            {"typeDefinitions": 42},
            {"typeDefinitions": "noSuchFile.json"},
            {"categoryDefinitions": "noSuchFile.json"},
            {"categories": "noSuchCategory"},
            {"categories": [4]},
            {"categories": {"has\tTab": "Illegal name"}},
        ]
        for combination in bad_combinations:
            combination.update(required)
            with self.assertRaises(ogn.ParseError):
                _ = ogn.NodeInterface("bad", combination, None)

        assorted_flags = {
            "singleton": True,
            "tokens": "red,green,blue",
            "categoryDefinitions": {"color": "Node types dealing with colors"},
            "categories": "color",
        }
        assorted_flags.update(required)
        interface = ogn.NodeInterface("good", assorted_flags, None)
        self.assertEqual(interface.metadata[ogn.MetadataKeys.SINGLETON], "1")
        self.assertEqual(interface.metadata[ogn.MetadataKeys.TOKENS], '"red,green,blue"')
        self.assertEqual(interface.metadata[ogn.MetadataKeys.CATEGORIES], "color")

        settings = ogi.Settings()
        self.assertFalse(settings.pyOptimize)
        carb.settings.get_settings().set("/persistent/omnigraph/generator/pyOptimize", False)
        self.assertEqual(False, ogi.Settings.generator_settings().pyOptimize)

    # --------------------------------------------------------------------------------------------------------------
    async def test_categories(self):
        """Test node type parsing that reference permutations of category definition."""
        required = {"description": "This is required", "version": 1}
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            category_path = tmp_dir / "CategoryConfiguration.json"

            with open(category_path, "w", encoding="utf-8") as cat_fd:
                cat_fd.write(
                    """{
    "categoryDefinitions": {
        "internal:test": "Internal use only",
        "color": "Pertaining to color"
    }
}
"""
                )

            # Permutations of legitimate methods of defining categories. All categories assigned to the node type
            # are the same so that this can be done in a loop.
            category_definitions = [
                {
                    "categoryDefinitions": "CategoryConfiguration.json",
                    "categories": "internal:test,color",
                },
                {
                    "categoryDefinitions": str(category_path),
                    "categories": ["internal:test", "color"],
                },
                {
                    "categoryDefinitions": {"internal:test": "Internal use only", "color": "Pertaining to color"},
                    "categories": "internal:test,color",
                },
                {"categories": {"internal:test": "Internal use only", "color": "Pertaining to color"}},
                {"categories": [{"internal:test": "Internal use only", "color": "Pertaining to color"}]},
            ]

            for category_definition in category_definitions:
                category_definition.update(required)
                interface = ogn.NodeInterface("good", category_definition, tmpdir_fd)
                self.assertCountEqual(
                    ["internal:test", "color"], interface.metadata[ogn.MetadataKeys.CATEGORIES].split(",")
                )

            category_definition = {
                "categoryDefinitions": "CategoryConfiguration.json",
                "categories": "internal:test,color",
            }
            category_definition.update(required)
            interface = ogn.NodeInterface("good", category_definition, None, node_directory=tmpdir_fd)
            self.assertCountEqual(
                ["internal:test", "color"], interface.metadata[ogn.MetadataKeys.CATEGORIES].split(",")
            )

            category_definition = {
                "categoryDefinitions": str(tmp_dir / "noSuchFile"),
            }
            category_definition.update(required)
            with self.assertRaises(ogn.ParseError):
                _ = ogn.NodeInterface("bad", category_definition, None)

    # --------------------------------------------------------------------------------------------------------------
    async def test_type_definitions(self):
        """Test node type parsing that reference permutations of type definitions."""
        required = {"description": "This is required", "version": 1}
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            definitions_path = tmp_dir / "TypeDefinitions.json"

            with open(definitions_path, "w", encoding="utf-8") as def_fd:
                def_fd.write(
                    """{
    "typeDefinitions": {
        "c++": {
            "double": ["none", ["noFile.h"]]
        }
    }
}
"""
                )

            type_definition = {
                "typeDefinitions": "TypeDefinitions.json",
            }
            type_definition.update(required)
            _ = ogn.NodeInterface("good", type_definition, tmpdir_fd)
            config = DoubleAttributeManager.CPP_CONFIGURATION
            self.assertEqual(config["double"].include_files, ["noFile.h"])

            type_definition = {
                "typeDefinitions": str(definitions_path),
            }
            type_definition.update(required)
            _ = ogn.NodeInterface("good", type_definition, None)
            config = DoubleAttributeManager.CPP_CONFIGURATION
            self.assertEqual(config["double"].include_files, ["noFile.h"])

            type_definition = {
                "typeDefinitions": {"c++": {"double": ["none", ["noFile.h"]]}},
            }
            type_definition.update(required)
            _ = ogn.NodeInterface("good", type_definition, None)
            config = DoubleAttributeManager.CPP_CONFIGURATION
            self.assertEqual(config["double"].include_files, ["noFile.h"])

            type_definition = {
                "typeDefinitions": {"c++": {"double": ["none", "noFile.h"]}},
            }
            type_definition.update(required)
            with self.assertRaises(ogn.ParseError):
                _ = ogn.NodeInterface("bad", type_definition, None)

            type_definition = {
                "typeDefinitions": "notATypeDefinition",
            }
            with self.assertRaises(ogn.ParseError):
                _ = ogn.NodeInterface("bad", type_definition, tmpdir_fd)

    # --------------------------------------------------------------------------------------------------------------
    async def test_output(self):
        """Test the output support."""
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()

            out_file = tmp_dir / "OutFile.txt"
            with open(out_file, "w", encoding="utf-8") as out_fd:
                out = ogt.IndentedOutput(out_fd)
                out.write_as_is(["Line 1", "Line 2"])
                out.write_as_is("Line3")
                out.prepend("Hello")
                self.assertEqual(str(out_file), str(out))
                out.close()

            self.assertFalse(is_unwritable(tmpdir_fd))
            tag_file = tmp_dir / UNWRITABLE_TAG_FILE
            with open(tag_file, "w", encoding="utf-8") as tag_fd:
                tag_fd.write("Lock")
            self.assertTrue(is_unwritable(str(tag_file)))

            with self.assertRaises(ValueError):
                ensure_writable_directory(None)

        parser = argparse.ArgumentParser(description="Test parser to exercise directory utilities")
        parser.add_argument("-rm", "--readableMulti", action=ReadableDirs, metavar="DIRS", nargs="?")
        parser.add_argument("-r1", "--readableOne", action=ReadableDirs, metavar="DIRS", nargs=1)
        parser.add_argument("-ra", "--readableAny", action=ReadableDirs, metavar="DIRS")

        # Set up directory structure containing three subdirectories and one file
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            tmp_file = tmp_dir / "TempFile.txt"
            with open(tmp_file, "w", encoding="utf-8") as tmp_fd:
                tmp_fd.write("Non Empty File")
            dir1 = tmp_dir / "dir1"
            ensure_writable_directory(str(dir1))
            dir2 = tmp_dir / "dir2"
            ensure_writable_directory(str(dir2))
            dir3 = tmp_dir / "dir3"
            ensure_writable_directory(str(dir3))

            # Test for specifying a file instead of a directory
            with self.assertRaises(argparse.ArgumentTypeError):
                parser.parse_args(["--readableMulti", str(tmp_file)])
            with self.assertRaises(argparse.ArgumentTypeError):
                parser.parse_args(["--readableMulti", "NotADirectory"])

            # Test for specifying None instead of a directory
            with self.assertRaises(ValueError):
                parser.parse_args(["--readableMulti", None])

            # Test for specifying the wrong number of directories
            with self.assertRaises(argparse.ArgumentTypeError):
                parser.parse_args(["--readableOne", str(dir1), "--readableOne", str(dir2)])

    # --------------------------------------------------------------------------------------------------------------
    async def test_string_helpers(self):
        """Test the string helper support."""
        self.assertEqual(ensure_quoted('"hello"'), '"hello"')
        self.assertEqual(ensure_quoted("hello"), '"hello"')
        self.assertEqual(ensure_quoted('he"llo'), '"he\\"llo"')

        self.assertEqual(["ab", "cd", "ef"], shorten_string_lines_to("ab cd ef", 2))

        lines = "Line1\nLine2\n"
        self.assertEqual("    # Line1\n    # Line2", to_python_comment(lines, 1))
        self.assertEqual(
            '''docs="""Line1
Line2
"""''',
            to_usd_docs(lines),
        )
        self.assertEqual(['docs="""Line1\n', 'Line2\n"""'], to_usd_docs(["Line1\n", "Line2\n"]))

        self.assertEqual(None, value_as_usd(None))
        self.assertEqual("true", value_as_usd(True))
        self.assertEqual(1.0, value_as_usd(1.0))
        self.assertEqual((1.0, 2.0), value_as_usd([1.0, 2.0]))
        self.assertEqual(("true", "false"), value_as_usd((True, False)))

        self.assertEqual("", rst_table([[]]))
        self.assertEqual([], rst_csv_table([]))

        with self.assertRaises(ogn.ParseError):
            check_color([1, 2, 256, 1])
