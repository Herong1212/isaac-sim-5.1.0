import asyncio
import math
import os

import carb
import numpy as np
import omni.graph.core as og
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.timeline
from omni.anim.shared.core import get_ext
from omni.anim.shared.core.scripts.kit_utils import get_points_attr, get_prim_io, get_time_node, get_xform_attr
from pxr import Gf, UsdUtils
from usdrt import Gf as usdrt_Gf
from usdrt import Sdf as usdrt_Sdf
from usdrt import Usd as usdrt_Usd

REL_TOL = 1e-03  # delta judge if close


class TestAnimShared(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        path_to_file = os.path.join(get_ext().get_ext_path(), "data", "usd", "cube_timesample.usda")
        self._usd_context = omni.usd.get_context()
        carb.settings.get_settings().set("/app/player/playComputegraph", True)
        await self._usd_context.open_stage_async(path_to_file)

        self._stage = self._usd_context.get_stage()

    async def tearDown(self):
        self._usd_context = None
        self._stage = None

    async def test_time_node(self):
        fps = self._stage.GetFramesPerSecond()
        # create the node
        tn = get_time_node()
        omni.timeline.get_timeline_interface().set_current_time(1.0)
        await omni.kit.app.get_app().next_update_async()

        time_attr = og.Controller.attribute("outputs:time", tn)
        time_val = og.Controller.get(time_attr)
        frame_attr = og.Controller.attribute("outputs:frame", tn)
        frame_val = og.Controller.get(frame_attr)
        assert math.isclose(time_val, 1.0, rel_tol=REL_TOL)
        assert math.isclose(frame_val, fps, rel_tol=REL_TOL)

    async def test_get_xform_node(self):

        stage_id = UsdUtils.StageCache.Get().GetId(self._stage).ToLongInt()
        stage = usdrt_Usd.Stage.Attach(stage_id)
        np.random.seed(1)

        def random_mat():

            q = Gf.Quatd(np.random.rand(), np.random.rand(), np.random.rand(), np.random.rand())
            q.Normalize()
            rm = Gf.Matrix4d()
            rm.SetRotate(q)
            sm = Gf.Matrix4d()
            sm.SetScale(Gf.Vec3d(np.random.rand(), np.random.rand(), np.random.rand()))
            mtx = sm * rm
            mtx.SetTranslateOnly(Gf.Vec3d(np.random.rand(), np.random.rand(), np.random.rand()))
            return mtx

        def decompose(mtx):
            scale = (mtx.GetRow3(0).GetLength(), mtx.GetRow3(1).GetLength(), mtx.GetRow3(2).GetLength())
            translation = mtx.ExtractTranslation()

            r0 = mtx.GetRow3(0) / scale[0]
            r1 = mtx.GetRow3(1) / scale[1]
            r2 = mtx.GetRow3(2) / scale[2]

            rotmat = Gf.Matrix3d(r0[0], r0[1], r0[2], r1[0], r1[1], r1[2], r2[0], r2[1], r2[2])
            rotation = rotmat.ExtractRotation().GetQuaternion()

            return translation, rotation, scale

        def transform_prim(prim, mtx, fabric=False):
            if fabric:
                rtprim = stage.GetPrimAtPath(usdrt_Sdf.Path(prim.GetPath().pathString))
                worldPosAttr = rtprim.CreateAttribute("_worldPosition", usdrt_Sdf.ValueTypeNames.Double3, True)
                worldRotAttr = rtprim.CreateAttribute("_worldOrientation", usdrt_Sdf.ValueTypeNames.Quatf, True)
                worldScaleAttr = rtprim.CreateAttribute("_worldScale", usdrt_Sdf.ValueTypeNames.Float3, True)

                translation, rotation, scale = decompose(mtx)

                worldPosAttr.Set(usdrt_Gf.Vec3d(translation[0], translation[1], translation[2]))
                worldRotAttr.Set(
                    usdrt_Gf.Quatf(
                        rotation.GetReal(),
                        rotation.GetImaginary()[0],
                        rotation.GetImaginary()[1],
                        rotation.GetImaginary()[2],
                    )
                )
                worldScaleAttr.Set(usdrt_Gf.Vec3f(scale[0], scale[1], scale[2]))
            else:
                omni.kit.commands.execute("TransformPrimCommand", path=prim.GetPath(), new_transform_matrix=mtx)

        def check_matrix(attr, node, mtx):
            attribute = og.Controller.attribute(attr, node)
            vals = np.array(og.Controller.get(attribute))
            expected = np.array(mtx).reshape(-1)
            self.assertAlmostEqual(((vals - expected) ** 2).sum(), 0)

        xform_prim = self._stage.DefinePrim(f"{self._stage.GetDefaultPrim().GetPath()}/xform", "Xform")
        cube_prim = self._stage.DefinePrim(f"{self._stage.GetDefaultPrim().GetPath()}/xform/cube", "Cube")
        cube_get_xform_node, cube_get_xform_output = get_xform_attr(cube_prim)

        xform_mat = random_mat()
        cube_mat = random_mat()
        cube_world_mat = cube_mat * xform_mat

        # Both the prim and its parent are pure usd:
        transform_prim(xform_prim, xform_mat)
        transform_prim(cube_prim, cube_mat)

        # local mode off: should just return the cube's world matrix:
        og.Controller(cube_get_xform_node.get_attribute("inputs:useLocal")).set(False)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube_get_xform_output, cube_get_xform_node, cube_world_mat)

        # local mode on: should just return cube_mat, which is the cube's object matrix:
        og.Controller(cube_get_xform_node.get_attribute("inputs:useLocal")).set(True)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube_get_xform_output, cube_get_xform_node, cube_mat)

        # Now switch it so the prim's transform is in fabric:
        cube_mat = random_mat()
        transform_prim(cube_prim, cube_mat, fabric=True)

        # local mode off: fabric transforms override the world matrix so the cube's world matrix should just
        # be cube_mat:
        og.Controller(cube_get_xform_node.get_attribute("inputs:useLocal")).set(False)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube_get_xform_output, cube_get_xform_node, cube_mat)

        # local mode on: should return the relative transform between the parent's matrix and cube_mat:
        og.Controller(cube_get_xform_node.get_attribute("inputs:useLocal")).set(True)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube_get_xform_output, cube_get_xform_node, cube_mat * xform_mat.GetInverse())

        # Set fabric data on the parent too:
        xform_mat = random_mat()
        transform_prim(xform_prim, xform_mat, fabric=True)

        # local mode off: fabric transforms override the world matrix so the cube's world matrix should just
        # be cube_mat:
        og.Controller(cube_get_xform_node.get_attribute("inputs:useLocal")).set(False)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube_get_xform_output, cube_get_xform_node, cube_mat)

        # local mode on: should return the relative transform between the parent's matrix and cube_mat:
        og.Controller(cube_get_xform_node.get_attribute("inputs:useLocal")).set(True)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube_get_xform_output, cube_get_xform_node, cube_mat * xform_mat.GetInverse())

        # set fabric xform on parent only:
        xform2_prim = self._stage.DefinePrim(f"{self._stage.GetDefaultPrim().GetPath()}/xform2", "Xform")
        cube2_prim = self._stage.DefinePrim(f"{self._stage.GetDefaultPrim().GetPath()}/xform2/cube2", "Cube")
        cube2_get_xform_node, cube2_get_xform_output = get_xform_attr(cube2_prim)

        xform2_mat_usd = random_mat()
        xform2_mat = random_mat()
        cube2_mat = random_mat()
        cube2_world_mat = cube2_mat * xform2_mat_usd

        transform_prim(xform2_prim, xform2_mat_usd)
        transform_prim(xform2_prim, xform2_mat, fabric=True)
        transform_prim(cube2_prim, cube2_mat)

        # local mode off: transform should just be the world mat of cube2 if this scene were
        # pure usd:
        og.Controller(cube2_get_xform_node.get_attribute("inputs:useLocal")).set(False)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube2_get_xform_output, cube2_get_xform_node, cube2_world_mat)

        # local mode on: transform should just be the relative transform between the world
        # mat of cube2 if this scene were pure usd and the parent's transform:
        og.Controller(cube2_get_xform_node.get_attribute("inputs:useLocal")).set(True)
        await omni.kit.app.get_app().next_update_async()
        check_matrix(cube2_get_xform_output, cube2_get_xform_node, cube2_world_mat * xform2_mat.GetInverse())

    async def test_set_xform_node(self):
        # create the prim
        cube_prim = self._stage.DefinePrim(f"{self._stage.GetDefaultPrim().GetPath()}/cube2", "Cube")

        set_xform_node = get_prim_io(cube_prim, "omni.anim.SetXform", input_attr="inputs:prim")
        og.Controller(set_xform_node.get_attribute("inputs:transform")).set(
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 50, 0, 0, 0]
        )

        await omni.kit.app.get_app().next_update_async()
        vals = cube_prim.GetAttribute("xformOp:translate").Get()
        assert math.isclose(vals[0], 50, rel_tol=REL_TOL)
