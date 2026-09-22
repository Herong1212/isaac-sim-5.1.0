import omni
import omni.client
from omni.kit.usd_undo import UsdLayerUndo
import omni.usd
from typing import List
from pxr import Sdf, Usd
import AnimGraphSchema

ANIM_GRAPH_EXTERNAL = "animationGraph:external"


def get_stage_default_prim_path(stage):
    if stage.HasDefaultPrim():
        return stage.GetDefaultPrim().GetPath()
    else:
        return Sdf.Path.absoluteRootPath


def relationship_has_target(relationship, target_path):
    if relationship:
        targets = relationship.GetTargets()
        for path in targets:
            if path == target_path:
                return True
    return False


class ApplyAnimationGraphAPICommand(omni.kit.commands.Command):
    def __init__(
        self,
        layer: Sdf.Layer = None,
        paths: List[Sdf.Path] = [],
        animation_graph_path: Sdf.Path = Sdf.Path.emptyPath
    ):
        self._usd_undo = None
        self._layer = layer
        self._paths = paths
        self._animation_graph_path = animation_graph_path

    def do(self):
        stage = omni.usd.get_context().get_stage()
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if prim and not prim.HasAPI(AnimGraphSchema.AnimationGraphAPI):
                self._usd_undo.reserve(path)
                animGraphAPI = AnimGraphSchema.AnimationGraphAPI.Apply(prim)
                animGraphAPI.GetAnimationGraphRel().SetTargets([self._animation_graph_path])

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class RemoveAnimationGraphAPICommand(omni.kit.commands.Command):
    def __init__(
        self,
        layer: Sdf.Layer = None,
        paths: List[Sdf.Path] = []
    ):
        self._usd_undo = None
        self._layer = layer
        self._paths = paths

    def do(self):
        stage = omni.usd.get_context().get_stage()
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if prim and prim.HasAPI(AnimGraphSchema.AnimationGraphAPI):
                self._usd_undo.reserve(path)
                prim.RemoveProperty("animationGraph")
                prim.RemoveAPI(AnimGraphSchema.AnimationGraphAPI)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class CreateAnimationGraphCommand(omni.kit.commands.Command):
    def __init__(
        self,
        layer: Sdf.Layer = None,
        path: Sdf.Path = Sdf.Path.emptyPath,
        skeleton_path: Sdf.Path = Sdf.Path.emptyPath
    ):
        self._usd_undo = None
        self._layer = layer
        self._path = path
        self._skeleton_path = skeleton_path

    def do(self):
        stage = omni.usd.get_context().get_stage()
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        if self._path.isEmpty:
            default_prim_path = get_stage_default_prim_path(stage)
            self._path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, f"{default_prim_path}/AnimationGraph", False))
        self._usd_undo.reserve(self._path)
        anim_graph = AnimGraphSchema.AnimationGraph.Define(stage, self._path)
        if anim_graph is not None:
            if self._skeleton_path != Sdf.Path.emptyPath:
                rel = anim_graph.GetSkelSkeletonRel()
                if rel.IsValid():
                    rel.SetTargets([self._skeleton_path])

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class RenameAnimationGraphVariableAttributeCommand(omni.kit.commands.Command):
    def __init__(self, prim: Usd.Prim, old_attr_name: str, new_attr_name: str):
        self._prim = prim
        self._old_name = old_attr_name
        self._new_name = new_attr_name
        self._renamed = False

    @staticmethod
    def rename_variable(prim, old_name, new_name):
        with Sdf.ChangeBlock():
            old_attr = prim.GetAttribute(old_name)
            new_attr = prim.CreateAttribute(new_name, old_attr.GetTypeName(), True, Sdf.VariabilityUniform)
            new_attr.SetDocumentation(old_attr.GetDocumentation())
            old_value = old_attr.Get()
            if old_value:
                new_attr.Set(old_value)
            prim.RemoveProperty(old_name)

    def do(self):
        if self._old_name == self._new_name:
            return
        if not self._prim.HasAttribute(self._old_name) or self._prim.HasAttribute(self._new_name):
            return
        RenameAnimationGraphVariableAttributeCommand.rename_variable(self._prim, self._old_name, self._new_name)
        self._renamed = True

    def undo(self):
        if not self._renamed:
            return
        RenameAnimationGraphVariableAttributeCommand.rename_variable(self._prim, self._new_name, self._old_name)


class SetAnimationGraphVariableAttributeTypeCommand(omni.kit.commands.Command):
    def __init__(self, prim: Usd.Prim, attr_name: str, new_type: Sdf.ValueTypeName, new_value=None):
        self._prim = prim
        self._attr_name = attr_name
        self._old_type = None
        self._old_value = None
        self._new_type = new_type
        self._new_value = new_value
        self._type_changed = False

    @staticmethod
    def set_variable_type(prim, attr_name, new_type, new_value):
        with Sdf.ChangeBlock():
            old_attr = prim.GetAttribute(attr_name)
            old_description = old_attr.GetDocumentation()
            prim.RemoveProperty(attr_name)
            new_attr = prim.CreateAttribute(attr_name, new_type, True, Sdf.VariabilityUniform)
            new_attr.SetDocumentation(old_description)
            if new_value is not None:
                # We want to set the value, even if it would evaluate to False in an if statement.
                new_attr.Set(new_value)

    def do(self):
        if not self._prim.HasAttribute(self._attr_name):
            return
        attr = self._prim.GetAttribute(self._attr_name)
        self._old_type = attr.GetTypeName()
        if self._old_type == self._new_type:
            return
        self._old_value = attr.Get()

        SetAnimationGraphVariableAttributeTypeCommand.set_variable_type(
            self._prim,
            self._attr_name,
            self._new_type,
            self._new_value
        )
        self._type_changed = True

    def undo(self):
        if not self._type_changed:
            return
        SetAnimationGraphVariableAttributeTypeCommand.set_variable_type(
            self._prim,
            self._attr_name,
            self._old_type,
            self._old_value
        )


class SetAnimationGraphVariableDescriptionCommand(omni.kit.commands.Command):
    def __init__(self, prim: Usd.Prim, attr_name: str, description: str):
        self._prim = prim
        self._attr_name = attr_name
        self._description = description
        self._old_description = None
        self._set_description = False

    def do(self):
        if not self._prim.HasAttribute(self._attr_name):
            return
        attr = self._prim.GetAttribute(self._attr_name)
        self._old_description = attr.GetDocumentation()
        if self._description == self._old_description:
            return
        attr.SetDocumentation(self._description)
        self._set_description = True

    def undo(self):
        if not self._set_description:
            return
        attr = self._prim.GetAttribute(self._attr_name)
        attr.SetDocumentation(self._old_description)


omni.kit.commands.register_all_commands_in_module(__name__)
