__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


from omni.scene.optimizer.core import ExecutionContext
from omni.scene.optimizer.core.scripts import standalone
from pxr import Usd, UsdGeom, UsdShade, UsdUtils

from .test_utils import Test_Operation

FUNC_DEINSTANCE = 0
FUNC_UNBIND_MATERIALS = 2
FUNC_INSTANCE = 3
FUNC_INVALID = 99

# Default arguments for the command
DEFAULT_ARGS = {
    "paths": [],
    "function": FUNC_DEINSTANCE,
}


def _count_instanced(stage):
    """Count instanced prims in a stage"""
    count = 0
    for prim in stage.Traverse():
        if prim.IsInstance():
            count += 1

    return count


def _is_bound_material(stage, prim_path, material_path):
    """Returns true if the prim exists and is bound to a material with the given path"""
    prim = stage.GetPrimAtPath(prim_path)

    if prim:
        materialBindingAPI = UsdShade.MaterialBindingAPI(prim)
        material, _ = materialBindingAPI.ComputeBoundMaterial()

        if material and material.GetPath() == material_path:
            return True

    return False


class Test_Operation_Utility_Function(Test_Operation):

    OPERATION = "utilityFunction"

    async def test_basic_deinstance(self):
        """Test simple deinstancing"""

        stage = self._open_stage("instancedCubes.usda")

        count_before = _count_instanced(stage)
        self.assertEqual(count_before, 3)

        # Build JSON args and execute command
        json = """[
            {"operation": "utilityFunction",
            "paths": [],
            "function": 0}]"""
        status = standalone.execute_commands_from_json(stage, json)
        self.assertTrue(status)

        count_after = _count_instanced(stage)
        self.assertEqual(count_after, 0)

    async def test_basic_unbind_materials(self):
        """Test unbinding materials"""

        stage = self._open_stage("utilityMaterials.usda")

        self.assertTrue(_is_bound_material(stage, "/Cubes/Cube1", "/Looks/MaterialRed"))
        self.assertTrue(_is_bound_material(stage, "/Cubes/Cube2", "/Looks/MaterialRed"))
        self.assertTrue(_is_bound_material(stage, "/Cubes/Cube3", "/Looks/MaterialBlue"))

        self.assertTrue(_is_bound_material(stage, "/CollectionCubes/Cubes/Cube1", "/Looks/MaterialOrange"))
        self.assertTrue(_is_bound_material(stage, "/CollectionCubes/Cubes/Cube2", "/Looks/MaterialOrange"))

        args = DEFAULT_ARGS.copy()
        args["function"] = FUNC_UNBIND_MATERIALS
        self._execute_command(args)

        self.assertFalse(_is_bound_material(stage, "/Cubes/Cube1", "/Looks/MaterialRed"))
        self.assertFalse(_is_bound_material(stage, "/Cubes/Cube2", "/Looks/MaterialRed"))
        self.assertFalse(_is_bound_material(stage, "/Cubes/Cube3", "/Looks/MaterialBlue"))

        self.assertFalse(_is_bound_material(stage, "/CollectionCubes/Cubes/Cube1", "/Looks/MaterialOrange"))
        self.assertFalse(_is_bound_material(stage, "/CollectionCubes/Cubes/Cube2", "/Looks/MaterialOrange"))

    async def test_basic_set_instanceable(self):
        """Test the "set instanceable" utility function"""

        stage = self._open_stage("utilityInstance.usda")

        # Initial state: nothing is set to instanceable
        self.assertFalse(stage.GetPrimAtPath("/World/Thing1").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/Thing2").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/Thing3").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/Thing4").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/ThingEmpty1").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/ThingPayload1").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/ThingPayload2").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/ThingMaterialInside1").IsInstanceable())
        self.assertFalse(stage.GetPrimAtPath("/World/ThingMaterialOutside1").IsInstanceable())

        # Except one thing
        self.assertTrue(stage.GetPrimAtPath("/World/ThingInstanceable").IsInstanceable())

        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()
        context.verbose = 1

        args = DEFAULT_ARGS.copy()
        args["function"] = FUNC_INSTANCE
        self._execute_command(args, context=context)

        # Thing1/3/4 should now be set to instanceable
        self.assertTrue(stage.GetPrimAtPath("/World/Thing1").IsInstanceable())
        self.assertTrue(stage.GetPrimAtPath("/World/Thing3").IsInstanceable())
        self.assertTrue(stage.GetPrimAtPath("/World/Thing4").IsInstanceable())

        # Thing2 should not, as it has an extra opinion on a child that prevents it being an instance
        self.assertFalse(stage.GetPrimAtPath("/World/Thing2").IsInstanceable())

        # ThingEmpty should also not - it is empty, no point making it an instance
        self.assertFalse(stage.GetPrimAtPath("/World/ThingEmpty1").IsInstanceable())

        # ThingPayload1 should now be instanceable
        self.assertTrue(stage.GetPrimAtPath("/World/ThingPayload1").IsInstanceable())

        # ThingPayload2 also has a child opinion and should not be
        self.assertFalse(stage.GetPrimAtPath("/World/ThingPayload2").IsInstanceable())

        # MaterialInside should be instanceable, its material is local
        self.assertTrue(stage.GetPrimAtPath("/World/ThingMaterialInside1").IsInstanceable())

        # MaterialOutside references materials in, but they get localized.
        self.assertTrue(stage.GetPrimAtPath("/World/ThingMaterialOutside1").IsInstanceable())

        # Should still be instanceable
        self.assertTrue(stage.GetPrimAtPath("/World/ThingInstanceable").IsInstanceable())

    async def test_invalid_utility_function(self):
        """Test invalid utility function"""

        stage = self._open_stage("utilityInstance.usda")

        args = DEFAULT_ARGS.copy()
        args["function"] = FUNC_INVALID
        self._execute_command(args)

        # Got here, didn't crash
        self.assertTrue(True)
