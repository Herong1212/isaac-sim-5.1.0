# pylint: disable=too-many-lines
"""Tests the correct generation of node type definitions into the cache"""
from __future__ import annotations

import sys
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.graph.tools._internal as ogi
import omni.kit.test
from omni.graph.core._impl._registration.extension_management import extension_management_factory
from omni.graph.tools.tests.internal_utils import TemporaryPathAddition

from ._internal_utils import _TestExtensionManager

# Helper constants shared by many tests
_CURRENT_VERSIONS = ogi.GenerationVersions(ogi.Compatibility.FullyCompatible)
_EXT_INDEX = 0


# ==============================================================================================================
class ModuleContexts:
    def __init__(self, stack: ExitStack):
        """Set up a stack of contexts to use for tests running in individual temporary directory"""
        global _EXT_INDEX
        _EXT_INDEX += 1
        self.ext_name = f"omni.test.internal.registration{_EXT_INDEX}"
        # Default extension version is 0.1.0 so create an ID with that
        self.ext_id = f"{self.ext_name}-0.1.0"
        # Put all temporary files in a temporary directory for easy disposal
        self.test_directory = Path(stack.enter_context(TemporaryDirectory()))  # pylint: disable=consider-using-with
        self.python_root = Path(self.test_directory) / "exts"
        self.module_name = self.ext_name
        self.module_path = self.python_root / self.ext_name / self.ext_name.replace(".", "/")
        # Redirect the usual node cache to the temporary directory
        self.cache_root = stack.enter_context(ogi.TemporaryCacheLocation(self.test_directory / "cache"))
        # Add the import path of the new extension to the system path
        self.path_addition = stack.enter_context(TemporaryPathAddition(self.python_root / self.ext_name))
        # Uncomment this to dump debugging information while the tests are running
        # self.log = stack.enter_context(ogi.TemporaryLogLocation("stdout"))


# ==============================================================================================================
def _expected_cache_contents(
    cache_root: Path, node_type_name: str, exclusions: list[ogi.FileType] = None
) -> list[Path]:
    """Returns a list of the files that should be in the generated cache at the given root for the given node type"""
    file_list = [cache_root / "__init__.py", cache_root / f"{node_type_name}Database.py"]
    if ogi.FileType.DOCS not in (exclusions or []):
        file_list.append(cache_root / "docs" / f"{node_type_name}.rst")
    if ogi.FileType.TEST not in (exclusions or []):
        file_list.append(cache_root / "tests" / "__init__.py")
        file_list.append(cache_root / "tests" / f"Test{node_type_name}.py")
    if ogi.FileType.USD not in (exclusions or []):
        file_list.append(cache_root / "tests" / "usd" / f"{node_type_name}Template.usda")
    return file_list


# ==============================================================================================================
def _expected_1_18_module_files(
    module_root: Path, node_type_name: str, exclusions: list[ogi.FileType] = None
) -> list[Path]:
    """Returns a list of the files that should be in a standard V1.18 generated module directory for one node type"""
    file_list = [
        module_root / "__init__.py",
        module_root / "ogn" / "nodes" / f"{node_type_name}.ogn",
        module_root / "ogn" / "nodes" / f"{node_type_name}.py",
        module_root / "ogn" / f"{node_type_name}Database.py",
    ]
    if ogi.FileType.TEST not in (exclusions or []):
        file_list.append(module_root / "ogn" / "tests" / "__init__.py")
        file_list.append(module_root / "ogn" / "tests" / f"Test{node_type_name}.py")
    if ogi.FileType.USD not in (exclusions or []):
        file_list.append(module_root / "ogn" / "tests" / "usd" / f"{node_type_name}Template.usda")
    return file_list


# ==============================================================================================================
def _expected_standalone_module_files(module_root: Path, node_type_name: str) -> list[Path]:
    """Returns a list of the files that should be in a non-generated module directory for one node type"""
    return [
        module_root / "__init__.py",
        module_root / "nodes" / f"{node_type_name}.ogn",
        module_root / "nodes" / f"{node_type_name}.py",
    ]


# ==============================================================================================================
class TestInternalRegistration(ogts.OmniGraphTestCase):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None  # Diffs of file path lists can be large so let the full details be seen

    # --------------------------------------------------------------------------------------------------------------
    async def _test_extension_modules(self, import_ogn: bool, import_ogn_tests: bool, generate_tests: bool):
        """Metatest that the utility to create a test extension creates the proper imports for a single configuration
        Args:
            import_ogn: Add the ogn submodule to the extension.toml python module list
            import_ogn: Add the ogn.tests submodule to the extension.toml python module list
            generate_tests: Generate/initialize test files for the node type generated code
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            self.assertTrue(str(ctx.python_root / ctx.ext_name) in sys.path)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                _CURRENT_VERSIONS,
                import_ogn=import_ogn,
                import_ogn_tests=import_ogn_tests,
            )
            exclusions = [] if generate_tests else [ogi.FileType.TEST]
            exclusions += [ogi.FileType.USD, ogi.FileType.DOCS]
            ext_contents.add_v1_18_node("OgnTestNode", exclusions)

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
            ]
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnTestNode", exclusions)

            actual_files = []
            for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                for file in files:
                    actual_files.append(Path(root) / file)
            self.assertCountEqual(expected_files, actual_files, "Created extension contents")

            ext_ogn_mgr = extension_management_factory(ctx.ext_id, ctx.ext_name, ctx.python_root / ctx.ext_name)
            self.assertIsNotNone(ext_ogn_mgr)
            ext_ogn_mgr.scan_for_nodes()
            ext_ogn_mgr.ensure_files_up_to_date()

            (ogn_module, ogn_test_module) = ext_ogn_mgr.ensure_required_modules_exist()
            self.assertIsNotNone(ogn_module)
            if generate_tests:
                self.assertIsNotNone(ogn_test_module)
            else:
                self.assertIsNone(ogn_test_module)

            await ext_contents.disable()

    # --------------------------------------------------------------------------------------------------------------
    async def test_extension_modules(self):
        """Metatest that the utility to create a test extension creates the proper modules for all configurations"""
        for test_configuration in [0b000, 0b100, 0b110, 0b001, 0b101, 0b111]:
            import_ogn = test_configuration & 0b100 != 0
            import_ogn_tests = test_configuration & 0b010 != 0
            generate_tests = test_configuration & 0b001 != 0
            with self.subTest(import_ogn=import_ogn, import_ogn_tests=import_ogn_tests, generate_tests=generate_tests):
                await self._test_extension_modules(
                    import_ogn=import_ogn, import_ogn_tests=import_ogn_tests, generate_tests=generate_tests
                )

    # --------------------------------------------------------------------------------------------------------------
    async def _test_extension_imports(self, import_ogn: bool, import_ogn_tests: bool, generate_tests: bool):
        """Metatest that the utility to create a test extension creates the proper imports for a single configuration
        Args:
            import_ogn: Add the ogn submodule to the extension.toml python module list
            import_ogn: Add the ogn.tests submodule to the extension.toml python module list
            generate_tests: Generate/initialize test files for the node type generated code
        """
        test_config = f"import_ogn={import_ogn}, import_ogn_tests={import_ogn_tests}"
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            self.assertTrue(str(ctx.python_root / ctx.ext_name) in sys.path)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                _CURRENT_VERSIONS,
                import_ogn=import_ogn,
                import_ogn_tests=import_ogn_tests,
            )
            exclusions = [] if generate_tests else [ogi.FileType.TEST]
            exclusions += [ogi.FileType.USD, ogi.FileType.DOCS]
            ext_contents.add_v1_18_node("OgnTestNode", exclusions)

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
            ]
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnTestNode", exclusions)

            actual_files = []
            for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                for file in files:
                    actual_files.append(Path(root) / file)
            self.assertCountEqual(expected_files, actual_files, f"Created extension contents using {test_config}")

            ext_ogn_mgr = extension_management_factory(ctx.ext_id, ctx.ext_name, ctx.python_root / ctx.ext_name)
            self.assertIsNotNone(ext_ogn_mgr, test_config)
            ext_ogn_mgr.scan_for_nodes()
            ext_ogn_mgr.ensure_files_up_to_date()

            # Ensure that the OGN submodules could be found in the newly created extension
            (ogn_module, ogn_test_module) = ext_ogn_mgr.ensure_required_modules_exist()
            self.assertIsNotNone(ogn_module, test_config)
            self.assertTrue(not generate_tests or ogn_test_module is not None, test_config)
            (ogn_module, ogn_test_module) = ext_ogn_mgr.do_python_imports()
            # Do it twice because the second time it should just pick it up from sys.modules
            (ogn_module_2, ogn_test_module_2) = ext_ogn_mgr.do_python_imports()
            self.assertEqual(ogn_module, ogn_module_2, test_config)
            self.assertEqual(ogn_test_module, ogn_test_module_2, test_config)

            # Check the contents of the ogn submodule to make sure the node class and database were imported
            self.assertIsNotNone(ogn_module, test_config)
            self.assertTrue(hasattr(ogn_module, ext_ogn_mgr.NODE_STORAGE_OBJECT), test_config)
            self.assertTrue(getattr(ogn_module, ext_ogn_mgr.NODE_STORAGE_OBJECT), test_config)
            self.assertTrue(hasattr(ogn_module, "OgnTestNodeDatabase"), test_config)
            ogn_module_file_path = ogi.get_module_path(ogn_module)
            self.assertIsNotNone(ogn_module_file_path, test_config)
            self.assertTrue(ctx.module_path in ogn_module_file_path.parents, test_config)

            # If tests were requested then confirm the generated tests was imported into the ogn.tests submodule
            if generate_tests:
                self.assertIsNotNone(ogn_test_module, test_config)
                self.assertTrue(hasattr(ogn_test_module, "TestOgnTestNode"), test_config)
                ogn_test_module_file_path = ogi.get_module_path(ogn_test_module)
                self.assertIsNotNone(ogn_test_module_file_path, test_config)
                self.assertTrue(ctx.module_path in ogn_test_module_file_path.parents, test_config)
            else:
                self.assertIsNone(ogn_test_module, test_config)

            await ext_contents.disable()

    # --------------------------------------------------------------------------------------------------------------
    async def test_extension_imports(self):
        """Metatest that the utility to create a test extension imports the proper modules for all configurations"""
        for test_configuration in [0b000, 0b100, 0b110, 0b001, 0b101, 0b111]:
            import_ogn = test_configuration & 0b100 != 0
            import_ogn_tests = test_configuration & 0b010 != 0
            generate_tests = test_configuration & 0b001 != 0
            with self.subTest(import_ogn=import_ogn, import_ogn_tests=import_ogn_tests, generate_tests=generate_tests):
                await self._test_extension_imports(
                    import_ogn=import_ogn, import_ogn_tests=import_ogn_tests, generate_tests=generate_tests
                )

    # --------------------------------------------------------------------------------------------------------------
    async def _test_extension_cached_imports(
        self,
        import_ogn: bool,
        import_ogn_tests: bool,
        generate_tests: bool,
        use_prebuilt_cache: bool,
    ):
        """Metatest that the utility to create a test extension creates the proper imports for a single configuration
        Args:
            import_ogn: Add the ogn submodule to the extension.toml python module list
            import_ogn: Add the ogn.tests submodule to the extension.toml python module list
            generate_tests: Generate/initialize test files for the node type generated code
            use_prebuilt_cache: If True then prebuild the up-to-date cache files, otherwise generate old ones to ignore
        """
        # ogi.set_registration_logging("stdout")  # Uncomment for test debugging information
        test_config = (
            f"import_ogn={import_ogn}, import_ogn_tests={import_ogn_tests}, "
            f"tests={generate_tests}, prebuilt={use_prebuilt_cache}"
        )
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            self.assertTrue(str(ctx.python_root / ctx.ext_name) in sys.path, test_config)
            # Create an old cache to make sure it gets ignored as well
            exclusions = [] if generate_tests else [ogi.FileType.TEST]
            exclusions += [ogi.FileType.USD, ogi.FileType.DOCS]
            ext_contents_incompatible = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                ogi.GenerationVersions(ogi.Compatibility.Incompatible),
                import_ogn=import_ogn,
                import_ogn_tests=import_ogn_tests,
            )
            ext_contents_incompatible.add_v1_18_node("OgnTestNode", exclusions)

            compatibility = ogi.Compatibility.FullyCompatible if use_prebuilt_cache else ogi.Compatibility.Incompatible
            cache_versions = ogi.GenerationVersions(compatibility)
            current_cache_directory = ogi.full_cache_path(cache_versions, ctx.ext_id, ctx.module_name)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                cache_versions,
                import_ogn=import_ogn,
                import_ogn_tests=import_ogn_tests,
            )
            ext_contents.add_cache_for_node("OgnTestNode", exclusions)

            cached_files = _expected_cache_contents(current_cache_directory, "OgnTestNode", exclusions)

            # If using the obsolete cache then add in the ones that will be built when the generator runs
            if not use_prebuilt_cache:
                current_cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
                cached_files += _expected_cache_contents(current_cache_directory, "OgnTestNode", exclusions)

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",  # Not in the cache
            ]
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnTestNode", exclusions)
            expected_files += cached_files

            ext_ogn_mgr = extension_management_factory(ctx.ext_id, ctx.ext_name, ctx.python_root / ctx.ext_name)
            self.assertIsNotNone(ext_ogn_mgr, test_config)
            ext_ogn_mgr.scan_for_nodes()
            ext_ogn_mgr.ensure_files_up_to_date()
            actual_files = []
            for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                for file in files:
                    actual_files.append(Path(root) / file)
            self.assertCountEqual(expected_files, actual_files, f"Created extension contents with {test_config}")

            # Ensure that the OGN submodules could be found in the newly created extension
            (ogn_module, ogn_test_module) = ext_ogn_mgr.do_python_imports()
            # Do it twice because the second time it should just pick it up from sys.modules
            (ogn_module_2, ogn_test_module_2) = ext_ogn_mgr.do_python_imports()
            self.assertEqual(ogn_module, ogn_module_2, test_config)
            self.assertEqual(ogn_test_module, ogn_test_module_2, test_config)

            # Check the contents of the ogn submodule to make sure the node class and database were imported
            self.assertIsNotNone(ogn_module, test_config)
            self.assertTrue(hasattr(ogn_module, ext_ogn_mgr.NODE_STORAGE_OBJECT), test_config)
            self.assertTrue(getattr(ogn_module, ext_ogn_mgr.NODE_STORAGE_OBJECT), test_config)
            self.assertTrue(hasattr(ogn_module, "OgnTestNodeDatabase"), test_config)
            ogn_module_file_path = ogi.get_module_path(ogn_module.OgnTestNodeDatabase)
            self.assertIsNotNone(ogn_module_file_path, test_config)
            self.assertTrue(
                current_cache_directory in ogn_module_file_path.parents,
                f"Cache {current_cache_directory} not in {ogn_module_file_path} - {test_config}",
            )

            # If tests were requested then confirm the generated tests was imported into the ogn.tests submodule
            if generate_tests:
                self.assertIsNotNone(ogn_test_module, test_config)
                self.assertTrue(hasattr(ogn_test_module, "TestOgnTestNode"), test_config)
                ogn_test_module_file_path = ogi.get_module_path(ogn_test_module)
                self.assertIsNotNone(ogn_test_module_file_path, test_config)
                self.assertTrue(
                    current_cache_directory in ogn_module_file_path.parents,
                    f"Cache {current_cache_directory} not in {ogn_module_file_path} - {test_config}",
                )
            else:
                self.assertIsNone(ogn_test_module, test_config)

            await ext_contents.disable()
            await ext_contents_incompatible.disable()

    # --------------------------------------------------------------------------------------------------------------
    async def test_extension_cached_imports_ffff(self):
        """Metatest that the utility to create a test extension that requires building a cache imports the proper
        modules for all configurations from that cache. These all have to run as separate tests in order to
        avoid stomping on each other's import spaces and cache directories.
        """
        await self._test_extension_cached_imports(False, False, False, False)

    async def test_extension_cached_imports_tfff(self):
        await self._test_extension_cached_imports(True, False, False, False)

    async def test_extension_cached_imports_ttff(self):
        await self._test_extension_cached_imports(True, True, False, False)

    async def test_extension_cached_imports_fftf(self):
        await self._test_extension_cached_imports(False, False, True, False)

    async def test_extension_cached_imports_tftf(self):
        await self._test_extension_cached_imports(True, False, True, False)

    async def test_extension_cached_imports_tttf(self):
        await self._test_extension_cached_imports(True, True, True, False)

    async def test_extension_cached_imports_ffft(self):
        await self._test_extension_cached_imports(False, False, False, True)

    async def test_extension_cached_imports_tfft(self):
        await self._test_extension_cached_imports(True, False, False, True)

    async def test_extension_cached_imports_ttft(self):
        await self._test_extension_cached_imports(True, True, False, True)

    async def test_extension_cached_imports_fftt(self):
        await self._test_extension_cached_imports(False, False, True, True)

    async def test_extension_cached_imports_tftt(self):
        await self._test_extension_cached_imports(True, False, True, True)

    async def test_extension_cached_imports_tttt(self):
        await self._test_extension_cached_imports(True, True, True, True)

    # --------------------------------------------------------------------------------------------------------------
    def __confirm_module_contents(self, expected_modules_and_contents: list[tuple[str, str]]):
        """Asserts if the module does not contain at least all of the expected symbols.
        Args:
            expected_modules_and_contents: List of (MODULE_NAME, EXPECTED_SYMBOLS) to verify
        """
        for expected_name, symbols in expected_modules_and_contents:
            self.assertTrue(expected_name in sys.modules, f"Looking for module {expected_name}")
            actual_contents = dir(sys.modules[expected_name])
            for expected_symbol in symbols:
                self.assertTrue(
                    expected_symbol in actual_contents, f"Looking for symbol {expected_symbol} in {expected_name}"
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_raw_extension_creation(self):
        """Metatest that the utility to create a test extension using the generated files and successfully load a
        file of the generated type into a scene.
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            self.assertTrue(str(ctx.python_root / ctx.ext_name) in sys.path)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                _CURRENT_VERSIONS,
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents.add_v1_18_node("OgnTestNode")

            ext_ogn_mgr = extension_management_factory(ctx.ext_id, ctx.ext_name, ctx.python_root / ctx.ext_name)
            self.assertIsNotNone(ext_ogn_mgr)
            ext_ogn_mgr.scan_for_nodes()
            ext_ogn_mgr.ensure_files_up_to_date()
            (ogn_module, ogn_test_module) = ext_ogn_mgr.do_python_imports()
            self.assertIsNotNone(ogn_module)
            self.assertIsNotNone(ogn_test_module)

            # Enable the extension inside Kit
            await ext_contents.enable()

            # Confirm that the test node type now exists and can be instantiated
            (_, (test_node,), _, _) = og.Controller.edit(
                "/TestGraph", {og.Controller.Keys.CREATE_NODES: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
            )
            self.assertIsNotNone(test_node)
            self.assertTrue(test_node.is_valid())

            # Confirm that the modules were correctly created
            expected_modules_and_contents = [
                (ctx.ext_name, ["_PublicExtension"]),
                (f"{ctx.ext_name}.ogn", ["OgnTestNodeDatabase"]),
                (f"{ctx.ext_name}.ogn.OgnTestNodeDatabase", ["OgnTestNodeDatabase"]),
                (f"{ctx.ext_name}.ogn.nodes.OgnTestNode", ["OgnTestNode"]),
                (f"{ctx.ext_name}.ogn.tests", ["TestOgnTestNode"]),
                (f"{ctx.ext_name}.ogn.tests.TestOgnTestNode", ["TestOgn"]),
            ]
            self.__confirm_module_contents(expected_modules_and_contents)

            # Clear the scene and disable the extension
            await omni.usd.get_context().new_stage_async()
            await ext_contents.disable()

            # Confirm that the test node type no longer exists
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {og.Controller.Keys.CREATE_NODES: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_cache_generation(self):
        """Test that an extension with no prebuilt files registers and is seen correctly.
        This entails enabling the test extension and then looking at the modules to ensure that:
            - the database exists and can be imported
            - the node type was correctly registered
            - the generated test was correctly registered
            - the database, node type, and generated test are removed when the extension is disabled
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                ogi.GenerationVersions(),
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents.add_standalone_node("OgnTestNode")
            expected_cache_files = _expected_cache_contents(cache_directory, "OgnTestNode")
            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
            ]
            expected_files += _expected_standalone_module_files(ctx.module_path, "OgnTestNode")
            expected_files += expected_cache_files

            # Register the extension and enable it
            try:
                await ext_contents.enable()

                actual_files = []
                for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                    for file in files:
                        actual_files.append(Path(root) / file)
                self.assertCountEqual(expected_files, actual_files, "Rebuilt cached extension")

                # Confirm that the test node type now exists and can be instantiated
                key_create = og.Controller.Keys.CREATE_NODES
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )
                self.assertIsNotNone(test_node)
                self.assertTrue(test_node.is_valid())

                # Confirm that the modules were correctly created
                expected_modules_and_contents = [
                    (ctx.ext_name, ["_PublicExtension"]),
                    (f"{ctx.ext_name}.nodes.OgnTestNode", ["OgnTestNode"]),
                    (f"{ctx.ext_name}.ogn", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.OgnTestNodeDatabase", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnTestNode", ["TestOgn"]),
                ]
                self.__confirm_module_contents(expected_modules_and_contents)

                # Double check the imported database file to make sure it is using the cached one
                db_object = getattr(sys.modules[f"{ctx.ext_name}.ogn.OgnTestNodeDatabase"], "OgnTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())
                ogn_module_file_path = ogi.get_module_path(sys.modules[f"{ctx.ext_name}.ogn"])
                self.assertIsNotNone(ogn_module_file_path)
                self.assertTrue(cache_directory in ogn_module_file_path.parents)

                # Clear the scene and disable the extension
                await omni.usd.get_context().new_stage_async()
            finally:
                await ext_contents.disable()

            # Confirm that the test node type no longer exists
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_cache_generation_from_old_build(self):
        """Test that an extension with prebuilt files that are out of date registers and is seen correctly.
        This entails enabling the test extension and then looking at the modules to ensure that:
            - the database exists and can be imported
            - the node type was correctly registered
            - the generated test was correctly registered
            - the database, node type, and generated test are removed when the extension is disabled
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                ogi.GenerationVersions(ogi.Compatibility.Incompatible),
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents.add_v1_18_node("OgnTestNode")

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
            ]
            expected_files += _expected_cache_contents(cache_directory, "OgnTestNode")
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnTestNode")

            # Register the extension and enable it
            try:
                await ext_contents.enable()

                actual_files = []
                for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                    for file in files:
                        actual_files.append(Path(root) / file)
                self.assertCountEqual(expected_files, actual_files, "Rebuilt cached extension")

                # Confirm that the test node type now exists and can be instantiated
                key_create = og.Controller.Keys.CREATE_NODES
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )
                self.assertIsNotNone(test_node)
                self.assertTrue(test_node.is_valid())

                # Confirm that the modules were correctly created
                expected_modules_and_contents = [
                    (ctx.ext_name, ["_PublicExtension"]),
                    (f"{ctx.ext_name}.ogn", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.nodes.OgnTestNode", ["OgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.OgnTestNodeDatabase", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnTestNode", ["TestOgn"]),
                ]
                self.__confirm_module_contents(expected_modules_and_contents)

                # Double check the version number in the imported database file to make sure it is using the cached one
                db_module = sys.modules[f"{ctx.ext_name}.ogn.OgnTestNodeDatabase"]
                db_object = getattr(db_module, "OgnTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())
                db_module_path = ogi.get_module_path(db_module)
                self.assertIsNotNone(db_module_path)
                self.assertTrue(cache_directory in db_module_path.parents)

                # Clear the scene and disable the extension
                await omni.usd.get_context().new_stage_async()
            finally:
                await ext_contents.disable()

            # Confirm that the test node type no longer exists
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_cache_update(self):
        """Test that an extension with prebuilt files that are from a compatible version but whose .ogn files are
        out of date correctly notices and rebuilds cached files and registers them correctly.
        This entails enabling the test extension and then looking at the modules to ensure that:
            - the database exists and can be imported
            - the node type was correctly registered
            - the generated test was correctly registered
            - the database, node type, and generated test are removed when the extension is disabled
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            incompatible = ogi.GenerationVersions(ogi.Compatibility.Incompatible)
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
            old_cache_directory = ogi.full_cache_path(incompatible, ctx.ext_id, ctx.module_name)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                _CURRENT_VERSIONS,
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents.add_v1_18_node("OgnTestNode")

            ext_contents_incompatible = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                incompatible,
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents_incompatible.add_cache_for_node("OgnTestNode")

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
            ]
            expected_files += _expected_cache_contents(old_cache_directory, "OgnTestNode")
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnTestNode")

            actual_files = []
            for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                for file in files:
                    actual_files.append(Path(root) / file)
            self.assertCountEqual(expected_files, actual_files, "Rebuilt cached extension")
            ogn_file = ctx.module_path / "ogn" / "nodes" / "OgnTestNode.ogn"
            ogn_file.touch()

            # Files that will be built when the cache updates after registration
            expected_cache_files = _expected_cache_contents(cache_directory, "OgnTestNode")

            # Register the extension and enable it
            try:
                await ext_contents.enable()

                actual_files = []
                for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                    for file in files:
                        actual_files.append(Path(root) / file)
                self.assertCountEqual(expected_files + expected_cache_files, actual_files, "Rebuilt cached extension")

                # Confirm that the test node type now exists and can be instantiated
                key_create = og.Controller.Keys.CREATE_NODES
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )
                self.assertIsNotNone(test_node)
                self.assertTrue(test_node.is_valid())

                # Confirm that the modules were correctly created
                expected_modules_and_contents = [
                    (ctx.ext_name, ["_PublicExtension"]),
                    (f"{ctx.ext_name}.ogn", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.nodes.OgnTestNode", ["OgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.OgnTestNodeDatabase", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnTestNode", ["TestOgn"]),
                ]
                self.__confirm_module_contents(expected_modules_and_contents)

                # Double check the version number in the imported database file to make sure it is using the cached one
                db_module = sys.modules[f"{ctx.ext_name}.ogn.OgnTestNodeDatabase"]
                db_object = getattr(db_module, "OgnTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())
                db_module_path = ogi.get_module_path(db_module)
                self.assertIsNotNone(db_module_path)
                self.assertTrue(cache_directory in db_module_path.parents)

                # Double check the path to the registered test to make sure it is using the newly generated cache
                test_module = sys.modules[f"{ctx.ext_name}.ogn.tests.TestOgnTestNode"]
                test_module_path = ogi.get_module_path(test_module)
                self.assertIsNotNone(test_module_path)
                self.assertTrue(cache_directory in test_module_path.parents)

                # Clear the scene and disable the extension
                await omni.usd.get_context().new_stage_async()
            finally:
                await ext_contents.disable()

            # Confirm that the test node type no longer exists
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_hot_reload(self):
        """Test that an extension cache is correctly generated when loading, then regenerated after a .ogn change.
        The .ogn change is such that it can be checked at runtime (adding an attribute).
        """
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                ogi.GenerationVersions(ogi.Compatibility.Incompatible),
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents.add_v1_18_node("OgnTestNode")

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
            ]
            expected_files += _expected_cache_contents(cache_directory, "OgnTestNode")
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnTestNode")

            # Register the extension and enable it
            try:
                await ext_contents.enable()

                actual_files = []
                for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                    for file in files:
                        actual_files.append(Path(root) / file)
                self.assertCountEqual(expected_files, actual_files, "Rebuilt cached extension")

                # Confirm that the test node type now exists and can be instantiated
                key_create = og.Controller.Keys.CREATE_NODES
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )
                await og.Controller.evaluate()
                self.assertIsNotNone(test_node)
                self.assertTrue(test_node.is_valid())

                # Modify the .ogn to add in a new attribute, then wait for the scene to reattach
                await ext_contents.add_hot_attribute_to_ogn()

                # This syncs are to wait for the hot reload to happen
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()

                actual_files = []
                for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                    for file in files:
                        actual_files.append(Path(root) / file)
                self.assertCountEqual(expected_files, actual_files, "After hot reload")

                # Rebuild the scene. This is necessary because the scene reattach process does not currently update any
                # modified nodes with their new attributes so the only way to test this is to create a new node and
                # check that it picks up the new definition.
                await omni.usd.get_context().new_stage_async()
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )
                await og.Controller.evaluate()
                self.assertIsNotNone(test_node)
                self.assertTrue(test_node.is_valid())

                # Confirm that the hot-reloading attribute now exists
                hot_attribute = og.Controller.attribute("inputs:hot", test_node)
                self.assertIsNotNone(hot_attribute)
                self.assertTrue(hot_attribute.is_valid())

                # Confirm that the modules were correctly created
                expected_modules_and_contents = [
                    (ctx.ext_name, ["_PublicExtension"]),
                    (f"{ctx.ext_name}.ogn", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.nodes.OgnTestNode", ["OgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.OgnTestNodeDatabase", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnTestNode", ["TestOgn"]),
                ]
                self.__confirm_module_contents(expected_modules_and_contents)

                # Double check the imported database file to make sure it is using the cached one
                db_object = getattr(sys.modules[f"{ctx.ext_name}.ogn.OgnTestNodeDatabase"], "OgnTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())
                db_file_path = ogi.get_module_path(sys.modules[f"{ctx.ext_name}.ogn.OgnTestNodeDatabase"])
                self.assertIsNotNone(db_file_path)
                self.assertTrue(
                    cache_directory in db_file_path.parents,
                    f"Expected {cache_directory} to be a parent of {db_file_path}",
                )

                # Clear the scene and disable the extension
                await omni.usd.get_context().new_stage_async()
            finally:
                await ext_contents.disable()

            # Confirm that the test node type no longer exists
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph", {key_create: [("TestNode", f"{ctx.ext_name}.OgnTestNode")]}
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_multiple_nodes(self):
        """Test that a built extension with more than one node correctly imports all of them"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                _CURRENT_VERSIONS,
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents.add_v1_18_node("OgnTestNode")
            ext_contents.add_v1_18_node("OgnGoodTestNode")

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
            ]
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnTestNode")
            expected_files += _expected_1_18_module_files(ctx.module_path, "OgnGoodTestNode")
            expected_files += _expected_cache_contents(cache_directory, "OgnTestNode")
            expected_files = list(set(expected_files))

            # Touch the .ogn file to make it out of date
            outdated_ogn = ctx.module_path / "ogn" / "nodes" / "OgnTestNode.ogn"
            outdated_ogn.touch()

            # Register the extension and enable it
            try:
                await ext_contents.enable()

                actual_files = []
                for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                    for file in files:
                        actual_files.append(Path(root) / file)
                self.assertCountEqual(expected_files, actual_files, "Rebuilt cached extension")

                # Confirm that the test node type now exists and can be instantiated
                key_create = og.Controller.Keys.CREATE_NODES
                (_, (test_node, test_good_node), _, _) = og.Controller.edit(
                    "/TestGraph",
                    {
                        key_create: [
                            ("TestNode", f"{ctx.ext_name}.OgnTestNode"),
                            ("GoodTestNode", f"{ctx.ext_name}.OgnGoodTestNode"),
                        ]
                    },
                )
                self.assertIsNotNone(test_node)
                self.assertTrue(test_node.is_valid())
                self.assertIsNotNone(test_good_node)
                self.assertTrue(test_good_node.is_valid())

                # Confirm that the modules were correctly created
                expected_modules_and_contents = [
                    (ctx.ext_name, ["_PublicExtension"]),
                    (f"{ctx.ext_name}.ogn", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.nodes.OgnTestNode", ["OgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.OgnTestNodeDatabase", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnTestNode", ["TestOgn"]),
                    (f"{ctx.ext_name}.ogn.OgnGoodTestNodeDatabase", ["OgnGoodTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnGoodTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnGoodTestNode", ["TestOgn"]),
                ]
                self.__confirm_module_contents(expected_modules_and_contents)

                # Double check the version number in the imported database file to make sure it is using the cached one
                db_module = sys.modules[f"{ctx.ext_name}.ogn.OgnTestNodeDatabase"]
                db_object = getattr(db_module, "OgnTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the cached database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())

                db_module_path = ogi.get_module_path(db_module)
                self.assertIsNotNone(db_module_path)
                self.assertTrue(cache_directory in db_module_path.parents)

                test_module = sys.modules[f"{ctx.ext_name}.ogn.tests.TestOgnTestNode"]
                test_object = getattr(test_module, "TestOgn", None)
                self.assertIsNotNone(test_object, "Could not get the cached test from the extension imports")
                test_module_path = ogi.get_module_path(test_module)
                self.assertIsNotNone(test_module_path)
                self.assertTrue(cache_directory in test_module_path.parents)

                # Check that the node that did not have to be rebuilt imports from the build directory, not the cache
                db_module = sys.modules[f"{ctx.ext_name}.ogn.OgnGoodTestNodeDatabase"]
                db_object = getattr(db_module, "OgnGoodTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the built database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())

                db_module_path = ogi.get_module_path(db_module)
                self.assertIsNotNone(db_module_path)
                self.assertTrue(ctx.module_path in db_module_path.parents)

                test_module = sys.modules[f"{ctx.ext_name}.ogn.tests.TestOgnGoodTestNode"]
                test_object = getattr(test_module, "TestOgn", None)
                self.assertIsNotNone(test_object, "Could not get the built test from the extension imports")
                test_module_path = ogi.get_module_path(test_module)
                self.assertIsNotNone(test_module_path)
                self.assertTrue(ctx.module_path in test_module_path.parents)

                # Clear the scene and disable the extension
                await omni.usd.get_context().new_stage_async()
            finally:
                await ext_contents.disable()

            # Confirm that the test node type no longer exists
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph",
                    {
                        key_create: [
                            ("TestNode", f"{ctx.ext_name}.OgnTestNode"),
                        ]
                    },
                )
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph",
                    {
                        key_create: [
                            ("GoodTestNode", f"{ctx.ext_name}.OgnGoodTestNode"),
                        ]
                    },
                )

    # --------------------------------------------------------------------------------------------------------------
    async def test_multiple_standalone_nodes(self):
        """Test that a built extension with more than one node without generation correctly imports all of them"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_id, ctx.module_name)
            ext_contents = _TestExtensionManager(
                ctx.python_root,
                ctx.ext_name,
                _CURRENT_VERSIONS,
                import_ogn=False,
                import_ogn_tests=False,
            )
            ext_contents.add_standalone_node("OgnTestNode")
            ext_contents.add_standalone_node("OgnGoodTestNode")

            expected_files = [
                ctx.python_root / ctx.ext_name / "config" / "extension.toml",
                ctx.module_path / "__init__.py",
            ]
            expected_files += _expected_standalone_module_files(ctx.module_path, "OgnTestNode")
            expected_files += _expected_standalone_module_files(ctx.module_path, "OgnGoodTestNode")
            expected_files += _expected_cache_contents(cache_directory, "OgnTestNode")
            expected_files += _expected_cache_contents(cache_directory, "OgnGoodTestNode")
            expected_files = list(set(expected_files))

            # Register the extension and enable it
            try:
                await ext_contents.enable()

                actual_files = []
                for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                    for file in files:
                        actual_files.append(Path(root) / file)
                self.assertCountEqual(expected_files, actual_files, "Rebuilt cached extension")

                # Confirm that the test node type now exists and can be instantiated
                key_create = og.Controller.Keys.CREATE_NODES
                (_, (test_node, test_good_node), _, _) = og.Controller.edit(
                    "/TestGraph",
                    {
                        key_create: [
                            ("TestNode", f"{ctx.ext_name}.OgnTestNode"),
                            ("GoodTestNode", f"{ctx.ext_name}.OgnGoodTestNode"),
                        ]
                    },
                )
                self.assertIsNotNone(test_node)
                self.assertTrue(test_node.is_valid())
                self.assertIsNotNone(test_good_node)
                self.assertTrue(test_good_node.is_valid())

                # Confirm that the modules were correctly created
                expected_modules_and_contents = [
                    (ctx.ext_name, ["_PublicExtension"]),
                    (f"{ctx.ext_name}.nodes.OgnTestNode", ["OgnTestNode"]),
                    (f"{ctx.ext_name}.ogn", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.OgnTestNodeDatabase", ["OgnTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnTestNode", ["TestOgn"]),
                    (f"{ctx.ext_name}.nodes.OgnGoodTestNode", ["OgnGoodTestNode"]),
                    (f"{ctx.ext_name}.ogn", ["OgnGoodTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.OgnGoodTestNodeDatabase", ["OgnGoodTestNodeDatabase"]),
                    (f"{ctx.ext_name}.ogn.tests", ["TestOgnGoodTestNode"]),
                    (f"{ctx.ext_name}.ogn.tests.TestOgnGoodTestNode", ["TestOgn"]),
                ]
                self.__confirm_module_contents(expected_modules_and_contents)

                # Double check the version number in the imported database file to make sure it is using the cached one
                db_module = sys.modules[f"{ctx.ext_name}.ogn.OgnTestNodeDatabase"]
                db_object = getattr(db_module, "OgnTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the cached database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())

                db_module_path = ogi.get_module_path(db_module)
                self.assertIsNotNone(db_module_path)
                self.assertTrue(cache_directory in db_module_path.parents)

                test_module = sys.modules[f"{ctx.ext_name}.ogn.tests.TestOgnTestNode"]
                test_object = getattr(test_module, "TestOgn", None)
                self.assertIsNotNone(test_object, "Could not get the cached test from the extension imports")
                test_module_path = ogi.get_module_path(test_module)
                self.assertIsNotNone(test_module_path)
                self.assertTrue(cache_directory in test_module_path.parents)

                # Check that the node that did not have to be rebuilt imports from the build directory, not the cache
                db_module = sys.modules[f"{ctx.ext_name}.ogn.OgnGoodTestNodeDatabase"]
                db_object = getattr(db_module, "OgnGoodTestNodeDatabase", None)
                self.assertIsNotNone(db_object, "Could not get the built database from the extension imports")
                generator_version = getattr(db_object, ogi.VersionProperties.GENERATOR.value, None)
                self.assertEqual(generator_version, ogi.get_generator_extension_version())
                target_version = getattr(db_object, ogi.VersionProperties.TARGET.value, None)
                self.assertEqual(target_version, ogi.get_target_extension_version())

                db_module_path = ogi.get_module_path(db_module)
                self.assertIsNotNone(db_module_path)
                self.assertTrue(
                    cache_directory in db_module_path.parents, f"{db_module_path} must be a child of {cache_directory}"
                )

                test_module = sys.modules[f"{ctx.ext_name}.ogn.tests.TestOgnGoodTestNode"]
                test_object = getattr(test_module, "TestOgn", None)
                self.assertIsNotNone(test_object, "Could not get the built test from the extension imports")
                test_module_path = ogi.get_module_path(test_module)
                self.assertIsNotNone(test_module_path)
                self.assertTrue(cache_directory in test_module_path.parents)

                # Clear the scene and disable the extension
                await omni.usd.get_context().new_stage_async()
            finally:
                await ext_contents.disable()

            # Confirm that the test node type no longer exists
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph",
                    {
                        key_create: [
                            ("TestNode", f"{ctx.ext_name}.OgnTestNode"),
                        ]
                    },
                )
            with self.assertRaises(og.OmniGraphError):
                (_, (test_node,), _, _) = og.Controller.edit(
                    "/TestGraph",
                    {
                        key_create: [
                            ("GoodTestNode", f"{ctx.ext_name}.OgnGoodTestNode"),
                        ]
                    },
                )

    async def test_node_release(self):
        """Helper Python node that verifies that release was called"""

        class OgnReleaseTest:
            TEST_FAILED = True

            @staticmethod
            def compute(context: og.GraphContext, node: og.Node):
                return True

            @staticmethod
            def get_node_type() -> str:
                return "omni.graph.OgnReleaseTest"

            @staticmethod
            def release(node):
                print("omni.graph.OgnReleaseTest: release() called")
                OgnReleaseTest.TEST_FAILED = False

        og.register_node_type(OgnReleaseTest, 1)

        controller = og.Controller()
        keys = og.Controller.Keys
        _ = controller.edit("/TestGraph", {keys.CREATE_NODES: [("Test", "omni.graph.OgnReleaseTest")]})
        await controller.evaluate()

        og.deregister_node_type(OgnReleaseTest.get_node_type())

        self.assertTrue("omni.graph.OgnReleaseTest" not in og.get_registered_nodes())
        self.assertFalse(OgnReleaseTest.TEST_FAILED)
