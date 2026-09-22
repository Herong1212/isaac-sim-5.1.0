# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pxr import Sdf
from pxr import Usd
from pxr import UsdGeom

import omni.kit.test
import omni.usd
import omni.kit.undo

from ..prim_serializer import get_prim_as_text, _to_layer, text_to_stage

sdf_prim_to_text = """#usda 1.0

def "Item_00"
{
    def Sphere "Sphere01"
    {
    }
}
"""

sdf_duplicate_name = """#usda 1.0

def "Item_00"
{
    def Sphere "Sphere01"
    {
    }
}

def "Item_01"
{
    def Sphere "Sphere01"
    {
    }
}
"""

sdf_preserve_relationships = """#usda 1.0

def "Item_00"
{
    def Sphere "Sphere01"
    {
        custom rel test = </Item_01/Sphere02>
    }
}

def "Item_01"
{
    def Sphere "Sphere02"
    {
    }
}
"""

# This usda has 2 incoming connections on the first node, and an internal
# connection between the 2 nodes on the 2nd node.
delete_external_connections = """#usda 1.0

def "Item_00"
{
    def OmniGraphNode "add_01" (
        apiSchemas = ["NodeGraphNodeAPI"]
    )
    {
        custom token inputs:a
        token inputs:a.connect = </World/ActionGraph/add.outputs:sum>
        custom token inputs:b
        token inputs:b.connect = </World/ActionGraph/read_time.outputs:frame>
        token node:type = "omni.graph.nodes.Add"
        int node:typeVersion = 1
        custom token outputs:sum
        uniform float2 ui:nodegraph:node:pos = (617.9488, -19.670042)
    }
}

def "Item_01"
{
    def OmniGraphNode "scale_to_size_01" (
        apiSchemas = ["NodeGraphNodeAPI"]
    )
    {
        custom double inputs:speed = 1
        double inputs:speed.connect = </Item_00/add_01.outputs:sum>
        token node:type = "omni.graph.nodes.ScaleToSize"
        uniform float2 ui:nodegraph:node:pos = (882.75476, 398.3356)
    }
}
"""


class TestStageCopyPaste(omni.kit.test.AsyncTestCase):
    async def test_prim_to_text(self):
        """Testing how only one prim can be converted to text"""

        stage = Usd.Stage.CreateInMemory()
        path = Sdf.Path("/Sphere01")
        UsdGeom.Sphere.Define(stage, path)
        UsdGeom.Sphere.Define(stage, "/Sphere02")

        # Extract only one prim
        result = get_prim_as_text(stage, [path])
        # Linux line endings
        result = "\n".join(result.splitlines())

        self.assertEqual(result, sdf_prim_to_text)

    async def test_text_to_stage(self):
        """Testing converting text to layer and import to stage"""
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        path = Sdf.Path("/Sphere01")
        UsdGeom.Sphere.Define(stage, path)
        UsdGeom.Xform.Define(stage, "/root_for_import")
        import_root_prim = stage.GetPrimAtPath("/root_for_import")

        # test that invalid text returns False
        self.assertFalse(text_to_stage(stage, "asdf", root=import_root_prim.GetPath()))
        self.assertFalse(import_root_prim.GetChildren())

        # test import to specific root
        text_to_stage(stage, sdf_prim_to_text, root=import_root_prim.GetPath())
        self.assertEqual(len(import_root_prim.GetChildren()), 1)
        child = import_root_prim.GetChildren()[0]
        self.assertEqual(child.GetName(), "Sphere01")
        omni.kit.undo.undo()

        # test import to default root
        text_to_stage(stage, sdf_prim_to_text)
        self.assertFalse(import_root_prim.GetChildren())
        imported = stage.GetPrimAtPath("/Item_00")
        self.assertIsNotNone(imported)
        omni.kit.undo.undo()

    async def test_duplicate_name(self):
        """Testing the ability to copy two prims with the same name and different paths"""

        stage = Usd.Stage.CreateInMemory()
        path1 = Sdf.Path("/Sphere01")
        UsdGeom.Sphere.Define(stage, path1)
        path2 = Sdf.Path("/Parent/Sphere01")
        UsdGeom.Sphere.Define(stage, path2)

        # Serialize prims
        result = get_prim_as_text(stage, [path1, path2])
        # Linux line endings
        result = "\n".join(result.splitlines())

        self.assertEqual(result, sdf_duplicate_name)

    async def test_preserve_relationships(self):
        """Testing relationship target updates when copying multiple prims"""

        stage = Usd.Stage.CreateInMemory()
        path1 = Sdf.Path("/Sphere01")
        sphere1 = UsdGeom.Sphere.Define(stage, path1)
        path2 = Sdf.Path("/Sphere02")
        UsdGeom.Sphere.Define(stage, path2)

        rel = sphere1.GetPrim().CreateRelationship("test")
        rel.SetTargets([path2])

        # Serialize prims
        result = get_prim_as_text(stage, [path1, path2])
        # Linux line endings
        result = "\n".join(result.splitlines())

        self.assertEqual(result, sdf_preserve_relationships)

    async def test_delete_external_connections(self):
        """Testing that external connections are removed, but internal connections remain"""

        layer = _to_layer(delete_external_connections, keep_inputs=False)
        root_prims = layer.rootPrims

        self.assertIsNotNone(root_prims)

        # Check to make sure the incoming connections are gone
        prim_spec = root_prims[0].nameChildren[0]
        num_connections = 0
        for attr in prim_spec.attributes:
            connections = attr.connectionPathList.explicitItems
            if connections:
                num_connections += len(connections)

        self.assertEqual(num_connections, 0)

        # Check to make sure the internal connection is there still
        prim_spec = root_prims[1].nameChildren[0]
        num_connections = 0
        for attr in prim_spec.attributes:
            connections = attr.connectionPathList.explicitItems
            if connections:
                num_connections += len(connections)

        self.assertEqual(num_connections, 1)
