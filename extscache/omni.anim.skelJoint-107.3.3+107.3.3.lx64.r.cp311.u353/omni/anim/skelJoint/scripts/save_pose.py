import carb
import omni.kit.commands
import omni.timeline
import omni.kit.usd_undo
import omni.kit.menu.utils
import omni.usd
from omni.kit.menu.utils import MenuItemDescription
from pxr import Sdf, UsdSkel, Usd
import OmniSkelSchema


class SaveSkelPoseCommand(omni.kit.commands.Command):

    class SaveTarget:
        animation = "animation"
        rest_pose = "rest_pose"

    def __init__(self, save_target):
        self._usd_undo = None
        self._save_target = save_target

    def _get_joint_skeleton_token(self, prim):
        if prim.IsA(OmniSkelSchema.OmniJoint):
            parent = prim.GetParent()
            while parent and not parent.IsA(UsdSkel.Skeleton):
                parent = parent.GetParent()
            if parent and parent.IsA(UsdSkel.Skeleton):
                parent.GetPath().MakeRelativePath(prim.GetPath())
                return UsdSkel.Skeleton(parent), ""
        return UsdSkel.Skeleton(), ""

    def do(self):
        prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        stage = omni.usd.get_context().get_stage()

        skel_prims = set()
        for prim_path in prim_paths:
            prim = stage.GetPrimAtPath(prim_path)
            if not prim:
                continue

            def add_skel(prim):
                if UsdSkel.Skeleton(prim):
                    skel_prims.add(prim)
                    return True
                return False

            if add_skel(prim):
                pass
            elif UsdSkel.Root(prim):
                for child in Usd.PrimRange(prim):
                    add_skel(child)
            elif OmniSkelSchema.OmniJoint(prim):
                # skeleton, joint_token = OmniSkelSchema.OmniJoint(prim).GetJoint()
                skeleton, joint_token = self._get_joint_skeleton_token(prim)
                if skeleton:
                    skel_prims.add(skeleton.GetPrim())
            elif UsdSkel.BindingAPI(prim):
                paths = UsdSkel.BindingAPI(prim).GetSkeletonRel().GetTargets()
                if len(paths) > 0:
                    add_skel(prim.GetStage().GetPrimAtPath(paths[0]))

        if len(skel_prims) == 0:
            for prim in stage.TraverseAll():
                if prim.IsA(UsdSkel.Skeleton):
                    skel_prims.add(prim)

        if len(skel_prims) == 0:
            carb.log_error("No skeletons, skinned prims, skeleton roots, skeleton joints are selected.")
            return

        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())
        skel_cache = UsdSkel.Cache()
        time_code = omni.timeline.get_timeline_interface().get_current_time() * stage.GetTimeCodesPerSecond()

        for skel_prim in skel_prims:
            skel_query = skel_cache.GetSkelQuery(UsdSkel.Skeleton(skel_prim))
            transforms = skel_query.ComputeJointLocalTransforms(time_code)

            if self._save_target == SaveSkelPoseCommand.SaveTarget.animation:
                # remove manipulation
                anim_query = skel_query.GetAnimQuery()
                skel_anim = UsdSkel.Animation(anim_query.GetPrim())

                if skel_anim.GetPrim().GetName().startswith("SkelPreviewAnimation"):
                    session_layer = stage.GetSessionLayer()
                    with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(session_layer)):
                        stage.RemovePrim(skel_anim.GetPath())
                        skel_prim.RemoveProperty("skel:animationSource")
                else:
                    continue

                # save pose to animation
                if not skel_anim:
                    anim_path = omni.usd.get_stage_next_free_path(
                        stage, str(skel_prim.GetPath().AppendElementString("anim")), False
                    )
                    self._usd_undo.reserve(anim_path)
                    skel_anim = UsdSkel.Animation.Define(stage, anim_path)
                    UsdSkel.BindingAPI(skel_prim).CreateAnimationSourceRel().SetTargets([skel_anim.GetPath()])

                skel_anim.GetPrim().SetSpecifier(Sdf.SpecifierDef)
                skel_anim.GetPrim().SetTypeName("SkelAnimation")

                self._usd_undo.reserve(skel_anim.GetPath().AppendProperty(UsdSkel.Tokens.joints))
                joints_attr = skel_anim.CreateJointsAttr()
                joints_attr.Clear()
                joints = skel_query.GetJointOrder()
                joints_attr.Set(joints)

                translates, rotations, scales = UsdSkel.DecomposeTransforms(transforms)
                self._usd_undo.reserve(skel_anim.GetPath().AppendProperty(UsdSkel.Tokens.translations))
                translates_attr = skel_anim.CreateTranslationsAttr()
                translates_attr.Clear()
                translates_attr.Set(translates)
                self._usd_undo.reserve(skel_anim.GetPath().AppendProperty(UsdSkel.Tokens.rotations))
                rotations_attr = skel_anim.CreateRotationsAttr()
                rotations_attr.Clear()
                rotations_attr.Set(rotations)
                self._usd_undo.reserve(skel_anim.GetPath().AppendProperty(UsdSkel.Tokens.scales))
                scales_attr = skel_anim.CreateScalesAttr()
                scales_attr.Clear()
                scales_attr.Set(scales)
            elif self._save_target == SaveSkelPoseCommand.SaveTarget.rest_pose:
                self._usd_undo.reserve(skel_prim.GetPath().AppendProperty(UsdSkel.Tokens.restTransforms))
                UsdSkel.Skeleton(skel_prim).CreateRestTransformsAttr().Set(transforms)
            else:
                raise Exception("Invalid enum: " + self._save_target)

    def undo(self):
        if self._usd_undo is None:
            return
        self._usd_undo.undo()


MENU_SAVE_POSE_TO_REST_POSE = "Save Pose to Rest Pose"
MENU_SAVE_POSE_TO_ANIMATION = "Save Pose to Animation"


class SavePose:
    def __init__(self, ext_id):
        self._ext_id = ext_id
        omni.kit.commands.register(SaveSkelPoseCommand)
        self._register_actions()

        self._menus = []
        self._sub_menus = [
            MenuItemDescription(
                name=MENU_SAVE_POSE_TO_REST_POSE,
                onclick_action=(self._ext_id, "save_pose_to_rest_pose")
            ),
            MenuItemDescription(
                name=MENU_SAVE_POSE_TO_ANIMATION,
                onclick_action=(self._ext_id, "save_pose_to_animation")
            )
        ]
        self._menus = [MenuItemDescription(name="Skeleton", sub_menu=self._sub_menus)]
        omni.kit.menu.utils.add_menu_items(self._menus, "Animation")

    def destroy(self):
        omni.kit.commands.unregister(SaveSkelPoseCommand)
        omni.kit.menu.utils.remove_menu_items(self._menus, "Animation")
        self._deregister_actions()

    def _save_pose_to_rest_pose(self):
        omni.kit.commands.execute("SaveSkelPoseCommand", save_target=SaveSkelPoseCommand.SaveTarget.rest_pose)

    def _save_pose_to_animation(self):
        omni.kit.commands.execute("SaveSkelPoseCommand", save_target=SaveSkelPoseCommand.SaveTarget.animation)

    def _register_actions(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "Animation Skeleton Actions"
        action_registry.register_action(
            self._ext_id,
            "save_pose_to_rest_pose",
            self._save_pose_to_rest_pose,
            display_name=f"Animation->Skeleton->{MENU_SAVE_POSE_TO_REST_POSE}",
            description=MENU_SAVE_POSE_TO_REST_POSE,
            tag=actions_tag,
        )
        action_registry.register_action(
            self._ext_id,
            "save_pose_to_animation",
            self._save_pose_to_animation,
            display_name=f"Animation->Skeleton->{MENU_SAVE_POSE_TO_ANIMATION}",
            description=MENU_SAVE_POSE_TO_ANIMATION,
            tag=actions_tag,
        )

    def _deregister_actions(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self._ext_id)
