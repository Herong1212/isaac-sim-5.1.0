import omni.kit.ui_test as ui_test
import omni.usd
import omni.kit.undo
from pxr import UsdSkel
import OmniSkelSchema
import omni.timeline

from omni.anim.skelJoint.scripts import utils

from .base_test import BaseTest
import numpy as np


class UtilsTest(BaseTest):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def test_find_skeleton(self):

        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        stage = omni.usd.get_context().get_stage()
        skel = utils.find_skeleton(stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2"))
        self.assertTrue(skel.IsA(UsdSkel.Skeleton) and skel.HasAPI(OmniSkelSchema.OmniSkeletonAPI))

        skel = utils.find_skeleton(stage.GetPrimAtPath("/Root/group1/joint1"))
        self.assertTrue(skel.IsA(UsdSkel.Skeleton) and skel.HasAPI(OmniSkelSchema.OmniSkeletonAPI))

        self.assertFalse(utils.find_skeleton(stage.GetPrimAtPath("/Root/group1")))

    async def test_get_joint_rotation_order_and_attrname(self):

        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        stage = omni.usd.get_context().get_stage()
        self.assertEqual(
            utils.get_joint_rotation_order_and_attrname(stage.GetPrimAtPath("/Root/group1")), ['', '']
        )
        jointPrim = stage.GetPrimAtPath("/Root/group1/joint1/joint1")
        self.assertEqual(
            utils.get_joint_rotation_order_and_attrname(jointPrim),
            ['rotateXYZ', 'xformOp:rotateXYZ']
        )

        omni.kit.commands.execute(
            "ChangeRotationOp",
            src_op_attr_path="/Root/group1/joint1/joint1.xformOp:rotateXYZ",
            op_name="xformOp:rotateXYZ",
            dst_op_attr_name="xformOp:rotateXZY",
            is_inverse_op=False,
            auto_target_layer=True
        )
        self.assertEqual(
            utils.get_joint_rotation_order_and_attrname(jointPrim),
            ['rotateXZY', 'xformOp:rotateXZY']
        )

    async def test_poses(self):

        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        stage = omni.usd.get_context().get_stage()
        skel = UsdSkel.Skeleton(stage.GetPrimAtPath("/Root/group1/joint1"))

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=skel.GetPath(),
            transform_mode=0
        )

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=skel.GetPath(),
            transform_mode=1
        )

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=skel.GetPath(),
            transform_mode=2
        )

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=skel.GetPath(),
            transform_mode=3
        )

        utils.set_joint_poses(skel, *utils.get_bind_poses(skel))

        def equal_poses(p1, p2):
            maxdiff = np.abs(np.array(p1[:3]) - np.array(p2[:3])).max()
            return maxdiff < 1.e-5 and p1[3] == p2[3]

        self.assertEqual(
            utils.is_joint_poses_matching_bind_poses(skel),
            equal_poses(utils.get_bind_poses(skel), utils.get_joint_poses(skel))
        )

        self.assertEqual(
            utils.is_joint_poses_matching_rest_poses(skel),
            equal_poses(utils.get_rest_poses(skel), utils.get_joint_poses(skel))
        )

        self.assertEqual(
            utils.is_joint_poses_matching_retarget_poses(skel),
            equal_poses(utils.get_retarget_poses(skel), utils.get_joint_poses(skel))
        )
