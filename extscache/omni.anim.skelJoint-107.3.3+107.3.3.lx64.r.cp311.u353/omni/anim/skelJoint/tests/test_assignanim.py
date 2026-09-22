import omni.kit.ui_test as ui_test
import omni.usd
import omni.kit.undo
from pxr import UsdSkel
import omni.timeline

from omni.anim.skelJoint.scripts import assignAnim

from .base_test import BaseTest


class AssignAnimTest(BaseTest):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def test_assignanim_funcs(self):
        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()

        # has a descendant with animation:
        self.assertTrue(assignAnim.ContainsAnimation(self._stage.GetPrimAtPath("/Root")))

        # has no descendants with animation:
        self.assertFalse(assignAnim.ContainsAnimation(self._stage.GetPrimAtPath("/Root/group1/joint1/joint1")))

        # is an animation:
        self.assertTrue(assignAnim.ContainsAnimation(self._stage.GetPrimAtPath("/Root/group1/joint1/Animation")))

        # invalid:
        self.assertFalse(assignAnim.ContainsAnimation(None))

        # finds a prim with the specified type among descendants:
        skelprim = assignAnim.ContainsPrimType(self._stage.GetPrimAtPath("/Root"), UsdSkel.Skeleton)
        self.assertTrue(skelprim.IsA(UsdSkel.Skeleton))
        self.assertEqual(skelprim.GetPath(), "/Root/group1/joint1")

        # returns null prim for things that don't exist:
        self.assertFalse(assignAnim.ContainsPrimType(self._stage.GetPrimAtPath("/noexist"), UsdSkel.Skeleton))

        # that's the actual skeleton so it should return the skel prim:
        skelprim = assignAnim.ContainsPrimType(self._stage.GetPrimAtPath("/Root/group1/joint1"), UsdSkel.Skeleton)
        self.assertTrue(skelprim.IsA(UsdSkel.Skeleton))
        self.assertEqual(skelprim.GetPath(), "/Root/group1/joint1")

        # traverses up the hierarchy and finds the skeleton:
        skelprim = assignAnim.ContainsPrimType(self._stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2"), UsdSkel.Skeleton)
        self.assertTrue(skelprim.IsA(UsdSkel.Skeleton))
        self.assertEqual(skelprim.GetPath(), "/Root/group1/joint1")

        # has no descendents or ancestors that are skeletons so should return null:
        self.assertFalse(assignAnim.ContainsPrimType(self._stage.GetPrimAtPath("/Root/group1/pCylinder1"), UsdSkel.Skeleton))

        skelprim = assignAnim.GetSkeleton(self._stage.GetPrimAtPath("/Root"))
        self.assertTrue(skelprim.IsA(UsdSkel.Skeleton))
        self.assertEqual(skelprim.GetPath(), "/Root/group1/joint1")

        skelprim = assignAnim.GetSkeleton(self._stage.GetPrimAtPath("/Root/group1/pCylinder1"))
        self.assertTrue(skelprim.IsA(UsdSkel.Skeleton))
        self.assertEqual(skelprim.GetPath(), "/Root/group1/joint1")

        self.assertFalse(assignAnim.GetSkeleton(self._stage.GetPrimAtPath("/woteva")))

    async def test_assignanim_command(self):

        await self.load_stage("skelcylinder_ref.usda")
        await ui_test.wait_n_updates(10)

        self._stage = omni.usd.get_context().get_stage()

        skelprim = self._stage.GetPrimAtPath("/Root/group1/joint1")
        oldanimprim = self._stage.GetPrimAtPath("/Root/group1/joint1/Animation")
        self.assertEqual(UsdSkel.BindingAPI(skelprim).GetAnimationSourceRel().GetTargets(), [oldanimprim.GetPath()])

        animprim = self._stage.GetPrimAtPath("/ZAnimation")

        omni.kit.commands.execute(
            "AssignAnimation",
            skeleton_path="/Root/group1/joint1",
            animprim_path="/ZAnimation"
        )
        self.assertEqual(UsdSkel.BindingAPI(skelprim).GetAnimationSourceRel().GetTargets(), [animprim.GetPath()])

        omni.kit.undo.undo()
        self.assertEqual(UsdSkel.BindingAPI(skelprim).GetAnimationSourceRel().GetTargets(), [oldanimprim.GetPath()])

        with self.assertRaises(Exception):
            assignAnim.AssignAnimation(
                skeleton_path="/Root/group1/joint1/joint1",
                animprim_path="/ZAnimation"
            ).do()

        with self.assertRaises(Exception):
            assignAnim.AssignAnimation(
                skeleton_path="/Root/group1/joint1",
                animprim_path="/Root/group1/pCylinder1"
            ).do()
