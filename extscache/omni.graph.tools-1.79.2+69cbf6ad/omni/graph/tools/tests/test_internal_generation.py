"""Tests the correct generation of node type definitions into the cache"""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

import omni.graph.tools._internal as ogi
import omni.kit.test
from omni.graph.tools.tests.internal_utils import TemporaryPathAddition

from .internal_utils import CreateHelper

# Helper constants shared by many tests
_CURRENT_VERSIONS = ogi.GenerationVersions(ogi.Compatibility.FullyCompatible)
EXT_INDEX = 0


# ==============================================================================================================
class ModuleContexts:
    def __init__(self, stack: ExitStack):
        """Set up a stack of contexts to use for tests running in individual temporary directory"""
        global EXT_INDEX
        EXT_INDEX += 1
        self.ext_name = f"omni.test.internal.generation{EXT_INDEX}"
        # Put all temporary files in a temporary directory for easy disposal
        self._directory_ctx = stack.enter_context(TemporaryDirectory())  # pylint: disable=consider-using-with
        self.test_directory = Path(self._directory_ctx)
        self.module_root = Path(self.test_directory) / "exts"
        self.module_name = self.ext_name
        self.module_path = self.module_root / self.ext_name / self.module_name.replace(".", "/")
        # Add the import path of the new extension to the system path
        self.path_addition = stack.enter_context(TemporaryPathAddition(self.module_root / self.ext_name))
        # Redirect the usual node cache to the temporary directory
        self.cache_root = stack.enter_context(ogi.TemporaryCacheLocation(self.test_directory / "cache"))
        # Uncomment this to dump debugging information while the tests are running
        # self.log = stack.enter_context(ogi.TemporaryLogLocation("stdout"))


# ==============================================================================================================
class TestInternalGeneration(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None  # Diffs of file path lists can be large so let the full details be seen

    # --------------------------------------------------------------------------------------------------------------
    async def test_out_of_date_node_types(self):
        """Test that a standalone build with no cache recognizes that it needs to build the nodes"""
        incompatible = ogi.GenerationVersions(ogi.Compatibility.Incompatible)
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            creator = CreateHelper(ctx.ext_name, ctx.module_root, incompatible)
            creator.add_v1_18_node("OgnTestNode")
            creator.add_v1_18_node("OgnOtherNode")

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()
            self.assertCountEqual(
                ["OgnTestNode", "OgnOtherNode"], list(ext_contents.get_out_of_date_definitions().keys())
            )

    # --------------------------------------------------------------------------------------------------------------
    async def test_build_standalone(self):
        """Test that the caching system builds new versions of generated files when no build directory exists"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_standalone_node("OgnTestNode")
            cache_directory = ogi.full_cache_path(_CURRENT_VERSIONS, ctx.ext_name, ctx.module_name)

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()
            ext_contents.ensure_files_up_to_date()
            definition = ext_contents.node_type_definition("OgnTestNode")
            self.assertIsNotNone(definition)

            expected_files = [
                ctx.module_path / "nodes" / "OgnTestNode.ogn",
                ctx.module_path / "nodes" / "OgnTestNode.py",
                cache_directory / "__init__.py",
                cache_directory / "OgnTestNodeDatabase.py",
                cache_directory / "docs" / "OgnTestNode.rst",
                cache_directory / "tests" / "__init__.py",
                cache_directory / "tests" / "TestOgnTestNode.py",
                cache_directory / "tests" / "usd" / "OgnTestNodeTemplate.usda",
            ]
            actual_files = []
            for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                for file in files:
                    actual_files.append(Path(root) / file)
            self.assertCountEqual(expected_files, actual_files, "New files generated")

    # --------------------------------------------------------------------------------------------------------------
    async def test_no_generation(self):
        """Test that the caching system does not build anything when the built files are up to date"""
        with ExitStack() as stack:
            ctx = ModuleContexts(stack)
            ogn_directory = ctx.module_path / "ogn"

            creator = CreateHelper(ctx.ext_name, ctx.module_root, _CURRENT_VERSIONS)
            creator.add_v1_18_node("OgnTestNode")

            ext_contents = ogi.extension_contents_factory(ctx.ext_name, ctx.ext_name, ctx.module_root / ctx.ext_name)
            self.assertIsNotNone(ext_contents)
            ext_contents.scan_for_nodes()
            ext_contents.ensure_files_up_to_date()
            definition = ext_contents.node_type_definition("OgnTestNode")
            self.assertIsNotNone(definition)

            expected_files = [
                ogn_directory / "nodes" / "OgnTestNode.ogn",
                ogn_directory / "nodes" / "OgnTestNode.py",
                ogn_directory / "OgnTestNodeDatabase.py",
                ogn_directory / "tests" / "__init__.py",
                ogn_directory / "tests" / "TestOgnTestNode.py",
                ogn_directory / "tests" / "usd" / "OgnTestNodeTemplate.usda",
            ]
            actual_files = []
            for root, _dirs, files in ogi.walk_with_excludes(ctx.test_directory, ["__pycache__"]):
                for file in files:
                    actual_files.append(Path(root) / file)
            self.assertCountEqual(expected_files, actual_files, "New files generated")
