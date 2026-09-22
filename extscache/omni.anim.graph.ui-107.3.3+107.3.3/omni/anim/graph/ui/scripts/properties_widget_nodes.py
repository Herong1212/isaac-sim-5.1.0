import omni.ui as ui
import omni.usd
from pxr import Usd, UsdSkel, Sdf
import AnimGraphSchema
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry, UsdPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import (
            CustomLayoutFrame,
            CustomLayoutProperty,
        )
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.window.popup_dialog import MessageDialog
from omni.kit.property.usd.widgets import ICON_PATH
from omni.kit.usd_undo import *
from .token_array_edit_widget import build_joints_token_array_prop, build_blendshapes_token_array_prop, build_token_array_prop
from .skel_tree_searchable_widget import build_skel_tree_prop
from .stage_picker_dialog import StagePickerDialog
from .variable_compare_widget import build_compare_variable_name_prop, build_compare_operation_prop
from .token_combobox_widget import build_token_combobox_prop
from typing import List

from .mm_relationship_widget import UsdMmRelationshipUiEntry, mm_relationship_builder
from .mm_joint_widget import UsdMmJointUiEntry, mm_joint_builder

ANIM_GRAPH_NODE_SETTINGS_TYPES = [
    AnimGraphSchema.AnimationClip,
    AnimGraphSchema.Filter,
    AnimGraphSchema.LookAtIK,
    AnimGraphSchema.TwoBoneIK,
    AnimGraphSchema.FullBodyIK,
    AnimGraphSchema.SetEffector,
    AnimGraphSchema.Transition,
    AnimGraphSchema.ConditionTimeFractionCrossed,
    AnimGraphSchema.ConditionSpeed,
    AnimGraphSchema.ConditionCompareVariable,
    AnimGraphSchema.MotionMatching,
    AnimGraphSchema.BehaviorScript,
    AnimGraphSchema.Blend,
    AnimGraphSchema.PoseProvider,
]

NODE_SETTINGS_ATTRS = [
    "inputs:animationSource", "inputs:startTime", "inputs:endTime", "inputs:loop", "inputs:backwards",
    "inputs:joints", "inputs:inclusive", "inputs:includeChildren", "inputs:blendShapes", "inputs:blendShapesInclusive",
    "inputs:startJoint", "inputs:hingeJoint", "inputs:endJoint", "inputs:forwardAxis", "inputs:worldSpaceTarget",
    "inputs:durationTime",
    "inputs:fraction", "inputs:speed",
    "inputs:variableName", "inputs:operator", "inputs:value",
    "inputs:clips", "inputs:clipsEnabled", "inputs:clipsStartTimes", "inputs:clipsEndTimes",
    "inputs:joints", "inputs:jointsPositionWeights", "inputs:jointsVelocityWeights",
    "inputs:matchingDelayTime", "inputs:transitionDurationTime",
    "inputs:sampleRate", "inputs:timeHorizon", "inputs:trajectorySamples",
    "inputs:trajectoryPositionWeight", "inputs:trajectoryDirectionWeight",
    "inputs:movementAverageForwardSpeed", "inputs:movementAverageSidewardSpeed", "inputs:movementAverageBackwardSpeed",
    "inputs:effector", "inputs:worldTransform", "inputs:position_alpha", "inputs:rotation_alpha", "inputs:maxIteration", "inputs:tolerance",
    "inputs:damping", "inputs:minLinearStrength", "inputs:maxLinearStrength",
    "inputs:minAngularStrength", "inputs:maxAngularStrength", "inputs:jacobianStrength", "inputs:constraintStrength", "inputs:allowPelvisToTranslate",
    "scriptPath", "target",
    "inputs:jointPositionBlendMode", "inputs:jointRotationBlendMode", "inputs:blendshapeBlendMode", "inputs:passThroughMode",
    "inputs:blendShapesMapping",
]


class AnimationGraphNodePropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title: str):
        super().__init__(title, collapsed=False)
        self._title = title

    def destroy(self):
        pass

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            for schema in ANIM_GRAPH_NODE_SETTINGS_TYPES:
                if prim.IsA(schema):
                    return True
            return False
        return False

    def _filter_props_to_build(self, props):
        return [prop for prop in props if prop.GetName() in NODE_SETTINGS_ATTRS]

    def get_additional_kwargs(self, ui_attr):
        random_prim = Usd.Prim()
        if self._payload:
            prim_paths = self._payload.get_paths()
            for prim_path in prim_paths:
                prim = self._get_prim(prim_path)
                if not prim:
                    continue
                if not random_prim:
                    random_prim = prim
                elif random_prim.GetTypeName() != prim.GetTypeName():
                    break
        if ui_attr.prop_name == "inputs:clips":
            return None, {"target_picker_filter_type_list": [UsdSkel.Animation]}
        elif ui_attr.prop_name == "inputs:animationSource":
            return None, {"target_picker_filter_type_list": [UsdSkel.Animation], "targets_limit": 1}
        elif ui_attr.prop_name == "target":
            return None, {"target_picker_filter_type_list": [UsdSkel.Root], "targets_limit": 1}
        return None, {"targets_limit": 1}

    def _customize_props_layout(self, props):
        anchor_prim = self._get_prim(self._payload[-1])

        filtered_props = []
        for prop in props:
            if prop.attr_name == "inputs:clips":
                filtered_props.append(
                    UsdMmRelationshipUiEntry(
                        display_name="Clips",
                        rel_name=prop.attr_name,
                        pre_rel_attr_names=["inputs:clipsEnabled"],
                        post_rel_attr_names=["inputs:clipsStartTimes", "inputs:clipsEndTimes"],
                        display_group="",
                        metadata={
                            "inputs:clipsEnabled":
                            {Sdf.PrimSpec.TypeNameKey: "bool[]", "customData": {"default": [], "defaultElement": True}},
                            "inputs:clips":
                            {Sdf.PrimSpec.TypeNameKey: "rel", "customData": {"default": ""}},
                            "inputs:clipsStartTimes":
                            {Sdf.PrimSpec.TypeNameKey: "float[]", "customData": {"default": [], "defaultElement": 0.0}},
                            "inputs:clipsEndTimes":
                            {Sdf.PrimSpec.TypeNameKey: "float[]", "customData": {"default": [], "defaultElement": 0.0}},
                        },
                        build_fn=mm_relationship_builder
                    )
                )
            elif prop.attr_name == "inputs:joints" and anchor_prim and anchor_prim.IsA(AnimGraphSchema.MotionMatching):
                filtered_props.append(
                    UsdMmJointUiEntry(
                        display_name="Joints",
                        rel_name=prop.attr_name,
                        pre_rel_attr_names=[],
                        post_rel_attr_names=["inputs:jointsPositionWeights", "inputs:jointsVelocityWeights"],
                        display_group="",
                        metadata={
                            "inputs:joints":
                            {Sdf.PrimSpec.TypeNameKey: "token[]", "customData": {"default": ""}},
                            "inputs:jointsPositionWeights":
                            {Sdf.PrimSpec.TypeNameKey: "float[]", "customData": {"default": [], "defaultElement": 1.0}},
                            "inputs:jointsVelocityWeights":
                            {Sdf.PrimSpec.TypeNameKey: "float[]", "customData": {"default": [], "defaultElement": 1.0}},
                        },
                        build_fn=mm_joint_builder
                    )
                )
            else:
                filtered_props.append(prop)

        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.AnimationClip):
                CustomLayoutProperty("inputs:animationSource")
                CustomLayoutProperty("inputs:startTime")
                CustomLayoutProperty("inputs:endTime")
                CustomLayoutProperty("inputs:loop")
                CustomLayoutProperty("inputs:backwards")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.Filter):
                CustomLayoutProperty("inputs:joints")
                CustomLayoutProperty("inputs:inclusive")
                CustomLayoutProperty("inputs:includeChildren")
                CustomLayoutProperty("inputs:blendShapes")
                CustomLayoutProperty("inputs:blendShapesInclusive")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.PoseProvider):
                CustomLayoutProperty("inputs:joints")
                CustomLayoutProperty("inputs:inclusive")
                CustomLayoutProperty("inputs:includeChildren")
                CustomLayoutProperty("inputs:blendShapesMapping")
                CustomLayoutProperty("inputs:blendShapesInclusive")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.LookAtIK):
                CustomLayoutProperty("inputs:startJoint")
                CustomLayoutProperty("inputs:endJoint")
                CustomLayoutProperty("inputs:forwardAxis")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.TwoBoneIK):
                CustomLayoutProperty("inputs:startJoint")
                CustomLayoutProperty("inputs:hingeJoint")
                CustomLayoutProperty("inputs:endJoint")
                CustomLayoutProperty("inputs:worldSpaceTarget")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.FullBodyIK):
                CustomLayoutProperty("inputs:maxIteration")
                CustomLayoutProperty("inputs:tolerance")
                CustomLayoutProperty("inputs:damping")
                CustomLayoutProperty("inputs:minLinearStrength")
                CustomLayoutProperty("inputs:maxLinearStrength")
                CustomLayoutProperty("inputs:minAngularStrength")
                CustomLayoutProperty("inputs:maxAngularStrength")
                CustomLayoutProperty("inputs:jacobianStrength")
                CustomLayoutProperty("inputs:constraintStrength")
                CustomLayoutProperty("inputs:allowPelvisToTranslate")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.SetEffector):
                CustomLayoutProperty("inputs:effector")
                CustomLayoutProperty("inputs:worldTransform")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.MotionMatching):
                CustomLayoutProperty("inputs:clips")
                CustomLayoutProperty("inputs:joints")
                CustomLayoutProperty("inputs:matchingDelayTime")
                CustomLayoutProperty("inputs:transitionDurationTime")
                CustomLayoutProperty("inputs:sampleRate")
                CustomLayoutProperty("inputs:timeHorizon")
                CustomLayoutProperty("inputs:trajectorySamples")
                CustomLayoutProperty("inputs:trajectoryPositionWeight")
                CustomLayoutProperty("inputs:trajectoryDirectionWeight")
                CustomLayoutProperty("inputs:movementAverageForwardSpeed")
                CustomLayoutProperty("inputs:movementAverageSidewardSpeed")
                CustomLayoutProperty("inputs:movementAverageBackwardSpeed")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.Transition):
                CustomLayoutProperty("inputs:durationTime")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.ConditionTimeFractionCrossed):
                CustomLayoutProperty("inputs:fraction")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.ConditionSpeed):
                CustomLayoutProperty("inputs:speed")
                CustomLayoutProperty("inputs:operator")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.ConditionCompareVariable):
                CustomLayoutProperty("inputs:variableName")
                CustomLayoutProperty("inputs:operator")
                CustomLayoutProperty("inputs:value", "Value")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.BehaviorScript):
                CustomLayoutProperty("scriptPath", "Script Path")
                CustomLayoutProperty("target", "Target")
            if anchor_prim and anchor_prim.IsA(AnimGraphSchema.Blend):
                CustomLayoutProperty("inputs:jointPositionBlendMode")
                CustomLayoutProperty("inputs:jointRotationBlendMode")
                CustomLayoutProperty("inputs:blendshapeBlendMode")
                CustomLayoutProperty("inputs:passThroughMode")
        return frame.apply(filtered_props)

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        metadata = ui_prop.metadata
        if metadata:
            type_name = metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")
            sdf_type_name = Sdf.ValueTypeNames.Find(type_name)
            if ui_prop.prop_name == "inputs:joints":
                ui_prop.build_fn = build_joints_token_array_prop
            elif ui_prop.prop_name == "inputs:startJoint" or \
                    ui_prop.prop_name == "inputs:hingeJoint" or \
                    ui_prop.prop_name == "inputs:endJoint" or \
                    ui_prop.prop_name == "inputs:effector":
                ui_prop.build_fn = build_skel_tree_prop
            elif ui_prop.prop_name == "inputs:variableName":
                ui_prop.build_fn = build_compare_variable_name_prop
            elif ui_prop.prop_name == "inputs:operator":
                ui_prop.build_fn = build_compare_operation_prop
            elif ui_prop.prop_name == "inputs:blendShapes" or ui_prop.prop_name == "inputs:blendShapesMapping":
                ui_prop.build_fn = build_blendshapes_token_array_prop
            elif ui_prop.prop_name == "inputs:jointPositionBlendMode" or ui_prop.prop_name == "inputs:jointRotationBlendMode" or \
                    ui_prop.prop_name == "inputs:blendshapeBlendMode" or ui_prop.prop_name == "inputs:passThroughMode":
                ui_prop.build_fn = build_token_combobox_prop
            elif sdf_type_name.type == Sdf.ValueTypeNames.TokenArray.type:
                ui_prop.build_fn = build_token_array_prop
        if isinstance(ui_prop, UsdMmRelationshipUiEntry):
            ui_prop.build_fn = mm_relationship_builder
            return self._build_motion_matching_rel_entry(stage, ui_prop, prim_paths)
        if isinstance(ui_prop, UsdMmJointUiEntry):
            ui_prop.build_fn = mm_joint_builder
            return self._build_motion_matching_rel_entry(stage, ui_prop, prim_paths)
        else:
            return super().build_property_item(stage, ui_prop, prim_paths)

    def _build_motion_matching_rel_entry(self, stage, ui_prop: UsdMmRelationshipUiEntry, prim_paths: List[Sdf.Path]):
        if ui_prop.prim_paths:
            prim_paths = ui_prop.prim_paths

        # TODO: we probably want to support the generic properties widget builder, but the named arguments don't match
        build_fn = ui_prop.build_fn if ui_prop.build_fn else mm_relationship_builder  # UsdPropertiesWidgetBuilder.build
        additional_label_kwargs, additional_widget_kwargs = self.get_additional_kwargs(ui_prop)
        models = build_fn(
            stage=stage,
            label_name=ui_prop.display_name,
            rel_name=ui_prop.prop_name,
            pre_rel_attr_names=ui_prop.pre_rel_attr_names,
            post_rel_attr_names=ui_prop.post_rel_attr_names,
            metadata=ui_prop.metadata,
            prim_paths=prim_paths,
            additional_label_kwargs=additional_label_kwargs,
            additional_widget_kwargs=additional_widget_kwargs,
        )
        if models:
            if not isinstance(models, list):
                models = [models]
            for model in models:
                for prim_path in prim_paths:
                    # TODO: Using the prop_name, which is the first attribute name is risky
                    self._models[prim_path.AppendProperty(ui_prop.prop_name)].append(model)
