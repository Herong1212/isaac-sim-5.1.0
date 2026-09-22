"""Low level testing for the omnigraph_metadata repo tool functionality.

As full testing relies on enabled extensions containing nodes that type of test is in the downstream extension
omni.graph.test. All that is tested here is directory scanning using the omni.graph.image.nodes extension
"""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import carb
import omni.graph.tools as ogt
import omni.kit.test
from omni.graph.tools._impl.repo_tools.generate_node_metadata import OgnScanError, generate_node_metadata


# ==============================================================================================================
class TestMetadataGenerator(omni.kit.test.AsyncTestCase):
    async def test_scan(self):
        """Test the scanning of a directory known to contain node type definitions"""
        root_directory = Path(carb.tokens.get_tokens_interface().resolve("${kit}"))
        ext_name = "omni.graph.image.nodes"
        ext_path = root_directory / "exts" / ext_name

        metadata = ogt.build_directory_metadata(ext_path, destination=None)
        self.assertCountEqual(["extension", "nodes"], list(metadata))
        # Version number isn't appended when scanning directories
        self.assertEqual(metadata["extension"], ext_name)

        # Do not use an exact number so that the test continues to work if more node types are added
        self.assertTrue(len(metadata["nodes"]) > 5)

        # Also check that the file output works
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            tmp_fd = NamedTemporaryFile(dir=tmp_dir, suffix=".json", delete=False)
            tmp_fd.close()
            fd_metadata = ogt.build_directory_metadata(ext_path, destination=Path(tmp_fd.name))
            self.assertEqual(metadata, fd_metadata)
            with open(tmp_fd.name, "r", encoding="utf-8") as result_fd:
                result_metadata = json.load(result_fd)
            self.assertEqual(fd_metadata, result_metadata)

    async def test_scan_with_repo_tool(self):
        """
        Test the scanning of a directory known to contain node type definitions
        using the corresponding repo_tool wrapper.
        """
        root_directory = Path(carb.tokens.get_tokens_interface().resolve("${kit}"))
        ext_name = "omni.graph.image.nodes"
        ext_path = root_directory / "exts" / ext_name
        generate_node_metadata(["-r", str(ext_path), "-d", None, "-l", "DEBUG"])

    async def test_scan_error_handling(self):
        """Test the error handling of the node metadata generation tools"""

        # Directory without any .ogn files.
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            json_fd = NamedTemporaryFile(dir=tmp_dir, suffix=".json")
            self.assertEqual({}, ogt.build_directory_metadata(tmp_dir, destination=None))
            json_fd.close()

        # Directory with an empty (i.e. invalid) .ogn file.
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            ogn_fd = NamedTemporaryFile(dir=tmp_dir, suffix=".ogn", delete=False)
            ogn_fd.close()
            _ = Path(ogn_fd.name)
            with self.assertRaises(OgnScanError):
                _ = ogt.build_directory_metadata(tmp_dir, destination=None)
            ogn_fd.close()

        # Exercise the OgnScanError object.
        _ = OgnScanError(problem="Worrisome problem", path="path", ogn_files_failed=None)
        _ = OgnScanError(problem="Worrisome problem", path=None, ogn_files_failed=["my_file.ogn"])
        _ = OgnScanError(problem="Worrisome problem")

        # repo_tool with invalid logger setting.
        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            with self.assertRaises(ValueError):
                generate_node_metadata(["-r", str(tmp_dir), "-d", None, "-l", "INVALID"])
