"""Unit testing for the build process that generates OmniGraph node document index files."""

import importlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import carb
import omni.kit.test
from omni.graph.tools._impl.node_generator.main_docs import main_docs


# ==============================================================================================================
class TestMainDocs(omni.kit.test.AsyncTestCase):
    async def test_main_docs(self):
        """Test the generation of documentation in a directory known to contain node type definitions"""
        docs_script_path = carb.tokens.get_tokens_interface().resolve("${omni.graph.tools}") + "/omni/graph/tools"

        ext_path = Path(__file__).parent / "extensions"

        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            old_args = sys.argv
            sys.argv = [
                "make_docs_toc.py",
                "--ognDirectory",
                str(tmp_dir),
                "--extensionRoot",
                str(ext_path),
                "--extensionRoot",
                str(ext_path / "omni.graph.scaffolding"),
                "--warningsOnly",
                "--verbose",
                "--veryVerbose",
            ]

            # The path must be temporarily updated to let relative imports work. The test is run through the
            # make_docs_toc.py script so that everything is covered, not just the implementation.
            sys.path.append(str(docs_script_path))
            _ = importlib.import_module("omni.graph.tools.make_docs_toc")
            sys.path.remove(str(docs_script_path))
            sys.argv = old_args

            by_category = tmp_dir / "index.rst"
            by_extension = tmp_dir / "byExtension.rst"
            self.assertTrue(by_category.is_file())
            self.assertTrue(by_extension.is_file())

            # Run again to hit the changed contents case.
            with open(by_category, "a", encoding="utf-8") as cat_fd:
                cat_fd.write("New stuff\n")
            with open(by_extension, "a", encoding="utf-8") as ext_fd:
                ext_fd.write("New stuff\n")
            main_docs(
                [
                    "--ognDirectory",
                    str(tmp_dir),
                    "--extensionRoot",
                    str(ext_path),
                    "--extensionRoot",
                    str(ext_path / "omni.graph.scaffolding"),
                    "--warningsOnly",
                    "--verbose",
                    "--veryVerbose",
                ]
            )

            # Check that each node type was mentioned in the category index
            patterns = ["omni_graph_node1", "omni_graph_node2", "omni_graph_node3"]
            found = [0, 0, 0]
            with open(by_category, "r", encoding="utf-8") as fd:
                for line in fd.readlines():
                    for index, pattern in enumerate(patterns):
                        if line.find(pattern) >= 0:
                            found[index] += 1
            self.assertEqual([1, 1, 1], found)

            # Check that each node type was mentioned in the extension index
            found = [0, 0, 0]
            with open(by_extension, "r", encoding="utf-8") as fd:
                for line in fd.readlines():
                    for index, pattern in enumerate(patterns):
                        if line.find(pattern) >= 0:
                            found[index] += 1
            self.assertEqual([1, 1, 1], found)
