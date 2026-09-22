import carb
import omni.kit.ui_test as ui_test
import omni.usd
from omni.anim.retarget.core.scripts.utils import get_skeleton_tag_joint_dict
from pxr import UsdSkel
import RetargetingSchema
from omni.anim.retarget.core.scripts.rig import RetargetRig

from ..scripts.extension import ext
from ..scripts.retarget_window import EXTENSION_NAME
from .base_test import BaseTest


def apply_tags(skeleton):
    # Default is no longer to auto-tag, so we provide the tags
    rig = RetargetRig("Human")
    rig.set_skeleton(skeleton)
    rig.auto_setup()


class RetargetWindowTest(BaseTest):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    # return true when asked to verify if it matches expected result
    def _verify_retarget_setup(self, skeleton, verify_facing, expected_facing, expected_forward_axis, expected_up_axis, verify_tag, expected_tag, tag_names, tag_values, verify_pose, expected_pose):
        if verify_facing:
            self.assertTrue(self._verify_retarget_facing(skeleton, expected_forward_axis, expected_up_axis) == expected_facing)

        if verify_tag:
            self.assertTrue(self._verify_retarget_tag_setup(skeleton, tag_names, tag_values) == expected_tag)

        if verify_pose:
            self.assertTrue(self._verify_retarget_pose(skeleton) == expected_pose)

    def _clear_retarget_setup(self, skeleton, clear_facing=True, clear_tag=True, clear_pose=True):
        if clear_facing:
            self._clear_retarget_facing(skeleton)

        if clear_tag:
            self._clear_retarget_tag_setup(skeleton)

        if clear_pose:
            self._clear_retarget_pose(skeleton)

    def _clear_retarget_facing(self, skeleton):
        skel_prim = skeleton.GetPrim()
        skel_prim.GetAttribute("controlRig:forwardAxis").Clear()
        skel_prim.GetAttribute("controlRig:upAxis").Clear()

    def _verify_retarget_facing(self, skeleton, expected_forward_axis, expected_up_axis):
        if not self._verify_control_rig_api(skeleton):
            return False

        apply_tags(skeleton)

        skel_prim = skeleton.GetPrim()
        forward_attr = skel_prim.GetAttribute("controlRig:forwardAxis")
        up_attr = skel_prim.GetAttribute("controlRig:upAxis")
        if not forward_attr:
            return False

        if not up_attr:
            return False

        forward_axis = forward_attr.Get()
        up_axis = up_attr.Get()

        # print(expected_forward_axis)
        # print(expected_up_axis)
        # carb.log_error("forward " + str(forward_axis) +", expected forward " + str(expected_forward_axis))
        # carb.log_error("up  " + str(up_axis) +", expected up " + str(expected_up_axis))
        return forward_axis == expected_forward_axis and up_axis == expected_up_axis

    def _clear_retarget_tag_setup(self, skeleton):
        skel_prim = skeleton.GetPrim()
        if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
            return

        control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
        retarget_tag_attr = control_rig_api.GetRetargetTagsAttr()
        retarget_tag_attr.Clear()

    def _verify_retarget_tag_setup(self, skeleton, tag_name_list, tag_value_list):
        if not self._verify_control_rig_api(skeleton):
            carb.log_error("-- No control rig API.")
            return False

        skel_prim = skeleton.GetPrim()
        control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
        retarget_tag_attr = control_rig_api.GetRetargetTagsAttr()

        if not retarget_tag_attr:
            carb.log_error("-- No control rig API.")
            return False

        apply_tags(skeleton)
        tag_joint_dict = get_skeleton_tag_joint_dict(skeleton)

        print(f"tag_joint_dict: {tag_joint_dict}")
        print(f"tag_name_list: {tag_name_list}")
        print(f"tag_value_list: {tag_value_list}")

        # both is empty, then go
        if len(tag_joint_dict) == 0 and len(tag_name_list) == 0:
            return True

        matching_count = 0
        for i, tag in enumerate(tag_name_list):
            if tag not in tag_joint_dict:
                carb.log_error(f"-- Missing Tag '{tag}'.")
                return False

            # if not same
            if tag_joint_dict[tag] != tag_value_list[i]:
                carb.log_error(f"-- Tag '{tag}' is '{tag_joint_dict[tag]}' -- joint dict does not match value list {i}: '{tag_value_list[i]}'.")
                return False

            matching_count += 1

        if matching_count != len(tag_name_list):
            carb.log_error(f"-- Counts do not match: '{matching_count}' vs {len(tag_name_list)}.")
            return False

        if matching_count == 0:
            carb.log_error("-- No matching tags found.")

        # otherwise, we matched everything in the list
        return matching_count > 0

    def _clear_retarget_pose(self, skeleton):
        transforms_attr = skeleton.GetPrim().GetAttribute("controlRig:retargetTransforms")
        if transforms_attr:
            # if we have it, make sure we have same number as joints
            transforms_attr.Clear()

    def _verify_retarget_pose(self, skeleton):
        if not self._verify_control_rig_api(skeleton):
            return False

        transforms_attr = skeleton.GetPrim().GetAttribute("controlRig:retargetTransforms")
        if transforms_attr is None:
            return False
        # if we have it, make sure we have same number as joints
        transforms = transforms_attr.Get()
        if transforms is None:
            return False

        joint_attr = skeleton.GetJointsAttr()
        if joint_attr is None:
            return False

        joints = joint_attr.Get()
        return len(transforms) == len(joints)

    def _verify_control_rig_api(self, skeleton):
        return skeleton.GetPrim().HasAPI(RetargetingSchema.ControlRigAPI)

    def _remove_control_rig_api(self, skeleton):
        skel_prim = skeleton.GetPrim()
        if skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
            skel_prim.Remove(RetargetingSchema.ControlRigAPI)

    async def _wait_for_window(self, window_name: str):
        MAX_WAIT = 100

        # Find active window
        for _ in range(MAX_WAIT):
            window_root = ui_test.find(f"{window_name}")
            if window_root and window_root.widget.visible:
                await ui_test.human_delay()
                break
            await ui_test.human_delay(1)

        if not window_root:
            raise Exception("Can't find window {window_name}, wait time exceeded.")

    async def _select_skeleton(self, skel_prim_path):
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()
        selection.set_selected_prim_paths([skel_prim_path], True)

        await self.assign_skeleton_button.click()
        await ui_test.human_delay(60)

    async def _open_window(self, menu_widget):
        # none of the below menu option works, so using command for now
        # await ui_test.menu_click(WINDOW_MENU)
        '''
        await menu_widget.find_menu("Window").click()
        await ui_test.human_delay()
        await menu_widget.find_menu("Animation").click()
        await ui_test.human_delay()
        await menu_widget.find_menu("Retargeting").click()
        await ui_test.human_delay()
        '''
        omni.kit.commands.execute(
            "RetargetOpenWindowCommand",
            skel_path="")

    async def _setup_test(self):
        await omni.usd.get_context().new_stage_async()
        menu_widget = ui_test.get_menubar()
        await self._open_window(menu_widget)

        await self.load_stage("retargeting-clip.usda")
        # give time after loading map
        await ui_test.human_delay(180)
        self._context = omni.usd.get_context()
        self._stage = self._context.get_stage()

        # find retarget_window
        self.retarget_window = ui_test.find(EXTENSION_NAME)
        self.assertTrue(self.retarget_window is not None)

        # resize the window
        self.retarget_window.window.position_x = 0
        self.retarget_window.window.position_y = 0
        self.retarget_window.window.width = 600
        self.retarget_window.window.height = 1000

        # find all widgets required
        # use assign button
        self.assign_skeleton_button = ui_test.find(f"{EXTENSION_NAME}//Frame/**/Button[*].identifier=='assign_skeleton_button'")
        self.reset_pose_button = ui_test.find(f"{EXTENSION_NAME}//Frame/**/Button[*].identifier=='reset_pose_button'")
        self.auto_retarget_button = ui_test.find(f"{EXTENSION_NAME}//Frame/**/Button[*].text=='Retarget'")

        self.assertTrue(self.assign_skeleton_button is not None)
        self.assertTrue(self.reset_pose_button is not None)
        self.assertTrue(self.auto_retarget_button is not None)

        # select /World/Human/Root in viewport
        self.human_skel_path = "/World/Human/Root"
        self.human_skel_prim = self._stage.GetPrimAtPath(self.human_skel_path)
        self.human_skeleton = UsdSkel.Skeleton(self.human_skel_prim)

        self.debra_skel_path = "/World/Debra/ManRoot/Debra/Debra"
        self.debra_skel_prim = self._stage.GetPrimAtPath(self.debra_skel_path)
        self.debra_skeleton = UsdSkel.Skeleton(self.debra_skel_prim)

        for item in self.human_skeleton, self.debra_skeleton:
            apply_tags(item)

        # ensure we have prim
        self.assertTrue(self.human_skel_prim is not None)
        self.assertTrue(self.debra_skel_prim is not None)

        self.extension = ext

    def _verify_selected_skeleton(self, skel_prim):
        selected_skeleton = self.extension.get_skeleton()
        self.assertTrue(selected_skeleton is not None)
        selected_path = selected_skeleton.GetPrim().GetPath()
        verify_path = skel_prim.GetPath()
        if not selected_path == verify_path:
            carb.log_error(f"verify_selected_skeleton: selected path {selected_path} != verify_path {verify_path}")
            return False
        return True

    async def test_retarget_window(self):
        await self._setup_test()

        # select
        await self._select_skeleton(self.human_skel_path)

        self.assertTrue(self._verify_selected_skeleton(self.human_skel_prim))

        # verify retarget tag
        self._verify_retarget_setup(self.human_skeleton, True, True, "Z", "Y", True, True, ["Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot"], ["Head", "L_Wrist", "R_Wrist", "L_Ankle", "R_Ankle"], True, True)

        # select debra
        await self._select_skeleton(self.debra_skel_path)

        carb.log_warn(f"Trying {self.debra_skel_path}")

        self.assertTrue(self._verify_selected_skeleton(self.debra_skel_prim))
        self._verify_retarget_setup(self.debra_skeleton, True, True, "MINUS Y", "Z", True, True, ["Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot", "LeftToeBase", "RightHandPinky3"], ["Head", "L_Hand", "R_Hand", "L_Foot", "R_Foot", "L_ToeBase", "R_Pinky2"], True, True)

        # now clear and test auto set up
        self._clear_retarget_setup(self.human_skeleton)

        await self._select_skeleton(self.human_skel_path)

        self.assertTrue(self._verify_selected_skeleton(self.human_skel_prim))

        # verify retarget tag
        self._verify_retarget_setup(self.human_skeleton, True, True, "Z", "Y", True, True, ["Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot"], ["Head", "L_Wrist", "R_Wrist", "L_Ankle", "R_Ankle"], True, True)

        self._clear_retarget_setup(self.debra_skeleton)
        await ui_test.wait_n_updates(10)
        await self._select_skeleton(self.debra_skel_path)

        self.assertTrue(self._verify_selected_skeleton(self.debra_skel_prim))
        self._verify_retarget_setup(self.debra_skeleton, True, True, "MINUS Y", "Z", True, True, ["Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot", "LeftToeBase", "RightHandPinky3"], ["Head", "L_Hand", "R_Hand", "L_Foot", "R_Foot", "L_ToeBase", "R_Pinky2"], True, True)

        await self.reset_pose_button.click()
        await ui_test.wait_n_updates(10)

        # run auto set up
        await self.auto_retarget_button.click()
        await ui_test.human_delay(60)

        # make sure only 5 tags are set up
        self._verify_retarget_setup(self.debra_skeleton, True, True, "MINUS Y", "Z", True, True, ["Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot"], ["Head", "L_Hand", "R_Hand", "L_Foot", "R_Foot"], True, True)
