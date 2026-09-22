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
import sys
import time
import unittest

from . import TestRtScenegraph, get_data_path, tc_logger

DATA_DIR = get_data_path()


def setUpModule():
    try:
        if platform.processor() == "aarch64":
            # warp not supported on aarch64 yet for our testing
            return

        import warp as wp

        wp.init()
    except ImportError:
        # not needed in Kit
        pass


class TestDocExamples(TestRtScenegraph):
    @tc_logger
    def test_usdrt_one_property(self):
        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # Begin example one property RT

        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        path = "/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back"
        prim = stage.GetPrimAtPath(path)
        attr = prim.GetAttribute(UsdGeom.Tokens.primvarsDisplayColor)

        # Get the value of displayColor on White_Wall_Back,
        # which is mid-gray on this stage
        result = attr.Get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], Gf.Vec3f(0.5, 0.5, 0.5))

        # Set the value of displayColor to red,
        # and verify the change by getting the value
        attr.Set(Vt.Vec3fArray([Gf.Vec3f(1, 0, 0)]))
        result = attr.Get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], Gf.Vec3f(1, 0, 0))

        # End example one property RT

    @tc_logger
    def test_usd_one_property(self):
        from pxr import Gf, Sdf, Usd, UsdUtils, Vt

        # FIXME - Fabric is holding notices to a stage in the cache
        # and gets hung here if the cache isn't cleared first - How?
        UsdUtils.StageCache.Get().Clear()

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # Begin example one property USD

        from pxr import Gf, Sdf, Usd, Vt

        path = "/Cornell_Box/Root/Cornell_Box1_LP/White_Wall_Back"
        prim = stage.GetPrimAtPath(path)
        attr = prim.GetAttribute("primvars:displayColor")

        # Get the value of displayColor on White_Wall_Back,
        # which is mid-gray on this stage
        result = attr.Get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], Gf.Vec3f(0.5, 0.5, 0.5))

        # Set the value of displayColor to red,
        # and verify the change by getting the value
        attr.Set(Vt.Vec3fArray([Gf.Vec3f(1, 0, 0)]))
        result = attr.Get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], Gf.Vec3f(1, 0, 0))

        # End example one property USD

    @tc_logger
    def test_usdrt_many_property(self):
        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # Begin example many prims RT

        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        red = Vt.Vec3fArray([Gf.Vec3f(1, 0, 0)])
        meshPaths = stage.GetPrimsWithTypeName("Mesh")
        for meshPath in meshPaths:
            prim = stage.GetPrimAtPath(meshPath)
            if prim.HasAttribute(UsdGeom.Tokens.primvarsDisplayColor):
                prim.GetAttribute(UsdGeom.Tokens.primvarsDisplayColor).Set(red)

        # End example many prims RT

    @tc_logger
    def test_usdrt_abstract_schema_query(self):
        from usdrt import Gf, Sdf, Usd, UsdGeom, Vt

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # Begin example abstract query

        from usdrt import Gf, Sdf, Usd, UsdGeom

        gPrimPaths = stage.GetPrimsWithTypeName("Gprim")
        attr = UsdGeom.Tokens.doubleSided
        doubleSided = []
        for gPrimPath in gPrimPaths:
            prim = stage.GetPrimAtPath(gPrimPath)
            if prim.HasAttribute(attr) and prim.GetAttribute(attr).Get():
                doubleSided.append(prim)

        # End example abstract query

    @tc_logger
    def test_usd_many_property(self):
        from pxr import Gf, Sdf, Usd, UsdUtils

        # FIXME - Fabric is holding notices to a stage in the cache
        # and gets hung here if the cache isn't cleared first - How?
        UsdUtils.StageCache.Get().Clear()

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # Begin example many prims USD

        from pxr import Gf, Usd, UsdGeom, Vt

        red = Vt.Vec3fArray([Gf.Vec3f(1, 0, 0)])
        for prim in stage.Traverse():
            if prim.GetTypeName() == "Mesh":
                prim.GetAttribute(UsdGeom.Tokens.primvarsDisplayColor).Set(red)

        # End example many prims USD

    @tc_logger
    def test_usdrt_one_relationship(self):
        from usdrt import Gf, Sdf, Usd, UsdShade

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # Begin example relationship RT

        from usdrt import Gf, Sdf, Usd, UsdGeom

        path = "/Cornell_Box/Root/Cornell_Box1_LP/Green_Wall/Green1SG"
        prim = stage.GetPrimAtPath(path)
        rel = prim.GetRelationship(UsdShade.Tokens.materialBinding)

        # The currently bound Material prim, and a new
        # Material prim to bind
        old_mtl = "/Cornell_Box/Root/Looks/Green1SG"
        new_mtl = "/Cornell_Box/Root/Looks/Red1SG"

        # Get the first target
        self.assertTrue(rel.HasAuthoredTargets())
        mtl_path = rel.GetTargets()[0]
        self.assertEqual(mtl_path, old_mtl)

        # Update the relationship to target a different material
        rel.SetTargets([new_mtl])
        updated_path = rel.GetTargets()[0]
        self.assertEqual(updated_path, new_mtl)

        # End example relationship RT

    @tc_logger
    def test_usd_one_relationship(self):
        from pxr import Gf, Sdf, Usd, UsdUtils, Vt

        # FIXME - Fabric is holding notices to a stage in the cache
        # and gets hung here if the cache isn't cleared first - How?
        UsdUtils.StageCache.Get().Clear()

        stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        self.assertTrue(stage)

        # Begin example relationship USD

        from pxr import Gf, Sdf, Usd

        path = "/Cornell_Box/Root/Cornell_Box1_LP/Green_Wall/Green1SG"
        prim = stage.GetPrimAtPath(path)
        rel = prim.GetRelationship("material:binding")

        # The currently bound Material prim, and a new
        # Material prim to bind
        old_mtl = "/Cornell_Box/Root/Looks/Green1SG"
        new_mtl = "/Cornell_Box/Root/Looks/Red1SG"

        # Get the first target
        self.assertTrue(rel.HasAuthoredTargets())
        mtl_path = rel.GetTargets()[0]
        self.assertEqual(mtl_path, old_mtl)

        # Update the relationship to target a different material
        rel.SetTargets([new_mtl])
        updated_path = rel.GetTargets()[0]
        self.assertEqual(updated_path, new_mtl)

        # End example relationship USD

    @tc_logger
    def test_usd_usdrt_interop(self):
        if True:
            # FIXME - crash on Linux here on TC why?
            return

        from pxr import UsdUtils

        # Paranoia - see above test
        UsdUtils.StageCache.Get().Clear()

        # Begin example interop
        from pxr import Sdf, Usd, UsdUtils
        from usdrt import Usd as RtUsd

        usd_stage = Usd.Stage.Open(DATA_DIR + "/cornell.usda")
        usd_stage_id = UsdUtils.StageCache.Get().Insert(usd_stage)

        stage = RtUsd.Stage.Attach(usd_stage_id.ToLongInt())

        mesh_paths = stage.GetPrimsWithTypeName("Mesh")

        for mesh_path in mesh_paths:
            # strings can be implicitly converted to SdfPath in Python
            usd_prim = usd_stage.GetPrimAtPath(str(mesh_path))

            if usd_prim.HasVariantSets():
                print(f"Found Mesh with variantSet: {mesh_path}")

        # End example interop

    @tc_logger
    def test_vt_array_gpu(self):
        if platform.processor() == "aarch64":
            return

        import weakref

        try:
            import warp as wp
        except ImportError:
            return

        # Begin example GPU

        import numpy as np
        import warp as wp
        from usdrt import Gf, Sdf, Usd, Vt

        def warp_array_from_cuda_array_interface(a):
            cai = a.__cuda_array_interface__
            return wp.types.array(
                dtype=wp.vec3,
                length=cai["shape"][0],
                capacity=cai["shape"][0] * wp.types.type_size_in_bytes(wp.vec3),
                ptr=cai["data"][0],
                device="cuda",
                owner=False,
                requires_grad=False,
            )

        stage = Usd.Stage.CreateInMemory("test.usda")

        prim = stage.DefinePrim(Sdf.Path("/prim"))
        attr = prim.CreateAttribute("points", Sdf.ValueTypeNames.Point3fArray, True)

        # First create a warp array from numpy
        points = np.zeros(shape=(1024, 3), dtype=np.float32)
        for i in range(1024):
            for j in range(3):
                points[i][j] = i * 3 + j

        warp_points = wp.array(points, device="cpu")

        with wp.ScopedDevice("cuda"):
            gpu_warp_points = warp_points.to("cuda")
            warp_ref = weakref.ref(gpu_warp_points)

            # Create a VtArray from a warp array
            vt_points = Vt.Vec3fArray(gpu_warp_points)

            # Set the Fabric attribute which will make a CUDA copy
            # from warp to Fabric
            attr.Set(vt_points)
            wp.synchronize()

            # Retrieve a new Fabric VtArray from USDRT
            new_vt_points = attr.Get()
            self.assertTrue(new_vt_points.HasFabricGpuData())

            # Create a warp array from the VtArray
            new_warp_points = warp_array_from_cuda_array_interface(new_vt_points)

            # Delete the fabric VtArray to ensure the data was
            # really copied into warp
            del new_vt_points

            # Convert warp points back to numpy
            new_points = new_warp_points.numpy()

        # Now compare the round-trip through USDRT and GPU was a success
        self.assertEqual(points.shape, new_points.shape)
        for i in range(1024):
            for j in range(3):
                self.assertEqual(points[i][j], new_points[i][j])

        # End example GPU

    @tc_logger
    def test_prim_selection_by_prim_type(self):
        # Begin populate cornell.usda for examples
        # Load a USD stage and populate Fabric with it
        from usdrt import Rt, Sdf, Usd

        stage = Usd.Stage.Open(DATA_DIR + "/cornell_with_physics.usda")
        for prim in stage.Traverse():  # Populate Fabric
            pass
        # End populate cornell.usda for examples

        # Begin example making a prim selection by prim type
        selection = stage.SelectPrims(require_prim_type="Mesh", device="cpu")
        print(f"Found {selection.GetCount()} meshes")
        # End example making a prim selection by prim type

    @tc_logger
    def test_prim_selection_by_prim_type_and_applied_schema(self):

        from usdrt import Rt, Sdf, Usd

        # Load a USD stage and populate Fabric with it
        stage = Usd.Stage.Open(DATA_DIR + "/cornell_with_physics.usda")

        for prim in stage.Traverse():
            pass

        # Begin example making a prim selection by prim type and applied schema
        selection = stage.SelectPrims(
            require_prim_type="Mesh", require_applied_schemas=["PhysicsRigidBodyAPI"], device="cpu"
        )
        print(f"Found {selection.GetCount()} physics meshes")
        # End example making a prim selection by prim type and applied schema

    @tc_logger
    def test_change_position_of_selected_prims(self):
        if platform.processor() == "aarch64":
            return

        # import omni.usd
        import warp as wp
        from usdrt import Gf, Rt, Sdf, Usd, UsdGeom

        # Load a USD stage and populate Fabric with it
        stage = Usd.Stage.Open(DATA_DIR + "/cornell_with_physics.usda")
        for prim in stage.Traverse():
            pass

        # Begin example setting world position, select prims
        sel = stage.SelectPrims(
            require_attrs=[(Sdf.ValueTypeNames.Matrix4d, "omni:fabric:localMatrix", Usd.Access.ReadWrite)],
            require_prim_type="Cube",
            device="cuda:0",
        )
        # End example setting world position, select prims

        # Begin example setting world position, kernel
        @wp.kernel(enable_backward=False)
        def move_prims(xforms: wp.fabricarray(dtype=wp.mat44d)):
            i = wp.tid()
            old_y = xforms[i][3][1]
            # Note: Each [] operator returns by value for differentiability reasons.
            xforms[i] = wp.mat44d(
                wp.vec4d(wp.float64(1.0), wp.float64(0.0), wp.float64(0.0), wp.float64(0.0)),
                wp.vec4d(wp.float64(0.0), wp.float64(1.0), wp.float64(0.0), old_y + wp.float64(19.0)),
                wp.vec4d(wp.float64(0.0), wp.float64(0.0), wp.float64(1.0), wp.float64(0.0)),
                wp.vec4d(wp.float64(0.0), wp.float64(0.0), wp.float64(0.0), wp.float64(1.0)),
            )

        # End example setting world position, kernel

        # Begin example setting world position, apply kernel
        with wp.ScopedDevice("cuda:0"):
            xforms = wp.fabricarray(sel, "omni:fabric:localMatrix")
            wp.launch(move_prims, dim=xforms.size, inputs=[xforms], device="cuda:0")
        # End example setting world position, apply kernel

    @tc_logger
    def test_select_by_prim_type_with_attributes(self):
        if platform.processor() == "aarch64":
            return

        import warp as wp
        from usdrt import Rt, Sdf, Usd, UsdGeom
        from warp.tests.test_fabricarray import _create_fabric_array_array_interface

        wp.config.cache_kernels = False

        # Load a USD stage and populate Fabric with it
        stage = Usd.Stage.Open(DATA_DIR + "/cornell_with_physics.usda")
        for prim in stage.Traverse():
            pass

        # Begin example setting array-valued attribute, select prims
        selection = stage.SelectPrims(
            require_attrs=[
                (Sdf.ValueTypeNames.Color3fArray, UsdGeom.Tokens.primvarsDisplayColor, Usd.Access.ReadWrite)
            ],
            require_prim_type="Mesh",
            device="cpu",
        )

        print(f"Found {selection.GetCount()} meshes with displayColor")
        # End example setting array-valued attribute, select prims

        # Begin example setting array-valued attribute, kernel
        @wp.kernel(enable_backward=False)
        def change_colors(colors: wp.fabricarrayarray(dtype=wp.vec3f)):
            i = wp.tid()
            # Note: Each [] operator returns by value for differentiability reasons.
            colors[i, 0] = wp.vec3f(1.0, 0.0, 0.0)

        # End example setting array-valued attribute, kernel

        # Begin example setting array-valued attribute, apply kernel
        with wp.ScopedDevice("cpu"):
            colors = wp.fabricarrayarray(data=selection, attrib="primvars:displayColor")
            wp.launch(change_colors, dim=colors.size, inputs=[colors], device="cpu")
        # End example setting array-valued attribute, apply kernel
