import omni.kit.ui_test as ui_test
import omni.usd
from pxr import UsdSkel
import omni.timeline


from .base_test import BaseTest


class SavePoseTest(BaseTest):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def test_savepose_command(self):
        await self.load_stage("skelcylinder_ref.usda")
        self._stage = self._context.get_stage()

        await ui_test.human_delay(10)
        skel_anim = UsdSkel.Animation.Define(self._stage,"/Root/SkelPreviewAnimation")
        skel_prim = self._stage.GetPrimAtPath("/Root/group1/joint1")

        omni.kit.commands.execute(
            "AssignAnimation",
            skeleton_path="/Root/group1/joint1",
            animprim_path="/Root/SkelPreviewAnimation"
        )

        # test with skeleton selected:
        omni.usd.get_context().get_selection().set_selected_prim_paths(
            ["/Root/group1/joint1"],
            True
        )
        omni.kit.commands.execute(
            "SaveSkelPoseCommand",
            save_target="animation"
        )

        # should have set values on these attrs:
        self.assertTrue(skel_anim.GetTranslationsAttr().Get())
        self.assertTrue(skel_anim.GetRotationsAttr().Get())
        self.assertTrue(skel_anim.GetScalesAttr().Get())

        omni.kit.undo.undo()

        # attrs should have been cleared:
        self.assertFalse(skel_anim.GetTranslationsAttr().Get())
        self.assertFalse(skel_anim.GetRotationsAttr().Get())
        self.assertFalse(skel_anim.GetScalesAttr().Get())

        # test with skelroot selected:
        omni.usd.get_context().get_selection().set_selected_prim_paths(
            ["/Root/group1"],
            True
        )
        omni.kit.commands.execute(
            "SaveSkelPoseCommand",
            save_target="animation"
        )

        # should have set values on these attrs:
        self.assertTrue(skel_anim.GetTranslationsAttr().Get())
        self.assertTrue(skel_anim.GetRotationsAttr().Get())
        self.assertTrue(skel_anim.GetScalesAttr().Get())

        omni.kit.undo.undo()

        # attrs should have been cleared:
        self.assertFalse(skel_anim.GetTranslationsAttr().Get())
        self.assertFalse(skel_anim.GetRotationsAttr().Get())
        self.assertFalse(skel_anim.GetScalesAttr().Get())


        # test with joint selected:
        omni.usd.get_context().get_selection().set_selected_prim_paths(
            ["/Root/group1/joint1/joint1/joint2"],
            True
        )
        omni.kit.commands.execute(
            "SaveSkelPoseCommand",
            save_target="animation"
        )

        # should have set values on these attrs:
        self.assertTrue(skel_anim.GetTranslationsAttr().Get())
        self.assertTrue(skel_anim.GetRotationsAttr().Get())
        self.assertTrue(skel_anim.GetScalesAttr().Get())

        omni.kit.undo.undo()

        # attrs should have been cleared:
        self.assertFalse(skel_anim.GetTranslationsAttr().Get())
        self.assertFalse(skel_anim.GetRotationsAttr().Get())
        self.assertFalse(skel_anim.GetScalesAttr().Get())


        # test with the mesh selected:
        omni.usd.get_context().get_selection().set_selected_prim_paths(
            ["/Root/group1/pCylinder1"],
            True
        )
        omni.kit.commands.execute(
            "SaveSkelPoseCommand",
            save_target="animation"
        )

        # should have set values on these attrs:
        self.assertTrue(skel_anim.GetTranslationsAttr().Get())
        self.assertTrue(skel_anim.GetRotationsAttr().Get())
        self.assertTrue(skel_anim.GetScalesAttr().Get())

        omni.kit.undo.undo()

        # attrs should have been cleared:
        self.assertFalse(skel_anim.GetTranslationsAttr().Get())
        self.assertFalse(skel_anim.GetRotationsAttr().Get())
        self.assertFalse(skel_anim.GetScalesAttr().Get())

        # test for rest pose:
        initRest = UsdSkel.Skeleton(skel_prim).GetRestTransformsAttr().Get()

        # undo anim assign:
        omni.kit.undo.undo()
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_current_time(13.0)
        omni.kit.commands.execute(
            "SaveSkelPoseCommand",
            save_target="rest_pose"
        )

        self.assertNotEqual(initRest, UsdSkel.Skeleton(skel_prim).GetRestTransformsAttr().Get())

        omni.kit.undo.undo()

        self.assertEqual(initRest,UsdSkel.Skeleton(skel_prim).GetRestTransformsAttr().Get())
