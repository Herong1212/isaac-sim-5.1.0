__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

from omni.scene.optimizer.core import ExecutionContext
from pxr import UsdGeom, UsdShade, UsdUtils

from .test_utils import Test_Operation

DEFAULT_ARGS = {"materialPrimPaths": [], "optimizeMaterialsMode": 0}


def _is_bound_material(stage, prim_path, material_path):
    """Returns true if the prim exists and is bound to a material with the given path"""
    prim = stage.GetPrimAtPath(prim_path)

    if prim:
        materialBindingAPI = UsdShade.MaterialBindingAPI(prim)
        material, _ = materialBindingAPI.ComputeBoundMaterial()

        if material and material.GetPath() == material_path:
            return True

    return False


def _count_materials(stage):
    """Count the number of Materials in a stage"""

    numMaterials = 0
    for prim in stage.Traverse():
        if prim.IsA(UsdShade.Material):
            numMaterials += 1

    return numMaterials


def _count_material_displayColor_displayOpacity(stage):
    """Count the number of Materials and displayColor, displayOpacity primvars in the stage"""
    # Result counters
    numMaterials = 0
    numDisplayColor = 0
    numDisplayOpacity = 0

    # Iterate all the prims in the stage
    for prim in stage.Traverse():

        # Count materials
        if prim.IsA(UsdShade.Material):
            numMaterials += 1

        if prim.GetTypeName() == "Cube" or prim.GetTypeName() == "Mesh":
            primvarsAPI = UsdGeom.PrimvarsAPI(prim)

            # Count displayColor
            displayColor = primvarsAPI.GetPrimvar("displayColor").Get()
            if displayColor:
                numDisplayColor += 1

            # Count displayOpacity
            displayOpacity = primvarsAPI.GetPrimvar("displayOpacity").Get()
            if displayOpacity:
                numDisplayOpacity += 1

    return (numMaterials, numDisplayColor, numDisplayOpacity)


class Test_Operation_Optimize_Materials(Test_Operation):

    OPERATION = "optimizeMaterials"

    async def test_materials_bound_within_scope(self):
        """Instanced meshes should not be bound to materials outside the scope of the reference"""
        # Test case is duplicate materials within two components, one is instanceable and the other is not.
        stage = self._open_stage("materialBind.usd")
        self._execute_json(stage, "materialBind.json")

        # Instance proxies should NOT be bound to the world materials
        self.assertFalse(_is_bound_material(stage, "/World/Instance/Geometry/Mesh_1", "/World/Looks/Red"))
        self.assertFalse(_is_bound_material(stage, "/World/Instance/Geometry/Mesh_2", "/World/Looks/Red"))
        self.assertFalse(_is_bound_material(stage, "/World/Instance/Geometry/Mesh_3", "/World/Looks/Green"))
        self.assertFalse(_is_bound_material(stage, "/World/PayloadInstance/Geometry/Mesh_1", "/World/Looks/Red"))
        self.assertFalse(_is_bound_material(stage, "/World/PayloadInstance/Geometry/Mesh_2", "/World/Looks/Red"))
        self.assertFalse(_is_bound_material(stage, "/World/PayloadInstance/Geometry/Mesh_3", "/World/Looks/Green"))

        # Instance proxies will be bound to materials within the scope of the instance
        self.assertTrue(_is_bound_material(stage, "/World/Instance/Geometry/Mesh_1", "/World/Instance/Looks/Red"))
        self.assertTrue(_is_bound_material(stage, "/World/Instance/Geometry/Mesh_2", "/World/Instance/Looks/Red"))
        self.assertTrue(_is_bound_material(stage, "/World/Instance/Geometry/Mesh_3", "/World/Instance/Looks/Green"))
        self.assertTrue(
            _is_bound_material(stage, "/World/PayloadInstance/Geometry/Mesh_1", "/World/PayloadInstance/Looks/Red")
        )
        self.assertTrue(
            _is_bound_material(stage, "/World/PayloadInstance/Geometry/Mesh_2", "/World/PayloadInstance/Looks/Red")
        )
        self.assertTrue(
            _is_bound_material(stage, "/World/PayloadInstance/Geometry/Mesh_3", "/World/PayloadInstance/Looks/Green")
        )

        # Referenced prims (that are not instanceable) will be bound to the world materials
        self.assertTrue(_is_bound_material(stage, "/World/Component/Geometry/Mesh_1", "/World/Looks/Red"))
        self.assertTrue(_is_bound_material(stage, "/World/Component/Geometry/Mesh_2", "/World/Looks/Red"))
        self.assertTrue(_is_bound_material(stage, "/World/Component/Geometry/Mesh_3", "/World/Looks/Green"))

        # Payload prims (that are not instanceable) will be bound to the world materials
        self.assertTrue(_is_bound_material(stage, "/World/PayloadComponent/Geometry/Mesh_1", "/World/Looks/Red"))
        self.assertTrue(_is_bound_material(stage, "/World/PayloadComponent/Geometry/Mesh_2", "/World/Looks/Red"))
        self.assertTrue(_is_bound_material(stage, "/World/PayloadComponent/Geometry/Mesh_3", "/World/Looks/Green"))

        # The instanced prims will be bound to materials within the scope of the instance
        # So that when instanced they generate instance proxies with materials in scope
        self.assertTrue(
            _is_bound_material(stage, "/World/Meshes/Asset/Geometry/Mesh_1", "/World/Meshes/Asset/Looks/Red")
        )
        self.assertTrue(
            _is_bound_material(stage, "/World/Meshes/Asset/Geometry/Mesh_2", "/World/Meshes/Asset/Looks/Red")
        )
        self.assertTrue(
            _is_bound_material(stage, "/World/Meshes/Asset/Geometry/Mesh_3", "/World/Meshes/Asset/Looks/Green")
        )

    async def test_DeduplicateMaterials(self):
        """Test the Deduplicate Materials command"""
        stage = self._open_stage("deduplicateMaterials.usda")

        # Initially 7 unique materials
        uniqueMaterials = 0
        for prim in stage.TraverseAll():
            if prim.IsA(UsdShade.Material):
                uniqueMaterials += 1

        self.assertEqual(uniqueMaterials, 7)

        # Run the operation
        self._execute_json(stage, "deduplicateMaterials.json")

        # After de-duplication should only be 4
        uniqueMaterials = 0
        for prim in stage.TraverseAll():
            if prim.IsA(UsdShade.Material):
                uniqueMaterials += 1

        self.assertEqual(uniqueMaterials, 4)

    async def test_OptimizeMaterials(self):
        """Test various material optimizations"""
        stage = self._open_stage("optimizeMaterials.usda")

        # Original scene has 6 materials, and no display color/opacity
        num_materials, num_display_color, num_display_opacity = _count_material_displayColor_displayOpacity(stage)
        self.assertEqual(num_materials, 6)
        self.assertEqual(num_display_color, 0)
        self.assertEqual(num_display_opacity, 0)

        # One material has inputs:opacity
        transparentPrim = stage.GetPrimAtPath("/PlaneTransparent/Plane")
        opacityPrimvar = UsdGeom.PrimvarsAPI(transparentPrim).GetPrimvar("displayOpacity")
        self.assertIsNone(opacityPrimvar.Get())

        # Optimize
        self._execute_json(stage, "optimizeMaterials.json")

        # After optimize all materials should be gone, and replaced with colors/opacity.
        num_materials, num_display_color, num_display_opacity = _count_material_displayColor_displayOpacity(stage)
        self.assertEqual(num_materials, 0)
        self.assertEqual(num_display_color, 6)
        self.assertEqual(num_display_opacity, 1)

        # Explicitly check opacity was converted to a primvar with the correct value
        transparentPrim = stage.GetPrimAtPath("/PlaneTransparent/Plane")
        opacityPrimvar = UsdGeom.PrimvarsAPI(transparentPrim).GetPrimvar("displayOpacity")
        opacity = list(opacityPrimvar.Get())
        self.assertEqual(len(opacity), 1)
        self.assertAlmostEqual(opacity[0], 0.6)

    async def test_OptimizeMaterialsInheritedColors(self):
        """Test that when converting to color, child opinions on color are blocked"""

        stage = self._open_stage("optimizeMaterialsInheritedMaterial.usda")

        # The top level xform should not initially have a primvar value
        primvarsAPI = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath("/Cube"))
        displayColorPrimvar = primvarsAPI.GetPrimvar("displayColor")
        self.assertFalse(displayColorPrimvar.HasAuthoredValue())

        # The initial child mesh should have a primvar value
        primvarsAPI = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath("/Cube/CubeShape"))
        displayColorPrimvar = primvarsAPI.GetPrimvar("displayColor")
        self.assertTrue(displayColorPrimvar.HasAuthoredValue())
        color = displayColorPrimvar.Get()
        self.assertEqual(list(color), [(0, 0, 1)])

        # Convert materials
        self._execute_json(stage, "optimizeMaterialsInheritedMaterial.json")

        # After convert the top level xform should have a primvar
        primvarsAPI = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath("/Cube"))
        xformPrimvar = primvarsAPI.GetPrimvar("displayColor")
        self.assertTrue(xformPrimvar.HasAuthoredValue())
        xformColor = xformPrimvar.Get()
        self.assertEqual(list(xformColor), [(1, 1, 0)])

        # The primvar on the prim should have been blocked
        primvarsAPI = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath("/Cube/CubeShape"))
        displayColorPrimvar = primvarsAPI.GetPrimvar("displayColor")
        self.assertFalse(displayColorPrimvar.HasAuthoredValue())

        # Find the inherited primvar from the prim
        inheritedPrimvar = primvarsAPI.FindPrimvarWithInheritance("displayColor")
        color = inheritedPrimvar.Get()

        # Assert the expected value
        self.assertEqual(list(color), [(1, 1, 0)])

        # Assert it matches the xform value it inherited from
        self.assertEqual(color, xformColor)

        # Also assert the primvar came from where we expected it to
        self.assertEqual(inheritedPrimvar.GetAttr().GetPrim(), xformPrimvar.GetAttr().GetPrim())

    async def test_OptimizeMaterialsRemoveUnbound(self):
        """Test the "Remove Unbound" operation mode"""

        stage = self._open_stage("optimizeMaterialsUnbound.usda")

        materialsCount = _count_materials(stage)

        # Verify initial material count.
        # This is actually 2x the materials, due to the referenced copies - doesn't really matter
        # for the purpose of this test.
        self.assertEqual(materialsCount, 12)

        # Explicitly test that the unbound material exists
        self.assertTrue(stage.GetPrimAtPath("/World/Looks/MaterialUnused"))

        # Execute
        self._execute_json(stage, "optimizeMaterialsUnbound.json")

        # Count again. One unused material (plus the second referenced copy) should no longer
        # be present.
        materialsCount = _count_materials(stage)

        self.assertEqual(materialsCount, 10)

        # Explicitly test that the unbound material is now gone
        self.assertFalse(stage.GetPrimAtPath("/World/Looks/MaterialUnused"))

    async def test_OptimizeMaterialsReferenceOrder(self):
        """Test that removing duplicates when the source reference material is described after
        the reference in a stage"""

        # Test case is a stage with two prototypes with a copy of the same material and two
        # references to them. The distinction between other tests is that the prototypes (the
        # source materials) are described AFTER the references in the usda. This test ensures
        # that even though a standard traversal would encounter the references first, we still
        # bind to the least-referenced thing. Otherwise we end up deleting the thing that is
        # being referenced!
        stage = self._open_stage("referencedMaterials.usda")

        materialsCount = _count_materials(stage)
        self.assertEqual(materialsCount, 4)

        # Assert initial state
        self.assertTrue(_is_bound_material(stage, "/World/Cube1/Shape", "/World/Cube1/Material3"))
        self.assertTrue(_is_bound_material(stage, "/World/Cube2/Shape", "/World/Cube2/Material"))
        self.assertTrue(_is_bound_material(stage, "/Prototypes/CubeYellow1/Shape", "/Prototypes/CubeYellow1/Material3"))
        self.assertTrue(_is_bound_material(stage, "/Prototypes/CubeYellow2/Shape", "/Prototypes/CubeYellow2/Material"))

        args = DEFAULT_ARGS.copy()
        self._execute_command(args)

        # After optimize only one unique material should remain, and everything should be bound
        # to the first prototype that is encountered.
        materialsCount = _count_materials(stage)
        self.assertEqual(materialsCount, 1)

        self.assertTrue(_is_bound_material(stage, "/World/Cube1/Shape", "/Prototypes/CubeYellow1/Material3"))
        self.assertTrue(_is_bound_material(stage, "/World/Cube2/Shape", "/Prototypes/CubeYellow1/Material3"))
        self.assertTrue(_is_bound_material(stage, "/Prototypes/CubeYellow1/Shape", "/Prototypes/CubeYellow1/Material3"))
        self.assertTrue(_is_bound_material(stage, "/Prototypes/CubeYellow2/Shape", "/Prototypes/CubeYellow1/Material3"))

    async def test_OptimizeMaterialsPayloads(self):
        """Test that deduplicating materials added via payload works"""

        # This test scene is a stage with four cubes and four copies of a material,
        # which is added via payload.
        stage = self._open_stage("optimizeMaterialsPayload.usda")

        materialsCount = _count_materials(stage)
        self.assertEqual(materialsCount, 4)

        # Custom execution context
        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()
        context.generateReport = 1
        context.verbose = 1

        args = DEFAULT_ARGS.copy()
        self._execute_command(args, context)

        # After optimizing only one material should exist
        materialsCount = _count_materials(stage)
        self.assertEqual(materialsCount, 1)

        self.assertTrue(_is_bound_material(stage, "/World/Cube1", "/World/Looks/Blue1"))
        self.assertTrue(_is_bound_material(stage, "/World/Cube2", "/World/Looks/Blue1"))
        self.assertTrue(_is_bound_material(stage, "/World/Cube3", "/World/Looks/Blue1"))
        self.assertTrue(_is_bound_material(stage, "/World/Cube4", "/World/Looks/Blue1"))

    async def test_OptimizeMaterialsHierarchy(self):
        """Test recursive path expressions when removing duplicate materials"""

        stage = self._open_stage("optimizeMaterialsHierarchy.usda")

        # Assert initial state
        self.assertEqual(_count_materials(stage), 7)

        # First test is deduplicating the entire stage
        args = DEFAULT_ARGS.copy()
        self._execute_command(args)
        self.assertEqual(_count_materials(stage), 3)

        # Re-open stage
        stage = self._open_stage("optimizeMaterialsHierarchy.usda")
        self.assertEqual(_count_materials(stage), 7)

        # Now filter for a subset of materials
        args["materialPrimPaths"] = ["/Materials/Red//"]
        self._execute_command(args)

        # Should be 5: two duplicate "red" materials should have been removed
        self.assertEqual(_count_materials(stage), 5)

        # Repeat with a different path
        args["materialPrimPaths"] = ["/Materials/Blue//"]
        self._execute_command(args)

        # Should be 4: 5 from the previous assert, and then one duplicate blue one removed
        self.assertEqual(_count_materials(stage), 4)

        # Do the final subset
        args["materialPrimPaths"] = ["/Materials/Green//"]
        self._execute_command(args)

        # Now there should be 3, which is all of the duplicates gone
        self.assertEqual(_count_materials(stage), 3)

        # Finally re-open and assert initial state
        stage = self._open_stage("optimizeMaterialsHierarchy.usda")
        self.assertEqual(_count_materials(stage), 7)

        # Test everything under /Materials, which should also give us 3
        args["materialPrimPaths"] = ["/Materials//"]
        self._execute_command(args)
        self.assertEqual(_count_materials(stage), 3)

    async def test_OptimizeMaterialsNodeGraphLoop(self):
        """Test that a NodeGraph that connects to itself does not cause an infinite loop"""

        stage = self._open_stage("optimizeMaterialsNodeGraph.usda")

        # Assert initial state
        self.assertEqual(_count_materials(stage), 2)

        # Deduplicate
        args = DEFAULT_ARGS.copy()
        self._execute_command(args)

        # We should not segfault and end up with a duplicate removed
        self.assertEqual(_count_materials(stage), 1)
