"""Testing for the internal utilities, like extension version management, logging, and .ogn file handling"""

from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

import omni.graph.tools._internal as ogi
import omni.kit.test

from .internal_utils import (
    CreateHelper,
    TemporaryPathAddition,
    _check_module_api_consistency,
    _check_public_api_contents,
)

# Helper constants shared by many tests
EXT_INDEX = 0
_CLASS_NAME = "OgnTestNode"
_CURRENT_VERSIONS = ogi.GenerationVersions(ogi.Compatibility.FullyCompatible)
_INCOMPATIBLE_MAJOR_VERSIONS = ogi.GenerationVersions(generator_version=(1000, 1000, 1000))


# ==============================================================================================================
class ModuleContexts:
    def __init__(self, stack: ExitStack):
        """Set up a stack of contexts to use for tests running in individual temporary directory"""
        global EXT_INDEX
        EXT_INDEX += 1
        self.ext_name = f"omni.test.internal.extension{EXT_INDEX}"
        # Default extension version is 0.1.0 so create an ID with that
        self.ext_id = f"{self.ext_name}-0.1.0"
        # Put all temporary files in a temporary directory for easy disposal
        self.test_directory = Path(stack.enter_context(TemporaryDirectory()))  # pylint: disable=consider-using-with
        self.module_root = Path(self.test_directory) / "exts"
        self.module_name = self.ext_name
        self.module_path = self.module_root / self.ext_name / self.module_name.replace(".", "/")
        # Redirect the usual node cache to the temporary directory
        self.cache_root = stack.enter_context(ogi.TemporaryCacheLocation(self.test_directory / "cache"))
        # Add the import path of the new extension to the system path
        self.path_addition = stack.enter_context(TemporaryPathAddition(self.module_root / self.ext_name))
        # Uncomment this to dump debugging information while the tests are running
        # self.log = stack.enter_context(ogi.TemporaryLogLocation("stdout"))


# ==============================================================================================================
class TestInternalExtension(omni.kit.test.AsyncTestCase):
    """Tests concerned with exercising the information provided by the code generation utilities. For tests related
    to the node type registration see omni.graph.core.tests.test_register_python_ogn.py
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None  # Diffs of file path lists can be large so let the full details be seen

    # --------------------------------------------------------------------------------------------------------------
    async def test_build_tree_constructor(self):
        """Test the CreateHelper utility class"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            ogn_directory_v1_18 = ctx.module_path / "ogn"
            ogn_directory_v1_19 = ctx.module_root / ctx.module_name / "ogn" / "generated"

            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            # Create a build tree with one up-to-date version and one out-of-date version to cover both cases
            creator.add_standalone_node("OgnTestNode")
            creator.add_v1_18_node("OgnBuiltNode")
            creator.add_v1_19_node("OgnNewNode")

            expected_files = [
                ctx.module_path / "nodes" / "OgnTestNode.ogn",
                ctx.module_path / "nodes" / "OgnTestNode.py",
                ogn_directory_v1_18 / "OgnBuiltNodeDatabase.py",
                ogn_directory_v1_18 / "nodes" / "OgnBuiltNode.ogn",
                ogn_directory_v1_18 / "nodes" / "OgnBuiltNode.py",
                ogn_directory_v1_18 / "tests" / "__init__.py",
                ogn_directory_v1_18 / "tests" / "TestOgnBuiltNode.py",
                ogn_directory_v1_18 / "tests" / "usd" / "OgnBuiltNodeTemplate.usda",
                ctx.module_path / "OgnNewNode.ogn",
                ctx.module_path / "OgnNewNode.py",
                ogn_directory_v1_19 / "__init__.py",
                ogn_directory_v1_19 / "ogn" / "OgnNewNodeDatabase.py",
                ogn_directory_v1_19 / "tests" / "TestOgnNewNode.py",
                ogn_directory_v1_19 / "tests" / "usd" / "OgnNewNodeTemplate.usda",
            ]
            for expected_file in expected_files:
                expected_path = ctx.module_root / expected_file
                self.assertTrue(expected_path.is_file(), f"Checking existence of {expected_path}")
                self.assertTrue(expected_path.stat().st_size > 0, f"Checking size of {expected_path}")

    # --------------------------------------------------------------------------------------------------------------
    async def test_walk_with_excludes(self):
        """Test the utility that imitates os.walk with directory exclusions"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_standalone_node("OgnTestNode")
            creator.add_v1_18_node("OgnBuiltNode")

            # Exclude the tests directory and make sure the two files in there didn't get found
            files_found = []
            for _, _, file_names in ogi.walk_with_excludes(ctx.test_directory, {"tests"}):
                files_found += file_names
            self.assertCountEqual(
                files_found,
                [
                    "OgnTestNode.ogn",
                    "OgnTestNode.py",
                    "OgnBuiltNode.ogn",
                    "OgnBuiltNode.py",
                    "OgnBuiltNodeDatabase.py",
                ],
            )

            # Walk with no exclusions to make sure all files are found
            files_found = []
            for _, _, file_names in ogi.walk_with_excludes(ctx.test_directory, {}):
                files_found += file_names
            self.assertCountEqual(
                files_found,
                [
                    "OgnTestNode.ogn",
                    "OgnTestNode.py",
                    "OgnBuiltNode.ogn",
                    "OgnBuiltNode.py",
                    "OgnBuiltNodeDatabase.py",
                    "TestOgnBuiltNode.py",
                    "__init__.py",
                    "OgnBuiltNodeTemplate.usda",
                ],
            )

    # --------------------------------------------------------------------------------------------------------------
    async def test_scan_extension(self):
        """Test the process of scanning an extension for existing .ogn, .py, and Database.py files"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_v1_18_node(_CLASS_NAME)

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()

            user_types_expected = [ogi.FileType.OGN, ogi.FileType.PYTHON]
            generated_types_expected = [ogi.FileType.PYTHON_DB, ogi.FileType.TEST, ogi.FileType.USD]
            file_names = {file_type: ogi.get_ogn_file_name(_CLASS_NAME, file_type) for file_type in ogi.FileType}
            definition = ext_contents.node_type_definition(_CLASS_NAME)
            self.assertEqual(definition.name, _CLASS_NAME)
            self.assertEqual(len(user_types_expected), len(definition.user_files))
            self.assertTrue(
                all(
                    info[0] is not None
                    for info in [definition.user_files[file_type] for file_type in user_types_expected]
                )
            )
            self.assertCountEqual(list(definition.generated_files.keys()), generated_types_expected)
            ogn_directory = ctx.module_path / "ogn"
            expected_files = {
                ogi.FileType.OGN: ogn_directory / "nodes" / file_names[ogi.FileType.OGN],
                ogi.FileType.PYTHON: ogn_directory / "nodes" / file_names[ogi.FileType.PYTHON],
                ogi.FileType.PYTHON_DB: ogn_directory / file_names[ogi.FileType.PYTHON_DB],
                ogi.FileType.TEST: ogn_directory / "tests" / file_names[ogi.FileType.TEST],
                ogi.FileType.USD: ogn_directory / "tests" / "usd" / file_names[ogi.FileType.USD],
            }
            # All of the file types should be in the expected locations
            for expected_type, expected_path in expected_files.items():
                self.assertEqual(definition.file_path(expected_type), expected_path)

            # The files types, in type order, should also be in time order initially
            self.assertTrue(definition.file_mtime(ogi.FileType.OGN) <= definition.file_mtime(ogi.FileType.PYTHON))
            self.assertTrue(definition.file_mtime(ogi.FileType.PYTHON) <= definition.file_mtime(ogi.FileType.PYTHON_DB))
            self.assertTrue(definition.file_mtime(ogi.FileType.PYTHON_DB) <= definition.file_mtime(ogi.FileType.TEST))
            self.assertTrue(definition.file_mtime(ogi.FileType.TEST) <= definition.file_mtime(ogi.FileType.USD))
            # The files types should have all received the artificially generated version number
            self.assertEqual(
                definition.generated_versions,
                _CURRENT_VERSIONS,
                f"Comparing generated version {definition.generated_versions} to"
                f" current version {_CURRENT_VERSIONS}",
            )

            # The node type definitions are up to date by design
            self.assertFalse(definition.is_out_of_date(_CURRENT_VERSIONS))

            # Touch the .ogn file to make the database out of date.
            self.assertTrue(definition.user_files.touch(ogi.FileType.OGN))
            # For generated files - the modified ogn is ignored
            self.assertFalse(definition.is_out_of_date(_CURRENT_VERSIONS))
            self.assertTrue(definition.is_out_of_date(_INCOMPATIBLE_MAJOR_VERSIONS))

            # Check the functionality that walks the available list of generated file types
            available_types = list(definition.iter_valid_generated_filetypes())
            self.assertCountEqual(available_types, generated_types_expected + [ogi.FileType.DOCS])

    # --------------------------------------------------------------------------------------------------------------
    async def test_scan_empty(self):
        """Test the utility that scans a directory looking for .ogn files when the directory has none, though it
        does have some nodes that look like node files due to their naming.
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNone(ext_contents)

    # --------------------------------------------------------------------------------------------------------------
    async def test_scan_standalone(self):
        """Test the utility that scans a directory looking for .ogn files when the directory is structured as a
        standalone extension (i.e. no built files)
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_standalone_node(_CLASS_NAME)

            ogn_directory = ctx.module_path / "ogn"
            node_directory = ctx.module_path / "nodes"

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()

            self.assertEqual(ext_contents.node_type_count, 1)
            definition = ext_contents.node_type_definition(_CLASS_NAME)
            self.assertIsNotNone(definition)

            self.assertEqual(definition.name, _CLASS_NAME)
            self.assertEqual(2, len(definition.user_files))
            self.assertEqual(0, len(definition.generated_files))
            self.assertEqual(definition.user_files[ogi.FileType.OGN][0], node_directory / f"{_CLASS_NAME}.ogn")
            self.assertEqual(definition.user_files[ogi.FileType.PYTHON][0], node_directory / f"{_CLASS_NAME}.py")
            self.assertTrue(definition.is_out_of_date(_CURRENT_VERSIONS))

            expected_files = {
                ogi.FileType.OGN: node_directory / f"{_CLASS_NAME}.ogn",
                ogi.FileType.PYTHON: node_directory / f"{_CLASS_NAME}.py",
                ogi.FileType.PYTHON_DB: ogn_directory / f"{_CLASS_NAME}Database.py",
                ogi.FileType.TEST: ogn_directory / "tests" / f"Test{_CLASS_NAME}.py",
                ogi.FileType.USD: ogn_directory / "tests" / "usd" / f"{_CLASS_NAME}Template.usda",
                ogi.FileType.DOCS: ogn_directory / "docs" / f"{_CLASS_NAME}.rst",
            }
            for file_type, expected_file in expected_files.items():
                if file_type in [ogi.FileType.OGN, ogi.FileType.PYTHON]:
                    self.assertEqual(definition.file_path(file_type), expected_file)
                else:
                    self.assertEqual(definition.file_path(file_type), None)

    # --------------------------------------------------------------------------------------------------------------
    async def test_exclude_types(self):
        """Test that files excluded by a node do not appear in its outdated list when missing"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            ogn_directory = ctx.module_path / "ogn"
            exclusions = [ogi.FileType.USD, ogi.FileType.DOCS]
            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_v1_18_node(_CLASS_NAME, exclusions)

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()

            self.assertEqual(ext_contents.node_type_count, 1)
            definition = ext_contents.node_type_definition(_CLASS_NAME)
            self.assertIsNotNone(definition)

            self.assertEqual(definition.name, _CLASS_NAME)
            self.assertEqual(definition.file_path(ogi.FileType.OGN), ogn_directory / "nodes" / "OgnTestNode.ogn")
            self.assertEqual(definition.file_path(ogi.FileType.PYTHON), ogn_directory / "nodes" / "OgnTestNode.py")
            self.assertEqual(
                {file_type: gen_def[0] for file_type, gen_def in definition.generated_files.items()},
                {
                    ogi.FileType.TEST: ogn_directory / "tests" / "TestOgnTestNode.py",
                    ogi.FileType.PYTHON_DB: ogn_directory / "OgnTestNodeDatabase.py",
                },
            )

            # The up-to-date database should have been found
            self.assertEqual(
                definition.generated_versions,
                ogi.GenerationVersions(ogi.Compatibility.FullyCompatible),
            )
            self.assertFalse(definition.is_out_of_date(_CURRENT_VERSIONS))

    # --------------------------------------------------------------------------------------------------------------
    async def test_out_of_date_versions(self):
        """Test that versions with good timestamps but old versions are flagged for regeneration"""
        incompatible = ogi.GenerationVersions(ogi.Compatibility.Incompatible)
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            creator = CreateHelper(ctx.ext_name, ctx.module_root, incompatible)
            creator.add_v1_18_node(_CLASS_NAME)

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()

            self.assertEqual(ext_contents.node_type_count, 1)
            definition = ext_contents.node_type_definition(_CLASS_NAME)
            self.assertIsNotNone(definition)

            # The node was generated to be deliberately incompatible with the current versions
            self.assertEqual(definition.generated_versions, incompatible)
            self.assertTrue(definition.is_out_of_date(_CURRENT_VERSIONS))

    # --------------------------------------------------------------------------------------------------------------
    async def test_versions_in_build_and_cache(self):
        """Test that the newer version is selected when they exist in both the build and the cache
        The structure it generates here is a local directory with the cache/ and ogn/ directories together:
            ogn/
                OgnSampleNodeDatabase.py
                nodes/
                    OgnSampleNode.py
                    OgnSampleNode.ogn
                tests/
                    TestOgnSampleNode.py
                    usd/
                        OgnSampleNodeTemplate.usda
            cache/
                ogn_generated/
                    XX.YY.ZZ/
                        omni.test.internal.extension/
                            OgnSampleNodeDatabase.py
                            docs/
                                OgnSampleNode.rst
                            tests/
                                TestOgnSampleNode.py
                                usd/
                                    OgnSampleNodeTemplate.usda
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            major_compatible_versions = ogi.GenerationVersions(ogi.Compatibility.MajorVersionCompatible)
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
            creator_major = CreateHelper(ctx.ext_name, ctx.module_root, major_compatible_versions)
            generated_db_file = creator_major.add_v1_18_node(_CLASS_NAME)[3]
            self.assertTrue(str(generated_db_file).endswith("Database.py"))
            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_cache_for_node(_CLASS_NAME)

            ext_contents = ogi.extension_contents_factory(ctx.ext_id, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()

            self.assertEqual(1, ext_contents.node_type_count)
            definition = ext_contents.node_type_definition(_CLASS_NAME)
            self.assertIsNotNone(definition)

            # Different versions should have been found for the cache and the build generated files
            self.assertEqual(
                definition.generated_versions,
                major_compatible_versions,
                f"Generated versions {definition.generated_versions} versus major {major_compatible_versions}",
            )
            self.assertEqual(
                definition.cached_versions,
                _CURRENT_VERSIONS,
                f"Cached versions {definition.cached_versions} versus current {_CURRENT_VERSIONS}",
            )

            # The generated (package file) is always the one returned if it exists
            self.assertEqual(generated_db_file, definition.database_to_use())

            # Remove the generated file type, so the only the cache file exists
            definition.generated_files[ogi.FileType.PYTHON_DB] = None
            cached_db_file = cache_directory / ogi.get_ogn_file_name(_CLASS_NAME, ogi.FileType.PYTHON_DB)
            self.assertEqual(cached_db_file, definition.database_to_use())

            # Test that cached files are flagged for rebuilding when they have the correct version but are
            # older than the .ogn from which they are generated.
            self.assertTrue(definition.user_files.touch(ogi.FileType.OGN))
            self.assertTrue(definition.is_out_of_date(_CURRENT_VERSIONS))

    # --------------------------------------------------------------------------------------------------------------
    async def test_cached_version_old(self):
        """Test that cached files with incompatible versions are ignored"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            incompatible_versions = ogi.GenerationVersions(ogi.Compatibility.Incompatible)
            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_v1_18_node(_CLASS_NAME)
            creator_incompatible = CreateHelper(ctx.ext_name, ctx.module_root, incompatible_versions)
            creator_incompatible.add_cache_for_node(_CLASS_NAME)

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()

            self.assertEqual(1, ext_contents.node_type_count)
            definition = ext_contents.node_type_definition(_CLASS_NAME)
            self.assertIsNotNone(definition)

            # Different versions should have been found for the cache and the build generated files
            self.assertEqual(
                definition.generated_versions,
                _CURRENT_VERSIONS,
                f"Generated versions {definition.generated_versions} versus current {_CURRENT_VERSIONS}",
            )

            # The generated file is the one that is currently up to date so it should be the one returned when
            # asking for the database file.
            generated_db_file = ctx.module_path / "ogn" / ogi.get_ogn_file_name(_CLASS_NAME, ogi.FileType.PYTHON_DB)
            self.assertEqual(generated_db_file, definition.database_to_use())

    # --------------------------------------------------------------------------------------------------------------
    async def test_check_module_api_consistency(self):
        """Test that incongruities between a module's visible and published APIs are correctly detected"""

        class DummyModule:
            """
            Dummy class that serves as our test module. Note that the API method names stashed
            in the __all__ list are purposefully different from the class's actual public methods.
            """

            __all__ = ["method_0", "method_1"]

            def method_2(self):
                return

            def method_3(self):
                return

        with self.assertRaises(ValueError):
            _check_module_api_consistency(DummyModule)

    async def test_check_public_api_contents(self):
        """Test that incongruities between a module's expected and published APIs are correctly detected"""

        class DummyModule:
            """
            Dummy class that serves as our test module.
            """

            __all__ = []

        # An error should be raised if an expected published API object is not exposed in the module (i.e., its
        # name is not included in the __all__ list).
        with self.assertRaises(ValueError):
            _check_public_api_contents(
                module=DummyModule, published=["method_0"], unpublished=[], only_expected_allowed=True
            )

        # An error should be raised if an expected published API object is exposed in the module (i.e., its name
        # is included in the __all__ list), but is not actually a member of said module.
        DummyModule.__all__ = ["method_0"]
        with self.assertRaises(ValueError):
            _check_public_api_contents(
                module=DummyModule, published=["method_0"], unpublished=[], only_expected_allowed=True
            )

        # An error should be raised if a given unpublished object is listed in a module's __all__ variable.
        DummyModule.method_0 = lambda: True
        with self.assertRaises(ValueError):
            _check_public_api_contents(
                module=DummyModule, published=[], unpublished=["method_0"], only_expected_allowed=True
            )

        # An error should be raised if a module contains any published API objects whose names do not show up
        # in the input expected published names list.
        DummyModule.method_1 = lambda: True
        DummyModule.__all__ = ["method_0", "method_1"]
        with self.assertRaises(ValueError):
            _check_public_api_contents(
                module=DummyModule, published=["method_0"], unpublished=[], only_expected_allowed=True
            )

        # An error should be raised if a module contains any visible API objects whose names do not show up
        # in the input visible names list (combination of the published and unpublished lists).
        DummyModule.method_2 = lambda: True
        DummyModule.scan_for_test_modules = False
        with self.assertRaises(ValueError):
            _check_public_api_contents(
                module=DummyModule, published=["method_0", "method_1"], unpublished=[], only_expected_allowed=True
            )
