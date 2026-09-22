"""Testing for the internal utilities, like extension version management, logging, and .ogn file handling
To turn on debugging for a test just add this line at the beginning:
        ogi.set_registration_logging("stdout")  # TODO:
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import omni.graph.tools._internal as ogi
import omni.kit.test
from omni.graph.tools._impl.node_generator.attributes.attribute_unions import parse_union_definitions
from omni.graph.tools._impl.node_generator.utils import ParseError, rst_table

from .internal_utils import CreateHelper


# ==============================================================================================================
class TestInternalVersions(omni.kit.test.AsyncTestCase):
    async def test_compatibility(self):
        """Low level test of the compatibility functions"""
        bad_version = (0, 0, 0)

        # Run twice to make sure the lru caching behaves
        for _ in range(0, 2):
            self.assertEqual(bad_version, ogi.get_generator_extension_version(ogi.Compatibility.Incompatible))
            current_version = ogi.get_generator_extension_version()
            major_compatible_version = ogi.get_generator_extension_version(ogi.Compatibility.MajorVersionCompatible)
            self.assertEqual(current_version[0], major_compatible_version[0])
            self.assertTrue(current_version > major_compatible_version)

            self.assertEqual(bad_version, ogi.get_target_extension_version(ogi.Compatibility.Incompatible))
            current_version = ogi.get_target_extension_version()
            major_compatible_version = ogi.get_target_extension_version(ogi.Compatibility.MajorVersionCompatible)
            self.assertEqual(current_version[0], major_compatible_version[0])
            self.assertTrue(current_version < major_compatible_version)

    # --------------------------------------------------------------------------------------------------------------
    async def test_generation_versions(self):
        """Test of the class that manages generation versions"""
        base_version = [3, 3, 3]
        minor_version = [3, 3, 4]
        major_version = [3, 4, 5]
        new_version = [4, 0, 0]

        def _with_versions(
            generator_version: ogi.ExtensionVersion_t, target_version: ogi.ExtensionVersion_t
        ) -> ogi.GenerationVersions:
            new_versions = ogi.GenerationVersions(generator_version=generator_version, target_version=target_version)
            return new_versions

        base = _with_versions(base_version, base_version)

        # Set up the test suite with all 16 possible combinations of version compatibility
        test_data = [
            (base_version, base_version, ogi.Compatibility.FullyCompatible),
            (base_version, minor_version, ogi.Compatibility.FullyCompatible),
            (base_version, major_version, ogi.Compatibility.MajorVersionCompatible),
            (base_version, new_version, ogi.Compatibility.Incompatible),
            (minor_version, base_version, ogi.Compatibility.FullyCompatible),
            (minor_version, minor_version, ogi.Compatibility.FullyCompatible),
            (minor_version, major_version, ogi.Compatibility.MajorVersionCompatible),
            (minor_version, new_version, ogi.Compatibility.Incompatible),
            (major_version, base_version, ogi.Compatibility.MajorVersionCompatible),
            (major_version, minor_version, ogi.Compatibility.MajorVersionCompatible),
            (major_version, major_version, ogi.Compatibility.MajorVersionCompatible),
            (major_version, new_version, ogi.Compatibility.Incompatible),
            (new_version, base_version, ogi.Compatibility.Incompatible),
            (new_version, minor_version, ogi.Compatibility.Incompatible),
            (new_version, major_version, ogi.Compatibility.Incompatible),
            (new_version, new_version, ogi.Compatibility.Incompatible),
        ]

        for generator_version, target_version, expected_compatibility in test_data:
            test_version = _with_versions(generator_version, target_version)
            self.assertEqual(expected_compatibility, test_version.compatibility(base))

        # Test extraction of the version numbers from a database file
        with TemporaryDirectory() as test_directory_fd:
            test_directory = Path(test_directory_fd)
            versions = ogi.GenerationVersions(generator_version=[1, 2, 3], target_version=[4, 5, 6])
            creator = CreateHelper("omni.test.internal.versions", test_directory, versions)
            db_path = creator.create_py_database(creator.TEST_CLASS, Path("."))
            db_versions = ogi.GenerationVersions()
            db_versions.set_versions_from_database(db_path)
            self.assertEqual(db_versions, versions, f"Compare {db_versions} and {versions}")
            self.assertEqual(ogi.Compatibility.FullyCompatible, versions.compatibility(db_versions))

        # Test the comparison operators
        minor = ogi.GenerationVersions(generator_version=minor_version, target_version=minor_version)
        major = ogi.GenerationVersions(generator_version=major_version, target_version=major_version)
        newest = ogi.GenerationVersions(generator_version=new_version, target_version=new_version)
        none = ogi.GenerationVersions()
        all_versions = [base, minor, major, newest]
        for version in all_versions + [none]:
            self.assertTrue(version == version)  # noqa: PLR0124
            self.assertTrue(version <= version)  # noqa: PLR0124
            self.assertTrue(version >= version)  # noqa: PLR0124
        for index, version in enumerate(all_versions[:-1]):
            next_version = all_versions[index + 1]
            self.assertTrue(version < next_version)
            self.assertTrue(next_version >= version)
            self.assertTrue(version <= next_version)
            self.assertTrue(next_version > version)
            self.assertTrue(version != next_version)
            self.assertTrue(next_version != version)
        self.assertTrue(none < base)
        self.assertTrue(base > none)
        self.assertTrue(none <= base)
        self.assertTrue(base >= none)
        self.assertFalse(none > base)
        self.assertFalse(base < none)
        self.assertFalse(none >= base)
        self.assertFalse(base <= none)
        self.assertFalse(none == None)  # noqa: PLC0121, E711
        self.assertTrue(none != None)  # noqa: PLC0121, E711
        self.assertFalse(none < None)
        self.assertFalse(none <= None)
        self.assertFalse(none > None)
        self.assertFalse(none >= None)

    # --------------------------------------------------------------------------------------------------------------
    async def test_logging(self):
        """Test the basic extensions made to the logging function"""

        # Check all of the legal locations for logging
        locations = {
            "1": ("StdOutInterceptor", "StreamInterceptor"),
            "stdout": ("StdOutInterceptor", "StreamInterceptor"),
            "cout": ("StdOutInterceptor", "StreamInterceptor"),
            "stderr": ("StdErrInterceptor", "StreamInterceptor"),
            "cerr": ("StdErrInterceptor", "StreamInterceptor"),
        }
        for location, stream_names in locations.items():
            ogi.set_registration_logging(location)
            self.assertEqual(len(ogi.LOG.handlers), 1)
            self.assertIn(ogi.LOG.handlers[0].stream.__class__.__name__, stream_names)

        # The last type is a file, which can be tested directly by looking at its contents after logging
        with TemporaryDirectory() as test_directory_fd:
            test_directory = Path(test_directory_fd)
            log_path = test_directory / "Log.txt"
            ogi.set_registration_logging(log_path)
            try:
                ogi.LOG.info("Hello")
                with open(log_path, "r", encoding="utf-8") as log_fd:
                    actual_contents = log_fd.readlines()
                self.assertCountEqual(["INFO: Hello\n"], actual_contents)
            finally:
                ogi.set_registration_logging(None)

    # --------------------------------------------------------------------------------------------------------------
    async def test_ogn_file_names(self):
        """Test the utility that returns the generated file name given a base name"""
        expected_names = {
            ogi.FileType.OGN: f"{CreateHelper.TEST_CLASS}.ogn",
            ogi.FileType.PYTHON: f"{CreateHelper.TEST_CLASS}.py",
            ogi.FileType.PYTHON_DB: f"{CreateHelper.TEST_CLASS}Database.py",
            ogi.FileType.TEST: f"Test{CreateHelper.TEST_CLASS}.py",
            ogi.FileType.CPP_DB: f"{CreateHelper.TEST_CLASS}Database.h",
            ogi.FileType.DOCS: f"{CreateHelper.TEST_CLASS}.rst",
            ogi.FileType.USD: f"{CreateHelper.TEST_CLASS}Template.usda",
        }
        # Test going from root+type to the full name
        for file_type, expected_name in expected_names.items():
            self.assertEqual(
                expected_name, ogi.get_ogn_file_name(CreateHelper.TEST_CLASS, file_type), f"Assembled {expected_name}"
            )

        # Test going from full name back to type+root
        for file_type, full_name in expected_names.items():
            (root_name, found_type) = ogi.get_ogn_type_and_node(full_name)
            self.assertEqual(found_type, file_type, f"Extracted type from {full_name}")
            self.assertEqual(root_name, CreateHelper.TEST_CLASS, f"Extracted root name from {full_name}")

    # --------------------------------------------------------------------------------------------------------------
    async def test_find_build_directory(self):
        """Test the utility for finding a build directory above a given directory"""
        build_dir = ogi.find_ogn_build_directory(Path(__file__))
        self.assertTrue(build_dir is not None)
        self.assertTrue(build_dir.is_dir())
        self.assertEqual(build_dir.name, "ogn")

        non_dir = ogi.find_ogn_build_directory(build_dir.parent.parent)
        self.assertIsNone(non_dir)

    # --------------------------------------------------------------------------------------------------------------
    async def test_temporary_cache_location(self):
        """Test the temporary redirection of the cache location, used for testing"""
        expected_cache_location = Path("This/Does/Not/Exist")
        with ogi.TemporaryCacheLocation(expected_cache_location):
            self.assertEqual(ogi.cache_location(), expected_cache_location)
            self.assertEqual(
                ogi.full_cache_path(
                    ogi.GenerationVersions(generator_version=[1, 2, 3], target_version=[4, 5, 6]),
                    "my.extension-0.1",
                    "my.extension",
                ),
                expected_cache_location / "ogn_generated" / "1.2.3" / "my.extension-0.1" / "my.extension" / "ogn",
            )


# ==============================================================================================================
class TestUtiltities(omni.kit.test.AsyncTestCase):
    """Tests for some of the miscellaneous functionality that appears in the node generator code"""

    async def test_rst_table(self):
        """Test generation of simple rst tables from text"""
        test_table = [
            ["Language", "Hello World"],
            [
                "C++",
                """#include <iostream>
int main()
{
    std::cout << "Hello World!";
    return 0;
}""",
            ],
            ["Python", 'print("Hello World!")'],
        ]

        expected_result = """+----------+----------------------------------+
| Language | Hello World                      |
+==========+==================================+
| C++      | #include <iostream>              |
|          |                                  |
|          | int main()                       |
|          |                                  |
|          | {                                |
|          |                                  |
|          |     std::cout << "Hello World!"; |
|          |                                  |
|          |     return 0;                    |
|          |                                  |
|          | }                                |
+----------+----------------------------------+
| Python   | print("Hello World!")            |
+----------+----------------------------------+
"""
        actual_result = rst_table(test_table)
        self.assertEqual(expected_result, actual_result)


# ==============================================================================================================
class TestAttributeUnionUtilities(omni.kit.test.AsyncTestCase):
    """Tests parsing utilities for attribute unions configurations"""

    # --------------------------------------------------------------------------------------------------------------
    async def test_throws_on_invalid_entries(self):
        """Tests that ParseError is thrown when there are invalid entries"""
        invalid_values = [1, (1, 2), {"dict": "missing 'entries' and 'appends' keys"}, ["valid", 1]]
        for x in invalid_values:
            definition = {"valid_entry": "valid", "invalid_entry": x}
            with self.assertRaises(ParseError):
                parse_union_definitions(definition)

    # --------------------------------------------------------------------------------------------------------------
    async def test_throws_on_recursive_definition(self):
        """Test that recursive definitions throw an error"""

        # self referencing
        definition = {
            "entry_a": "valid_entry",
            "entry_b": "entry_b",
        }
        with self.assertRaises(ParseError):
            parse_union_definitions(definition)

        # recursive via cross-entries
        definition = {
            "entry_a": "entry_b",
            "entry_b": "entry_c",
            "entry_c": "entry_d",
            "entry_d": ["entry_e", "entry_f", "entry_a"],
        }
        with self.assertRaises(ParseError):
            parse_union_definitions(definition)

    # --------------------------------------------------------------------------------------------------------------
    async def test_flattens_referenced_entries(self):
        """Tests that referenced entries work as expected"""

        definition = {
            "entry_a": ["a", "b", "c", "d"],
            "entry_b": ["entry_a", "e"],
            "entry_c": ["entry_b", "f"],
        }
        result = parse_union_definitions(definition)
        expected_result = {
            "entry_a": ["a", "b", "c", "d"],
            "entry_b": ["a", "b", "c", "d", "e"],
            "entry_c": ["a", "b", "c", "d", "e", "f"],
        }
        self.assertDictEqual(result, expected_result)

    # --------------------------------------------------------------------------------------------------------------
    async def test_append_operator(self):
        """Simple test that the appends operator works as expected"""

        definition = {"entry_a": ["a", "b", "c", "d"], "entry_b": {"entries": ["entry_a", "f"], "append": "_z"}}
        result = parse_union_definitions(definition)
        expected_result = {"entry_a": ["a", "b", "c", "d"], "entry_b": ["a_z", "b_z", "c_z", "d_z", "f_z"]}
        self.assertDictEqual(result, expected_result)
