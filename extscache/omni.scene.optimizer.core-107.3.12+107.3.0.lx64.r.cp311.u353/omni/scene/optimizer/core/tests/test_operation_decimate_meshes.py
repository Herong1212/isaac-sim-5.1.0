__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import filecmp
import os
import tempfile

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdUtils, Vt

from .test_utils import Test_Operation, _get_test_data_file_path

DEFAULT_ARGS = {
    "paths": [],
    "reductionFactor": 0.0,
    "maxMeanError": 0.1,
    "cpuVertexCountThreshold": 100000,
    "gpuVertexCountThreshold": 500000,
    "pinBoundaries": False,
}


def _get_meshes(stage):
    return [x for x in stage.TraverseAll() if x.IsA(UsdGeom.Mesh)]


class Test_Operation_DecimateMeshes(Test_Operation):

    OPERATION = "decimateMeshes"
    WRITE_TEST_RESULTS = False

    # Ensures files are converted to linux line breaks to be ready for comparison.
    def convert_crlf_to_lf(self, file_path):
        WINDOWS_LINE_ENDING = b"\r\n"
        UNIX_LINE_ENDING = b"\n"
        with open(file_path, "rb") as open_file:
            content = open_file.read()
        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
        with open(file_path, "wb") as open_file:
            open_file.write(content)

    # Safe a stage to file.
    async def save_stage_in_usd_context_async(self, stage, file_path):
        # Export the root layer on the assumption that it holds all the opinions needed for diff.
        # We export rather than using "save_as_stage_async" to avoid the default custom metadata being added.
        stage.GetRootLayer().Export(file_path)
        self.convert_crlf_to_lf(file_path)

    def compare_files(self, golden_file_path, result_file_path):
        result = filecmp.cmp(golden_file_path, result_file_path, False)
        if result:
            return result

        # For debugging, when regressions occur
        print(
            "A result file does not match the corresponding golden file. Consider updating the golden file in case the change is intended."
        )  # pragma: no cover

        print(
            "In case the change affects many golden files, consider regenerating all golden files by setting WRITE_TEST_RESULTS to True."
        )  # pragma: no cover

        print("Expected:", golden_file_path)  # pragma: no cover
        print("  Actual:", result_file_path)  # pragma: no cover

        return result  # pragma: no cover

    async def save_and_compare_golden_file(self, stage, golden_file_path, result_name):
        """Save a stage to a file and then assert that it matches the expected
        golden file.
        """

        if self.WRITE_TEST_RESULTS:  # pragma: no cover
            await self.save_stage_in_usd_context_async(stage, golden_file_path)
            return

        # Manually build a temporary filename.
        # Note: this is done manually in order to keep the output file if the assert
        # fails, for easier debugging.
        result_file_path = os.path.join(tempfile.gettempdir(), result_name)

        await self.save_stage_in_usd_context_async(stage, result_file_path)
        self.assertTrue(self.compare_files(golden_file_path, result_file_path))

        # On success, clean up the temp file.
        os.remove(result_file_path)

    async def test_decimate_merge_colocated_vertices(self):
        """Test decimate functions handling of meshes with unmerged colocated vertices"""
        stage = self._open_stage("mergeColocatedVertices_input.usd")
        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 2)

        file_path = _get_test_data_file_path("mergeColocatedVertices_output.usd")
        expected_stage = Usd.Stage.Open(file_path)
        after_meshes = _get_meshes(expected_stage)
        self.assertEqual(len(before_meshes), len(after_meshes))

        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            after_mesh = UsdGeom.Mesh(after_meshes[i])
            # before operation, the vertices have not been merged
            self.assertGreaterEqual(len(mesh.GetPointsAttr().Get()), len(after_mesh.GetPointsAttr().Get()))
            # some degenerate faces have been removed, so faces will not match
            self.assertGreaterEqual(
                len(mesh.GetFaceVertexCountsAttr().Get()), len(after_mesh.GetFaceVertexCountsAttr().Get())
            )

        self._execute_json(stage, "decimateSceneNoOp.json")

        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            after_mesh = UsdGeom.Mesh(after_meshes[i])
            # after operation, colocated vertices have been merged
            self.assertEqual(len(mesh.GetPointsAttr().Get()), len(after_mesh.GetPointsAttr().Get()))
            # face count should remain the same as before, if this fails mesh decimation has occurred
            self.assertEqual(len(mesh.GetFaceVertexCountsAttr().Get()), len(after_mesh.GetFaceVertexCountsAttr().Get()))

    async def test_decimate_reduction_by_half(self):
        """Test decimate function, reducing vertex count by 50%"""
        stage = self._open_stage("simpleCube.usda")
        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 1)

        old_face_counts = []
        old_vertex_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        args = DEFAULT_ARGS.copy()
        args["maxMeanError"] = 0.0
        args["reductionFactor"] = 50.0
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertGreater(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))
            self.assertGreater(old_vertex_counts[i], len(mesh.GetPointsAttr().Get()))
            self.assertEqual(old_vertex_counts[i] // 2, len(mesh.GetPointsAttr().Get()))

    async def test_decimate_reduction_by_half_one_mesh(self):
        """Test decimate function, reducing vertex count by 50% for specified paths"""
        stage = self._open_stage("simpleFourCubes.usda")
        target_prim_path = "/World/Cube_02"

        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 4)

        old_face_counts = []
        old_vertex_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        args = DEFAULT_ARGS.copy()
        args["paths"] = [target_prim_path]
        args["maxMeanError"] = 0.0
        args["reductionFactor"] = 50.0
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        # Assert that the mesh reduction has taken place, but only for the selected prim path
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            if mesh.GetPath() == target_prim_path:
                self.assertGreater(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))
                self.assertEqual(old_vertex_counts[i] // 2, len(mesh.GetPointsAttr().Get()))
            else:
                self.assertEqual(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))
                self.assertEqual(old_vertex_counts[i], len(mesh.GetPointsAttr().Get()))

    async def test_decimate_reduction_using_hierarchy(self):
        """Test decimate function, giving root prim as input"""
        stage = self._open_stage("simpleCube.usda")
        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 1)

        old_face_counts = []
        old_vertex_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        args = DEFAULT_ARGS.copy()
        args["maxMeanError"] = 0.0
        args["reductionFactor"] = 50.0
        args["paths"] = ["/World//"]
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertGreater(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))
            self.assertGreater(old_vertex_counts[i], len(mesh.GetPointsAttr().Get()))
            self.assertEqual(old_vertex_counts[i] // 2, len(mesh.GetPointsAttr().Get()))

    async def test_decimate_reduction_single_threaded(self):
        """Test decimate function, reducing vertex count by 50%, single-threaded operation"""
        stage = self._open_stage("maxDataVolumePartial.usd")

        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 55)

        old_vertex_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        self._execute_json(stage, "decimateSceneByHalfSingleThreaded.json")

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertEqual(old_vertex_counts[i] // 2, len(mesh.GetPointsAttr().Get()))

    async def test_decimate_reduction_parallel(self):
        """Test decimate function, reducing vertex count by 50%, multi-threaded operation"""
        stage = self._open_stage("maxDataVolumePartial.usd")

        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 55)

        old_face_counts = []
        old_vertex_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        self._execute_json(stage, "decimateSceneByHalf.json")

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertGreater(old_vertex_counts[i], len(mesh.GetPointsAttr().Get()))
            self.assertEqual(old_vertex_counts[i] // 2, len(mesh.GetPointsAttr().Get()))

    async def test_decimate_reduction_parallel_gpu(self):
        """Test decimate function, reducing vertex count by 50%, multi-threaded operation on GPU"""
        stage = self._open_stage("maxDataVolumePartial.usd")

        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 55)

        old_face_counts = []
        old_vertex_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        self._execute_json(stage, "decimateSceneByHalfGPU.json")

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertGreater(old_vertex_counts[i], len(mesh.GetPointsAttr().Get()))
            self.assertEqual(old_vertex_counts[i] // 2, len(mesh.GetPointsAttr().Get()))

    async def test_decimate_pin_boundaries(self):
        """Test decimate function, reducing vertex count by 50%, multi-threaded operation with pinned boundaries"""
        stage = self._open_stage("maxDataVolumePartial.usda")

        args = DEFAULT_ARGS.copy()
        args["paths"] = []
        args["maxMeanError"] = 0.0
        args["reductionFactor"] = 50.0
        args["pinBoundaries"] = True
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        golden_file_path = _get_test_data_file_path("maxDataVolumePartial_decimate_pinBoundaries_golden.usda")
        await self.save_and_compare_golden_file(
            stage, golden_file_path, "maxDataVolumePartial_decimate_pinBoundaries_result.usda"
        )

    async def test_decimate_max_mean_error_single_threaded(self):
        """Test decimate function, using 0.25 for maxMeanError, single-threaded operation"""
        stage = self._open_stage("maxDataVolumePartial.usda")

        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 55)

        old_face_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))

        self._execute_json(stage, "decimateSceneMaxMeanErrorSingleThreaded.json")

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertGreater(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))

        golden_file_path = _get_test_data_file_path("maxDataVolumePartial_decimate_golden.usda")
        await self.save_and_compare_golden_file(
            stage, golden_file_path, "maxDataVolumePartial_decimate_singlethreaded_result.usda"
        )

    async def test_decimate_max_mean_error_parallel(self):
        """Test decimate function, using 0.25 for maxMeanError, multi-threaded operation"""
        stage = self._open_stage("maxDataVolumePartial.usda")

        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 55)

        old_face_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))

        self._execute_json(stage, "decimateSceneMaxMeanError.json")

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertGreater(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))

        golden_file_path = _get_test_data_file_path("maxDataVolumePartial_decimate_golden.usda")
        await self.save_and_compare_golden_file(
            stage, golden_file_path, "maxDataVolumePartial_decimate_parallel_result.usda"
        )

    async def test_decimate_invalid_mesh(self):
        """Test decimate function on a mesh that is invalid (fewer vertices than referenced by face vertex indices)"""
        stage = self._open_stage("sealing_invalid_mesh.usda")

        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 1)

        old_face_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))

        self._execute_json(stage, "decimateSceneByHalfSingleThreaded.json")

        # Assert that mesh has not been removed from the scene even though it is invalid
        after_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), len(after_meshes))

        # Assert that no mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertEqual(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))

    async def test_decimate_time_varying_mesh(self):
        """Test decimate operation on a mesh with time varying attributes, the mesh should not be processed"""
        stage = self._open_stage("time_varying_mesh.usd")

        # currently skipping time sampled meshes to avoid a crash
        # test to be expanded when time samples are better handled in the operation
        # _execute_json asserts success of execution
        self._execute_json(stage, "decimateSceneByHalfSingleThreaded.json")
