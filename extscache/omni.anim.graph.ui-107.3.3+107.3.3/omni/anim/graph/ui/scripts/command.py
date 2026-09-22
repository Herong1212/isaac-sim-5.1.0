import omni
from pxr import Sdf, Usd
from omni.usd.commands import RelationshipTargetBase
from .utils import relationship_has_target, refresh_property_window
from typing import List, Optional, Tuple


class AnimGraphUIReplaceRelationshipTargetCommand(RelationshipTargetBase):
    def __init__(self, relationship: Usd.Relationship, old_target: Sdf.Path, new_target: Sdf.Path):
        super().__init__(relationship, old_target)
        self._new_target = new_target

    def do(self):
        rel = self._get_relationship()
        if rel and relationship_has_target(rel, self._target):
            self._prev_targets = rel.GetTargets()
            rel.RemoveTarget(self._target)
            if not relationship_has_target(rel, self._new_target):
                rel.AddTarget(self._new_target)


class AnimGraphUISetRelationshipTargetsCommand(RelationshipTargetBase):
    def __init__(self, relationship: Usd.Relationship, targets: List[Sdf.Path]):
        super().__init__(relationship, None)
        self._new_targets = targets

    def do(self):
        rel = self._get_relationship()
        if rel:
            self._prev_targets = rel.GetTargets()
            rel.SetTargets(self._new_targets)


class AnimGraphUIRefreshPropertyWindowCommand(omni.kit.commands.Command):
    def __init__(self):
        pass

    def do(self):
        refresh_property_window()

    def undo(self):
        pass


class AnimGraphUISetNodePositionCommand(omni.kit.commands.Command):
    def __init__(self, prim: Usd.Prim, position_attribute_name: str, value: Optional[Tuple[float, float]]):
        self._stage = prim.GetStage()
        self._prim_path = prim.GetPath()
        self._position_attribute_name = position_attribute_name
        self._value = value
        self._created_attr = False
        self._set_attr = False
        self._last_value = None

    def do(self):
        prim = self._stage.GetPrimAtPath(self._prim_path)
        if not prim:
            return

        prim_had_attr = prim.HasAttribute(self._position_attribute_name)
        attr = prim.CreateAttribute(
            self._position_attribute_name,
            Sdf.ValueTypeNames.Float2,
            True,
            Sdf.VariabilityUniform
        )

        if attr:
            if prim_had_attr:
                self._last_value = attr.Get()
                if self._last_value == self._value:
                    return
            else:
                self._created_attr = True

            attr.Set(self._value)
            self._set_attr = True

    def undo(self):
        prim = self._stage.GetPrimAtPath(self._prim_path)
        if not prim:
            return

        if self._created_attr:
            prim.RemoveProperty(self._position_attribute_name)
        elif self._set_attr:
            prim.GetAttribute(self._position_attribute_name).Set(self._last_value)


omni.kit.commands.register_all_commands_in_module(__name__)
