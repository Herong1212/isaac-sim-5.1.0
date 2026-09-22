from pathlib import Path
import carb
import carb.settings
from typing import List, Dict


def rgb_to_abgr(rgb: int) -> int:
    """Convert RGB value to ABGR, which is what omni.ui wants"""
    a = 0xFF
    b = rgb & 0xFF
    g = (rgb >> 8) & 0xFF
    r = (rgb >> 16) & 0xFF
    return (a << 24) | (b << 16) | (g << 8) | r


def lerp_component(color: int, fixed_color: int) -> int:
    """Lerp a value to the fixed color"""
    return int(color + 0.5 * (fixed_color - color))


def lerp_color_to_secondary(rgb: int) -> int:
    """Calculate secondary from primary color
    This is defined as a desaturation of the primary color. One way to do this is to simply
    lerp the color towards grey. In our case half-way to #1F2123.
    """
    b = rgb & 0xFF
    g = (rgb >> 8) & 0xFF
    r = (rgb >> 16) & 0xFF
    return lerp_component(b, 0x23) | (lerp_component(g, 0x21) << 8) | (lerp_component(r, 0x1F) << 16)


class Paths:
    EXT_PATH = Path(__file__).parent.parent.parent.parent.parent.parent
    ICON_PATH = EXT_PATH.joinpath("icons")


class Settings:
    @staticmethod
    def set_default_settings():
        """Set up defaults for the settings that are owned by this extension"""
        settings = carb.settings.get_settings()
        settings.set_default_bool("/persistent/animGraph/showNameAsType", False)
        settings.set_default_bool("/exts/omni.anim.graph.ui/show_window", False)

    @staticmethod
    def get_show_window():
        return carb.settings.get_settings().get_as_bool("/exts/omni.anim.graph.ui/show_window")

    @staticmethod
    def get_show_name_as_type():
        return carb.settings.get_settings().get_as_bool("/persistent/animGraph/showNameAsType")

    @staticmethod
    def get_enable_FBIK():
        return carb.settings.get_settings().get_as_bool("/exts/omni.anim.graph.ui/enable_FBIK_nodes")

    @staticmethod
    def set_show_name_as_type(value: bool):
        carb.settings.get_settings().set("/persistent/animGraph/showNameAsType", value)


def get_blend_tree_node_types() -> Dict[str, List[str]]:

    nodes = {"Blend Tree": ["Blend", "MotionMatching", "LookAtIK", "Filter", "PoseProvider", "TwoBoneIK"],
            "State Machine": ["StateMachine"],
            "Animation": ["AnimationClip"]}

    if Settings.get_enable_FBIK():
        nodes["Blend Tree"].append("FullBodyIK")
        nodes["Blend Tree"].append("SetEffector")

    return nodes


def get_state_machine_node_types() -> Dict[str, List[str]]:
    return {"State Machine": ["State"]}


def get_condition_graph_node_types() -> Dict[str, List[str]]:
    return {"Condition": ["ConditionCompareVariable", "ConditionTimeFractionCrossed", "ConditionSpeed", "ConditionAND", "ConditionOR"]}


def get_icon_urls() -> Dict[str, str]:
    return {"Blend Tree": "node/type_blendtree_dark.svg",
            "Blend": "node/type_blend_dark.svg",
            "MotionMatching": "node/type_motion_matching_dark.svg",
            "LookAtIK": "node/type_look_at_ik_dark.svg",
            "TwoBoneIK": "node/type_two_bone_ik_dark.svg",
            "FullBodyIK": "node/type_full_body_ik_dark.svg",
            "SetEffector": "node/type_set_effector_dark.svg",
            "Filter": "node/type_filter_dark.svg",
            "PoseProvider": "node/type_pose_provider_dark.svg",
            "State Machine": "node/type_statemachine_dark.svg",
            "StateMachine": "node/type_statemachine_dark.svg",
            "State": "node/type_state_dark.svg",
            "Transition": "node/type_transition_dark.svg",
            "Condition": "node/type_condition_dark.svg",
            "ConditionCompareVariable": "node/type_condition_dark.svg",
            "ConditionTimeFractionCrossed": "node/type_condition_dark.svg",
            "ConditionSpeed": "node/type_condition_dark.svg",
            "ConditionAND": "node/type_condition_dark.svg",
            "ConditionOR": "node/type_condition_dark.svg",
            "Animation": "node/type_animation_clip_dark.svg",
            "AnimationClip": "node/type_animation_clip_dark.svg"}
