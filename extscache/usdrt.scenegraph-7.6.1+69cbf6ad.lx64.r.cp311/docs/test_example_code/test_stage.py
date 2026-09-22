__copyright__ = "Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import os
import pathlib
import platform
import random
import sys
import tempfile
import time
import unittest

from . import TestRtScenegraph, get_data_path, tc_logger

DATA_DIR = get_data_path()


def get_tmp_usda_path(outdir):
    timestr = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    randstr = random.randint(0, 32767)

    return os.path.join(outdir, f"{timestr}_{randstr}.usda")


def setup_stage_and_hier(scene_path):
    from usdrt import Gf, Sdf, Usd, hierarchy, population

    stage = Usd.Stage.Open(DATA_DIR + scene_path)

    srw_id = stage.GetStageReaderWriterId()
    stage_id = stage.GetStageIdAsStageId()
    fabric_id = stage.GetFabricId()

    # Note, in Kit all of this population happens automatically if FSD is enabled
    pop = population.IUtils()
    pop.set_enable_usd_notice_handling(stage_id, fabric_id, True)
    pop.populate_from_usd(srw_id, stage_id, Sdf.Path("/"), 0)
    pop.apply_pending_usd_updates(stage_id, srw_id, 0)

    hier = hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
    hier.update_world_xforms()
    hier.track_world_xform_changes(True)

    return stage, hier


class TestUsdStage(TestRtScenegraph):
    @tc_logger
    def test_open(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")

        self.assertTrue(stage)

    @tc_logger
    def test_create_new(self):
        from usdrt import Sdf, Usd

        with tempfile.TemporaryDirectory() as tempdir:
            stage = Usd.Stage.CreateNew(get_tmp_usda_path(tempdir))

            self.assertTrue(stage)

    @tc_logger
    def test_attach(self):
        import pxr
        from usdrt import Sdf, Usd

        # SSWH ref = 1
        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        cache = pxr.UsdUtils.StageCache.Get()
        layer = pxr.Sdf.Layer.FindOrOpen(DATA_DIR + "/cornell.usda")
        usd_stage = cache.FindOneMatching(layer)
        stage_id = cache.GetId(usd_stage).ToLongInt()

        # SSWH ref = 2
        attached_stage = Usd.Stage.Attach(stage_id)
        self.assertTrue(attached_stage)

        # verify attached stage can access stage in progress
        prim = attached_stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))
        self.assertTrue(prim)

        # verify destruction of attached stage does not destroy stage in progress
        del attached_stage
        prim = stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))
        self.assertTrue(prim)

        cache.Clear()

    @tc_logger
    def test_attach_no_swh(self):
        import pxr
        from usdrt import Sdf, Usd

        # Note - no SSWH created here
        stage = pxr.Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        cache = pxr.UsdUtils.StageCache.Get()
        id = cache.Insert(stage)
        stage_id = id.ToLongInt()

        # This creates the SSWH
        self.assertFalse(Usd.Stage.SimStageWithHistoryExists(stage_id))
        attached_stage = Usd.Stage.Attach(stage_id)
        self.assertTrue(attached_stage)
        self.assertTrue(Usd.Stage.SimStageWithHistoryExists(stage_id))

        # verify attached stage can access stage in progress
        prim = attached_stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))
        self.assertTrue(prim)

        # verify that assumed ownership cleans up SSWH on destruction
        self.assertTrue(Usd.Stage.SimStageWithHistoryExists(stage_id))

        # deprecated API support for 104
        self.assertTrue(Usd.Stage.StageWithHistoryExists(stage_id))

        del attached_stage
        self.assertFalse(Usd.Stage.SimStageWithHistoryExists(stage_id))

        # deprecated API support for 104
        self.assertFalse(Usd.Stage.StageWithHistoryExists(stage_id))

        cache.Clear()

    @tc_logger
    def test_invalid_swh_id(self):
        import pxr
        from usdrt import Sdf, Usd

        # OM-85698 can pass invalid ID to StageWithHistoryExists
        self.assertFalse(Usd.Stage.SimStageWithHistoryExists(-1))
        self.assertFalse(Usd.Stage.StageWithHistoryExists(-1))

    @tc_logger
    def test_get_sip_id(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        id = stage.GetStageReaderWriterId()
        self.assertNotEqual(id.id, 0)

        # deprecated API support for 104
        id2 = stage.GetStageInProgressId()
        self.assertNotEqual(id2.id, 0)
        self.assertEqual(id.id, id2.id)

    @tc_logger
    def test_get_prim_at_path(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        prim = stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))

        self.assertTrue(prim)

    @tc_logger
    def test_get_prim_at_path_invalid(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        prim = stage.GetPrimAtPath(Sdf.Path("/Invalid"))

        self.assertFalse(prim)

    @tc_logger
    def test_get_prim_at_path_only_in_fabric(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        defined = stage.DefinePrim("/Test", "Cube")
        self.assertTrue(defined)

        got = stage.GetPrimAtPath("/Test")
        self.assertTrue(got)
        self.assertEqual(got.GetName(), "Test")

    @tc_logger
    def test_get_default_prim(self):
        from usdrt import Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        prim = stage.GetDefaultPrim()

        self.assertTrue(prim)
        self.assertTrue(prim.GetName() == "Cornell_Box")

    @tc_logger
    def test_get_pseudo_root(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        prim = stage.GetPseudoRoot()

        self.assertTrue(prim)
        self.assertTrue(prim.GetPath() == Sdf.Path("/"))

    @tc_logger
    def test_define_prim(self):
        from usdrt import Sdf, Usd

        with tempfile.TemporaryDirectory() as tempdir:
            stage = Usd.Stage.CreateNew(get_tmp_usda_path(tempdir))
            self.assertTrue(stage)

            prim = stage.DefinePrim(Sdf.Path("/Test"), "Mesh")
            self.assertTrue(prim)
            self.assertEqual(prim.GetName(), "Test")
            self.assertEqual(prim.GetTypeName(), "Mesh")

            prim_notype = stage.DefinePrim(Sdf.Path("/Test2"))
            self.assertTrue(prim_notype)
            self.assertEqual(prim_notype.GetName(), "Test2")
            self.assertEqual(prim_notype.GetTypeName(), "")

    @tc_logger
    def test_define_prim_with_complete_type(self):
        from usdrt import Sdf, Usd

        # OM-90066 - use either alias or complete type name to define prim
        with tempfile.TemporaryDirectory() as tempdir:
            stage = Usd.Stage.CreateNew(get_tmp_usda_path(tempdir))
            self.assertTrue(stage)

            prim = stage.DefinePrim(Sdf.Path("/Test"), "Mesh")
            self.assertTrue(prim)
            self.assertEqual(prim.GetName(), "Test")
            self.assertEqual(prim.GetTypeName(), "Mesh")

            prim = stage.DefinePrim(Sdf.Path("/Test2"), "UsdGeomMesh")
            self.assertTrue(prim)
            self.assertEqual(prim.GetTypeName(), "Mesh")

            result = stage.GetPrimsWithTypeName("Xformable")
            self.assertEqual(len(result), 2)
            self.assertTrue(Sdf.Path("/Test") in result)
            self.assertTrue(Sdf.Path("/Test2") in result)

    @tc_logger
    def test_get_attribute_at_path(self):
        from usdrt import Sdf, Usd, UsdGeom

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        attr = stage.GetAttributeAtPath(Sdf.Path("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back.points"))
        self.assertTrue(attr)
        self.assertTrue(attr.HasValue())
        self.assertTrue(attr.GetName() == UsdGeom.Tokens.points)

    @tc_logger
    def test_get_attribute_at_path_fabric_only(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        prim = stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))
        self.assertFalse(prim.HasAttribute("myAttr"))

        attr = prim.CreateAttribute("myAttr", Sdf.ValueTypeNames.Int, True)
        self.assertTrue(attr)
        self.assertTrue(prim.HasAttribute("myAttr"))

        attr = stage.GetAttributeAtPath(Sdf.Path("/Cornell_Box.myAttr"))
        self.assertTrue(attr)
        self.assertTrue(attr.GetName() == "myAttr")

    @tc_logger
    def test_get_attribute_at_path_invalid(self):
        from usdrt import Sdf, Usd, UsdGeom

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        attr = stage.GetAttributeAtPath(Sdf.Path("/Invalid.points"))
        self.assertFalse(attr)

        attr = stage.GetAttributeAtPath(Sdf.Path("/Cornell_Box.invalid"))
        self.assertFalse(attr)

    @tc_logger
    def test_get_relationship_at_path(self):
        from usdrt import Sdf, Usd, UsdShade

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        rel = stage.GetRelationshipAtPath(
            Sdf.Path("/Cornell_Box/Root/Cornell_Box1_LP/Green_Wall/Green1SG.material:binding")
        )
        self.assertTrue(rel)
        self.assertTrue(rel.HasAuthoredTargets())
        self.assertEqual(rel.GetName(), UsdShade.Tokens.materialBinding)

    @tc_logger
    def test_get_relationship_at_path_invalid(self):
        from usdrt import Sdf, Usd, UsdShade

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        rel = stage.GetRelationshipAtPath(Sdf.Path("/Invalid.material:binding"))
        self.assertFalse(rel)

        rel = stage.GetRelationshipAtPath(Sdf.Path("/Cornell_Box.invalid"))
        self.assertFalse(rel)

    @tc_logger
    def test_traverse(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        prim = stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))
        self.assertTrue(prim)
        prim_range = stage.Traverse()
        self.assertTrue(prim_range)

        count = 0
        for this_prim in prim_range:
            count += 1
            prim = this_prim

        self.assertTrue(count == 40)
        self.assertEqual(prim.GetPath(), Sdf.Path("/RectLight"))

    @tc_logger
    def test_write_layer(self):
        """
        Note that in this implementation, WriteToLayer has the same limitations
        as Fabric's exportUsd. New prims are not typed, empty prims may be
        defined as overs, etc...
        """
        import pxr
        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        stage = Usd.Stage.CreateInMemory("test.usda")
        self.assertTrue(stage)

        world = stage.DefinePrim(Sdf.Path("/World"), "Xform")
        triangle = stage.DefinePrim(Sdf.Path("/World/Triangle"), "Mesh")
        points = triangle.CreateAttribute(UsdGeom.Tokens.points, Sdf.ValueTypeNames.Point3fArray, False)
        faceVertexCounts = triangle.CreateAttribute(UsdGeom.Tokens.faceVertexCounts, Sdf.ValueTypeNames.IntArray, False)
        faceVertexIndices = triangle.CreateAttribute(
            UsdGeom.Tokens.faceVertexIndices, Sdf.ValueTypeNames.IntArray, False
        )

        points.Set(Vt.Vec3fArray([Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0), Gf.Vec3f(-1, 0, 0)]))
        faceVertexCounts.Set(Vt.IntArray([3]))
        faceVertexIndices.Set(Vt.IntArray([0, 1, 2]))

        with tempfile.TemporaryDirectory() as tempdir:
            test_file = get_tmp_usda_path(tempdir)
            stage.WriteToLayer(test_file)

            # Verfiy that data was stored to the new layer
            test_stage = pxr.Usd.Stage.Open(test_file)
            attr = test_stage.GetAttributeAtPath(pxr.Sdf.Path("/World/Triangle.points"))
            self.assertTrue(attr)
            self.assertTrue(attr.HasValue())
            self.assertEqual(len(attr.Get()), 3)

            prim = test_stage.GetPrimAtPath(pxr.Sdf.Path("/World/Triangle"))
            self.assertEqual(prim.GetTypeName(), "Mesh")

    @tc_logger
    def test_write_stage(self):
        """
        Note that in this implementation, WriteToStage has the same limitations
        as Fabric's cacheToUsd. Most importantly, new prims defined in
        Fabric are not written out to the USD Stage
        """
        import pxr
        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        cache = pxr.UsdUtils.StageCache.Get()
        layer = pxr.Sdf.Layer.FindOrOpen(DATA_DIR + "/cornell.usda")
        usd_stage = cache.FindOneMatching(layer)
        stage_id = cache.GetId(usd_stage).ToLongInt()

        prim = stage.GetPrimAtPath(Sdf.Path("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back"))
        self.assertTrue(prim)

        # Change doubleSided to False in Fabric
        attr = prim.GetAttribute(UsdGeom.Tokens.doubleSided)
        self.assertTrue(attr)
        result = attr.Set(False)
        self.assertTrue(result)

        attr = prim.GetAttribute(UsdGeom.Tokens.normals)
        self.assertTrue(attr)
        result = attr.Get()
        self.assertEqual(len(result), 4)
        for i in range(4):
            self.assertEqual(result[i], Gf.Vec3f(0, 0, -1))

        # Change normals to (1, 0, 0) in Fabric
        self.assertTrue(result.IsFabricData())
        for i in range(4):
            result[i] = Gf.Vec3f(1, 0, 0)

        stage.WriteToStage()

        usd_prim = usd_stage.GetPrimAtPath(pxr.Sdf.Path("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back"))
        # Verify doubleSided is now false on USD stage
        usd_attr = usd_prim.GetAttribute(UsdGeom.Tokens.doubleSided)
        self.assertFalse(usd_attr.Get())

        # Verify normals are now (1, 0, 0) on USD stage
        usd_attr = usd_prim.GetAttribute(UsdGeom.Tokens.normals)
        new_normals = usd_attr.Get()
        self.assertEqual(len(new_normals), 4)

        for i in range(4):
            self.assertEqual(new_normals[i], pxr.Gf.Vec3f(1, 0, 0))

        # Clear stage cache, since we modified the USD stage
        cache.Clear()

    @tc_logger
    def test_set_attribute_value(self):
        from usdrt import Gf, Sdf, Usd, Vt

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        newNormals = Vt.Vec3fArray([Gf.Vec3f(1, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(1, 0, 0)])

        attrPath = Sdf.Path("/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back.normals")
        result = stage.SetAttributeValue(attrPath, newNormals)
        self.assertTrue(result)

        attr = stage.GetAttributeAtPath(attrPath)
        self.assertTrue(attr)
        value = attr.Get()
        for i in range(4):
            self.assertEqual(value[i], Gf.Vec3f(1, 0, 0))

    @tc_logger
    def test_set_attribute_value_invalid_prim(self):
        from usdrt import Gf, Sdf, Usd, Vt

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        newNormals = Vt.Vec3fArray([Gf.Vec3f(1, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(1, 0, 0)])

        attrPath = Sdf.Path("/Invalid.normals")
        result = stage.SetAttributeValue(attrPath, newNormals)
        self.assertFalse(result)

    @tc_logger
    def test_has_prim_at_path(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # No prims populated into Fabric yet
        self.assertFalse(stage.HasPrimAtPath(Sdf.Path("/Cornell_Box")))

        prim = stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))

        # Prim is now in Fabric
        self.assertTrue(stage.HasPrimAtPath(Sdf.Path("/Cornell_Box")))

        # OM-87225
        # prim not in fabric
        self.assertFalse(stage.HasPrimAtPath(Sdf.Path("/Cube_5")))
        # do a stage query, this will tag everything with metadata
        paths = stage.GetPrimsWithTypeName("Mesh")
        # prim not in fabric when we ignore tags by default
        self.assertFalse(stage.HasPrimAtPath(Sdf.Path("/Cube_5")))
        # prim in fabric if we include tags in the query
        self.assertTrue(stage.HasPrimAtPath(Sdf.Path("/Cube_5"), excludeTags=False))

    @tc_logger
    def test_remove_prim(self):
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # No prims populated into Fabric yet
        self.assertFalse(stage.HasPrimAtPath(Sdf.Path("/Cornell_Box")))

        prim = stage.GetPrimAtPath(Sdf.Path("/Cornell_Box"))

        # Prim is now in Fabric
        self.assertTrue(stage.HasPrimAtPath(Sdf.Path("/Cornell_Box")))

        self.assertTrue(stage.RemovePrim(Sdf.Path("/Cornell_Box")))

        # Prim removed from Fabric by RemovePrim
        self.assertFalse(stage.HasPrimAtPath(Sdf.Path("/Cornell_Box")))

        # Remove non-existant prim does not cause crash, but returns False
        self.assertFalse(stage.RemovePrim(Sdf.Path("/Cornell_Box")))

    @tc_logger
    def test_remove_prim_from_usd(self):
        import pxr
        from usdrt import Sdf, Usd, UsdGeom

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        cache = pxr.UsdUtils.StageCache.Get()
        layer = pxr.Sdf.Layer.FindOrOpen(DATA_DIR + "/cornell.usda")
        usd_stage = cache.FindOneMatching(layer)
        stage_id = cache.GetId(usd_stage).ToLongInt()

        path = "/DistantLight/BillboardComponent_0"

        # Populate into Fabric
        prim = stage.GetPrimAtPath(Sdf.Path(path))

        # Remove from USD stage
        usd_stage.RemovePrim(path)

        # The prim is still in Fabric
        self.assertTrue(stage.HasPrimAtPath(Sdf.Path(path)))

        expected_attrs = [UsdGeom.Tokens.visibility, UsdGeom.Tokens.xformOpOrder, "xformOp:transform"]

        for attr in prim.GetAttributes():
            self.assertTrue(attr.GetName() in expected_attrs)

        # Removing prim from Fabric is okay
        self.assertTrue(stage.RemovePrim(Sdf.Path(path)))
        self.assertFalse(stage.HasPrimAtPath(Sdf.Path(path)))

        cache.Clear()

    @tc_logger
    def test_repr_representation(self):
        import pxr
        from usdrt import Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        cache = pxr.UsdUtils.StageCache.Get()
        layer = pxr.Sdf.Layer.FindOrOpen(DATA_DIR + "/cornell.usda")
        usd_stage = cache.FindOneMatching(layer)
        stage_id = cache.GetId(usd_stage).ToLongInt()

        expected = "Stage(<ID: " + str(stage_id) + ">)"

        self.assertEqual(repr(stage), expected)

    @tc_logger
    def test_layer_rewrite(self):
        # OM-70883
        import pxr
        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        stage = Usd.Stage.CreateInMemory("test.usda")
        self.assertTrue(stage)

        world = stage.DefinePrim(Sdf.Path("/World"), "Xform")
        triangle = stage.DefinePrim(Sdf.Path("/World/Triangle"), "Mesh")
        points = triangle.CreateAttribute(UsdGeom.Tokens.points, Sdf.ValueTypeNames.Point3fArray, False)
        faceVertexCounts = triangle.CreateAttribute(UsdGeom.Tokens.faceVertexCounts, Sdf.ValueTypeNames.IntArray, False)
        faceVertexIndices = triangle.CreateAttribute(
            UsdGeom.Tokens.faceVertexIndices, Sdf.ValueTypeNames.IntArray, False
        )

        points.Set(Vt.Vec3fArray([Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0), Gf.Vec3f(-1, 0, 0)]))
        faceVertexCounts.Set(Vt.IntArray([3]))
        faceVertexIndices.Set(Vt.IntArray([0, 1, 2]))

        with tempfile.TemporaryDirectory() as tempdir:
            test_file = get_tmp_usda_path(tempdir)
            stage.WriteToLayer(test_file)

            # In OM-70883, multiple WriteToLayer on the same file causes a crash
            stage.WriteToLayer(test_file)

            # Verfiy that data was stored to the new layer
            test_stage = pxr.Usd.Stage.Open(test_file)
            attr = test_stage.GetAttributeAtPath(pxr.Sdf.Path("/World/Triangle.points"))
            self.assertTrue(attr)
            self.assertTrue(attr.HasValue())
            self.assertEqual(len(attr.Get()), 3)

            prim = test_stage.GetPrimAtPath(pxr.Sdf.Path("/World/Triangle"))
            self.assertEqual(prim.GetTypeName(), "Mesh")

    @tc_logger
    def test_get_prims_with_type_name(self):
        from usdrt import Gf, Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        paths = stage.GetPrimsWithTypeName("Mesh")
        self.assertEqual(len(paths), 8)

        paths = stage.GetPrimsWithTypeName("Shader")
        self.assertEqual(len(paths), 5)

        paths = stage.GetPrimsWithTypeName("Invalid")
        self.assertEqual(len(paths), 0)

        paths = stage.GetPrimsWithTypeName("UsdGeomBoundable")
        aliasPaths = stage.GetPrimsWithTypeName("Boundable")
        self.assertEqual(len(paths), len(aliasPaths))

    @tc_logger
    def test_get_prims_with_applied_api_name(self):
        # Begin example query by API
        from usdrt import Gf, Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        paths = stage.GetPrimsWithAppliedAPIName("ShapingAPI")
        self.assertEqual(len(paths), 2)

        paths = stage.GetPrimsWithAppliedAPIName("CollectionAPI:lightLink")
        self.assertEqual(len(paths), 5)
        # End example query by API

        paths = stage.GetPrimsWithAppliedAPIName("Invalid:test")
        self.assertEqual(len(paths), 0)

    @tc_logger
    def test_get_prims_with_type_and_applied_api_name(self):
        # Begin example query mixed
        from usdrt import Gf, Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        paths = stage.GetPrimsWithTypeAndAppliedAPIName("Mesh", ["CollectionAPI:test"])
        self.assertEqual(len(paths), 1)
        # End example query mixed

        paths = stage.GetPrimsWithTypeAndAppliedAPIName("Invalid", ["Invalid:test"])
        self.assertEqual(len(paths), 0)

    @tc_logger
    def test_get_stage_extent(self):
        # Begin example stage extent
        from usdrt import Gf, Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        bound = stage.GetStageExtent()
        self.assertTrue(Gf.IsClose(bound.GetMin(), Gf.Vec3d(-333.8142, -249.9100, -5.444), 0.01))
        self.assertTrue(Gf.IsClose(bound.GetMax(), Gf.Vec3d(247.1132, 249.9178, 500.0), 0.01))
        # End example stage extent

    @tc_logger
    def test_get_prims_with_type_and_scenegraph_instancing(self):
        from usdrt import Gf, Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/xform_component_hierarchy_instances.usda")
        self.assertTrue(stage)

        # There are 2 prototype proxy meshes on the stage
        paths = stage.GetPrimsWithTypeName("Mesh")
        self.assertEqual(len(paths), 2)

        paths = stage.GetPrimsWithTypeName("Invalid")
        self.assertEqual(len(paths), 0)

    @tc_logger
    def test_get_prims_with_type_and_unknown_schema(self):
        from usdrt import Gf, Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/TestConversionOnLoad.usda")
        self.assertTrue(stage)

        # This is an old OG schema that no longer exists
        paths = stage.GetPrimsWithTypeName("ComputeGraphSettings")
        self.assertEqual(len(paths), 1)

    @tc_logger
    def test_get_children_with_connectivity(self):
        from usdrt import Gf, Sdf, Usd

        stage, hier = setup_stage_and_hier("/xforms_small.usda")

        # Note: this prim only exists in Fabric
        stage.DefinePrim("/Base/Row_00/Col_09/Dummy", "Xform")
        prim = stage.GetPrimAtPath("/Base/Row_00/Col_09")

        children = prim.GetChildren()

        children_names = set([i.GetName() for i in children])
        expected = set(["Depth_0" + str(i) for i in range(10)])
        expected.add("Dummy")

        self.assertEqual(children_names, expected)

    @tc_logger
    def test_get_next_sibling_with_connectivity(self):
        from usdrt import Gf, Sdf, Usd

        stage, hier = setup_stage_and_hier("/xforms_small.usda")

        # Note: this prim only exists in Fabric
        stage.DefinePrim("/Base/Row_00/Col_09/Dummy", "Xform")
        prim = stage.GetPrimAtPath("/Base/Row_00/Col_09/Depth_09")

        sibling_names = set()
        sibling = prim.GetNextSibling()
        while sibling.GetName() not in sibling_names:
            sibling_names.add(sibling.GetName())
            sibling = sibling.GetNextSibling()

        expected = set(["Depth_0" + str(i) for i in range(10)])
        expected.add("Dummy")

        self.assertEqual(sibling_names, expected)
