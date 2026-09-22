
from pathlib import Path
import omni.ui as ui
from pxr import Usd, UsdSkel
from .base_test import BaseTest
import omni.kit.property.usd
import omni.timeline
import carb.settings

from omni.anim.skelJoint.scripts import utils

# Classes for filtering the parameter UI so it only contains SkelJoint widgets:
from omni.kit.window.property.property_scheme_delegate import PropertySchemeDelegate


class TestDelegate(PropertySchemeDelegate):

    def get_widgets(self, payload):
        return ["SkelJoint"]

    def get_unwanted_widgets(self, payload):
        return ["transform", "attribute", "path", "payloads", "references", "variants"]


class TestDelegateGuard:
    def __enter__(self):
        import omni.kit.window.property as p
        w = p.get_window()
        w.register_scheme_delegate("prim", "test", TestDelegate())

    def __exit__(self, type, value, traceback):
        import omni.kit.window.property as p
        w = p.get_window()
        w.unregister_scheme_delegate("prim", "test")


class SkelJointParamUiTests(BaseTest):

    async def test_joint_ui_image(self):

        with TestDelegateGuard():
            from omni.kit import ui_test
            usd_context = omni.usd.get_context()

            from omni.kit.test_suite.helpers import open_stage

            import os
            EXT_DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.anim.skelJoint}/data"))
            usd_scene_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("usd")

            await open_stage(os.path.join(usd_scene_dir, "skelcylinder_ref.usda"))
            await ui_test.human_delay(10)

            ui.Workspace.show_window("Property", True)
            recorder_window = ui.Workspace.get_window("Property")

            # This actually maintains state and resizes the window, potentially
            # affecting later tests. Eg if the height is too small, test_skeleton_ui_save()
            # can fail because some of the buttons get pushed off the window and the
            # test framework can't click them
            await self.docked_test_window(
                window=recorder_window,
                width=500,
                height=800,
            )

            # Select a joint.
            usd_context.get_selection().set_selected_prim_paths(["/Root/group1/joint1/joint1/joint2"], True)

            # Need to wait for an additional frames for omni.ui rebuild to take effect
            await ui_test.human_delay(10)

            # verify image
            golden_img_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("golden")
            await self.finalize_test(golden_img_dir=golden_img_dir, golden_img_name="test_joint_ui.png")

    async def test_skel_ui_image(self):

        with TestDelegateGuard():
            from omni.kit import ui_test
            usd_context = omni.usd.get_context()

            from omni.kit.test_suite.helpers import open_stage

            import os
            EXT_DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.anim.skelJoint}/data"))
            usd_scene_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("usd")

            await open_stage(os.path.join(usd_scene_dir, "skelcylinder_ref.usda"))
            await ui_test.human_delay(10)
            ui.Workspace.show_window("Property", True)
            recorder_window = ui.Workspace.get_window("Property")

            stage = omni.usd.get_context().get_stage()
            skel = UsdSkel.Skeleton(stage.GetPrimAtPath("/Root/group1/joint1"))

            # check the data in the rig is consistent with the ground truth
            # ui image:
            bind_poses = utils.get_bind_poses(skel)
            rest_poses = utils.get_rest_poses(skel)
            retarget_poses = utils.get_retarget_poses(skel)
            joint_poses = utils.get_joint_poses(skel)

            self.assertEqual(joint_poses[3], bind_poses[3])
            self.assertEqual(joint_poses[3], rest_poses[3])
            self.assertEqual(joint_poses[3], retarget_poses[3])

            print("joint_poses:")
            for p in joint_poses:
                print(p)

            print("bind_poses:")
            for p in bind_poses:
                print(p)

            print("rest_poses:")
            for p in rest_poses:
                print(p)

            print("retarget_poses:")
            for p in retarget_poses:
                print(p)

            self.assertTrue(utils.is_joint_poses_matching_bind_poses(skel))
            self.assertTrue(utils.is_joint_poses_matching_rest_poses(skel))
            self.assertTrue(utils.is_joint_poses_matching_retarget_poses(skel))

            # This actually maintains state and resizes the window, potentially
            # affecting later tests. Eg if the height is too small, test_skeleton_ui_save()
            # can fail because some of the buttons get pushed off the window and the
            # test framework can't click them
            await self.docked_test_window(
                window=recorder_window,
                width=500,
                height=800,
            )

            # Select a skeleton.
            usd_context.get_selection().set_selected_prim_paths(["/Root/group1/joint1"], True)

            self.assertTrue(utils.is_joint_poses_matching_bind_poses(skel))
            self.assertTrue(utils.is_joint_poses_matching_rest_poses(skel))
            self.assertTrue(utils.is_joint_poses_matching_retarget_poses(skel))

            # Need to wait for an additional frames for omni.ui rebuild to take effect
            await ui_test.human_delay(10)

            self.assertTrue(utils.is_joint_poses_matching_bind_poses(skel))
            self.assertTrue(utils.is_joint_poses_matching_rest_poses(skel))
            self.assertTrue(utils.is_joint_poses_matching_retarget_poses(skel))

            # verify image
            golden_img_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("golden")
            await self.finalize_test(golden_img_dir=golden_img_dir, golden_img_name="test_skel_ui.png")

    '''
    Temporarily turned off duo to a crash on linux
    async def test_joint_ui_menus(self):
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import open_stage, select_prims

        import os
        EXT_DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.anim.skelJoint}/data"))
        usd_scene_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("usd")

        await open_stage(os.path.join(usd_scene_dir, "skelcylinder_ref.usda"))
        await ui_test.human_delay(10)

        stage = omni.usd.get_context().get_stage()
        jointprim = stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2")

        # Select the prim.
        await select_prims(["/Root/group1/joint1/joint1/joint2"])

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        async def click_add_menu(path):
            for widget in ui_test.find_all("Property//Frame/**/Button[*]"):
                if widget.widget.text.endswith(" Add"):
                    await widget.click()
                    await ui_test.human_delay(10)
                    await ui_test.select_context_menu(path, offset=ui_test.Vec2(10, 10))
                    await ui_test.human_delay(10)

        await click_add_menu("SkelJoint/Add Joint Limits")
        self.assertTrue(jointprim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI))

        await click_add_menu("SkelJoint/Remove Joint Limits")
        self.assertFalse(jointprim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI))

        await click_add_menu("SkelJoint/Joint Box Shape")
        await ui_test.human_delay(10)
        box_prim = stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2/BoxShape")
        self.assertTrue(box_prim)
        self.assertTrue(box_prim.HasAPI(OmniSkelSchema.OmniJointBoxShapeAPI))

        omni.kit.undo.undo()
        await ui_test.human_delay(10)

        await select_prims(["/Root/group1/joint1/joint1/joint2"])
        await ui_test.human_delay(10)

        await click_add_menu("SkelJoint/Joint Sphere Shape")
        await ui_test.human_delay(10)
        sphere_prim = stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2/SphereShape")
        self.assertTrue(sphere_prim)
        self.assertTrue(sphere_prim.HasAPI(OmniSkelSchema.OmniJointSphereShapeAPI))

        omni.kit.undo.undo()
        await ui_test.human_delay(10)

        await select_prims(["/Root/group1/joint1/joint1/joint2"])
        await ui_test.human_delay(10)

        await click_add_menu("SkelJoint/Joint Capsule Shape")
        await ui_test.human_delay(10)
        capsule_prim = stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2/CapsuleShape")
        self.assertTrue(capsule_prim)
        self.assertTrue(capsule_prim.HasAPI(OmniSkelSchema.OmniJointCapsuleShapeAPI))

        omni.kit.undo.undo()
        # TODO: check undo?
    '''

    async def test_skeleton_ui_save(self):

        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import open_stage, select_prims

        import os
        EXT_DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.anim.skelJoint}/data"))
        usd_scene_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("usd")

        await open_stage(os.path.join(usd_scene_dir, "skelcylinder_ref.usda"))
        await ui_test.human_delay(10)

        stage = omni.usd.get_context().get_stage()
        skelprim = stage.GetPrimAtPath("/Root/group1/joint1")
        jointprim = stage.GetPrimAtPath("/Root/group1/joint1/joint1/joint2")

        # Select the prim.
        await select_prims(["/Root/group1/joint1"])

        # Test the radio buttons
        anim_radio_btn = ui_test.find("Property//Frame/**.identifier=='anim_radio_btn'")
        retarget_radio_btn = ui_test.find("Property//Frame/**.identifier=='retarget_radio_btn'")
        rest_radio_btn = ui_test.find("Property//Frame/**.identifier=='rest_radio_btn'")
        bind_radio_btn = ui_test.find("Property//Frame/**.identifier=='bind_radio_btn'")

        await bind_radio_btn.click()
        await ui_test.human_delay(10)
        self.assertEqual(skelprim.GetCustomDataByKey("TransformMode"), 3)

        await rest_radio_btn.click()
        await ui_test.human_delay(10)
        self.assertEqual(skelprim.GetCustomDataByKey("TransformMode"), 2)

        await retarget_radio_btn.click()
        await ui_test.human_delay(10)
        self.assertEqual(skelprim.GetCustomDataByKey("TransformMode"), 1)

        await anim_radio_btn.click()
        await ui_test.human_delay(10)
        self.assertEqual(skelprim.GetCustomDataByKey("TransformMode"), 0)

        save_retarget_btn = ui_test.find("Property//Frame/**.identifier=='save_retarget_btn'")
        save_rest_btn = ui_test.find("Property//Frame/**.identifier=='save_rest_btn'")

        with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(stage.GetSessionLayer())):
            jointprim.GetAttribute("xformOp:rotateXYZ").Set((10, 20, 30))

        self.assertFalse(utils.is_joint_poses_matching_rest_poses(UsdSkel.Skeleton((skelprim))))
        await save_rest_btn.click()
        await ui_test.human_delay(10)
        self.assertTrue(utils.is_joint_poses_matching_rest_poses(UsdSkel.Skeleton(skelprim)))

        self.assertFalse(utils.is_joint_poses_matching_retarget_poses(UsdSkel.Skeleton(skelprim)))
        await save_retarget_btn.click()
        await ui_test.human_delay(10)
        self.assertTrue(utils.is_joint_poses_matching_retarget_poses(UsdSkel.Skeleton(skelprim)))
