import omni.kit.ui_test as ui_test
import omni.usd
import omni.kit.undo
from pxr import UsdSkel, UsdGeom
import OmniSkelSchema
import omni.timeline

from omni.anim.skelJoint.scripts import utils

from .base_test import BaseTest


class SkelJointCommandsTest(BaseTest):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def test_switch_skel_mode(self):
        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()
        omni_skel_prim = self._stage.GetPrimAtPath("/Root/group1/joint1")

        transform_mode = omni_skel_prim.GetCustomDataByKey("TransformMode")
        self.assertEqual(transform_mode, 0)

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=omni_skel_prim.GetPath(),
            transform_mode=1
        )
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 1)

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=omni_skel_prim.GetPath(),
            transform_mode=2
        )
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 2)

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=omni_skel_prim.GetPath(),
            transform_mode=3
        )
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 3)

        omni.kit.undo.undo()
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 2)

        omni.kit.commands.execute(
            "SwitchSkeletonTransformMode",
            skeleton_path=omni_skel_prim.GetPath(),
            transform_mode=0
        )
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 0)

        omni.kit.undo.undo()
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 2)

        omni.kit.undo.undo()
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 1)

        omni.kit.undo.undo()
        self.assertEqual(omni_skel_prim.GetCustomDataByKey("TransformMode"), 0)

    async def test_apply_rest_pose(self):
        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()
        omni_skel_prim = self._stage.GetPrimAtPath("/Root/group1/joint1")
        omni_joint_prim = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1")
        omni_joint_prim2 = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2")
        omni_joint_prim3 = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2/joint3/joint4/joint5")

        attr = omni_joint_prim.GetAttribute("xformOp:rotateXYZ")
        attr2 = omni_joint_prim2.GetAttribute("xformOp:scale")
        attr3 = omni_joint_prim3.GetAttribute("xformOp:translate")

        rest_attr = omni_joint_prim.GetAttribute("restRotation")
        rest_attr2 = omni_joint_prim2.GetAttribute("restScale")
        rest_attr3 = omni_joint_prim3.GetAttribute("restTranslate")

        rest_transforms_attr = omni_skel_prim.GetAttribute("restTransforms")
        rest_transforms_attr_val = rest_transforms_attr.Get()

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr.GetPath(),
            value=(10, 20, 30),
            prev=None
        )

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr2.GetPath(),
            value=(40, 50, 60),
            prev=None
        )

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr3.GetPath(),
            value=(70, 80, 90),
            prev=None
        )

        self.assertEqual(attr.Get(), (10, 20, 30))
        self.assertEqual(attr2.Get(), (40, 50, 60))
        self.assertEqual(attr3.Get(), (70, 80, 90))

        # check everything's at the bind pose:
        omni.kit.commands.execute(
            "ApplyJointRestPoseToSkeletonCommand",
            skeleton_path=omni_skel_prim.GetPath()
        )

        self.assertNotEqual(rest_transforms_attr_val, rest_transforms_attr.Get())

        jts = []
        self.get_all_descendents_joint(omni_skel_prim, jts)
        for jt in jts:
            self.assertEqual(jt.GetAttribute("xformOp:rotateXYZ").Get(), jt.GetAttribute("restRotation").Get())
            self.assertEqual(jt.GetAttribute("xformOp:scale").Get(), jt.GetAttribute("restScale").Get())
            self.assertEqual(jt.GetAttribute("xformOp:translate").Get(), jt.GetAttribute("restTranslation").Get())

        self.assertEqual(attr.Get(), (10, 20, 30))
        self.assertEqual(attr2.Get(), (40, 50, 60))
        self.assertEqual(attr3.Get(), (70, 80, 90))

        omni.kit.undo.undo()

        # check the attributes we changed are back at their original values:
        self.assertNotEqual(attr.Get(), rest_attr.Get())
        self.assertNotEqual(attr2.Get(), rest_attr2.Get())
        self.assertNotEqual(attr3.Get(), rest_attr3.Get())

        # rest transforms attr should have been set back to its original value:
        self.assertEqual(rest_transforms_attr_val, rest_transforms_attr.Get())

    async def test_apply_retarget_pose(self):
        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()
        omni_skel_prim = self._stage.GetPrimAtPath("/Root/group1/joint1")
        omni_joint_prim = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1")
        omni_joint_prim2 = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2")
        omni_joint_prim3 = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2/joint3/joint4/joint5")

        attr = omni_joint_prim.GetAttribute("xformOp:rotateXYZ")
        attr2 = omni_joint_prim2.GetAttribute("xformOp:scale")
        attr3 = omni_joint_prim3.GetAttribute("xformOp:translate")

        retarget_attr = omni_joint_prim.GetAttribute("retargetRotation")
        retarget_attr2 = omni_joint_prim2.GetAttribute("retargetScale")
        retarget_attr3 = omni_joint_prim3.GetAttribute("retargetTranslate")

        retarget_transforms_attr = omni_skel_prim.GetAttribute("controlRig:retargetTransforms")
        retarget_transforms_attr_val = retarget_transforms_attr.Get()

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr.GetPath(),
            value=(10, 20, 30),
            prev=None
        )

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr2.GetPath(),
            value=(40, 50, 60),
            prev=None
        )

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr3.GetPath(),
            value=(70, 80, 90),
            prev=None
        )

        self.assertEqual(attr.Get(), (10, 20, 30))
        self.assertEqual(attr2.Get(), (40, 50, 60))
        self.assertEqual(attr3.Get(), (70, 80, 90))

        omni.kit.commands.execute(
            "ApplyJointRetargetPoseToSkeletonCommand",
            skeleton_path=omni_skel_prim.GetPath()
        )

        # retarget transforms should have been modified:
        self.assertNotEqual(retarget_transforms_attr_val, retarget_transforms_attr.Get())

        jts = []
        self.get_all_descendents_joint(omni_skel_prim, jts)
        for jt in jts:
            self.assertEqual(jt.GetAttribute("xformOp:rotateXYZ").Get(), jt.GetAttribute("retargetRotation").Get())
            self.assertEqual(jt.GetAttribute("xformOp:scale").Get(), jt.GetAttribute("retargetScale").Get())
            self.assertEqual(jt.GetAttribute("xformOp:translate").Get(), jt.GetAttribute("retargetTranslation").Get())

        self.assertEqual(attr.Get(), (10, 20, 30))
        self.assertEqual(attr2.Get(), (40, 50, 60))
        self.assertEqual(attr3.Get(), (70, 80, 90))

        omni.kit.undo.undo()

        # check the attributes we changed are back at their original values:
        self.assertNotEqual(attr.Get(), retarget_attr.Get())
        self.assertNotEqual(attr2.Get(), retarget_attr2.Get())
        self.assertNotEqual(attr3.Get(), retarget_attr3.Get())

        # retarget transforms attr should have been set back to its original value:
        self.assertEqual(retarget_transforms_attr_val, retarget_transforms_attr.Get())

    async def test_reset_to_binding(self):
        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()
        omni_skel_prim = self._stage.GetPrimAtPath("/Root/group1/joint1")
        omni_joint_prim = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1")
        omni_joint_prim2 = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2")
        omni_joint_prim3 = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2/joint3/joint4/joint5")

        attr = omni_joint_prim.GetAttribute("xformOp:rotateXYZ")
        attr2 = omni_joint_prim2.GetAttribute("xformOp:scale")
        attr3 = omni_joint_prim3.GetAttribute("xformOp:translate")

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr.GetPath(),
            value=(10, 20, 30),
            prev=None
        )

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr2.GetPath(),
            value=(40, 50, 60),
            prev=None
        )

        omni.kit.commands.execute(
            "ChangeProperty",
            prop_path=attr3.GetPath(),
            value=(70, 80, 90),
            prev=None
        )

        self.assertEqual(attr.Get(), (10, 20, 30))
        self.assertEqual(attr2.Get(), (40, 50, 60))
        self.assertEqual(attr3.Get(), (70, 80, 90))

        # check everything's at the bind pose:
        omni.kit.commands.execute(
            "ResetToBindingCommand",
            skeleton_path=omni_skel_prim.GetPath()
        )

        jts = []
        self.get_all_descendents_joint(omni_skel_prim, jts)
        for jt in jts:
            self.assertEqual(jt.GetAttribute("xformOp:rotateXYZ").Get(), jt.GetAttribute("bindRotation").Get())
            self.assertEqual(jt.GetAttribute("xformOp:scale").Get(), jt.GetAttribute("bindScale").Get())
            self.assertEqual(jt.GetAttribute("xformOp:translate").Get(), jt.GetAttribute("bindTranslation").Get())

        omni.kit.undo.undo()

        # check the attributes we changed are back at their original values:
        self.assertEqual(attr.Get(), (10, 20, 30))
        self.assertEqual(attr2.Get(), (40, 50, 60))
        self.assertEqual(attr3.Get(), (70, 80, 90))

    async def test_joint_limits_commands(self):

        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()
        omni_joint_prim = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2")

        omni.kit.commands.execute(
            "ApplyOmniSkelJointLimitsAPICommand",
            paths=[omni_joint_prim.GetPath()],
            select_prim=True
        )

        self.assertTrue(omni_joint_prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI))
        self.assertEqual(omni.usd.get_context().get_selection().get_selected_prim_paths(), [omni_joint_prim.GetPath()])
        self.assertTrue(omni_joint_prim.GetProperty("swingHorizontalAngle"))

        omni.kit.undo.undo()

        self.assertFalse(omni_joint_prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI))
        self.assertFalse(omni_joint_prim.GetProperty("swingHorizontalAngle"))

        omni.usd.get_context().get_selection().set_selected_prim_paths([], True)

        omni.kit.commands.execute(
            "ApplyOmniSkelJointLimitsAPICommand",
            paths=[omni_joint_prim.GetPath()],
            select_prim=False
        )

        self.assertTrue(omni_joint_prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI))
        self.assertEqual(omni.usd.get_context().get_selection().get_selected_prim_paths(), [])
        self.assertTrue(omni_joint_prim.GetProperty("swingHorizontalAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("swingVerticalAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("twistMinimumAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("twistMaximumAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("offsetRotation"))
        self.assertTrue(omni_joint_prim.GetProperty("enabled"))

        omni.kit.commands.execute(
            "RemoveOmniSkelJointLimitsAPICommand",
            paths=[omni_joint_prim.GetPath()]
        )

        self.assertFalse(omni_joint_prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI))
        self.assertFalse(omni_joint_prim.GetProperty("swingHorizontalAngle"))
        self.assertFalse(omni_joint_prim.GetProperty("swingVerticalAngle"))
        self.assertFalse(omni_joint_prim.GetProperty("twistMinimumAngle"))
        self.assertFalse(omni_joint_prim.GetProperty("twistMaximumAngle"))
        self.assertFalse(omni_joint_prim.GetProperty("offsetRotation"))
        self.assertFalse(omni_joint_prim.GetProperty("enabled"))

        omni.kit.undo.undo()

        self.assertTrue(omni_joint_prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI))
        self.assertTrue(omni_joint_prim.GetProperty("swingHorizontalAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("swingVerticalAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("twistMinimumAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("twistMaximumAngle"))
        self.assertTrue(omni_joint_prim.GetProperty("offsetRotation"))
        self.assertTrue(omni_joint_prim.GetProperty("enabled"))

    async def test_joint_shape_commands(self):

        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()
        omni_joint_prim = self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2")
        path = omni_joint_prim.GetPath().AppendPath("newprim")
        testlist = [
            ("CreateOmniSkelJointBoxShapeCommand", OmniSkelSchema.OmniJointBoxShapeAPI, UsdGeom.Cube),
            ("CreateOmniSkelJointSphereShapeCommand", OmniSkelSchema.OmniJointSphereShapeAPI, UsdGeom.Sphere),
            ("CreateOmniSkelJointCapsuleShapeCommand", OmniSkelSchema.OmniJointCapsuleShapeAPI, UsdGeom.Capsule),
        ]

        for cmd, api, primtype in testlist:

            omni.kit.commands.execute(
                cmd,
                paths=[str(path)],
                select_prim=True
            )

            newPrim = self._stage.GetPrimAtPath(path)
            self.assertTrue(newPrim)
            self.assertTrue(newPrim.HasAPI(api))
            self.assertTrue(newPrim.IsA(primtype))
            self.assertEqual(newPrim.GetProperty("purpose").Get(), "guide")
            self.assertEqual(omni.usd.get_context().get_selection().get_selected_prim_paths(), [path])

            omni.kit.undo.undo()

            self.assertFalse(self._stage.GetPrimAtPath(path))

            omni.kit.commands.execute(
                cmd,
                paths=[str(path)],
                select_prim=False
            )

            newPrim = self._stage.GetPrimAtPath(path)
            self.assertTrue(newPrim)
            self.assertTrue(newPrim.HasAPI(api))
            self.assertTrue(newPrim.IsA(primtype))
            self.assertEqual(newPrim.GetProperty("purpose").Get(), "guide")
            self.assertEqual(omni.usd.get_context().get_selection().get_selected_prim_paths(), [])

            omni.kit.undo.undo()

            self.assertFalse(self._stage.GetPrimAtPath(path))

    async def test_joint_poses_command(self):

        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        stage = omni.usd.get_context().get_stage()

        skel = UsdSkel.Skeleton(stage.GetPrimAtPath("/Root/group1/joint1"))
        t, r, s, o = utils.get_joint_poses(skel)

        omni.kit.commands.execute(
            "SetJointPosesCommand",
            skeleton_path=skel.GetPath(),
            stage=stage,
            translations=t,
            rotations=[(30, 30, 30) for x in r],
            scales=s,
            rotation_orders=o
        )

        t_new, r_new, s_new, o_new = utils.get_joint_poses(skel)
        self.assertEqual(t, t_new)
        self.assertNotEqual(r, r_new)
        self.assertEqual(s, s_new)
        self.assertEqual(o, o_new)

        omni.kit.undo.undo()

        t_new, r_new, s_new, o_new = utils.get_joint_poses(skel)
        self.assertEqual(t, t_new)
        self.assertEqual(r, r_new)
        self.assertEqual(s, s_new)
        self.assertEqual(o, o_new)

    def get_all_descendents_joint(self, prim, output=[]):
        if prim and prim.IsA(OmniSkelSchema.OmniJoint):
            output.append(prim)
        for child in prim.GetChildren():
            self.get_all_descendents_joint(child, output)