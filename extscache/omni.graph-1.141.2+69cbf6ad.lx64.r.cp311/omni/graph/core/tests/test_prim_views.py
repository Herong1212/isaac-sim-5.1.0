# pylint: disable=broad-exception-raised
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.usd
import usdrt.Sdf
import usdrt.Usd
from pxr import Usd


def _get_usd_rt_stage(stage: Usd.Stage):
    try:
        from pxr import UsdUtils

        stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
        fabric_active_for_stage = usdrt.Usd.Stage.StageWithHistoryExists(stage_id)
        if fabric_active_for_stage:
            return usdrt.Usd.Stage.Attach(stage_id)
    except ImportError:
        pass
    return None


class TestPrimView(ogts.OmniGraphTestCase):
    def _create_xform_prim(self, name: str, translate_value):
        """Creates an xform prim"""
        prim = self._stage.DefinePrim(name, "Xform")
        translate = prim.CreateAttribute("xformOp:translate", usdrt.Sdf.ValueTypeNames.Double3, False)
        translate.Set(translate_value)
        self._prim_names.append(name)
        self._num_xforms = self._num_xforms + 1

    def _create_sphere_prim(self, name: str, translate_value, radius_value):
        """Creates a sphere prim"""
        prim = self._stage.DefinePrim(name, "Sphere")
        translate = prim.CreateAttribute("xformOp:translate", usdrt.Sdf.ValueTypeNames.Double3, False)
        translate.Set(translate_value)
        radius = prim.CreateAttribute("radius", usdrt.Sdf.ValueTypeNames.Double, False)
        radius.Set(radius_value)
        self._prim_names.append(name)
        self._num_spheres = self._num_spheres + 1

    def _remove_prim(self, path: str):
        """Removes an xform prim"""
        if self._stage.RemovePrim(usdrt.Sdf.Path(path)):
            from contextlib import suppress

            with suppress(ValueError):
                self._prim_names.remove(path)
        else:
            raise Exception("Failed to remove prim")

    def _add_attribute(self, path: str, name: str, type_name: usdrt.Sdf.ValueTypeNames, value):
        prim = self._stage.GetPrimAtPath(usdrt.Sdf.Path(path))
        if not prim:
            raise Exception(f"Prim {path} not found")
        attr = prim.CreateAttribute(name, type_name, False)
        if not attr:
            raise Exception(f"Could not add {name} attribute to {path}")
        attr.Set(value)

    def _remove_attribute(self, path: str, name: str):
        prim = self._stage.GetPrimAtPath(usdrt.Sdf.Path(path))
        if not prim:
            raise Exception(f"Prim {path} not found")
        if not prim.RemoveProperty(name):
            raise Exception(f"Could not remove {name} attribute from {path}")

    async def setUp(self):
        await super().setUp()
        self._stage = _get_usd_rt_stage(omni.usd.get_context().get_stage())
        self._num_xforms = 0
        self._num_spheres = 0
        self._prim_names = []

        # sets up a stage with 2 buckets of prims containing xformOp:translate attribute
        for i in range(10):
            self._create_xform_prim(f"/World/Xform{i}", (i, i, i))

        for i in range(20):
            self._create_sphere_prim(f"/World/Sphere{i}", (i, i, i), i)

    async def test_prim_view_from_prims(self):
        """Tests basic functionality of a simple, non-segmented prim view"""
        # Create a prim view from a list of prims
        prim_view = og.create_prim_view_from_prims(self._prim_names)
        self.assertIsNotNone(prim_view)
        self.assertEqual(len(prim_view.paths), len(self._prim_names))
        self.assertEqual(len(prim_view.segments), len(self._prim_names))

    async def test_prim_view_from_attributes(self):
        """Tests basic functionality of a simple, segmented prim view"""

        query = [("xformOp:translate", og.Type(og.BaseDataType.DOUBLE, 3))]

        prim_view = og.create_prim_view_from_query(query)
        og.Controller().create_graph("/World/Graph").set_prim_view(prim_view)

        self.assertIsNotNone(prim_view)
        self.assertEqual(len(self._prim_names), len(prim_view.paths))
        self.assertEqual(2, len(prim_view.segments))
        self.assertEqual(self._num_xforms, len(prim_view.segments[0]))
        self.assertEqual(self._num_spheres, len(prim_view.segments[1]))

    async def test_prim_view_from_attributes_handles_changes(self):
        """Tests that the attribute handles additions to the stage"""
        query = [("xformOp:translate", og.Type(og.BaseDataType.DOUBLE, 3))]

        prim_view = og.create_prim_view_from_query(query)
        og.Controller().create_graph("/World/Graph").set_prim_view(prim_view)

        self.assertIsNotNone(prim_view)
        self.assertEqual(len(self._prim_names), len(prim_view.paths))

        # Add a new prim with xformOp:translate attribute
        for i in range(0, 5):
            self._create_xform_prim(f"/World/XtraXform{i}", (i, 0, i))
            self.assertEqual(len(self._prim_names), len(prim_view.paths))

    async def test_prim_view_from_attributes_removal(self):
        """Tests that the attribute handles additions to the stage"""
        query = [("xformOp:translate", og.Type(og.BaseDataType.DOUBLE, 3))]

        prim_view = og.create_prim_view_from_query(query)
        og.Controller().create_graph("/World/Graph").set_prim_view(prim_view)

        self.assertIsNotNone(prim_view)
        self.assertEqual(len(self._prim_names), len(prim_view.paths))

        # remove prims, and check if the prim view is updated
        for i in range(0, 5):
            self._remove_prim(f"/World/Xform{i}")
            self.assertEqual(len(self._prim_names), len(prim_view.paths))

    async def test_prim_view_from_attributes_handles_rebucket(self):
        """Tests a prim view under various rebucketing scenarios"""
        query = [("xformOp:translate", og.Type(og.BaseDataType.DOUBLE, 3))]

        prim_view = og.create_prim_view_from_query(query)
        og.Controller().create_graph("/World/Graph").set_prim_view(prim_view)

        self.assertIsNotNone(prim_view)
        self.assertEqual(len(self._prim_names), len(prim_view.paths))

        # rebucket prims
        prev_segment_count = len(prim_view.segments)
        for i in range(0, 5):
            self._add_attribute(f"/World/Xform{i}", "xformOp:scale", usdrt.Sdf.ValueTypeNames.Double3, (i, i, i))
            self.assertEqual(len(self._prim_names), len(prim_view.paths))
        self.assertEqual(prev_segment_count + 1, len(prim_view.segments))

        # remove the filtered attribute
        expected_count = len(self._prim_names)
        for i in range(6, 10):
            self._remove_attribute(f"/World/Xform{i}", "xformOp:translate")
            expected_count = expected_count - 1
            self.assertEqual(expected_count, len(prim_view.paths))

        # remove a non-filtered attribute
        for i in range(0, 5):
            self._remove_attribute(f"/World/Sphere{i}", "radius")
            self.assertEqual(expected_count, len(prim_view.paths))

    async def test_prim_view_paths_binding(self):
        """Tests that prim view paths binding returns a list of paths"""

        query = [("xformOp:translate", og.Type(og.BaseDataType.DOUBLE, 3))]

        prim_view = og.create_prim_view_from_query(query)
        og.Controller().create_graph("/World/Graph").set_prim_view(prim_view)

        # Validate that the paths are the same, order independent
        self.assertEqual(sorted(prim_view.paths), sorted(self._prim_names))
