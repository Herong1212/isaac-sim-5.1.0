import omni.kit.ui_test as ui_test
import omni.usd
from pxr import UsdSkel, Gf
import OmniSkelSchema
import omni.timeline
import usdrt

from .base_test import BaseTest


class SkelJointTest(BaseTest):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def test_skelJoint_generate(self):
        await self.load_stage("skelcylinder_ref.usda")
        self._stage = self._context.get_stage()

        await ui_test.human_delay(10)

        usd_skel_prim = self._stage.GetPrimAtPath("/Root/group1/joint1")
        self.assertTrue(usd_skel_prim.IsA(UsdSkel.Skeleton))

        await ui_test.human_delay(10)

        omni_skel_prim = self._stage.GetPrimAtPath("/Root/group1/joint1")
        self.assertTrue(omni_skel_prim and omni_skel_prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI))

    async def test_skelJoint_omni_joint_transformation_loadable_with_usdrt(self):
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        timeline.set_current_time(0.0)
        timeline.set_auto_update(False)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.load_stage("skelcylinder_ref.usda")
        self._stage = self._context.get_stage()

        await ui_test.human_delay(10)
        omni_joint_path = "/Root/group1/joint1/joint1/joint2"
        omni_joint_prim = self._stage.GetPrimAtPath(omni_joint_path)

        self.assertTrue(omni_joint_prim.IsA(OmniSkelSchema.OmniJoint))

        usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        prim = usdrt_stage.GetPrimAtPath(usdrt.Sdf.Path(omni_joint_path))

        timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        initial_local_position = prim.GetAttribute('_localPosition').Get()
        initial_local_rotation = prim.GetAttribute('_localOrientation').Get()
        expected_initial_local_position = Gf.Vec3f(3.0272298, -9.8607613e-32, 7.910339e-16)
        expected_initial_local_rotation = Gf.Quatf(0.9999479, 1.9756056e-36, -0.010210691, -8.708908e-37)
        self._compare_translation(initial_local_position, expected_initial_local_position)
        self._compare_quaternion(initial_local_rotation, expected_initial_local_rotation)

        for i in range(20):
            timeline.forward_one_frame()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        end_local_position = prim.GetAttribute('_localPosition').Get()
        end_local_rotation = prim.GetAttribute('_localOrientation').Get()
        expected_end_local_position = Gf.Vec3f(3.0272298, -9.8607613e-32, 7.910339e-16)
        expected_end_local_rotation = Gf.Quatf(0.9271051, -3.814175e-35, 0.37480146, 1.1338883e-34)
        self._compare_translation(end_local_position, expected_end_local_position)
        self._compare_quaternion(end_local_rotation, expected_end_local_rotation)

    def _compare_translation(self, vector_a: Gf.Vec3f, vector_b: Gf.Vec3f):
        diff = [abs(vector_a[0] - vector_b[0]), abs(vector_a[1] - vector_b[1]), abs(vector_a[2] - vector_b[2])]
        self.assertLessEqual(max(diff), 1e-3)

    def _compare_quaternion(self, vector_a: Gf.Quatf, vector_b: Gf.Quatf):
        dot_product = (vector_a.Normalize() * vector_b.Normalize()).GetLength()
        self.assertLessEqual(abs(dot_product - 1.0), 1e-3)
