# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import pathlib

import omni.kit.app
import omni.kit.test
from pxr import Gf, Usd

from .. import array_const
from ..array_params import ArrayParams
from ..extension import CreateArrayCommand

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
DATA_DIR = EXTENSION_FOLDER_PATH.joinpath("omni/tools/array/tests/data")


class TestArrayCoreCommand(omni.kit.test.AsyncTestCase):
    # inherits from async test case
    def setUp(self):
        self._results_stage = self._open_stage("results_one_d_two_d_three_d")
        self._source_stage = self._open_stage("source_one_d_two_d_three_d")
        self._results_neg_zero_stage = self._open_stage("results_negative_zero_counts")
        self._source_neg_zero_stage = self._open_stage("source_negative_zero_counts")
        self._small_number = 1e-5

    # inherits from async test case
    def tearDown(self):
        self._results_stage = None
        self._source_stage = None
        self._results_neg_zero_stage = None
        self._source_neg_zero_stage = None

    # One D, Preview On
    async def test_array_one_d(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/One_D/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.PREVIEW] = True
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/One_D")
        self.assertTrue(results[0], results[1])

    # Two D, Preview Off
    async def test_array_two_d(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Two_D/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.PREVIEW] = False
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.TWO_D_COUNT] = 2
        array_values[array_const.TWO_D_OFFSET] = Gf.Vec3d(0, 125, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Two_D")
        self.assertTrue(results[0], results[1])

    # Three D, Preview Off
    async def test_array_three_d(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Three_D/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.PREVIEW] = False
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.TWO_D_COUNT] = 2
        array_values[array_const.TWO_D_OFFSET] = Gf.Vec3d(0, 125, 0)
        array_values[array_const.THREE_D_COUNT] = 2
        array_values[array_const.THREE_D_OFFSET] = Gf.Vec3d(0, 0, 125)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Three_D")
        self.assertTrue(results[0], results[1])

    # Create instances - proper setup
    async def test_create_instances_proper(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Instances_Proper_Setup/Cube_Parent"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.INSTANCES
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Instances_Proper_Setup")
        self.assertTrue(results[0], results[1])

    # Create instances - improper setup
    async def test_create_instances_improper(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Instances_Improper_Setup/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.INSTANCES
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Instances_Improper_Setup")
        self.assertTrue(results[0], results[1])

    # Create instances - mixed setup
    async def test_create_instances_mixed(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Instances_Mixed_Setup/Cube"))
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Instances_Mixed_Setup/Xform"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.INSTANCES
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Instances_Mixed_Setup")
        self.assertTrue(results[0], results[1])

    # Copying: Instances/Instanceable, References
    async def test_copy_instanceable_references(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        # Instances/Instanceable
        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Instanceable/Cube_Parent"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Instanceable")
        self.assertTrue(results[0], results[1])

        # References
        source_prims.clear()
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Reference/Cube_Parent_Reference"))

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Reference")
        self.assertTrue(results[0], results[1])

    # Group & Select
    async def test_group_select(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Group_Select/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.ARRAY_GROUP_RESULT] = True
        array_values[array_const.AUTO_SELECT_CREATED] = True
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        creation_results = self._run_create_array_command(source_prims, array_values)

        results_parent = self._get_prim_from_stage(self._results_stage, "/World/Group_Select")
        source_parent = self._get_prim_from_stage(self._source_stage, "/World/Group_Select")

        results = self._compare_results(source_parent, results_parent, True, creation_results[2])
        self.assertTrue(results[0], results[1])

    # Select Only
    async def test_select_results(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Select/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.AUTO_SELECT_CREATED] = True
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        creation_results = self._run_create_array_command(source_prims, array_values)

        results_parent = self._get_prim_from_stage(self._results_stage, "/World/Select")
        source_parent = self._get_prim_from_stage(self._source_stage, "/World/Select")

        results = self._compare_results(source_parent, results_parent, True, creation_results[2])
        self.assertTrue(results[0], results[1])

    # Follow Rotations
    async def test_follow_rotations(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Follow_Rot/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.INC_ROTATE] = Gf.Vec3d(0, 0, 5)
        array_values[array_const.REORIENT_ROTATION] = True
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Follow_Rot")
        self.assertTrue(results[0], results[1])

    # Follow Rotations with rotations already applied on the source prim
    async def test_follow_rotations_offset(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Follow_Rot_Offset/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.INC_ROTATE] = Gf.Vec3d(0, 0, 5)
        array_values[array_const.REORIENT_ROTATION] = True
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Follow_Rot_Offset")
        self.assertTrue(results[0], results[1])

    # Different Op Types
    async def test_different_op_types(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Diff_Op_Types/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Diff_Op_Types")
        self.assertTrue(results[0], results[1])

    # Missing Ops
    async def test_missing_ops(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Missing_Ops/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Missing_Ops")
        self.assertTrue(results[0], results[1])

    # Orient Op instead of Rotate op
    async def test_orient_op(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Orient_Op/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.INC_ROTATE] = Gf.Vec3d(0, 0, 1)
        array_values[array_const.TWO_D_COUNT] = 2
        array_values[array_const.TWO_D_OFFSET] = Gf.Vec3d(0, 125, 0)
        array_values[array_const.THREE_D_COUNT] = 2
        array_values[array_const.THREE_D_OFFSET] = Gf.Vec3d(0, 0, 125)
        array_values[array_const.REORIENT_ROTATION] = True
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Orient_Op")
        self.assertTrue(results[0], results[1])

    # No prims provided
    async def test_empty_prims(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        creation_results = self._run_create_array_command(source_prims, array_values)

        self.assertIsNone(creation_results)

    # No array values provided
    async def test_empty_array_values(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/One_D/Cube"))

        array_values = {}

        creation_results = self._run_create_array_command(source_prims, array_values)

        self.assertIsNone(creation_results)

    # Missing array values
    async def test_missing_array_values(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/One_D/Cube"))

        array_values = {}
        array_values[array_const.COUNT] = 10

        creation_results = self._run_create_array_command(source_prims, array_values)

        self.assertIsNone(creation_results)

    # Non-Xformables
    async def test_non_xformables(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Non_Xformable/Scope"))
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Non_Xformable/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Non_Xformable")
        self.assertTrue(results[0], results[1])

    # Negative/zero counts - 1D/2D/3D
    async def test_negative_and_zero_counts(self):
        self._set_active_stage("source_negative_zero_counts")

        array_values = self._construct_new_array()
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.TWO_D_OFFSET] = Gf.Vec3d(0, 125, 0)
        array_values[array_const.THREE_D_OFFSET] = Gf.Vec3d(0, 0, 125)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        # One D Neg
        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_neg_zero_stage, "/World/One_D_Neg/Cube"))
        array_values[array_const.COUNT] = -3
        array_values[array_const.TWO_D_COUNT] = 2
        array_values[array_const.THREE_D_COUNT] = 5
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_neg_zero_stage, self._source_neg_zero_stage, "/World/One_D_Neg")
        self.assertTrue(results[0], results[1])

        # Two D Neg
        source_prims.clear()
        source_prims.append(self._get_prim_from_stage(self._source_neg_zero_stage, "/World/Two_D_Neg/Cube"))
        array_values[array_const.COUNT] = 6
        array_values[array_const.TWO_D_COUNT] = -2
        array_values[array_const.THREE_D_COUNT] = 5
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_neg_zero_stage, self._source_neg_zero_stage, "/World/Two_D_Neg")
        self.assertTrue(results[0], results[1])

        # Three D Neg
        source_prims.clear()
        source_prims.append(self._get_prim_from_stage(self._source_neg_zero_stage, "/World/Three_D_Neg/Cube"))
        array_values[array_const.COUNT] = 6
        array_values[array_const.TWO_D_COUNT] = 2
        array_values[array_const.THREE_D_COUNT] = -5
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_neg_zero_stage, self._source_neg_zero_stage, "/World/Three_D_Neg")
        self.assertTrue(results[0], results[1])

    # Parent/Child
    async def test_parent_child(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Parent_Child/Cube"))
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Parent_Child/Cube/Torus"))

        array_values = self._construct_new_array()
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Parent_Child")
        self.assertTrue(results[0], results[1])

    # Timesampled
    async def test_timesampled(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Timesampled/Timesampled_Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Timesampled")
        self.assertTrue(results[0], results[1])

    # Instance Proxies (Copies)
    async def test_instance_proxies(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Instance_Proxy/Xform_01/Cube"))

        array_values = self._construct_new_array()
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)
        array_values[array_const.CREATE_TYPE] = array_const.CreateType.COPIES

        creation_results = self._run_create_array_command(source_prims, array_values)

        self.assertTrue(creation_results, ([], [], []))

    # Unit Resolve Ops - Ops added by the Metrics Assembler extension to correct mismatched scales and rotations
    async def test_unit_resolve_ops(self):
        self._set_active_stage("source_one_d_two_d_three_d")

        source_prims = []
        source_prims.append(self._get_prim_from_stage(self._source_stage, "/World/Resolve_Ops/serving_bowl"))

        array_values = self._construct_new_array()
        array_values[array_const.COUNT] = 10
        array_values[array_const.INC_TRANSLATE] = Gf.Vec3d(125, 0, 0)

        self._run_create_array_command(source_prims, array_values)

        results = self._get_results(self._results_stage, self._source_stage, "/World/Resolve_Ops")
        self.assertTrue(results[0], results[1])

    # ============= UTILITY ===============

    def _construct_new_array(self):
        return ArrayParams().get_defaults()

    def _run_create_array_command(self, target_prims: list, array_values: dict):
        cmd = CreateArrayCommand(target_prims=target_prims, array_values=array_values)
        results = cmd.do()
        return results

    def _open_stage(self, stage_name: str):
        path = DATA_DIR.joinpath(stage_name + ".usda")
        stage = Usd.Stage.Open(str(path), Usd.Stage.LoadNone)
        return stage

    def _set_active_stage(self, stage_name: str):
        path = DATA_DIR.joinpath(stage_name + ".usda")
        usd_context = omni.usd.get_context()
        usd_context.open_stage(str(path))

    def _get_prim_from_stage(self, stage_to_get_prim_from: Usd.Stage, prim_path: str):
        return stage_to_get_prim_from.GetPrimAtPath(prim_path)

    def _get_results(self, results_stage: Usd.Stage, source_stage: Usd.Stage, parent_path: str):
        results_parent = self._get_prim_from_stage(results_stage, parent_path)
        source_parent = self._get_prim_from_stage(source_stage, parent_path)
        return self._compare_results(source_parent, results_parent)

    def _compare_results(
        self,
        source_parent: Usd.Prim,
        result_parent: Usd.Prim,
        check_selection: bool = False,
        created_selected_prim_paths: list = None,
    ) -> tuple:
        """
        Returns a tuple of (Results match (bool), Mismatch message (str))
        """
        source_children = source_parent.GetAllChildren()
        result_children = result_parent.GetAllChildren()

        if len(source_children) == len(result_children):
            for i in range(len(source_children)):
                source_prim = source_children[i]
                result_prim = result_children[i]

                display_predicate = Usd.TraverseInstanceProxies(Usd.PrimAllPrimsPredicate)
                source_prim_range = list(Usd.PrimRange(source_prim, display_predicate))
                result_prim_range = list(Usd.PrimRange(result_prim, display_predicate))

                for index in range(len(source_prim_range)):
                    sub_source_prim = source_prim_range[index]
                    sub_result_prim = result_prim_range[index]

                    if sub_source_prim.GetPath() != sub_result_prim.GetPath():
                        return False, f"Mismatched paths: {sub_source_prim}, {sub_result_prim}"

                    src_s, src_r, src_r_order, src_t = omni.usd.get_local_transform_SRT(sub_source_prim)
                    result_s, result_r, result_r_order, result_t = omni.usd.get_local_transform_SRT(sub_result_prim)

                    match = (
                        Gf.IsClose(src_s, result_s, self._small_number)
                        and Gf.IsClose(src_r, result_r, self._small_number)
                        and Gf.IsClose(src_t, result_t, self._small_number)
                        and src_r_order == result_r_order
                    )
                    if not match:
                        return False, f"Mismatched transforms: {sub_source_prim}, {sub_result_prim}"

            if check_selection:
                if created_selected_prim_paths is not None:
                    selected_prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
                    if created_selected_prim_paths != selected_prim_paths:
                        return False, "Selection mismatch"
                else:
                    return False, "Please provide the list of selected created prim paths when checking selection."
            return True, "Exact match"
        else:
            return False, "Mismatched results"
