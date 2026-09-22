import carb
import carb.settings
import omni.kit.notification_manager as nm
import omni.usd
from omni.kit.usd_undo import *
from omni.kit.viewport.utility import create_drop_helper
from pxr import Sdf, Tf, Usd, UsdGeom, UsdSkel

SkelAnimationDragDropSetting = "/app/viewport/animationDragDrop"


def ContainsAnimation(inPrim: Usd.Prim):
    if not inPrim:
        return False

    if inPrim.IsA(UsdSkel.Animation):
        return True

    for child in inPrim.GetChildren():
        if ContainsAnimation(child):
            return True

    return False


def ContainsPrimType(inPrim: Usd.Prim, primType: Tf.Type):
    def _find_desandant(prim, primType):
        if prim.IsA(primType):
            return prim
        for child in prim.GetChildren():
            descandant_search_prim = _find_desandant(child, primType)
            if descandant_search_prim:
                return descandant_search_prim
        return Usd.Prim()

    if not inPrim:
        return Usd.Prim()

    if inPrim.IsA(primType):
        return inPrim

    desandant_prim = _find_desandant(inPrim, primType)
    if desandant_prim:
        return desandant_prim

    parent = inPrim.GetParent()
    while parent and not parent.IsPseudoRoot():
        if parent.IsA(primType):
            return parent
        parent = parent.GetParent()

    return Usd.Prim()


def GetSkeleton(inPrim: Usd.Prim):
    if not inPrim:
        return Usd.Prim()

    if inPrim.IsA(UsdGeom.Mesh):
        bindingAPI = UsdSkel.BindingAPI(inPrim)
        skeleton = bindingAPI.GetInheritedSkeleton()
        if skeleton:
            return skeleton.GetPrim()

    return ContainsPrimType(inPrim, UsdSkel.Skeleton)


class AssignAnimation(omni.kit.commands.Command):
    def __init__(self, skeleton_path, animprim_path):
        self.usd_undo = None
        self.skeleton_path = skeleton_path
        self.animprim_path = animprim_path

    def do(self):
        stage = omni.usd.get_context().get_stage()

        skel_prim = UsdSkel.Skeleton(stage.GetPrimAtPath(self.skeleton_path))
        anim_prim = UsdSkel.Animation(stage.GetPrimAtPath(self.animprim_path))
        if skel_prim and anim_prim:
            omni.kit.undo.begin_group()
            self.usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
            self.usd_undo.reserve(self.skeleton_path)
            UsdSkel.BindingAPI(skel_prim).GetAnimationSourceRel().SetTargets([self.animprim_path])
            omni.kit.undo.end_group()
        else:
            raise Exception("Invalid prim: skeleton " + self.skeleton_path + ", anim " + self.animprim_path)

    def undo(self):
        if self.usd_undo is None:
            return

        self.usd_undo.undo()


class AnimationDropHelper:
    def __init__(self):
        self._usd_context = omni.usd.get_context()
        self._settings = carb.settings.get_settings()
        omni.kit.commands.register(AssignAnimation)
        self._drop_helper = create_drop_helper(
            pickable=False,
            on_drop_accepted_fn=self._on_drop_accepted,
            on_drop_fn=self._on_drop,
            on_pick_fn=self._on_pick_fn,
        )

    def __del__(self):
        self._drop_helper = None
        command = omni.kit.commands.get_command_class("AssignAnimation")
        if command != None:
            omni.kit.commands.unregister(AssignAnimation)
        self._settings = None
        self._usd_context = None

    def _on_drop_accepted(self, url: str):
        enable_anim_drop = self._settings.get_as_bool(SkelAnimationDragDropSetting)
        if not enable_anim_drop:
            return False
        if url is not None and url.startswith("/"):
            path = Sdf.Path(url)
            if path.IsPrimPath():
                stage = self._usd_context.get_stage()
                prim = stage.GetPrimAtPath(path)
                return ContainsAnimation(prim)

        return False

    def _on_drop(self, url: str, target, viewport_name, context_name):
        print(f"drop url {url}")
        print(f"drop target {target}")
        enable_anim_drop = self._settings.get_as_bool(SkelAnimationDragDropSetting)
        if not enable_anim_drop:
            return target

        if url is not None and url.startswith("/") and target is not None and target != "":
            stage = self._usd_context.get_stage()
            src_path = Sdf.Path(url)
            src_prim = stage.GetPrimAtPath(src_path)
            if ContainsAnimation(src_prim):
                dst_path = Sdf.Path(target)
                dst_prim = stage.GetPrimAtPath(dst_path)
                skel_prim = GetSkeleton(dst_prim)
                anim_prim = ContainsPrimType(src_prim, UsdSkel.Animation)
                if skel_prim and anim_prim:
                    omni.kit.commands.execute(
                        "AssignAnimation",
                        skeleton_path=skel_prim.GetPath().pathString,
                        animprim_path=anim_prim.GetPath().pathString,
                    )

        return target

    def _on_pick_fn(self, payload, prim_path, usd_context_name):
        print(f"pick payload {payload}")
        print(f"prim_path {prim_path}")
